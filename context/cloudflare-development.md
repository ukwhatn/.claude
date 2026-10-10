# Cloudflare (wrangler) 開発ガイド

Read when: Cloudflare（wrangler / Workers / D1 / R2）を触る前。

## セットアップ・アカウント

- wranglerはbunでインストールする（`bun add -d wrangler`）
- **CRITICAL: 複数のCloudflareアカウントが存在する。デプロイ先アカウントは必ずユーザーに確認する**（推測・仮定は禁止）。`bunx wrangler whoami` で利用可能なアカウント一覧を確認してから提示・質問する。PJ CLAUDE.mdまたはpackage.jsonに `CLOUDFLARE_ACCOUNT_ID` が明記されている場合はそれを使う

## cf CLI（Cloudflare公式の新しいCLI）

- npmパッケージ `cf`（github.com/cloudflare/cf）。学習時点より新しく、手持ちの知識に無い前提で扱う。`command -v cf` で有無を確かめ、無ければ導入をユーザーに確認する。認証は `cf auth login`（状態は `cf auth whoami`）、アカウントは `CLOUDFLARE_ACCOUNT_ID` で選ぶ
- **wranglerに無い操作と、ダッシュボードでしかできないと思える操作は、cfで自分で行う**。cfはCloudflare APIの大半を覆う（Workers Buildsのトリガー作成・ビルド一覧とログ、Observabilityのクエリ、AI Gateway、アカウントのメンバー・APIトークン、DNS、キャッシュのpurgeなど）。ダッシュボードでの作業をユーザーに頼む前に、cfでできるかを確かめる（頼んだ作業が済むまで後続が止まり、済んだかの確認も漏れやすいため）
- コマンドは `cf cli search "<やりたい操作と対象の種類>"` で探し、見つけたコマンドの `--help` を読む。`--help` を入れ子にたどって探さない（CLI自身がエージェントにそう指示している）。検索語に名前・ID・ドメイン・トークンを入れない。APIの詳細は、見つけたコマンドの先頭の `cf` を `cf schema` に替えて引く
- 設定を書き換えるコマンドは、`--dry-run` があれば先に流して送信内容を確かめる（全体を置き換える更新では、渡さなかった設定が初期値に戻る）
- デプロイ先アカウントの確認と、対外に効く変更の事前確認はwranglerと同じ扱いにする

## Workersランタイムの落とし穴（実機検証済み）

- **`fetch()` の `redirect` は `follow` / `manual` のみ。`"error"` は未実装**で、指定すると即 `TypeError: Invalid redirect value, must be one of "follow" or "manual"`（公式docsは3値とも有効値として記載、TS型も受理、lint / typecheck / test / CIも全通過するためデプロイするまで気付けない）。リダイレクトを拒否したい場合は `"manual"` を使い、`!response.ok`（3xxがstatusに出る）で弾く
- HTTP invocationの `ctx.waitUntil()` は応答後 **30秒**上限（cronのwall-clock 15分・CPU時間上限とは別枠）。外部APIのリトライ等で超え得る処理はQueue（consumerはwall-clock 15分）へ移す
- 挙動が疑わしいランタイムAPIは `wrangler dev --remote` に最小スクリプトを載せて実機で確定する（ローカルworkerd・公式docsと実機で差が出る）

## wrangler / D1の落とし穴（実機検証済み）

- **wranglerがタイムアウト系エラー（7429 storage timeout等）を返しても、D1側では処理が完遂していることがある**。長時間DDL（大規模CREATE INDEX等）は、sqlite_master・d1_migrations・実クエリで実態を確認してから失敗と断定する
- **本番D1を止めないため、運用中のDBに `wrangler d1 export --remote` を実行しない**。exportの実行中は同じDBへの他のリクエストがすべてブロックされ、アプリが応答不能になる（公式docs「Import and export data」: "A running export will block other database requests."）。本番データの集計は、期間・件数を絞った `d1 execute --remote` のSELECTを直列に投げて行う。委譲の指示書にもexportを手段として書かない
- `wrangler d1 export` は100KB超のINSERT文を吐くが、D1のSQL文長上限は100KBのためそのままimportできない（エラーを出さずに失敗したように見える）。大行はチャンク分割INSERT ＋連結UPDATEが必要
- `wrangler d1 export` のCREATE TABLE順はFK依存順でない。FK有効なD1へ直接importせず、migrations適用後にdata-onlyで投入する
- `wrangler deployments list` は最新が**末尾**（先頭ではない）
- `wrangler r2 object` に `list` サブコマンドはない（get / put / deleteのみ。一覧はダッシュボードかAPIで）
- vitest-pool-workersのストレージ分離は**テストファイル単位**（同一ファイル内のテスト間ではD1 / R2が共有される）。一意ID ＋ beforeEachクリーンアップで衝突を避ける
