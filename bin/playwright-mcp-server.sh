#!/bin/bash
# playwright-mcp を standalone HTTP server として1本だけ常駐させ、
# ユーザーが起動した Chrome の CDP endpoint に接続する。
#
# Why not stdio: セッションごとに MCP サーバを起こすと、
#   - 拡張モード: 拡張が同時に1接続しか保持しないため、後から接続したセッションが先のセッションを切断する
#   - CDP 直結: 接続ごとに Chrome の承認ダイアログが出る
# サーバを1本に集約すると CDP 接続も1本になり、各セッションは HTTP クライアントとして
# 同一 browser context を共有しつつ、自分の current tab を独立して持てる。
set -u

PORT="${PLAYWRIGHT_MCP_PORT:-8931}"
HOST="${PLAYWRIGHT_MCP_HOST:-127.0.0.1}"
CHROME_DIR="${CHROME_USER_DATA_DIR:-$HOME/Library/Application Support/Google/Chrome}"
PORT_FILE="$CHROME_DIR/DevToolsActivePort"
NPX="${NPX_BIN:-$HOME/.local/share/mise/shims/npx}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# DevToolsActivePort は Chrome が remote debugging 有効時に書く2行のファイル（1行目: port, 2行目: browser ws path）
read_endpoint() {
  [ -f "$PORT_FILE" ] || return 1
  local p wspath
  p=$(sed -n '1p' "$PORT_FILE")
  wspath=$(sed -n '2p' "$PORT_FILE")
  [ -n "$p" ] && [ -n "$wspath" ] || return 1
  printf 'ws://127.0.0.1:%s%s' "$p" "$wspath"
}

endpoint=""
for _ in $(seq 1 60); do
  if endpoint=$(read_endpoint); then break; fi
  sleep 5
done
if [ -z "$endpoint" ]; then
  log "DevToolsActivePort not found in $CHROME_DIR (Chrome 未起動、または chrome://inspect/#remote-debugging が無効)"
  exit 1
fi

fingerprint=$(cat "$PORT_FILE")
log "connecting to $endpoint (port $PORT)"

"$NPX" -y @playwright/mcp@latest \
  --port "$PORT" \
  --host "$HOST" \
  --allowed-hosts "127.0.0.1:$PORT,localhost:$PORT,[::1]:$PORT" \
  --cdp-endpoint "$endpoint" \
  --shared-browser-context &
child=$!

# 接続クライアントが 0 になると Chrome から detach され、次の操作で承認ダイアログが再度出る。
# pin クライアントを1本張り続けて attach を維持する。
PLAYWRIGHT_MCP_PORT="$PORT" python3 "$(dirname "$0")/playwright-mcp-pin.py" &
pin=$!

cleanup() {
  kill "$pin" 2>/dev/null
  kill "$child" 2>/dev/null
}
trap cleanup EXIT INT TERM

# Chrome が終了・再起動すると endpoint が変わるので、変化を検知したら自分ごと終了して
# launchd に再起動させる（再起動時に endpoint を再解決する）
while kill -0 "$child" 2>/dev/null; do
  sleep 10
  if [ "$(cat "$PORT_FILE" 2>/dev/null)" != "$fingerprint" ]; then
    log "CDP endpoint changed or Chrome exited; restarting"
    exit 0
  fi
  if ! kill -0 "$pin" 2>/dev/null; then
    log "pin client died; restarting"
    exit 1
  fi
done
wait "$child"
