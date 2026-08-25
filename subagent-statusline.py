#!/usr/bin/env python3
"""subagentStatusLine: agent panel の各 subagent 行を ctx バー中心の表示に差し替える。

既定表示 (name + description + elapsed / tokens / queued) は contextWindowSize と
model / effort を使っていないため、どの agent がコンテキストを食っているかが読めない。
この行は tokenCount / contextWindowSize からバーを出し、model と effort を添える。

stdin:  {"columns": <行本体の実効幅>, "tasks": [{...}], ...}
stdout: 差し替えたい行ごとに1行 {"id": ..., "content": ...}

デバッグ: SUBAGENT_STATUSLINE_DUMP=<path> を設定すると stdin をそのパスへ保存する。
"""
import json
import os
import sys
import time

BAR_WIDTH_FULL = 8
BAR_WIDTH_NARROW = 4
NAME_WIDTH = 17

# 終了した行は既定表示に任せる。tasks[] に endTime が無く所要時間を正しく出せないうえ、
# 終わった agent の ctx バーを見る用がないため
TERMINAL_STATUS = frozenset({"completed", "failed", "killed"})

MODEL_TIERS = (("opus", "opu"), ("sonnet", "son"), ("haiku", "hai"), ("fable", "fab"))
EFFORT_LEVELS = {"low": "lo", "medium": "md", "high": "hi", "xhigh": "xh", "max": "mx"}


def _rgb(h):
    return "\033[38;2;%d;%d;%dm" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


OFF = "\033[0m"
BOLD = "\033[1m"
if os.environ.get("CC_STATUSLINE_THEME") == "dark":
    DIM, FG = _rgb("8b949e"), _rgb("e6edf3")
    GRN, AMB, RED = _rgb("3fb950"), _rgb("d29922"), _rgb("f85149")
else:
    DIM, FG = _rgb("656d76"), _rgb("1f2328")
    GRN, AMB, RED = _rgb("1a7f37"), _rgb("9a6700"), _rgb("cf222e")


def ctx_color(pct):
    """statusline 側と同じ閾値 (40% 超で警告、60% 以上で危険)"""
    if pct >= 60:
        return BOLD + RED
    if pct > 40:
        return BOLD + AMB
    return GRN


def shorten_model(model):
    """resolved model ID から世代を落として3文字にする。

    Why not: 先頭3文字で切らない。ID は "claude-sonnet-5" のようにベンダー名から
    始まるため、切ると全モデルが同じ略称になる
    """
    if not isinstance(model, str):
        return ""
    lowered = model.lower()
    for needle, short in MODEL_TIERS:
        if needle in lowered:
            return short
    return lowered[:3]


def shorten_effort(effort):
    """effort は level 文字列とトークン予算の数値の両方を取り得る。"""
    if isinstance(effort, str):
        return EFFORT_LEVELS.get(effort.lower(), effort[:2].lower())
    if isinstance(effort, (int, float)) and effort > 0:
        return fmt_tokens(int(effort))
    return ""


def fmt_tokens(n):
    if not isinstance(n, (int, float)) or n < 0:
        return ""
    n = int(n)
    if n >= 1000000:
        whole, frac = divmod(n, 1000000)
        tenth = frac // 100000
        return "%d.%dM" % (whole, tenth) if tenth else "%dM" % whole
    if n >= 1000:
        return "%dk" % (n // 1000)
    return str(n)


def fmt_elapsed(ms):
    if not isinstance(ms, (int, float)) or ms < 0:
        return ""
    secs = int(ms // 1000)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    if h:
        return "%dh%02dm" % (h, m)
    if m:
        return "%dm%02ds" % (m, s)
    return "%ds" % s


def bar(pct, width):
    filled = min(width, max(0, round(pct / 100 * width)))
    return "▓" * filled + "░" * (width - filled)


def _label_of(task):
    for key in ("label", "description"):
        value = task.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _name_of(task):
    """name は名前付きで spawn された agent にしか入らない。

    type ("local_agent" 等) はカテゴリでしかなく識別に使えないので代用しない。
    """
    name = task.get("name")
    return name.strip()[:NAME_WIDTH] if isinstance(name, str) and name.strip() else ""


def _badge_of(task):
    tier = shorten_model(task.get("model"))
    effort = shorten_effort(task.get("effort"))
    if not tier and not effort:
        return ""
    # Why not: 区切りに中黒 (U+00B7) を使わない。East Asian Width が Ambiguous で
    # CJK フォントを含む環境では全角に描かれ、幅計算とずれて truncate 位置が狂う
    return tier + (":" + effort if tier and effort else effort)


def compute_widths(tasks):
    """バーの縦位置を揃えるため、その tick の全行から可変列の幅を決める。

    全行が空なら 0 を返し、その列ごと消える。
    """
    names = [_name_of(t) for t in tasks]
    badges = [_badge_of(t) for t in tasks]
    return max([len(n) for n in names] + [0]), max([len(b) for b in badges] + [0])


def render_row(task, columns, now_ms, name_width, badge_width):
    """1 task 分の content を組み立てる。差し替えない場合は None。"""
    if task.get("status") in TERMINAL_STATUS:
        return None

    name = _name_of(task)

    tokens = task.get("tokenCount")
    window = task.get("contextWindowSize")
    has_pct = (isinstance(tokens, (int, float)) and isinstance(window, (int, float))
               and window > 0)
    pct = int(tokens / window * 100) if has_pct else 0

    show_tokens = columns >= 80
    bar_width = BAR_WIDTH_FULL if columns >= 68 else BAR_WIDTH_NARROW
    show_elapsed = columns >= 58
    show_label = columns >= 48

    parts = []
    if name_width:
        parts.append("%s%-*s%s" % (FG, name_width, name, OFF))
    if badge_width:
        parts.append("%s%-*s%s" % (DIM, badge_width, _badge_of(task), OFF))

    if has_pct:
        col = ctx_color(pct)
        parts.append("%s%s %3d%%%s" % (col, bar(pct, bar_width), pct, OFF))
        if show_tokens:
            parts.append("%s%5s/%s%s" % (DIM, fmt_tokens(tokens), fmt_tokens(window), OFF))
    elif isinstance(tokens, (int, float)) and tokens > 0:
        parts.append("%s%s tokens%s" % (DIM, fmt_tokens(tokens), OFF))

    # Why not: paused でも経過時間を出さない。停止していた時間 (totalPausedMs) が
    # tasks[] に来ないため、実際の稼働時間と乖離した値になる
    if show_elapsed and task.get("status") != "paused":
        started = task.get("startTime")
        if isinstance(started, (int, float)) and started > 0:
            elapsed = fmt_elapsed(now_ms - started)
            if elapsed:
                parts.append("%s%6s%s" % (DIM, elapsed, OFF))

    if show_label:
        label = _label_of(task)
        if label:
            parts.append("%s%s%s" % (FG, label, OFF))

    # Why not: 末尾を OFF で閉じないまま返さない。Claude Code は行をまたいで SGR を
    # 引き継ぐため、閉じ忘れると次の行へ色が漏れる
    return "  ".join(parts) + OFF


def main():
    raw = sys.stdin.read()
    dump_path = os.environ.get("SUBAGENT_STATUSLINE_DUMP")
    if dump_path:
        try:
            with open(dump_path, "w") as fh:
                fh.write(raw)
        except OSError:
            pass

    try:
        payload = json.loads(raw)
    except ValueError:
        return 0
    if not isinstance(payload, dict):
        return 0

    columns = payload.get("columns")
    if not isinstance(columns, int) or columns <= 0:
        columns = 999

    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        return 0

    renderable = [t for t in tasks
                  if isinstance(t, dict)
                  and isinstance(t.get("id"), str) and t.get("id")
                  and t.get("status") not in TERMINAL_STATUS]
    name_width, badge_width = compute_widths(renderable)

    now_ms = time.time() * 1000
    out = []
    for task in renderable:
        try:
            content = render_row(task, columns, now_ms, name_width, badge_width)
        except Exception:
            # 1 行の失敗で他の行まで落とさない。その行は既定表示に戻る
            continue
        if content is None:
            continue
        out.append(json.dumps({"id": task["id"], "content": content}))

    if out:
        sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
