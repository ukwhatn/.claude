#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Claude Code セッションログ (~/.claude/projects/**/*.jsonl) を集計分析する。

skillの発火回数・toolの使用頻度・ユーザーの軌道修正シグナル(中断/権限拒否/AskUserQuestionでの
Other選択)・compaction頻度などをJSONLをストリーム処理で集計し、JSONレポートを出力する。

Usage:
    uv run analyze_claude_sessions.py [--projects-dir DIR] [--since YYYY-MM-DD]
                                       [--project SUBSTR] [--json-out PATH]
                                       [--top-n N] [--skills-dir DIR ...]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ASKQ_ANSWER_RE = re.compile(r'"((?:[^"\\]|\\.)*)"="((?:[^"\\]|\\.)*)"')


def unescape(s: str) -> str:
    return s.replace('\\"', '"').replace("\\\\", "\\")


def iter_jsonl(path: Path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def analyze_session(path: Path, stats: dict, is_subagent: bool) -> None:
    project = path.parts[-4] if is_subagent else path.parts[-2]
    session_id = path.stem

    tool_use_names: dict[str, str] = {}  # tool_use_id -> name
    tool_use_inputs: dict[str, dict] = {}  # tool_use_id -> input (for AskUserQuestion)
    last_tool_name: str | None = None
    first_ts: str | None = None
    last_ts: str | None = None
    human_turns = 0
    assistant_turns = 0
    permission_modes = set()

    stats["by_project"][project]["sessions"] += 1
    if is_subagent:
        stats["meta"]["subagent_files"] += 1
    else:
        stats["meta"]["main_files"] += 1

    for d in iter_jsonl(path):
        ts = d.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts

        dtype = d.get("type")

        if dtype == "permission-mode":
            permission_modes.add(d.get("permissionMode"))

        elif dtype == "user":
            msg = d.get("message", {})
            content = msg.get("content")
            if isinstance(content, str):
                if d.get("origin", {}).get("kind") == "human" or not is_subagent:
                    human_turns += 1
                    stats["meta"]["human_turns"] += 1
                    if "[Request interrupted by user" in content:
                        stats["interrupt"]["total"] += 1
                        stats["interrupt"]["by_last_tool"][last_tool_name or "(none)"] += 1
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text" and "[Request interrupted by user" in str(item.get("text", "")):
                        stats["interrupt"]["total"] += 1
                        stats["interrupt"]["by_last_tool"][last_tool_name or "(none)"] += 1
                    if item.get("type") == "tool_result":
                        tid = item.get("tool_use_id")
                        tname = tool_use_names.get(tid, "(unknown)")
                        raw_content = item.get("content")
                        text = raw_content if isinstance(raw_content, str) else json.dumps(raw_content, ensure_ascii=False)
                        if item.get("is_error"):
                            stats["errors"]["total"] += 1
                            stats["errors"]["by_tool"][tname] += 1
                            if "has been denied" in text:
                                stats["denials"]["total"] += 1
                                stats["denials"]["by_tool"][tname] += 1
                        if tname == "AskUserQuestion" and "Your questions have been answered" in text:
                            stats["askq"]["answered"] += 1
                            q_input = tool_use_inputs.get(tid, {})
                            questions = q_input.get("questions", [])
                            option_labels_by_q = {
                                q.get("question", ""): {o.get("label") for o in q.get("options", [])}
                                for q in questions
                                if isinstance(q, dict)
                            }
                            for qtext, atext in ASKQ_ANSWER_RE.findall(text):
                                qtext = unescape(qtext)
                                atext = unescape(atext)
                                stats["askq"]["qa_pairs"] += 1
                                labels = option_labels_by_q.get(qtext)
                                if labels and atext not in labels:
                                    stats["askq"]["custom_other_answers"] += 1

        elif dtype == "assistant":
            assistant_turns += 1
            stats["meta"]["assistant_turns"] += 1
            for c in d.get("message", {}).get("content", []):
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                name = c.get("name", "(unknown)")
                tid = c.get("id")
                if tid:
                    tool_use_names[tid] = name
                    tool_use_inputs[tid] = c.get("input", {}) if isinstance(c.get("input"), dict) else {}
                last_tool_name = name
                stats["tools"]["all"][name] += 1
                if is_subagent:
                    stats["tools"]["subagent"][name] += 1
                else:
                    stats["tools"]["main"][name] += 1
                if name == "Skill":
                    inp = c.get("input", {}) if isinstance(c.get("input"), dict) else {}
                    skill = inp.get("skill", "(unknown)")
                    stats["skills"]["counts"][skill] += 1
                    stats["skills"]["by_project"][skill][project] += 1
                    if not is_subagent:
                        stats["skills"]["main_counts"][skill] += 1
                elif name == "Agent":
                    inp = c.get("input", {}) if isinstance(c.get("input"), dict) else {}
                    atype = inp.get("subagent_type", "(unspecified)")
                    stats["agent_tool"]["by_subagent_type"][atype] += 1

        elif dtype == "system":
            subtype = d.get("subtype")
            stats["system_events"][subtype] += 1
            if subtype == "compact_boundary":
                meta = d.get("compactMetadata", {})
                pre = meta.get("preTokens")
                post = meta.get("postTokens")
                if isinstance(pre, int) and isinstance(post, int):
                    stats["compaction"]["events"] += 1
                    stats["compaction"]["pre_tokens_total"] += pre
                    stats["compaction"]["post_tokens_total"] += post

        elif dtype == "ai-title":
            title = d.get("aiTitle")
            if title:
                stats["titles"][project].add(title)

    stats["meta"]["sessions_seen"] += 0 if is_subagent else 1
    if not is_subagent and first_ts and last_ts:
        stats["timeline"].append({"project": project, "session": session_id, "start": first_ts, "end": last_ts})
    for pm in permission_modes:
        stats["permission_modes"][pm or "(none)"] += 1


def new_stats() -> dict:
    return {
        "meta": {
            "main_files": 0,
            "subagent_files": 0,
            "sessions_seen": 0,
            "human_turns": 0,
            "assistant_turns": 0,
        },
        "by_project": defaultdict(lambda: {"sessions": 0}),
        "skills": {
            "counts": Counter(),
            "main_counts": Counter(),
            "by_project": defaultdict(Counter),
        },
        "tools": {"all": Counter(), "main": Counter(), "subagent": Counter()},
        "agent_tool": {"by_subagent_type": Counter()},
        "interrupt": {"total": 0, "by_last_tool": Counter()},
        "denials": {"total": 0, "by_tool": Counter()},
        "errors": {"total": 0, "by_tool": Counter()},
        "askq": {"answered": 0, "qa_pairs": 0, "custom_other_answers": 0},
        "compaction": {"events": 0, "pre_tokens_total": 0, "post_tokens_total": 0},
        "system_events": Counter(),
        "permission_modes": Counter(),
        "titles": defaultdict(set),
        "timeline": [],
    }


def to_jsonable(obj):
    if isinstance(obj, Counter):
        return dict(obj.most_common())
    if isinstance(obj, defaultdict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return sorted(obj)
    if isinstance(obj, list):
        return [to_jsonable(v) for v in obj]
    return obj


def print_report(stats: dict, top_n: int) -> None:
    m = stats["meta"]
    print("=" * 60)
    print("Claude Code セッション分析レポート")
    print("=" * 60)
    print(f"メインセッションファイル数: {m['main_files']}")
    print(f"サブエージェントログファイル数: {m['subagent_files']}")
    print(f"人間の発話ターン数: {m['human_turns']}")
    print(f"assistantターン数: {m['assistant_turns']}")
    print()

    print("--- プロジェクト別セッション数 (上位) ---")
    for proj, d in sorted(stats["by_project"].items(), key=lambda x: -x[1]["sessions"])[:top_n]:
        print(f"  {d['sessions']:>4}  {proj}")
    print()

    print("--- Skill発火回数 (メインセッションのみ) ---")
    for skill, cnt in Counter(stats["skills"]["main_counts"]).most_common(top_n):
        print(f"  {cnt:>4}  {skill}")
    print()

    print("--- Tool使用頻度 (メインセッションのみ) ---")
    for tool, cnt in Counter(stats["tools"]["main"]).most_common(top_n):
        print(f"  {cnt:>4}  {tool}")
    print()

    print("--- Agent tool: subagent_type別 ---")
    for t, cnt in Counter(stats["agent_tool"]["by_subagent_type"]).most_common(top_n):
        print(f"  {cnt:>4}  {t}")
    print()

    print("--- ユーザー軌道修正シグナル ---")
    print(f"  中断([Request interrupted by user]): {stats['interrupt']['total']}件")
    for tool, cnt in Counter(stats["interrupt"]["by_last_tool"]).most_common(5):
        print(f"      直前のtool={tool}: {cnt}件")
    print(f"  権限拒否 (has been denied): {stats['denials']['total']}件")
    for tool, cnt in Counter(stats["denials"]["by_tool"]).most_common(5):
        print(f"      tool={tool}: {cnt}件")
    print(f"  tool_result エラー総数: {stats['errors']['total']}件")
    print()

    print("--- AskUserQuestion ---")
    aq = stats["askq"]
    print(f"  質問セット回答数: {aq['answered']}")
    print(f"  Q&Aペア総数: {aq['qa_pairs']}")
    print(f"  Other(自由記述)回答数: {aq['custom_other_answers']}")
    if aq["qa_pairs"]:
        rate = aq["custom_other_answers"] / aq["qa_pairs"] * 100
        print(f"  Other選択率: {rate:.1f}%")
    print()

    print("--- Compaction ---")
    c = stats["compaction"]
    print(f"  発生回数: {c['events']}")
    if c["events"]:
        avg_pre = c["pre_tokens_total"] / c["events"]
        avg_post = c["post_tokens_total"] / c["events"]
        print(f"  平均 preTokens: {avg_pre:.0f} / 平均 postTokens: {avg_post:.0f}")
    print()

    print("--- system イベント種別 ---")
    for st, cnt in Counter(stats["system_events"]).most_common(top_n):
        print(f"  {cnt:>4}  {st}")
    print()

    print("--- permission mode 利用状況 ---")
    for pm, cnt in Counter(stats["permission_modes"]).most_common():
        print(f"  {cnt:>4}  {pm}")


def print_skill_inventory(stats: dict, skills_dirs: list[Path]) -> None:
    fired = set(stats["skills"]["counts"].keys())
    defined = []
    for d in skills_dirs:
        if not d.is_dir():
            continue
        defined.extend(sorted(p.name for p in d.iterdir() if p.is_dir()))
    if not defined:
        return
    never_fired = [s for s in defined if s not in fired]
    print()
    print(f"--- Skill棚卸し (定義={len(defined)}, 分析対象期間内で未発火={len(never_fired)}) ---")
    for s in never_fired:
        print(f"  (未発火)  {s}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projects-dir", default=str(Path.home() / ".claude" / "projects"))
    ap.add_argument("--json-out", default=None, help="集計結果をJSONで書き出すパス")
    ap.add_argument("--top-n", type=int, default=15)
    ap.add_argument("--include-subagents", action="store_true", default=True)
    ap.add_argument("--since", default=None, help="YYYY-MM-DD。このmtime以降に更新されたファイルのみ対象")
    ap.add_argument("--project", default=None, help="プロジェクトディレクトリ名の部分一致フィルタ（大小無視）")
    ap.add_argument(
        "--skills-dir",
        action="append",
        default=None,
        help="定義済みskill一覧との突合(未発火skill棚卸し)。複数指定可。既定: ~/.claude/skills",
    )
    args = ap.parse_args()

    root = Path(args.projects_dir)
    main_files = sorted(root.glob("*/*.jsonl"))
    subagent_files = sorted(root.glob("*/*/subagents/*.jsonl")) if args.include_subagents else []

    since_dt = None
    if args.since:
        since_dt = datetime.combine(date.fromisoformat(args.since), datetime.min.time())

    def project_name(f: Path, is_subagent: bool) -> str:
        return f.parts[-4] if is_subagent else f.parts[-2]

    def filter_files(files: list[Path], is_subagent: bool) -> list[Path]:
        out = []
        for f in files:
            if since_dt and datetime.fromtimestamp(f.stat().st_mtime) < since_dt:
                continue
            if args.project and args.project.lower() not in project_name(f, is_subagent).lower():
                continue
            out.append(f)
        return out

    main_files = filter_files(main_files, is_subagent=False)
    subagent_files = filter_files(subagent_files, is_subagent=True)

    stats = new_stats()
    for f in main_files:
        analyze_session(f, stats, is_subagent=False)
    for f in subagent_files:
        analyze_session(f, stats, is_subagent=True)

    print_report(stats, args.top_n)

    skills_dirs = [Path(p) for p in args.skills_dir] if args.skills_dir else [Path.home() / ".claude" / "skills"]
    print_skill_inventory(stats, skills_dirs)

    if args.json_out:
        out_path = Path(args.json_out)
        out_path.write_text(json.dumps(to_jsonable(stats), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON詳細を書き出しました: {out_path}")


if __name__ == "__main__":
    main()
