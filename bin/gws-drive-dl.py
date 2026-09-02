#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""google-workspace-mcp のトークンを使って Drive のファイルを直接ローカルへ落とす。

MCP の `drive_download_file` は中身を base64 にして戻り値で返すため、数百KBの
ファイルでもコンテキストを大きく消費する。この経路なら直接ファイルへ書けるので、
PDF・画像・動画のような添付用ファイルの取得に使う。

使い方:
    python3 ~/.claude/bin/gws-drive-dl.py <account> <out_dir> <file_id>:<filename> [...]

例:
    python3 ~/.claude/bin/gws-drive-dl.py nxtend ./tmp \\
        "1AbCdEf...:契約書.pdf" "1GhIjKl...:規約.pdf"

- `<account>` は `data/tokens/<account>.json` のファイル名（MCP の account_id と同じ）
- access token が切れていれば refresh_token で自動更新し、トークンファイルへ書き戻す
- MCP のインストール先は環境変数 `GWS_MCP_DIR` で上書きできる
  （既定: `~/workspace/mcp/google-workspace-mcp`）

**トークンの中身を標準出力へ出さないこと。** 値を確認したい場合もキー名と長さに留める。
"""
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

MCP_DIR = os.path.expanduser(os.environ.get("GWS_MCP_DIR", "~/workspace/mcp/google-workspace-mcp"))


def load_token(account):
    path = os.path.join(MCP_DIR, "data", "tokens", account + ".json")
    if not os.path.exists(path):
        raise SystemExit("token not found: %s" % path)
    with open(path) as f:
        return path, json.load(f)


def refresh_if_needed(path, tok):
    """期限が2分以内に切れるなら refresh する。戻り値は (access_token, 更新したか)。"""
    exp = tok.get("expiry")
    if exp:
        margin = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=2)
        if datetime.datetime.fromisoformat(exp.replace("Z", "+00:00")) > margin:
            return tok["token"], False

    body = urllib.parse.urlencode({
        "client_id": tok["client_id"],
        "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(tok["token_uri"], data=body, method="POST")
    with urllib.request.urlopen(req) as r:
        d = json.loads(r.read().decode())

    tok["token"] = d["access_token"]
    tok["expiry"] = (
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=d.get("expires_in", 3600))
    ).isoformat().replace("+00:00", "Z")
    with open(path, "w") as f:
        json.dump(tok, f)
    return tok["token"], True


def download(access_token, file_id, dest):
    url = ("https://www.googleapis.com/drive/v3/files/%s"
           "?alt=media&supportsAllDrives=true" % file_id)
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + access_token})
    with urllib.request.urlopen(req) as r, open(dest, "wb") as f:
        f.write(r.read())
    return os.path.getsize(dest)


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    account, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    path, tok = load_token(account)
    at, refreshed = refresh_if_needed(path, tok)
    print("token: %s" % ("refreshed" if refreshed else "still valid"))

    for spec in sys.argv[3:]:
        if ":" not in spec:
            raise SystemExit("expected <file_id>:<filename>, got %r" % spec)
        fid, name = spec.split(":", 1)
        dest = os.path.join(out_dir, name)
        print("  %8d bytes  %s" % (download(at, fid, dest), dest))


if __name__ == "__main__":
    main()
