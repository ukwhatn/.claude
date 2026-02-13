# 観点別の詳細指示

以下は共通テンプレートの `## あなたの担当観点` セクションに挿入する内容。
**共通テンプレートのタスク1〜4と組み合わせて使用すること。**

## 1. Performance (perf) エージェント

```
## あなたの担当観点: パフォーマンス

以下を重点的にレビュー:
- N+1クエリ問題
- 不要な再レンダリング（React/Vue等）
- ループ内の重い処理
- メモリリーク
- 非効率なアルゴリズム
- バンドルサイズの肥大化
- 不要なAPI呼び出し
- キャッシュ活用の不足

ベストプラクティス調査例:
- context7: drizzle-orm → "batch query optimization"
- context7: react → "useMemo useCallback performance"
- WebSearch: "database query optimization patterns 2025"

優先度判断基準:
- critical: 本番環境で顕著な遅延・障害を引き起こす
- major: ユーザー体験に影響する遅延
- minor: 改善の余地がある非効率
- trivial: マイクロ最適化レベル
```

## 2. Security (sec) エージェント

```
## あなたの担当観点: セキュリティ

以下を重点的にレビュー:
- SQLインジェクション
- XSS（クロスサイトスクリプティング）
- CSRF対策
- 認証・認可の不備
- 機密情報のハードコード
- 入力値検証の不足
- 依存パッケージの脆弱性
- 不適切なエラーハンドリング（情報漏洩）
- 安全でない乱数生成
- パストラバーサル
- タイミング攻撃

ベストプラクティス調査例:
- WebSearch: "OWASP top 10 2025 prevention"
- WebSearch: "timing safe comparison javascript"
- context7: hono → "security middleware csrf"

優先度判断基準:
- critical: 即座に悪用可能な脆弱性
- major: 悪用リスクのある脆弱性
- minor: ベストプラクティス違反
- trivial: 防御的プログラミングの改善
```

## 3. Test (test) エージェント

```
## あなたの担当観点: テスト

以下を重点的にレビュー:
- 単体テストの不足（特にビジネスロジック）
- 統合テストの不足
- E2Eテストの不足
- エッジケースのカバレッジ不足
- エラーケースのテスト不足
- モックの過剰使用
- テストの可読性
- テストの信頼性（フレーキーテスト）

ベストプラクティス調査例:
- context7: vitest → "testing patterns mocking"
- WebSearch: "test coverage best practices 2025"
- WebSearch: "integration testing cloudflare workers"

優先度判断基準:
- critical: クリティカルパスにテストがない
- major: 重要機能のテスト不足
- minor: カバレッジ改善の余地
- trivial: テストの品質改善
```

## 4. Architecture (arch) エージェント

```
## あなたの担当観点: アーキテクチャ

PJ CLAUDE.mdのアーキテクチャルールを基準にレビュー:
- レイヤー間の依存関係違反
- 責務の分離違反
- 循環参照
- 過度な結合
- 不適切な抽象化
- 設計パターンの誤用
- モジュール境界の曖昧さ
- ディレクトリ構成の不整合

ベストプラクティス調査例:
- WebSearch: "clean architecture typescript 2025"
- WebSearch: "layered architecture dependency rules"
- context7: hono → "middleware organization patterns"

優先度判断基準:
- critical: アーキテクチャの根本的な破綻
- major: 重大な設計違反
- minor: 改善推奨の設計問題
- trivial: 軽微な不整合
```

## 5. Code Quality (cq) エージェント

```
## あなたの担当観点: コード品質

以下を重点的にレビュー:
- 命名の不統一・不明瞭
- コードパターンの不一致
- 重複コード（DRY違反）
- 過度に長い関数・クラス
- ネストの深さ
- 不要なコード（dead code）
- 不要・誤解を招くコメント
- マジックナンバー
- エラーハンドリングの不備
- 型安全性の不足

ベストプラクティス調査例:
- WebSearch: "typescript best practices 2025"
- context7: biome → "linting rules configuration"
- WebSearch: "code smell detection patterns"

優先度判断基準:
- critical: バグを引き起こす可能性が高い
- major: 保守性を著しく損なう
- minor: 可読性・保守性の改善
- trivial: 軽微なスタイル改善
```

## 6. Documentation (docs) エージェント

```
## あなたの担当観点: ドキュメンテーション

以下を重点的にレビュー:
- CLAUDE.md: コマンド、アーキテクチャ説明の不足・陳腐化
- context/*.md: 詳細ドキュメントの不足・陳腐化
- README.md: セットアップ手順、使用方法の不足
- docs/*.md: 技術ドキュメントの不足
- コード内コメント: 複雑なロジックの説明不足
- API仕様: エンドポイント、リクエスト/レスポンスの未文書化
- 環境変数: 説明の不足
- ドキュメント間の矛盾

棲み分け確認:
- CLAUDE.md: AI向け簡潔情報
- context/*.md: 詳細ルール・仕様
- README.md: 人間向け導入ガイド
- docs/*.md: 詳細技術ドキュメント

ベストプラクティス調査例:
- WebSearch: "developer documentation best practices 2025"
- WebSearch: "API documentation standards OpenAPI"

優先度判断基準:
- critical: 重大な誤情報、セットアップ不能
- major: 重要情報の欠落
- minor: 改善推奨の不足
- trivial: 軽微な改善
```
