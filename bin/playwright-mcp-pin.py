#!/usr/bin/env python3
"""playwright-mcp standalone server に常駐 MCP クライアントを1本張り、Chrome への CDP attach を維持する。

playwright-mcp は接続クライアントが 0 になると Chrome から detach し、次の操作で再 attach する。
Chrome の remote debugging 承認ダイアログは attach ごとに出るため、クライアントを1本張り続けることで
承認をサーバ起動時の1回に固定する。
"""
import json
import os
import time
import urllib.request

PORT = os.environ.get("PLAYWRIGHT_MCP_PORT", "8931")
URL = f"http://127.0.0.1:{PORT}/mcp"
KEEPALIVE_INTERVAL = int(os.environ.get("PIN_KEEPALIVE_INTERVAL", "60"))
RETRY_INTERVAL = int(os.environ.get("PIN_RETRY_INTERVAL", "5"))


def log(message):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [pin] {message}", flush=True)


def post(body, session_id=None, timeout=180):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        session_id = response.headers.get("Mcp-Session-Id", session_id)
        result = None
        for line in response.read().decode().splitlines():
            if line.startswith("data:"):
                result = json.loads(line[5:].strip())
        return result, session_id


def connect():
    _, session_id = post({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "playwright-mcp-pin", "version": "1"},
        },
    })
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id)
    # initialize だけでは backend が生成されず CDP attach が起きないため、副作用のないツールを1回呼ぶ
    # initialize だけでは backend が生成されず CDP attach が起きないため、副作用のないツールを1回呼ぶ。
    # ここで返らない場合はサーバ側の CDP セッションが応答していないので、短めの timeout で失敗させる
    post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
          "params": {"name": "browser_tabs", "arguments": {"action": "list"}}}, session_id, timeout=60)
    log(f"attached (session {session_id})")
    return session_id


def main():
    session_id = None
    request_id = 2
    failures = 0
    while True:
        try:
            if session_id is None:
                session_id = connect()
            else:
                request_id += 1
                post({"jsonrpc": "2.0", "id": request_id, "method": "tools/list"}, session_id, timeout=30)
            failures = 0
        except Exception as error:
            log(f"attach failed or session lost ({type(error).__name__}: {error})")
            session_id = None
            failures += 1
            # サーバ側が応答しない状態は再接続では解けないため、プロセスごと落として launchd に作り直させる
            if failures >= 3:
                log("giving up; exiting so the server is restarted")
                raise SystemExit(1)
        time.sleep(KEEPALIVE_INTERVAL if session_id else RETRY_INTERVAL)


if __name__ == "__main__":
    main()
