# Changelog

Updates are pull-based. Nothing reaches an installed copy until the user runs:

```bash
claude plugin marketplace update krrish-skills
claude plugin update <plugin>@krrish-skills   # restart required
```

## branding 1.1.0

Four tools from [logo-design-skill](https://github.com/kaankiziltug/logo-design-skill)
(MIT), wired into the existing phases. The icon-mark default and workflow are unchanged.

- `search_library.py` — category conventions from ~1,400 classified real logos, used in
  Phase 1.5 so at least one concept departs from them. The catalog ships; the SVGs
  themselves are third-party trademarks, so they are downloaded on demand into
  `~/.cache/logo-designer/library-svg` from a pinned commit and never bundled.
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
