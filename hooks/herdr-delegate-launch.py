#!/usr/bin/env python3
"""PreToolUse hook: herdr-delegate.sh を harness の完了通知が届かない形で起動したら拒否する。

起動の形の規定（context/herdr-delegation.md「ライフサイクル」）の強制側。harness の完了通知は
Bash 呼び出しのプロセスの終了に紐づくため、`&`・nohup で切り離すと、委譲先が終わっても
通知が来ない。ループで複数を1呼び出しに入れると、通知は全部が終わった時に1回だけになる。

判定するのは herdr-delegate.sh を「コマンドとして起動している」呼び出しだけ。
grep・cat・bash -n のように引数として名前が出るだけの呼び出しは対象外。
"""
import json
import re
import sys

# 行頭・区切り記号・ラッパーの直後に置かれたものだけを起動とみなす
INVOCATION = re.compile(
    r"(?:^|[;&|({]|\b(?:do|then|else|nohup|exec|setsid|time|env|command|bash|sh))"
    r"\s*(?:\w+=\S*\s+)*(?:\S*/)?herdr-delegate\.sh\b",
    re.MULTILINE,
)
# `&&`・`2>&1`・`&>`・`|&` は切り離しではない
DETACH = re.compile(r"(?<![&>|<])&(?![&>])|\b(?:nohup|disown|setsid)\b")
LOOP = re.compile(r"\b(?:do|xargs|parallel)\b")


def violations(tool_input: dict) -> list[str]:
    command = tool_input.get("command") or ""
    invocations = INVOCATION.findall(command)
    if not invocations:
        return []
    found = []
    if tool_input.get("run_in_background") is not True:
        found.append("run_in_background: true が付いていない")
    if DETACH.search(command):
        found.append("`&`・nohup・disown・setsid で切り離している")
    if len(invocations) > 1 or LOOP.search(command):
        found.append("1回の呼び出しで複数の委譲を起動している（ループ・複数行）")
    return found


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    if data.get("tool_name") != "Bash":
        return 0
    found = violations(data.get("tool_input") or {})
    if not found:
        return 0
    reason = (
        "herdr-delegate.sh の起動の形が規定に合わない: " + " / ".join(found) + "。"
        "1委譲を Bash 1呼び出しにし、run_in_background: true で、`&`・nohup を付けずに起動する"
        "（切り離すと委譲先が終わっても harness の完了通知が来ない）。"
        "並列に回すときは同じメッセージに Bash 呼び出しを体数分並べ、state の確認は別の呼び出しで行う。"
        "規定: ~/.claude/context/herdr-delegation.md「ライフサイクル」"
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
