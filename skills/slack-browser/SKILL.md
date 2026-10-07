---
name: slack-browser
description: playwright の常駐 Chrome にログイン済みの Slack Web クライアントを scripts/slack_browser.py で操作し、チャンネル一覧・履歴・スレッド・検索の取得と、承認済み文面の投稿を行う。Slack の MCP・アプリ連携を繋げないワークスペース（guest 権限など）で、Slack のパーマリンクを読む・Slack を検索する・Slack に投稿や返信をする依頼時に使用。境界: Slack MCP が繋がるワークスペースはそちらを使う、投稿する日本語の文面の作成は ukwhatn-writing、ブラウザ経路の選び方と共有コンテキストの規則は context/browser-automation.md。
---

# Slack をブラウザ経由で読み書きする

Slack のアプリ連携を認可できないワークスペースで、ユーザーがログインした自動化 Chrome の画面を操作して読み書きする。操作は全部 `scripts/slack_browser.py` を Bash で実行して行い、結果は JSON で受け取る（スナップショットを読まない）。

## 前提

- playwright-mcp の常駐サーバ（`context/browser-automation.md`）が動いていて、その Chrome で対象ワークスペースにログイン済みであること。ログインはユーザーが常駐 Chrome のウィンドウで行う（エージェントは代行しない）
- ワークスペースの対応表 `~/.claude/local/slack-workspaces.json`（git 管理外）に登録してあること:

```json
{"<domain>": {"team": "T0123456789", "home": "D0123456789"}}
```

- `<domain>`: `<domain>.slack.com` の部分。パーマリンクから自動で引く
- `team`: Web クライアントの URL `app.slack.com/client/<team>/...` の先頭
- `home`: 開いて既読になっても困らない会話（Slackbot か自分の DM）の ID。Web クライアントはどの URL から入っても最後に見た会話を開くので、channels・search はここを起点にする
- 未登録なら、ユーザーに Slackbot DM を開いた URL を貼ってもらい、そこから `team` と `home` を書く

完了基準: `slack_browser.py channels --ws <domain>` がチャンネルの配列を返す。`クライアントが開かない` が返ったら未ログインかセッション切れなので、ユーザーに常駐 Chrome でのログインを頼んで止まる。

## コマンド

`S=~/.claude/skills/slack-browser/scripts/slack_browser.py` として:

| やること | コマンド | 既読 |
|---|---|---|
| チャンネル・DM の一覧（ID・未読） | `python3 $S channels --ws <domain>` | home だけ |
| パーマリンクのスレッドを全件 | `python3 $S thread '<permalink>'` | そのスレッド |
| チャンネルの最新 N 件 | `python3 $S history --ws <domain> <channel_id> --limit 30` | そのチャンネル |
| 検索（Slack の検索構文が使える） | `python3 $S search --ws <domain> '<query>' --limit 20` | home だけ |
| 投稿の確認（送らない） | `python3 $S post <permalink または channel_id> --file body.txt [--ws <domain>]` | なし |
| 投稿 | 上に `--send` を付ける | 送り先 |

- パーマリンクを渡すとスレッドへの返信、チャンネル ID（`--ws` 必須）を渡すとチャンネル本体への投稿になる。スレッド返信は「チャンネルにも投稿」をオフのまま送る
- 出力は `ts`・`author`・`text`・`replies`・`link` の配列。長いときは出力をファイルに落としてから必要な部分だけ読む

## 読むときの順序

1. パーマリンクを渡されたら `thread` で読む
2. 話題やキーワードで探すときは、まず `search` で当たりを付ける（会話を開かないので既読を付けない）。`in:#<channel>`・`from:@<name>`・`is:thread`・`after:YYYY-MM-DD` が使える
3. `history` はチャンネルの流れを追う必要があるときだけ使う。開いたチャンネルは既読になり、ユーザーの未読の目印が消える

## 投稿するとき

投稿は相手に見える外向きの操作。**1 件ごとに、送信先と本文をユーザーに見せて承認を得てから `--send` する**（承認は投稿 1 件に限って有効。前の承認を次の投稿に流用しない）。

1. 日本語の文面は `/ukwhatn-writing` スキルで書き、`body.txt` に保存する
2. `--send` なしで実行し、出力の `to` と `text` をそのままユーザーに提示する
3. 承認を得たら同じ引数に `--send` を付けて実行する。完了基準: `"sent": true` と `last_link` が返る。`last_link` を報告に添える

書式: 入力欄に本文を流し込む方式なので、Slack の自動書式は働かない。改行は保たれるが、`` `code` ``・`*bold*`・コードブロック・`<url|text>` は記号のまま送られる。書式付きで送るには、ユーザー自身が Slack の環境設定「マークアップでメッセージを書式設定する」を有効にしておく必要がある（有効なら mrkdwn が送信時に解釈される）。設定の変更はユーザーの判断で、エージェントは画面から切り替えない。URL は書式設定なしでもリンクになる。

## Gotchas

- **ブラウザのセッションのトークンで Web API を呼ぶ方法は使わない**。トークンを読む操作は、Claude Code の auto mode の安全判定に認証情報の探索として拒否される。画面操作だけで完結させる
- **検索欄で Enter を押さない**。本文を流し込んだ直後は、候補一覧の先頭が最近のチャンネルのままで、Enter でそのチャンネルが開いて既読になる。スクリプトは、打鍵してから先頭の候補が「検索結果を表示する」であることを確かめてクリックし、違えば中止する
- 検索欄には前回の検索語が残る。スクリプトは全選択して消してから打つ
- Slack はチャンネルごとのスクロール位置を覚えている。`history` は最下部まで送ってから遡る
- 1 文字ずつ打鍵すると、`` ` `` は書式になるが `*` や `~` の前後で文字が欠ける。本文の入力に打鍵を使わない
- 空行は詰まることがある。段落を空けたいときは見出しや記号で区切る
- 画面は仮想リストで、DOM にあるのは表示範囲の十数件だけ。スクリプトはスクロールしながら `ts` で重ねて集める
- スクリプトは毎回 `page.context().newPage()` で自分専用のタブを開いて閉じる。共有コンテキストの current tab（他のセッションのタブ）には触れない。手で MCP の playwright ツールを使うときも同じく自分のタブだけを操作する
- 常駐 Chrome は全セッションで共有されるので、ログインした Slack はどのセッションからも操作できる。投稿の承認は上の手順でセッションごとに取る
- Slack の DOM（`data-qa` 属性）が変わると、セレクタが外れて空配列やタイムアウトになる。`browser_run_code_unsafe` で `newPage()` を開き、該当要素の `data-qa` を調べてスクリプトを直す
- 実行のたびに、playwright-mcp の出力先（作業ディレクトリの `.playwright-mcp/` になることが多い）へタブごとの console ログが残る。Slack の画面のログを含むので、作業の終わりに自分の実行時刻の分を消す
- 投稿先のチャンネルに入力欄が無い（ワークフロー専用など）と `入力欄が無い` を返す
- スレッド返信の経路（`threads_flexpane` 内の入力欄）は、入力欄の特定までしか実機で確かめていない。初回のスレッド返信では、送信後に `thread` で読み戻して届いたことを確かめる
