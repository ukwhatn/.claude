#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""google-workspace-mcp のトークンを使って Drive へファイルを直接アップロードする。

MCP の `drive_create_file` は名前と MIME だけを取り、中身を渡せない (空のファイルが
できる)。gws-drive-dl.py と対になる経路として、トークンを流用して Drive API を直接叩く。

使い方:
    python3 ~/.claude/bin/gws-drive-up.py <account> <parent_folder_id> <local_path> [表示名]

- `<account>` は `data/tokens/<account>.json` のファイル名 (MCP の account_id と同じ)
- access token が切れていれば refresh_token で自動更新し、トークンファイルへ書き戻す
- 5MB を超えるファイルがあるため resumable upload を使う (multipart は 5MB 上限)
- 共有ドライブへ入れるため supportsAllDrives=true を付ける
- MCP のインストール先は環境変数 `GWS_MCP_DIR` で上書きできる

**トークンの中身を標準出力へ出さないこと。** 値を確認したい場合もキー名と長さに留める。
"""
import json
import mimetypes
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


def refresh(path, tok):
    body = urllib.parse.urlencode({
        "client_id": tok["client_id"],
        "client_secret": tok["client_secret"],
        "refresh_token": tok["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body)
    with urllib.request.urlopen(req) as r:
        new = json.load(r)
    tok["token"] = new["access_token"]
    with open(path, "w") as f:
        json.dump(tok, f)
    return tok["token"]


def api(url, token, method="GET", data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    return urllib.request.urlopen(req)


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    account, parent, local = sys.argv[1], sys.argv[2], sys.argv[3]
    name = sys.argv[4] if len(sys.argv) > 4 else os.path.basename(local)
    if not os.path.isfile(local):
        raise SystemExit("file not found: %s" % local)

    tok_path, tok = load_token(account)
    token = tok["token"]
    size = os.path.getsize(local)
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    meta = json.dumps({"name": name, "parents": [parent]}).encode()

    start = ("https://www.googleapis.com/upload/drive/v3/files"
             "?uploadType=resumable&supportsAllDrives=true&fields=id,name,webViewLink")
    hdr = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": mime,
        "X-Upload-Content-Length": str(size),
    }
    try:
        r = api(start, token, "POST", meta, hdr)
    except urllib.error.HTTPError as e:
        if e.code != 401:
            raise SystemExit("start failed: %s %s" % (e.code, e.read().decode()[:400]))
        token = refresh(tok_path, tok)
        r = api(start, token, "POST", meta, hdr)
    session = r.headers["Location"]

    with open(local, "rb") as f:
        payload = f.read()
    try:
        r = api(session, token, "PUT", payload,
                {"Content-Type": mime, "Content-Length": str(size)})
    except urllib.error.HTTPError as e:
        raise SystemExit("upload failed: %s %s" % (e.code, e.read().decode()[:400]))
    out = json.load(r)
    print(json.dumps({"id": out["id"], "name": out["name"],
                      "webViewLink": out.get("webViewLink"), "bytes": size},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
