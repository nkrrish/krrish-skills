# Construction Patterns

Structural recipes for icon marks. In Phase 2, assign each concept **one** family so the five
concepts differ in construction rather than in color.

All snippets are in a `viewBox="0 0 100 100"` and use `currentColor` where a single-color test
is useful. Treat them as skeletons: change the proportions, angles, and counts to fit the brief.
Shipping a recipe unmodified produces a generic mark.

---

## 1. Geometric letterform

Abstract the project's initial into pure geometry — arcs, bars, and cuts rather than a typeface.
Reads as literal and ownable. Best when the name is short and the initial has a distinctive
skeleton (A, K, M, R, S, W beat H, I, L).

```svg
<g id="icon" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round">
  <path d="M28 76 L50 24 L72 76" />
  <path d="M38 58 H62" />
</g>
```

Moves: cut one stroke short of the join; replace one straight with an arc; let the crossbar
break the outer contour; rotate the whole letter 12–18°.

**Avoid**: setting the letter in a real font and calling it a logo.

---

## 2. Boolean shape

Two primitives intersected, subtracted, or united. The most reliable route to a mark that looks
professionally drawn, because the geometry does the work.

```svg
<g id="icon">
  <circle cx="42" cy="50" r="26" fill="currentColor"/>
  <circle cx="62" cy="50" r="26" fill="#fff"/>
  <circle cx="62" cy="50" r="22" fill="currentColor"/>
</g>
```

That is a crescent by subtraction. Other operations: square minus circle (rounded notch),
triangle intersect circle (a shield or a pick), two squares offset and united.

Moves: vary the overlap between 25% and 60% — under 25% reads as two objects, over 60% loses
both silhouettes.

**Avoid**: a subtraction so subtle it reads as a rendering bug.

---

## 3. Negative-space mark

The subject is the hole. High memorability when it lands, and the strongest differentiator in a
concept round.

```svg
<g id="icon">
  <rect x="14" y="14" width="72" height="72" rx="22" fill="currentColor"/>
  <path d="M40 32 L66 50 L40 68 Z" fill="#fff"/>
</g>
```

Here the play triangle exists only as absence. Works with arrows, chevrons, letters, keyholes,
and simple silhouettes.

Moves: let the negative form break the container edge; make it asymmetric within the container.

**Avoid**: a negative shape under ~20 units across — it closes up at 32px.

---

## 4. Line system

Parallel lines, waves, or concentric arcs. Communicates motion, signal, sound, flow, data.

```svg
<g id="icon" stroke="currentColor" stroke-width="4" stroke-linecap="round" fill="none">
  <path d="M22 50 H30"/>
  <path d="M38 34 V66"/>
  <path d="M50 26 V74"/>
  <path d="M62 38 V62"/>
  <path d="M74 46 V54"/>
</g>
```

An amplitude envelope. Vary the envelope shape — rising, symmetric, decaying, interrupted — to
change the meaning.

Moves: break the rhythm at exactly one position; use two colors across the run with a single
crossover point; bend the whole system along an arc.

**Avoid**: more than 7 lines. Past that it is texture, not a mark.

---

## 5. Node network

Points joined by connections. Reads as infrastructure, relation, graph, protocol.

```svg
<g id="icon">
  <g stroke="currentColor" stroke-width="3" fill="none">
    <path d="M50 28 L28 66"/>
    <path d="M50 28 L72 66"/>
    <path d="M28 66 L72 66"/>
  </g>
  <circle cx="50" cy="28" r="9" fill="currentColor"/>
  <circle cx="28" cy="66" r="6" fill="currentColor"/>
  <circle cx="72" cy="66" r="6" fill="currentColor"/>
</g>
```

The unequal node radii create the focal point — keep that.

Moves: leave one edge open; make one node hollow; use three or four nodes, never more than five.

**Avoid**: an evenly sized, evenly spaced constellation. That is the single most generic
AI-logo output there is.

---

## 6. Dot matrix

Repeated dots whose size or spacing forms a gradient. Reads digital, systematic, precise.

```svg
<g id="icon" fill="currentColor">
  <circle cx="32" cy="32" r="7"/>
  <circle cx="52" cy="32" r="5.5"/>
  <circle cx="70" cy="32" r="4"/>
  <circle cx="32" cy="52" r="5.5"/>
  <circle cx="52" cy="52" r="4"/>
  <circle cx="70" cy="52" r="2.5"/>
  <circle cx="32" cy="70" r="4"/>
  <circle cx="52" cy="70" r="2.5"/>
</g>
```

The dropped ninth dot and the diagonal size ramp are what make it a composition rather than a
grid.

Moves: mask the matrix inside a circle or letterform; ramp along a diagonal or radius; drop 1–2
dots to open a path through the field.

**Avoid**: a full uniform grid — it has no focal point and turns to grey mush at 32px.

---

## 7. Container mark

A symbol inside a squircle or circle. Native to app icons, where the OS mask expects it.

```svg
<g id="icon">
  <rect x="8" y="8" width="84" height="84" rx="22" fill="currentColor"/>
  <g stroke="#fff" stroke-width="5" stroke-linecap="round" fill="none">
    <path d="M34 52 L46 64 L68 38"/>
  </g>
</g>
```

Moves: let the inner symbol overflow the container edge slightly for tension; use a two-tone
container with a diagonal split.

**Avoid**: a thin interior symbol — inside a container it needs *more* weight, not less. Keep the
inner symbol within a 60×60 safe area so an OS rounding mask cannot clip it.

---

## 8. Pictorial abstraction

A real object reduced to its minimum recognizable form. Concrete and friendly; the risk is
looking like clip art.

```svg
<g id="icon" fill="currentColor">
  <path d="M50 22 C34 22 22 34 22 48 c0 16 14 24 28 32 14-8 28-16 28-32 0-14-12-26-28-26z"/>
  <circle cx="50" cy="46" r="9" fill="#fff"/>
</g>
```

Moves: cut the object with a single straight edge; keep exactly one interior detail; flatten all
perspective.

**Avoid**: more than three curves' worth of detail, and any attempt at shading.

---

---

## Generating raw shape vocabulary

The families above are hand-drawn skeletons. When a brief wants forms with more visual interest
than primitives alone give — lobed rosettes, quarter-disc tile grids, gooey unions — generate a
batch mechanically and curate, rather than trying to draw them freehand:

```bash
python3 <path-to-skill>/scripts/shapegen.py sheet --out logos/vocab/
```

Four systems, all emitting flat single-fill SVG in the standard 0–100 viewBox:

| System | Produces | Notes |
|---|---|---|
| `truchet` | Grids of quarter-disc / square / disc tiles | The workhorse. Enormous variety from four tile types; the basis of most modern geometric shape sets |
| `rosette` | k-fold lobed flowers | Overlapping circles union automatically — no boolean library needed |
| `cluster` | Off-centre gooey unions | Unequal radii supply the focal point |
| `checker` | Positive/negative rhythm with disc counterpoint | Strongest at small sizes |

**These are raw material, not marks.** Most of any generated batch is unusable — unbalanced,
symmetric in the boring way, or lacking a focal point. The workflow is: generate 15–20, discard
the 17 that fail, take the 2 that have something, then redraw them by hand to carry the concept's
seed. A generated shape that has not been redrawn to mean something is decoration.

Tune with `--seed`, `--n` (grid size), `--k` (lobes), `--ratio`, `--density`.

### Match the system to the temperament

The generators are not interchangeable, and picking the wrong one wastes a round:

| System | Temperament | Use when | Avoid when |
|---|---|---|---|
| `truchet` | Precise, systematic, Ulm/Swiss | The product is technical, native, engineered | The mark must carry a narrative idea — tiles read as abstract mass, not as meaning |
| `rosette` | Soft, botanical, decorative | Organic, wellness, craft, hospitality | Anything precise or technical — and note every rosette is radially symmetric, so it has **no focal point** and fails design principle 6 by construction |
| `cluster` | Informal, gooey, playful | Consumer, social, creative tools | Small sizes — lobes merge into a blob below 32px |
| `checker` | Rhythmic, graphic, bold | Pattern-forward brands, editorial | The brief wants a single focal gesture |

### The limit of generated form

Generated vocabulary is good at **form** and useless at **meaning**. A tile grid can be beautifully
balanced and still say nothing about the product, because no seed went into it.

The marks that win are the ones where the form *is* the idea — a step function that steps up and
drops out below where it entered says something a tile grid cannot, no matter how well composed.
So when a generated shape and a seed-driven hand-drawn mark compete, expect the hand-drawn one to
win on anything but decoration. Use the generator to escape a formal rut, not to find the concept.

## Choosing five for one round

Pick families that disagree with each other, so the user's choice is informative:

- **Product / app**: container, negative-space, geometric letterform, boolean, pictorial
- **Developer tool / infra**: node network, boolean, line system, geometric letterform, dot matrix
- **Media / audio / motion**: line system, negative-space, container, boolean, dot matrix
- **Consumer / lifestyle**: pictorial, container, geometric letterform, negative-space, line system

Always include at least one negative-space or boolean concept — those two produce the highest
proportion of marks that survive to a final.
