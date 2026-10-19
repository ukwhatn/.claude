#!/usr/bin/env python3
"""発動が決まっているスキルを呼ばないまま、そのきっかけの操作をしようとしたら止める。

AGENTS.md「文章とスキル」「コミット・ブランチ・PR」が求めるスキルの発動の強制側。発動をその場の
モデルの判断に任せると、コード編集の約4割で writing-code が呼ばれていなかった。意図は AGENTS.md、
強制はこの hook。

- PreToolUse: きっかけの操作で、対応するスキルがこのセッションで（compaction の後に）呼ばれていなければ deny
- PostToolUse（Skill）: 呼ばれたスキルを状態ファイルに記録する
- SessionStart（compact）: 状態ファイルを消す。compaction でスキル本文が落ちることがあるため

subagent の中の呼び出し（agent_id がある）は止めない。入力・記録が読めないときも止めない。
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from typing import Callable

CODE_EXTENSIONS = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs", ".rb", ".java", ".kt",
    ".swift", ".php", ".cs", ".c", ".cc", ".cpp", ".h", ".hpp", ".css", ".scss", ".sass", ".less",
    ".html", ".vue", ".svelte", ".astro", ".sql", ".sh", ".bash", ".zsh", ".fish", ".lua", ".dart",
    ".ex", ".exs", ".gs", ".m", ".mm",
}
# 本番のコードを置かない場所。ここへの書き込みは writing-code の対象にしない
NON_PRODUCTION_PARTS = ("/.local/", "/.claude/projects/", "/private/tmp/", "/tmp/", "/var/folders/")

FILE_EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
OUTWARD_MCP = re.compile(
    r"^mcp__.*__("
    r"slack_send_message|slack_send_message_draft|slack_schedule_message|slack_create_canvas|slack_update_canvas"
    r"|create_draft|update_draft"
    r"|add_issue_comment|update_issue_comment|add_reply_to_pull_request_comment|add_comment_to_pending_review"
    r"|pull_request_review_write|create_pull_request|update_pull_request|issue_write"
    r"|addCommentToJiraIssue|createConfluencePage|updateConfluencePage|createConfluenceFooterComment"
    r"|createConfluenceInlineComment"
    r")$"
)
OUTWARD_GH = re.compile(r"\bgh\s+(pr\s+(create|comment|review|edit)|issue\s+(create|comment|edit))\b")
OUTWARD_GH_API = re.compile(r"\bgh\s+api\b.*\b(comments|reviews)\b.*(-f|-F|--field|--raw-field)\s+body=", re.S)
GIT_COMMIT = re.compile(r"\bgit\s+(-C\s+\S+\s+)?commit\b")
# Bash でファイルを書く先: リダイレクトと tee の直後の語
BASH_WRITE_TARGET = re.compile(r"(?:[^0-9&]>>?|^>>?|\btee\s+(?:-a\s+)?)\s*[\"']?([^\s\"'<>|;&()]+)")
# その場で書き換える sed・perl。-i の後ろの引数の並びが方言で違うので、引数のうちファイルらしい語を書き込み先とみなす
BASH_INPLACE_EDIT = re.compile(r"\b(?:sed|perl)\b[^|;&\n]*?\s(?:-[A-Za-z]*i|--in-place)[^|;&\n]*")
BASH_CD = re.compile(r"(?:^|[;&|\n]\s*)cd\s+[\"']?([^\s;&|\"']+)")
SLASH_COMMAND = re.compile(r"<command-name>/?([\w:-]+)</command-name>")


def is_production_code_path(path: str, data: dict, cwd: str | None = None) -> bool:
    absolute = os.path.normpath(os.path.join(cwd or data.get("cwd") or "", os.path.expanduser(path)))
    scratchpad = data.get("scratchpad_dir") or ""
    if scratchpad and absolute.startswith(scratchpad):
        return False
    if any(part in absolute + "/" for part in NON_PRODUCTION_PARTS):
        return False
    return os.path.splitext(absolute)[1].lower() in CODE_EXTENSIONS


def edits_production_code(tool_name: str, tool_input: dict, data: dict) -> bool:
    if tool_name in FILE_EDIT_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        return bool(path) and is_production_code_path(path, data)
    if tool_name == "Bash":
        return any(is_production_code_path(target, data, cwd) for target, cwd in bash_write_targets(tool_input, data))
    return False


def bash_write_targets(tool_input: dict, data: dict) -> list[tuple[str, str]]:
    """Bash のコマンドが書き込むファイルと、その時点の作業ディレクトリの組。

    変数を含むパスと、変数の先へ cd した後の相対パスは中身が分からないので返さない
    （実際にはほとんどが scratchpad を指している）。
    """
    command = tool_input.get("command") or ""
    found: list[tuple[int, str]] = [(match.start(), match.group(1)) for match in BASH_WRITE_TARGET.finditer(command)]
    for match in BASH_INPLACE_EDIT.finditer(command):
        found += [(match.start(), word.strip("\"'")) for word in match.group(0).split()[1:]]
    targets = []
    for position, path in found:
        cd_paths = [cd.group(1) for cd in BASH_CD.finditer(command) if cd.start() < position]
        cwd = data.get("cwd") or ""
        if cd_paths:
            if "$" in cd_paths[-1] and not os.path.isabs(path):
                continue
            cwd = os.path.join(cwd, os.path.expanduser(cd_paths[-1]))
        if "$" not in path:
            targets.append((path, cwd))
    return targets


def sends_text_outward(tool_name: str, tool_input: dict, data: dict) -> bool:
    if OUTWARD_MCP.match(tool_name):
        return True
    if tool_name != "Bash":
        return False
    command = tool_input.get("command") or ""
    return bool(OUTWARD_GH.search(command) or OUTWARD_GH_API.search(command))


def commits(tool_name: str, tool_input: dict, data: dict) -> bool:
    return tool_name == "Bash" and bool(GIT_COMMIT.search(tool_input.get("command") or ""))


# (スキル名, きっかけの判定, 止めたときに示す対象)
RULES: list[tuple[str, Callable[[str, dict, dict], bool], str]] = [
    ("writing-code", edits_production_code, "コードファイルの編集"),
    ("ukwhatn-writing", sends_text_outward,
     "人に宛てた文章を外へ出す操作。日本語なら続けて /yomiyasu、英語なら /humanizer も発動する"),
    ("commit", commits, "git commit。コミットは /commit の手順で行う"),
]


def skill_name(raw: str) -> str:
    return raw.split(":")[-1]


def state_path(session_id: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id) or "unknown"
    directory = os.path.join(tempfile.gettempdir(), "claude-skill-gate")
    os.makedirs(directory, exist_ok=True)
    return os.path.join(directory, safe + ".json")


def load_state(session_id: str) -> set[str]:
    try:
        with open(state_path(session_id), encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def save_state(session_id: str, skills: set[str]) -> None:
    path = state_path(session_id)
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as f:
        json.dump(sorted(skills), f)
    os.replace(temporary, path)


def skills_in_transcript(transcript_path: str) -> set[str]:
    """最後の compaction より後に呼ばれたスキル（Skill tool とユーザーの /<名前>）。"""
    invoked: set[str] = set()
    with open(transcript_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
                invoked = set()
                continue
            content = (entry.get("message") or {}).get("content")
            if entry.get("type") == "user":
                texts = [content] if isinstance(content, str) else [
                    block.get("text") or "" for block in content or [] if isinstance(block, dict)
                ]
                for text in texts:
                    invoked.update(skill_name(name) for name in SLASH_COMMAND.findall(text))
            elif entry.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                        invoked.add(skill_name(str((block.get("input") or {}).get("skill", ""))))
    return invoked


def deny(skill: str, note: str) -> None:
    reason = (
        f"この操作の前に Skill ツールで `{skill}` を発動する（対象: {note}）。"
        "このセッションでまだ発動していないか、compaction の後に発動し直していない"
        "（AGENTS.md「文章とスキル」「コミット・ブランチ・PR」の規則を hook で強制している）。"
        "発動したら同じ操作をやり直す。"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def gate(data: dict, session_id: str) -> None:
    tool_name = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    required = [(skill, note) for skill, triggered, note in RULES if triggered(tool_name, tool_input, data)]
    if not required:
        return
    invoked = load_state(session_id)
    if any(skill not in invoked for skill, _ in required):
        try:
            invoked |= skills_in_transcript(data.get("transcript_path") or "")
        except OSError:
            return
        save_state(session_id, invoked)
    for skill, note in required:
        if skill not in invoked:
            deny(skill, note)
            return


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    session_id = data.get("session_id") or ""
    if not session_id or data.get("agent_id"):
        return 0
    event = data.get("hook_event_name")
    if event == "SessionStart" and data.get("source") == "compact":
        try:
            os.remove(state_path(session_id))
        except OSError:
            pass
    elif event == "PostToolUse" and data.get("tool_name") == "Skill":
        skill = skill_name(str((data.get("tool_input") or {}).get("skill", "")))
        save_state(session_id, load_state(session_id) | {skill})
    elif event == "PreToolUse":
        gate(data, session_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
