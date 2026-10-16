#!/usr/bin/env python3
"""Check domain availability for any TLDs the user picks. No account or key needed.

Usage:
  check_domains.py names.json --tld com,ai,app --out checked.json
  check_domains.py --names yunoly,trepil --tld com,io

Input: a JSON list of names (strings or {"name": ...} objects) or a text file, one per line.
Output: one record per name and TLD, with "domain", "tld" and "status": "free", "taken" or
"unknown".

How it decides:
  1. RDAP, using the registry's own server from the IANA bootstrap file
     (data.iana.org/rdap/dns.json): 404 means unregistered, 200 means registered.
  2. WHOIS on port 43 for TLDs with no RDAP server (many country codes, for example .io,
     .so, .co): the registry's WHOIS server comes from whois.iana.org, and "not found" style
     answers mean unregistered.
  Anything else is "unknown": re-run it, never report it as free.

"free" means not registered right now. It is not a reservation, and some free names are
premium priced or reserved by the registry; a registrar check at purchase time is final.
"""
import argparse, json, os, re, socket, sys, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "brand-builder/1.1 (+https://github.com/nkrrish/krrish-skills)", "Accept": "application/rdap+json"}
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "brand-builder")
FREE_WHOIS = re.compile(r"no match|not found|no data found|no entries found|status:\s*free|status:\s*available|"
                        r"is available|domain not found|no object found|nothing found|not registered|available for registration",
                        re.I)
_lock = threading.Lock()
_whois_server = {}
_host_sem = {}


def bootstrap():
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, "rdap-dns.json")
    if not os.path.exists(p) or time.time() - os.path.getmtime(p) > 7 * 86400:
        try:
            data = urllib.request.urlopen(urllib.request.Request("https://data.iana.org/rdap/dns.json", headers=UA), timeout=20).read()
            open(p, "wb").write(data)
        except Exception:
            if not os.path.exists(p): return {}
    m = {}
    for tlds, urls in json.load(open(p)).get("services", []):
        url = next((u for u in urls if u.startswith("https")), urls[0])
        for t in tlds: m[t.lower()] = url.rstrip("/") + "/"
    return m


def sem(host):
    with _lock:
        if host not in _host_sem: _host_sem[host] = threading.Semaphore(3)
        return _host_sem[host]


def rdap(base, domain, tries=4):
    url = base + "domain/" + domain
    host = url.split("/")[2]
    for attempt in range(tries):
        with sem(host):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=15) as r:
                    return "taken" if r.status == 200 else "unknown"
            except urllib.error.HTTPError as e:
                if e.code == 404: return "free"
                if e.code not in (429, 500, 502, 503, 504): return "unknown"
            except Exception:
                pass
        time.sleep(1.5 * (attempt + 1))
    return "unknown"


def whois_query(server, q, timeout=15):
    with socket.create_connection((server, 43), timeout=timeout) as s:
        s.sendall((q + "\r\n").encode())
        chunks = []
        while True:
            b = s.recv(4096)
            if not b: break
            chunks.append(b)
    return b"".join(chunks).decode("utf-8", "ignore")


def whois_server(tld):
    with _lock:
        if tld in _whois_server: return _whois_server[tld]
    try:
        m = re.search(r"^(?:refer|whois):\s*(\S+)", whois_query("whois.iana.org", tld), re.M | re.I)
        srv = m.group(1) if m else None
    except Exception:
        srv = None
    with _lock: _whois_server[tld] = srv
    return srv


def whois(domain, tld, tries=3):
    srv = whois_server(tld)
    if not srv: return "unknown"
    for attempt in range(tries):
        with sem(srv):
            try:
                txt = whois_query(srv, domain)
                if FREE_WHOIS.search(txt): return "free"
                if re.search(r"domain name:|registrar:|creation date|created:|registered:|nserver|name server", txt, re.I): return "taken"
                if re.search(r"limit|exceeded|try again", txt, re.I): raise RuntimeError("rate limited")
                return "unknown"
            except Exception:
                pass
        time.sleep(2 * (attempt + 1))
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
    ap.add_argument("--tld", default="com", help="comma list the user picked, e.g. com,ai,app,io")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out")
    a = ap.parse_args()
    if not a.input and not a.names: ap.error("give a file or --names")
    recs = load(a.input) if a.input else [{"name": n.strip().lower()} for n in a.names.split(",") if n.strip()]
    tlds = [t.strip().lstrip(".").lower() for t in a.tld.split(",") if t.strip()]
    boot = bootstrap()
    how = {t: ("rdap" if t in boot else "whois") for t in tlds}

    def run(job):
        i, t = job
        d = f"{recs[i]['name']}.{t}"
        s = rdap(boot[t], d) if how[t] == "rdap" else whois(d, t)
        return i, t, d, s

    results = []
    with ThreadPoolExecutor(a.workers) as ex:
        for i, t, d, s in ex.map(run, [(i, t) for i in range(len(recs)) for t in tlds]):
            r = dict(recs[i]); r.update({"domain": d, "tld": t, "status": s}); results.append(r)
    counts = {s: sum(1 for r in results if r["status"] == s) for s in ("free", "taken", "unknown")}
    via = ", ".join(f".{t} {how[t]}" for t in tlds)
    if a.out:
        json.dump(results, open(a.out, "w"), indent=1)
        print(f"{len(results)} checked -> {a.out}  free:{counts['free']} taken:{counts['taken']} unknown:{counts['unknown']}  ({via})")
    else:
        for r in results: print(f"{r['status']:8} {r['domain']}")
        print(f"free:{counts['free']} taken:{counts['taken']} unknown:{counts['unknown']}  ({via})")
    if counts["unknown"]:
        print("some lookups did not answer clearly; re-run those before reporting", file=sys.stderr)


if __name__ == "__main__":
    main()
