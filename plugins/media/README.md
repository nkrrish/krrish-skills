# media — Higgsfield API skill for Claude Code

Make realistic creator photos, product shoots and UGC videos from a Claude Code chat,
using **your own** key for the [Open Higgsfield API](https://docs.higgsfield.ai) — Soul 2,
Marketing Studio, Kling 3.0 and Seedance 2.0.

> **Unofficial.** Not affiliated with, endorsed by or sponsored by Higgsfield AI.
> "Higgsfield" is their trademark. You pay Higgsfield directly from your own prepaid balance.

```text
you     make a candid photo of a 25-year-old creator filming a skincare reel at her
        bathroom mirror, 9:16

claude  Soul 2 · 1 image · 9:16 · 720p — $0.003 on your account. Go ahead?   (example prices)
        ┌──────────────────────────────────────────────────────────────┐
        │ Higgsfield guard: this command can spend Higgsfield credits. │
        │ Allow?  Yes / No                                             │
        └──────────────────────────────────────────────────────────────┘
        Saved higgsfield-output/hf-3f9a1c02-1.png  ·  spent $0.003
        Next: animate it with Kling 3.0 (5s, about $0.21) — want a talking version?
```

## Contents

- [Install](#install)
- [Connect your key](#connect-your-key)
- [What you can make](#what-you-can-make)
- [What it costs](#what-it-costs)
- [How your money and key are protected](#how-your-money-and-key-are-protected)
- [Commands](#commands)
- [Troubleshooting](#troubleshooting)
- [Licence and credits](#licence-and-credits)

## Install

```bash
/plugin marketplace add nkrrish/krrish-skills
/plugin install media@krrish-skills
```

Restart Claude Code. Requires `python3` and `curl` (both come with macOS).

## Connect your key

1. Create an API key at **[cloud.higgsfield.ai](https://cloud.higgsfield.ai)** → API keys.
   You get two values: a **key ID** and a **key secret**. Add credit to the account.
2. In Claude Code, say **"connect my Higgsfield key"**.
3. A small dialog opens. Paste the key ID, then the secret. The input is hidden.

That's it. The key goes straight into your **macOS Keychain** (service `higgsfield-api`) —
it never passes through the chat and never lands in a file in your project. Setup then
makes a free test call and shows what the main models cost on your account.

<details>
<summary>Linux, or no dialog?</summary>

Run setup in a terminal so it can prompt without echoing:

```bash
"$(ls -d ~/.claude/plugins/cache/krrish-skills/media/*/ | tail -1)skills/higgsfield/scripts/hf.sh" setup
```

Without a Keychain, the key is saved to `~/.config/higgsfield-api/credentials`,
readable only by you (mode 600).

Already use `HF_API_KEY_ID` / `HF_API_KEY_SECRET` environment variables (for example in CI)?
They take priority over the Keychain, so nothing else is needed.
</details>

## What you can make

Just ask in plain words. The skill picks the model, asks at most four quick questions,
quotes the price and waits for your OK.

| Ask for… | Model it uses | Why |
|---|---|---|
| A realistic creator, influencer or lifestyle photo | **Soul 2** | Built for people who look real, cheapest per image |
| Product shots: studio, lifestyle, hero banner, Pinterest pin, ad pack, try-on, restyle | **Marketing Studio 2.5** Flare (drafts) → Sunburst (finals) | Higgsfield's own presets write the photography prompt from your product photo |
| Graphics or anything with text in the image | **Marketing Studio Sunburst** | Best at on-image text and precise edits |
| The same face across many posts | **Soul ID** → Soul 2 | Train a character once, reuse it everywhere |
| UGC, talking-to-camera, handheld or product-demo video | **Kling 3.0** | Native audio, multi-shot ads, good value per second |
| Premium, cinematic or 4K video | **Seedance 2.0** | Richer motion and higher resolution |

**The UGC trick it follows:** make the opening frame as a cheap still first, get it right,
then animate it. Iterating on stills costs cents; iterating on video doesn't.

Files are saved to the folder you name, or `./higgsfield-output/`. Higgsfield deletes outputs
after about 7 days, so the skill always downloads them.

## What it costs

Prices depend on your account — plans and claimed discounts differ — so this plugin never
quotes a price from memory. Ask **"what does Higgsfield cost me?"** or run:

```bash
hf.sh prices
```

Before every job, the skill prices the **exact** request with Higgsfield's free estimate
endpoint and tells you the number. Two model families are **metered** — Marketing Studio
(per token) and Seedance (per video token) — so Higgsfield returns their pricing rule rather
than a fixed price; the skill shows you that rule and the charge is settled on completion.

Tip: Kling's built-in audio adds about 50% to the price. If you'll add your own voiceover
or music, ask for sound off. Failed, moderated and cancelled requests are refunded by
Higgsfield. You can only ever spend the credit already on your account.

## How your money and key are protected

The plugin installs a **PreToolUse hook**: a check that runs before every command Claude
tries. It can't be skipped by the model, and it works in every permission mode — including
auto mode and "allow all" setups.

| Claude tries to… | What happens |
|---|---|
| Start a generation or training job | **You're asked** |
| Upload one of your files to Higgsfield | **You're asked** |
| Call the Higgsfield API any other way (curl, a script, Python) | **You're asked** |
| Write code that calls the API or uses the key | **You're asked** |
| Read, print or dump the key (Keychain, env, credentials file, shell profile) | **You're asked** |
| Check a price, poll a running job, download results, list presets | Runs — it's free |

Free commands are matched strictly: a paid call chained after a free one
(`hf.sh wait … ; hf.sh submit …`) is still caught. The repository's test suite checks this.

**Limit:** the guard protects you inside Claude Code. Like any key stored on your computer,
programs you run yourself outside Claude Code could read it — the same as an SSH key or a
`.env` file. Keep an eye on usage at [console.higgsfield.ai](https://console.higgsfield.ai).

## Commands

The skill runs these for you; they're listed so you know what each prompt means.

| Command | Cost | Asks you? |
|---|---|---|
| `hf.sh setup` | free | — |
| `hf.sh status` | free | — |
| `hf.sh prices` | free | — |
| `hf.sh estimate <endpoint> @request.json` | free | — |
| `hf.sh submit <endpoint> @request.json` | **spends credits** | yes |
| `hf.sh upload <file>` | free (sends your file) | yes |
| `hf.sh wait <request_id> [folder]` | free | — |
| `hf.sh get <endpoint>` | free | — |
| `hf.sh cancel <request_id>` | refunded | yes |

## Troubleshooting

| Problem | Fix |
|---|---|
| "No Higgsfield API key connected" | Say "connect my Higgsfield key", or run `hf.sh setup`. |
| "Higgsfield rejected it" after setup | The ID and secret are two different values — check both at cloud.higgsfield.ai and run setup again. |
| A job ended as `nsfw` | Moderation rejected it (refunded). Avoid real public figures, trademarks and sexual content; rephrase. |
| A job ended as `failed` | Refunded. The skill reports the error and doesn't retry on its own — ask it to try again. |
| No prompt appeared before a generation | Restart Claude Code after installing; hooks load at start-up. |
| Remove the key | `security delete-generic-password -s higgsfield-api -a key-id` and `… -a key-secret` (macOS), or delete `~/.config/higgsfield-api/credentials`. |

## Licence and credits

GPL-3.0-or-later, like the rest of [krrish-skills](../../README.md). Images and videos you
make are yours; the licence covers the skill itself.

The product-photoshoot modes and interview, the prompting guide and the model-picking rules
are adapted from [higgsfield-ai/skills](https://github.com/higgsfield-ai/skills)
(MIT, © 2026 Higgsfield AI), rewritten for the Open API. Their notice is in
[NOTICE](../../NOTICE). The helper script, guard, video pipeline and Soul ID guide are
original.
