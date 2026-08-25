#!/usr/bin/env python3
"""codex の月次クレジット枠の消費率をキャッシュに書き出す。

statusline から数秒間隔で呼べる形にするための前段。app-server への照会は
1.5 秒前後かかるため statusline から直接は叩けず、このスクリプトが
バックグラウンドでキャッシュを更新し、statusline はキャッシュだけを読む。

使い方:
    codex-usage.py --refresh    照会してキャッシュを更新する
    codex-usage.py --show       キャッシュを読んで1行で出す（デバッグ用）
"""
import json
import os
import select
import subprocess
import sys
import time

CACHE_DIR = os.path.expanduser("~/.cache/claude-statusline")
CACHE_PATH = os.path.join(CACHE_DIR, "codex-usage.json")
LOCK_PATH = os.path.join(CACHE_DIR, "codex-usage.lock")

LOCK_STALE_SEC = 120
RPC_TIMEOUT_SEC = 10


def query_rate_limits():
    """codex app-server に account/rateLimits/read を投げて rateLimits を返す。

    モデル推論は発生しない（thread/turn を開始しないため）。
    """
    proc = subprocess.Popen(
        ["codex", "app-server", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    try:
        for payload in (
            {"method": "initialize", "id": 1, "params": {
                "clientInfo": {"name": "claude-statusline", "title": None, "version": "1"},
                "capabilities": {"experimentalApi": True, "requestAttestation": False}}},
            {"method": "account/rateLimits/read", "id": 2, "params": None},
        ):
            proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()

        deadline = time.monotonic() + RPC_TIMEOUT_SEC
        while time.monotonic() < deadline:
            ready, _, _ = select.select([proc.stdout], [], [], 0.2)
            if not ready:
                continue
            line = proc.stdout.readline()
            if not line:
                return None
            try:
                message = json.loads(line)
            except ValueError:
                continue
            if message.get("id") == 2:
                return (message.get("result") or {}).get("rateLimits")
        return None
    except (BrokenPipeError, OSError):
        return None
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


def to_cache_entry(rate_limits, now):
    """rateLimits から統計を抜き、キャッシュに載せる形にする。

    Why not: remainingPercent をそのまま使わない。枠を超過しても 0 で止まり、
    100% と 150% を区別できないため、used/limit から消費率を出す。
    """
    if not isinstance(rate_limits, dict):
        return None
    individual = rate_limits.get("individualLimit")
    if not isinstance(individual, dict):
        return None
    try:
        used = float(individual.get("used"))
        limit = float(individual.get("limit"))
    except (TypeError, ValueError):
        return None
    if limit <= 0:
        return None
    resets_at = individual.get("resetsAt")
    return {
        "pct": int(round(used / limit * 100)),
        "used": used,
        "limit": limit,
        "resets_at": int(resets_at) if isinstance(resets_at, (int, float)) else None,
        "fetched_at": int(now),
    }


def acquire_lock(now):
    """os.mkdir のアトミック性でロックを取る。取れたら True。"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        os.mkdir(LOCK_PATH)
        return True
    except FileExistsError:
        pass
    try:
        age = now - os.stat(LOCK_PATH).st_mtime
    except OSError:
        return False
    if age < LOCK_STALE_SEC:
        return False
    # Why not: 奪う前に消して mkdir し直す。rmdir だけでは、同時に stale と
    # 判定した別プロセスと二重に走る余地が残るため、mkdir の成否で決める
    try:
        os.rmdir(LOCK_PATH)
        os.mkdir(LOCK_PATH)
        return True
    except OSError:
        return False


def release_lock():
    try:
        os.rmdir(LOCK_PATH)
    except OSError:
        pass


def write_cache(entry):
    tmp = CACHE_PATH + ".tmp.%d" % os.getpid()
    with open(tmp, "w") as fh:
        json.dump(entry, fh)
    os.replace(tmp, CACHE_PATH)


def read_cache():
    try:
        with open(CACHE_PATH) as fh:
            entry = json.load(fh)
    except (OSError, ValueError):
        return None
    return entry if isinstance(entry, dict) else None


def refresh(now):
    if not acquire_lock(now):
        return 0
    try:
        entry = to_cache_entry(query_rate_limits(), now)
        # 照会が失敗しても既存キャッシュは残す（値が消えるより古い値の方が有用）
        if entry is None:
            return 1
        write_cache(entry)
        return 0
    finally:
        release_lock()


def main(argv):
    if "--refresh" in argv:
        return refresh(time.time())
    if "--show" in argv:
        entry = read_cache()
        if entry is None:
            return 1
        print(json.dumps(entry))
        return 0
    sys.stderr.write(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
