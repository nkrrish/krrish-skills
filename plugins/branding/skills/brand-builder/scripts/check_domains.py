#!/usr/bin/env python3
"""Check domain availability through public RDAP (no account or key needed).

Usage:
  check_domains.py names.json [--tld com] [--workers 8] --out checked.json
  check_domains.py --names yunoly,trepil --tld com,app

Input: a JSON list of names (strings or {"name": ...} objects) or a text file, one per line.
Output: the same records with "domain" and "status": "free", "taken" or "unknown".

RDAP answers 404 for an unregistered name and 200 for a registered one. .com and .net go
to Verisign directly; other TLDs go through the rdap.org bootstrap. "free" means not
registered right now; it is not a reservation, and some free names are premium priced.
"""
import argparse, json, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "brand-builder/1.0 (+https://github.com/nkrrish/krrish-skills)", "Accept": "application/rdap+json"}


def rdap_url(domain):
    tld = domain.rsplit(".", 1)[-1]
    if tld in ("com", "net"):
        return f"https://rdap.verisign.com/{tld}/v1/domain/{domain}"
    return f"https://rdap.org/domain/{domain}"


def check(domain, tries=3):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(rdap_url(domain), headers=UA)
            with urllib.request.urlopen(req, timeout=15) as r:
                return "taken" if r.status == 200 else "unknown"
        except urllib.error.HTTPError as e:
            if e.code == 404: return "free"
            if e.code in (429, 500, 502, 503): time.sleep(1.5 * (attempt + 1)); continue
            return "unknown"
        except Exception:
            time.sleep(1.0 * (attempt + 1))
    return "unknown"


def load(path):
    try:
        data = json.load(open(path))
        return [d if isinstance(d, dict) else {"name": d} for d in data]
    except json.JSONDecodeError:
        return [{"name": l.strip()} for l in open(path) if l.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?")
    ap.add_argument("--names", help="comma list instead of a file")
    ap.add_argument("--tld", default="com", help="comma list, e.g. com,app,io")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out")
    a = ap.parse_args()
    if not a.input and not a.names: ap.error("give a file or --names")
    recs = load(a.input) if a.input else [{"name": n.strip().lower()} for n in a.names.split(",") if n.strip()]
    tlds = [t.strip().lstrip(".") for t in a.tld.split(",") if t.strip()]
    jobs = [(i, t) for i in range(len(recs)) for t in tlds]

    def run(job):
        i, t = job
        d = f"{recs[i]['name']}.{t}"
        return i, t, d, check(d)

    results = []
    with ThreadPoolExecutor(a.workers) as ex:
        for i, t, d, s in ex.map(run, jobs):
            r = dict(recs[i]); r.update({"domain": d, "tld": t, "status": s}); results.append(r)
    counts = {s: sum(1 for r in results if r["status"] == s) for s in ("free", "taken", "unknown")}
    if a.out:
        json.dump(results, open(a.out, "w"), indent=1)
        print(f"{len(results)} checked -> {a.out}  free:{counts['free']} taken:{counts['taken']} unknown:{counts['unknown']}")
    else:
        for r in results: print(f"{r['status']:8} {r['domain']}")
        print(f"free:{counts['free']} taken:{counts['taken']} unknown:{counts['unknown']}")
    if counts["unknown"]:
        print("some lookups failed; re-run them before reporting", file=sys.stderr)


if __name__ == "__main__":
    main()
