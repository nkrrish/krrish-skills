# Models

The core set this skill routes to. Prices are per account (plans and discounts differ):
get them with `hf.sh prices` or `hf.sh estimate`, never from memory.

| Model | Endpoint | Unit | Best at |
|---|---|---|---|
| SOUL V2 | `/higgsfield-ai/soul/v2/standard` | per image | Realistic people: creator, UGC, fashion, editorial, lifestyle |
| Marketing Studio 2.5 Flare | `/marketing-studio/image/flare` | per image | Fast drafts and variants of product and ad images |
| Marketing Studio 2.5 Sunburst | `/marketing-studio/image/sunburst` | per image | Finals, text in the image, graphics, edits that keep the rest intact |
| Kling 3.0 | `/kling-video/v3.0/{std,pro,4k}/{text,image}-to-video`, `/kling-video/v3.0-turbo/{text,image}-to-video` | per second | UGC, talking, handheld, single-scene clips, native audio, multi-shot |
| Seedance 2.0 | `/bytedance/seedance-2.0/{text,image,reference}-to-video` | per second | Premium motion, cinematic, up to 4K, image/video/audio references |

Marketing Studio 2.0 Alpha (`/marketing-studio/image`) is the older version; prefer 2.5.
If the user has claimed discounts on specific models in their console, prefer those —
`hf.sh prices` shows the effect.

Other models (Seedance 2.5, Wan, MiniMax, Recraft, Ideogram, Grok, …): see
`https://docs.higgsfield.ai/docs/models.md`, estimate, and confirm before using.

## Live schemas (read before building a request)

`curl -s https://docs.higgsfield.ai/docs/models/<page>.md`

- `soul-2/generate`
- `marketing-studio-image/flare`, `marketing-studio-image/sunburst`
- `kling-3/standard-text-to-video`, `kling-3/standard-image-to-video`, `kling-3/pro-…`, `kling-3/4k-…`, `kling-3/turbo-…`
- `seedance-2/text-to-video`, `seedance-2/image-to-video`, `seedance-2/reference-to-video`
- `soul-id/create-character`

## Key fields (as of September 2026)

**Soul 2**: `prompt` (required), `aspect_ratio` 9:16 | 16:9 | 4:3 | 3:4 | 1:1 | 2:3 | 3:2
(default 1:1), `resolution` 720p | 1080p (default 720p), `batch_size` 1 or 4, `seed`,
`style_id`, `enhance_prompt`, `custom_reference_id` + `custom_reference_strength` (0 < s ≤ 1)
for a Soul ID character.

**Marketing Studio Flare / Sunburst**: `prompt` (required, ≤ 5000 chars), `quality`
low | medium | high | xhigh | max (default high), `resolution` 1k | 2k | 4k (default 2k),
`aspect_ratio` auto | 1:1 | 3:2 | 2:3 | 4:3 | 3:4 | 16:9 | 9:16 | 21:9, `image_urls`
(≤ 16 for edits), `enhance_prompt` + `preset_id` (see product-photoshoot.md), `moderation`.
Quality and resolution change the price: estimate before going above `high` + `2k`.

**Kling 3.0**: `prompt` (≤ 2500 chars), `duration` 3–15s (default 5), `sound` on | off
(default on), `aspect_ratio` 16:9 | 9:16 | 1:1 (text-to-video), `image_url` (+ optional
`last_image_url`) for image-to-video, `multi_shots` + `multi_prompt` (1–6 shots, each
≤ 512 chars and 1–15s; billed on the sum), `cfg_scale` 0–1.

**Seedance 2.0**: `prompt`, `duration` 4–15s (default 5), `resolution` 480p | 720p |
1080p | 4k (default 720p), `aspect_ratio` (text-to-video) 16:9 | 4:3 | 1:1 | 3:4 | 9:16 | 21:9,
`generate_audio` (default true), `image_url` + optional `end_image_url` for image-to-video.

## Picking rules

Adapted from Higgsfield's production defaults (higgsfield-ai/skills, MIT).

- People who should look real → Soul 2. Product, typography, UI, banner → Marketing Studio.
- Drafting → Flare; a final, or an edit that must preserve untouched regions → Sunburst.
- A person or product in one scene, UGC feel, lower cost → Kling 3.0 (std; pro for finals).
- Heavy motion, a multi-shot story, identity held across shots, 4K → Seedance 2.0.
- Best video realism: make the first frame as a still, then animate it with image-to-video.
  Iterating on stills costs cents; iterating on video costs much more.
- Don't invent model names or fields; if unsure, read the live schema.
