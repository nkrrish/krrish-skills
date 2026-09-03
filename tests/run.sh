#!/usr/bin/env bash
# Full local test run. Same checks CI performs.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT="$ROOT/plugins/branding/skills/logo-designer/scripts/audit.sh"
FIX="$ROOT/tests/fixtures"
fail=0

echo "== manifests =="
python3 "$ROOT/tests/validate_manifests.py" || fail=1

echo
echo "== audit: good fixtures must pass =="
if bash "$AUDIT" "$FIX/good" >/dev/null 2>&1; then echo "  ok"; else
  echo "  FAIL — good fixtures did not pass:"; bash "$AUDIT" "$FIX/good" 2>&1 | sed 's/^/    /'; fail=1
fi

echo
echo "== audit: each bad fixture must be caught =="
for f in "$FIX"/bad/*.svg; do
  n="$(basename "$f" .svg)"
  if bash "$AUDIT" "$f" >/dev/null 2>&1; then echo "  FAIL $n was NOT caught"; fail=1
  else echo "  ok   $n caught"; fi
done

echo
echo "== shapegen: every generator emits parsable SVG =="
G="$ROOT/plugins/branding/skills/logo-designer/scripts/shapegen.py"
tmp="$(mktemp -d)"
for m in truchet rosette cluster checker squircle carve; do
  if python3 "$G" "$m" --out "$tmp/$m.svg" >/dev/null 2>&1 \
     && python3 -c "import xml.dom.minidom,sys;xml.dom.minidom.parse(sys.argv[1])" "$tmp/$m.svg"; then
    echo "  ok   $m"
  else echo "  FAIL $m"; fail=1; fi
done
rm -rf "$tmp"

echo
[[ $fail -eq 0 ]] && echo "ALL TESTS PASSED" || echo "TESTS FAILED"
exit $fail
