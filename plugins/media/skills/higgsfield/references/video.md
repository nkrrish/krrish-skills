# Video: UGC and premium

## Which model

- **Kling 3.0**: UGC, talking to camera, handheld, product demo, one scene. `std` for
  drafts, `pro` for finals, `turbo` when speed matters, `4k` only when asked. Native audio is
  on by default and adds about 50% to the price: set `sound: "off"` when the user will add
  their own voiceover or music. The cheaper of the two per second.
- **Seedance 2.0**: premium, cinematic, heavy motion, 4K, or reference-to-video with image,
  video or audio references. Costs more per second than Kling; check `hf.sh prices`.

## The UGC pipeline (best realism per dollar)

1. **Still first.** Make the opening frame with Soul 2 (creator) or Marketing Studio (product),
   at 9:16. Iterate here: stills cost cents, video costs dimes.
2. **Animate.** Kling 3.0 `std/image-to-video` with `image_url` = the still, `duration: 5`,
   `sound: "on"`. The prompt describes motion and speech only (see `prompting.md`):
   `handheld phone footage, slight natural shake. She holds the jar up to the lens and says: "okay, this is the one I keep rebuying."`
3. **Longer ads:** `multi_shots: true` with 2–6 `multi_prompt` shots (hook → demo → reaction
   → CTA), each 1–15s; billing is the sum of the shot durations. Keep a top-level prompt too.
4. **Finals:** rerun the chosen take on Kling `pro`, or Seedance 2.0 image-to-video at 1080p
   if motion needs to be richer.

Use `last_image_url` / `end_image_url` to land on a specific end frame (a product packshot
or end card).

## Interview (≤ 4, skip the obvious)

Format? [9:16 Reels/TikTok / 1:1 feed / 16:9 web] · Length? [5s / 10s / 15s] · Who's on
camera? [Existing still / New creator (Soul 2) / Product only] · Spoken line or silent?

## Cost line

Run `hf.sh estimate` on the exact request (duration, tier, resolution, sound and multi-shot
all change the price) and quote it before submitting: "Kling 3.0 std, 5s, 9:16, sound on —
$X on your account". Start at 5s.

Seedance is token-metered: `estimate` returns its pricing rule instead of a number. Quote
the rule's arithmetic (seconds × width × height × 24 / 1024 tokens at the listed rate) as an
upper bound "before your discount", and say the final charge is reconciled on completion.

Live schemas: `kling-3/standard-image-to-video`, `kling-3/standard-text-to-video`,
`seedance-2/image-to-video`, `seedance-2/text-to-video`, `seedance-2/reference-to-video`
under `https://docs.higgsfield.ai/docs/models/<page>.md`.
