#!/usr/bin/env python3
"""日本語の文から、話し言葉・和語に開いた作業動詞と、基準に合わない Markdown の表を検出する。

語の対照表は references/prose.md §2-5 が真実源で、ここには検出の正規表現だけを置く。
表とここの語が食い違うと --self-test が失敗する（片方だけ更新されるのを防ぐため）。

使い方:
  check_register.py <ファイル>...   ファイルを検査する（- で標準入力）
  check_register.py --self-test     prose.md §2-5 の表と検出の語の一致と、検出の回帰の例を確認する

終了コード: 0 該当なし、1 該当あり、2 実行できない
"""
from __future__ import annotations

import argparse
import bisect
import os
import re
import sys
from dataclasses import dataclass

PROSE_MD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "prose.md")
TABLE_HEADING = "### 2-5."

# 別の動詞の連用形に続く複合（読み直す、並べ直す、付け足す、取り消す）は書き言葉なので数えない。
# 連用形の末尾に来るかなの後は複合とみなし、助詞と「だけ」の後だけ単独の動詞とみなす。
# 「て」は、かなの後（突き合わせて直す）なら助詞、漢字の後（当て直す）なら連用形の末尾とみなす。
# ただし1字の語幹の動詞（見て・出て）の後と、指示語（これ・それ）の後は単独の動詞とみなす
COMPOUND_BEFORE = "いきぎしちにびみりえけせてねべめれげじ"
ONE_KANJI_TE = "見出寝来着似"
STANDALONE = (rf"(?:(?<![{COMPOUND_BEFORE}])|(?<=に)|(?<=[ぁ-ゖ]て)|(?<=[{ONE_KANJI_TE}]て)"
              r"|(?<=[こそあど]れ)|(?<=だけ))")
# 名詞の「直後」「足元」と区別するため、表に名指しした複合は活用語尾が続くときだけ数える
VERB_ENDING = r"(?=[すさしせそ])"

# prose.md §2-5 の表の左列（そのままの文字列）→ 検出の正規表現。
# 長い語（やり直す）を短い語（直す）より先に置く。同じ位置で重なった検出は先の語だけを残す
VOCAB_PATTERNS: dict[str, str] = {
    "やり直す、作り直す": rf"(?:やり|作り)直{VERB_ENDING}",
    "直す、書き直す": rf"書き直{VERB_ENDING}|(?<![見手立持問出言]){STANDALONE}直(?:す|さ[なれずせ]|し|せ|そう)",
    "確かめる": r"確かめ",
    "足す、書き足す": rf"書き足{VERB_ENDING}|(?<![不満補充発自具付継遠]){STANDALONE}足(?:す|さ[なれずせ]|し(?!算)|せ|そう)",
    "消す": rf"(?<![取打解抹]){STANDALONE}消(?:す|さ[なれずせ]|し|せ|そう)",
    "そろえる": r"そろえ|揃え",
    "要る、要らない": r"要(?:る|ら|り[まそ]|っ)",
    "（データを）引く": r"(?<![字割差線手綱間値取長りし])引(?:く(?!(?:継|続))|け[るばなま]|いて|いた|かな|こう)",
    "呼べる": r"呼べ(?:る|な|ま|た|ず)",
    "叩く（API を）": r"叩(?:く|け|い|か|き)",
    "拾う（通知・変更を）": r"拾(?:う|え|い|わ|っ)",
    "潰す（バグを）": r"潰(?:す|し|さ|せ)",
    "刺さる": r"刺さ",
    "畳む": r"畳(?:む|み|ん|ま|め)",
    "文頭の「なので」": r"(?:^|(?<=[。！？]))[ \t]*なので|^[ \t]*[-*][ \t]+なので",
    "〜かも": r"かも(?!しれ)(?=[。、\s!！]|$|です)",
    "〜てる、〜ちゃう、〜んです、けど": (
        rf"(?:して|って|いて|んで|えて|けて|めて|(?<=[{ONE_KANJI_TE}])て)(?:る|ます|ました|ない)"
        r"|ちゃ[うっいえお]|(?<=[るいたなう])んです|けど"
    ),
}
COMPILED = [(term, re.compile(pattern, re.M)) for term, pattern in VOCAB_PATTERNS.items()]

# 3つ以上の ` か ~ で開き、同じ字で同じ長さ以上の行で閉じるフェンス。閉じていなければ末尾まで
FENCE = re.compile(r"^[ \t]*((`|~)\2{2,})[^\n]*\n.*?(?:^[ \t]*\1\2*[ \t]*$|\Z)", re.S | re.M)
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
# この見出しで始まる表は語の対照表なので、左列の語を数えない
VOCAB_TABLE_HEADER = "| 話し言葉・和語の作業動詞 |"
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
SENTENCE_CELL_CHARS = 30


@dataclass(frozen=True)
class Finding:
    line: int
    kind: str  # "語" か "表"
    term: str
    suggestion: str
    excerpt: str


def load_vocab_table() -> dict[str, str]:
    """prose.md §2-5 の表を {左列: 右列} で返す。"""
    with open(PROSE_MD, encoding="utf-8") as f:
        lines = f.read().split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith(TABLE_HEADING))
    rows: dict[str, str] = {}
    in_table = False
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        if TABLE_ROW.match(line):
            if TABLE_SEPARATOR.match(line):
                in_table = True
                continue
            if in_table:
                cells = split_cells(line)
                rows[cells[0]] = cells[1] if len(cells) > 1 else ""
        elif in_table:
            break
    return rows


def split_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def mask_quoted(text: str) -> str:
    """引用（コードブロック・バッククォート・「」『』・> 行・URL）を、行の数と位置を保ったまま空白にする。"""
    def blank(match: re.Match[str]) -> str:
        return re.sub(r"[^\n]", " ", match.group(0))

    text = FENCE.sub(blank, text)
    text = re.sub(r"`[^`\n]*`", blank, text)
    text = re.sub(r"「[^」]*」", blank, text)
    text = re.sub(r"『[^』]*』", blank, text)
    text = re.sub(r"https?://\S+", blank, text)
    lines = []
    in_vocab_table = False
    for line in text.split("\n"):
        in_vocab_table = line.startswith(VOCAB_TABLE_HEADER) or (in_vocab_table and bool(TABLE_ROW.match(line)))
        lines.append(" " * len(line) if in_vocab_table or line.lstrip().startswith(">") else line)
    return "\n".join(lines)


def find_vocab(text: str, suggestions: dict[str, str]) -> list[Finding]:
    masked = mask_quoted(text)
    original_lines = text.split("\n")
    line_starts = [0] + [i + 1 for i, char in enumerate(masked) if char == "\n"]
    taken = bytearray(len(masked))
    findings: list[tuple[int, Finding]] = []
    for term, regex in COMPILED:
        for match in regex.finditer(masked):
            start, end = match.span()
            if any(taken[start:end]):
                continue
            taken[start:end] = b"\x01" * (end - start)
            line_no = bisect.bisect_right(line_starts, start)
            findings.append((start, Finding(line_no, "語", term, suggestions.get(term, ""),
                                            original_lines[line_no - 1].strip()[:80])))
    return [finding for _, finding in sorted(findings, key=lambda pair: pair[0])]


def find_tables(text: str) -> list[Finding]:
    """2列の表と、セルに文（句点を含むか30字を超える）が入る表を返す。コードブロック内の表は見ない。"""
    lines = mask_quoted_blocks_only(text).split("\n")
    findings = []
    i = 0
    while i < len(lines) - 1:
        if TABLE_ROW.match(lines[i]) and TABLE_SEPARATOR.match(lines[i + 1]):
            header = split_cells(lines[i])
            j = i + 2
            body = []
            while j < len(lines) and TABLE_ROW.match(lines[j]):
                body.append(split_cells(lines[j]))
                j += 1
            problems = []
            if len(header) <= 2:
                problems.append("2列")
            if any("。" in cell or len(cell) > SENTENCE_CELL_CHARS for row in body for cell in row):
                problems.append("セルに文")
            if problems:
                findings.append(Finding(i + 1, "表", "・".join(problems),
                                        "対象を親項目、属性を子項目にしたネストの箇条書き", lines[i].strip()[:80]))
            i = j
        else:
            i += 1
    return findings


def mask_quoted_blocks_only(text: str) -> str:
    return FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def check(text: str, suggestions: dict[str, str] | None = None) -> list[Finding]:
    """text の該当を行順に返す。suggestions を省くと prose.md §2-5 から読む。"""
    if suggestions is None:
        suggestions = load_vocab_table()
    return sorted(find_vocab(text, suggestions) + find_tables(text), key=lambda f: f.line)


# 検出の回帰の例: (本文, 該当の数)。複合動詞・引用・対照表を数えず、単独の用法を数えることを固定する
REGRESSION_CASES: list[tuple[str, int]] = [
    ("確認し直す。言い直さない。読み直す。並べ直す。付け足す。取り消す。絞り直す。", 0),
    ("直す。だけ直さず。必ず直す。突き合わせて直す。漢語に直す。の直し方。", 6),
    ("改変を当て直す。長引く見込み。", 0),
    ("書き直す。書き足す。足す。消す。", 4),
    ("「直す」と `消す` は引用なので数えない。", 0),
    ("これ直す。見て直す。見てる。確認してるので。", 4),
    ("下書き直後に確認する。作り直前の版。", 0),
    ("~~~text\n直す\n~~~\n````\n```\n直す\n```\n````\n「引用の続きとして\n直す」", 0),
    ("```text\n```~\n直す\n```", 0),
    (f"{VOCAB_TABLE_HEADER} 書き言葉 |\n|---|---|\n| 直す | 修正する |", 0),
]


def self_test() -> list[str]:
    table = set(load_vocab_table())
    patterns = set(VOCAB_PATTERNS)
    errors = [f"prose.md §2-5 にあり、検出の語に無い: {term}" for term in sorted(table - patterns)]
    errors += [f"検出の語にあり、prose.md §2-5 に無い: {term}" for term in sorted(patterns - table)]
    for text, expected in REGRESSION_CASES:
        found = len(find_vocab(text, {}))
        if found != expected:
            errors.append(f"回帰: {expected}件のはずが{found}件: {text[:40]}")
    return errors


def format_finding(finding: Finding, label: str = "") -> str:
    prefix = f"{label}:" if label else ""
    if finding.kind == "語":
        return f"{prefix}L{finding.line} {finding.term} → {finding.suggestion}: {finding.excerpt}"
    return f"{prefix}L{finding.line} 表（{finding.term}）→ {finding.suggestion}: {finding.excerpt}"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="話し言葉・作業動詞と表の形を検査する")
    parser.add_argument("paths", nargs="*", help="検査するファイル。- で標準入力")
    parser.add_argument("--self-test", action="store_true", help="prose.md §2-5 と検出の語の一致と回帰の例を確認する")
    args = parser.parse_args(argv)
    try:
        if args.self_test:
            errors = self_test()
            for error in errors:
                print(error)
            print("self-test: " + ("NG" if errors else "OK"))
            return 1 if errors else 0
        if not args.paths:
            parser.print_usage()
            return 2
        suggestions = load_vocab_table()
        total = 0
        for path in args.paths:
            text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
            findings = check(text, suggestions)
            total += len(findings)
            for finding in findings:
                print(format_finding(finding, "" if len(args.paths) == 1 else path))
    except (OSError, StopIteration) as error:
        print(f"実行できない: {error}", file=sys.stderr)
        return 2
    print(f"該当: {total}件", file=sys.stderr)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
