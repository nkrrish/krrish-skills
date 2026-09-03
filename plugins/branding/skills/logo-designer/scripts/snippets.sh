#!/usr/bin/env bash
set -euo pipefail

# Usage: snippets.sh <logo.svg> <output-dir> [ComponentName]
# Emits USAGE.md: every paste-ready form of the mark someone actually needs.

SVG="${1:?Usage: snippets.sh <logo.svg> <output-dir> [ComponentName]}"
OUT="${2:?Usage: snippets.sh <logo.svg> <output-dir> [ComponentName]}"
NAME="${3:-Logo}"
[[ -f "$SVG" ]] || { echo "ERROR: no such file: $SVG" >&2; exit 1; }
mkdir -p "$OUT"

# Minify: drop XML decl, doctype, comments, collapse whitespace between tags.
MIN="$(sed -e 's/<?xml[^>]*?>//g' -e 's/<!DOCTYPE[^>]*>//g' "$SVG" \
      | perl -0pe 's/<!--.*?-->//gs; s/>\s+</></gs; s/^\s+|\s+$//gs')"

# data: URI (unquoted-safe percent-encoding, keeps it readable in CSS)
DATA="data:image/svg+xml,$(printf '%s' "$MIN" \
  | perl -pe 's/%/%25/g; s/"/%22/g; s/#/%23/g; s/</%3C/g; s/>/%3E/g; s/\n//g')"

# JSX: React needs camelCase attrs and {} for style
JSX="$(printf '%s' "$MIN" | perl -pe '
  s/\bstroke-width=/strokeWidth=/g; s/\bstroke-linecap=/strokeLinecap=/g;
  s/\bstroke-linejoin=/strokeLinejoin=/g; s/\bfill-rule=/fillRule=/g;
  s/\bclip-path=/clipPath=/g; s/\bclip-rule=/clipRule=/g;
  s/\bstroke-dasharray=/strokeDasharray=/g; s/\bxmlns:xlink="[^"]*"//g;
  s/<svg /<svg {...props} /;')"

{
cat <<MD
# Using this mark

Every form below is paste-ready. The SVG is the source of truth — the PNGs are for
platforms that cannot take vectors.

## Inline SVG (HTML)

Best default. Scales freely, inherits nothing, no request.

\`\`\`html
$MIN
\`\`\`

## React / JSX component

\`\`\`jsx
export function $NAME(props) {
  return (
    $JSX
  );
}
\`\`\`

Use it at any size: \`<$NAME width={32} />\` — the viewBox does the scaling.

## CSS background (data URI)

No extra network request.

\`\`\`css
.logo {
  width: 32px;
  height: 32px;
  background: url("$DATA") center / contain no-repeat;
}
\`\`\`

## Monochrome / menu-bar template

Renders the mark in whatever colour the surrounding text is — for macOS menu bars,
single-colour print, and inverted contexts.

\`\`\`css
.logo-mono {
  width: 32px;
  height: 32px;
  background-color: currentColor;
  -webkit-mask: url("$DATA") center / contain no-repeat;
          mask: url("$DATA") center / contain no-repeat;
}
\`\`\`

If the mark disappears or turns into a solid block here, it has a background plate baked
in and must be rebuilt — see the SVG conventions in SKILL.md.

## Favicon (drop into \`<head>\`)

\`\`\`html
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
\`\`\`

Map the exported files: \`logo.svg\` → \`favicon.svg\`, \`logo-32.png\` → \`favicon-32.png\`,
\`logo-180.png\` → \`apple-touch-icon.png\`.

## Web manifest

\`\`\`json
{
  "icons": [
    { "src": "/logo-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/logo-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/logo-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
\`\`\`

## Swift / macOS menu bar

\`\`\`swift
// Template rendering makes macOS tint the mark for light/dark automatically.
let image = NSImage(contentsOfFile: "logo.svg")
image?.isTemplate = true
statusItem.button?.image = image
\`\`\`
MD
} > "$OUT/USAGE.md"

echo "Wrote $OUT/USAGE.md ($(wc -l < "$OUT/USAGE.md" | tr -d ' ') lines)"
