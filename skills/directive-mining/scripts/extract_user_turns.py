#!/usr/bin/env python3
"""セッションログからユーザー発話だけを全件抽出し、除外の内訳を会計として出す。

ログの user ロールには、ユーザーが打った発話以外に tool_result・他セッションからの
メッセージ・サブエージェント完了通知・compaction 要約・skill 読込の注記が混ざる。
これらを理由別にカウントしてから落とすことで、「何件を見ていないか」を明示する。

使い方:
    extract_user_turns.py --out user_turns.jsonl [--since YYYY-MM-DD] [--project SUBSTR]
    extract_user_turns.py --out user_turns.jsonl --chunk-dir . --cap 3000 --chunk-chars 115000
"""
import argparse
import glob
import json
import os
import re
from collections import Counter

ROOT = os.path.expanduser("~/.claude/projects")


def classify(text):
    """ユーザー発話か、システム由来の混入かを判定する。"""
    t = text.lstrip()
    if t.startswith("<system-reminder>"):
        return "system-reminder"
    if t.startswith("Caveat:") or t.startswith("<local-command-caveat>"):
        return "caveat"
    if t.startswith("[Request interrupted"):
        return "interrupt"
    if t.startswith("API Error") or t.startswith("Error:"):
        return "error"
    if t.startswith("<user-prompt-submit-hook>"):
        return "hook"
    if t.startswith("<local-command-stdout") or t.startswith("<local-command-stderr"):
        return "local-command-output"
    if t.startswith("Another Claude session sent a message:") or t.startswith("<teammate-message"):
        return "teammate"
    if t.startswith("<task-notification>"):
        return "task-notification"
    if t.startswith("This session is being continued from a previous conversation"):
        return "compaction-summary"
    if re.match(r"^(Background agent|\d+ background agents?) .{0,80}(stopped|was stopped)", t):
        return "agent-stop-notice"
    return "user"


def collect(since=None, project=None):
    reasons = Counter()
    rows = []
    files = glob.glob(os.path.join(ROOT, "*", "*.jsonl"))
    for fp in files:
        proj = os.path.basename(os.path.dirname(fp))
        if project and project.lower() not in proj.lower():
            continue
        session = os.path.basename(fp)[:-6]
        with open(fp, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except Exception:
                    continue
                if ev.get("type") != "user":
                    continue
                ts = ev.get("timestamp", "")
                if since and ts[:10] < since:
                    continue
                msg = ev.get("message") or {}
                content = msg.get("content")
                texts, has_tool_result = [], False
                if isinstance(content, str):
                    texts.append(content)
                elif isinstance(content, list):
                    for blk in content:
                        if not isinstance(blk, dict):
                            continue
                        if blk.get("type") == "text":
                            texts.append(blk.get("text", ""))
                        elif blk.get("type") == "tool_result":
                            has_tool_result = True
                if has_tool_result and not texts:
                    reasons["tool_result"] += 1
                    continue
                raw = "\n".join(t for t in texts if t).strip()
                if not raw:
                    reasons["empty"] += 1
                    continue
                if ev.get("isMeta"):
                    reasons["isMeta"] += 1
                    continue
                body = re.sub(r"<system-reminder>.*?</system-reminder>", "", raw, flags=re.S).strip()
                if not body:
                    reasons["system-reminder-only"] += 1
                    continue
                kind = classify(body)
                if kind != "user":
                    reasons[kind] += 1
                    continue
                # スラッシュコマンドは引数（ユーザーが書いた部分）だけを残す
                if body.lstrip().startswith(("<command-message>", "<command-name>")):
                    name = re.search(r"<command-name>(.*?)</command-name>", body, re.S)
                    args = re.search(r"<command-args>(.*?)</command-args>", body, re.S)
                    args = args.group(1).strip() if args else ""
                    if not args:
                        reasons["slash-command-noarg"] += 1
                        continue
                    body = f"[slash {name.group(1).strip() if name else '?'}] {args}"
                reasons["user"] += 1
                rows.append({"ts": ts, "project": proj, "session": session,
                             "uuid": ev.get("uuid", ""), "text": body})
    rows.sort(key=lambda r: r["ts"])
    return rows, reasons, len(files)


def write_chunks(rows, chunk_dir, cap, chunk_chars):
    for p in glob.glob(os.path.join(chunk_dir, "chunk*.txt")):
        os.remove(p)
    capped = []
    for r in rows:
        t = r["text"]
        if len(t) > cap:
            t = t[:cap] + f"\n…（以下 {len(r['text']) - cap} 字省略）"
        capped.append({**r, "text": t})
    chunks, cur, cnt = [], [], 0
    for r in capped:
        cur.append(r)
        cnt += len(r["text"])
        if cnt >= chunk_chars:
            chunks.append(cur)
            cur, cnt = [], 0
    if cur:
        chunks.append(cur)
    out = []
    for i, part in enumerate(chunks, 1):
        path = os.path.join(chunk_dir, f"chunk{i}.txt")
        with open(path, "w", encoding="utf-8") as f:
            for r in part:
                f.write(f"===== [{r['ts'][:16]}] {r['project']}\n{r['text']}\n\n")
        out.append((path, len(part), sum(len(r["text"]) for r in part),
                    part[0]["ts"][:10], part[-1]["ts"][:10]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="抽出結果の JSONL 出力先")
    ap.add_argument("--since", help="この日付以降の発話のみ（YYYY-MM-DD）")
    ap.add_argument("--project", help="プロジェクトディレクトリ名の部分一致フィルタ")
    ap.add_argument("--chunk-dir", help="指定するとクラスタリング用のチャンクも書き出す")
    ap.add_argument("--cap", type=int, default=3000, help="1発話の最大文字数（超過分は打ち切る）")
    ap.add_argument("--chunk-chars", type=int, default=115000, help="1チャンクの目安文字数")
    args = ap.parse_args()

    rows, reasons, nfiles = collect(args.since, args.project)
    with open(args.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    total = sum(reasons.values())
    print("=== user イベントの内訳（除外の会計）===")
    print(f"対象セッションファイル: {nfiles}")
    for k, v in reasons.most_common():
        mark = "  <= 分析対象" if k == "user" else ""
        print(f"{v:7d}  {k}{mark}")
    print(f"{total:7d}  合計")
    if not rows:
        print("\nユーザー発話が0件。--since / --project を確認する。")
        return
    lens = [len(r["text"]) for r in rows]
    print(f"\n抽出: {len(rows)}件 / {sum(lens):,}字  median={sorted(lens)[len(lens)//2]} max={max(lens)}")
    print(f"期間: {rows[0]['ts'][:10]} -> {rows[-1]['ts'][:10]}")
    print(f"出力: {args.out}")
    if args.chunk_dir:
        print("\n=== クラスタリング用チャンク ===")
        for path, n, c, a, b in write_chunks(rows, args.chunk_dir, args.cap, args.chunk_chars):
            print(f"{path}  turns={n} chars={c} period={a}..{b}")


if __name__ == "__main__":
    main()
