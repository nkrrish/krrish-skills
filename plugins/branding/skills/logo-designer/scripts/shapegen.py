#!/usr/bin/env python3
"""
shapegen.py — parametric mark generator.

Builds marks from geometric systems rather than freehand paths. Overlapping
shapes of one fill visually union, so a rosette or gooey cluster needs no
boolean library.

  shapegen.py truchet  --seed 7  --n 3
  shapegen.py rosette  --k 8 --ratio 0.42
  shapegen.py cluster  --seed 3
  shapegen.py checker  --n 3 --seed 2
  shapegen.py sheet    --out sheet/        # many variants at once

Every mark is a single flat fill on a transparent ground, 0..100 viewBox,
which is what the skill's monochrome-template rule requires.
"""
import argparse, math, os, random

V = 100.0          # viewBox
M = 8.0            # safe margin


def svg(body, fill="#111"):
    return (f'<svg viewBox="0 0 {V:g} {V:g}" xmlns="http://www.w3.org/2000/svg">'
            f'<g id="icon" fill="{fill}">{body}</g></svg>')


# ---------------------------------------------------------------- truchet ---
def quarter(cx, cy, s, dx, dy):
    """Quarter disc of radius s centred on a cell corner, filling one quadrant."""
    sweep = 1 if dx * dy > 0 else 0
    return (f'<path d="M{cx:g} {cy:g}L{cx+dx*s:g} {cy:g}'
            f'A{s:g} {s:g} 0 0 {sweep} {cx:g} {cy+dy*s:g}Z"/>')


def truchet(n=3, seed=0, density=0.62):
    """Grid of quarter-disc / square / empty tiles — the core shapes.gallery system."""
    rnd = random.Random(seed)
    s = (V - 2 * M) / n
    out = []
    corners = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for r in range(n):
        for c in range(n):
            x, y = M + c * s, M + r * s
            if rnd.random() > density:
                continue
            kind = rnd.choice(["q", "q", "q", "sq", "disc"])
            if kind == "sq":
                out.append(f'<rect x="{x:g}" y="{y:g}" width="{s:g}" height="{s:g}"/>')
            elif kind == "disc":
                out.append(f'<circle cx="{x+s/2:g}" cy="{y+s/2:g}" r="{s/2:g}"/>')
            else:
                dx, dy = rnd.choice(corners)
                cx = x + (s if dx < 0 else 0)
                cy = y + (s if dy < 0 else 0)
                out.append(quarter(cx, cy, s, dx, dy))
    return "".join(out)


# ---------------------------------------------------------------- rosette ---
def rosette(k=8, ratio=0.42, core=0.0):
    """k circles on a ring; overlapping fills union into a lobed flower."""
    R = (V / 2 - M) / (1 + ratio)
    r = R * ratio
    out = []
    if core > 0:
        out.append(f'<circle cx="{V/2:g}" cy="{V/2:g}" r="{R*core:g}"/>')
    for i in range(k):
        a = 2 * math.pi * i / k - math.pi / 2
        out.append(f'<circle cx="{V/2 + R*math.cos(a):.3f}" '
                   f'cy="{V/2 + R*math.sin(a):.3f}" r="{r:.3f}"/>')
    return "".join(out)


# ---------------------------------------------------------------- cluster ---
def cluster(seed=0, n=5):
    """Off-centre gooey union — unequal radii give the focal point."""
    rnd = random.Random(seed)
    out, placed = [], []
    for i in range(n):
        for _ in range(200):
            r = rnd.uniform(9, 22) if i else rnd.uniform(17, 24)
            cx = rnd.uniform(M + r, V - M - r)
            cy = rnd.uniform(M + r, V - M - r)
            # must touch the mass without swallowing a neighbour
            if not placed:
                break
            ok = any(math.hypot(cx - px, cy - py) < (r + pr) * 0.92 for px, py, pr in placed)
            far = all(math.hypot(cx - px, cy - py) > abs(r - pr) + 4 for px, py, pr in placed)
            if ok and far:
                break
        placed.append((cx, cy, r))
        out.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>')
    return "".join(out)


# ---------------------------------------------------------------- checker ---
def checker(n=3, seed=0, disc=True):
    """Alternating cells with a disc counterpoint — positive/negative rhythm."""
    rnd = random.Random(seed)
    s = (V - 2 * M) / n
    out = []
    for r in range(n):
        for c in range(n):
            x, y = M + c * s, M + r * s
            if (r + c) % 2 == 0:
                out.append(f'<rect x="{x:g}" y="{y:g}" width="{s:g}" height="{s:g}"/>')
            elif disc and rnd.random() < 0.5:
                out.append(f'<circle cx="{x+s/2:g}" cy="{y+s/2:g}" r="{s*0.30:g}"/>')
    return "".join(out)



# ------------------------------------------------------------- superellipse ---
def _superellipse_pts(cx, cy, a, b, n, steps=32):
    """|x/a|^n + |y/b|^n = 1 — the squircle. n=2 circle, 4 Apple-ish, 8 near-square."""
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        ct, st = math.cos(t), math.sin(t)
        x = math.copysign(abs(ct) ** (2.0 / n), ct) * a
        y = math.copysign(abs(st) ** (2.0 / n), st) * b
        pts.append((cx + x, cy + y))
    return pts


def _smooth_path(pts, close=True):
    """Catmull-Rom through the points, emitted as cubic Beziers (C2 smooth)."""
    m = len(pts)
    d = [f"M{pts[0][0]:.2f} {pts[0][1]:.2f}"]
    for i in range(m if close else m - 1):
        p0 = pts[(i - 1) % m]; p1 = pts[i]; p2 = pts[(i + 1) % m]; p3 = pts[(i + 2) % m]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{c1[0]:.2f} {c1[1]:.2f} {c2[0]:.2f} {c2[1]:.2f} {p2[0]:.2f} {p2[1]:.2f}")
    return " ".join(d) + ("Z" if close else "")


def squircle(exp=4.0, inset=0.0):
    """A true superellipse — continuous curvature, unlike rect rx which jumps at the
    tangent point. This is why an app icon drawn with rx looks subtly cheaper."""
    r = (V / 2 - M) * (1 - inset)
    return f'<path d="{_smooth_path(_superellipse_pts(V/2, V/2, r, r, exp))}"/>'


# ------------------------------------------------------------------- carve ---
def _circle_d(cx, cy, r):
    return (f"M{cx-r:.2f} {cy:.2f}A{r:.2f} {r:.2f} 0 1 0 {cx+r:.2f} {cy:.2f}"
            f"A{r:.2f} {r:.2f} 0 1 0 {cx-r:.2f} {cy:.2f}Z")


def carve(exp=4.0, seed=0, cuts=2):
    """Real subtraction: one path, fill-rule evenodd. Where subpaths overlap the
    fill cancels, so the cuts are true holes — they survive a monochrome flatten,
    which a same-colour shape laid on top does not."""
    rnd = random.Random(seed)
    subs = [_smooth_path(_superellipse_pts(V / 2, V / 2, V / 2 - M, V / 2 - M, exp))]
    for _ in range(cuts):
        r = rnd.uniform(11, 20)
        ang = rnd.uniform(0, 2 * math.pi)
        rad = rnd.uniform(6, 26)
        subs.append(_circle_d(V / 2 + rad * math.cos(ang), V / 2 + rad * math.sin(ang), r))
    return f'<path fill-rule="evenodd" d="{" ".join(subs)}"/>'


GEN = {"truchet": truchet, "rosette": rosette, "cluster": cluster,
       "checker": checker, "squircle": squircle, "carve": carve}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=list(GEN) + ["sheet"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--ratio", type=float, default=0.42)
    ap.add_argument("--core", type=float, default=0.0)
    ap.add_argument("--density", type=float, default=0.62)
    ap.add_argument("--exp", type=float, default=4.0, help="superellipse exponent")
    ap.add_argument("--cuts", type=int, default=2)
    ap.add_argument("--fill", default="#111")
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    if a.mode == "sheet":
        os.makedirs(a.out or "shapes", exist_ok=True)
        d = a.out or "shapes"
        made = []
        for s in range(6):
            made.append((f"truchet-{s}.svg", truchet(3, s, a.density)))
        for k, rt in ((6, .46), (8, .40), (5, .52), (12, .30)):
            made.append((f"rosette-{k}.svg", rosette(k, rt, core=.72)))
        for s in range(3):
            made.append((f"cluster-{s}.svg", cluster(s)))
        for s in range(3):
            made.append((f"checker-{s}.svg", checker(3, s)))
        for name, body in made:
            open(os.path.join(d, name), "w").write(svg(body, a.fill))
        print(f"wrote {len(made)} shapes to {d}/")
        return

    kw = {}
    if a.mode == "truchet":  kw = dict(n=a.n, seed=a.seed, density=a.density)
    if a.mode == "rosette":  kw = dict(k=a.k, ratio=a.ratio, core=a.core)
    if a.mode == "cluster":  kw = dict(seed=a.seed)
    if a.mode == "checker":  kw = dict(n=a.n, seed=a.seed)
    if a.mode == "squircle": kw = dict(exp=a.exp)
    if a.mode == "carve":    kw = dict(exp=a.exp, seed=a.seed, cuts=a.cuts)
    out = svg(GEN[a.mode](**kw), a.fill)
    if a.out:
        open(a.out, "w").write(out)
        print(f"wrote {a.out}")
    else:
        print(out)


if __name__ == "__main__":
    main()
