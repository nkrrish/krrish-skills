# Product photoshoot and ad creatives

Adapted from higgsfield-ai/skills `higgsfield-product-photoshoot` (MIT, © 2026 Higgsfield AI).
The official skill runs through the Higgsfield CLI; here the same idea runs on Marketing
Studio's own prompt enhancer via the API.

## Two ways to generate

**A. Enhanced (preferred when there's a product photo).** Higgsfield assembles the
photography prompt from a preset, like the official skill's backend enhancer.

1. `hf.sh get /marketing-studio/image/presets` (free) and pick the preset that matches the mode below.
2. `hf.sh upload product.jpg` (asks), and optionally a person/model reference.
3. Submit to Sunburst (finals) or Flare (drafts) with
   `{"prompt": "<short intent>", "enhance_prompt": true, "preset_id": "<uuid>",
   "image_urls": ["<product>", "<optional person>"], "resolution": "2k", "aspect_ratio": "auto"}`.
   Enhanced mode takes 1–2 images: product first. `auto` uses the preset's ratio.

Don't write the full photography prompt yourself in this mode: give the short intent and
let the preset do it.

**B. Hand-written (no product photo, or no fitting preset).** `enhance_prompt: false`, write
the prompt using `prompting.md`, and pass up to 16 reference `image_urls` if editing.

## Modes

| Mode | When the user wants… |
|---|---|
| product_shot | Product on a neutral, studio or catalog background |
| lifestyle_scene | Product in a real place: kitchen, gym, café, outdoors, in use |
| closeup_product_with_person | Hands holding, applying, demonstrating; partial face |
| moodboard_pin | Vertical 2:3 Pinterest-native aesthetic |
| hero_banner | Wide website, email or campaign header |
| social_carousel | 3–10 connected slides for IG / LinkedIn |
| ad_creative_pack | Coordinated static ad variants for Meta / TikTok / Pinterest / Google |
| virtual_model_tryout | Product worn or used by an AI model |
| conceptual_product | Levitating, splash, frozen motion, surreal, CGI, sculptural |
| restyle | Change an existing image's mood, season or aesthetic, same subject |

Pick by intent; the more specific mode wins. "Pinterest pin of my product on a kitchen
counter" → moodboard_pin. "Hero banner showing the product in use" → hero_banner.
"Closeup of someone applying my serum" → closeup_product_with_person.

For carousels and ad packs, make every slide in the same model, resolution and preset so the
visual system holds; vary angle, lighting and copy, not the look.

## Interview (≤ 4 questions, labeled options, skip the obvious)

**Has a product photo, "make me images":** How many? [1 / 3 / 5] · Style? [Clean studio /
Lifestyle / Conceptual / With a model] · Where will it run? [Shopify / Instagram / Pinterest /
Paid ads / Website hero] · Brand colors to match?

**Named a use case ("make ads", "hero banner"):** only the gaps: how many, the offer or
hook, what to emphasize.

**No photo:** ask for one (much higher fidelity); otherwise category, packaging, colors,
distinctive features, then style and placement.

**Restyle:** aesthetic [Clean girl / Cottagecore / Quiet luxury / Dark academia / Y2K] ·
season [Christmas / Valentine's / Black Friday / none] · what must stay the same.

**Try-on:** model archetype (suggest 2–3 for their audience) · environment [Studio / Outdoor /
Street / Editorial / Home] · framing [Full body / Three-quarter / Waist up / Close-up].

## Defaults

`resolution: 2k`, `quality: high`. Draft on Flare, then rerun the winner on Sunburst.
Estimate one image, then quote count × that price in the one-line confirmation.
