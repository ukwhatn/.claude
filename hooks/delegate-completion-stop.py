#!/usr/bin/env python3
"""Stop hook（委譲先の pane 専用）: lead へ連絡せずに応答を終えようとしたら1回だけ止める。

bin/herdr-delegate.sh が claude を起動するときに --settings で足す。user-level の settings には
登録しない（lead・普段のセッションで発火させないため）。

lead は委譲先が応答を終えたことしか検知できず、完了か途中の待機かは委譲先からの連絡でしか
分からない。最後の入力以降に lead 宛の送信が無ければ停止を block して送らせる。

usage: delegate-completion-stop.py [--lead-name NAME] [--lead-pane PANE_ID]
"""
import argparse
import json
import sys


def is_input(entry: dict) -> bool:
    """委譲先への新しい入力か（ツール結果を除く user エントリと、turn の途中に届いたメッセージ）。"""
    if entry.get("type") == "attachment":
        return (entry.get("attachment") or {}).get("type") == "queued_command"
    if entry.get("type") != "user":
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return any(b.get("type") != "tool_result" for b in content if isinstance(b, dict))
    return False


def is_report(block: dict, lead_name: str, lead_pane: str) -> bool:
    if block.get("type") != "tool_use":
        return False
    tool_input = block.get("input") or {}
    if block.get("name") == "SendMessage":
        return bool(lead_name) and tool_input.get("to") == lead_name
    if block.get("name") == "Bash":
        command = tool_input.get("command") or ""
        return bool(lead_pane) and "herdr agent prompt" in command and lead_pane in command
    return False


def reported_since_last_input(transcript_path: str, lead_name: str, lead_pane: str) -> bool:
    reported = False
    with open(transcript_path, encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if is_input(entry):
                reported = False
                continue
            if entry.get("type") != "assistant":
                continue
            content = (entry.get("message") or {}).get("content")
            if isinstance(content, list) and any(
                isinstance(b, dict) and is_report(b, lead_name, lead_pane) for b in content
            ):
                reported = True
    return reported


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lead-name", default="")
    parser.add_argument("--lead-pane", default="")
    args = parser.parse_args()
    if not args.lead_name and not args.lead_pane:
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    # block 後の再停止は通す。止め続けると、送れない状況で委譲先が終われなくなる
    if data.get("stop_hook_active"):
        return 0
    transcript_path = data.get("transcript_path")
    if not transcript_path:
        return 0
    try:
        if reported_since_last_input(transcript_path, args.lead_name, args.lead_pane):
            return 0
    except OSError:
        return 0
    # herdr agent prompt は lead の画面にユーザーの入力として入り、送り主が見分けにくいので後回しにする
    pane_route = f"Bash で `herdr agent prompt \"{args.lead_pane}\" '<本文>'`"
    if args.lead_name:
        route = f'SendMessage ツールで `to: "{args.lead_name}"` に送って'
        if args.lead_pane:
            route += f"（SendMessage が使えないときだけ {pane_route} で送って）"
    else:
        route = pane_route + " で送って"
    reason = (
        "lead への連絡がまだです。" + route + "から応答を終えてください。"
        "作業が終わったなら成果物のパスと要点を数行、途中で止まるなら何を待っているか"
        "（バックグラウンドのコマンド・lead の返答など）を送ります。"
    )
    print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
