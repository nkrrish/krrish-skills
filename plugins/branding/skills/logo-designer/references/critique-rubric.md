# Critique Rubric

Run this on rendered PNGs, never on markup. Reading an SVG source tells you what you intended;
looking at the render tells you what exists. Every failure found in building this skill — blank
exports, collapsing background plates, a gouge that silted up at 16px — was invisible in the
source and obvious in the pixels.

## Order of operations

1. `scripts/audit.sh logos/concepts/` — the measurable failures. Fix every FAIL before looking.
2. `scripts/similarity.py check logos/concepts/` — prior art.
3. Then, and only then, this rubric — the judgements a machine cannot make.

The audit and similarity checks are gates. This rubric is the interesting part, and it is only
worth your attention on marks that already passed.

## Look at four renders per mark

Never judge from one. Render at **512 on white**, **512 on near-black**, **32**, and **16**.

| Render | The question it answers |
|---|---|
| 512 light | Is the drawing actually well made? Joins, tangents, optical balance |
| 512 dark | Does the form invert cleanly, or was it relying on a light ground? |
| 32 | Is it still the same mark, or a different one? |
| 16 | Is it still *a* mark, or a smudge? |

## Score each, 1–5

**Idea** — does the mark carry its seed, without a caption?
1: generic category picture. 3: readable once explained. 5: the form *is* the idea.

**Ownability** — could this belong to a competitor with no change but the colour?
1: interchangeable. 3: distinct in its category. 5: unmistakable.

**Craft** — tangents, terminals, optical centring, weight consistency.
1: parts assembled. 3: clean but inert. 5: looks arrived at, not composed.

**Durability** — 16px, monochrome, inverted, embroidered, one inch wide.
1: only works at hero size. 3: survives. 5: gets better as it gets smaller.

**Restraint** — is anything present that could be removed?
1: three ideas fighting. 3: one element too many. 5: nothing left to take away.

Anything scoring 1–2 on Idea or Ownability is dead regardless of its craft score. A beautifully
drawn generic mark is still a generic mark, and craft is the cheapest of the five to fix later.

## Questions that find real problems

- Cover the colour. Is it still good? If not, colour is doing the work.
- Describe it to someone over the phone in one sentence. If you can't, it is too complex.
- What else does it read as? Every mark has a second reading — find it before a customer does.
  Letters, body parts, and rude shapes are the three to check deliberately.
- Would this survive being the 40th icon in a macOS menu bar at 16px, in grey?
- If a competitor shipped this tomorrow, would you think they'd done well?

## Recording the verdict

State the score, the second reading you found, and the one change that would raise the lowest
axis. "Concept 3: Idea 4, Own 4, Craft 3, Dur 5, Restraint 4. Second reading: a lowercase 'b'.
Raise Craft by aligning the inner cut's tangent to the outer arc." That is a note the next
iteration can act on. "Looks good" is not.
