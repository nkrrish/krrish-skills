#!/usr/bin/env python3
"""Generate candidate brand names in several styles.

Usage:
  gen_names.py --styles coined,formula,letter,pair,affix --count 900 \
      [--seeds cue,nod,memo] [--prefixes say,meet] [--suffixes hq,labs] \
      [--min-len 5] [--max-len 8] [--avoid granola,otter] [--exclude seen.txt] \
      [--seed 7] --out names.json

Output: a JSON list of {"name", "style", "display"} plus "brand" when the domain carries a
prefix or a domain-only suffix (heyjova.com and jovahq.com both have brand "jova"). "display"
is how the brand is written (GlimoQ, Jova); "name" is the lowercase domain label.
"""
import argparse, json, random, re, sys

V = "aeiou"
ONSETS = list("bdfgklmnprstvz") + ["br", "cl", "fl", "gl", "pl", "tr", "kr", "sk", "sn", "sp", "st"]
SOFT = list("lmnrv")
MIDS = ["lv", "rn", "rv", "lm", "nv", "lk", "rm", "ln", "mb", "nd", "lb", "nt", "sk", "mp"]
FORMULA_ENDS = ["io", "ix", "um", "a", "o", "ena", "ora", "ivo", "ani", "ly"]
ONE_LETTERS = list("qmxkvz")
PAIRS = ["hq", "ly", "io", "ix", "ox", "ux", "km", "mx", "qo"]
# Suffixes that live only in the domain: the brand is the root (Tiko on tikohq.com).
DOMAIN_ONLY = {"hq", "labs", "app", "hub", "kit", "ai"}
BAD = ["fuk", "fuc", "sex", "cum", "tit", "nig", "fag", "ass", "kkk", "shit", "poo", "pee",
       "dik", "dic", "cok", "gay", "nazi", "rape", "die", "kil", "porn", "anal", "jiz", "wank",
       "puta", "merd", "kak", "lez", "piss", "crap", "dum", "slut"]


def ok_shape(n, min_len, max_len):
    if not (min_len <= len(n) <= max_len): return False
    if re.search(r"(.)\1", n): return False
    core = n[2:] if n[:2] in {"br", "cl", "fl", "gl", "pl", "tr", "kr", "sk", "sn", "sp", "st"} else n
    if re.search(r"[^aeiouy]{3}", core): return False
    if re.search(r"[aeiou]{3}", n): return False
    if re.search(r"([^aeiou])[aeiou]\1", n): return False  # sing-song repeats: krurla, lalnio
    return not any(b in n for b in BAD)


def lev(a, b):
    p = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        c = [i]
        for j, cb in enumerate(b, 1):
            c.append(min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (ca != cb)))
        p = c
    return p[-1]


def coined(r):
    o, v = r.choice(ONSETS), r.choice(V)
    s = r.random()
    if s < .4: return o + v + r.choice(SOFT) + r.choice("bdgkmnptvl") + r.choice("aoi") + r.choice(["n", "l", "r", ""])
    if s < .7: return o + v + r.choice("bdgkmnptvl") + r.choice(V) + r.choice(["n", "l", "r", "x", "m"])
    return o + v + r.choice(SOFT) + r.choice(["ly", "ra", "ro", "ri", "la", "lo", "vo", "va", "mi", "mo", "no", "ni"])


def formula(r):
    return r.choice(list("bcdfghjklmnprstvwz")) + r.choice(V) + r.choice(MIDS[:8]) + r.choice(FORMULA_ENDS)


def soft_root(r):
    c = list("bdfgklmnprstvz")
    return r.choice(c) + r.choice(V) + r.choice(SOFT) + r.choice("aoi")


def style_display(n, style):
    if style == "letter": return n[:-1].capitalize() + n[-1].upper()
    if style == "pair" and n[-2:] not in ("ly", "io", "ix", "ox"): return n[:-2].capitalize() + n[-2:].upper()
    return n.capitalize()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--styles", default="coined,formula,letter,pair,affix")
    ap.add_argument("--count", type=int, default=900)
    ap.add_argument("--seeds", default="", help="comma list of short real words for the product (roots)")
    ap.add_argument("--prefixes", default="say,meet,with,its,the,hello")
    ap.add_argument("--suffixes", default="hq,labs")
    ap.add_argument("--min-len", type=int, default=5)
    ap.add_argument("--max-len", type=int, default=8)
    ap.add_argument("--avoid", default="", help="brands to stay at least 2 edits away from")
    ap.add_argument("--exclude", help="file of names already tried, one per line")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    r = random.Random(a.seed)
    styles = [s.strip() for s in a.styles.split(",") if s.strip()]
    seeds = [s.strip().lower() for s in a.seeds.split(",") if s.strip()]
    avoid = [s.strip().lower() for s in a.avoid.split(",") if s.strip()]
    seen = set()
    if a.exclude:
        seen = {l.strip().lower() for l in open(a.exclude) if l.strip()}
    out, names = [], set()

    def add(n, style, check_shape=True, brand=None):
        n = n.lower()
        if n in names or n in seen: return
        if check_shape and not ok_shape(n, a.min_len, a.max_len): return
        if not check_shape and not (a.min_len <= len(n) <= max(a.max_len, 12)): return
        if any(lev(n, b) < 2 for b in avoid): return
        rec = {"name": n, "style": style, "display": style_display(n, style)}
        if brand and brand != n: rec.update(brand=brand, display=brand.capitalize())
        names.add(n); out.append(rec)

    per = max(1, a.count // max(1, len(styles)))
    for st in styles:
        start, tries = len(out), 0
        while len(out) - start < per and tries < per * 200:
            tries += 1
            if st == "coined": add(coined(r), st)
            elif st == "formula": add(formula(r), st)
            elif st == "letter":
                root = r.choice(seeds) if seeds and r.random() < .3 else soft_root(r)
                add(root + r.choice(ONE_LETTERS), st, check_shape=False)
            elif st == "pair":
                root = r.choice(seeds) if seeds and r.random() < .3 else soft_root(r)
                suf = r.choice(PAIRS)
                add(root + suf, st, check_shape=False, brand=root if suf in DOMAIN_ONLY else None)
            elif st == "affix":
                if not seeds: break
                w = r.choice(seeds)
                if r.random() < .5: add(r.choice(a.prefixes.split(",")).strip() + w, st, check_shape=False, brand=w)
                else:
                    suf = r.choice(a.suffixes.split(",")).strip()
                    add(w + suf, st, check_shape=False, brand=w if suf in DOMAIN_ONLY else None)
            else:
                sys.exit(f"unknown style: {st}")
    json.dump(out, open(a.out, "w"), indent=1)
    by = {}
    for x in out: by[x["style"]] = by.get(x["style"], 0) + 1
    print(f"{len(out)} names -> {a.out}  " + "  ".join(f"{k}:{v}" for k, v in by.items()))


if __name__ == "__main__":
    main()
