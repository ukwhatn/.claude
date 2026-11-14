#!/usr/bin/env python3
"""人に渡す日本語の文に、話し言葉・和語の作業動詞と基準に合わない表が無いかを検査する。

writing-prose の原則2と prose.md §2-5（書き言葉の語彙）、原則1（表の基準）の強制側。規則を名指しした
語だけが減り、名指ししていない語は規則の後も残り続けたため、書いた後に機械で数える。検出は
skills/writing-prose/scripts/check_register.py に任せ、ここは渡す経路だけを受け持つ。

- PreToolUse（外へ出す送信・taskboard への提示）: 本文に該当があれば1回だけ deny して該当を返す。
  同じ本文の2回目は通す（引用として残す語や、媒体のテンプレートが定める表があるため）。
  送信の判定は skill-gate.py の MCP の一覧と同じで、入力の文字列を入れ子まで読む。Bash の gh は見ない
  （シェルのコマンドから本文を取り出すとパスと cd の解釈を抱えるため。gh の投稿は skill-gate.py が
  writing-prose の発動を強制し、writing-prose の手順が check_register.py を実行する）
- Stop: 直前の返答を検査し、該当を状態ファイルに書く（返答のたびに止めると、書き直しで返答が二重になるため）
- UserPromptSubmit: 前の返答に該当があったときだけ、1行の注意を additionalContext で入れる

かなと漢字を含まない文は日本語でないとみなして検査しない。subagent の中（agent_id がある）と、
入力・本文が読めないときも何もしない。
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter

CONFIG_DIR = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
CHECKER = os.path.join(CONFIG_DIR, "skills", "writing-prose", "scripts", "check_register.py")
SKILL_GATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skill-gate.py")
PRESENT_MCP = re.compile(r"^mcp__taskboard__(doc_publish|ask_user|review_request)$")
MAX_LISTED = 15


def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # dataclass は定義の時点で sys.modules から自分の module を引くので、実行の前に登録する
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_checker():
    return load_module("check_register", CHECKER)


def is_japanese(text: str) -> bool:
    return re.search(r"[ぁ-ゟ゠-ヿ一-鿿]", text) is not None


def read_text(path: str, cwd: str) -> str:
    try:
        with open(os.path.join(cwd, os.path.expanduser(path)), encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def strings_in(value) -> list[str]:
    """入力の文字列を入れ子（ask_user の questions[].options[] など）まで集める。
    キーは整列して読む（同じ入力をキーの順序を変えて再実行しても、同じ本文として扱うため）。"""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for key, item in sorted(value.items()) if key != "path" for s in strings_in(item)]
    if isinstance(value, list):
        return [s for item in value for s in strings_in(item)]
    return []


def outgoing_text(data: dict, skill_gate) -> str | None:
    tool_name = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    if not (skill_gate.OUTWARD_MCP.match(tool_name) or PRESENT_MCP.match(tool_name)):
        return None
    texts = strings_in(tool_input)
    path = tool_input.get("path")
    if tool_name.endswith("__doc_publish") and isinstance(path, str):
        texts.append(read_text(path, data.get("cwd") or os.getcwd()))
    text = "\n\n".join(t for t in texts if t.strip())
    return text or None


def state_dir() -> str:
    directory = os.path.join(tempfile.gettempdir(), "claude-prose-check")
    os.makedirs(directory, exist_ok=True)
    return directory


def state_path(session_id: str, suffix: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)
    return os.path.join(state_dir(), f"{safe}.{suffix}")


def load_json(path: str, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def save_json(path: str, value) -> None:
    temporary = f"{path}.{os.getpid()}.tmp"
    with open(temporary, "w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False)
    os.replace(temporary, path)


def first_denial(session_id: str, text: str) -> bool:
    """この本文を初めて止めるなら印を作って True。印は本文ごとに O_EXCL で作るので、並列の呼び出しでも1回だけ True になる。"""
    directory = state_path(session_id, "denied")
    os.makedirs(directory, exist_ok=True)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    try:
        os.close(os.open(os.path.join(directory, digest), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return False
    return True


def pre_tool_use(data: dict, session_id: str) -> None:
    text = outgoing_text(data, load_module("skill_gate", SKILL_GATE))
    if not text or not is_japanese(text):
        return
    checker = load_checker()
    findings = checker.check(text)
    if not findings or not first_denial(session_id, text):
        return
    listed = "\n".join(checker.format_finding(f) for f in findings[:MAX_LISTED])
    more = f"\n（ほか {len(findings) - MAX_LISTED} 件）" if len(findings) > MAX_LISTED else ""
    reason = (
        f"本文に話し言葉・和語の作業動詞か、基準に合わない表が {len(findings)} 件ある"
        "（writing-prose の原則1・原則2、prose.md §2-5）。\n"
        f"{listed}{more}\n"
        "該当を書き言葉と箇条書きに書き換えて出し直す。字義どおりの用法・引用として残す語と、原則1が表のまま使うとした表"
        "（媒体のテンプレート、置き換えの対応の一覧）だけなら、同じ本文のまま再実行すれば通る。"
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, ensure_ascii=False))


def stop(data: dict, session_id: str) -> None:
    # Stop は止められた後の書き直しで同じターンに何度も来るので、毎回、最後の返答の結果で置き換える
    path = state_path(session_id, "last-reply.json")
    text = data.get("last_assistant_message") or ""
    findings = load_checker().check(text) if is_japanese(text) else []
    if findings:
        save_json(path, [[f.kind, f.term, f.suggestion] for f in findings])
        return
    try:
        os.remove(path)
    except OSError:
        pass


def user_prompt_submit(session_id: str) -> None:
    path = state_path(session_id, "last-reply.json")
    # 読んでから削除すると、そのあいだに Stop が保存した新しい結果まで消えるので、先に別名へ移してから読む
    taken = f"{path}.{os.getpid()}.taken"
    try:
        os.replace(path, taken)
    except OSError:
        return
    findings = load_json(taken, [])
    try:
        os.remove(taken)
    except OSError:
        pass
    if not findings:
        return
    counts = Counter((kind, term, suggestion) for kind, term, suggestion in findings)
    parts = [
        (f"{term}→{suggestion}" if kind == "語" else f"表（{term}）") + f" ×{n}"
        for (kind, term, suggestion), n in counts.most_common(8)
    ]
    context = (
        "前の返答に話し言葉・和語の作業動詞か基準に合わない表があった: " + "、".join(parts)
        + "。以降の返答は書き言葉で書き、表はセルが語か数値の3列以上の比較と、原則1が表のまま使うとした表（媒体のテンプレート、置き換えの対応の一覧）"
        "だけにする（writing-prose 原則1・2、prose.md §2-5）。"
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}},
                     ensure_ascii=False))


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    session_id = data.get("session_id") or ""
    if not session_id or data.get("agent_id"):
        return 0
    event = data.get("hook_event_name")
    if event == "UserPromptSubmit":
        user_prompt_submit(session_id)
        return 0
    # 検査器や skill-gate が読めないとき（ファイルの欠落・prose.md の表の欠落）は止めずに通す
    try:
        if event == "PreToolUse":
            pre_tool_use(data, session_id)
        elif event == "Stop":
            stop(data, session_id)
    except (OSError, ImportError, SyntaxError, StopIteration):
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
