#!/usr/bin/env python3
"""taskherd のボードを Claude Code のセッション状態に追随させる hook。

呼び出し方（settings.json から）:
  stop    Stop イベント。セッションに紐づくタスクの列を PR の実状態へ前進させる
  prompt  UserPromptSubmit イベント。紐づくタスクが無いまま実装が進んでいたら起票を促す

どちらのモードも、判断材料が揃わなければ黙って exit 0 する（hook でターンを壊さない）。
列を戻す方向には動かさない。終端列（kind = terminal）に居るタスクは触らない。
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import time

REFRESH_INTERVAL_SEC = 180  # PR の live 状態を取り直す最小間隔


def run(args, timeout=20):
    """コマンドを実行して (exit_code, stdout) を返す。失敗は例外にしない。"""
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout
    except Exception:
        return 1, ""


def run_json(args, timeout=20):
    code, out = run(args, timeout=timeout)
    if code != 0 or not out.strip():
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def state_dir():
    d = os.path.expanduser("~/.local/state/taskherd/claude-hook")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        return None
    return d


def column_order():
    """config.toml の [[columns]] を定義順に返す。(順序リスト, 終端列の集合)"""
    paths = run_json(["taskherd", "config", "path", "--json"])
    if not paths or not paths.get("config"):
        return [], set()
    try:
        with open(paths["config"], encoding="utf-8") as f:
            body = f.read()
    except Exception:
        return [], set()

    order, terminal, current = [], set(), None
    for line in body.splitlines():
        line = line.strip()
        if line == "[[columns]]":
            current = None
            continue
        m = re.match(r'^id\s*=\s*"([^"]+)"', line)
        if m:
            current = m.group(1)
            order.append(current)
            continue
        m = re.match(r'^kind\s*=\s*"([^"]+)"', line)
        if m and current and m.group(1) == "terminal":
            terminal.add(current)
    return order, terminal


def linked_task(session_id):
    """このセッションに紐づくタスクを1件返す（無ければ None）。"""
    if not session_id:
        return None
    data = run_json(["taskherd", "list", "--all", "--json"])
    if not data:
        return None
    for task in data.get("tasks") or []:
        for s in task.get("sessions") or []:
            if s.get("session_id") == session_id:
                return task
    return None


def desired_column(task_id, current, order, terminal):
    """PR の live 状態から進めたい列を返す（進めないなら None）。"""
    if current in terminal:
        return None

    # 期限を切って refresh する（毎ターン叩くと gh 呼び出しが積む）
    d = state_dir()
    marker = os.path.join(d, "refresh-%s" % task_id) if d else None
    fresh_enough = False
    if marker and os.path.exists(marker):
        fresh_enough = (time.time() - os.path.getmtime(marker)) < REFRESH_INTERVAL_SEC
    if not fresh_enough:
        run(["taskherd", "refresh", str(task_id), "--json"], timeout=25)
        if marker:
            try:
                open(marker, "w").close()
            except Exception:
                pass

    shown = run_json(["taskherd", "show", str(task_id), "--json"])
    if not shown:
        return None

    has_open_ready = False
    has_merged = False
    has_open = False
    for entry in (shown.get("link_states") or {}).values():
        if entry.get("Kind") != "github_pr":
            continue
        gh = entry.get("GitHub") or {}
        state = (gh.get("state") or "").upper()
        if state == "OPEN":
            has_open = True
            if not gh.get("is_draft"):
                has_open_ready = True
        elif state == "MERGED":
            has_merged = True

    target = None
    if has_open_ready:
        target = "review"
    if has_merged and not has_open:
        target = "deploying"
    if not target or target not in order or current not in order:
        return None
    # 前進方向のみ
    return target if order.index(target) > order.index(current) else None


def mode_stop(payload):
    task = linked_task(payload.get("session_id"))
    if not task:
        return
    order, terminal = column_order()
    if not order:
        return
    target = desired_column(task.get("id"), task.get("status"), order, terminal)
    if not target:
        return
    moved = run_json(["taskherd", "move", str(task["id"]), target, "--json"])
    if moved and (moved.get("task") or {}).get("status") == target:
        print("taskherd: task %s を %s へ移動しました（PR の状態に追随）" % (task["id"], target))


def git(args):
    code, out = run(["git"] + args, timeout=10)
    return out.strip() if code == 0 else ""


def mode_prompt(payload):
    session_id = payload.get("session_id") or ""
    if linked_task(session_id):
        return
    if not git(["rev-parse", "--is-inside-work-tree"]):
        return

    branch = git(["rev-parse", "--abbrev-ref", "HEAD"])
    if not branch or branch == "HEAD":
        return
    base = git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"]) or "origin/main"
    if branch == base.split("/", 1)[-1]:
        return
    ahead = git(["rev-list", "--count", "%s..HEAD" % base])
    if not ahead.isdigit() or int(ahead) < 1:
        return

    # 同じセッション・同じブランチでは1回しか促さない
    d = state_dir()
    if d:
        key = hashlib.sha256(("%s|%s" % (session_id, branch)).encode()).hexdigest()[:16]
        marker = os.path.join(d, "nudge-%s" % key)
        if os.path.exists(marker):
            return
        try:
            open(marker, "w").close()
        except Exception:
            pass

    msg = (
        "taskherd: このセッションに紐づくタスクがありません（ブランチ `%s` に %s commit）。"
        "作業内容が固まっているなら taskherd スキルの規約で起票し、"
        "`taskherd session link <id> --current --json` で紐づけてください。"
        "起票しない判断をしたならこの通知は無視してよい。" % (branch, ahead)
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": msg,
                }
            }
        )
    )


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    raw = ""
    try:
        raw = sys.stdin.read()
    except Exception:
        pass
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    # taskherd が無い環境では何もしない
    if not any(
        os.path.exists(os.path.join(p, "taskherd"))
        for p in os.environ.get("PATH", "").split(os.pathsep)
        if p
    ):
        return

    if mode == "stop":
        mode_stop(payload)
    elif mode == "prompt":
        mode_prompt(payload)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
