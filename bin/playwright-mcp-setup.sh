#!/bin/bash
# ブラウザ操作MCP（playwright / chrome-devtools）を新規PCにセットアップする。
# 冪等: 何度実行しても同じ状態に収束する。既存の LaunchAgent・MCP設定は上書きされる。
#
# やること:
#   1. bin/*.sh, bin/*.py に実行権限を付与
#   2. node バージョンが chrome-devtools-mcp の engines を満たすか確認（満たさなければ警告のみ）
#   3. playwright-mcp-config.json（CDPポート指定）を生成
#   4. LaunchAgent plist を実行環境から生成して配置・(再)ロード
#   5. ~/.claude.json の mcpServers.playwright / mcpServers.chrome-devtools を設定
#   6. サーバの起動（自動化専用Chromeへのattach）を確認するまで待つ
#
# やらないこと（このPCで手動が必要）:
#   - 自動化専用Chrome（Chrome-automation プロファイル）への実際のログイン
#     （OAuthフローは自動化できないため。スクリプト完了後に開いたウィンドウで行う）
set -eu

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${PLAYWRIGHT_MCP_PORT:-8931}"
CDP_PORT="${PLAYWRIGHT_MCP_CDP_PORT:-9223}"
PLIST_LABEL="com.ukwhatn.playwright-mcp"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_PATH="$HOME/Library/Logs/playwright-mcp.log"

log() { echo "[setup] $*"; }
die() { echo "[setup] ERROR: $*" >&2; exit 1; }

log "対象ディレクトリ: $BIN_DIR"

# --- 1. 実行権限 -------------------------------------------------------
chmod +x "$BIN_DIR/playwright-mcp-server.sh" "$BIN_DIR/playwright-mcp-pin.py"
log "実行権限を付与した"

# --- 2. node バージョン確認 --------------------------------------------
NPX_BIN="$(command -v npx || true)"
[ -n "$NPX_BIN" ] || die "npx が見つからない。node/npm を先にインストールすること"
NODE_BIN="$(command -v node || true)"
[ -n "$NODE_BIN" ] || die "node が見つからない"

NODE_VERSION="$("$NODE_BIN" -v)"
NODE_OK=$("$NODE_BIN" -e '
  const v = process.versions.node.split(".").map(Number);
  const [maj, min] = v;
  const ok = maj >= 23 || (maj === 22 && min >= 12) || (maj === 20 && min >= 19);
  console.log(ok ? "yes" : "no");
')
if [ "$NODE_OK" = "no" ]; then
  log "警告: node $NODE_VERSION は chrome-devtools-mcp の要求（^20.19.0 || ^22.12.0 || >=23）を満たさない"
  log "      chrome-devtools 側は起動直後に exit し、MCP 接続失敗としてしか見えなくなる"
  log "      'mise use -g node@22' 等で上げてから再実行すること（playwright 側はこのまま使える）"
else
  log "node $NODE_VERSION: OK"
fi

NPX_DIR="$(dirname "$NPX_BIN")"

# --- 3. playwright-mcp-config.json（CDPポートの単一ソース）--------------
cat > "$BIN_DIR/playwright-mcp-config.json" <<EOF
{
  "browser": {
    "launchOptions": {
      "args": ["--remote-debugging-port=${CDP_PORT}"]
    }
  }
}
EOF
log "playwright-mcp-config.json を生成した（CDP port: ${CDP_PORT}）"

# --- 3b. LaunchAgent の生成・配置・(再)ロード ---------------------------
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${BIN_DIR}/playwright-mcp-server.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>15</integer>
    <key>StandardOutPath</key>
    <string>${LOG_PATH}</string>
    <key>StandardErrorPath</key>
    <string>${LOG_PATH}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${NPX_DIR}:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PLAYWRIGHT_MCP_PORT</key>
        <string>${PORT}</string>
    </dict>
</dict>
</plist>
EOF
log "LaunchAgent を生成した: $PLIST_PATH"

LOG_OFFSET=0
[ -f "$LOG_PATH" ] && LOG_OFFSET=$(wc -c < "$LOG_PATH" | tr -d ' ')

launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl load "$PLIST_PATH"
log "LaunchAgent をロードした"

# --- 4. MCP設定（~/.claude.json） --------------------------------------
python3 "$BIN_DIR/playwright-mcp-setup-mcpjson.py" "$PORT" "$CDP_PORT"

# --- 5. attach 確認 ------------------------------------------------------
log "サーバの起動を待っている（自動化専用Chromeへのattach）..."
ATTACHED=no
for _ in $(seq 1 60); do
  if [ -f "$LOG_PATH" ] && tail -c "+$((LOG_OFFSET + 1))" "$LOG_PATH" | grep -q "attached (session"; then
    ATTACHED=yes
    break
  fi
  sleep 2
done

if [ "$ATTACHED" = "yes" ]; then
  log "起動確認OK。自動化専用Chromeが立ち上がっているはず"
else
  log "60秒待っても attach ログが出なかった。ログを確認すること: $LOG_PATH"
fi

cat <<'EOF'

[setup] 完了。残っているのは手動作業のみ:
  - 開いた自動化専用Chromeのウィンドウで、使うアカウントにログインする
    （拡張機能は動かない構成。ログイン状態の保持のみが目的）
  - 他の Claude Code セッションで /mcp を実行し、playwright / chrome-devtools を再接続する
EOF
