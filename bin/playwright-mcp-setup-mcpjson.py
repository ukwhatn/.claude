#!/usr/bin/env python3
"""~/.claude.json の mcpServers.playwright / mcpServers.chrome-devtools を
常駐サーバ構成（HTTP / 自動化ブラウザへのCDP接続）に書き換える。

playwright-mcp-setup.sh から呼ばれる。引数: <port> <cdp_port>
既存の他エントリ（github・slack等）は変更しない。書き込みは一時ファイル経由の
os.replace で行い、他プロセスが同時に ~/.claude.json を書いていても壊さない。
"""
import json
import os
import sys
import tempfile


def main():
    if len(sys.argv) != 3:
        print("usage: playwright-mcp-setup-mcpjson.py <port> <cdp_port>", file=sys.stderr)
        sys.exit(1)
    port, cdp_port = sys.argv[1], sys.argv[2]

    path = os.path.expanduser("~/.claude.json")
    if not os.path.exists(path):
        print(f"[setup] {path} が存在しない。Claude Code を一度起動してから再実行すること", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    servers = data.setdefault("mcpServers", {})
    servers["playwright"] = {
        "type": "http",
        "url": f"http://127.0.0.1:{port}/mcp",
    }
    servers["chrome-devtools"] = {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "chrome-devtools-mcp@latest", "--browserUrl", f"http://127.0.0.1:{cdp_port}"],
        "env": {},
    }

    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise
    os.chmod(path, 0o600)
    print(f"[setup] ~/.claude.json を更新した（playwright: {port}, chrome-devtools: {cdp_port} 経由）")


if __name__ == "__main__":
    main()
