# gws MCPの運用ノート

gws MCPで戻り値が数百KBを超える経路（`drive_download_file` / `get_attachment` / 長い `get_message`）の回避策と、Gmailの下書きを作るときの落とし穴。

## Google Driveから大きいファイルをローカルへ落とす

gws MCPの `drive_download_file` は中身を **base64にして戻り値で返す**ため、数百KBのPDFでもコンテキストを大きく消費する。メール添付用のファイルを取りに行くときは、MCPのトークンを流用してDrive APIを直接叩く。

```bash
python3 ~/.claude/bin/gws-drive-dl.py <account> <out_dir> "<file_id>:<保存名>" ["<file_id>:<保存名>" ...]
```

- `<account>` はMCPの `account_id` と同じ（`data/tokens/<account>.json` のファイル名）
- access tokenが切れていれば `refresh_token` で自動更新し、トークンファイルへ書き戻す
- MCPのインストール先は `GWS_MCP_DIR` で上書き可（既定 `~/workspace/mcp/google-workspace-mcp`）

トークンファイル（`data/tokens/*.json`）の中身は標準出力に出さない。構造を確認するときもキー名と文字数に留める。`client_secret` は35文字程度なので、「長い値だけ伏せる」実装では伏せられずに出力される。

file_idはDriveのURLから取る: `https://drive.google.com/file/d/<FILE_ID>/view` / `https://drive.google.com/open?id=<FILE_ID>`

## Gmailの添付をローカルへ落とす

`get_attachment` も同じく **base64を戻り値で返す**。添付1つでもコンテキストを大きく消費するので、中身を読みたいときはGmail APIを直接叩く。

```bash
python3 ~/.claude/bin/gws-gmail-att-dl.py <account> <out_dir> <message_id> [<message_id> ...]
```

- message_idは `search_all_messages` / `get_message` が返す `id`（RFCのMessage-IDではない）
- 保存名は `<message_id>_<添付のファイル名>`。1メッセージ内の全添付を再帰的に拾う
- トークンの読み込みと更新は `gws-drive-dl.py` の実装をimportして共有している

注文書・請求書のような業務書類の添付は、拡張子を見て決め打ちしない。PDFに見える書類がHTMLで届くことがあり、その場合はタグを除去してテキスト化してから読む。

## メール本文が戻り値の上限を超えるとき

長いスレッドへの返信は引用が積み上がるため、`get_message` の戻り値が上限を超えてファイルに退避されることがある。本文だけを読めばよいので、退避先を `jq -r '.data.body'` に通して先頭から必要な行だけ見る（ファイル全体を読むと引用部分でコンテキストを使い切る）。

## Gmailの下書き（`create_draft` / `update_draft`）の落とし穴（実機で確定）

- **`to` / `cc` / `bcc` に配列を渡すと、アドレスが1つも入らない**。実際のヘッダは `,`（カンマだけ）になる。カンマ区切りの文字列で渡す（`"a@example.com, b@example.com"`）
  - `create_draft` の戻り値の `to` は渡した値を反射するだけで、実ヘッダを表していない。作成後は `get_draft` で実ヘッダを見て、`,` や空になっていないことを確かめる
- **`from_address` を指定すると失敗する**（表示名に非ASCII文字を含むSend-Asでは、RFC 2047エンコードでFromヘッダが折り返され、「Header values may not contain linefeed or carriage return characters」になる）。`from_address` は渡さず、Gmail側の既定のSend-Asを送信時に使わせる
- `reply_all=true` は元メッセージの受信者をCCへマージする（自分のアドレスも入る）。CCを厳密に決めたいときは `reply_all=false` にしてccを明示する
- 返信スレッドに載せるには `reply_to_message_id`（Gmailのメッセージid。RFCのMessage-IDではない）を渡す
- **`update_draft` で下書きを直さない。本文・CC・添付のどれを直すときも、削除して作り直す**。`get_draft` が返す `body` はGmailが生成したHTML文字列だが、`update_draft` の `body` はプレーンテキストとして登録されるため、`<html>` `<br>` などがそのまま本文に出る。さらに `threadId` が下書き自身のIDに変わり、返信スレッドから外れる
  - 壊れていないかは、本文の先頭にタグが混じっていないこと（`search_all_messages` のsnippetに `&lt;html&gt;` が出ていないか）と、`thread_id` が元のスレッドのままであることの両方で確かめる。CCだけを見ても分からない
