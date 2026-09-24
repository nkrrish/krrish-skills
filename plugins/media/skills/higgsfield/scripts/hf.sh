#!/usr/bin/env bash
# hf.sh — Higgsfield Open API helper (unofficial). Pay-per-use against your own API key.
#
#   hf.sh setup [--from-env]                      connect your key (macOS dialog / terminal prompt), then verify it
#   hf.sh status                                  where the key is stored and whether it works (never prints it)
#   hf.sh prices                                  what the core models cost on YOUR account (free estimates)
#   hf.sh estimate <endpoint> <json | @file>      cost of one exact request (free)
#   hf.sh submit   <endpoint> <json | @file>      start a generation or training job (spends credits)
#   hf.sh upload   <local-file>                   upload an input image/video/audio, prints its public URL
#   hf.sh wait     <request_id> [out_dir]         poll until done and download every output (free)
#   hf.sh get      <endpoint>                     read-only GET, e.g. presets or Soul ID status (free)
#   hf.sh cancel   <request_id>                   cancel while still queued (refunded)
#
# Key lookup order: HF_API_KEY_ID / HF_API_KEY_SECRET env vars → macOS Keychain (service
# "higgsfield-api") → ${XDG_CONFIG_HOME:-~/.config}/higgsfield-api/credentials (mode 600).
# The plugin's guard hook asks before submit, upload and cancel; everything else is free.
set -euo pipefail

BASE="https://api.higgsfield.ai"
SERVICE="higgsfield-api"
CRED_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/higgsfield-api/credentials"
KEY_ID="" KEY_SECRET="" KEY_SOURCE=""

have_keychain() { [[ "$(uname)" == "Darwin" ]] && command -v security >/dev/null; }

load_keys() {
  if [[ -n "${HF_API_KEY_ID:-}" && -n "${HF_API_KEY_SECRET:-}" ]]; then
    KEY_ID="$HF_API_KEY_ID" KEY_SECRET="$HF_API_KEY_SECRET" KEY_SOURCE="environment variables"
    return 0
  fi
  if have_keychain; then
    local id secret
    id="$(security find-generic-password -s "$SERVICE" -a key-id -w 2>/dev/null || true)"
    secret="$(security find-generic-password -s "$SERVICE" -a key-secret -w 2>/dev/null || true)"
    if [[ -n "$id" && -n "$secret" ]]; then
      KEY_ID="$id" KEY_SECRET="$secret" KEY_SOURCE="macOS Keychain ($SERVICE)"
      return 0
    fi
  fi
  if [[ -f "$CRED_FILE" ]]; then
    KEY_ID="$(sed -n 's/^HF_API_KEY_ID=//p' "$CRED_FILE" | head -1)"
    KEY_SECRET="$(sed -n 's/^HF_API_KEY_SECRET=//p' "$CRED_FILE" | head -1)"
    if [[ -n "$KEY_ID" && -n "$KEY_SECRET" ]]; then KEY_SOURCE="$CRED_FILE"; return 0; fi
  fi
  return 1
}

need_keys() {
  load_keys && return 0
  echo "No Higgsfield API key connected. Run: $0 setup" >&2
  echo "(Create a key at https://cloud.higgsfield.ai — you get a key ID and a key secret.)" >&2
  exit 2
}

# Curl reads the header from stdin-free config so the key never appears in the process list.
api() { # api <METHOD> <path> [body]
  local method="$1" path="$2" body="${3:-}"
  local args=(-sS --fail-with-body -X "$method" "$BASE$path" -K -)
  [[ -n "$body" ]] && args+=(-H "Content-Type: application/json" --data "$body")
  printf 'header = "Authorization: Key %s:%s"\n' "$KEY_ID" "$KEY_SECRET" | curl "${args[@]}"
}

json_get() { python3 -c 'import json,sys; d=json.load(sys.stdin); print(eval(sys.argv[1], {"d": d}))' "$1"; }

body_arg() { # accepts inline JSON or @file.json; validates it parses
  local b="${1:?JSON body or @file.json}"
  [[ "$b" == @* ]] && b="$(cat "${b#@}")"
  printf '%s' "$b" | python3 -c 'import json,sys; json.load(sys.stdin)' 2>/dev/null \
    || { echo "Request body is not valid JSON" >&2; exit 2; }
  printf '%s' "$b"
}

endpoint_arg() { local e="${1:?endpoint path, e.g. /higgsfield-ai/soul/v2/standard}"; [[ "$e" == /* ]] || e="/$e"; printf '%s' "$e"; }

# Fixed-price models answer {"usd","credits"}; token-metered ones (Marketing Studio, Seedance)
# answer {"type":"description","pricing_description"} and are billed on actual usage.
usd() { python3 -c '
import json, sys
d = json.load(sys.stdin)
if "usd" in d: print(d["usd"], d.get("credits", "?"))
elif d.get("type") == "description": print("metered", "-")
else: print("?", "?")'; }

metered_note() { python3 -c 'import json,sys; print(json.load(sys.stdin).get("pricing_description",""))'; }

# ---------- setup ----------

ask_secret() { # ask_secret <prompt> → value on stdout
  local prompt="$1" v=""
  if [[ "$(uname)" == "Darwin" ]] && command -v osascript >/dev/null; then
    v="$(osascript -e "text returned of (display dialog \"$prompt\" default answer \"\" with hidden answer with title \"Connect Higgsfield\" buttons {\"Cancel\", \"Save\"} default button \"Save\")" 2>/dev/null)" \
      || { echo "Setup cancelled." >&2; exit 1; }
  elif [[ -t 0 ]]; then
    read -r -s -p "$prompt: " v; echo >&2
  else
    echo "Run setup in a terminal so it can prompt for the key: $0 setup" >&2; exit 2
  fi
  printf '%s' "$v"
}

store_keys() { # store_keys <id> <secret>  — either value may be the combined "ID:secret" string
  local id="$1" secret="$2"
  # Higgsfield also shows the key as one "ID:secret" string; accept it in either field.
  if [[ "$id" == *:* ]]; then secret="${id#*:}" id="${id%%:*}"; fi
  if [[ "$secret" == *:* && ( "${secret%%:*}" == "$id" || -z "$id" ) ]]; then id="${secret%%:*}" secret="${secret#*:}"; fi
  for v in "$id" "$secret"; do
    [[ -n "$v" && "$v" =~ ^[A-Za-z0-9._:+/=-]+$ ]] || { echo "That doesn't look like a Higgsfield key (empty or unexpected characters)." >&2; exit 2; }
  done
  if have_keychain; then
    # `security -i` reads commands from stdin, so the secret never appears in argv.
    printf 'add-generic-password -U -s %s -a key-id -l "Higgsfield API key ID" -w "%s"\nadd-generic-password -U -s %s -a key-secret -l "Higgsfield API key secret" -w "%s"\n' \
      "$SERVICE" "$id" "$SERVICE" "$secret" | security -i >/dev/null
    echo "Saved to macOS Keychain (service \"$SERVICE\")."
  else
    mkdir -p "$(dirname "$CRED_FILE")"
    ( umask 077; printf 'HF_API_KEY_ID=%s\nHF_API_KEY_SECRET=%s\n' "$id" "$secret" > "$CRED_FILE" )
    chmod 600 "$CRED_FILE"
    echo "Saved to $CRED_FILE (readable only by you)."
  fi
}

verify() {
  local r
  if r="$(api POST /estimate/higgsfield-ai/soul/v2/standard '{"prompt":"connection check"}' 2>&1)"; then
    echo "Connected ✓  (a Soul 2 image costs \$$(printf '%s' "$r" | usd | cut -d' ' -f1) on this account)"
  else
    echo "The key was saved but Higgsfield rejected it: $r" >&2
    echo "Check the key ID and secret at https://cloud.higgsfield.ai and run setup again." >&2
    exit 1
  fi
}

# ---------- commands ----------

cmd="${1:-}"; shift || true
case "$cmd" in
  setup)
    if [[ "${1:-}" == "--from-env" ]]; then
      [[ -n "${HF_API_KEY_ID:-}" && -n "${HF_API_KEY_SECRET:-}" ]] || { echo "HF_API_KEY_ID / HF_API_KEY_SECRET are not set in this shell." >&2; exit 2; }
      store_keys "$HF_API_KEY_ID" "$HF_API_KEY_SECRET"
    else
      echo "Opening a prompt for your Higgsfield key (cloud.higgsfield.ai → API keys)…"
      id="$(ask_secret "Paste your Higgsfield API key ID — or the whole key as ID:secret")"
      secret=""
      [[ "$id" == *:* ]] || secret="$(ask_secret "Paste your Higgsfield API key secret")"
      store_keys "$id" "$secret"
    fi
    unset HF_API_KEY_ID HF_API_KEY_SECRET
    load_keys && verify
    ;;

  status)
    if load_keys; then echo "Key found in: $KEY_SOURCE"; verify
    else echo "No key connected. Run: $0 setup"; exit 2; fi
    ;;

  prices)
    need_keys
    echo "Prices on your account (Higgsfield estimates, nothing is charged):"
    printf '  %-34s %-26s %10s\n' "MODEL" "REQUEST" "USD"
    notes=""
    while IFS='|' read -r label ep req body; do
      if r="$(api POST "/estimate$ep" "$body" 2>/dev/null)"; then
        cost="$(printf '%s' "$r" | usd | cut -d' ' -f1)"
        case "$cost" in
          metered) cost="metered*"; notes+="  * $label: $(printf '%s' "$r" | metered_note)"$'\n' ;;
          "?")     cost="?" ;;
          *)       cost="\$$cost" ;;
        esac
      else
        cost="n/a"
      fi
      printf '  %-34s %-26s %10s\n' "$label" "$req" "$cost"
    done <<'EOF'
Soul 2 (realistic people)|/higgsfield-ai/soul/v2/standard|1 image, 720p|{"prompt":"price check"}
Marketing Studio 2.5 Flare|/marketing-studio/image/flare|1 image, 2k, high|{"prompt":"price check","resolution":"2k","quality":"high"}
Marketing Studio 2.5 Sunburst|/marketing-studio/image/sunburst|1 image, 2k, high|{"prompt":"price check","resolution":"2k","quality":"high"}
Kling 3.0 Standard|/kling-video/v3.0/std/text-to-video|5s, sound off|{"prompt":"price check","duration":5,"sound":"off"}
Kling 3.0 Standard|/kling-video/v3.0/std/text-to-video|5s, sound on|{"prompt":"price check","duration":5}
Kling 3.0 Pro|/kling-video/v3.0/pro/text-to-video|5s, sound on|{"prompt":"price check","duration":5}
Seedance 2.0|/bytedance/seedance-2.0/text-to-video|5s, 720p|{"prompt":"price check","duration":5,"resolution":"720p"}
EOF
    if [[ -n "$notes" ]]; then
      echo; echo "Metered models are billed on actual usage; Higgsfield's own pricing rules:"
      printf '%s' "$notes" | fold -s -w 100 | sed 's/^/  /'
      echo "  Your console (console.higgsfield.ai) shows any discounts you've claimed on these."
    fi
    echo "Exact cost of any other request: $0 estimate <endpoint> @request.json"
    ;;

  estimate)
    need_keys
    ep="$(endpoint_arg "${1:-}")"; body="$(body_arg "${2:-}")"
    raw="$(api POST "/estimate$ep" "$body")"
    read -r cost credits < <(printf '%s' "$raw" | usd)
    case "$cost" in
      metered) echo "Metered — billed on actual usage, not a fixed price:"; printf '%s' "$raw" | metered_note ;;
      "?")     echo "Unexpected estimate response: $raw" ;;
      *)       echo "\$$cost  ($credits credits)" ;;
    esac
    ;;

  submit)
    need_keys
    ep="$(endpoint_arg "${1:-}")"; body="$(body_arg "${2:-}")"
    api POST "$ep" "$body"; echo
    ;;

  upload)
    need_keys
    file="${1:?local file to upload}"
    [[ -f "$file" ]] || { echo "No such file: $file" >&2; exit 2; }
    case "$(printf '%s' "${file##*.}" | tr '[:upper:]' '[:lower:]')" in
      jpg|jpeg) type="image/jpeg" ;; png) type="image/png" ;; webp) type="image/webp" ;;
      gif) type="image/gif" ;; mp4) type="video/mp4" ;; wav) type="audio/wav" ;;
      *) echo "Unsupported type: $file (jpg, png, webp, gif, mp4, wav)" >&2; exit 2 ;;
    esac
    up="$(api POST /files/generate-upload-url "{\"content_type\":\"$type\"}")"
    # Presigned storage URL: send only its own headers, never the Higgsfield key.
    headers=()
    while IFS= read -r h; do headers+=(-H "$h"); done < <(printf '%s' "$up" |
      python3 -c 'import json,sys; [print(f"{k}: {v}") for k, v in json.load(sys.stdin)["upload_headers"].items()]')
    curl -sS --fail-with-body -X PUT "$(printf '%s' "$up" | json_get 'd["upload_url"]')" \
      "${headers[@]}" --upload-file "$file" >/dev/null
    printf '%s' "$up" | json_get 'd["public_url"]'
    ;;

  wait)
    need_keys
    id="${1:?request_id}"; out="${2:-.}"
    [[ "$id" =~ ^[0-9a-fA-F-]+$ ]] || { echo "request_id looks wrong: $id" >&2; exit 2; }
    mkdir -p "$out"
    delay=3
    while :; do
      resp="$(api GET "/requests/$id/status")"
      status="$(printf '%s' "$resp" | json_get 'd.get("status","")')"
      case "$status" in
        queued|in_progress) sleep "$delay"; (( delay < 20 )) && delay=$(( delay + 2 )) ;;
        completed) break ;;
        *) echo "Request $id ended as '$status' (failed and nsfw requests are refunded):" >&2; echo "$resp" >&2; exit 1 ;;
      esac
    done
    printf '%s' "$resp" | python3 -c '
import json, sys
d = json.load(sys.stdin)
urls = []
def walk(v):
    if isinstance(v, dict):
        if isinstance(v.get("url"), str): urls.append(v["url"])
        for x in v.values(): walk(x)
    elif isinstance(v, list):
        for x in v: walk(x)
walk({k: v for k, v in d.items() if k not in ("status_url", "cancel_url")})
seen = set()
for u in urls:
    if u not in seen:
        seen.add(u); print(u)
' | {
      n=0
      while read -r url; do
        n=$((n + 1))
        ext="${url%%\?*}"; ext="${ext##*.}"; [[ ${#ext} -le 4 ]] || ext="bin"
        f="$out/hf-${id:0:8}-$n.$ext"
        curl -sS -L "$url" -o "$f"
        echo "$f"
      done
    }
    ;;

  get)
    need_keys
    api GET "$(endpoint_arg "${1:-}")"; echo
    ;;

  cancel)
    need_keys
    id="${1:?request_id}"
    printf 'header = "Authorization: Key %s:%s"\n' "$KEY_ID" "$KEY_SECRET" |
      curl -sS -o /dev/null -w '%{http_code}\n' -X POST "$BASE/requests/$id/cancel" -K -
    ;;

  *)
    sed -n '2,17p' "$0"; exit 2 ;;
esac
