#!/usr/bin/env python3
"""UserPromptSubmit / PreToolUse hook: 受付の会話に作業をさせない。

規則は context/tool-claude-code.md「受付の会話」、切り出しの手順は skills/taskboard/SKILL.md。
受付の会話は、Slack の依頼の届け先（案件の Slack 設定の routes）のタスクの会話と、オーケストレーターの会話
（定期実行の会話は除く）。taskboard の daemon の状態から判定する。

- UserPromptSubmit: 受付の会話なら、そのことを additionalContext で知らせる
- PreToolUse: 受付の会話でのファイルの書き込み（メモリディレクトリと一時ディレクトリを除く）、
  commit・push・PR の作成を拒否する

daemon に繋がらない・taskboard の会話でないときは何もしない（daemon の停止中に全セッションの書き込みを拒否しないため）。
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request

FILE_TOOLS = {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}
ALLOWED_PATH_PARTS = ("/.local/memory/", "/.local/issues/")
GIT_WRITE = re.compile(r"\bgit\b[^;&|\n]*?\s(?:commit|push)\b")
GH_PR_WRITE = re.compile(r"\bgh\s+pr\s+(?:create|ready|merge)\b")
GITHUB_MCP_WRITE = re.compile(r"^mcp__github[\w-]*__(?:create_pull_request|push_files|create_or_update_file|merge_pull_request)$")

INTAKE_NOTICE = (
    "この会話は受付の会話（~/.claude/context/tool-claude-code.md「受付の会話」）。"
    "返答の文だけで答えられる質問以外は、調べる前にタスクを切って会話を起こす（/taskboard「受付の会話の依頼を切り出す」）。"
)
DENY_REASON = (
    "受付の会話では作業せず、タスクを切って会話を起こす（/taskboard「受付の会話の依頼を切り出す」、"
    "規則は ~/.claude/context/tool-claude-code.md「受付の会話」）。"
    "書き込めるのはメモリディレクトリ（.local/memory・.local/issues）と一時ディレクトリだけ。"
)


def daemon_get(path: str) -> dict:
    support = os.environ.get("TASKBOARD_SUPPORT_DIR") or os.path.expanduser("~/Library/Application Support/taskboard")
    with open(os.path.join(support, "token"), encoding="utf-8") as f:
        token = f.read().strip()
    port = os.environ.get("TASKBOARD_DAEMON_PORT") or "5780"
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=3) as response:
        return json.load(response)


def is_intake(conversation_id: str) -> bool:
    state = daemon_get("/v1/state")
    conversation = next((c for c in state.get("conversations", []) if c.get("id") == conversation_id), None)
    if conversation is None or conversation.get("purpose") == "schedule":
        return False
    if (state.get("orchestrator") or {}).get("conversationID") == conversation_id:
        return True
    task_number = conversation.get("taskNumber")
    if task_number is None:
        return False
    for board in state.get("boards", []):
        routes = daemon_get(f"/v1/boards/{board['id']}/slack").get("routes", [])
        if any(route.get("taskNumber") == task_number for route in routes):
            return True
    return False


def allowed_path(path: str) -> bool:
    real = os.path.realpath(os.path.expanduser(path))
    if any(part in real for part in ALLOWED_PATH_PARTS):
        return True
    temp_roots = {os.path.realpath(p) for p in (os.environ.get("TMPDIR"), "/tmp", "/private/tmp") if p}
    return any(real == root or real.startswith(root.rstrip("/") + "/") for root in temp_roots)


def is_work_call(tool_name: str, tool_input: dict) -> bool:
    if tool_name in FILE_TOOLS:
        path = tool_input.get(FILE_TOOLS[tool_name])
        return bool(path) and not allowed_path(path)
    if tool_name == "Bash":
        command = tool_input.get("command") or ""
        return bool(GIT_WRITE.search(command) or GH_PR_WRITE.search(command))
    return bool(GITHUB_MCP_WRITE.match(tool_name))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    conversation_id = os.environ.get("TASKBOARD_CONVERSATION_ID")
    if not conversation_id:
        return 0
    event = data.get("hook_event_name")
    if event == "PreToolUse" and not is_work_call(data.get("tool_name") or "", data.get("tool_input") or {}):
        return 0
    try:
        intake = is_intake(conversation_id)
    except (OSError, ValueError, KeyError):
        return 0
    if not intake:
        return 0
    if event == "UserPromptSubmit":
        output = {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": INTAKE_NOTICE}}
    elif event == "PreToolUse":
        output = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": DENY_REASON}}
    else:
        return 0
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
