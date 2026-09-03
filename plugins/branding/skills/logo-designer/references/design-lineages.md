# Design Lineages

A named aesthetic position, chosen **before** any drawing, is what separates a mark with a point
of view from a competent shape. "Minimal geometric" is not a position — it is the absence of one,
and it is why generated logos converge on the same rounded-square-with-a-glyph.

Pick **one** lineage per concept and commit to it completely. A half-committed lineage reads as
indecision. Name the lineage out loud when presenting the concept — the user is choosing between
positions, not between pictures.

---

## Swiss Rationalist
*Müller-Brockmann, Vignelli, Unimark*

Believes the mark should be the most reduced true statement of the thing, and that reduction is
achieved by construction, not by taste. Everything sits on a visible underlying grid; every curve
is a compass arc; every angle is 0/30/45/60/90.

**In a mark:** circles struck from a single radius, stems of exactly one weight, mathematical
spacing. No optical fudging that cannot be justified.
**Suits:** infrastructure, finance, transport, tools that must feel dependable.
**Fails as:** cold, anonymous, forgettable — the failure mode is a mark nobody objects to.

## Ulm Systems
*HfG Ulm, Otl Aicher, the Munich '72 pictograms*

Believes a mark is one member of a system that does not exist yet. It is drawn as though forty
siblings must follow, from the same modular kit.

**In a mark:** strict 45° diagonals, uniform stroke terminals, forms built from a limited part
vocabulary. Reads instantly at signage distance.
**Suits:** products with many surfaces — apps with feature icons, design systems, platforms.
**Fails as:** generic pictogram; guard against it by making one part of the kit strange.

## Bauhaus Primitives
*Albers, Bayer, Schlemmer*

Believes circle, square and triangle carry inherent meaning and that colour is structural, not
decorative. Composition through overlap and tension between three pure forms.

**In a mark:** two or three primitives, overlapped so the intersections become the subject.
Flat, unmodulated colour.
**Suits:** education, creative tools, anything claiming first principles.
**Fails as:** a child's shape-sorter; guard by making the overlap do something unexpected.

## Japanese Mon
*Kamon family crests, 12th century onward*

Believes a mark must be perfectly legible as a silhouette at any scale, on cloth, in ink, at
arm's length — and that negative space is the primary material. The most refined tradition of
pure marks in existence, and the most under-used reference in software.

**In a mark:** radial or bilateral symmetry inside a strict circular boundary, forms rendered as
solid mass with white cuts of equal weight to the black. Nothing thin, nothing accidental.
**Suits:** anything wanting permanence and quiet authority. Exceptional for app icons.
**Fails as:** pastiche if you borrow motifs rather than the method. Borrow the method.

## Constructivist
*Rodchenko, Lissitzky, Stenberg brothers*

Believes form should express force. Diagonal energy, wedges, the sense that the mark is
mid-motion and slightly unstable.

**In a mark:** a dominant diagonal axis, forms that cantilever, deliberate off-balance
resolved by one anchoring element.
**Suits:** speed, transformation, anything disrupting an incumbent.
**Fails as:** a paper-plane logo; guard by resisting the arrow.

## Op / Systematic Repetition
*Vasarely, Bridget Riley, Anni Albers' weaving*

Believes meaning accumulates through patient repetition, and that the eye completes what the
pattern implies. Dense fields of near-identical marks that shift by increment.

**In a mark:** a repeated unit with a controlled gradient of size, spacing or rotation; the form
emerges from the field rather than being drawn.
**Suits:** data, audio, density, anything about many-becoming-one.
**Fails as:** mud at small sizes. Only viable if the gradient survives 32px — test early.

## Brutalist Mass
*Le Corbusier, Paul Rudolph, concrete*

Believes weight is honesty. Enormous solid forms, raw cuts, no tapering, no politeness.

**In a mark:** one heavy mass with a single decisive cut through it. Stroke weights far beyond
comfortable. Deliberately blunt terminals.
**Suits:** developer tools, security, anything that should feel unbreakable.
**Fails as:** a black blob; the cut has to be as considered as the mass.

## Instrument / Signal
*Oscilloscopes, seismographs, spectrograms, scientific plotting*

Believes the mark should look like a reading taken from the world rather than a picture drawn of
it. Treats the product's phenomenon as something measured.

**In a mark:** plotted forms, tick marks, axis logic, envelopes and decay curves — the visual
grammar of instrumentation, abstracted until only the gesture remains.
**Suits:** audio, sensing, monitoring, anything transforming a real-world signal.
**Fails as:** a literal waveform. The lineage is the *logic of measurement*, not the squiggle.

## Terminal Vernacular
*ASCII art, monospace grids, early bitmap icons*

Believes the constraint of the cell grid is the aesthetic. Everything snaps to a coarse grid,
diagonals are staircases, curves are approximations.

**In a mark:** a deliberately low-resolution construction that stays crisp because it was drawn
at the resolution it will be viewed at. Pixel-honest.
**Suits:** developer tools, CLIs, anything with a terminal-native audience.
**Fails as:** nostalgia kitsch; guard by keeping the grid coarse but the composition modern.

## Memphis / Postmodern
*Sottsass, Ettore, the Milan group*

Believes seriousness is a pose and that clashing elements can cohere through confidence alone.

**In a mark:** shapes that do not belong together, an unexpected colour against the palette, a
deliberate wrongness held with total conviction.
**Suits:** consumer products, creative tools, brands competing on personality.
**Fails as:** noise. Only one element may be wrong; the rest must be immaculate.

## Woodcut / Carved
*Block printing, Vallotton, punch-cutting*

Believes the mark should carry the trace of the tool that made it. Slight irregularity,
chiselled terminals, the sense of material resistance.

**In a mark:** subtly non-uniform edges, tapered cuts, contrast between a heavy mass and a fine
carved line. All irregularity deliberate and drawn, never a filter.
**Suits:** craft products, editorial, food, anything claiming human authorship.
**Fails as:** "handmade" texture applied on top. The irregularity must be structural.

---

## Choosing lineages for one round

Pick five that genuinely disagree with each other, so the user is choosing a *position*:

- **Developer tool:** Terminal Vernacular, Brutalist Mass, Ulm Systems, Swiss Rationalist, Constructivist
- **Audio / sensing:** Instrument, Op, Japanese Mon, Brutalist Mass, Constructivist
- **Consumer app:** Japanese Mon, Bauhaus Primitives, Memphis, Ulm Systems, Woodcut
- **Infrastructure / B2B:** Swiss Rationalist, Ulm Systems, Brutalist Mass, Instrument, Japanese Mon

Never fill a round with five lineages from the same temperament. If four are cold and rational,
the user is not really being offered a choice.
