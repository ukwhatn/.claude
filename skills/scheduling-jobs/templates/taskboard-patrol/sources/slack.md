# ソース部品: Slack

指示の受け口と、自分へのメンション・自分の発言の収集。各節を RUNBOOK.md の「貼る:」の位置へ写す。tool 名は Slack の MCP server が出す名前に合わせる（引数は呼ぶ前にツールスキーマで確かめる。版が変わると引数の名前が変わる）。

## 固定値の行

| 対象 | 値 |
|---|---|
| Slack の自分のユーザー ID | `{{SLACK_USER_ID}}` |
| 通知先チャンネル（指示の受け口を兼ねる） | `{{NOTIFY_CHANNEL_NAME}}` (`{{NOTIFY_CHANNEL_ID}}`) |
| Slack MCP | `{{SLACK_MCP}}` **1本だけ**（同じワークスペースに届く server が複数あっても、1本に決める。複数使うと同じ発言を二重に拾う） |

## 指示の受け口（1-0 に貼る）

通知チャンネルは通知専用なので、**そこにある自分の発言はすべて巡回への指示**として扱う。

```
slack_read_channel(channel_id="{{NOTIFY_CHANNEL_ID}}", oldest=state.cursors.slack_instruction_ts, limit=50)
```

`{{SLACK_USER_ID}}` の発言だけ拾う。

**指示はほぼスレッドの返信で来る。** `read_channel` はスレッドの返信を返さないので、これだけでは取りこぼす。チャンネル読みで得た各メッセージの返信数を見て、返信があるものは `slack_read_thread(channel_id="{{NOTIFY_CHANNEL_ID}}", message_ts=<通知の ts>)` を開く。**直近の通知は必ず開く**（`state.pending[].notify_ts`。無ければ `read_channel` の詳細表示で ts を取る）。

処理したチャンネル本体の ts は `state.cursors.slack_instruction_ts` に進める。**スレッドの返信の ts は `state.processed_instructions` に積む**（cursor では追えないため）。どちらかに入っている ts は二度実行しない。

## 通知の後（Step 4 の末尾に貼る）

**投稿した通知の ts を必ず保存する。** Webhook の応答は ts を返さないので、投稿の直後に `read_channel(channel_id="{{NOTIFY_CHANNEL_ID}}", limit=1)` を詳細表示で読み、自分の投稿の ts を `pending[].notify_ts` と `last_notification.ts` に入れる。null のまま残すと、次の回に指示のスレッドを開けない。

## 収集（1-2〜 に貼る）

### 1-N. Slack（メンションと自分の発言）

`{{SLACK_MCP}}` だけを使う。**query の山括弧はエスケープせず生で渡す**（`&lt;` にするとメンションとして解釈されない）。

```
# 自分へのメンション
slack_search_public_and_private(
  query="<@{{SLACK_USER_ID}}>", after="<since の Unix 秒>",
  limit=20, sort="timestamp", include_context=false)

# 自分の発言（「対応します」「やっておきます」等の宣言を拾う）
slack_search_public_and_private(
  query="from:<@{{SLACK_USER_ID}}>", after="<since の Unix 秒>",
  limit=20, sort="timestamp", include_context=false)
```

- `after` には `date -j -f "%Y-%m-%dT%H:%M:%S%z" "<since の ISO8601>" "+%s"` で変えた Unix 秒を渡す。**返ってきた各メッセージの timestamp は `since` と自分でも比べて仕分ける**（検索のフィルタを過信しない）
- メンションの検索には**メンションを含まない投稿も混ざる**ので、本文に `{{SLACK_USER_ID}}` があるものだけ残す
- 文脈が要るものだけ `slack_read_thread` で該当スレッドを読む（全件は読まない）
- **ページは `cursor` で追う**。応答が次のページありを示したら、`cursor` に前の値を渡して最大3ページまで取る。3ページ使い切ってもまだ残るときだけ「■ 打ち切り」に書く（1ページで打ち切らない）
- **スレッド単位の無視**: ユーザーが「このスレッドは今後起票しなくて良い」等とスレッド全体を指したら、root の `thread_ts` を `state.seen["slack:thread:<root_ts>"]` に `{"decision":"ignored"}` で登録する。検索でヒットしたメッセージの `thread_ts` がこれと一致したら、個別の permalink が未処理でも無視する

## 起票の既定

- **候補として通知する**（起票しない）。`seen.decision = "notified"`。起票は「起票 N」の指示か `@{{JOB_NAME}}` の明示指定があったときだけ
- `seen` のキー: 発言の permalink
- 起票するときは permalink をリンクに付ける

## cursor

- `slack_instruction_ts`（初期値 `"0"`）: 受け口のチャンネル本体の走査位置
- `slack_scan_from`（初期値 null）: 検索の `since`。Slack の取得が全部成功した回だけ進める

## 上限

| 項目 | 上限 |
|---|---|
| メンション / 自分の発言 | 各20件 × 最大3ページ |
| スレッドの展開 | 5件 |

## 禁止事項

- Slack へメッセージを送らない（`slack_send_message`・下書き・予約投稿・リアクションを含む）。Slack への出力は通知の Webhook だけ
