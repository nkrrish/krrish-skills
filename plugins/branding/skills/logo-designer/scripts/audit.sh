#!/usr/bin/env bash
set -uo pipefail
# audit.sh <dir|file.svg>
#
# The pre-flight checklist as measurements. Needs only rsvg-convert (or resvg /
# ImageMagick) plus ImageMagick — no new dependencies.
#
#   ink    fraction of canvas inked.  >0.85 = a background plate, not a mark.
#   tpl    std-dev of the single-colour flatten. 0 = blank / total collapse.
#   rgn    distinct regions at 256px -> at 16px. A drop means interior counters
#          close up at favicon size: the mark turns to mush.
#   thin   radius (px) of the thinnest feature AT 16px.  <0.65 = it vanishes.
#   nodes  path commands. >90 on an icon mark = traced or over-fussed.
#
# Thresholds are calibrated against marks verified by eye, not invented.
# Exit 1 on any FAIL.

T="${1:?Usage: audit.sh <dir|file.svg>}"
command -v magick &>/dev/null || { echo "needs ImageMagick" >&2; exit 3; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

render() {
  if   command -v rsvg-convert &>/dev/null; then rsvg-convert -w "$2" -h "$2" -o "$3" "$1" 2>/dev/null
  elif command -v resvg        &>/dev/null; then resvg "$1" "$3" --width "$2" >/dev/null 2>&1
  else magick -background none -density 600 "$1" -resize "${2}x${2}" "$3" 2>/dev/null; fi
}
regions() { # png areaThreshold
  magick "$1" -alpha extract -threshold 50% \
    -define connected-components:verbose=true \
    -define connected-components:area-threshold="$2" \
    -connected-components 8 null: 2>&1 | grep -cE '^[[:space:]]+[0-9]+:'
}
lt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0<b+0)}'; }
gt() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0>b+0)}'; }

FILES=()
if [[ -d "$T" ]]; then while IFS= read -r f; do FILES+=("$f"); done < <(find "$T" -maxdepth 1 -name '*.svg'|sort)
else FILES=("$T"); fi
[[ ${#FILES[@]} -gt 0 ]] || { echo "no SVGs in $T" >&2; exit 3; }

FAIL=0; NAMES=()
printf "%-18s %6s %6s %9s %6s %6s  %s\n" MARK INK TPL RGN THIN NODES VERDICT
printf -- "----------------------------------------------------------------------------\n"

for f in "${FILES[@]}"; do
  n="$(basename "$f" .svg)"
  render "$f" 256 "$TMP/a.png"; render "$f" 16 "$TMP/b.png"
  [[ -s "$TMP/a.png" ]] || { printf "%-18s RENDER FAILED\n" "$n"; FAIL=1; continue; }

  magick "$TMP/a.png" -alpha extract "$TMP/al.png"
  ink="$(magick "$TMP/al.png" -format '%[fx:mean]' info:)"
  magick "$TMP/a.png" -alpha extract -background white -alpha shape -fill '#111' \
    -colorize 100 -background white -flatten "$TMP/tp.png"
  tpl="$(magick "$TMP/tp.png" -format '%[fx:standard_deviation]' info:)"
  r256="$(regions "$TMP/a.png" 12)"; r16="$(regions "$TMP/b.png" 1)"
  thin="$(magick "$TMP/b.png" -alpha extract -morphology Distance Euclidean \
          -format '%[fx:maxima*255]' info: 2>/dev/null || echo 0)"
  nodes="$(grep -o '[MLCQAHVSTZmlcqahvstz]' "$f" 2>/dev/null | wc -l | tr -d ' ')"

  v="ok"
  gt "$ink" 0.85                      && { v="FAIL plate baked in";   FAIL=1; }
  [[ $v == ok ]] && lt "$tpl" 0.001   && { v="FAIL blank";            FAIL=1; }
  [[ $v == ok ]] && [[ "$r16" -lt "$r256" ]] && { v="FAIL counters close at 16px"; FAIL=1; }
  [[ $v == ok ]] && lt "$thin" 0.65   && { v="FAIL too thin for 16px"; FAIL=1; }
  [[ $v == ok ]] && lt "$thin" 0.95   && v="warn thin"
  [[ $v == ok ]] && gt "$ink" 0.62    && v="warn heavy"
  [[ $v == ok ]] && lt "$ink" 0.08    && v="warn sparse"
  [[ $v == ok ]] && [[ "$nodes" -gt 90 ]] && v="warn $nodes nodes"

  printf "%-18s %6.3f %6.3f %4s->%-3s %6.2f %6s  %s\n" \
    "$n" "$ink" "$tpl" "$r256" "$r16" "$thin" "$nodes" "$v"
  NAMES+=("$n"); magick "$TMP/al.png" -resize 128x128 "$TMP/h_${#NAMES[@]}.png"
done

if [[ ${#NAMES[@]} -ge 2 ]]; then
  echo; echo "Distinctness (RMSE; <0.18 = the round is one idea, not a real choice)"
  for ((i=1;i<=${#NAMES[@]};i++)); do for ((j=i+1;j<=${#NAMES[@]};j++)); do
    r="$(magick compare -metric RMSE "$TMP/h_$i.png" "$TMP/h_$j.png" null: 2>&1|grep -o '(.*)'|tr -d '()')"; r="${r:-1}"
    fl=""; lt "$r" 0.18 && { fl="  <-- TOO ALIKE"; FAIL=1; }
    printf "  %-14s ~ %-14s %6.3f%s\n" "${NAMES[i-1]}" "${NAMES[j-1]}" "$r" "$fl"
  done; done
fi

echo
[[ $FAIL -eq 0 ]] && echo "AUDIT PASSED" || echo "AUDIT FAILED — fix these before showing them"
exit $FAIL
