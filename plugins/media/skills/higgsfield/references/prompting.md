# Prompting

Adapted from higgsfield-ai/skills `prompt-engineering.md` (MIT, © 2026 Higgsfield AI), plus
notes for realistic creator content.

## Basics

Higgsfield models reward concrete, sensory prompts. Keep them under ~200 tokens; very long
prompts distort.

- **Subject + setting + style**: "a woman in her 20s filming a skincare routine at her bathroom mirror, morning light, iPhone photo"
- **Camera**: lens (24mm phone wide, 35mm, 85mm), angle (eye level, low, overhead), distance (close-up, waist up)
- **Lighting**: window light, golden hour, ring light, overhead fluorescent, rim light
- **Style / medium**: candid phone photo, editorial, studio product shot, 3D render

## Making people look real (creator / UGC)

- Ask for imperfection: "candid", "shot on iPhone", "natural skin texture", "slightly
  messy background", "handheld framing", "no retouching look".
- Real places beat studios: a lived-in kitchen, a car seat, a gym mirror, a café window.
- Give the person an action, not a pose: "mid-laugh while holding up the bottle", "talking to camera".
- Specify age range, style and setting; avoid real public figures (moderation rejects them).

## Image-to-image and edits

With `image_urls`, describe what changes, not the whole image again.

- Bad: "a man with brown hair in a leather jacket holding coffee, made into anime"
- Good: "transform into anime style, vibrant colors, soft cel shading"

## Image-to-video

The start image anchors the first frame; the prompt describes motion only.

- Camera verbs: slow push in, handheld drift, dolly left, whip pan, static tripod.
- Subject motion: "she lifts the jar toward the lens and smiles", "steam rises from the cup".
- For UGC: "handheld phone footage, slight natural shake, talking directly to camera".
- Put speech in quotes when you want it spoken (Kling and Seedance can make native audio):
  `she says: "okay this actually changed my morning routine"`.

## Negative phrasing

Most endpoints have no `negative_prompt`. Say what you want instead:
"tack sharp" not "no blur"; "empty street" not "no people".

## Aspect ratios

`9:16` Reels / TikTok / Stories · `4:5` or `3:4` feed · `1:1` square · `16:9` web hero, YouTube ·
`2:3` Pinterest · `21:9` cinematic banner. Check each model's allowed values.

## Safety

`nsfw` or failed moderation: no real public figures, sexual content, trademarked characters
or brand logos you don't own. Rephrase rather than resubmitting.
