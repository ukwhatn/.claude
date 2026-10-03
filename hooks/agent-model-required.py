#!/usr/bin/env python3
"""PreToolUse hook: Agent tool の呼び出しに model が無ければ拒否する。

委譲先のモデルは用途で選ぶ規則（context/herdr-delegation.md「モデルの選択」）の強制側。
Agent tool は model を省略すると親セッションのモデルを継承するため、省略を許すと
調査にも親と同じ上位モデルが使われる。意図は context 側、強制はこの hook。

例外: subagent_type が fork のとき（fork は常に親モデルで動き、model 指定が無視される）。
"""
import json
import sys


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Agent":
        return 0
    tool_input = data.get("tool_input") or {}
    if tool_input.get("subagent_type") == "fork":
        return 0
    if tool_input.get("model"):
        return 0
    reason = (
        "Agent tool には model を用途で選んで渡す（コードを書かない調査: sonnet / "
        "レビュー報告・単発判定: opus / 前例のない難所: fable。"
        "表は ~/.claude/context/herdr-delegation.md「モデルの選択」）。"
        "親セッションと同じモデルが要ると判断したときは、そのモデル名を model に明示し、"
        "判断を 05_log.md に書く。"
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
