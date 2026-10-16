# Light brand cards

One card per shortlisted name, so the user can feel each name as a brand before choosing.
Not a brand book: a mark, a wordmark, four colours, a favicon, one sentence.

## Per card

1. **Positioning in one line** (kept in your notes): "For [audience], [name] is the [category]
   that [difference]." Every choice below should serve it.
2. **Mark**: one simple geometric idea tied to the name's meaning or sound (a loop that lands
   on a dot, two lines merging, three bars, a ripple). `build_shortlist.py` has a set of marks;
   add your own as inline SVG paths. The final mark is designed later with `logo-designer`.
3. **Wordmark**: one free font (Google Fonts), one weight, tracking set. Vary fonts across
   cards so names are judged on their own; do not reuse one font for every card.
4. **Four colours, each with a job**: primary (logo, buttons), accent (the dot, highlights),
   ink or neutral (text), light ground (background). HEX for each.
5. **Two tiles**: the logo on the light ground, and the logo on the brand ground. Optional
   overrides per tile (`t1`, `t2`) for brands whose second tile is not the primary colour.
6. **Favicon at 24px and an app icon**, so legibility at small sizes is visible.
7. **One sentence of rationale** linking mark, colour and name.

## Checks

- Run `scripts/contrast.py` on every pair you use. Body text at least 4.5:1; wordmark and marks
  at least 3:1 on both grounds. Every colour chip picks its own text colour by contrast.
- Avoid the stock looks: beige plus brass plus espresso, purple-to-blue gradients, lime on
  black, sparkle icons, anything that resembles a competitor in the category.
- No industry clichés (lightbulbs, gears, chat bubbles with robots) without a twist.
- Change one card without touching the others when the user asks.

## In-use mockups (for the two or three names the user leans toward)

Write product-specific copy, then show:

- **App window**: sidebar with the logo, a real-looking item (a meeting, a document), the one
  brand-coloured element (for a notes app: the plan card), a primary button.
- **Phone**: a lock-screen notification and the app icon on a home screen next to two neutral
  apps.
- **Team chat**: a teammate asks a colleague to share their notes from the product, using the
  name the way people talk ("can you drop your noodl notes from the Halden call?"). The reply
  carries a link preview of the shared item, not a product blurb. Use made-up people.
- **Social post**: a square image in the brand ground with a short headline and one product
  motif, plus a caption written in the brand's voice.

# The full brand board (Phase 7, for the chosen name only)

The light card was for choosing. Once a name is chosen, build one full board for it. The
method follows the shape of the community "brandkit" skill (credited in SKILL.md), written
here in our own words.

1. **Brief**: industry, audience, two or three competitors, three brand attributes. Fill gaps
   with stated assumptions and mark them as assumptions.
2. **Positioning**: "For [audience], [name] is the [category] that [difference]." Test every
   later choice against this sentence; drop anything that does not serve it.
3. **Two or three directions** (for example quiet product versus loud social, geometric versus
   warm), each with a one-line rationale. Recommend one and say why.
4. **Colour system, six colours at most**: one primary, one or two secondary, two neutrals, one
   accent. Each has a HEX value and a named job ("the plan card", "recording state"). No
   decorative extras. Check every text pair with `scripts/contrast.py` in light and dark mode.
5. **Type, two families at most**, both freely licensed (Google Fonts or the client's own
   licence): one for headings, one for text, with fallback stacks and a size scale (a 1.25
   ratio works well: 49, 39, 31, 25, 20, 16).
6. **Three to five logo concepts**, wordmark first and a symbol only when the idea earns it.
   Design and audit them with the `logo-designer` skill: one colour, inverted, and legible as a
   24px favicon.
7. **Mockups** using only the defined colours and fonts: a website hero, a business card, a
   social profile image, plus the in-use set from the shortlist (app, phone, team chat, post).
8. **One page** that puts it together, and a short text spec: the positioning sentence, the
   colour table (HEX and job), the fonts with their licence, why each logo concept works, and
   three don'ts.

Every decision gets one sentence of reasoning, not just an assertion. No category clichés
(lightbulbs, gears, handshakes, robot chat bubbles) unless there is a deliberate twist.
