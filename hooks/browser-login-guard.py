#!/usr/bin/env python3
"""PreToolUse hook: browser-login の実行中は、ページの要素一覧（スナップショット）を返すブラウザ操作を拒否する。

playwright のスナップショットは、パスワード欄に入った値を伏せずに書き出し、ファイルにも残す。
browser-login がパスワードや TOTP を入れている間にクリックや遷移のツールを使うと、その値が
エージェントの文脈に入る。意図は context/browser-automation.md、強制はこの hook。

実行中の判定: ~/.local/state/browser-login/run-*.json があり、その pid が browser-login として
生きていること（異常終了で残った実行記録では止めない）。自動化 Chrome はセッション間で共有して
いるので、どのセッションが起動したヘルパーかは区別しない。
"""
import json
import subprocess
import sys
from pathlib import Path

STATE_DIR = Path.home() / ".local/state/browser-login"

# スナップショットを返さないツールだけを通す
ALLOWED = {
    "mcp__playwright__browser_evaluate",
    "mcp__playwright__browser_take_screenshot",
    "mcp__playwright__browser_tabs",
    "mcp__playwright__browser_console_messages",
    "mcp__playwright__browser_network_requests",
    "mcp__playwright__browser_network_request",
    "mcp__chrome-devtools__list_pages",
    "mcp__chrome-devtools__take_screenshot",
    "mcp__chrome-devtools__evaluate_script",
    "mcp__chrome-devtools__list_console_messages",
    "mcp__chrome-devtools__get_console_message",
    "mcp__chrome-devtools__list_network_requests",
    "mcp__chrome-devtools__get_network_request",
}


def helper_running() -> bool:
    for f in STATE_DIR.glob("run-*.json"):
        try:
            pid = int(json.loads(f.read_text())["pid"])
        except (OSError, ValueError, KeyError, TypeError):
            continue
        cmd = subprocess.run(["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True).stdout
        if "browser-login" in cmd:
            return True
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool = data.get("tool_name") or ""
    if not tool.startswith(("mcp__playwright__", "mcp__chrome-devtools__")) or tool in ALLOWED:
        return 0
    if not helper_running():
        return 0
    reason = (
        "browser-login の実行中は、スナップショットを返すブラウザ操作を使わない（パスワード欄の値が平文で写る）。"
        "クリックと遷移は browser_evaluate（ボタンを文言で探して click()、遷移は location.href）で行い、"
        "画面は browser_take_screenshot で確認する。ログインが済むか止めたあとなら使える。"
        "手順は ~/.claude/context/browser-automation.md。"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
