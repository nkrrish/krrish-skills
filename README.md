# krrish-skills

[![validate](https://github.com/nkrrish/krrish-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/nkrrish/krrish-skills/actions/workflows/validate.yml)
[![licence: GPL-3.0](https://img.shields.io/badge/licence-GPL--3.0-blue.svg)](LICENSE)

Skills for [Claude Code](https://claude.com/claude-code) that verify their own output: logo
design, a project todo board, and Higgsfield API image and video generation.

Most skills tell a model what to do and hope. These ship the tooling to check whether it
worked — and fail loudly when it didn't.

```bash
/plugin marketplace add nkrrish/krrish-skills
/plugin install branding@krrish-skills
/plugin install planning@krrish-skills
/plugin install media@krrish-skills
```

Install only what you need. Each enabled skill costs context permanently, so they are split
by domain rather than bundled.

---

## branding — logo and icon-mark design

Designs icon marks as SVG through interview → explore → refine → export, then proves the
result holds up.

**What makes it different: it can tell whether its own output is any good.**

```
MARK                  INK    TPL       RGN   THIN  NODES  VERDICT
concept-1           0.361  0.446    2->2     1.17     58  ok
concept-3           0.410  0.458    3->3     1.33     34  ok
concept-5           0.191  0.365    3->2     1.56     56  FAIL counters close at 16px
```

- **`audit.sh`** — the pre-flight checklist as measurements. Ink coverage, monochrome-template
  collapse, whether interior counters survive 16px, thinnest feature, node count, and pairwise
  distinctness across a round (which catches a set that is one idea in five colourways). Exits
  non-zero on failure. Thresholds calibrated against marks verified by eye, not invented.
- **`similarity.py`** — checks each mark against ~3,450 real brand marks (CC0 `simple-icons`).
  Validated by self-matching known logos at 0.000. A prior-art smoke test, not a trademark search.
- **`shapegen.py`** — parametric shape systems: Truchet tiles, rosettes, gooey clusters,
  checkers, true superellipses, and real `evenodd` boolean carving.
- **`export.sh`** — PNG at 8 sizes, aspect-preserving, with blank-output detection.
- **`snippets.sh`** — paste-ready handoff: inline SVG, React component, CSS data-URI,
  monochrome mask rule, favicon `<head>` block, web manifest, Swift menu-bar template.

It also refuses the obvious answer. A per-domain ban list makes the first idea unavailable
(no equalizer bars for an audio product, no sparkles for AI, no shields for security), each
concept commits to a **named design lineage** — Swiss Rationalist, Japanese Mon, Brutalist Mass,
Instrument/Signal — and every round allocates risk 3+1+1: three on-brief, one that breaks a
stated preference, one arguing the opposite temperament.

**Requires** an SVG renderer and ImageMagick:

```bash
brew install librsvg imagemagick     # or: npm i -g @resvg/resvg-js-cli
```

## planning — per-project todo board

A three-column board (Todo / Review / Done) published as a private Artifact backed by a shared
database. Drag and drop, card view, live search, owner filter. One board per project; the skill
creates it and drives the cards.

Ships a SessionStart hook: any chat opened in a directory with a board picks up its link
automatically, so you never publish a second board for the same project. Requires `jq`.

## media — Higgsfield API skill for Claude Code (images, UGC video)

Realistic creator photos, product shoots and UGC video from Claude Code. Works with the
[Open Higgsfield API](https://docs.higgsfield.ai), billed to your own prepaid key.
Unofficial — not affiliated with Higgsfield AI.

**What makes it different: it can't spend your money without asking, and it quotes the
real price first.**

```
$ hf.sh prices
Prices on your account (Higgsfield estimates, nothing is charged):
  MODEL                              REQUEST                           USD
  Soul 2 (realistic people)          1 image, 720p                  $0.004
  Marketing Studio 2.5 Sunburst      1 image, 2k, high            metered*
  Kling 3.0 Standard                 5s, sound off                  $0.210
  Kling 3.0 Standard                 5s, sound on                   $0.315
  …
```

- **A guard hook, not a promise.** It ships with the plugin and makes Claude Code ask before
  every generation, upload or cancel — in every permission mode, including auto — and before
  anything could read or print your key. A regression suite of 45 tool calls proves it,
  including attempts to smuggle a paid call behind a free one.
- **Prices from your account, not from a table.** Every job runs Higgsfield's free estimate
  endpoint on the exact request first, so plan discounts show up and nothing goes stale.
- **The key never touches the chat.** `setup` opens a hidden-input dialog and stores it in the
  macOS Keychain (or a mode-600 file on Linux), then verifies it with a free call.

Full guide: [plugins/media/README.md](plugins/media/README.md). Requires `python3` and `curl`.

---

## Why the verification focus

Every check in `branding` exists because building it surfaced a defect that reasoning about it
had missed:

- Exports came back **blank PNGs with exit code 0** — ImageMagick's internal SVG renderer
  silently drops gradients, masks and clip-paths. Now detected and failed.
- Marks that looked correct **collapsed to solid squares** under a monochrome flatten, because
  a background plate was baked into the SVG. Now caught by region count and ink coverage.
- An interior cut **silted up at 16px** while looking fine at 512. Now caught by comparing
  distinct regions at both sizes.

None were visible in the SVG source. All were obvious in the pixels.

## Tests

```bash
bash tests/run.sh
```

CI runs the same suite on every push. It is a regression suite, not a lint — it asserts the
audit **catches** three known-bad marks (a baked background plate, hairline strokes, interior
counters that close at 16px) and **passes** three good ones. Loosen a threshold and the bad
fixtures start passing, and CI goes red.

Bad fixtures must exit exactly 1. An audit that cannot run exits 3, and the runner treats that
as a failure rather than a detection — otherwise a missing dependency produces a green suite
that measured nothing.

It also checks shipped HTML assets: every `{{PLACEHOLDER}}` in a template must be documented
in the skill's `SKILL.md` or `references/`, and the document must parse with no unclosed tags.
A renamed placeholder is otherwise silent — nothing notices until substitution leaves it in the
published page.

For `media`, it runs 45 tool calls through the guard hook — every paid call, key read and
chained-command trick must prompt, and free polling must not — and checks that `hf.sh` stops
before touching the network when there's no key, bad JSON or a malformed request ID.

Where the `claude` CLI is available the suite also runs `claude plugin validate` on the
marketplace and each plugin; it skips that step where the CLI is absent.

Requires `librsvg2-bin` and ImageMagick (either version 6 or 7).

## Licence

**GPL-3.0-or-later.** You may use these commercially and free of charge. If you distribute a
modified copy, it must carry attribution and be released under the same licence.

Logos, boards and other **output** you create with these skills are yours — output is not a
derivative work of the tool. The copyleft applies to modified copies of the skills themselves.

`branding` derives in part from [logo-designer-skill](https://github.com/neonwatty/logo-designer-skill)
by Jeremy Watt (MIT), relicensed under GPL-3.0 as that licence permits. `media` adapts parts of
[higgsfield-ai/skills](https://github.com/higgsfield-ai/skills) by Higgsfield AI (MIT) the same
way. See [NOTICE](NOTICE).
