#!/bin/bash
# playwright-mcp を standalone HTTP server として1本だけ常駐させ、指定プロファイルで Chrome を起動する。
#
# Why not stdio: セッションごとに MCP サーバを起こすと、拡張ブリッジ方式では拡張が同時に1接続しか
# 保持しないため後から繋いだセッションが先のセッションを切断し、永続プロファイルは同時に1インスタンス
# しか掴めないため衝突する。サーバを1本に集約すると、各セッションは HTTP クライアントとして
# 同一プロファイル・同一コンテキストを共有しつつ、自分の current tab を独立して持てる。
#
# Why not --cdp-endpoint: ユーザーが起動したブラウザへ CDP で繋ぐ方式は、接続ごとにブラウザ側の
# 承認ダイアログが出る。サーバ自身がブラウザを起動すればこの経路を通らない。
set -u

PORT="${PLAYWRIGHT_MCP_PORT:-8931}"
HOST="${PLAYWRIGHT_MCP_HOST:-127.0.0.1}"
CHROME_PROFILE="${CHROME_PROFILE_DIR:-$HOME/Library/Application Support/Google/Chrome}"
NPX="${NPX_BIN:-$HOME/.local/share/mise/shims/npx}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "starting (profile: $CHROME_PROFILE, port: $PORT)"

"$NPX" -y @playwright/mcp@latest \
  --port "$PORT" \
  --host "$HOST" \
  --allowed-hosts "127.0.0.1:$PORT,localhost:$PORT,[::1]:$PORT" \
  --browser chrome \
  --user-data-dir "$CHROME_PROFILE" \
  --shared-browser-context &
child=$!

# サーバが listen する前に pin を繋ぐと初回が必ず失敗するため、待ってから起動する
for _ in $(seq 1 30); do
  nc -z "$HOST" "$PORT" 2>/dev/null && break
  sleep 1
done

# 接続クライアントが 0 になると playwright はブラウザを閉じる。普段使いのブラウザが勝手に終了しては
# 困るため、pin クライアントを1本張り続けてブラウザを生かしておく。
PLAYWRIGHT_MCP_PORT="$PORT" python3 "$(dirname "$0")/playwright-mcp-pin.py" &
pin=$!

cleanup() {
  kill "$pin" 2>/dev/null
  kill "$child" 2>/dev/null
}
trap cleanup EXIT INT TERM

while kill -0 "$child" 2>/dev/null; do
  sleep 10
  if ! kill -0 "$pin" 2>/dev/null; then
    log "pin client died; restarting"
    exit 1
  fi
done
log "server exited"
wait "$child"
