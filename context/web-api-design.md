# Web API 設計ガイド（標準・デファクト準拠）

HTTP API（REST/JSON API）の外部仕様 — エラー形式・日時・認証/認可・バージョニング・廃止告知・ページネーション・レートリミット・冪等キー・API記述 — を**新規に決める・変更するとき**に読む。記載内容は一次資料（RFC Editor / IETF Datatracker / 公式仕様）で検証済み（検証: 2026-08）。

## 適用順序（CRITICAL）

1. **PJ の既存実装・既存パターンが第一優先**。同一サービス内で形式を混在させない（既存 API が独自エラー形式なら、新エンドポイントもそれに合わせる）。既存形式から標準形式への移行は機構・外部仕様の変更なので、提案したうえでユーザー確認を取る（AGENTS.md「規約遵守」「緩和しない安全項目」）
2. PJ CLAUDE.md・PJ 規約の規定が次点
3. **どちらにも前例・規定がない「自由に決められる場面」でのみ、本ガイドの標準・デファクトを既定として採用する**（新規サービス・新規 API 面・既存に該当領域の前例がない決定）

## 早見表

| 領域 | 既定の選択 | 根拠 |
|---|---|---|
| エラーレスポンス | Problem Details（`application/problem+json`） | RFC 9457（obsoletes 7807） |
| 日時フォーマット | RFC 3339（UTC は `Z` サフィックス） | RFC 3339 |
| メソッド・ステータスコード | RFC 9110 を参照して選ぶ | RFC 9110（Internet Standard, STD 97） |
| 認可フロー | Authorization Code + PKCE | RFC 9700（BCP 240） |
| ログイン（認証） | OpenID Connect を上乗せ | OIDC Core（OAuth 単体は認可であって認証ではない） |
| バージョニング | 社内/自社向け: パス `/v1` ・ 外部公開: 日付ベース | 標準なし（デファクト） |
| 廃止告知 | `Deprecation` + `Sunset` + `Link` ヘッダ | RFC 9745 / RFC 8594 / RFC 8288 |
| ページネーション | カーソル方式 + `Link: rel="next"` | 標準なし（デファクト）+ RFC 8288 |
| レートリミット | `429` + `Retry-After` + `X-RateLimit-*` | RFC 6585 + デファクト |
| 冪等キー | `Idempotency-Key` ヘッダ（Stripe 仕様準拠） | デファクト（IETF draft は失効） |
| API 記述 | OpenAPI 3.x | デファクト（OpenAPI Initiative） |

## 各領域の要点

### エラーレスポンス — RFC 9457 Problem Details

- media type は `application/problem+json`。メンバーは `type`（エラー種別を識別する URI）/ `title` / `status` / `detail` / `instance`
- HTTP ステータスコード（トランスポート層の機械分岐）と `type`（アプリ固有エラーの識別子）の二層で表現する。独自のエラー封筒（`{"error": {...}}` 等)を新規に発明しない
- 拡張メンバー（バリデーションエラーの `errors` 配列等）の追加は仕様上公認されている
- フレームワーク対応: Spring Boot 3（`ProblemDetail`、opt-in）・ASP.NET Core（既定で対応）は組み込みあり。NestJS / Express / Fastify / Hono は組み込みなし（自前で形式を揃える）

### 日時フォーマット — RFC 3339

- API 境界の日時は RFC 3339 で受け渡す。サーバは UTC（`Z`）で返し、タイムゾーンのローカライズはクライアント側の責務とする
- Unix タイムスタンプの数値や独自形式（`YYYY/MM/DD` 等）を新規 API に採用しない

### メソッド・ステータスコード — RFC 9110

- HTTP セマンティクスの現行仕様は RFC 9110/9111/9112（2022 年再編、9110 は Internet Standard / STD 97）。メソッド・ステータスコードの選択に迷ったら RFC 9110 を参照する
- `429 Too Many Requests` の出典は RFC 6585
- RFC 2616 や RFC 7231 を根拠に引く資料は 1〜2 世代前。設計根拠は RFC 9110 に読み替える

### 認証・認可 — RFC 9700（BCP 240）

- 認可コードフローに PKCE を付けるのが全クライアント種別の既定。パブリッククライアント（SPA・モバイル）では PKCE 必須
- **ROPC（password グラント）は MUST NOT**。Implicit グラントも新規採用しない（SPA も Authorization Code + PKCE）
- OAuth 2.1 は Internet-Draft 段階（2026-08 時点 rev 15）。RFC 化を待つ必要はなく、従うべき発行済み文書は RFC 9700
- ログイン（ユーザー認証）用途は OAuth 2.0 単体で済ませず OpenID Connect を使う

### バージョニング（標準なし・デファクト）

- 利用者が社内・自社アプリに限られる API: パスに `/v1`（Google AIP-185 / Microsoft 型）。破壊的変更の頻度が低ければ弱点（v1 併存の長期化）は顕在化しない
- 不特定多数の外部開発者向け API: 日付ベース（GitHub / Stripe / Shopify 型）。利用者が自分のペースで小刻みに追従できる
- バージョニング方式は外部仕様であり後からの変更は全クライアント改修になるため、API 公開前に確定させる

### 廃止告知 — RFC 9745 / RFC 8594

- 非推奨化の告知はレスポンスヘッダで機械可読に行う（ブログ・メール通知は実行中のコードに届かない）:
  - `Deprecation: @<unixtime>`（RFC 9745、構造化フィールドの Date 型。「いつから非推奨か」）
  - `Sunset: <HTTP-date>`（RFC 8594、Informational。「いつ停止するか」）
  - `Link: <移行ガイドURL>; rel="deprecation"`（RFC 8288）

### ページネーション（標準なし・デファクト: カーソル方式）

- 既定はカーソル方式（`WHERE id < :cursor ... LIMIT n` 型）。深いページでも一定速度で、閲覧中の挿入・削除で重複・読み飛ばしが起きない
- オフセット方式は深いページで線形に劣化しズレも起きる。「N ページ目へジャンプ」が要件の画面（管理画面等）に限って選ぶ
- 次ページの伝達は `Link` ヘッダの `rel="next"`（RFC 8288、GitHub 型）またはボディ内の next cursor。同一 PJ 内では既存の伝達方式に合わせる
- ページネーション方式も外部仕様のため、最初のリリース前に確定させる

### レートリミット — RFC 6585 + デファクト

- 超過時は `429 Too Many Requests` を返し、回復までの時間を `Retry-After` で伝える
- 残量ヘッダの標準はまだない。現時点のデファクトは `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset`
- IETF httpapi WG の draft（`RateLimit` / `RateLimit-Policy` ヘッダ、2026-08 時点 rev 11・Active）は RFC 化まで採用しない（draft のヘッダ名・構文は変わり得るため）

### 冪等キー — `Idempotency-Key`（Stripe 仕様準拠）

IETF draft は失効済み（2026-08 時点 rev 07・Expired）。Stripe 実装を事実上の仕様として踏襲する:

- 対象は POST のみ（GET / DELETE は定義上冪等。キーを付けない）
- キーはクライアント生成のランダム文字列（UUID v4 目安、最大 255 字、メールアドレス等の機微情報を使わない）
- 同一キーの再送には初回リクエストの結果（失敗・500 含む）をそのまま返す
- 同一キーで異なるパラメータが来たらエラーを返す
- バリデーション失敗等でエンドポイント実行前に終わったリクエストは結果を保存しない（クライアントはリトライできる）
- 保持期間は 24 時間目安。恒久的な重複排除でなく「リトライを短期間で安全にする」仕組みとして設計する

### API 記述 — OpenAPI 3.x

- API 記述のデファクトは OpenAPI（2026-08 時点の最新は 3.2.0）。呼称は「OpenAPI」を使う（「Swagger」は 2.0 時代の呼称）
- スキーマを真実源にし、型付きクライアント・サーバスタブ・ドキュメントの生成起点とする（ドキュメントは副産物）
- レスポンス形式は JSON 固定が主流。`Accept` ヘッダでの JSON/XML 切替は新規採用しない。形式の多様性が要る場面は gRPC/Protocol Buffers（サービス間）・GraphQL（クライアント主導のフィールド選択）へ

## 標準がない領域の調べ方

新しい設計判断で本ガイドに該当領域がない場合、次の順で調べる:

1. RFC Editor（rfc-editor.org）— 発行済み RFC があるか
2. IETF Datatracker — 標準化進行中か（Web API 周辺の集約地は httpapi WG）。draft は rev とステータス（Active/Expired）を必ず確認する
3. 大手 API の現物（GitHub / Stripe）— デファクトの実装
4. 設計ガイド: Google AIP（番号付きルール集・体系性）、Zalando RESTful API Guidelines（理由の説明が厚い）

## 鮮度の注意

本ガイドの draft 状態（rev・Active/Expired）と「最新バージョン」表記はすべて 2026-08 時点。draft 由来の記述を設計根拠にする前に Datatracker で現況を再確認する。
