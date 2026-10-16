#!/usr/bin/env python3
"""Score free names for sound, look, syllables and ending, ready for the sheet.

Usage:
  score_names.py checked.json --out scored.json [--tlds com,ai,app] [--require com]
                 [--ratings ratings.json] [--all]

Groups the per-TLD results by name. A name is kept when at least one of the checked TLDs is
free (or the --require TLD is free), unless --all. "free" lists the free TLDs in the order
given by --tlds (default: the order they were checked), and "dom" is the first of them. A ratings file overrides the
heuristics for names you have judged by ear:
  {"vamlin": {"sound": 5, "look": 4, "tier": "best", "say": "VAM-lin"}}
Tiers: best, good, okay, hard. Without a rating the tier comes from the scores.
"""
import argparse, json, re

V = "aeiouy"


def ending(n, display):
    if display.endswith("HQ"): return "hq"
    if len(display) >= 3 and display[-2:].isupper() and display[-3].islower(): return "two"
    if len(display) >= 2 and display[-1].isupper() and display[-2].islower(): return "one"
    if n.endswith("io"): return "io"
    if n.endswith("ly"): return "ly"
    if re.search(r"(ix|ox|ux|um|ex|ena|ivo|ani|ora)$", n): return "made"
    return "plain"


def syl_root(s):
    s = re.sub(r"io$", "i-o", s)
    return max(1, len(re.findall(r"[aeiou]+|y$", s)))


def syllables(n, e):
    if e == "one": return syl_root(n[:-1]) + 1
    if e in ("hq", "two"): return syl_root(n[:-2]) + 2
    return syl_root(n)


def sound(n, e):
    s = 3.0
    if n[-1] in "aoi": s += 0.8
    elif n.endswith("ly"): s += 0.6
    s += min(1.2, sum(n.count(c) for c in "lmnrv") * 0.3)
    s -= sum(n.count(c) for c in "xqzkj") * 0.5
    s -= max(0, n.count("u") - 1) * 0.7
    if re.search(r"[^aeiouy]{3}", n): s -= 1
    if re.search(r"([^aeiou])[aeiou]\1", n): s -= 0.8
    if "lk" in n: s -= 0.8
    if e in ("two",): s -= 0.3
    return int(max(1, min(5, round(s))))


def look(n, e):
    s = 3.0
    cv = "".join("v" if c in V else "c" for c in n)
    if re.fullmatch(r"(cv)+c?|c(vc)+v?|ccv(cv)+c?", cv): s += 1
    if "ccc" in cv: s -= 1
    if re.search(r"(.)\1", n): s -= 1
    if sum(n.count(c) for c in "oa") >= 2: s += 0.5
    if sum(n.count(c) for c in "jwqx") >= 2: s -= 1
    if re.search(r"[aeiou](ix|ox)$", n): s -= 1
    if e in ("hq", "one"): s += 0.5
    if len(n) == 5: s += 0.5
    return int(max(1, min(5, round(s))))


def say(n):
    idx = [i for i, c in enumerate(n) if c in V]
    cuts = [b if b - a - 1 == 0 else b - 1 for a, b in zip(idx, idx[1:])]
    parts, p = [], 0
    for c in cuts: parts.append(n[p:c]); p = c
    parts.append(n[p:])
    return "-".join(x for x in parts if x)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input"); ap.add_argument("--out", required=True)
    ap.add_argument("--ratings"); ap.add_argument("--all", action="store_true")
    ap.add_argument("--tlds", help="preference order of TLDs, e.g. com,ai,app")
    ap.add_argument("--require", help="keep only names where this TLD is free, e.g. com")
    a = ap.parse_args()
    data = json.load(open(a.input))
    rat = json.load(open(a.ratings)) if a.ratings else {}
    order = [t.strip().lstrip(".") for t in a.tlds.split(",")] if a.tlds else []
    groups = {}
    for r in data:
        n = r["name"].lower()
        g = groups.setdefault(n, {"rec": r, "st": {}})
        tld = r.get("tld") or (r.get("domain", n + ".com").split(".", 1)[1] if "." in r.get("domain", "") else "com")
        if tld not in order: order.append(tld)
        g["st"][tld] = r.get("status", "free")
    out = []
    for n, g in groups.items():
        r = g["rec"]
        free = [t for t in order if g["st"].get(t) == "free"]
        if not a.all and (not free or (a.require and a.require not in free)): continue
        disp = r.get("display") or n.capitalize()
        e = ending(n, disp)
        so, lo = sound(n, e), look(n, e)
        x = rat.get(n, {})
        so, lo = x.get("sound", so), x.get("look", lo)
        tier = x.get("tier") or ("best" if so >= 5 and lo >= 4 else "good" if so >= 4 else "okay" if so >= 3 else "hard")
        out.append({"n": n, "d": disp, "dom": n + "." + (free[0] if free else order[0]), "free": free, "style": r.get("style", ""),
                    "e": e, "sy": syllables(n, e), "so": so, "lo": lo, "t": tier, "s": x.get("say", say(n))})
    order = {"best": 0, "good": 1, "okay": 2, "hard": 3}
    out.sort(key=lambda x: (order[x["t"]], -(x["so"] + x["lo"]), x["n"]))
    json.dump(out, open(a.out, "w"), indent=1)
    c = {t: sum(1 for x in out if x["t"] == t) for t in order}
    print(f"{len(out)} names -> {a.out}  " + "  ".join(f"{k}:{v}" for k, v in c.items()))


if __name__ == "__main__":
    main()
