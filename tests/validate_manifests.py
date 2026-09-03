#!/usr/bin/env python3
"""Structural checks on the marketplace, its plugins, and every SKILL.md."""
import html.parser, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errs, checked = [], 0


def err(m): errs.append(m)


class _HTML(html.parser.HTMLParser):
    VOID = {"br", "img", "input", "meta", "link", "hr", "source", "col",
            "area", "base", "embed", "param", "track", "wbr",
            "path", "circle", "rect", "line", "polyline", "polygon", "use", "stop"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass


def check_html(body):
    p = _HTML()
    try:
        p.feed(body)
    except Exception as e:
        return [f"parse error: {e}"]
    return p.stack


mkt_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
mkt = json.load(open(mkt_path))
for k in ("name", "description", "owner", "plugins"):
    if k not in mkt: err(f"marketplace.json missing '{k}'")
if not mkt.get("plugins"): err("marketplace.json lists no plugins")

for entry in mkt.get("plugins", []):
    for k in ("name", "description", "source"):
        if k not in entry: err(f"marketplace plugin entry missing '{k}': {entry}")
    src = os.path.join(ROOT, entry["source"])
    if not os.path.isdir(src):
        err(f"plugin source does not exist: {entry['source']}"); continue

    man = os.path.join(src, ".claude-plugin", "plugin.json")
    if not os.path.isfile(man):
        err(f"{entry['name']}: missing .claude-plugin/plugin.json"); continue
    pj = json.load(open(man))
    if pj.get("name") != entry["name"]:
        err(f"{entry['name']}: plugin.json name is '{pj.get('name')}', marketplace says '{entry['name']}'")
    for k in ("version", "description", "license"):
        if k not in pj: err(f"{entry['name']}: plugin.json missing '{k}'")

    skills = os.path.join(src, "skills")
    if not os.path.isdir(skills):
        err(f"{entry['name']}: no skills/ directory"); continue
    for d in sorted(os.listdir(skills)):
        sd = os.path.join(skills, d)
        if not os.path.isdir(sd): continue
        sk = os.path.join(sd, "SKILL.md")
        if not os.path.isfile(sk):
            err(f"{entry['name']}/{d}: no SKILL.md"); continue
        checked += 1
        text = open(sk, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            err(f"{d}: SKILL.md has no YAML frontmatter"); continue
        fm = m.group(1)
        nm = re.search(r"^name:\s*(.+)$", fm, re.M)
        if not nm:
            err(f"{d}: frontmatter missing 'name'")
        elif nm.group(1).strip().strip("\"'") != d:
            err(f"{d}: frontmatter name '{nm.group(1).strip()}' != directory '{d}'")
        if not re.search(r"^description:\s*\S", fm, re.M):
            err(f"{d}: frontmatter missing 'description'")

        # every referenced script must exist and be executable
        for ref in set(re.findall(r"scripts/([A-Za-z0-9_.-]+\.(?:sh|py))", text)):
            sp = os.path.join(sd, "scripts", ref)
            if not os.path.isfile(sp): err(f"{d}: SKILL.md references missing scripts/{ref}")
            elif not os.access(sp, os.X_OK): err(f"{d}: scripts/{ref} is not executable")
        for ref in set(re.findall(r"references/([A-Za-z0-9_.-]+\.md)", text)):
            if not os.path.isfile(os.path.join(sd, "references", ref)):
                err(f"{d}: SKILL.md references missing references/{ref}")

        # --- shipped HTML assets: must parse, and every {{PLACEHOLDER}} in one
        # must be documented, or the skill silently fails at substitution time.
        docs = text
        rd = os.path.join(sd, "references")
        if os.path.isdir(rd):
            for r in sorted(os.listdir(rd)):
                if r.endswith(".md"):
                    docs += open(os.path.join(rd, r), encoding="utf-8").read()
        for asset in sorted(f for f in os.listdir(sd) if f.endswith(".html")):
            ap = os.path.join(sd, asset)
            body = open(ap, encoding="utf-8").read()
            unclosed = check_html(body)
            if unclosed:
                err(f"{d}/{asset}: unclosed tags at EOF: {', '.join(unclosed[:5])}")
            for ph in sorted(set(re.findall(r"\{\{([A-Z_]+)\}\}", body))):
                if "{{%s}}" % ph not in docs:
                    err(f"{d}/{asset}: placeholder {{{{{ph}}}}} is not documented "
                        f"in SKILL.md or references/ — substitution would leave it in place")

print(f"marketplace '{mkt['name']}': {len(mkt.get('plugins', []))} plugins, {checked} skills checked")
if errs:
    print("\n".join("  FAIL " + e for e in errs)); sys.exit(1)
print("  all structural checks passed")
