#!/usr/bin/env python3
"""UserPromptSubmit hook: settings.json の language を毎ターン additionalContext で再提示する。

Claude Code は言語指定をセッション開始時と compaction 直後にしか差し込まないため、
長い自律実行や英語の要約・ツール結果が続くと応答が英語に流れる。直近に指定を置いて防ぐ。
"""
import json
import os
import sys


def main() -> None:
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    try:
        with open(os.path.join(config_dir, "settings.json"), encoding="utf-8") as f:
            language = json.load(f).get("language")
    except (OSError, ValueError):
        return
    if not language:
        return
    context = (
        f"応答・報告・質問は{language}で書く。ツールを何度も実行した後のターン末の報告も同じ。"
        "英語のツール結果・要約・通知が続いていても言語を切り替えない（コード・識別子・引用は原文のまま）。"
    )
    json.dump(
        {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}},
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
