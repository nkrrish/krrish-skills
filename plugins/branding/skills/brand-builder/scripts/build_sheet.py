#!/usr/bin/env python3
"""Build the filterable name sheet from scored names.

Usage:
  build_sheet.py scored.json --out sheet.html [--title "Free .com names"] [--intro "..."]
                 [--fragment] [--date "16 Oct 2026"] [--tried 4700]

--fragment leaves out <!doctype>, <html>, <head> and <body> for hosts that wrap the page
themselves (for example Claude Artifacts). Stars and hidden names are kept in the viewer's
browser (localStorage key "brand-builder-sheet"); the "Copy my stars" button is how the
user hands their picks back.

Names on a prefixed or suffixed domain (scored with "b" and "via") show the brand big and the
full domain under it ("Jova", then "on heyjova.com"), so the reader sees the proposed name,
not the domain label. Length, search and the copied star list use the brand.
"""
import argparse, html, json

CSS = """
:root{--bg:#f4f5f2;--card:#fff;--fg:#17191d;--muted:#5b6069;--line:#e2e4de;--accent:#2f6b45;--accent-soft:#e3efe6;--star:#9a6a00;
--font-display:'Familjen Grotesk','Avenir Next',system-ui,sans-serif;--font-body:'Instrument Sans',system-ui,sans-serif;--font-mono:'JetBrains Mono',ui-monospace,Menlo,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141619;--card:#1c1f24;--fg:#f1f2ee;--muted:#a0a5ae;--line:#2c3038;--accent:#7cc795;--accent-soft:#1f3227;--star:#f2c14e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141619;--card:#1c1f24;--fg:#f1f2ee;--muted:#a0a5ae;--line:#2c3038;--accent:#7cc795;--accent-soft:#1f3227;--star:#f2c14e;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--font-body);font-size:15px;line-height:1.5;margin:0}
.wrap{max-width:1120px;margin:0 auto;padding-inline:20px;padding-block:40px 64px}
h1{font-family:var(--font-display);font-weight:700;font-size:clamp(28px,5vw,42px);letter-spacing:-.02em;line-height:1.05;margin:0 0 10px;text-wrap:balance}
.intro{color:var(--muted);max-width:66ch;margin:0}
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:2;background:var(--bg);display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding-block:14px;margin-block:20px 8px;border-bottom:1px solid var(--line)}
.bar input[type=search]{flex:1 1 180px;min-width:0;height:36px;padding:0 12px;border-radius:9px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit}
.seg{display:inline-flex;border:1px solid var(--line);border-radius:9px;overflow:hidden;background:var(--card)}
.seg button,.tog{height:34px;padding:0 12px;border:0;background:transparent;color:var(--muted);font:500 13.5px var(--font-body);cursor:pointer}
.seg button[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.tog{border:1px solid var(--line);border-radius:9px;background:var(--card);height:36px}
.tog[aria-pressed=true]{color:var(--fg);border-color:var(--fg)}
.row2{display:flex;flex-wrap:wrap;gap:8px;width:100%;align-items:center}
.fl{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--muted)}
.fl select{height:34px;border-radius:9px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:500 13.5px var(--font-body);padding:0 8px}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.count{font-family:var(--font-mono);font-size:12.5px;color:var(--muted);margin-left:auto}
section{margin-top:28px}
section h2{font-family:var(--font-display);font-weight:600;font-size:21px;margin:0}
.sub{color:var(--muted);margin:2px 0 14px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(178px,1fr));gap:10px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 14px 10px;display:flex;flex-direction:column;gap:2px;min-width:0}
.tile.star{border-color:var(--star)}
.nm{font-family:var(--font-display);font-weight:600;font-size:25px;letter-spacing:-.015em;line-height:1.1;overflow-wrap:anywhere}
.nm small{font-family:var(--font-mono);font-weight:400;font-size:12px;color:var(--muted);margin-left:1px}
.say{font-family:var(--font-mono);font-size:12.5px;color:var(--muted)}
.dom{font-family:var(--font-mono);font-size:12.5px;color:var(--fg);overflow-wrap:anywhere}
.dom i{font-style:normal;color:var(--muted)}
.fit{align-self:flex-start;font-family:var(--font-mono);font-size:11.5px;font-weight:500;border-radius:999px;padding:1px 8px;margin-bottom:6px;border:1px solid var(--accent)}
.fit.pure{background:var(--accent);color:var(--card)}
.fit.aff{color:var(--muted);border-color:var(--line);border-style:dashed}
.meta{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;font-family:var(--font-mono);font-size:11px;color:var(--muted)}
.meta span{border:1px solid var(--line);border-radius:999px;padding:1px 7px}
.meta b{font-weight:500;color:var(--fg)}
.meta .tl{border-color:var(--accent);color:var(--accent)}
.acts{display:flex;gap:2px;margin-top:8px;align-items:center}
.acts button,.acts a{height:28px;min-width:28px;padding:0 8px;border:0;border-radius:7px;background:transparent;color:var(--muted);font:500 12.5px var(--font-body);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center}
.acts button:hover,.acts a:hover{background:var(--bg);color:var(--fg)}
.acts .on{color:var(--star)}
.acts .reg{margin-left:auto}
details.stars{margin-top:28px;border:1px solid var(--line);border-radius:14px;background:var(--card);padding:4px 16px 16px}
details.stars summary{cursor:pointer;list-style:none;display:flex;align-items:baseline;gap:12px;padding:12px 0}
details.stars summary::-webkit-details-marker{display:none}
details.stars .h2{font-family:var(--font-display);font-weight:600;font-size:21px}
details.stars .tile{background:var(--bg)}
.plain{user-select:all;font-family:var(--font-mono);font-size:12.5px;color:var(--muted);margin:0 0 12px;overflow-wrap:anywhere}
.empty{color:var(--muted);font-size:14px}
.note{margin-top:40px;color:var(--muted);font-size:13.5px;max-width:72ch}
"""

JS = r"""
const ENDN={plain:"plain",io:"-io",ly:"-ly",made:"made-up ending",one:"+1 letter",hq:"+HQ",two:"+2 letters"};
const TIER={best:0,good:1,okay:2,hard:3};
let fFit="all",fTld="all",fEnd="all",fSyl="all",fSo=0,fLo=0,fSort="rec",len="all",q="",starOnly=false,showHidden=false;
let st={stars:{},hidden:{}};
try{st=JSON.parse(localStorage.getItem(KEY)||"null")||st}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}};
const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e};
const BY={};for(const d of DATA)BY[d.n]=d;
const B=d=>d.b||d.n;
const label=d=>d.via?(d.d||B(d))+" ("+d.dom+")":d.dom;
function tile(d){
  const t=el("article","tile"+(st.stars[d.n]?" star":""));
  const tld="."+(d.dom||"").split(".").pop();
  if(!d.gone)t.append(el("span","fit "+(d.via?"aff":"pure"),d.via?(d.via==="prefix"?d.aff+"\u00b7\u00b7\u00b7"+tld:"\u00b7\u00b7\u00b7"+d.aff+tld):"pure "+tld));
  const nm=el("div","nm",d.d||d.n);if(!d.via)nm.append(el("small",null,tld));
  t.append(nm);
  if(d.gone)t.append(el("div","say","No longer in the list. Check the domain again."));
  else if(d.via){const dm=el("div","dom");dm.append(el("i",null,"on "),d.dom);t.append(dm,el("div","say",d.s))}
  else t.append(el("div","say",d.dom+" · "+d.s));
  if(!d.gone){const m=el("div","meta");const a1=el("span");a1.append("sound ",el("b",null,d.so+"/5"));const a2=el("span");a2.append("look ",el("b",null,d.lo+"/5"));
    m.append(...(d.free||[]).map(x=>el("span","tl","."+x)),a1,a2,el("span",null,d.sy+" syllables"),el("span",null,B(d).length+" letters"),...(d.via?[el("span",null,d.aff+" in domain")]:[]),el("span",null,ENDN[d.e]||""));t.append(m)}
  const a=el("div","acts");
  const sb=el("button",st.stars[d.n]?"on":"",st.stars[d.n]?"★ Starred":"☆ Star");sb.setAttribute("aria-pressed",!!st.stars[d.n]);
  sb.onclick=()=>{st.stars[d.n]?delete st.stars[d.n]:st.stars[d.n]=1;save();render()};
  const hb=el("button",null,st.hidden[d.n]?"Unhide":"Hide");hb.onclick=()=>{st.hidden[d.n]?delete st.hidden[d.n]:st.hidden[d.n]=1;save();render()};
  const cb=el("button",null,"Copy");cb.onclick=async()=>{try{await navigator.clipboard.writeText(d.dom);cb.textContent="Copied"}catch(e){cb.textContent=d.dom}setTimeout(()=>cb.textContent="Copy",1400)};
  const r=el("a","reg","Register");r.href="https://www.namecheap.com/domains/registration/results/?domain="+encodeURIComponent(d.dom);r.target="_blank";r.rel="noopener";
  a.append(sb,hb,cb,r);t.append(a);return t;
}
function render(){
  const root=document.getElementById("list");root.textContent="";let shown=0;
  const starred=Object.keys(st.stars).sort().map(n=>BY[n]||{n,d:n,dom:n+".com",s:"",gone:true});
  if(starred.length){
    const det=el("details","stars");det.open=!st.starsClosed;det.ontoggle=()=>{st.starsClosed=!det.open;save()};
    const sm=el("summary");sm.append(el("span","h2","Your stars · "+starred.length),el("span","sub","Click to open or close"));
    const cp=el("button","tog","Copy my stars");cp.style.margin="0 0 12px";const txt=starred.map(label).join(", ");
    cp.onclick=async()=>{try{await navigator.clipboard.writeText(txt);cp.textContent="Copied "+starred.length+" names"}catch(e){cp.textContent="Select the list below"}setTimeout(()=>cp.textContent="Copy my stars",1600)};
    const g=el("div","grid");for(const d of starred)g.append(tile(d));det.append(sm,cp,el("p","plain",txt),g);root.append(det);
  }
  let items=DATA.filter(d=>(len==="all"||B(d).length==+len)&&(!q||d.n.includes(q)||B(d).includes(q)||(d.d||"").toLowerCase().includes(q))&&(fFit==="all"||(fFit==="exact"?!d.via:d.via===fFit))&&(!starOnly||st.stars[d.n])&&(showHidden||!st.hidden[d.n])&&(fTld==="all"||(d.free||[]).includes(fTld))&&(fEnd==="all"||d.e===fEnd)&&(fSyl==="all"||(fSyl==="4"?d.sy>=4:d.sy==+fSyl))&&d.so>=fSo&&d.lo>=fLo);
  const S={so:(a,b)=>b.so-a.so||b.lo-a.lo,lo:(a,b)=>b.lo-a.lo||b.so-a.so,both:(a,b)=>(b.so+b.lo)-(a.so+a.lo),sy:(a,b)=>a.sy-b.sy||b.so-a.so,len:(a,b)=>B(a).length-B(b).length||b.so-a.so,az:(a,b)=>B(a).localeCompare(B(b))||a.n.localeCompare(b.n)};
  if(S[fSort])items.sort(S[fSort]);
  const s=el("section");s.append(el("h2",null,"All names · "+items.length),el("p","sub",fSort==="rec"?"Recommended order: best sounding first.":"Sorted by your choice above."));
  const g=el("div","grid");for(const d of items){shown++;g.append(tile(d))}s.append(g);root.append(s);
  document.getElementById("count").textContent=shown+" shown";if(!shown)root.append(el("p","empty","No names match these filters. Try Reset."));
}
document.querySelectorAll(".seg button").forEach(b=>b.onclick=()=>{len=b.dataset.len;document.querySelectorAll(".seg button").forEach(x=>x.setAttribute("aria-pressed",x===b));render()});
document.getElementById("q").oninput=e=>{q=e.target.value.trim().toLowerCase();render()};
for(const [id,fn] of [["starOnly",v=>starOnly=v],["showHidden",v=>showHidden=v]]){const b=document.getElementById(id);b.onclick=()=>{const v=b.getAttribute("aria-pressed")!=="true";b.setAttribute("aria-pressed",v);fn(v);render()}}
if(document.getElementById("fTld"))document.getElementById("fTld").onchange=e=>{fTld=e.target.value;render()};
if(document.getElementById("fFit"))document.getElementById("fFit").onchange=e=>{fFit=e.target.value;render()};
for(const [id,set] of [["fEnd",v=>fEnd=v],["fSyl",v=>fSyl=v],["fSo",v=>fSo=+v],["fLo",v=>fLo=+v],["fSort",v=>fSort=v]])document.getElementById(id).onchange=e=>{set(e.target.value);render()};
document.getElementById("reset").onclick=()=>{fTld="all";fFit="all";if(document.getElementById("fFit"))document.getElementById("fFit").value="all";if(document.getElementById("fTld"))document.getElementById("fTld").value="all";fEnd="all";fSyl="all";fSo=0;fLo=0;fSort="rec";len="all";q="";starOnly=false;showHidden=false;
  for(const [id,v] of [["fEnd","all"],["fSyl","all"],["fSo","0"],["fLo","0"],["fSort","rec"],["q",""]])document.getElementById(id).value=v;
  document.querySelectorAll(".seg button").forEach(x=>x.setAttribute("aria-pressed",x.dataset.len==="all"));
  for(const id of ["starOnly","showHidden"])document.getElementById(id).setAttribute("aria-pressed","false");render()};
render();
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input"); ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="Free .com names")
    ap.add_argument("--intro", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--tried", type=int, default=0)
    ap.add_argument("--fragment", action="store_true")
    a = ap.parse_args()
    data = json.load(open(a.input))
    e = html.escape
    lens = sorted({len(d.get("b") or d["n"]) for d in data})
    tlds = []
    for d in data:
        for x in d.get("free", []):
            if x not in tlds: tlds.append(x)
    tld_select = ('<label class="fl">Domain <select id="fTld"><option value="all">Any free domain</option>'
                  + "".join(f'<option value="{e(x)}">.{e(x)} free</option>' for x in tlds) + "</select></label>") if len(tlds) > 1 else ""
    fit_select = ('<label class="fl">Domain shape <select id="fFit"><option value="all">Any</option><option value="exact">Pure domains (name.com)</option>'
                  '<option value="prefix">Prefix in domain (with···.com)</option><option value="suffix">Suffix in domain (···hq.com)</option></select></label>'
                  ) if any(d.get("via") for d in data) else ""
    seg = '<button data-len="all" aria-pressed="true">All</button>' + "".join(
        f'<button data-len="{n}" aria-pressed="false">{n} letters</button>' for n in lens)
    intro = a.intro or (f"{len(data)} names with at least one free domain" + (f" when checked on {a.date}" if a.date else "")
                        + (f", out of {a.tried:,} tried" if a.tried else "") + ". Best sounding first. Sound and look are rough ratings out of 5. "
                        "Star the ones you like and hide the rest; your picks stay in this browser. When you are ready, open Your stars and press Copy my stars.")
    body = f"""<div class="wrap">
<h1>{e(a.title)}</h1>
<p class="intro">{e(intro)}</p>
<div class="bar" role="toolbar" aria-label="Filters">
<input type="search" id="q" placeholder="Search names" aria-label="Search names">
<div class="seg" role="group" aria-label="Length">{seg}</div>
<button class="tog" id="starOnly" aria-pressed="false">Starred only</button>
<button class="tog" id="showHidden" aria-pressed="false">Show hidden</button>
<span class="count" id="count"></span>
<div class="row2">
<label class="fl">Ending <select id="fEnd"><option value="all">Any ending</option><option value="plain">Plain made-up</option><option value="io">Ends in -io</option><option value="ly">Ends in -ly</option><option value="made">-ix, -um, -ena, -ivo</option><option value="one">Plus one letter</option><option value="hq">Plus HQ</option><option value="two">Plus two letters</option></select></label>
{tld_select}{fit_select}<label class="fl">Syllables <select id="fSyl"><option value="all">Any</option><option value="2">2</option><option value="3">3</option><option value="4">4 or more</option></select></label>
<label class="fl">Sound <select id="fSo"><option value="0">Any</option><option value="4">4 and up</option><option value="5">5 only</option></select></label>
<label class="fl">Look <select id="fLo"><option value="0">Any</option><option value="4">4 and up</option><option value="5">5 only</option></select></label>
<label class="fl">Sort <select id="fSort"><option value="rec">Recommended</option><option value="so">Best sounding</option><option value="lo">Best looking</option><option value="both">Sound plus look</option><option value="sy">Fewest syllables</option><option value="len">Shortest</option><option value="az">A to Z</option></select></label>
<button class="tog" id="reset">Reset</button>
</div>
</div>
<div id="list"></div>
<p class="note">Green tags show which of the checked domains are free for each name. A solid "pure .com" tag means the name itself is the domain. A dashed tag such as "with···.com" or "···hq.com" means the big word is the proposed name and the prefix or suffix lives only in the domain. Availability came from a registry lookup and can change at any time; nothing is reserved, and some free names are premium priced. Sound and look scores are judgements, not measurements.</p>
</div>
<script>
const KEY="brand-builder-sheet";
const DATA={json.dumps(data, separators=(",", ":")).replace("</", "<\\/")};
{JS}
</script>"""
    head = f"""<title>{e(a.title)}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{CSS}</style>"""
    page = head + "\n" + body if a.fragment else (
        f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n{head}\n</head><body>\n{body}\n</body></html>')
    open(a.out, "w").write(page)
    print(f"{len(data)} names -> {a.out}")


if __name__ == "__main__":
    main()
