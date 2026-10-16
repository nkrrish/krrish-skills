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
echo "== branding python tools run offline =="
# None of these may touch the network: no --refs-industry, no --format paths.
S="$ROOT/plugins/branding/skills/logo-designer/scripts"
tmp="$(mktemp -d)"
pyok() { # pyok <name> <cmd...>
  local name="$1"; shift
  if "$@" >"$tmp/out" 2>&1; then echo "  ok   $name"; else echo "  FAIL $name"; sed 's/^/    /' "$tmp/out"; fail=1; fi
}
pyok "svg_audit parses good fixtures"  python3 -I "$S/svg_audit.py" --json "$FIX"/good/*.svg
pyok "search_library reads catalog"    python3 -I "$S/search_library.py" --industry fintech --summary
pyok "preview_sheet writes HTML"       python3 -I "$S/preview_sheet.py" "$FIX"/good/*.svg -o "$tmp/sheet.html"
pyok "export_variants writes SVGs"     python3 -I "$S/export_variants.py" "$FIX/good/squircle.svg" \
                                         --mono "#0F7C80" --out-dir "$tmp/ex"
for f in "$tmp"/ex/*.svg; do
  python3 -c "import xml.dom.minidom,sys;xml.dom.minidom.parse(sys.argv[1])" "$f" \
    || { echo "  FAIL $(basename "$f") is not valid XML"; fail=1; }
done
[ "$(ls "$tmp"/ex/*.svg 2>/dev/null | wc -l)" -ge 5 ] || { echo "  FAIL expected 5+ variant SVGs"; fail=1; }
if find "$S" -name __pycache__ | grep -q .; then echo "  FAIL scripts left __pycache__ in the skill"; fail=1; fi
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
echo "== branding: brand-builder scripts work offline =="
# No network here: names are generated, scored and rendered from a fixture; the domain
# checker and handle probe are only asked for their usage.
BB="$ROOT/plugins/branding/skills/brand-builder/scripts"
bb="$(mktemp -d)"
check "gen_names makes names"            0 python3 "$BB/gen_names.py" --count 60 --seeds cue,nod --out "$bb/names.json"
python3 - "$bb" <<'PY'
import json, sys
d = sys.argv[1]
names = json.load(open(f"{d}/names.json"))
json.dump([dict(n, domain=n["name"] + ".com", status="free") for n in names], open(f"{d}/checked.json", "w"))
PY
check "score_names scores"               0 python3 "$BB/score_names.py" "$bb/checked.json" --out "$bb/scored.json"
check "build_sheet renders"              0 python3 "$BB/build_sheet.py" "$bb/scored.json" --out "$bb/sheet.html"
check "sheet has its filters"            0 grep -q 'id="fEnd"' "$bb/sheet.html"
python3 "$BB/build_shortlist.py" --example > "$bb/short.json" 2>/dev/null
check "build_shortlist renders"          0 python3 "$BB/build_shortlist.py" "$bb/short.json" --out "$bb/short.html"
python3 "$BB/build_shortlist.py" --example companion > "$bb/short2.json" 2>/dev/null
python3 "$BB/build_shortlist.py" "$bb/short2.json" --out "$bb/short2.html" >/dev/null 2>&1
check "shortlist mockups follow the product" 1 grep -q "recorded on this Mac" "$bb/short2.html"
check "contrast passes a good pair"      0 python3 "$BB/contrast.py" "#15171C/#F6C445"
check "contrast fails a bad pair"        1 python3 "$BB/contrast.py" "#F6C445/#F7F7F4"
check "voice lists its commands"        0 python3 "$BB/voice.py" --help
check "check_deps flags a missing skill" 1 python3 "$BB/check_deps.py" no-such-skill-xyz
check "check_domains needs input"        2 python3 "$BB/check_domains.py"
check "no rude names generated"          0 python3 -c "import json,sys;n=[x['name'] for x in json.load(open(sys.argv[1]))];sys.exit(any(b in x for x in n for b in ('sex','fuk','ass','lez')))" "$bb/names.json"
rm -rf "$bb"

echo
[[ $fail -eq 0 ]] && echo "ALL TESTS PASSED" || echo "TESTS FAILED"
exit $fail
