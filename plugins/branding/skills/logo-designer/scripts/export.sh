#!/usr/bin/env bash
set -euo pipefail

# Usage: export.sh <input.svg> <output-dir> [icon.svg]
#
# Renders SVGs to PNG at standard logo sizes using whichever converter is
# available. Aspect ratio is preserved: sizes are target WIDTHS, so a square
# icon exports square and a 2:1 wordmark exports 2:1.

INPUT_SVG="${1:?Usage: export.sh <input.svg> <output-dir> [icon.svg]}"
OUTPUT_DIR="${2:?Usage: export.sh <input.svg> <output-dir> [icon.svg]}"
ICON_SVG="${3:-}"
SIZES=(16 32 48 180 192 512 1024 2048)

[[ -f "$INPUT_SVG" ]] || { echo "ERROR: no such file: $INPUT_SVG" >&2; exit 1; }
mkdir -p "$OUTPUT_DIR"

abspath() { printf '%s/%s\n' "$(cd "$(dirname "$1")" && pwd -P)" "$(basename "$1")"; }

copy_unless_same() {
  [[ "$(abspath "$1")" != "$(abspath "$2")" ]] && cp "$1" "$2" || true
}

copy_unless_same "$INPUT_SVG" "$OUTPUT_DIR/logo.svg"
[[ -n "$ICON_SVG" ]] && copy_unless_same "$ICON_SVG" "$OUTPUT_DIR/icon.svg"

# --- converter detection, best first -----------------------------------------
TOOL=""
if command -v resvg &>/dev/null; then
  TOOL="resvg"
elif command -v rsvg-convert &>/dev/null; then
  TOOL="rsvg-convert"
elif command -v inkscape &>/dev/null; then
  TOOL="inkscape"
elif command -v node &>/dev/null && node -e "require('sharp')" &>/dev/null; then
  TOOL="sharp"
elif command -v magick &>/dev/null; then
  TOOL="magick"
elif command -v convert &>/dev/null; then
  TOOL="convert"
elif command -v python3 &>/dev/null && python3 -c "import cairosvg" &>/dev/null; then
  TOOL="cairosvg"
else
  cat >&2 <<'MSG'
ERROR: No SVG-to-PNG converter found.

Install any one of these (all verified to exist):
  npm  install -g @resvg/resvg-js-cli    # fastest, best SVG fidelity
  brew install librsvg                   # provides rsvg-convert
  brew install imagemagick               # provides magick
  brew install inkscape
  pip  install cairosvg
MSG
  exit 1
fi

echo "Using: $TOOL"
BLANK_OUTPUTS=0

if [[ "$TOOL" == "magick" || "$TOOL" == "convert" ]] \
   && ! magick -list configure 2>/dev/null | grep -q rsvg; then
  cat >&2 <<'WARN'
WARNING: ImageMagick is built without the rsvg delegate, so it falls back to its
internal SVG renderer. That renderer silently drops gradients, masks, clip-paths
and text -- producing blank or wrong PNGs with a success exit code.

Install a real SVG renderer before trusting these exports:
  brew install librsvg                 # provides rsvg-convert
  npm  install -g @resvg/resvg-js-cli  # or this

WARN
fi
echo ""

# Intrinsic pixel width the tool sees, used to scale rasterization density so
# large exports are rendered rather than upscaled.
intrinsic_width() {
  local src="$1" w=""
  if command -v magick &>/dev/null; then
    w="$(magick identify -format "%w" "$src" 2>/dev/null | head -1 || true)"
  fi
  [[ "$w" =~ ^[0-9]+$ ]] && [[ "$w" -gt 0 ]] && echo "$w" || echo 100
}

render() {
  local src="$1" base="$2" size="$3"
  local out="$OUTPUT_DIR/${base}-${size}.png"

  case "$TOOL" in
    resvg)        resvg "$src" "$out" --width "$size" >/dev/null ;;
    rsvg-convert) rsvg-convert -w "$size" -o "$out" "$src" ;;
    inkscape)     inkscape "$src" --export-type=png --export-filename="$out" \
                    --export-width="$size" >/dev/null 2>&1 ;;
    sharp)
      node - "$src" "$out" "$size" <<'NODE'
const sharp = require('sharp');
const [src, out, sizeText] = process.argv.slice(2);
const size = Number(sizeText);
(async () => {
  const base = await sharp(src).metadata();
  // Re-rasterize at a density that yields at least the target width.
  const density = Math.min(3000, Math.max(72, Math.ceil(72 * (size / (base.width || 100)))));
  await sharp(src, { density })
    .resize({ width: size, fit: 'inside', background: { r: 0, g: 0, b: 0, alpha: 0 } })
    .png()
    .toFile(out);
})().catch(e => { console.error(e); process.exit(1); });
NODE
      ;;
    magick|convert)
      local iw density
      iw="$(intrinsic_width "$src")"
      density="$(awk -v s="$size" -v w="$iw" 'BEGIN{d=96*s/w; if(d<96)d=96; if(d>6000)d=6000; printf "%d", d}')"
      "$TOOL" -background none -density "$density" "$src" -resize "${size}x" "$out"
      ;;
    cairosvg)
      python3 -c "import cairosvg,sys; cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=int(sys.argv[3]))" \
        "$src" "$out" "$size"
      ;;
  esac

  local dims="" sd=""
  if command -v magick &>/dev/null; then
    dims=" ($(magick identify -format '%wx%h' "$out" 2>/dev/null))"
    # A uniform image means the renderer silently dropped the artwork.
    # ImageMagick's internal MSVG renderer does this with gradients, masks
    # and clip-paths: exit 0, blank PNG.
    sd="$(magick identify -format '%[fx:standard_deviation]' "$out" 2>/dev/null || echo 1)"
    if [[ "$sd" == "0" ]]; then
      BLANK_OUTPUTS=$((BLANK_OUTPUTS + 1))
      echo "  ${base}-${size}.png${dims}  <-- BLANK"
      return
    fi
  fi
  echo "  ${base}-${size}.png${dims}"
}

for SIZE in "${SIZES[@]}"; do render "$INPUT_SVG" "logo" "$SIZE"; done

if [[ -n "$ICON_SVG" ]]; then
  echo ""
  for SIZE in "${SIZES[@]}"; do render "$ICON_SVG" "icon" "$SIZE"; done
fi

echo ""
if [[ "${BLANK_OUTPUTS:-0}" -gt 0 ]]; then
  echo "FAILED: $BLANK_OUTPUTS output(s) came out blank -- the SVG uses features" >&2
  echo "this renderer does not support. Install librsvg or @resvg/resvg-js-cli" >&2
  echo "and re-run; do not ship these files." >&2
  exit 2
fi
echo "Done. Files in: $OUTPUT_DIR"
