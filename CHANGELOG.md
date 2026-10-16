# Changelog

Updates are pull-based. Nothing reaches an installed copy until the user runs:

```bash
claude plugin marketplace update krrish-skills
claude plugin update <plugin>@krrish-skills   # restart required
```

## branding 1.2.3

- The sheet's domain tags are register links for that exact domain, and the Register button
  opens the best one (".com" first, then the user's other endings; for affixed names
  hey, meet, hello, with and say first). The Copy button is gone. "+N more" expands in place.
- `build_sheet.py --register-url` takes a link template with `{domain}`, for an affiliate
  deep link.

## branding 1.2.2

- Names on a prefixed or suffixed domain now show the proposed brand, not the domain label: the
  sheet tile reads "Jova" with "on heyjova.com" under it. `gen_names.py` writes a `brand`
  field for prefixes and the domain-only suffixes (hq, labs, app, hub, kit, ai);
  `score_names.py` scores sound, look, length and syllables on the brand and can infer it for
  hand-added affix and pair names; `build_sheet.py` adds a "Domain shape" filter and copies
  stars as "Jova (heyjova.com)".
- The sheet is easier to scan: one tile per name with all its free domains (solid green
  ".com", ".ai" when the name itself is free, dashed "hey···.com" or "···hq.com" when the affix
  is only in the domain), tiles grouped into Top picks, Good, Okay and Harsh, sound and look as
  dot meters, and a star button in the corner. Stars saved by domain move to the name.

## branding 1.2.1

- `canvas-design` and `design-taste-frontend` are no longer bundled, so you always get their
  latest versions. New `check_deps.py` finds them wherever they are installed (personal skills,
  any plugin, `npx skills`, the project) and only suggests an install when one is missing.
- `voice.py setup` connects an OpenAI key through a hidden-input dialog and stores it in the
  macOS Keychain (or a mode-600 file elsewhere); `voice.py status` says whether one is
  connected. The skill asks before recordings instead of failing silently without a key.

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

## branding 1.1.0

Four tools from [logo-design-skill](https://github.com/kaankiziltug/logo-design-skill)
(MIT), wired into the existing phases. The icon-mark default and workflow are unchanged.

- `search_library.py` — category conventions from ~1,400 classified real logos, used in
  Phase 1.5 so at least one concept departs from them. The catalog ships; the SVGs
  themselves are third-party trademarks, so they are downloaded on demand into
  `~/.cache/logo-designer/library-svg` from a pinned commit and never bundled.
  `search_library.py --download-all` caches the whole library (~11 MB) for offline use.
- `svg_audit.py` — source-level checks alongside `audit.sh`: live text, rasters, filters,
  unexpanded strokes, near-miss angles, tiny sub-paths, centring. Advisory, always exits 0.
- `preview_sheet.py` — full HTML test sheet for Phase 3: size ladder, pixel test, five
  backgrounds, squint/mirror/rotate, context mockups, and a shelf test beside real logos.
- `export_variants.py` — one-colour black/white/brand SVGs, square and app-icon masters, and
  with `--web-icons` a real `favicon.ico`, apple-touch, maskable and manifest set.
- Supporting `svglib.py` and `render_png.py` (renderer fallback chain, HTML screenshots).
- All Python 3 standard library; no new required dependencies.

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
