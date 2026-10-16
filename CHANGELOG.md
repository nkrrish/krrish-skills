# Changelog

Updates are pull-based. Nothing reaches an installed copy until the user runs:

```bash
claude plugin marketplace update krrish-skills
claude plugin update <plugin>@krrish-skills   # restart required
```

## branding 1.2.0

New skill, `brand-builder`: name finding and vetting before the logo.

- `gen_names.py` generates coined, formula, letter, pair and affix names with shape, rude-word
  and lookalike filters.
- `check_domains.py` checks any TLDs the user picks (.com, .ai, .app, .io, country codes):
  RDAP from the IANA bootstrap list where the registry has it, WHOIS where it does not. No
  account or key.
- `score_names.py` and `build_sheet.py` make a filterable, starrable name sheet with a
  "Copy my stars" hand-back, a per-name list of free domains and a domain filter.
- A full brand-board step for the chosen name, following the brandkit method in our own words.
- `build_shortlist.py` makes the shortlist page: brand cards, research, recordings, in-use mockups.
- `voice.py` records pronunciations and runs the hear-it-then-spell-it test (OpenAI audio API).
- `probe_handles.py` and `contrast.py` for handles and WCAG contrast.

Also bundles `canvas-design` (Apache-2.0) and `design-taste-frontend` (MIT) under their own
licences; see NOTICE.

## media 1.0.0

Initial release. One skill, `higgsfield`, for the Higgsfield Open API on the user's own key.

- `hf.sh setup` stores the key in the macOS Keychain (or a mode-600 file elsewhere) through
  a hidden-input dialog, so the key never passes through the chat, and verifies it.
- Prices come from the API's estimate endpoint for the connected account (`hf.sh prices`,
  `hf.sh estimate`), so plan discounts show up and nothing is quoted from memory.
- A PreToolUse guard ships with the plugin (`hooks/hooks.json`): Claude Code asks before
  any generation, upload or cancel, and before anything could read or print the key — in
  every permission mode, including auto.
- Guides for realistic creator photos, product photoshoots (10 modes, adapted from
  higgsfield-ai/skills under MIT), Soul ID characters and a stills-first UGC video pipeline.
- Requires `python3` and `curl`.

## planning 1.3.0

- Cards carry `tags` (an array). The board shows them as chips on the card
  face, edits them in the card view and the new card form, and filters on one
  tag from a toolbar dropdown that sits next to the All/User/Agent filter.
  Search matches tags too.
- `SKILL.md` gains a tag vocabulary (Infra, Product, UX, Website, Marketing,
  Compliance, Business, Billing), `tag <n> …` and "show <tag> cards" commands,
  and a tags column in the card table.
- Existing boards need one republish of `board.html` to get the chips and the
  filter (see "Changing the page" in `SKILL.md`). Cards without `tags` render as
  before.

## planning 1.2.0

- The SessionStart hook now ships with the plugin (`hooks/hooks.json`), so
  installing `planning` wires it up automatically. Previously it had to be added
  to `settings.json` by hand.
- If you added that hook manually, remove it after updating or it will run twice:
  delete the `SessionStart` entry pointing at
  `.../skills/todo-board/session-start-hook` from your `settings.json`.
- The hook requires `jq`.

## planning 1.1.0

- Reworked the todo-board HTML template: card modal, segmented All/User/Agent
  owner filter, live search, chips, properties panel, and empty-state
  affordances.
- `SKILL.md` unchanged; the three substitution placeholders (`{{TITLE}}`,
  `{{SUBTITLE}}`, `{{SLUG}}`) are unchanged, so existing boards are unaffected.

## branding 1.0.1

- `audit.sh` and `export.sh` now work under ImageMagick 6 as well as 7. Debian
  and Ubuntu ship version 6, which has no `magick` binary — on those systems the
  audit previously exited without measuring anything. Affects every Linux user.
- `audit.sh` reports a baked-in background plate before reporting "blank"; a
  full-canvas plate trips both checks and the plate is the actionable diagnosis.

## branding 1.0.0 / planning 1.0.0

Initial release.
