# Naming: styles, rules and scores

## Defaults when the user does not say

- Length: 5 to 8 letters, shorter is better. Eight is the ceiling for coined names.
- Domains: check only the TLDs the user picked. If they do not say, check `.com` and ask
  whether `.ai`, `.app`, `.io` or others matter. A liked prefix or suffix plus the name on
  their must-have TLD also counts.
- Lowercase wordmark is fine; check whether the user wants the name always lowercase.

## Styles (generate several at once)

| Style | Shape | Examples | Notes |
|---|---|---|---|
| coined | CV(C)CV(C), 5 to 6 letters | vamlin, glembi, kralmo | The core. Two clean beats, soft letters. |
| formula | sharp start + vowel + firm pair + soft ending | Zernio, Cirnio, Kalnio, Gurnix, Zalvum | Endings: -io, -ix, -um, -a, -o, -ena, -ora, -ivo, -ani. -io, -ix and -um still have free .coms with almost any first letter; -ora, -ena, -ivo, -ani are nearly full. |
| letter | root + one capital letter | BenQ, ZeroM, GlimoQ, RecapQ | Real-word roots are almost all taken; coined roots work. Show it styled (GlimoQ) with the plain domain under it. |
| pair | root + two letters | TikoHQ, CueUX, Junoly | HQ and -ly are friendly and often free. The extra letters can live only in the domain (brand "Tiko" on tikohq.com). |
| affix | prefix or suffix + everyday word | saytuesday, withgelato, meethin | Uses the user's liked affixes. |
| word | everyday word, plain | Granola, Monday | Almost never free on .com; check anyway for the user's favourites. |

### Prefixes and suffixes

Popular and still pleasant: say, meet, with, its, the, hello, try, use, go, get, join, hey.
Suffixes: hq, labs, app, ly, io, hub, kit. Ask which the user likes and dislikes before using
any; people often hate specific ones (for example ask, talk, yo, ok, hi). "try" and "use" are
overused.

## Rules

- Pronounceable on first read in English. No three consonants in a row except a starting
  cluster (br, cl, fl, gl, pl, sk, sn, sp, st, tr, kr).
- No doubled letters in coined names unless the user likes them.
- No lookalikes or parodies of brands the user cited (Lorvel for Vercel, Moblox for Roblox).
- Avoid saturated category words (for a notes app: note, whispr, memo as the whole name).
- Screen for bad meanings: check rude substrings (the generator filters common ones), slang,
  and meanings in Spanish, French, German, Italian, Portuguese, Hindi and Mandarin pinyin.
- Avoid sounding like a medicine (-il, -ine, -ex endings plus a Latin-ish root) unless the
  user has a pronunciation that breaks it (Trepil said like "triple").
- Avoid one-letter-off neighbours of live products in the same category (Zirnio vs Zernio).

## What earns a sound or look score

The script's scores are a first pass. Override the top of the list by hand.

**Sound, 1 to 5**
- 5: two clean beats, one obvious way to say it, soft letters (l, m, n, r, v), ends in a vowel
  or -ly. Vamlin, Kalnio, Temoly.
- 4: pleasant, one sharper letter or cluster. Glumik, Trunmo.
- 3: readable but plain or a little stiff.
- 2: odd clusters, two ways to say it, or a near-miss to an unfortunate word.
- 1: hard to say or reads badly.

**Look, 1 to 5**
- Up: even mix of consonants and vowels, round letters (o, a, e), 5 letters, a clean capital
  ending (HQ, Q) when styled.
- Down: three consonants in a row, doubled letters, clusters of j, w, q, x, vowel plus -ix or
  -ox.

**Syllables**: count vowel groups; -io counts as two; a capital letter counts as one (Q is
"kyoo"), HQ counts as two.

## Batching and honesty

- Check in batches of 50 or so. Keep every result on disk so nothing is lost.
- Report: how many tried, how many free, by style. Then generate more in the styles that hit.
- Never report a name from memory as free.
