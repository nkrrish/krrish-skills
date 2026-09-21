# Changelog

Updates are pull-based. Nothing reaches an installed copy until the user runs:

```bash
claude plugin marketplace update krrish-skills
claude plugin update <plugin>@krrish-skills   # restart required
```

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
