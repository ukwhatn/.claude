#!/bin/bash
# disk-inventory.sh を launchd に登録する。冪等: 何度実行しても同じ状態に収束する（既存のLaunchAgentは上書き）。
#
# やること:
#   1. 設定ファイルが無ければ雛形を置く（既存の設定は触らない）
#   2. 実行環境のPATHから、依存コマンド（docker / gh / npm / uv / brew）のディレクトリを拾ってplistを生成
#   3. LaunchAgentを(再)ロード。毎時起動し、disk-inventory.sh --scheduled が実行要否を判定する
#
# やらないこと: 初回の棚卸し。登録前に `disk-inventory.sh`（dry-run）で報告を確認すること
set -eu

BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLIST_LABEL="com.ukwhatn.disk-inventory"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"
LOG_PATH="$HOME/Library/Logs/disk-inventory/launchd.log"
CONFIG="$HOME/.config/disk-inventory/config.sh"

log() { echo "[setup] $*"; }

chmod +x "$BIN_DIR/disk-inventory.sh"
mkdir -p "$(dirname "$LOG_PATH")" "$(dirname "$CONFIG")" "$HOME/Library/LaunchAgents"

if [ ! -f "$CONFIG" ]; then
  cat > "$CONFIG" <<'EOF'
# disk-inventory.sh のマシン固有設定（git管理外）。項目の意味と既定値は ~/.claude/bin/disk-inventory.sh 冒頭を参照
MIN_FREE_GB=50
INTERVAL_DAYS=7
STALE_DAYS=14
# worktreeを片付けるリポジトリ。"パス" か "パス:基準ブランチ"
WORKTREE_REPOS=()
# ビルド成果物（.next / DerivedData*）を探す起点
BUILD_SCAN_ROOTS=()
PROTECT_PATHS=()
EOF
  log "設定の雛形を置いた: $CONFIG（WORKTREE_REPOS / BUILD_SCAN_ROOTS を埋めること）"
else
  log "既存の設定を使う: $CONFIG"
fi

path_dirs=""
for cmd in docker gh npm uv brew git; do
  p="$(command -v "$cmd" || true)"
  if [ -z "$p" ]; then log "$cmd が見つからない（その項目は飛ばされる）"; continue; fi
  d="$(dirname "$p")"
  case ":$path_dirs:" in *":$d:"*) ;; *) path_dirs="${path_dirs:+$path_dirs:}$d" ;; esac
done
LAUNCH_PATH="${path_dirs:+$path_dirs:}/usr/bin:/bin:/usr/sbin:/sbin"

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
        <string>${BIN_DIR}/disk-inventory.sh</string>
        <string>--scheduled</string>
        <string>--apply</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>LowPriorityIO</key>
    <true/>
    <key>Nice</key>
    <integer>10</integer>
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

launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl load "$PLIST_PATH"
log "LaunchAgent をロードした（毎時起動。実行するのは前回から INTERVAL_DAYS 経過したときか空きが MIN_FREE_GB 未満のとき）"
log "報告: $HOME/Library/Logs/disk-inventory/latest.md"
