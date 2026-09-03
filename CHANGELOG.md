# Changelog

Updates are pull-based. Nothing reaches an installed copy until the user runs:

```bash
claude plugin marketplace update krrish-skills
claude plugin update <plugin>          # restart required
```

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
