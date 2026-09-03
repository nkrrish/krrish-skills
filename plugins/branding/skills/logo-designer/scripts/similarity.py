#!/usr/bin/env python3
"""
similarity.py — is this mark already somebody's logo?

Checks a candidate against ~3,450 real brand marks (the CC0 `simple-icons` set).
Silhouette-based, so it catches a mark you have re-derived in a different colour
or at a different rotation-free scale.

  similarity.py build                 # one-time, caches to ~/.cache/logo-designer
  similarity.py check mark.svg        # top matches
  similarity.py check logos/concepts/ # every concept in a folder

This is a prior-art smoke test, not a trademark search. A clean result means
"not obviously someone else's mark", nothing more. Clearing a logo for real use
is a lawyer's job.
"""
import concurrent.futures as cf, json, os, shutil, subprocess, sys, tarfile, tempfile, urllib.request

CACHE = os.path.expanduser("~/.cache/logo-designer")
DB = os.path.join(CACHE, "corpus.json")
N = 16                      # fingerprint is N x N grayscale


def _render(svg):
    """SVG -> N*N grayscale bytes of the alpha silhouette, or None."""
    for cmd in (["rsvg-convert", "-w", "64", "-h", "64", svg],   # writes PNG to stdout
                ["magick", "-background", "none", "-density", "300", svg,
                 "-resize", "64x64", "png:-"]):
        try:
            png = subprocess.run(cmd, capture_output=True, timeout=20).stdout
            if not png:
                continue
            out = subprocess.run(
                ["magick", "png:-", "-alpha", "extract", "-resize", f"{N}x{N}!",
                 "-depth", "8", "gray:-"],
                input=png, capture_output=True, timeout=20).stdout
            if len(out) >= N * N:
                return list(out[:N * N])
        except Exception:
            pass
    return None


def build():
    os.makedirs(CACHE, exist_ok=True)
    tmp = tempfile.mkdtemp()
    print("fetching simple-icons (CC0)…")
    meta = json.load(urllib.request.urlopen(
        "https://registry.npmjs.org/simple-icons"))
    url = meta["versions"][meta["dist-tags"]["latest"]]["dist"]["tarball"]
    tgz = os.path.join(tmp, "si.tgz")
    urllib.request.urlretrieve(url, tgz)
    with tarfile.open(tgz) as t:
        t.extractall(tmp, filter="data")
    svgs = []
    for root, _, files in os.walk(tmp):
        svgs += [os.path.join(root, f) for f in files if f.endswith(".svg")]
    print(f"fingerprinting {len(svgs)} brand marks…")

    db = {}
    with cf.ThreadPoolExecutor(max_workers=min(16, (os.cpu_count() or 4) * 3)) as ex:
        for path, fp in zip(svgs, ex.map(_render, svgs)):
            if fp:
                db[os.path.splitext(os.path.basename(path))[0]] = fp
    json.dump({"version": meta["dist-tags"]["latest"], "n": N, "marks": db}, open(DB, "w"))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"cached {len(db)} marks -> {DB}")


def _dist(a, b):
    """Mean absolute difference, 0 (identical) .. 1 (opposite)."""
    return sum(abs(x - y) for x, y in zip(a, b)) / (len(a) * 255.0)


def check(targets, top=5):
    if not os.path.exists(DB):
        print("no corpus cached — run:  similarity.py build", file=sys.stderr)
        return 3
    d = json.load(open(DB))
    marks = d["marks"]
    files = []
    for t in targets:
        if os.path.isdir(t):
            files += sorted(os.path.join(t, f) for f in os.listdir(t) if f.endswith(".svg"))
        else:
            files.append(t)
    worst = 1.0
    for f in files:
        fp = _render(f)
        print(f"\n{os.path.basename(f)}")
        if not fp:
            print("  render failed")
            continue
        hits = sorted(((_dist(fp, v), k) for k, v in marks.items()))[:top]
        worst = min(worst, hits[0][0])
        for score, name in hits:
            flag = ("  <-- TOO CLOSE" if score < 0.055 else
                    "  <-- check by eye" if score < 0.085 else "")
            print(f"  {score:.3f}  {name}{flag}")
    print(f"\nclosest match overall: {worst:.3f}"
          f"   (<0.055 rework it; 0.055-0.085 look at it; >0.085 clear)")
    print("Prior-art smoke test only — not a trademark search.")
    return 1 if worst < 0.055 else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] not in ("build", "check"):
        print(__doc__)
        sys.exit(2)
    sys.exit(build() or 0 if a[0] == "build" else check(a[1:] or ["."]))
