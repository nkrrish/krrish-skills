# Consistent characters (Soul ID)

Adapted from higgsfield-ai/skills `higgsfield-soul-id` (MIT, © 2026 Higgsfield AI), for the
Open API.

Soul ID trains a reusable character from photos so the same person appears across many
Soul 2 images, for example a recurring "creator" for a brand's content. Use it when the
user wants the same face again, not for one-off images.

## Photos

Ask for 10–30 photos of one person: clear, well-lit face, varied angles (front, three-quarter,
profile) and expressions, a few half and full body, no sunglasses, filters, heavy makeup or
other people. More variety gives a more faithful character. Only train on a real person
with their consent; a generated character from Soul 2 stills works too.

## Train

1. `hf.sh upload` each photo (asks) → collect the `public_url`s.
2. Write the body to a file, try `hf.sh estimate /v1/custom-references @body.json` (if the
   estimate endpoint doesn't cover training, say the price is on the user's console), confirm
   with the user, then `hf.sh submit /v1/custom-references @body.json` with
   `{"name":"<name>","model_version":"v2","input_images":[{"type":"image_url","image_url":"<url>"}, …]}`.
   Use `model_version: v2` to match Soul 2.
3. Poll for free: `hf.sh get /v1/custom-references/<id>` until `completed`
   (`not_ready`, `queued`, `in_progress`, `failed` otherwise). Training takes a while;
   tell the user and check back instead of looping tightly.

Record the id and name somewhere the user can find them (their project notes, or tell them).
References belong to the account that trained them.

## Use

Soul 2 with `"custom_reference_id": "<id>", "custom_reference_strength": 0.8` (must be
> 0 and ≤ 1; lower it if the face looks stiff, raise it if likeness drifts). Then animate the
stills with `video.md` image-to-video to keep the same person in video.

Live schema: `curl -s https://docs.higgsfield.ai/docs/models/soul-id/create-character.md`
