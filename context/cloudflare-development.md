# Cloudflare (wrangler) 開発ガイド

Read when: Cloudflare（wrangler / Workers / D1 / R2）を触る前。

## セットアップ・アカウント

- wranglerはbunでインストールする（`bun add -d wrangler`）
- **CRITICAL: 複数のCloudflareアカウントが存在する。デプロイ先アカウントは必ずユーザーに確認する**（推測・仮定は禁止）。`bunx wrangler whoami` で利用可能なアカウント一覧を確認してから提示・質問する。PJ CLAUDE.mdまたはpackage.jsonに `CLOUDFLARE_ACCOUNT_ID` が明記されている場合はそれを使う

## Workersランタイムの落とし穴（実機検証済み）

- **`fetch()` の `redirect` は `follow` / `manual` のみ。`"error"` は未実装**で、指定すると即 `TypeError: Invalid redirect value, must be one of "follow" or "manual"`（公式docsは3値とも有効値として記載、TS型も受理、lint / typecheck / test / CIも全通過するためデプロイするまで気付けない）。リダイレクトを拒否したい場合は `"manual"` を使い、`!response.ok`（3xxがstatusに出る）で弾く
- HTTP invocationの `ctx.waitUntil()` は応答後 **30秒**上限（cronのwall-clock 15分・CPU時間上限とは別枠）。外部APIのリトライ等で超え得る処理はQueue（consumerはwall-clock 15分）へ移す
- 挙動が疑わしいランタイムAPIは `wrangler dev --remote` に最小スクリプトを載せて実機で確定する（ローカルworkerd・公式docsと実機で差が出る）

## wrangler / D1の落とし穴（実機検証済み）

- **wranglerがタイムアウト系エラー（7429 storage timeout等）を返しても、D1側では処理が完遂していることがある**。長時間DDL（大規模CREATE INDEX等）は、sqlite_master・d1_migrations・実クエリで実態を確認してから失敗と断定する
- `wrangler d1 export` は100KB超のINSERT文を吐くが、D1のSQL文長上限は100KBのためそのままimportできない（エラーを出さずに失敗したように見える）。大行はチャンク分割INSERT ＋連結UPDATEが必要
- `wrangler d1 export` のCREATE TABLE順はFK依存順でない。FK有効なD1へ直接importせず、migrations適用後にdata-onlyで投入する
- `wrangler deployments list` は最新が**末尾**（先頭ではない）
- `wrangler r2 object` に `list` サブコマンドはない（get / put / deleteのみ。一覧はダッシュボードかAPIで）
- vitest-pool-workersのストレージ分離は**テストファイル単位**（同一ファイル内のテスト間ではD1 / R2が共有される）。一意ID ＋ beforeEachクリーンアップで衝突を避ける
