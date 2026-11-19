#!/usr/bin/env python3
"""UserPromptSubmit / PreToolUse hook: 時給制の案件で、稼働時間外に作業させない。

稼働中かどうかは案件ごとの状態ファイルが持ち、利用者の発言（「稼働開始」「作業終了」など）だけで切り替える。
taskboard の通知・wake・委譲先への指示は利用者の発言ではないので、切り替えに使わない。

- UserPromptSubmit: 案件の最上位の会話（委譲先でない会話）で、利用者の発言が開始・終了の語を含めば状態を切り替える。
  稼働時間外ならそのことを additionalContext で知らせる
- PreToolUse: 稼働時間外なら、その案件のセッションの tool 呼び出しをすべて拒否する。
  稼働中でも、taskboard の tool に開始の語を書くこと（wake・委譲先への指示で状態を切り替えること）は拒否する

案件の一覧（名前・taskboard の案件名・作業ディレクトリ）は git 管理外の local/work-hours.json に置く。無ければ何もしない。
稼働中の状態は、切り替えた日の 24 時か、終了の発言にある時刻で切れる（終了を言い忘れた翌朝に動かないため）。

利用者が端末から切り替えるとき: python3 work-hours-guard.py set <案件名> on|off
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta

CLAUDE_DIR = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
CONFIG_PATH = os.path.join(CLAUDE_DIR, "local", "work-hours.json")
STATE_DIR = os.path.join(CLAUDE_DIR, "local", "work-hours")

START = re.compile(r"(?:稼働|作業)を?(?:開始|始め|再開)")
END = re.compile(r"(?:稼働|作業)を?(?:終了|終わ)|今日は(?:これで)?(?:終わり|おしまい)")
END_TIME = re.compile(r"(\d{1,2})\s*(?:時|:)\s*(\d{1,2})?\s*分?\s*(?:に|で|まで)")
NON_HUMAN_PREFIXES = ("<!-- taskboard:", "Continue from where you left off.")

OFF_NOTICE = (
    "{name} は稼働時間外（時給制）。tool は hook が拒否する。通知・wake・委譲先の報告が届いても作業せず、"
    "「稼働時間外のため対応しません」と 1 文だけ返してターンを終える。再開は利用者が「稼働開始」と言ったとき。"
)
DENY_REASON = (
    "{name} は稼働時間外（時給制）なので、tool を使わずにターンを終える。"
    "再開は利用者が「稼働開始」と言ったときだけ（~/.claude/hooks/work-hours-guard.py）。"
)
DENY_START_WORD = "稼働の開始は利用者の発言だけで切り替える。taskboard の文面に開始の語を書かない（~/.claude/hooks/work-hours-guard.py）。"


def load_projects() -> list[dict]:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f).get("projects", [])
    except (OSError, ValueError):
        return []


def state_path(name: str) -> str:
    return os.path.join(STATE_DIR, f"{name}.json")


def is_working(name: str, now: datetime) -> bool:
    try:
        with open(state_path(name), encoding="utf-8") as f:
            state = json.load(f)
    except (OSError, ValueError):
        return False
    return bool(state.get("on")) and now < datetime.fromisoformat(state["until"])


def write_state(name: str, on: bool, until: datetime, now: datetime, reason: str) -> None:
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = state_path(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"on": on, "until": until.isoformat(), "changed_at": now.isoformat(), "reason": reason}, f, ensure_ascii=False)
    os.replace(tmp, state_path(name))


def end_of_day(now: datetime) -> datetime:
    return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


def apply_human_prompt(name: str, prompt: str, now: datetime) -> str | None:
    """利用者の発言で状態を切り替え、切り替えたら知らせる文を返す。"""
    if START.search(prompt):
        write_state(name, True, end_of_day(now), now, prompt[:200])
        return f"{name} の稼働を開始した（今日の 24 時か、利用者の終了の発言まで）。"
    if END.search(prompt):
        match = END_TIME.search(prompt)
        if match:
            until = now.replace(hour=int(match.group(1)), minute=int(match.group(2) or 0), second=0, microsecond=0)
            if until > now:
                write_state(name, True, until, now, prompt[:200])
                return f"{name} の稼働は {until:%H:%M} に終了する。それ以降は作業しない。"
        write_state(name, False, now, now, prompt[:200])
        return f"{name} の稼働を終了した。以降は通知が届いても作業しない。"
    return None


def daemon_get(path: str) -> dict:
    support = os.environ.get("TASKBOARD_SUPPORT_DIR") or os.path.expanduser("~/Library/Application Support/taskboard")
    with open(os.path.join(support, "token"), encoding="utf-8") as f:
        token = f.read().strip()
    port = os.environ.get("TASKBOARD_DAEMON_PORT") or "5780"
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=3) as response:
        return json.load(response)


def taskboard_conversation(conversation_id: str) -> tuple[str | None, bool]:
    """taskboard の会話の案件名と、委譲先の会話かどうかを返す。"""
    state = daemon_get("/v1/state")
    conversation = next((c for c in state.get("conversations", []) if c.get("id") == conversation_id), None)
    if conversation is None:
        return None, False
    is_delegate = conversation.get("parentConversationID") is not None
    task = next((t for t in state.get("tasks", []) if t.get("number") == conversation.get("taskNumber")), None)
    board = next((b for b in state.get("boards", []) if task and b.get("id") == task.get("boardID")), None)
    return (board or {}).get("name"), is_delegate


def resolve_project(projects: list[dict], cwd: str) -> tuple[dict | None, bool]:
    """セッションが属する案件と、利用者の発言で状態を切り替えてよい会話かどうかを返す。"""
    conversation_id = os.environ.get("TASKBOARD_CONVERSATION_ID")
    if conversation_id:
        try:
            board_name, is_delegate = taskboard_conversation(conversation_id)
        except (OSError, ValueError, KeyError):
            board_name, is_delegate = None, True
        project = next((p for p in projects if board_name and p.get("board") == board_name), None)
        if project:
            return project, not is_delegate
    else:
        is_delegate = False
    real = os.path.realpath(cwd or os.getcwd())
    project = next((p for p in projects if any(real.startswith(os.path.realpath(os.path.expanduser(x))) for x in p.get("paths", []))), None)
    return project, not is_delegate


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "set":
        now = datetime.now()
        on = sys.argv[3] == "on"
        write_state(sys.argv[2], on, end_of_day(now) if on else now, now, "set from terminal")
        print(f"{sys.argv[2]}: {'on' if on else 'off'}")
        return 0
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    projects = load_projects()
    if not projects:
        return 0
    project, can_toggle = resolve_project(projects, data.get("cwd") or "")
    if project is None:
        return 0
    name = project["name"]
    now = datetime.now()
    event = data.get("hook_event_name")

    if event == "UserPromptSubmit":
        prompt = (data.get("prompt") or "").strip()
        notices = []
        if can_toggle and prompt and not prompt.startswith(NON_HUMAN_PREFIXES):
            changed = apply_human_prompt(name, prompt, now)
            if changed:
                notices.append(changed)
        if not is_working(name, now):
            notices.append(OFF_NOTICE.format(name=name))
        if notices:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "\n".join(notices)}}, ensure_ascii=False))
        return 0

    if event == "PreToolUse":
        tool_name = data.get("tool_name") or ""
        if not is_working(name, now):
            reason = DENY_REASON.format(name=name)
        elif tool_name.startswith("mcp__taskboard__") and START.search(json.dumps(data.get("tool_input") or {}, ensure_ascii=False)):
            reason = DENY_START_WORD
        else:
            return 0
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
