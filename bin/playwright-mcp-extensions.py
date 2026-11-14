#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "websocket-client>=1.7",
# ]
# ///
"""自動化専用 Chrome に、playwright-mcp-extensions.txt に並べた Chrome ウェブストアの拡張を入れる。

  playwright-mcp-extensions.py sync <user-data-dir>   # 一覧どおりに外部拡張の設定を置く（一覧から消した拡張は Chrome が外す）
  playwright-mcp-extensions.py enable <CDP ポート>     # 起動後に、外部から入った拡張を有効にする

外部拡張の設定（<user-data-dir>/External Extensions/<ID>.json）で入った拡張は、Chrome が無効の状態で入れる。
人が拡張の管理画面で有効にするのと同じ chrome.management.setEnabled を、chrome://extensions のページから呼ぶ。
playwright の既定の起動引数のうち --disable-default-apps と --disable-background-networking が付いていると、
Chrome は外部拡張の設定を読まない・ダウンロードしないので、playwright-mcp-config.json でこの2つを外しておく。
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from pathlib import Path

LIST_FILE = Path(__file__).with_name("playwright-mcp-extensions.txt")
UPDATE_URL = "https://clients2.google.com/service/update2/crx"
ID_RE = re.compile(r"^[a-p]{32}$")
INSTALL_TIMEOUT = 120


def listed_ids() -> list[str]:
    ids = []
    for n, line in enumerate(LIST_FILE.read_text().splitlines(), 1):
        token = line.split("#", 1)[0].strip()
        if not token:
            continue
        if not ID_RE.match(token):
            sys.exit(f"{LIST_FILE}:{n}: 拡張 ID ではない: {token}")
        ids.append(token)
    return ids


def sync(user_data_dir: Path) -> None:
    ids = set(listed_ids())
    ext_dir = user_data_dir / "External Extensions"
    ext_dir.mkdir(parents=True, exist_ok=True)
    present = {p.stem for p in ext_dir.glob("*.json")}
    for ext_id in ids - present:
        (ext_dir / f"{ext_id}.json").write_text(json.dumps({"external_update_url": UPDATE_URL}))
        print(f"[extensions] 追加: {ext_id}")
    for ext_id in present - ids:
        (ext_dir / f"{ext_id}.json").unlink()
        print(f"[extensions] 削除: {ext_id}")


def _evaluate(ws, expression: str):
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                        "params": {"expression": expression, "awaitPromise": True, "returnByValue": True}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == 1:
            break
    result = msg.get("result") or {}
    if "exceptionDetails" in result or "error" in msg:
        raise RuntimeError(str(msg)[:300])
    return result["result"].get("value")


GET_ALL_JS = "new Promise(r => chrome.management.getAll(xs => r(xs.map(x => ({id: x.id, enabled: x.enabled})))))"
ENABLE_JS = ("new Promise((r, j) => chrome.management.setEnabled({id}, true, "
             "() => chrome.runtime.lastError ? j(chrome.runtime.lastError.message) : r(true)))")


def enable(port: int) -> int:
    import websocket  # websocket-client

    ids = listed_ids()
    if not ids:
        print("[extensions] 一覧が空なので何もしない")
        return 0
    req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?chrome://extensions", method="PUT")
    with urllib.request.urlopen(req, timeout=10) as r:
        target = json.load(r)
    try:
        # suppress_origin: CDP は Origin ヘッダ付きの WebSocket を 403 で弾く
        ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=30, suppress_origin=True)
        try:
            deadline = time.monotonic() + INSTALL_TIMEOUT
            pending = set(ids)
            while pending and time.monotonic() < deadline:
                installed = {x["id"]: x["enabled"] for x in _evaluate(ws, GET_ALL_JS)}
                for ext_id in sorted(pending & installed.keys()):
                    if not installed[ext_id]:
                        _evaluate(ws, ENABLE_JS.replace("{id}", json.dumps(ext_id)))
                    print(f"[extensions] 有効: {ext_id}")
                    pending.discard(ext_id)
                if pending:
                    time.sleep(2)
        finally:
            ws.close()
    finally:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/close/{target['id']}", timeout=10).close()
    for ext_id in sorted(pending):
        print(f"[extensions] {INSTALL_TIMEOUT}秒待っても入らなかった: {ext_id}")
    return 1 if pending else 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "sync":
        sync(Path(argv[1]))
        return 0
    if len(argv) == 2 and argv[0] == "enable":
        return enable(int(argv[1]))
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
