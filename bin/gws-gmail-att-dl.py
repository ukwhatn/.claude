#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""google-workspace-mcp のトークンを使って Gmail の添付を直接ローカルへ落とす。

MCP の `get_attachment` は中身を base64 にして戻り値で返すため、添付1つでも
コンテキストを大きく消費する。この経路なら直接ファイルへ書けるので、PDF・
HTML・画像のような添付の中身を読みたいときに使う。

使い方:
    python3 ~/.claude/bin/gws-gmail-att-dl.py <account> <out_dir> <message_id> [...]

保存名は `<message_id>_<添付のファイル名>`。同じ差出人から同じ名前の添付が
続けて届いても上書きされない。添付が無いメッセージはその旨だけ出力する。

- `<account>` は `data/tokens/<account>.json` のファイル名（MCP の account_id と同じ）
- access token が切れていれば refresh_token で自動更新し、トークンファイルへ書き戻す
- MCP のインストール先は環境変数 `GWS_MCP_DIR` で上書きできる
  （既定: `~/workspace/mcp/google-workspace-mcp`）

**トークンの中身を標準出力へ出さないこと。** 値を確認したい場合もキー名と長さに留める。
"""
import base64
import importlib.util
import json
import os
import sys
import urllib.request

_DL = os.path.expanduser("~/.claude/bin/gws-drive-dl.py")
_spec = importlib.util.spec_from_file_location("gws_drive_dl", _DL)
_drive = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_drive)

load_token = _drive.load_token
refresh_if_needed = _drive.refresh_if_needed

API = "https://gmail.googleapis.com/gmail/v1/users/me/messages"


def api_get(access_token, url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + access_token})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def collect_parts(part, acc):
    """payload を再帰して (filename, attachment_id) を集める。"""
    if part.get("filename") and part.get("body", {}).get("attachmentId"):
        acc.append((part["filename"], part["body"]["attachmentId"]))
    for child in part.get("parts") or []:
        collect_parts(child, acc)
    return acc


def main():
    if len(sys.argv) < 4:
        raise SystemExit(__doc__)
    account, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    path, tok = load_token(account)
    at, refreshed = refresh_if_needed(path, tok)
    print("token: %s" % ("refreshed" if refreshed else "still valid"))

    for mid in sys.argv[3:]:
        msg = api_get(at, "%s/%s?format=full" % (API, mid))
        parts = collect_parts(msg.get("payload", {}), [])
        if not parts:
            print("  %s: no attachments" % mid)
            continue
        for filename, aid in parts:
            data = api_get(at, "%s/%s/attachments/%s" % (API, mid, aid))
            raw = base64.urlsafe_b64decode(data["data"])
            dest = os.path.join(out_dir, ("%s_%s" % (mid, filename)).replace("/", "_"))
            with open(dest, "wb") as f:
                f.write(raw)
            print("  %8d bytes  %s" % (len(raw), dest))


if __name__ == "__main__":
    main()
