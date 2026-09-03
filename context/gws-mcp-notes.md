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
