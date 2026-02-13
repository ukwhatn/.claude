# Agent Teams 活用ガイド

## 概要

Agent Teams（TeamCreate/SendMessage/TeamDelete）は複数のClaudeインスタンスを並列協調させるマルチエージェント機能。各チームメイトは独立したコンテキストウィンドウを持ち、共有タスクリストとメッセージングで自己調整する。

**CRITICAL: Agent Teams + Leadオーケストレーションは、あらゆる実装タスクのデフォルト動作。**
leadは自分でコードを書かず、オーケストレーションに専念する。
これにより、context compactionによる指示の忘却、品質の乱れ、ワークフロー/ログ記録の欠落を防止する。

**状態**: 実験的機能（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` で有効化済み）

## Lead Orchestrationパターン（デフォルト）

**CRITICAL: すべての実装タスクでこのパターンを使用する。**

### 概要

leadはコード実装を一切行わず、以下に専念する:
- タスク管理（TaskCreate/TaskUpdate/TaskList）
- チームメイトのspawn・アサイン・shutdown
- 進捗監視と05_log.mdへの記録
- 品質チェック・agent review

### ワークフロー

```
Phase 0: TeamCreate → TaskCreate（依存関係付き）
Phase 1: 調査（researcher or 自身）
Phase 2: 計画作成 → agent review
Phase 3: implementerチームメイトをspawn → タスクアサイン → 完了待ち → 次タスク
Phase 4: 品質チェック + agent review
Phase 5: 全チームメイトshutdown → TeamDelete → 完了報告
```

### Phase 3の詳細手順

1. 依存関係のないタスク（または先頭タスク）のimplementerをspawn
2. implementerにTaskUpdateでタスクをアサイン
3. implementerの完了報告を待つ（sleepやポーリング禁止）
4. 完了報告を受信 → 05_log.mdに記録
5. 依存が解消された次のタスクのimplementerをspawn（並列可能なら同時spawn）
6. 全タスク完了まで繰り返し
7. 全implementerにshutdown_requestを送信

### implementerチームメイトへの指示テンプレート

```
あなたは「{team_name}」チームのimplementerです。

## 担当タスク
TaskID: {taskId} - {subject}

## 実装内容
{タスクの詳細説明}

## 計画ファイル
{計画ファイルパス}を参照してください。

## 作業手順
1. 計画ファイルの該当タスクを読む
2. 必要に応じてcontext7/WebSearchで公式仕様を調査
3. 実装
4. 品質チェック（PJ CLAUDE.mdのコマンド参照）
5. コミット（git-cz形式）
6. TaskUpdate(taskId, status: "completed")
7. leadにSendMessageで完了報告
```

### 例外: Agent Teamsを使わなくてよい場合

以下の**すべて**を満たす場合のみ、leadが直接実装してよい:
- 変更ファイルが1-2個
- 実装ステップが3以下
- context compactionのリスクがない（短いタスク）

## Agent Teams vs Subagents（Task tool）の使い分け

### 判断基準

| 判断ポイント | → Agent Teams | → Subagents |
|-------------|---------------|-------------|
| 実装タスク（デフォルト） | **Yes** | - |
| チームメイト間の議論・情報共有が必要 | Yes | - |
| 結果を返すだけで十分 | - | Yes |
| 同一モジュールのインターフェース調整が必要 | Yes | - |
| トークンコストを最小限にしたい | - | Yes |
| 各作業者が完全独立で短い | - | Yes |

### 具体例

**Agent Teamsが有効な場面（デフォルト）:**
1. **あらゆる実装タスク**（Lead Orchestrationパターン）
2. 調査+実装の並行作業（researcherとimplementerが情報共有しながら）
3. competing hypotheses型デバッグ（複数仮説を並列検証、互いに反論）
4. cross-layer implementation（frontend/backend/testの分担、インターフェース調整）
5. レビュー+修正の並行作業（code-reviewerの発見をimplementerが即修正）

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

## Phase 0-5との統合（CRITICAL: デフォルト動作）

| Phase | leadの動作 |
|-------|-----------|
| Phase 0 | TeamCreate → TaskCreate（依存関係付き） |
| Phase 1 | 調査（researcher or 自身） |
| Phase 2 | 計画作成 → agent review |
| Phase 3 | **implementerチームメイトをspawn → タスクアサイン → 完了待ち → 次タスク**（leadはコード実装しない） |
| Phase 4 | 品質チェック + code-reviewerチームメイト + agent cli (gpt-5.2-high) でレビュー |
| Phase 5 | 全チームメイトshutdown → TeamDelete → 完了報告 |

**IMPORTANT**: 05_log.mdへの記録はAgent Teams使用時も必須（leadが記録する）。

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

### パターン0: Lead Orchestration（デフォルト）

```
lead（オーケストレーション専念）
  ├─→ impl-01（Task 1実装）→ 完了報告 → shutdown
  ├─→ impl-02（Task 2実装）→ 完了報告 → shutdown
  ├─→ impl-03（Task 3実装）→ 完了報告 → shutdown  ← impl-02完了後にspawn
  └─→ impl-04, impl-05（並列実行）→ 完了報告 → shutdown
```

- **デフォルトの実装パターン**
- leadはコード実装を一切行わず、タスク管理に専念
- 各implementerは独立インスタンスでCLAUDE.mdの指示を直接読み込む
- context compaction発生時もimplementerの作業品質に影響なし
- タスク依存関係に基づいて順次/並列でimplementerをspawn
- implementerは完了後にshutdown_requestで終了

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

## Context Compaction後の状態復元（CRITICAL）

Context compaction（コンテキスト圧縮）が発生すると、team-leadの会話履歴が要約に置き換えられ、spawn済みチームメイトの詳細を失う可能性がある。**ただし、チームメイトのプロセスとディスク上の状態ファイルはcompactionの影響を受けない。**

### compaction後に必ず実行すること

1. **チーム設定の再確認**:
   ```
   Read(~/.claude/teams/{team-name}/config.json)
   ```
   - `members` 配列で現在のチームメイト一覧を確認
   - 既にspawn済みのチームメイトを把握

2. **タスク状態の再確認**:
   ```
   TaskList()
   ```
   - `status: "in_progress"` かつ `owner` が設定されているタスク = 作業中のチームメイト
   - `status: "completed"` のタスク = 完了済み

3. **重複spawnの禁止**:
   - team configに存在するチームメイトは**絶対に再spawnしない**
   - `in_progress` のタスクを持つチームメイトは作業中であり、完了メッセージを待つ
   - 不明な場合はSendMessageで当該チームメイトに状況を確認する

### compaction発生の検知

以下の状況でcompactionが発生した可能性がある:
- 会話の途中で以前の詳細な経緯が想起できない
- チームメイトのspawn状況が不明確

**このような場合、新しいアクションを取る前に上記の確認手順を必ず実行すること。**

## 注意事項

- 同一ファイルの編集をチームメイト間で分担しない（上書き競合の原因）
- チームメイトはCLAUDE.mdを読み込むが、リードの会話履歴は引き継がない
- agent cli (gpt-5.2-high) レビューはAgent Teamsとは別に実施（Phase 4）
- チームメイトの名前（name）で参照する（agentIdは使用しない）
- broadcastはコスト高（N人 = N回のAPI呼び出し）、必要な場合のみ使用
- TeamDeleteは全チームメイトのシャットダウン完了後のみ実行可能
