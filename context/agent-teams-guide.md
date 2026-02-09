# Agent Teams 活用ガイド

## 概要

Agent Teams（TeamCreate/SendMessage/TeamDelete）は複数のClaudeインスタンスを並列協調させるマルチエージェント機能。各チームメイトは独立したコンテキストウィンドウを持ち、共有タスクリストとメッセージングで自己調整する。

**状態**: 実験的機能（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` で有効化済み）

## Agent Teams vs Subagents（Task tool）の使い分け

### 判断基準

| 判断ポイント | → Agent Teams | → Subagents |
|-------------|---------------|-------------|
| チームメイト間の議論・情報共有が必要 | Yes | - |
| 結果を返すだけで十分 | - | Yes |
| 同一モジュールのインターフェース調整が必要 | Yes | - |
| トークンコストを抑えたい | - | Yes |
| 各作業者が完全独立 | - | Yes |

### 具体例

**Agent Teamsが有効な場面:**
1. 調査+実装の並行作業（researcherとimplementerが情報共有しながら）
2. competing hypotheses型デバッグ（複数仮説を並列検証、互いに反論）
3. cross-layer implementation（frontend/backend/testの分担、インターフェース調整）
4. レビュー+修正の並行作業（code-reviewerの発見をimplementerが即修正）

**Subagents（Task tool）が適切な場面:**
1. codebase-reviewの6観点並列レビュー（各レビュアーは独立、議論不要）
2. 複数ファイルの独立した調査（結果をメインに返すだけ）
3. 単発の短いタスク（結果が要約されて返る）

## チームワークフロー

### 基本手順

```
1. TeamCreate(team_name: "<name>", description: "<purpose>")
2. TaskCreate で共有タスクを作成
3. Task tool でチームメイトをspawn（subagent_type指定 or カスタムエージェント名）
4. SendMessage(type: "message") で指示・情報共有
5. チームメイトがTaskUpdateでタスク完了
6. SendMessage(type: "shutdown_request") で各チームメイトをシャットダウン
7. 全員シャットダウン後、TeamDelete でクリーンアップ
```

### チームメイトのspawn

```
Task(
  prompt: "タスクの説明",
  subagent_type: "general-purpose",  # or カスタムエージェント名
  team_name: "<team_name>",
  name: "<teammate_name>"
)
```

### メッセージタイプ

| type | 用途 | 注意 |
|------|------|------|
| `message` | 特定チームメイトへのDM | recipientにname指定（UUID不可） |
| `broadcast` | 全員への一括送信 | コスト高、必要時のみ使用 |
| `shutdown_request` | チームメイトの終了要求 | 相手の承認必須 |
| `shutdown_response` | 終了要求への応答 | request_id必須 |
| `plan_approval_response` | 計画の承認/却下 | plan mode連携 |

## Phase 0-5との統合

| Phase | Agent Teamsでの活用 |
|-------|-------------------|
| Phase 0 | TeamCreate + TaskCreate（チームタスク作成） |
| Phase 1 | researcherチームメイトに調査を委譲 |
| Phase 2 | plannerチームメイトで計画策定（plan approval連携） |
| Phase 3 | implementer + test-writerチームメイトで並列実装 |
| Phase 4 | code-reviewerチームメイト + agent cli (gpt-5.2-high) でレビュー |
| Phase 5 | TeamDelete → 完了報告 |

**IMPORTANT**: 05_log.mdへの記録はAgent Teams使用時も必須。

## カスタムエージェント一覧

| エージェント | 用途 | ツール制限 | memory |
|------------|------|-----------|--------|
| researcher | 調査専門（context7/WebSearch活用） | Write/Edit不可 | user |
| implementer | 実装専門（計画に従った実装） | 制限なし | - |
| code-reviewer | レビュー専門（バグ/セキュリティ/パフォーマンス） | Write/Edit不可 | user |
| test-writer | テスト作成専門（既存パターン踏襲） | 制限なし | - |
| planner | 計画策定専門（リスク評価、実装計画） | Write/Edit不可 | - |

定義ファイル: `~/.claude/agents/`

## チーム構成パターン

### パターン1: 調査+実装

```
researcher → (調査結果をSendMessage) → implementer
```

- researcher: コードベース調査 + ベストプラクティス調査
- implementer: 調査結果に基づいて実装
- 調査と実装を並行して進めることで時間短縮

### パターン2: cross-layer

```
implementer-frontend ←→ implementer-backend ←→ test-writer
         （インターフェースをSendMessageで共有）
```

- 各レイヤーの担当者が独立して実装
- API仕様やインターフェース変更は即座に共有
- ファイルの重複編集を避けること

### パターン3: レビュー+修正

```
code-reviewer → (問題をSendMessage) → implementer
implementer → (修正完了をSendMessage) → code-reviewer（再レビュー）
```

- code-reviewerが変更をレビューし、問題をimplementerに通知
- implementerが修正後、code-reviewerが再レビュー
- Critical/Highの指摘がなくなるまでループ

### パターン4: 仮説検証デバッグ

```
researcher-A（仮説1）
researcher-B（仮説2）  → リードが結論をまとめる
researcher-C（仮説3）
```

- 各researcherが異なる仮説を検証
- 互いにSendMessageで反論・補強
- リードが最終的な結論をまとめる

## コスト考慮

- 各チームメイトは独立したClaudeインスタンス（コンテキスト×チームメイト数）
- **実用的な上限: 3-5人**
- 不要になったチームメイトは即座にshutdown_requestを送信
- 単純なタスクにはSubagents（Task tool）を使用してコストを抑える

## 待機パターン（CRITICAL）

Teammate/Subagentの完了を待つ際、以下のルールに従うこと:

**禁止:**
- `sleep` コマンドの使用（`Bash(command: "sleep ...")`）
- ポーリングループ（`while ... do sleep ... done` 等の定期的ステータス確認）
- 待機中に不要なツール呼び出しを行うこと

**正しい待ち方:**
- Teammate/Subagentをspawnした後、**何もせずターンを終了する**（出力を停止する）
- 完了報告はシステムにより自動的に次のターンとして配信される
- 配信されたメッセージに応答して次のアクションを実行する

**理由:** `sleep` を使用するとプロセスがブロックされ、Teammate/Subagentからの完了報告メッセージを受信できなくなる。ターンを終了して待機状態にすることで、メッセージが即座に配信される。

## 注意事項

- 同一ファイルの編集をチームメイト間で分担しない（上書き競合の原因）
- チームメイトはCLAUDE.mdを読み込むが、リードの会話履歴は引き継がない
- agent cli (gpt-5.2-high) レビューはAgent Teamsとは別に実施（Phase 4）
- チームメイトの名前（name）で参照する（agentIdは使用しない）
- broadcastはコスト高（N人 = N回のAPI呼び出し）、必要な場合のみ使用
- TeamDeleteは全チームメイトのシャットダウン完了後のみ実行可能
