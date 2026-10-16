#!/usr/bin/env python3
"""Build the filterable name sheet from scored names.

Usage:
  build_sheet.py scored.json --out sheet.html [--title "Free .com names"] [--intro "..."]
                 [--fragment] [--date "16 Oct 2026"] [--tried 4700]

--fragment leaves out <!doctype>, <html>, <head> and <body> for hosts that wrap the page
themselves (for example Claude Artifacts). Stars and hidden names are kept in the viewer's
browser (localStorage key "brand-builder-sheet"); the "Copy my stars" button is how the
user hands their picks back. Register and every domain tag link to --register-url (a template
with {domain}; put an affiliate deep link here). Register uses the first free domain in the
--tlds order of score_names.py, so the user's preferred ending comes first.

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
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));gap:12px}
.tile{position:relative;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 16px 10px;display:flex;flex-direction:column;gap:10px;min-width:0;transition:border-color .15s}
.tile:hover{border-color:var(--muted)}
.tile.star{border-color:var(--star);box-shadow:0 0 0 1px var(--star) inset}
.hd{display:flex;align-items:flex-start;gap:8px;min-width:0}
.hd>div{flex:1;min-width:0}
.nm{font-family:var(--font-display);font-weight:600;font-size:27px;letter-spacing:-.02em;line-height:1.05;overflow-wrap:anywhere}
.say{font-family:var(--font-mono);font-size:12px;color:var(--muted);margin-top:3px}
.sb{flex:none;width:32px;height:32px;border:0;border-radius:9px;background:transparent;color:var(--muted);font-size:19px;line-height:1;cursor:pointer}
.sb:hover{background:var(--bg);color:var(--fg)}
.sb.on{color:var(--star)}
.fits{display:flex;flex-wrap:wrap;gap:5px}
.fit{font-family:var(--font-mono);font-size:12px;font-weight:500;line-height:1;border-radius:7px;padding:5px 7px;border:1px solid var(--accent);white-space:nowrap}
.fit.pure{background:var(--accent);color:var(--card)}
.fit.aff{color:var(--fg);border-color:var(--muted);border-style:dashed}
a.fit{text-decoration:none;cursor:pointer}
a.fit.pure:hover{filter:brightness(1.15)}
a.fit.aff:hover{border-style:solid;border-color:var(--fg)}
button.fit.more{background:transparent;font:inherit;font-family:var(--font-mono);font-size:12px;cursor:pointer}
button.fit.more:hover{color:var(--fg)}
.acts a.reg{color:var(--fg);border:1px solid var(--line);padding:0 9px;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.acts a.reg:hover{border-color:var(--fg);background:var(--bg)}
.fit.more{border-color:transparent;color:var(--muted)}
.stats{display:flex;flex-wrap:wrap;gap:4px 14px;align-items:center;font-size:12px;color:var(--muted);padding-top:9px;border-top:1px solid var(--line)}
.dots{display:inline-flex;gap:2px;margin-left:5px;vertical-align:middle}
.dots i{width:6px;height:6px;border-radius:50%;background:var(--line)}
.dots i.f{background:var(--fg)}
.acts{display:flex;gap:2px;align-items:center;margin:-4px -6px 0}
.acts button,.acts a{height:26px;padding:0 6px;border:0;border-radius:6px;background:transparent;color:var(--muted);font:500 12px var(--font-body);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;white-space:nowrap}
.acts button:hover,.acts a:hover{background:var(--bg);color:var(--fg)}
.acts .reg{margin-left:auto}
.tier{display:flex;align-items:baseline;gap:10px;margin:26px 0 12px}
.tier h3{font-family:var(--font-display);font-weight:600;font-size:17px;margin:0}
.tier span{color:var(--muted);font-size:13px}
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
let fFit="all",fTld="all",fEnd="all",fSyl="all",fSo=0,fLo=0,fSort="rec",len="all",q="",starOnly=false,showHidden=false;
let st={stars:{},hidden:{}};
try{st=JSON.parse(localStorage.getItem(KEY)||"null")||st}catch(e){}
const save=()=>{try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}};
const el=(t,c,x)=>{const e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e};
const B=d=>d.b||d.n;
const TO={best:0,good:1,okay:2,hard:3};
// One tile per brand: the pure domains and every prefixed or suffixed domain for that name.
const G={},BY={};
for(const d of DATA){BY[d.n]=d;const k=B(d);let g=G[k];
  if(!g){g=G[k]={n:k,b:k,d:d.via?(d.d||k):(d.d||k),pure:[],aff:[],so:0,lo:0,sy:d.sy,e:d.e,t:"hard",s:d.s,dom:d.dom};}
  if(!d.via){g.pure=d.free||[];g.d=d.d||k;g.dom=d.dom;g.e=d.e}else for(const x of (d.free||[]))g.aff.push({dom:d.n+"."+x,via:d.via,aff:d.aff,tld:x});
  if(d.so+d.lo>g.so+g.lo){g.so=d.so;g.lo=d.lo}
  if(TO[d.t]<TO[g.t])g.t=d.t;
  if(/[A-Z]/.test(d.s||"")&&!/[A-Z]/.test(g.s||""))g.s=d.s;
}
const GROUPS=Object.values(G);
const AFF=["hey","meet","hello","with","say","get","join","its","the","my","dear","hq","labs","app","hub","kit","ai"];
const TLDS=[];for(const d of DATA)for(const x of d.free||[])if(!TLDS.includes(x))TLDS.push(x);
const rank=a=>TLDS.indexOf(a.tld)*100+(AFF.includes(a.aff)?AFF.indexOf(a.aff):50);
for(const g of GROUPS){g.aff.sort((x,y)=>rank(x)-rank(y)||x.dom.length-y.dom.length);g.free=[...g.pure,...g.aff.map(a=>a.tld)];g.via=g.pure.length?"":"aff";if(!g.pure.length)g.dom=g.aff[0].dom;
  g.doms=[...g.pure.map(x=>g.b+"."+x),...g.aff.map(a=>a.dom)]}
// Stars and hides used to be keyed by domain label; move them to the brand.
for(const o of [st.stars,st.hidden])for(const k of Object.keys(o))if(BY[k]&&B(BY[k])!==k){o[B(BY[k])]=1;delete o[k]}
save();
const label=g=>(g.d||g.n)+" ("+(g.doms||[g.dom]).join(", ")+")";
const regUrl=d=>REG.split("{domain}").join(encodeURIComponent(d));
const dots=v=>{const s=el("span","dots");for(let i=1;i<=5;i++)s.append(el("i",i<=v?"f":""));return s};
function tile(g){
  const t=el("article","tile"+(st.stars[g.n]?" star":""));
  const hd=el("div","hd"),tx=el("div");tx.append(el("div","nm",g.d||g.n),el("div","say",g.gone?"No longer in the list.":g.s));
  const sb=el("button","sb"+(st.stars[g.n]?" on":""),st.stars[g.n]?"★":"☆");sb.setAttribute("aria-pressed",!!st.stars[g.n]);sb.setAttribute("aria-label",(st.stars[g.n]?"Unstar ":"Star ")+(g.d||g.n));
  sb.onclick=()=>{st.stars[g.n]?delete st.stars[g.n]:st.stars[g.n]=1;save();render()};
  hd.append(tx,sb);t.append(hd);
  if(g.gone)return t;
  const f=el("div","fits");
  const link=(c,dom)=>{const a=el("a",c);a.href=regUrl(dom);a.target="_blank";a.rel="noopener";a.title="Register "+dom;return a};
  for(const x of g.pure){const c=link("fit pure",g.b+"."+x);c.textContent="."+x;f.append(c)}
  const MAX=6,open=!!st.open&&st.open[g.n];
  g.aff.slice(0,open?g.aff.length:MAX).forEach(a=>{const c=link("fit aff",a.dom);c.textContent=a.via==="prefix"?a.aff+"···."+a.tld:"···"+a.aff+"."+a.tld;f.append(c)});
  if(g.aff.length>MAX&&!open){const m=el("button","fit more","+"+(g.aff.length-MAX)+" more");m.title=g.aff.slice(MAX).map(a=>a.dom).join(", ");
    m.onclick=()=>{st.open=st.open||{};st.open[g.n]=1;save();render()};f.append(m)}
  t.append(f);
  const sx=el("div","stats");const a1=el("span",null,"Sound");a1.append(dots(g.so));const a2=el("span",null,"Look");a2.append(dots(g.lo));
  sx.append(a1,a2,el("span",null,g.sy+" syl · "+g.b.length+" letters"));t.append(sx);
  const a=el("div","acts");
  const hb=el("button",null,st.hidden[g.n]?"Unhide":"Hide");hb.onclick=()=>{st.hidden[g.n]?delete st.hidden[g.n]:st.hidden[g.n]=1;save();render()};
  const r=el("a","reg","Register ↗");r.title="Register "+g.doms[0]+". Tap any tag above to register that domain instead.";r.href=regUrl(g.doms[0]);r.target="_blank";r.rel="noopener";
  a.append(hb,r);t.append(a);return t;
}
const TIERS=[["best","Top picks","Best sounding and best looking"],["good","Good","Pleasant, a little plainer"],["okay","Okay","Readable but stiff"],["hard","Harsh","Hard sounds or odd clusters"]];
function render(){
  const root=document.getElementById("list");root.textContent="";let shown=0;
  const starred=Object.keys(st.stars).sort().map(n=>G[n]||{n,b:n,d:n,dom:n,doms:[n],gone:true});
  if(starred.length){
    const det=el("details","stars");det.open=!st.starsClosed;det.ontoggle=()=>{st.starsClosed=!det.open;save()};
    const sm=el("summary");sm.append(el("span","h2","Your stars · "+starred.length),el("span","sub","Click to open or close"));
    const cp=el("button","tog","Copy my stars");cp.style.margin="0 0 12px";const txt=starred.map(label).join("; ");
    cp.onclick=async()=>{try{await navigator.clipboard.writeText(txt);cp.textContent="Copied "+starred.length+" names"}catch(e){cp.textContent="Select the list below"}setTimeout(()=>cp.textContent="Copy my stars",1600)};
    const g=el("div","grid");for(const d of starred)g.append(tile(d));det.append(sm,cp,el("p","plain",txt),g);root.append(det);
  }
  let items=GROUPS.filter(d=>(len==="all"||d.b.length==+len)&&(!q||d.b.includes(q)||d.doms.some(x=>x.includes(q)))&&(fFit==="all"||(fFit==="exact"?d.pure.length>0:d.aff.some(a=>a.via===fFit)))&&(!starOnly||st.stars[d.n])&&(showHidden||!st.hidden[d.n])&&(fTld==="all"||d.free.includes(fTld))&&(fEnd==="all"||d.e===fEnd)&&(fSyl==="all"||(fSyl==="4"?d.sy>=4:d.sy==+fSyl))&&d.so>=fSo&&d.lo>=fLo);
  const S={rec:(a,b)=>TO[a.t]-TO[b.t]||(b.so+b.lo)-(a.so+a.lo)||(b.pure.length>0)-(a.pure.length>0)||a.b.localeCompare(b.b),so:(a,b)=>b.so-a.so||b.lo-a.lo,lo:(a,b)=>b.lo-a.lo||b.so-a.so,both:(a,b)=>(b.so+b.lo)-(a.so+a.lo),sy:(a,b)=>a.sy-b.sy||b.so-a.so,len:(a,b)=>a.b.length-b.b.length||b.so-a.so,az:(a,b)=>a.b.localeCompare(b.b)};
  items.sort(S[fSort]||S.rec);
  const s=el("section");s.append(el("h2",null,"All names · "+items.length),el("p","sub",fSort==="rec"?"Grouped by how good they sound. Each name shows every free domain for it.":"Sorted by your choice above."));
  if(fSort==="rec"){for(const [k,h,sub] of TIERS){const its=items.filter(d=>d.t===k);if(!its.length)continue;
      const th=el("div","tier");th.append(el("h3",null,h+" · "+its.length),el("span",null,sub));const g=el("div","grid");for(const d of its){shown++;g.append(tile(d))}s.append(th,g)}}
  else{const g=el("div","grid");for(const d of items){shown++;g.append(tile(d))}s.append(g)}
  root.append(s);
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
    ap.add_argument("--register-url", default="https://www.namecheap.com/domains/registration/results/?domain={domain}",
                    help="where Register and the domain tags link; {domain} is replaced, e.g. an affiliate deep link")
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
    fit_select = ('<label class="fl">Domain shape <select id="fFit"><option value="all">Any</option><option value="exact">Name is the domain</option>'
                  '<option value="prefix">Prefix (hey···.com)</option><option value="suffix">Suffix (···hq.com)</option></select></label>'
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
<p class="note">Each tile is one name with every free domain for it. A solid green tag (.com, .ai) means the name itself is free on that ending. A dashed tag such as "with···.com" or "···hq.com" means the prefix or suffix lives only in the domain. Availability came from a registry lookup and can change at any time; nothing is reserved, and some free names are premium priced. Sound and look scores are judgements, not measurements.</p>
</div>
<script>
const KEY="brand-builder-sheet";
const REG={json.dumps(a.register_url)};
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
