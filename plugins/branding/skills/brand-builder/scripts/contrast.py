#!/usr/bin/env python3
"""WCAG contrast ratios for colour pairs.

Usage:
  contrast.py "#15171C/#F6C445" "#5D616B/#F7F7F4" ...
  contrast.py --palette "#5B3CC4,#F4E04D,#17142B,#F5F3FB"     # every pair in a palette

Pass: body text 4.5:1, large text and marks 3:1. Exits 1 if any listed pair is under 3:1.
"""
import itertools, sys


def lum(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def ratio(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True)
    return (x + .05) / (y + .05)


def verdict(r):
    return "text ok" if r >= 4.5 else "large/marks only" if r >= 3 else "FAIL"


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"): sys.exit(__doc__)
    pairs = []
    if args[0] == "--palette":
        cols = [c.strip() for c in args[1].split(",")]
        pairs = list(itertools.combinations(cols, 2))
    else:
        pairs = [tuple(p.split("/")) for p in args]
    worst = 99
    for a, b in pairs:
        r = ratio(a, b); worst = min(worst, r)
        print(f"{a} on {b}: {r:5.2f}  {verdict(r)}")
    if args[0] != "--palette" and worst < 3: sys.exit(1)


if __name__ == "__main__":
    main()
