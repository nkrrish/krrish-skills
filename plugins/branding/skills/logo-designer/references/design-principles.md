# Design Principles for Icon Marks

The quality bar. Read this before generating any concept, and check every concept against the
pre-flight checklist before showing it to the user.

Generated logos fail in predictable ways: too many elements, no focal point, decoration
standing in for an idea, and detail that dissolves at favicon size. Each rule below exists to
block one of those failures.

---

## Part 0: What separates a real mark from a generated one

### 1. One idea, one to two elements

A mark carries a single idea. Two elements maximum, and the second must earn its place by
doing something the first cannot.

- **Weak**: a hexagon grid of twelve cells, a circle with three orbiting dots and a swoosh
- **Strong**: one thick incomplete ring; two circles merging at the seam; a square with one
  corner cut away
- **Why**: memorability is a function of how few things the eye has to encode. A mark you can
  describe over the phone in one sentence is a mark people can recall.

### 2. Negative space is 40–50% of the canvas

Empty area is structure, not leftover. Marks that fill their box read as illustrations.

- **Weak**: elements pushed to the viewBox edges, gaps under 6 units
- **Strong**: a wide central void, deliberate 10–14 unit gaps, the form floating clear of the edge
- **Practical**: keep artwork inside roughly `8,8 → 92,92` in a 100×100 viewBox. That margin is
  what stops the mark from colliding with a rounded app-icon mask.

### 3. Proportions are decided, not defaulted

In a 100×100 viewBox:

| Property | Value |
|---|---|
| Primary stroke width | 3–4 |
| Secondary stroke width | 2–2.5 |
| Dot radius | 2–8 |
| Minimum gap between elements | 8–12 |
| Corner radius on squircles | 20–24 |

`stroke-width="1.5"` looks timid and disappears at 32px. `stroke-width="6"` looks blunt.
Pick a value on purpose and hold it consistent across the whole mark — mixed stroke weights
inside one icon are the single most common tell of generated work.

### 4. Asymmetry creates tension

Perfect four-fold symmetry is inert. Introduce one deliberate imbalance.

- **Weak**: a perfectly centered, perfectly mirrored arrangement
- **Strong**: a ring broken at one point; a cluster weighted to the lower left; a shape rotated
  12° off axis
- **Caveat**: asymmetry must look chosen. A 3° rotation reads as a mistake; 12–20° reads as
  intent.

### 5. Restraint over decoration

Every element justifies its existence or gets deleted.

- **Delete on sight**: drop shadows, bevels, glows, three-color gradients, sparkles, orbit
  rings added "for balance", outlines around outlines
- **Test**: remove any single element. If the mark still communicates the idea, that element was
  decoration. Leave it out.

### 6. One focal point

The eye should land in exactly one place and then read outward. Two competing centers of
attention make a mark feel unresolved.

- Achieved by: one element noticeably larger, or heavier, or the only one in the accent color
- **Weak**: four equal quadrants, evenly spaced identical dots

### 7. Structural stability

The form should sit on the canvas, not drift in it. Anchor it: align to a visual baseline,
center of mass at or slightly above geometric center (optical centering — a mathematically
centered form looks like it is sinking).

### 8. Cuts and joins are rounded or deliberately sharp — never accidental

Where two shapes meet or a shape is cut, the treatment is a design decision applied
consistently. Round every join (`stroke-linecap="round"`, `stroke-linejoin="round"`) or square
every join. Mixing them within one mark looks unresolved.

### 9. The form works in one color

Design in monochrome first, add color after. Color is the least durable part of a mark — it
changes with themes, prints, and embroidery. If the silhouette does not communicate on its own,
color is compensating for a weak form and the mark will fail on a dark background, in a
watermark, and in a fax.

---

## Part 1: Sizes govern everything

An icon mark's hardest job is 16–32px. Design at 512 but judge at 32.

| Size | What survives |
|---|---|
| 16px | Silhouette and one interior cut. Nothing else. |
| 32px | Two elements, strokes ≥ 3, a single interior detail |
| 48px | Three elements, subtle asymmetry becomes visible |
| 192px+ | Fine detail, gradients, texture |

Rules that follow from this:

- Solid fills beat thin strokes at small sizes
- An interior gap narrower than ~4 units (in a 100 viewBox) will close up into mud
- Counters — the enclosed holes in shapes like a, e, o — need to be generously oversized
  relative to what looks right at 512px
- If a detail will not survive being 32px wide, it does not belong in the mark

---

## Part 2: Color

- **Two colors, plus background.** Three is already a stretch for an icon mark.
- **Contrast ratio of at least 3:1** between the mark and its background, so it holds up as a
  favicon on both light and dark browser chrome.
- **One accent.** If everything is accented, nothing is.
- **Gradients**: only along a single hue's value range, only when the concept depends on depth
  or motion. Never rainbow, never as a substitute for a form decision.
- **Test both grounds.** Every mark must be checked on white and on near-black. A mark that
  needs an inverted variant is fine; a mark that only works on one ground is not finished.

---

## Part 3: Pre-flight checklist

Run this on every concept before showing it. Any "no" means fix or regenerate.

**Form**

- [ ] One clear idea, two elements maximum
- [ ] 40%+ of the canvas is empty
- [ ] Artwork sits within the safe margin, clear of the viewBox edge
- [ ] A single focal point
- [ ] One deliberate asymmetry, or a stated reason for symmetry
- [ ] Nothing present that could be deleted without losing the idea

**Craft**

- [ ] Consistent stroke weight, in the 3–4 range for primaries
- [ ] Joins and caps consistently rounded or consistently sharp
- [ ] Optically centered, not just mathematically centered
- [ ] No shadow, bevel, glow, or unrequested gradient

**Durability**

- [ ] Flattens to a single color without becoming a solid blob (no background plate baked in)
- [ ] Readable at 32px
- [ ] Silhouette communicates in a single flat color
- [ ] Holds up on both white and near-black
- [ ] Distinct from the other concepts in this round in *construction*, not just color

**Technical**

- [ ] `viewBox` set, no `width`/`height` attributes
- [ ] Self-contained — no external font, image, or reference
- [ ] Groups named with stable IDs
- [ ] Markup is clean enough to hand-edit
