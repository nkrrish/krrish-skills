#!/usr/bin/env python3
"""Find out whether the companion skills are already installed, before suggesting any install.

Usage:
  check_deps.py                 # checks canvas-design and design-taste-frontend
  check_deps.py logo-designer canvas-design

Looks in every place Claude Code loads skills from: personal skills (~/.claude/skills),
skills installed with `npx skills` (~/.agents/skills), every installed plugin (from
~/.claude/plugins/installed_plugins.json), and the current project (.claude/skills and
.agents/skills). Prints where each skill was found. Only for skills found nowhere does it
print the install command, and it never installs anything itself.

Exit 0 when everything was found, 1 when something is missing.
"""
import json, os, sys

HOME = os.path.expanduser("~")
INSTALL = {
    "canvas-design": [
        "claude plugin marketplace add anthropics/skills",
        "claude plugin install example-skills@anthropic-agent-skills",
    ],
    "design-taste-frontend": [
        "npx -y skills add Leonxlnx/taste-skill --skill design-taste-frontend -g -a claude-code",
    ],
    "logo-designer": [
        "claude plugin marketplace add nkrrish/krrish-skills",
        "claude plugin install branding@krrish-skills",
    ],
}


def plugin_roots():
    p = os.path.join(HOME, ".claude", "plugins", "installed_plugins.json")
    roots = []
    try:
        data = json.load(open(p))
        for name, entries in (data.get("plugins", data) or {}).items():
            for e in entries if isinstance(entries, list) else [entries]:
                path = e.get("installPath") if isinstance(e, dict) else None
                if path: roots.append((f"plugin {name}", os.path.join(path, "skills")))
    except Exception:
        pass
    return roots


def places():
    cwd = os.getcwd()
    return ([("personal skills", os.path.join(HOME, ".claude", "skills")),
             ("npx skills (global)", os.path.join(HOME, ".agents", "skills")),
             ("this project", os.path.join(cwd, ".claude", "skills")),
             ("this project (npx skills)", os.path.join(cwd, ".agents", "skills"))]
            + plugin_roots())


def find(skill):
    hits = []
    for label, root in places():
        f = os.path.join(root, skill, "SKILL.md")
        if os.path.isfile(f): hits.append((label, os.path.dirname(f)))
    return hits


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"): sys.exit(__doc__)
    skills = sys.argv[1:] or ["canvas-design", "design-taste-frontend"]
    missing = []
    for s in skills:
        hits = find(s)
        if hits:
            print(f"found    {s}")
            for label, path in hits: print(f"           {label}: {path}")
            if len(hits) > 1: print(f"           ({len(hits)} copies; any one is enough)")
        else:
            missing.append(s)
            print(f"missing  {s}")
    if missing:
        print("\nOnly if the user wants them, these install the missing skills (ask first):")
        for s in missing:
            for c in INSTALL.get(s, [f"(no known install command for {s})"]): print(f"  {c}")
        sys.exit(1)


if __name__ == "__main__":
    main()
