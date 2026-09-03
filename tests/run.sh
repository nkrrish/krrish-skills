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
echo "== audit: good fixtures must pass (exit 0) =="
bash "$AUDIT" "$FIX/good" >/tmp/audit_good.txt 2>&1; rc=$?
if [ "$rc" -eq 0 ]; then echo "  ok"
elif [ "$rc" -eq 3 ]; then
  echo "  FAIL — audit could not run (missing dependency), not a verdict:"; sed 's/^/    /' /tmp/audit_good.txt; fail=1
else
  echo "  FAIL — good fixtures did not pass:"; sed 's/^/    /' /tmp/audit_good.txt; fail=1
fi

echo
echo "== audit: each bad fixture must be caught (exit 1, not 3) =="
# Exit 1 means a real FAIL verdict. Exit 3 means the audit could not run at all —
# accepting that as "caught" would let a broken environment fake a passing suite.
for f in "$FIX"/bad/*.svg; do
  n="$(basename "$f" .svg)"
  bash "$AUDIT" "$f" >/dev/null 2>&1; rc=$?
  case "$rc" in
    1) echo "  ok   $n caught" ;;
    0) echo "  FAIL $n was NOT caught"; fail=1 ;;
    *) echo "  FAIL $n — audit errored (exit $rc), not a verdict"; fail=1 ;;
  esac
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
