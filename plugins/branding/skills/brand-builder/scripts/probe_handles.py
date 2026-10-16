#!/usr/bin/env python3
"""Check whether a handle looks free on public platforms, without logging in.

Usage:
  probe_handles.py trepil [cirnio ...]

Reports free, taken or unknown per platform. Instagram, X, Threads and Reddit render
with JavaScript or block anonymous requests, so they come back unknown: tell the user to
check those by hand. A profile that exists but is empty still counts as taken.
"""
import json, re, sys, urllib.error, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36"}


def get(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(600000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def github(h):
    c, _ = get(f"https://github.com/{h}")
    return {404: "free", 200: "taken"}.get(c, "unknown")


def linkedin(h):
    c, _ = get(f"https://www.linkedin.com/company/{h}")
    return {404: "free", 200: "taken"}.get(c, "unknown")


def tiktok(h):
    c, b = get(f"https://www.tiktok.com/@{h}")
    if "find this account" in b: return "free"
    return "taken" if f'"uniqueId":"{h}"' in b else "unknown"


def youtube(h):
    c, b = get(f"https://www.youtube.com/@{h}")
    if c == 404: return "free"
    m = re.search(r'"canonicalBaseUrl":"/@([^"]+)"', b)
    if c == 200 and m and m.group(1).lower() == h.lower():
        t = re.search(r"<title>([^<]*)</title>", b)
        return "taken" + (f" ({t.group(1).replace(' - YouTube', '').strip()})" if t else "")
    return "unknown"


def bluesky(h):
    c, b = get(f"https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={h}.bsky.social")
    if c == 200 and '"did"' in b:
        try: return "taken (" + (json.loads(b).get("displayName") or h) + ")"
        except Exception: return "taken"
    return "free" if c == 400 else "unknown"


CHECKS = [("GitHub", github), ("TikTok", tiktok), ("YouTube", youtube), ("Bluesky", bluesky), ("LinkedIn company", linkedin)]


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"): sys.exit(__doc__)
    for h in sys.argv[1:]:
        print(f"== @{h}")
        for name, fn in CHECKS: print(f"  {name:17} {fn(h)}")
        for name in ("Instagram", "X", "Threads", "Reddit"): print(f"  {name:17} unknown (check by hand)")


if __name__ == "__main__":
    main()
