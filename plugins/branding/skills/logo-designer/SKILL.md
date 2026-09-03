---
name: logo-designer
description: |
  Design and iterate on logos and icon marks as SVG. Use when the user asks to
  "create a logo", "design a logo", "make me a logo", "design an icon",
  "app icon", "favicon", "iterate on this logo", "logo for my project", or
  discusses branding marks, symbols, or wordmarks. Produces distinct concepts,
  a browser preview, and PNG exports at standard sizes.
license: MIT
---

# Logo Designer

Design icon marks and logos as SVG, through a structured explore → refine → export loop.

**Default output is an icon mark** — a square symbol that works as a favicon, app icon, and
avatar. Only produce a wordmark or combination mark when the user explicitly asks for text.

## Before generating anything

Read `references/design-principles.md`. It is the quality bar for every mark this skill
produces — negative space, stroke weight, focal point, the pre-flight checklist. Do not skip
it and improvise; improvised marks are the main failure mode of logo generation.

Read all three references before Phase 2. They do different jobs and none is optional:

| Reference | Job |
|---|---|
| `design-principles.md` | The quality bar — proportion, negative space, the pre-flight checklist |
| `design-lineages.md` | The *position* — a named aesthetic committed to before drawing |
| `anti-cliche.md` | The *idea* — banned first ideas, the conceptual seed, risk allocation |
| `construction-patterns.md` | The *geometry* — SVG recipes so concepts differ structurally |
| `critique-rubric.md` | The *judgement* — how to score a rendered mark; read before presenting |
| `mood-references.md` | Optional. When to use generated imagery for direction, and why never to trace it |

A mark needs all four: a position, an idea, a construction, and craft. Skipping the first two is
what produces technically correct, entirely forgettable logos.

## Phase 1: Interview

### Step 1: Gather context automatically

If the user points to a repo, URL, or existing project:

- Read the README, `package.json`, CSS/theme/config files, and any existing branding
- Extract: project name, purpose, tech stack, color palette, design language, fonts
- Summarize what you found before asking anything — never ask what you can already see

If there is no project context, go straight to Step 2.

### Step 2: Ask, briefly

Use `AskUserQuestion`. Batch related questions into one call. **Skip anything already answered.**
Two questions is usually enough, because format defaults to an icon mark.

**Question 1 — Style direction:**

```
question: "What direction should the mark take?"
header: "Style"
options:
  - label: "Minimal / geometric"
    description: "Clean shapes, generous negative space, modern"
  - label: "Bold / graphic"
    description: "Heavy weight, high contrast, strong silhouette"
  - label: "Playful / organic"
    description: "Friendly curves, hand-drawn feel, warmth"
  - label: "Match my project"
    description: "Extract the design language from your existing code"
```

**Question 2 — Color:**

```
question: "Any color preferences?"
header: "Colors"
options:
  - label: "Use project colors"
    description: "Pull from your existing design system"
  - label: "Surprise me"
    description: "Pick a palette that fits the concept"
  - label: "Monochrome"
    description: "Single color + background — strongest test of the form"
  - label: "I have specific colors"
    description: "Ask me for them"
```

Ask about format **only** if the user hints they want text in the mark. Ask about sizes **only**
if they mention a platform with unusual requirements.

If the user says "just make something", use icon mark / minimal geometric / surprise me and go.

### Adapting

- **Points to a repo:** gather context, then ask style only.
- **Detailed description given:** ask nothing that is already covered.
- **"Design a logo for X":** ask both questions.

Move to Phase 2 once you can brief five meaningfully different concepts.

## Phase 1.5: Name the direction

Do this before drawing anything, and state it to the user.

1. **Identify the domain and open `references/anti-cliche.md`.** Write down the banned list for
   this product. Those marks are now unavailable in every concept — including the one the brief
   implicitly asks for. If the existing logo you are replacing *is* the cliché, say so.
2. **Write one conceptual seed per concept** — a single sentence naming the specific idea that
   concept encodes, which would be false of a competitor. Seeds are written before SVG, never
   reverse-engineered afterwards.
3. **Assign one named lineage per concept** from `references/design-lineages.md`, choosing five
   that genuinely disagree in temperament.

Present this as a short table before generating, so the user can redirect a bad seed cheaply
rather than after five SVGs exist:

| # | Lineage | Seed |
|---|---|---|
| 1 | Japanese Mon | The mark is the shape of the silence being listened through |

## SVG conventions

Every SVG this skill writes must follow these:

- **viewBox only** — `viewBox="0 0 100 100"` for icon marks, no `width`/`height` attributes.
  Use `0 0 1024 512` only for wordmarks and combination marks.
- **Self-contained** — no external fonts, images, or cross-file `<use>`. Everything inline.
- **Named groups** — wrap logical sections in `<g>` with stable IDs: `id="icon"`,
  `id="wordmark"`, `id="tagline"`. This is what makes "make the icon bigger" a one-line edit
  and lets iterations be diffed against each other.
- **Flat fills by default** — solid `fill`. Gradients only when the user asks or the concept
  genuinely depends on one.
- **Stroke weight** — in a 100×100 viewBox, primary strokes are 3–4, secondary 2. Below 2.5 the
  mark looks weak and vanishes at favicon size; above 5 it looks clumsy.
- **Text** — always convert to `<path>`; never ship a live `font-family` in a logo, because the
  mark then renders differently on any machine lacking that font. For wordmarks, prefer an OFL-licensed
  face — OFL permits redistribution, so a wordmark drawn from one is safe to ship commercially.
  If the `canvas-design` skill is installed it bundles 54 such faces at
  `canvas-design/canvas-fonts/`; otherwise pull one from Google Fonts. Set the text, then convert
  to outlines before saving.
- **Clean markup** — no stray transforms, no empty groups, no editor cruft.
- **Never bake a background plate into an icon mark.** The mark's own geometry carries the
  form; every void must be a real hole (mask, `fill-rule="evenodd"`, or subtracted path), not
  an opaque shape in the background color. A mark with a plate behind it flattens to a solid
  square when rendered as a macOS menu-bar template, an inverted favicon, or a single-color
  print. If a backdrop is wanted for presentation, put it in a separate `<g id="backdrop">`
  in the *preview*, never in the shipped SVG.
- **Filter the pattern families against the brief before assigning them.** If the brief
  forbids lettering, drop the geometric-letterform family rather than assigning it anyway —
  a single abstracted initial is still lettering.

## Phase 2: Explore

Generate **5 distinct concepts**. Distinct means a different *construction*, not a different
color of the same idea.

### Allocate the risk before allocating the geometry

Apply the **3+1+1 rule** from `references/anti-cliche.md`. Three concepts answer the brief
directly; one deliberately breaks a stated *soft* preference; one argues for the opposite
temperament. Hard constraints — 16px legibility, monochrome survival, no lettering when
forbidden — are never broken, by any of the five.

Five safe concepts is a failed round. Do not quietly drop the risky two before showing them.

### Assign one pattern family per concept

Open `references/construction-patterns.md` and pick five different families that suit the brief.
Each concept gets exactly one family as its structural backbone:

| Family | Reads as |
|---|---|
| Geometric letterform | Abstracted initial — literal, ownable |
| Boolean shape | Two primitives cut into each other — modern, corporate |
| Negative-space mark | The subject is the hole, not the ink — clever, memorable |
| Line system | Waves, arcs, parallel rhythm — motion, signal, flow |
| Node network | Points plus connections — infrastructure, relation |
| Dot matrix | Density gradients from repeated dots — digital, systematic |
| Container mark | Symbol inside a squircle/circle — app-icon native |
| Pictorial abstraction | Simplified real object — concrete, friendly |

### Raw shape vocabulary (optional)

If the brief calls for forms richer than primitives — lobed, tiled, gooey, systematically
repeated — generate a batch first and curate it, rather than drawing such forms freehand:

```bash
python3 <path-to-skill>/scripts/shapegen.py sheet --out logos/vocab/
```

Discard most of it. Redraw the survivors by hand so they carry their concept's seed. See
"Generating raw shape vocabulary" in `references/construction-patterns.md`.

Two generators matter beyond the raw vocabulary:

- `squircle --exp 4` emits a **true superellipse** — continuous curvature, unlike `rect rx`
  whose curvature jumps at the tangent point. That discontinuity is why an app icon drawn with
  `rx` looks subtly cheaper than one drawn with a superellipse; use it for any container mark.
- `carve --cuts 2` emits **real subtraction** — one path, `fill-rule="evenodd"`, so overlaps
  become true holes. A same-coloured shape laid on top *looks* identical and is not: it fills
  solid under a monochrome flatten. `audit.sh` tells the two apart by region count.

**Do not trace images found online.** A traced asset is a derivative work you cannot trademark,
and traced raster edges produce hundreds of path nodes that turn to mush at 16px. Reference
images are for studying structure, never for extracting geometry.

### Parallel generation

Dispatch one agent per concept using the Agent tool, **all in a single message** so they run
concurrently. Use `subagent_type: "general-purpose"`.

Agents share no context. Each prompt must carry, in full:

1. The project name, purpose, palette, and style brief
2. Its assigned pattern family, and the relevant recipe copied out of
   `references/construction-patterns.md`
3. The full SVG conventions above
4. The core principles from `references/design-principles.md` — at minimum: 40%+ negative
   space, one focal point, stroke 3–4, must survive 32px
5. Its exact output path, e.g. `logos/concepts/concept-3.svg`

Create `logos/concepts/` before dispatching.

### After the agents finish

1. **Check each concept against the pre-flight checklist** in `references/design-principles.md`.
   Regenerate any that fail — a busy or off-brief concept wastes a whole review round.
   Run the two mechanical tests rather than asserting the results from the markup:

   ```bash
   # 16px legibility — upscale with no smoothing and actually look at it
   rsvg-convert -w 16 -h 16 -o /tmp/c.png concept-1.svg
   magick /tmp/c.png -filter point -resize 800% /tmp/c16.png

   # single-color template — if this comes back a solid blob, the mark has a
   # background plate baked in and must be rebuilt
   rsvg-convert -w 200 -h 200 -o /tmp/t.png concept-1.svg
   magick /tmp/t.png -alpha extract -background white -alpha shape \
     -fill '#111' -colorize 100 -background white -flatten /tmp/tpl.png
   ```

   Read both PNGs before showing the concept to the user.
2. **Run the audit — it is a gate, not a report.**

```bash
bash <path-to-skill>/scripts/audit.sh   logos/concepts/     # measurable failures
python3 <path-to-skill>/scripts/similarity.py check logos/concepts/   # prior art
```

   `audit.sh` measures ink coverage, monochrome collapse, whether interior counters survive
   16px, thinnest feature, node count, and pairwise distinctness across the round. It exits
   non-zero on failure. **Fix every FAIL and re-run before a human sees the concepts** — these
   are exactly the defects that are invisible in the SVG source and obvious in the pixels.

   A `TOO ALIKE` pair means the round is one idea wearing five hats: regenerate, don't recolour.

   `similarity.py` checks each mark against ~3,450 real brand marks (CC0 `simple-icons`).
   Anything under 0.055 must be reworked; 0.055–0.085 needs a look by eye. First run needs
   `similarity.py build` (~45s, cached to `~/.cache/logo-designer`). It is a prior-art smoke
   test, not a trademark search — say so when reporting a clean result.

3. **Score what survived** against `references/critique-rubric.md`, from the renders rather
   than the markup. Anything scoring 1–2 on Idea or Ownability is dead regardless of its craft.

4. **Run the reduction pass** (`references/anti-cliche.md`, Part 5). Subtractive only: remove
   anything not carrying the seed, merge elements doing the same job, widen the negative space
   to just before the form breaks. If your instinct is to add a shape, that is the signal to
   remove one instead. A mark that survived a deliberate attempt to strip it looks inevitable
   rather than assembled — that impression is the entire difference between shipping and
   regenerating.
5. Generate `logos/preview.html` from `references/preview-template.md`, with `{{PHASE}}` set to
   `Concepts`. Include the favicon size strip from the very first round: an icon mark that
   fails at 32px is disqualified regardless of how it looks at 512px.
6. Tell the user to open `logos/preview.html`.
7. Present each concept as **lineage + seed**, not as a description of its shape — the user is
   choosing between positions and ideas. Label the two risky concepts plainly, e.g. "this one
   ignores your preference for restraint, because the product is louder than the brief admits."
8. Ask: "Which direction do you want to explore? Pick a number, or tell me what works and what
   doesn't across them."

```
logos/
├── concepts/
│   ├── concept-1.svg … concept-5.svg
└── preview.html
```

## Phase 3: Refine

Copy the chosen concept to `logos/iterations/iteration-1.svg` and work forward from there.

**Single tweak** — specific feedback ("thicker strokes", "rotate the cut 15°"): edit it yourself
and write the next numbered iteration. Do not spawn an agent for a one-line change.

**Batch exploration** — 3+ variations at once ("try five palettes", "vary the aperture angle"):
dispatch parallel agents as in Phase 2. Paste the **full base SVG** into every prompt, name the
exact variation and output path, and restate the SVG conventions.

After each round:

1. Regenerate `logos/preview.html` (`{{PHASE}}` = `Iterations`, most recent first)
2. Tell the user to refresh
3. Say what changed in one line, then ask for the next note

### Iteration rules

- Keep group IDs stable across iterations so changes are diffable
- "Go back to iteration N" → that file becomes the new base
- **Always include the favicon strip.** If strokes vanish at 32px, proactively propose
  thickening them; if fine detail muddies, propose removing it. Catching this here saves rounds.
- Between two iterations that read the same at 32px, keep the simpler one
- Test monochrome at least once — if the mark only works in color, the form is weak

## Phase 4: Export

Triggered by "export", "this is the one", "I'm happy with this".

1. Confirm which iteration is final if ambiguous
2. `mkdir -p logos/export` and copy the final SVG to `logos/export/logo.svg`
3. For a combination mark, also write `logos/export/icon.svg` — the `#icon` group alone, in a
   tight square viewBox, wordmark removed. Never squeeze a horizontal lockup into a square.
4. Run the bundled script:

```bash
bash <path-to-skill>/scripts/export.sh logos/export/logo.svg logos/export/
```

With a separate icon:

```bash
bash <path-to-skill>/scripts/export.sh logos/export/logo.svg logos/export/ logos/export/icon.svg
```

Produces `logo-16/32/48/180/192/512/1024/2048.png`, plus the matching `icon-*.png` family when
an icon SVG is given. Use `icon-*` for favicons and app icons.

5. **Generate the handoff.** A folder of PNGs is not a usable deliverable — people need the
   mark in the form their codebase actually takes:

```bash
bash <path-to-skill>/scripts/snippets.sh logos/export/logo.svg logos/export/ MyLogo
```

   Writes `logos/export/USAGE.md` with paste-ready inline SVG, a React component, a CSS data-URI
   background, a **monochrome mask** rule for menu-bar/inverted use, the favicon `<head>` block,
   web-manifest entries, and the Swift template snippet. Point the user at it explicitly.

6. List the exported files with their sizes.
6. If the script reports no converter, relay its install instructions verbatim — they name real,
   verified packages.

## Phase 5: Repo integration (optional)

Only when the user asks to commit the logo or open a PR.

1. **Find the existing targets** — `public/favicon.svg`, `favicon.ico`, `public/pwa-*.png`,
   `apple-touch-icon.png`, `assets/logo.svg`, `*.appiconset/`, `manifest.json`, README badges.
2. **Branch** — `chore/new-logo` on the existing checkout.
3. **Replace only files that already exist.** Do not introduce icon files the project does not
   reference. Standard mappings: `favicon.ico` 48px, `apple-touch-icon.png` 180px,
   `pwa-192x192.png` 192px, `pwa-512x512.png` 512px, iOS `AppIcon-512@2x.png` 1024px.
4. **Commit and PR** — summarize what was replaced and include the before/after at 32px.
