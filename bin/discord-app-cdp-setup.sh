#!/bin/bash
# discord-app-mcp.py の専用 Discord インスタンスを、ログイン時に起動する LaunchAgent を登録する。
# 冪等: 何度実行しても同じ状態に収束する（既存の LaunchAgent は上書き）。
#
# やること:
#   1. ログのディレクトリを作る
#   2. uv のディレクトリを PATH に入れて plist を生成する（launchd の PATH には Homebrew 等が無い）
#   3. LaunchAgent を (再) 登録する。ログイン時に 1 回だけ `discord-app-mcp.py launch --at-login` を実行する
#
# やらないこと: 定期実行。使用中の Discord を再起動しないため、ログイン後に専用インスタンスが落ちたら
#   `discord-app-mcp.py launch` を手で実行する。登録前の確認は `discord-app-mcp.py launch --dry-run`
set -eu

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_LABEL="com.ukwhatn.discord-app-cdp"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_PATH="$HOME/Library/Logs/discord-app-cdp/launch.log"

log() { echo "[setup] $*"; }

chmod +x "$BIN_DIR/discord-app-mcp.py"
mkdir -p "$(dirname "$LOG_PATH")" "$HOME/Library/LaunchAgents"

uv_path="$(command -v uv || true)"
if [ -z "$uv_path" ]; then log "uv が見つからない。中止する"; exit 1; fi
LAUNCH_PATH="$(dirname "$uv_path"):/usr/bin:/bin:/usr/sbin:/sbin"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${BIN_DIR}/discord-app-mcp.py</string>
        <string>launch</string>
        <string>--at-login</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${LOG_PATH}</string>
    <key>StandardErrorPath</key>
    <string>${LOG_PATH}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${LAUNCH_PATH}</string>
    </dict>
</dict>
</plist>
EOF
log "LaunchAgent を生成した: $PLIST_PATH"

launchctl bootout "gui/$(id -u)/${PLIST_LABEL}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"
log "LaunchAgent を登録した（ログイン時に 1 回。ログ: $LOG_PATH）"
