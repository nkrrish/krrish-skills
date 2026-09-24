---
name: higgsfield
description: Generate images and videos with the Higgsfield Open API on the user's own API key — realistic creator and UGC photos (Soul 2), product photoshoots and ad creatives (Marketing Studio GPT Image 2.5 with presets), recurring characters (Soul ID), UGC video (Kling 3.0) and premium video (Seedance 2.0) — quoting the exact price on their account before every spend. Use when the user asks to generate, make, render or animate an image, photo, product shot, ad, UGC clip or video with Higgsfield, asks what Higgsfield costs them, or wants to connect a Higgsfield API key.
---

# Higgsfield (Open API, pay-per-use)

Unofficial; not affiliated with Higgsfield AI. Every generation spends real money from the
user's prepaid cloud.higgsfield.ai balance. The plugin's guard hook makes Claude Code ask
before any submit, upload or cancel, in every permission mode. Never route around it: no
inline curl to the API, no new scripts that call it, never read or print the key.

## Tool

`scripts/hf.sh` in this skill's base directory. Call it by its absolute path.

| Command | Cost | Guard |
|---|---|---|
| `hf.sh setup` | free | runs; opens a hidden-input dialog, the user types the key there |
| `hf.sh status` | free | runs; says where the key is stored and verifies it, never prints it |
| `hf.sh prices` | free | runs; per-account prices for the core models |
| `hf.sh estimate <endpoint> @<file.json>` | free | runs; exact cost of that request |
| `hf.sh submit <endpoint> @<file.json>` | spends credits | asks |
| `hf.sh upload <local-file>` → public URL | free, sends the file to Higgsfield | asks |
| `hf.sh wait <request_id> <out_dir>` → saved paths | free | runs |
| `hf.sh get <endpoint>` (presets, Soul ID status) | free | runs |
| `hf.sh cancel <request_id>` (queued only, refunded) | — | asks |

Write each request body to a JSON file (e.g. `./higgsfield-output/req-<n>.json`) and pass
`@file` to both `estimate` and `submit`, so the price quoted is for the exact request sent.
Model inputs take public URLs, never local paths: `upload` local files first.

## First use

Run `hf.sh status`. If no key is connected, tell the user they need a key ID and secret
from cloud.higgsfield.ai (API keys), then run `hf.sh setup`: a dialog opens (macOS) for
them to paste into. Never ask them to paste the key into chat. On Linux without a GUI,
setup needs a terminal: ask them to run `! <abs path>/hf.sh setup` themselves.
After setup, show `hf.sh prices` so they see what things cost on their account.

## Pick the route

| The user wants… | Read | Default model |
|---|---|---|
| A realistic person, creator, influencer, lifestyle or UGC still | `references/models.md` | Soul 2 |
| The same person across many images and videos | `references/characters.md` | Soul ID → Soul 2 |
| Product photo, lifestyle scene, hero banner, Pinterest pin, ad pack, try-on, restyle | `references/product-photoshoot.md` | Marketing Studio Sunburst (+ preset) |
| A graphic, banner or anything with text in the image | `references/models.md` | Marketing Studio Sunburst |
| UGC, talking, selfie or handheld video, product demo | `references/video.md` | Kling 3.0 image-to-video |
| Premium, cinematic, motion-heavy or 4K video | `references/video.md` | Seedance 2.0 |

Read `references/prompting.md` before writing a prompt, and the chosen model's live schema
before building the request (links in `references/models.md`) — fields change.

## Every job, in order

1. **Interview only the gaps**: at most 4 short questions with labeled options, skipping
   anything obvious from context.
2. **Price it**: write the body file, run `hf.sh estimate`, and confirm in one line:
   model, prompt, count / duration / resolution, and the estimated cost from the API.
   Never quote prices from memory; they differ per account and change. Marketing Studio and
   Seedance are token-metered: `estimate` returns a pricing rule, not a number — quote it as
   "metered, billed on actual usage" with the rule's rough figure, and point to the user's
   console for claimed discounts.
3. **Drafts first**: 1 image on Flare or Soul 2, video at 5s on the standard tier, unless
   the user asked for more.
4. **Submit once.** Never loop, batch or retry a submit on your own. Failed and `nsfw`
   requests are refunded, but a retry is a new charge: report and let the user decide.
5. **Wait and save** to the folder the user named, else `./higgsfield-output/`. Output
   URLs expire after about 7 days, so always download.
6. **Deliver**: show images with Read, give file paths and what it cost, and one suggestion
   for the next iteration. No JSON or request IDs in chat.

Terminal statuses: `completed`, `failed` (refunded), `nsfw` (moderation, refunded — rephrase,
don't resubmit the same prompt), `canceled` (refunded).

Portions adapted from higgsfield-ai/skills (MIT, © 2026 Higgsfield AI); see NOTICE.
