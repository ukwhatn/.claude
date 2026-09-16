# gws MCP の運用ノート

## Google Drive から大きいファイルをローカルへ落とす

gws MCP の `drive_download_file` は中身を **base64 にして戻り値で返す**ため、数百KBのPDFでもコンテキストを大きく消費する。メール添付用のファイルを取りに行くときは、MCP のトークンを流用して Drive API を直接叩く。

```bash
python3 ~/.claude/bin/gws-drive-dl.py <account> <out_dir> "<file_id>:<保存名>" ["<file_id>:<保存名>" ...]
```

- `<account>` は MCP の `account_id` と同じ（`data/tokens/<account>.json` のファイル名）
- access token が切れていれば `refresh_token` で自動更新し、トークンファイルへ書き戻す
- MCP のインストール先は `GWS_MCP_DIR` で上書き可（既定 `~/workspace/mcp/google-workspace-mcp`）

**トークンファイル（`data/tokens/*.json`）の中身を標準出力に出さないこと。** 構造を確認するときもキー名と文字数に留める。`client_secret` は35文字程度なので、「長い値だけ伏せる」実装では素通りする。

file_id は Drive の URL から取る: `https://drive.google.com/file/d/<FILE_ID>/view` / `https://drive.google.com/open?id=<FILE_ID>`

## Gmail の添付をローカルへ落とす

`get_attachment` も同じく **base64 を戻り値で返す**。添付1つでもコンテキストを大きく消費するので、中身を読みたいときは Gmail API を直接叩く。

```bash
python3 ~/.claude/bin/gws-gmail-att-dl.py <account> <out_dir> <message_id> [<message_id> ...]
```

- message_id は `search_all_messages` / `get_message` が返す `id`（RFC の Message-ID ではない）
- 保存名は `<message_id>_<添付のファイル名>`。1メッセージ内の全添付を再帰的に拾う
- トークンの読み込みと更新は `gws-drive-dl.py` の実装を import して共有している

**注文書・請求書のような業務書類の添付は、拡張子を見て決め打ちしない。** PDF に見える書類が HTML で届くことがあり、その場合はタグを落としてテキスト化してから読む。

## メール本文が戻り値の上限を超えるとき

長いスレッドへの返信は引用が積み上がるため、`get_message` の戻り値が上限を超えてファイルに退避されることがある。**本文だけを読めばよいので、退避先を `jq -r '.data.body'` に通して先頭から必要な行だけ見る**（ファイル全体を読むと引用部分でコンテキストを使い切る）。
