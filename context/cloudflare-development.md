# Cloudflare (wrangler) 開発ガイド

Read when: Cloudflare（wrangler / Workers / D1 / R2）を触る前。

## セットアップ・アカウント

- wrangler は bun でインストールする（`bun add -d wrangler`）
- **CRITICAL: 複数の Cloudflare アカウントが存在する。デプロイ先アカウントは必ずユーザーに確認する**（推測・仮定は禁止）。`bunx wrangler whoami` で利用可能なアカウント一覧を確認してから提示・質問する。PJ CLAUDE.md または package.json に `CLOUDFLARE_ACCOUNT_ID` が明記されている場合はそれを使う

## Workers ランタイムの落とし穴（実機検証済み）

- **`fetch()` の `redirect` は `follow` / `manual` のみ。`"error"` は未実装**で、指定すると即 `TypeError: Invalid redirect value, must be one of "follow" or "manual"`（公式 docs は 3 値とも有効値として記載、TS 型も受理、lint / typecheck / test / CI も全通過するためデプロイするまで気付けない）。リダイレクトを拒否したい場合は `"manual"` を使い、`!response.ok`（3xx が status に出る）で弾く
- HTTP invocation の `ctx.waitUntil()` は応答後 **30 秒**上限（cron の wall-clock 15 分・CPU 時間上限とは別枠）。外部 API のリトライ等で超え得る処理は Queue（consumer は wall-clock 15 分）へ逃がす
- 挙動が疑わしいランタイム API は `wrangler dev --remote` に最小スクリプトを載せて実機で確定する（ローカル workerd・公式 docs と実機で差が出る）

## wrangler / D1 の落とし穴（実機検証済み）

- **wrangler がタイムアウト系エラー（7429 storage timeout 等）を返しても、D1 側では処理が完遂していることがある**。長時間 DDL（大規模 CREATE INDEX 等）は、sqlite_master・d1_migrations・実クエリで実態を確認してから失敗と断定する
- `wrangler d1 export` は 100KB 超の INSERT 文を吐くが、D1 の SQL 文長上限は 100KB のためそのまま import できない（silent fail に見える）。大行はチャンク分割 INSERT ＋連結 UPDATE が必要
- `wrangler d1 export` の CREATE TABLE 順は FK 依存順でない。FK 有効な D1 へ直接 import せず、migrations 適用後に data-only で投入する
- `wrangler deployments list` は最新が**末尾**（先頭ではない）
- `wrangler r2 object` に `list` サブコマンドはない（get / put / delete のみ。一覧はダッシュボードか API で）
- vitest-pool-workers のストレージ分離は**テストファイル単位**（同一ファイル内のテスト間では D1 / R2 が共有される）。一意 ID ＋ beforeEach クリーンアップで衝突を避ける
