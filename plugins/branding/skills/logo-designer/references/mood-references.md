# Mood References (optional)

Generated imagery has exactly one legitimate role in logo design: **agreeing on a direction
before anyone draws.** It is a conversation aid, not a source of geometry.

## Never trace generated output

This is not a stylistic preference, it is structural:

- Diffusion output is anti-aliased raster. Traced, it yields 200–800 path nodes, "circles" that
  are not circular, and stroke weights that drift 30% along a single stroke. Every proportion
  rule in `design-principles.md` is violated by construction.
- You will redraw it by hand anyway — at which point the image was a mood board, and you should
  have treated it as one from the start.
- Provenance: the US Copyright Office will not register works lacking human authorship.
  Trademark is a separate regime and is what actually protects a logo, but "traced from model
  output" is a materially weaker authorship story than "drawn from a stated concept."
  Keep the geometry human.

`scripts/audit.sh` will flag a traced mark on node count alone. If a concept comes back with
>90 nodes on an icon mark, that is what happened.

## When a mood pass is worth the round trip

Only when the *aesthetic direction* is genuinely unresolved and words are failing — the user has
said "modern" three times and rejected three different readings of it. Generate four images
representing four lineages from `design-lineages.md`, ask which one feels right, then draw.

If the direction is already clear, skip this entirely. It is a tie-breaker, not a stage.

## How to run one

This skill ships no image generation and requires no API key. If the session has an image tool
available, use it directly with prompts built from the lineage vocabulary:

> "A single abstract mark, {lineage} aesthetic — {its 'in a mark' description from
> design-lineages.md}. Flat, one colour on a plain ground, no text, no gradient, no shadow,
> centred, high contrast."

Four images, one per lineage, presented side by side. Ask which *direction* is right — never
"which logo do you like", because none of them are logos.

Then discard the images. They do not enter the deliverable, they are not referenced in the
concept files, and they are not shown alongside finished marks — where they would only make the
real work look worse by inviting a comparison against something that never had to survive 16px.

## What to take from a chosen image

Take the **temperament**: weight, density, angularity, how much space it breathes, whether it
feels carved or constructed or grown. Write that into the brief in words.

Take nothing else. Not the shapes, not the composition, not the palette.
