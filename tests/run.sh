#!/usr/bin/env bash
# Full local test run. Same checks CI performs.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AUDIT="$ROOT/plugins/branding/skills/logo-designer/scripts/audit.sh"
FIX="$ROOT/tests/fixtures"
fail=0

echo "== manifests =="
python3 "$ROOT/tests/validate_manifests.py" || fail=1

if command -v claude >/dev/null 2>&1; then
  echo
  echo "== official manifest validator =="
  for m in "$ROOT" "$ROOT"/plugins/*/; do
    if claude plugin validate "$m" >/dev/null 2>&1; then echo "  ok   $(basename "$m")"
    else echo "  FAIL $(basename "$m")"; claude plugin validate "$m" 2>&1 | sed 's/^/    /'; fail=1; fi
  done
else
  echo "  (claude CLI not present — skipping official validator)"
fi

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
echo "== media: guard asks before every spend or key exposure =="
python3 "$ROOT/tests/guard_cases.py" || fail=1

echo
echo "== media: hf.sh fails safe offline =="
# None of these may reach the network: each must stop before any request is made.
HFS="$ROOT/plugins/media/skills/higgsfield/scripts/hf.sh"
home="$(mktemp -d)"
check() { # check <name> <want-exit> <cmd...>
  local name="$1" want="$2"; shift 2
  "$@" >/dev/null 2>&1; local rc=$?
  if [ "$rc" -eq "$want" ]; then echo "  ok   $name"; else echo "  FAIL $name (exit $rc, want $want)"; fail=1; fi
}
nokey() { env -i HOME="$home" PATH="/usr/bin:/bin" XDG_CONFIG_HOME="$home/.config" "$@"; }
fake()  { env -i HOME="$home" PATH="/usr/bin:/bin" HF_API_KEY_ID=x HF_API_KEY_SECRET=y "$@"; }
check "script parses"                    0 bash -n "$HFS"
check "no key: status says so"           2 nokey bash "$HFS" status
check "no key: submit refuses"           2 nokey bash "$HFS" submit /x '{"prompt":"a"}'
check "invalid JSON body refused"        2 fake  bash "$HFS" estimate /x '{"prompt":'
check "missing body file refused"        2 fake  bash "$HFS" submit /x @"$home/none.json"
check "bad request id refused"           2 fake  bash "$HFS" wait 'abc;rm'
check "unknown file type refused"        2 fake  bash "$HFS" upload "$HFS"
check "no subcommand prints usage"       2 bash "$HFS"
rm -rf "$home"

echo
[[ $fail -eq 0 ]] && echo "ALL TESTS PASSED" || echo "TESTS FAILED"
exit $fail
