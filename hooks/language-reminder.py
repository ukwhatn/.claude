#!/usr/bin/env python3
"""UserPromptSubmit / PostToolUse / Stop hook: settings.json の language を再提示し、英語の返答を差し戻す。

Claude Code は言語指定をセッション開始時と compaction 直後にしか差し込まないため、
長い自律実行や英語の要約・ツール結果・ハーネスの通知が続くと応答が英語に流れる。直近に指定を置いて防ぐ。

- UserPromptSubmit: 毎回出す。ツール呼び出しの数え直しもここで始める
- PostToolUse: 1ターンが長いと UserPromptSubmit の指定が遠くなるので、ツール呼び出し INTERVAL 回ごとに出す
  （毎回だと長いターンで同じ文が数十回文脈に積まれる）
- Stop: language が日本語のとき、このターンの応答の段落（transcript の人の発言より後の文と last_assistant_message）に、
  英字が日本語の字の RATIO 倍を超え、MIN_LATIN 字以上ある段落があれば 1 回だけ差し戻して日本語で書き直させる
  （再提示だけでは、英語のツール結果や英語のスキル本文が続いたターンの返答が英語のまま出た）。
  コードの塊・行内のコード・URL・パス・HTML コメントは数えない。差し戻した後の Stop（stop_hook_active）では差し戻さない
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile

INTERVAL = 10
MIN_LATIN = 40
RATIO = 3

FENCE = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.S | re.M)
STRIP = [
    re.compile(r"`[^`\n]*`"),
    re.compile(r"<!--.*?-->", re.S),
    re.compile(r"https?://\S+"),
    re.compile(r"\]\([^)]*\)"),
    re.compile(r"(?:~|\.{0,2})/[\w./@+-]+"),
]
LATIN = re.compile(r"[A-Za-z]")
JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")


def is_japanese(language: str | None) -> bool:
    return bool(language) and (language.lower().startswith("ja") or "日本" in language)


def english_paragraphs(text: str) -> list[str]:
    """英字が日本語の字の RATIO 倍を超え、MIN_LATIN 字以上ある段落（コード・URL・パスを除いて数える）"""
    text = FENCE.sub("", text)
    for pattern in STRIP:
        text = pattern.sub(" ", text)
    found = []
    for paragraph in re.split(r"\n\s*\n", text):
        latin = len(LATIN.findall(paragraph))
        if latin >= MIN_LATIN and latin > RATIO * len(JAPANESE.findall(paragraph)):
            found.append(paragraph.strip())
    return found


def turn_texts(transcript_path: str | None) -> list[str]:
    """transcript の最後の人の発言より後の、応答の文の塊"""
    if not transcript_path:
        return []
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()[-2000:]
    except OSError:
        return []
    texts: list[str] = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        content = (entry.get("message") or {}).get("content")
        if entry.get("type") == "user":
            if isinstance(content, str) or (isinstance(content, list) and any(b.get("type") == "text" for b in content if isinstance(b, dict))):
                break
            continue
        if entry.get("type") == "assistant" and isinstance(content, list):
            texts.extend(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return texts


def stop_gate(payload: dict) -> None:
    if payload.get("stop_hook_active") or payload.get("agent_id") or not is_japanese(load_language()):
        return
    texts = turn_texts(payload.get("transcript_path"))
    last = payload.get("last_assistant_message") or ""
    if last and last not in texts:
        texts.insert(0, last)
    found = [p for text in texts for p in english_paragraphs(text)]
    if not found:
        return
    head = found[0][:80].replace("\n", " ")
    reason = (
        f"このターンの返答に英語で書いた段落が {len(found)} 個ある（「{head}…」）。"
        "応答・報告は日本語で書く決まりなので、英語で書いた部分の内容を日本語で書き直して、もう一度返答する"
        "（コード・識別子・引用は原文のまま）。"
    )
    json.dump({"decision": "block", "reason": reason}, sys.stdout, ensure_ascii=False)


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
    if event == "Stop":
        stop_gate(payload)
        return
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
