#!/usr/bin/env python3
"""Build the shortlist page: a light brand card, recordings, research and optional
in-use mockups for each shortlisted name.

Usage:
  build_shortlist.py shortlist.json --out shortlist.html [--audio audio] [--fragment]
  build_shortlist.py --example > shortlist.json      # print a filled-in example to start from
  build_shortlist.py --example companion            # the same with a non-meeting product

The in-use mockups (app window, phone, chat, social post) take every visible string from
"product" (shared by all names) or the name's "inuse" (per name overrides): nav, item,
itemMeta, action, cardTitle, cardItems, quoteBy, quote, notif, homeApps, chatChannel,
chatPeople ([name, time] pairs), previewTitle, previewText, postChips, postEnd. Write them for
the user's own product; anything left out is left off the mockup. Older shortlist files with
meeting, minutes, people, planTitle, items and transcript still work.

Recordings are linked as <audio>/<key>.mp3 (meant to sound) and <audio>/<key>__read.mp3
(first read by a stranger), relative to the page; players appear only for files that exist.
Publish the audio folder next to the page.

Marks available for "mark": cluster bubble cue gloss moon wave qcheck tick zring swirl sun
orbit tri hum loopdot cueplay duo merge three echo thread. Or pass "markSvg": an SVG string
with {fg} and {ac} placeholders inside a 48x48 viewBox.
"""
import argparse, html, json, os, sys

e = html.escape

MEETING = {"name": "meeting notes",
           "nav": ["Meetings", "Voice memos", "Plans", "Settings"],
           "item": "Halden pricing call", "itemMeta": "32 min · recorded on this Mac · 4 people", "action": "Share",
           "cardTitle": "The plan", "cardItems": ["Hold the price, add onboarding · Priya", "Send Halden the revised quote · Sam", "Book follow-up for the 24th · Mia"],
           "quoteBy": "Priya · 12:04", "quote": "So if we hold the price but add onboarding, does that work for you?",
           "notif": "The plan from Halden pricing call is ready", "homeApps": ["Calendar", "Mail"],
           "chatChannel": "#team", "chatPeople": [["Priya Shah", "10:42"], ["Sam Kerr", "10:44"]],
           "previewTitle": "Halden pricing call · notes by Sam", "previewText": "The plan: Hold the price, add onboarding, and 2 more.",
           "postChips": [["MI", "Mia"], ["JO", "Jo"], ["YOU", "You"]], "postEnd": "no bot"}

COMPANION = {"name": "AI companion",
             "nav": ["Talk", "Journal", "Reminders", "Settings"],
             "item": "Tuesday evening check-in", "itemMeta": "12 min · voice · with Juno", "action": "Save to journal",
             "cardTitle": "What you said you'd try", "cardItems": ["Walk after lunch, no phone", "Text Maya back tonight", "Bed by 11, check in at 10:30"],
             "quoteBy": "Juno · 9:41 pm", "quote": "That sounds like a lot to carry. Want to start with the part about work?",
             "notif": "Juno: it's 10:30. How did the walk go?", "homeApps": ["Notes", "Health"],
             "chatChannel": "Ana Ruiz", "chatPeople": [["Ana Ruiz", "21:12"], ["You", "21:15"]],
             "previewTitle": "Journal · Tuesday", "previewText": "Felt calmer after talking it through. Three small things for tomorrow.",
             "postChips": [], "postEnd": ""}

EXAMPLE = {
  "title": "Name shortlist", "date": "16 Oct 2026",
  "product": MEETING,
  "names": [{
    "key": "trepil", "display": "trepil", "domain": "trepil.com", "status": ".com free on 16 Oct 2026", "pinned": True,
    "font": "Red Hat Display", "weight": 800, "tracking": -0.03, "mark": "three",
    "colors": {"primary": ["Violet", "#5B3CC4", "logo, buttons"], "accent": ["Lemon", "#F4E04D", "the third point"],
               "ink": ["Ink", "#17142B", "text"], "light": ["Lilac paper", "#F5F3FB", "background"]},
    "tiles": {"t1": {"bg": "#F5F3FB", "fg": "#5B3CC4", "ac": "#17142B", "wm": "#17142B"},
              "t2": {"bg": "#5B3CC4", "fg": "#FFFFFF", "ac": "#F4E04D", "wm": "#FFFFFF"}},
    "why": "Three bars getting shorter: the three takeaways every call ends with.",
    "say": "TRIP-ul, like triple",
    "research": {"apps": "No app named Trepil found.", "appsLevel": "none", "google": "Nothing ranks for the exact word.",
                 "googleLevel": "Light", "ownability": 3, "ownabilityWhy": "Coined and unclaimed; low US trademark risk.",
                 "meanings": "Said like triple, it means three.", "social": "TikTok, LinkedIn and Bluesky free.", "sources": []},
    "inuse": {"headline": "Every call\nends in three.", "tag": "Three takeaways from every meeting",
              "chat": "@Sam can you share the trepil notes from this morning's sprint review?", "reply": "Sure, here's the trepil link.",
              "caption": "Long call, short memory. trepil turns every meeting into three takeaways with owners.",
              "groundBg": "#5B3CC4", "groundFg": "#FFFFFF", "planBg": "#F4E04D", "planFg": "#17142B"}
  }]
}

EXAMPLES = {"meeting": EXAMPLE, "companion": {**EXAMPLE, "product": COMPANION, "names": [{**EXAMPLE["names"][0], "inuse": {
    "headline": "Someone to\ntalk it through.", "tag": "A companion that remembers",
    "chat": "how are you sleeping better lately? you seem lighter", "reply": "honestly trepil. I talk things through with it at night. this was Tuesday",
    "caption": "Some days are a lot. trepil listens, remembers what matters to you and checks in when it counts.",
    "groundBg": "#5B3CC4", "groundFg": "#FFFFFF", "planBg": "#F4E04D", "planFg": "#17142B"}}]}}


def L(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def cr(a, b):
    x, y = sorted([L(a), L(b)], reverse=True); return (x + .05) / (y + .05)


def best_text(bg, cands):
    return max(cands, key=lambda c: cr(c, bg))


def mark(kind, fg, ac, s, custom=None):
    if kind == "thread":
        return (f'<svg viewBox="0 0 49.5 40" width="{s}" height="{round(s * 40 / 49.5)}" aria-hidden="true"><path d="M3 34C10 34 14 8 26 8C36 8 36 26 27 26C20 26 21 17 30 17L45 17" '
                f'fill="none" stroke="{fg}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="45" cy="17" r="3.8" fill="{ac}"/></svg>')
    P = {
      "cluster": '<circle cx="17" cy="20" r="11" fill="{fg}"/><circle cx="31" cy="20" r="11" fill="{fg}" opacity=".55"/><circle cx="24" cy="32" r="11" fill="{ac}"/>',
      "bubble": '<path d="M8 10h32a4 4 0 0 1 4 4v18a4 4 0 0 1-4 4H22l-9 7v-7H8a4 4 0 0 1-4-4V14a4 4 0 0 1 4-4z" fill="{fg}"/><circle cx="31" cy="23" r="5" fill="{ac}"/>',
      "cue": '<path d="M34 13A15 15 0 1 0 34 35" fill="none" stroke="{fg}" stroke-width="8" stroke-linecap="round"/><circle cx="38" cy="24" r="5" fill="{ac}"/>',
      "gloss": '<rect x="5" y="5" width="38" height="38" rx="12" fill="{fg}"/><path d="M13 21a11 11 0 0 1 11-9" fill="none" stroke="{ac}" stroke-width="5" stroke-linecap="round"/>',
      "moon": '<path d="M30 6a18 18 0 1 0 12 30A15 15 0 1 1 30 6z" fill="{fg}"/><circle cx="36" cy="14" r="4" fill="{ac}"/>',
      "wave": '<rect x="7" y="17" width="8" height="14" rx="4" fill="{fg}"/><rect x="20" y="8" width="8" height="32" rx="4" fill="{fg}"/><rect x="33" y="14" width="8" height="20" rx="4" fill="{ac}"/>',
      "qcheck": '<circle cx="22" cy="22" r="14" fill="none" stroke="{fg}" stroke-width="7"/><path d="M27 33l5 5 10-12" fill="none" stroke="{ac}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>',
      "tick": '<rect x="5" y="5" width="38" height="38" rx="12" fill="{fg}"/><path d="M15 25l6 6 12-14" fill="none" stroke="{ac}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>',
      "zring": '<circle cx="24" cy="24" r="19" fill="none" stroke="{fg}" stroke-width="5"/><path d="M16 16h16L16 32h16" fill="none" stroke="{ac}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>',
      "swirl": '<path d="M24 24a3 3 0 1 1 4 3a8 8 0 1 1-9-11a13 13 0 0 1 21 6" fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round"/><circle cx="40" cy="22" r="4" fill="{ac}"/>',
      "sun": '<path d="M9 32a15 15 0 0 1 30 0z" fill="{ac}"/><rect x="5" y="34" width="38" height="5" rx="2.5" fill="{fg}"/>',
      "orbit": '<circle cx="24" cy="24" r="15" fill="none" stroke="{fg}" stroke-width="6"/><circle cx="35" cy="13" r="6" fill="{ac}"/>',
      "tri": '<path d="M10 34L24 14L38 34" fill="none" stroke="{fg}" stroke-width="4" stroke-linejoin="round"/><circle cx="10" cy="34" r="6" fill="{fg}"/><circle cx="24" cy="14" r="6" fill="{ac}"/><circle cx="38" cy="34" r="6" fill="{fg}"/>',
      "hum": '<path d="M5 24c4-10 8-10 12 0s8 10 12 0 8-10 12 0" fill="none" stroke="{fg}" stroke-width="6" stroke-linecap="round"/><circle cx="43" cy="24" r="3.5" fill="{ac}"/>',
      "loopdot": '<path d="M34.6 13.4A15 15 0 1 0 38.8 21.4" fill="none" stroke="{fg}" stroke-width="6.5" stroke-linecap="round"/><circle cx="38.4" cy="15.6" r="4.6" fill="{ac}"/>',
      "cueplay": '<path d="M12 9.5c0-3 3.2-4.9 5.8-3.4l20.5 11.9c2.6 1.5 2.6 5.3 0 6.8L17.8 36.7c-2.6 1.5-5.8-.4-5.8-3.4z" fill="{fg}"/><circle cx="36" cy="38" r="5" fill="{ac}"/>',
      "duo": '<circle cx="18" cy="24" r="11" fill="{ac}"/><circle cx="30" cy="24" r="11" fill="none" stroke="{fg}" stroke-width="5"/>',
      "merge": '<path d="M11 9c0 9 13 10 13 19v10M37 9c0 9-13 10-13 19" fill="none" stroke="{fg}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="24" cy="42" r="4.5" fill="{ac}"/>',
      "three": '<rect x="6" y="9" width="36" height="8" rx="4" fill="{fg}"/><rect x="6" y="20" width="27" height="8" rx="4" fill="{fg}"/><rect x="6" y="31" width="16" height="8" rx="4" fill="{ac}"/>',
      "echo": '<circle cx="13" cy="24" r="6" fill="{ac}"/><path d="M24 13a15 15 0 0 1 0 22M32 7a23 23 0 0 1 0 34" fill="none" stroke="{fg}" stroke-width="5" stroke-linecap="round"/>',
    }
    body = custom if custom else P.get(kind)
    if body is None: sys.exit(f"unknown mark '{kind}'")
    return f'<svg viewBox="0 0 48 48" width="{s}" height="{s}" aria-hidden="true">' + body.replace("{fg}", fg).replace("{ac}", ac) + "</svg>"


LEVEL = {"na": "Not checked", "Empty": "Nothing ranks", "Light": "A few hits", "Moderate": "Busy", "Crowded": "Crowded"}
APPS = {"na": "Not checked", "none": "Nothing found", "minor": "Near names", "conflict": "Conflict"}
NA = {"apps": "Not checked.", "appsLevel": "na", "google": "Not checked.", "googleLevel": "na", "ownability": "n/a",
      "ownabilityWhy": "Not researched.", "meanings": "", "social": "Not checked.", "sources": []}


def legacy(prod):
    """Map the older meeting-only product keys onto the generic ones."""
    p = dict(prod)
    if "meeting" in p and "item" not in p: p["item"] = p["meeting"]
    if "item" in p and "itemMeta" not in p and ("minutes" in p or "people" in p):
        p["itemMeta"] = f'{p.get("minutes", 30)} min · recorded on this Mac · {p.get("people", 3)} people'
    if "planTitle" in p and "cardTitle" not in p: p["cardTitle"] = p["planTitle"]
    if "items" in p and "cardItems" not in p: p["cardItems"] = p["items"]
    if "transcript" in p and "quote" not in p: p["quote"] = p["transcript"]
    return p


def inuse(n, C, prod, mk):
    """Every visible string comes from the product (or the name's inuse overrides): write the copy
    for the user's own product. Missing pieces are left out rather than filled with another product."""
    u = n["inuse"]; P, A, K, Lc = C["primary"][1], C["accent"][1], C["ink"][1], C["light"][1]
    g = lambda k, d="": u.get(k, prod.get(k, d))
    onP = best_text(P, ["#FFFFFF", K, Lc])
    gb, gf = u.get("groundBg", P), u.get("groundFg", best_text(u.get("groundBg", P), ["#FFFFFF", K]))
    pb, pf = u.get("planBg", A), u.get("planFg", best_text(u.get("planBg", A), [K, "#FFFFFF"]))
    font, w, ls, name, dom = n["font"], n.get("weight", 700), n.get("tracking", -0.02), n["display"], n["domain"]
    st = (f"--bp:{P};--bop:{onP};--ba:{A};--bg2:{gb};--bog:{gf};--bpa:{Lc};--bi:{K};--bpl:{pb};--bopl:{pf};--bf:'{font}',sans-serif")
    wm = f'<span style="font-family:\'{font}\',sans-serif;font-weight:{w};letter-spacing:{ls}em;color:{K};font-size:20px;line-height:1">{e(name)}</span>'
    nav = g("nav", [])
    navh = "".join((f"<b>{e(x)}</b>" if i == 0 else f"<span>{e(x)}</span>") for i, x in enumerate(nav))
    item, meta, action = g("item"), g("itemMeta"), g("action")
    ct, ci = g("cardTitle"), g("cardItems", [])
    card = f'<div class="plan"><b>{e(ct)}</b><ol>{"".join(f"<li>{e(x)}</li>" for x in ci)}</ol></div>' if ct or ci else ""
    quote = f'<div class="tr"><span>{e(g("quoteBy"))}</span><p>{e(g("quote"))}</p></div>' if g("quote") else ""
    btn = f"<button>{e(action)}</button>" if action else ""
    homes = "".join(f'<div><div class="app g"></div><span>{e(x)}</span></div>' for x in g("homeApps", []))
    people = g("chatPeople", [])
    initials = lambda nm: "".join(w[0] for w in nm.split()[:2]).upper() or "?"
    def msg(i, text, extra=""):
        if i >= len(people) or not text: return ""
        nm, tm = (people[i] + ["", ""])[:2]
        return f'<div class="msg"><div class="av{" b" if i else ""}">{e(initials(nm))}</div><div><b>{e(nm)}</b> <small>{e(tm)}</small><p>{e(text)}</p>{extra}</div></div>'
    prev = (f'<div class="unf"><div class="bar"></div><div><small>{e(name)} · {e(dom)}</small><b>{e(g("previewTitle"))}</b>'
            f'<p>{e(g("previewText"))}</p></div></div>') if g("previewTitle") else ""
    chat = (f'<div class="chat"><div class="ch">{e(g("chatChannel"))}</div>{msg(0, u.get("chat", ""))}{msg(1, u.get("reply", ""), prev)}</div>'
            if people and u.get("chat") else "")
    notif = f'<div class="notif"><div class="ic">{mk(onP, A, 18)}</div><div><b>{e(name)}</b><p>{e(g("notif"))}</p></div></div>' if g("notif") else ""
    head = "".join(f"<span>{e(x)}</span>" for x in u.get("headline", name).split("\n"))
    chips = g("postChips", [])
    seats = ""
    if chips:
        end = f'<div class="empty">{mk(gf, gf, 30)}<em>{e(g("postEnd"))}</em></div>' if g("postEnd") else ""
        seats = '<div class="seats">' + "".join(f"<div><span>{e(a)}</span>{e(b)}</div>" for a, b in chips) + end + "</div>"
    return f'''<details class="inuse" open><summary>In use · app, phone, chat, social</summary>
<div class="iu" style="{st}">
<div class="win"><div class="wbar"><i></i><i></i><i></i><span>{e(dom)}</span></div>
<div class="wbody"><aside><div class="lk">{mk(K, A, 22)}{wm}</div><nav>{navh}</nav></aside>
<main><div class="mt"><div><h4>{e(item)}</h4><p>{e(meta)}</p></div>{btn}</div>
{card}
{quote}</main></div></div>
<div class="side">
<div class="phone">{notif}
<div class="home"><div><div class="app">{mk(onP, A, 34)}</div><span>{e(name)}</span></div>{homes}</div></div>
{chat}
</div>
<div class="post"><div class="ph"><div class="pa">{mk(onP, A, 18)}</div><b>{e(name)}</b></div>
<div class="pimg"><div class="hl">{head}</div>{seats}</div>
<p class="cap"><b>{e(name)}</b> {e(u.get("caption", ""))}</p></div>
</div></details>'''


CSS = """
:root{--bg:#f4f5f2;--card:#fff;--fg:#17191d;--muted:#5b6069;--line:#e2e4de;--good:#1f6b3f;--warn:#8a5a00;--bad:#b3261e;--goodbg:#e4f1e8;--warnbg:#fbf0d9;--badbg:#fbe4e2;--body:'Instrument Sans',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141619;--card:#1c1f24;--fg:#f1f2ee;--muted:#a0a5ae;--line:#2c3038;--good:#86d6a0;--warn:#f0c46a;--bad:#ff9b92;--goodbg:#1d3326;--warnbg:#3a2f17;--badbg:#3d1f1d;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141619;--card:#1c1f24;--fg:#f1f2ee;--muted:#a0a5ae;--line:#2c3038;--good:#86d6a0;--warn:#f0c46a;--bad:#ff9b92;--goodbg:#1d3326;--warnbg:#3a2f17;--badbg:#3d1f1d;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--body);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1040px;margin:0 auto;padding-inline:20px;padding-block:40px 64px}
h1{font-size:clamp(28px,4.5vw,40px);letter-spacing:-.02em;line-height:1.1;margin:0 0 8px}
.intro{color:var(--muted);max-width:66ch;margin:0 0 24px}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{border-collapse:collapse;width:100%;min-width:560px;font-size:14px}
th,td{text-align:left;padding:10px 14px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0} th{font-size:12px;color:var(--muted);font-weight:500}
td a{color:var(--fg);font-weight:600;text-decoration:none} .sm{display:block;color:var(--muted);font-size:12.5px;font-family:var(--mono)} .mono{font-family:var(--mono);font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px;margin-top:22px;display:flex;flex-direction:column;gap:16px}
.ch{display:flex;justify-content:space-between;gap:16px;align-items:flex-start} .ch h2{margin:0;font-size:26px;letter-spacing:-.02em}
.dom{margin:2px 0 0;font-family:var(--mono);font-size:13px;color:var(--muted)} .free{font-family:var(--body);color:var(--good);margin-left:6px}
.score{text-align:right;white-space:nowrap} .score b{font-size:30px;line-height:1} .score span{display:block;font-size:12px;color:var(--muted)}
.brand{display:grid;grid-template-columns:1fr 1fr auto;gap:10px}
.tile{border-radius:12px;min-height:120px;display:flex;align-items:center;justify-content:center;gap:12px;padding:16px;min-width:0}
.tile.small{flex-direction:column;gap:6px;padding:12px 18px} .wm{line-height:1;white-space:nowrap}
.fav{width:24px;height:24px;border-radius:6px;display:flex;align-items:center;justify-content:center} .fav.big{width:56px;height:56px;border-radius:14px}
.cap{font-size:11px;color:#5b6069;font-family:var(--mono)}
.chips{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.chip{border-radius:10px;padding:10px 12px;display:flex;flex-direction:column;gap:1px;font-size:12.5px;min-height:76px;justify-content:flex-end}
.chip b{font-size:14px} .chip span{font-family:var(--mono);font-size:11.5px}
.why{margin:0;color:var(--muted);font-size:14px} .why b{color:var(--fg)}
.say{display:grid;grid-template-columns:1fr 1fr;gap:12px} .say>div{border:1px solid var(--line);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:6px;min-width:0}
.lbl{font-size:12px;color:var(--muted)} .guide{font-family:var(--mono);font-size:15px;font-weight:500} audio{width:100%;height:34px}
.facts{margin:0;display:flex;flex-direction:column;gap:10px} .facts>div{display:grid;grid-template-columns:110px 1fr;gap:12px}
dt{font-size:13px;color:var(--muted)} dd{margin:0;font-size:14px}
.pill{display:inline-block;font-size:11.5px;font-weight:600;border-radius:999px;padding:1px 8px;margin-right:4px}
.pill.na,.pill.gna{background:var(--line);color:var(--muted)}
.pill.none,.pill.gEmpty{background:var(--goodbg);color:var(--good)} .pill.minor,.pill.gLight{background:var(--warnbg);color:var(--warn)}
.pill.conflict,.pill.gModerate,.pill.gCrowded{background:var(--badbg);color:var(--bad)}
.src summary{cursor:pointer;font-size:13px;color:var(--muted)} .src ul{margin:8px 0 0;padding-left:18px;font-size:12.5px;overflow-wrap:anywhere} .src a{color:var(--muted)}
a:focus-visible,summary:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
.note{margin-top:32px;color:var(--muted);font-size:13.5px;max-width:72ch}
.inuse{border-top:1px solid var(--line);padding-top:12px} .inuse>summary{cursor:pointer;font-weight:600;font-size:14px;margin-bottom:12px}
.iu{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:12px}
.win{grid-column:1/-1;border-radius:12px;overflow:hidden;background:var(--bpa);color:var(--bi);border:1px solid rgba(0,0,0,.08)}
.wbar{display:flex;gap:6px;align-items:center;padding:8px 12px;background:rgba(0,0,0,.04)} .wbar i{width:9px;height:9px;border-radius:50%;background:rgba(0,0,0,.18)} .wbar span{margin-left:10px;font-family:var(--mono);font-size:11px;opacity:.75}
.wbody{display:grid;grid-template-columns:170px 1fr;min-height:250px}
.wbody aside{background:#fff;padding:14px;display:flex;flex-direction:column;gap:14px;border-right:1px solid rgba(0,0,0,.06)}
.lk{display:flex;align-items:center;gap:6px} .wbody nav{display:flex;flex-direction:column;gap:4px;font-size:13px}
.wbody nav b{background:var(--bg2);color:var(--bog);border-radius:7px;padding:5px 8px;font-weight:600} .wbody nav span{padding:5px 8px;opacity:.75}
.wbody main{padding:16px 18px;display:flex;flex-direction:column;gap:12px;min-width:0}
.mt{display:flex;justify-content:space-between;gap:10px;align-items:flex-start} .mt h4{margin:0;font-size:19px;font-family:var(--bf)} .mt p{margin:2px 0 0;font-size:12.5px;opacity:.75}
.mt button{background:var(--bp);color:var(--bop);border:0;border-radius:9px;padding:8px 12px;font:600 13px var(--body);white-space:nowrap}
.plan{background:var(--bpl);color:var(--bopl);border-radius:12px;padding:12px 14px;font-size:13.5px} .plan b{font-family:var(--bf);font-size:15px} .plan ol{margin:6px 0 0;padding-left:18px;line-height:1.6}
.tr{background:#fff;border-radius:10px;padding:10px 12px;font-size:13px;border:1px solid rgba(0,0,0,.06)} .tr span{font-family:var(--mono);font-size:11px;opacity:.75} .tr p{margin:3px 0 0;opacity:.8}
.side{display:flex;flex-direction:column;gap:12px;min-width:0}
.phone{border-radius:18px;background:linear-gradient(160deg,#2b3140,#151821);padding:12px;display:flex;flex-direction:column;gap:14px;color:#fff}
.notif{display:flex;gap:10px;align-items:center;background:rgba(255,255,255,.88);color:#15171c;border-radius:12px;padding:9px 10px} .notif b{font-size:12.5px} .notif p{margin:0;font-size:12px;color:#3b3f48}
.ic{width:28px;height:28px;border-radius:7px;background:var(--bp);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.home{display:flex;gap:16px;padding:0 6px 4px} .home>div{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:10.5px;color:#e8e9ec}
.app{width:48px;height:48px;border-radius:12px;background:var(--bp);display:flex;align-items:center;justify-content:center} .app.g{background:rgba(255,255,255,.18)}
.chat{border-radius:12px;background:#fff;color:#1d1c1d;border:1px solid rgba(0,0,0,.1);padding:10px 12px;display:flex;flex-direction:column;gap:10px;font-size:13px}
.chat .ch{font-weight:700;font-size:12.5px;color:#616061;display:block} .msg{display:flex;gap:8px} .msg small{color:#616061;font-size:11px} .msg p{margin:2px 0 0;line-height:1.45}
.av{width:30px;height:30px;border-radius:7px;background:#6b4f9e;color:#fff;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0} .av.b{background:#2e7d6b}
.unf{display:flex;gap:8px;margin-top:6px} .unf .bar{width:4px;border-radius:2px;background:var(--bp);flex-shrink:0} .unf small{display:block;color:#616061} .unf b{display:block;color:#1264a3;font-size:12.5px} .unf p{font-size:12px;color:#454245}
.post{grid-column:1/-1;max-width:420px;border-radius:12px;background:#fff;color:#15171c;border:1px solid rgba(0,0,0,.1);overflow:hidden}
.ph{display:flex;align-items:center;gap:8px;padding:10px 12px;font-size:13px} .pa{width:28px;height:28px;border-radius:50%;background:var(--bp);display:flex;align-items:center;justify-content:center}
.pimg{aspect-ratio:1/1;max-width:100%;background:var(--bg2);color:var(--bog);padding:26px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:space-between}
.hl{font-family:var(--bf);font-size:40px;font-weight:800;letter-spacing:-.035em;line-height:.98;display:flex;flex-direction:column}
.seats{display:grid;grid-template-columns:repeat(4,1fr);gap:7px} .seats>div{background:var(--bpa);color:var(--bi);border-radius:10px;display:flex;flex-direction:column;align-items:center;gap:4px;padding:9px 4px;font-size:10.5px}
.seats span{width:30px;height:30px;border-radius:50%;background:var(--bp);color:var(--bop);display:flex;align-items:center;justify-content:center;font-size:9.5px;font-weight:700}
.seats .empty{background:none;border:2px dashed currentColor;color:var(--bog);justify-content:center} .seats .empty em{font-style:normal;font-weight:600}
.post .cap{margin:0;padding:10px 12px 12px;font-size:13px;line-height:1.5;font-family:var(--body);color:#15171c}
@media (max-width:720px){.brand,.iu,.say{grid-template-columns:1fr}.tile.small{flex-direction:row}.chips{grid-template-columns:repeat(2,minmax(0,1fr))}.facts>div{grid-template-columns:1fr;gap:2px}.wbody{grid-template-columns:1fr}.wbody nav{display:none}.hl{font-size:30px}}
"""


def build(spec, audio_dir, page_dir):
    prod = legacy(spec.get("product", {}))
    names = spec["names"]
    pinned = [n for n in names if n.get("pinned")]
    rest = sorted([n for n in names if not n.get("pinned")],
                  key=lambda n: (-(n.get("research", NA).get("ownability") if isinstance(n.get("research", NA).get("ownability"), int) else -1), n["key"]))
    cards, rows, fonts = [], [], set()
    for n in pinned + rest:
        C = n["colors"]; P, A, K, Lc = C["primary"][1], C["accent"][1], C["ink"][1], C["light"][1]
        r = {**NA, **n.get("research", {})}
        fonts.add((n["font"], n.get("weight", 700)))
        mk = lambda fg, ac, s, n=n: mark(n.get("mark", "orbit"), fg, ac, s, n.get("markSvg"))
        f, w, ls = n["font"], n.get("weight", 700), n.get("tracking", -0.02)
        wm = lambda col, size: f'<span class="wm" style="font-family:\'{f}\',sans-serif;font-weight:{w};letter-spacing:{ls}em;color:{col};font-size:{size}px">{e(n["display"])}</span>'
        onP = best_text(P, ["#FFFFFF", K, Lc])
        t1 = n.get("tiles", {}).get("t1", {"bg": Lc, "fg": P, "ac": A, "wm": P})
        t2 = n.get("tiles", {}).get("t2", {"bg": P, "fg": onP, "ac": A, "wm": onP})
        tile = lambda t: f'<div class="tile" style="background:{t["bg"]}">{mk(t["fg"], t["ac"], 52)}{wm(t["wm"], 40)}</div>'
        chips = "".join(f'<div class="chip" style="background:{c[1]};color:{best_text(c[1], ["#FFFFFF", "#15171C", K, Lc])}"><b>{e(c[0])}</b><span>{c[1]}</span><span>{e(c[2])}</span></div>'
                        for c in (C["primary"], C["accent"], C["ink"], C["light"]))
        key = n["key"]
        clip = lambda suffix: os.path.exists(os.path.join(page_dir, audio_dir, f"{key}{suffix}.mp3"))
        say = ""
        if n.get("say"):
            a1 = f'<audio controls preload="none" src="{audio_dir}/{key}.mp3"></audio>' if clip("") else ""
            a2 = f'<audio controls preload="none" src="{audio_dir}/{key}__read.mp3"></audio>' if clip("__read") else ""
            say = (f'<div class="say"><div><span class="lbl">Meant to sound</span><b class="guide">{e(n["say"])}</b>{a1}</div>'
                   f'<div><span class="lbl">First read by a stranger</span><b class="guide">{e(n["display"])}</b>{a2}</div></div>')
        own = r["ownability"]; ownt = f"{own}/5" if own != "n/a" else "n/a"
        srcs = "".join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(u[:70])}</a></li>' for u in r.get("sources", []))
        cards.append(f'''<article class="card" id="{e(key)}">
<header class="ch"><div><h2>{e(n["display"])}</h2><p class="dom">{e(n["domain"])} <span class="free">{e(n.get("status", ""))}</span></p></div><div class="score"><b>{own}</b><span>{"/5 " if own != "n/a" else ""}ownability</span></div></header>
<div class="brand">{tile(t1)}{tile(t2)}<div class="tile small" style="background:{Lc}"><div class="fav" style="background:{P}">{mk(onP, A, 16)}</div><span class="cap">24px</span><div class="fav big" style="background:{P}">{mk(onP, A, 40)}</div><span class="cap">app icon</span></div></div>
<div class="chips">{chips}</div>
<p class="why"><b>{e(f)}</b> for the wordmark. {e(n.get("why", ""))}</p>
{inuse(n, C, prod, mk) if n.get("inuse") else ""}
{say}
<dl class="facts">
<div><dt>App stores</dt><dd><span class="pill {r["appsLevel"]}">{APPS.get(r["appsLevel"], r["appsLevel"])}</span> {e(r["apps"])}</dd></div>
<div><dt>Google</dt><dd><span class="pill g{r["googleLevel"]}">{LEVEL.get(r["googleLevel"], r["googleLevel"])}</span> {e(r["google"])}</dd></div>
<div><dt>Ownability</dt><dd>{e(r["ownabilityWhy"])}</dd></div>
<div><dt>Meanings</dt><dd>{e(r.get("meanings", ""))}</dd></div>
<div><dt>Social</dt><dd>{e(r.get("social", ""))}</dd></div>
</dl>
<details class="src"><summary>Sources ({len(r.get("sources", []))})</summary><ul>{srcs}</ul></details>
</article>''')
        rows.append(f'<tr><td><a href="#{e(key)}">{e(n["display"])}</a><span class="sm">{e(n["domain"])}</span></td><td>{ownt}</td>'
                    f'<td>{LEVEL.get(r["googleLevel"], "")}</td><td>{APPS.get(r["appsLevel"], "")}</td><td class="mono">{e(n.get("say", ""))}</td></tr>')
    fam = "&".join("family=" + f.replace(" ", "+") + (f":wght@{w}" if w != 400 else "") for f, w in sorted(fonts))
    title = spec.get("title", "Name shortlist")
    intro = spec.get("intro") or (f"{len(names)} names. Pinned names first, then best ownability. Each has a light brand card, recordings and research"
                                  + (f"; domains checked on {spec['date']}" if spec.get("date") else "") + ".")
    head = (f'<title>{e(title)}</title>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{fam}&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">\n<style>{CSS}</style>')
    body = (f'<div class="wrap"><h1>{e(title)}</h1><p class="intro">{e(intro)}</p>'
            f'<div class="tw"><table><thead><tr><th>Name</th><th>Ownability</th><th>Google</th><th>App stores</th><th>Say it</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
            f'{"".join(cards)}<p class="note">Research came from web searches, not the app stores or trademark databases directly: treat it as a first pass and clear the final name with a trademark attorney. Recordings are generated voices.</p></div>')
    return head, body


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?"); ap.add_argument("--out")
    ap.add_argument("--audio", default="audio"); ap.add_argument("--fragment", action="store_true")
    ap.add_argument("--example", nargs="?", const="meeting", choices=sorted(EXAMPLES),
                    help="print a filled-in example: meeting (default) or companion")
    a = ap.parse_args()
    if a.example: print(json.dumps(EXAMPLES[a.example], indent=1, ensure_ascii=False)); return
    if not a.input or not a.out: ap.error("give shortlist.json and --out")
    spec = json.load(open(a.input))
    head, body = build(spec, a.audio, os.path.dirname(os.path.abspath(a.out)))
    page = (head + "\n" + body) if a.fragment else (
        f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n{head}\n</head><body>\n{body}\n</body></html>')
    open(a.out, "w").write(page)
    print(f"{len(spec['names'])} names -> {a.out}")


if __name__ == "__main__":
    main()
