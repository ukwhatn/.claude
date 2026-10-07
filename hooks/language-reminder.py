#!/usr/bin/env python3
"""UserPromptSubmit / PostToolUse hook: settings.json の language を additionalContext で再提示する。

Claude Code は言語指定をセッション開始時と compaction 直後にしか差し込まないため、
長い自律実行や英語の要約・ツール結果・ハーネスの通知が続くと応答が英語に流れる。直近に指定を置いて防ぐ。

- UserPromptSubmit: 毎回出す。ツール呼び出しの数え直しもここで始める
- PostToolUse: 1ターンが長いと UserPromptSubmit の指定が遠くなるので、ツール呼び出し INTERVAL 回ごとに出す
  （毎回だと長いターンで同じ文が数十回文脈に積まれる）
"""
import json
import os
import re
import sys
import tempfile

INTERVAL = 10


def load_language() -> str | None:
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    try:
        with open(os.path.join(config_dir, "settings.json"), encoding="utf-8") as f:
            return json.load(f).get("language")
    except (OSError, ValueError):
        return None


def counter_path(session_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id) or "unknown"
    directory = os.path.join(tempfile.gettempdir(), "claude-language-reminder")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, safe)


def tool_calls_since_prompt(session_id: str, reset: bool) -> int:
    path = counter_path(session_id)
    count = 0
    if not reset:
        try:
            with open(path, encoding="utf-8") as f:
                count = int(f.read().strip() or 0)
        except (OSError, ValueError):
            count = 0
        count += 1
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(count))
    except OSError:
        pass
    return count


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    event = payload.get("hook_event_name") or "UserPromptSubmit"
    session_id = str(payload.get("session_id") or "")

    if event == "PostToolUse":
        if tool_calls_since_prompt(session_id, reset=False) % INTERVAL != 0:
            return
    else:
        tool_calls_since_prompt(session_id, reset=True)

    language = load_language()
    if not language:
        return
    context = (
        f"応答・報告・質問は{language}で書く。ツールを何度も実行した後のターン末の報告も同じ。"
        "英語のツール結果・要約・通知が続いていても言語を切り替えない（コード・識別子・引用は原文のまま）。"
    )
    json.dump(
        {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}},
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
