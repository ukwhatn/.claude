#!/usr/bin/env python3
"""抽出済みユーザー発話に対する決定論的な頻度集計。

LLM に読ませるクラスタリングは網羅を保証しないため、こちらで機械的に数えて突き合わせる。
連投・複数セッションへの一括送信を畳んだ「インシデント数」を併記する（件数だけだと
同一文言の連投で頻度が水増しされる）。

使い方:
    count_directives.py user_turns.jsonl
    count_directives.py user_turns.jsonl --patterns my_patterns.json --min-repeat 2
"""
import argparse
import json
import re
from collections import Counter

# 観測から得た既定パターン。PJ 固有の語は --patterns で差し替える。
DEFAULT_PATTERNS = {
    "否定・訂正": r"(違う|ちがう|じゃなくて|ではなく|そうじゃ|間違っ|誤り)",
    "禁止・不要": r"(やめて|不要|いらない|いりません|しないで|するな|禁止)",
    "既出指示の再掲": r"(さっき|前に|何度も|毎回|いつも|再度|言ったよ|指示した)",
    "勝手・無断": r"(勝手に|無断|独断|承認して(ない|いない)|頼んで(ない|いない))",
    "抜け漏れ": r"(漏れ|抜け|忘れ|見落と|できてない|やってない)",
    "委譲・モデル指定": r"(委譲|subagent|サブエージェント|オーケストレート|opus|sonnet|fable)",
    "報告の型指定": r"(レポートして|報告して|まとめて|状況(を)?教えて|整理して)",
    "簡潔さ・構造化": r"(長い|冗長|箇条書き|構造化|短く|ネスト)",
    "commit・push": r"(コミットして|commitして|pushして|push して)",
    "PR操作": r"(PR(を)?(出|作)|approve|マージ|merge)",
    "CI・conflict": r"(CI ?(failed|落ち|通し|確認)|conflict|コンフリクト)",
    "worktree": r"(worktree|ワークツリー)",
    "外部レビュー": r"(agent review|codex|cursor|外部レビュー|out of credit)",
    "過去参照": r"(findmem|memdir|メモリディレクトリ|過去の)",
    "経緯収集": r"(スレッド|経緯|confluence|jira|コメント).{0,40}(読|集め|探索)",
    "完成度への要求": r"(完成形|要求ライン|考え抜|作り直|再考|やり直し)",
}


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def fold_incidents(hits):
    """直前の発話と先頭80字が一致するものを同一インシデントとして畳む。"""
    out, prev = [], None
    for h in hits:
        key = re.sub(r"\s+", "", h["text"])[:80]
        if key != prev:
            out.append(h)
        prev = key
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("turns", help="extract_user_turns.py の出力 JSONL")
    ap.add_argument("--patterns", help="パターン定義の JSON（名前 -> 正規表現）")
    ap.add_argument("--min-repeat", type=int, default=3, help="反復文言として表示する最小回数")
    ap.add_argument("--short-max", type=int, default=40, help="短い発話とみなす文字数")
    ap.add_argument("--examples", type=int, default=4, help="各パターンで表示する例の数")
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.turns, encoding="utf-8")]
    patterns = DEFAULT_PATTERNS
    if args.patterns:
        patterns = json.load(open(args.patterns, encoding="utf-8"))

    print(f"対象: {len(rows)}件 / {sum(len(r['text']) for r in rows):,}字\n")

    # 1) 完全一致で反復されている短い発話（毎回言わせている定型指示が出る）
    short = [norm(r["text"]) for r in rows if len(norm(r["text"])) <= args.short_max]
    print(f"=== 同一文言の反復（{args.short_max}字以下・{args.min_repeat}回以上）===")
    print(f"短い発話 {len(short)}件 / 全{len(rows)}件")
    for text, n in Counter(short).most_common():
        if n >= args.min_repeat:
            print(f"{n:5d}  {text}")

    # 2) パターン別の件数とインシデント数
    print("\n=== パターン別（件数 / インシデント数）===")
    for name, pat in patterns.items():
        hits = [r for r in rows if re.search(pat, r["text"], re.I)]
        uniq = fold_incidents(hits)
        print(f"\n{len(hits):4d}件 / {len(uniq):4d}インシデント  {name}")
        for h in uniq[:args.examples]:
            print(f"        {h['ts'][:10]} {norm(h['text'])[:100]}")

    # 3) 期間分布（後半に集中しているテーマは既存ルールで未カバーの可能性が高い）
    print("\n=== 月別の発話数 ===")
    for month, n in sorted(Counter(r["ts"][:7] for r in rows).items()):
        print(f"  {month}  {n}")


if __name__ == "__main__":
    main()
