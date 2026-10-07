# ソース部品: Gmail

未読の、人からのメールの収集。google-workspace の MCP（`search_all_messages`）を使う前提で書いてある。

## 固定値の行

| 対象 | 値 |
|---|---|
| Gmail | google-workspace MCP の `account_id: "{{GMAIL_ACCOUNT_ID}}"` だけ |

## 収集（1-2〜 に貼る）

### 1-N. Gmail

```
search_all_messages(account_id="{{GMAIL_ACCOUNT_ID}}", max_results=20,
  query="in:inbox is:unread newer_than:2d -category:promotions -category:social -category:updates \
         -from:notifications@github.com -from:noreply@github.com {{GMAIL_EXTRA_EXCLUDES}}")
```

- **GitHub の通知メールはクエリの側で除外する。** 除外しないと未読の大半が PR のコメント・approve の通知で埋まり、人からのメールが上限から押し出される。PR の状態は taskboard の `links[]` と GitHub の部品が一次情報なので、メールから拾わない
- `newer_than` は `since` より長めに取る（回が飛んだ分を拾うため）。重複は `seen` で落とす
- 定期の監査通知・全社のアナウンスのように「毎回同じものが来る」メールは、`seen` で1度だけ扱う。返信や作業を求めているものだけ残す

## 起票の既定

- **候補として通知する**（起票しない）。`seen.decision = "notified"`。起票は「起票 N」の指示か `@{{JOB_NAME}}` の明示指定があったときだけ
- `seen` のキー: `gmail:<message_id>`
- 起票するときのリンクは、本文の中の対象ページの URL を優先する（研修なら研修ページ、社内システムならその画面）。本文に URL が無いときは Gmail のスレッドの URL（`https://mail.google.com/mail/u/0/#all/<thread_id>`）

## cursor

- `gmail_scan_from`（初期値 null）: Gmail の取得が成功した回だけ進める

## 上限

| 項目 | 上限 |
|---|---|
| Gmail | 20件 |

## 禁止事項

- メールを送らない・下書きを作らない・ラベルや既読の状態を変えない・アーカイブしない（未読がユーザーの受信箱の状態そのものなので、巡回が変えると人が見落とす）
- メールの本文を通知に貼らない。差出人・件名の要約と参照先だけにする

## 認証切れ

「■ エラー」に `gmail: 認証切れ。gws_auth_reauth が必要` と書いてスキップする。
