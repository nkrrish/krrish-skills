#!/usr/bin/env python3
"""PreToolUse guard for the media plugin's Higgsfield skill.

Makes Claude Code ask the user before anything can spend Higgsfield credits or expose the
Higgsfield key — in every permission mode, including auto mode and bypass-style allowlists.

Asks when a tool call:
  - runs a shell command that mentions api.higgsfield.ai, HF_API_KEY, the skill's hf.sh
    (except its free subcommands: setup, status, prices, estimate <ep> @file, wait, get),
    the key's Keychain item or credentials file, a shell profile, or dumps the environment;
  - writes or edits a file whose new content calls the API or uses the key variables;
  - reads the credentials file or a shell profile.
Everything else passes through to the normal permission rules untouched.
"""
import json
import re
import sys

KEY_STORE = r"higgsfield-api|HF_API_KEY"
PROFILES = r"\.(zshrc|zprofile|zshenv|bashrc|bash_profile|profile)\b"

API_OR_KEY = re.compile(r"api\.higgsfield\.ai|" + KEY_STORE, re.I)
SHELL_RISK = re.compile(
    r"api\.higgsfield\.ai|" + KEY_STORE + r"|hf\.sh|" + PROFILES +
    r"|\bprintenv\b|\bexport\s+-p\b|(^|[;&|(]\s*)(env|set)\s*($|[;&|)>])",
    re.I,
)

# Free subcommands of the skill's own helper. Arguments are limited to characters that
# cannot chain or substitute another command, so nothing can ride along.
PATH = r"[\w./~-]+"
HF = r"\s*(?:bash\s+)?" + PATH + r"/skills/higgsfield/scripts/hf\.sh\s+"
FREE = re.compile(HF + r"(?:"
    r"setup(?:\s+--from-env)?"
    r"|status|prices"
    r"|estimate\s+/?" + PATH + r"\s+@" + PATH +
    r"|wait\s+[0-9a-fA-F-]{8,64}(?:\s+" + PATH + r")?"
    r"|get\s+/?" + PATH + r"(?:\?[\w=&.-]*)?"
    r")\s*")


def ask(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": "Higgsfield guard: " + reason,
        }
    }))
    sys.exit(0)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        return
    tool = event.get("tool_name", "")
    inp = event.get("tool_input") or {}

    if tool == "Bash":
        cmd = inp.get("command", "")
        if FREE.fullmatch(cmd):
            return
        if SHELL_RISK.search(cmd):
            ask("this command can spend Higgsfield credits or reveal your API key.")
    elif tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
        new_text = json.dumps({k: v for k, v in inp.items() if k != "old_string"})
        if API_OR_KEY.search(new_text):
            ask("this writes code that calls the Higgsfield API or uses your key.")
    elif tool == "Read":
        path = inp.get("file_path", "")
        if re.search(PROFILES + r"$|higgsfield-api/credentials$", path):
            ask("this file can hold your Higgsfield API key.")


main()
