# Agent Teams 活用ガイド

## 概要

Agent Teams（TeamCreate/SendMessage/TeamDelete）は複数のClaudeインスタンスを並列協調させるマルチエージェント機能。各チームメイトは独立したコンテキストウィンドウを持ち、共有タスクリストとメッセージングで自己調整する。

**状態**: 実験的機能（`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` で有効化済み）

## 発動条件（限定発動）

Opus 4.7 ベストプラクティスに従い、Agent Teams は**限定発動**。
以下のいずれかを満たす場合のみ使用する。それ以外は**モデル判断**（直接実装または単発Subagent）に委ねる。

- (a) **複数ファイル並列**: 5+ファイルの変更が見込まれ、独立に編集できる
- (b) **独立タスク3つ以上**: 互いに依存しないタスクが3つ以上ある
- (c) **ユーザー明示指示**: ユーザーが「チームで」「Agent Teamsで」等と明示

過度な明示的呼び出しは性能低下の原因になるため、(a)(b)(c) のいずれにも該当しないタスクでは Agent Teams を発動しない。

## Agent Teams vs Subagents（Task tool）vs 直接実装の使い分け

| ケース | 推奨手法 |
|-------|---------|
| 上記 (a)(b)(c) に該当 | Agent Teams |
| 独立した調査・コンテキスト分離が必要 | 単発Subagent（Task tool） |
| 上記いずれでもない通常の実装 | 直接実装（モデル判断） |
| codebase-reviewの6観点並列レビュー | 並列Subagent（独立、議論不要） |
| 複数ファイルの独立した調査 | 並列Subagent（結果をメインに返すだけ） |

### 直接実装が適切な場面

- 1〜数ファイルの編集
- 既知の単純なバグ修正
- 文書更新
- 実装ステップが少なく、context compactionの懸念が低い作業

これらは Agent Teams を起動せず、自分で直接実装する。

### Subagents（Task tool）が適切な場面

- 独立した調査タスクを並列に走らせたい
- メインコンテキストを汚さず大量のファイルを読みたい
- 結果を要約して返してほしい

### Agent Teams が適切な場面（発動条件下）

- 議論・情報共有が必要な並行作業
- インターフェース調整を伴う cross-layer 実装
- 長時間タスクで context compaction の懸念が高い場合
- 同種の独立タスクが3つ以上あり、並列化のメリットが大きい

## Lead Orchestration パターン（Agent Teams 発動時）

Agent Teams 発動条件を満たす場合、leadは原則として以下に専念する:
- タスク管理（TaskCreate/TaskUpdate/TaskList）
- チームメイトのspawn・アサイン・shutdown
- 進捗監視と05_log.mdへの記録
- 品質チェック・agent review

ただし、leadが直接実装した方が明らかに効率的なファイルや、方針判断を伴う中核ファイルは、自身で編集して構わない。「leadは絶対にコードを書かない」という強制ルールではない。

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

**Task tool の使用範囲（IMPORTANT）:**
- implementer は **自分に割り当てられた既存タスク**の TaskUpdate（status 変更・metadata 追記）のみ許可
- **TaskCreate（新規タスク作成）は禁止**。impl 側の内部進捗管理を task list に流用すると lead の view が汚れる（例: impl-sync-backend が #32-#41 を自作した実例あり）
- impl の内部進捗は完了報告のサマリ or 05_log.md への追記で表現する

**並列 spawn 時のファイル分担（IMPORTANT）:**
- 「同一ファイルの編集をチームメイト間で分担しない」（本ファイル末尾の既存原則）の具体化
- backend 共有ファイル（例: `routes/*.ts` 集約、`migrations/`、`packages/shared/schema/`、`_journal.json` 等）は分担境界が曖昧で並列衝突が起きやすい。lead は spawn 前に:
  1. 各 impl の担当ファイルを明示リストアップ
  2. 共有ファイル（複数領域が集約されている）は **backend / frontend で担当を分離**、または **順次実行**に切替
  3. `git add <file>` レベルで staged file を選別する運用を prompt に明示（`git add -A` 禁止）
- pre-commit hook の巻き添え（他 impl WIP で lint fail）は `--no-verify` 相当の環境変数（`HUSKY=0` 等）で回避する場合、その正当性（自分の変更範囲は事前に clean 確認済）と副作用（他 impl の WIP を巻き込みうる）を必ず 05_log.md に記録

## チームワークフロー

### 基本手順

```
1. TeamCreate(team_name: "<name>", description: "<purpose>")
2. TaskCreate で共有タスクを作成
3. Task tool でチームメイトをspawn（subagent_type指定）
4. SendMessage(type: "message") で指示・情報共有
5. チームメイトがTaskUpdateでタスク完了
6. SendMessage(type: "shutdown_request") で各チームメイトをシャットダウン
7. 全員シャットダウン後、TeamDelete でクリーンアップ
```

### チームメイトのspawn

```
Task(
  prompt: "タスクの説明",
  subagent_type: "general-purpose",
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

## エージェントロール一覧

以下のロールはgeneral-purposeサブエージェントにインライン指示で付与する。
専用の定義ファイルは不要（旧`~/.claude/agents/`は廃止済み）。

| ロール | 用途 | 推奨ツール制限（インライン指示で明示） |
|--------|------|--------------------------------------|
| researcher | 調査専門（context7/WebSearch活用） | Write/Edit不可 |
| implementer | 実装専門（計画に従った実装） | 制限なし |
| reviewer | レビュー専門（バグ/セキュリティ/パフォーマンス） | Write/Edit不可 |
| test-writer | テスト作成専門（既存パターン踏襲） | 制限なし |

## チーム構成パターン（発動条件下の構成例）

### パターン0: Lead Orchestration

```
lead（オーケストレーション）
  ├─→ impl-01（Task 1実装）→ 完了報告 → shutdown
  ├─→ impl-02（Task 2実装）→ 完了報告 → shutdown
  └─→ impl-03, impl-04（並列実行）→ 完了報告 → shutdown
```

- 独立タスクが3つ以上あるときの基本構成
- 各implementerは独立インスタンスでCLAUDE.mdの指示を直接読み込む
- context compaction発生時もimplementerの作業品質に影響なし

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

### パターン5: Review + Fix ループ（agent review自動化）

```
lead（オーケストレーション）
  ├─→ reviewer（長寿命: agent CLI実行）
  │     ├─ R1: agent -p ... | jq → leadに指摘報告
  │     ├─ R2: --resume → leadに報告
  │     └─ Rn: 指摘なし → leadに報告
  │
  └─→ implementer（長寿命: 修正担当）
        ├─ R1の修正
        ├─ R2の追加修正
        └─ 全修正完了 → leadに報告
```

- reviewerはagent CLIセッションを --resume で継続し、レビュー文脈を保持
- implementerは複数ラウンドの修正をコンテキスト付きで処理
- leadはSeverity判断とオーケストレーションに専念
- 打ち切り条件: Action Required = 0 / 同一指摘2R連続 / 安全上限5R

## チームメイトのライフサイクル

shutdownタイミングは「タスク完了時」ではなく「役割完了時」:
- reviewer: 全レビューラウンド完了後（Phase 2→4を跨いで存続可能）
- implementer: 担当する連続タスク群・修正ラウンド群が全て完了後
- researcher: 調査フェーズ完了後

理由: コンテキスト保持により、前回作業を参照した質の高い作業が可能。
spawn/shutdownのオーバーヘッドも削減される。

## コスト考慮

- 各チームメイトは独立したClaudeインスタンス（コンテキスト×チームメイト数）
- **実用的な上限: 3-5人**
- 役割が完了したチームメイトにshutdown_requestを送信
- 単純なタスクにはSubagents（Task tool）または直接実装でコストを抑える

## 待機パターン（CRITICAL）

Teammate/Subagentの完了を待つ際、以下のルールに従うこと:

**禁止:**
- `sleep` コマンドの使用
- ポーリングループ
- 待機中に不要なツール呼び出しを行うこと
- **idle通知のたびにTaskList/git status/SendMessageで確認・催促すること（マイクロマネジメント禁止）**

**正しい待ち方:**
- Teammate/Subagentをspawnした後、**何もせずターンを終了する**
- 完了報告はシステムにより自動的に次のターンとして配信される
- 配信されたメッセージに応答して次のアクションを実行する

**idle通知への対応:**
- idle通知は通常イベント。催促メッセージを送らない（チームメイトは自律的に進む）
- SendMessageが必要なケース: チームメイトが**明示的に質問・ブロック報告を送ってきた場合**、または**idle通知が届いたのに期待する最終報告が未着の場合**（後者は作業の催促ではなく成果物の回収。報告フォーマットを再掲して送信を依頼する）
- 進捗確認が必要なケース: **長時間（5分以上）idle状態が続き、かつTaskListでタスクが進んでいない場合のみ**
- **idle 通知が連続で届いても、既に応答済み or 静かに待機で OK の状態なら追加応答不要**（idle は agent 側の自動送信で、SendMessage で「送るな」と指示しても止まらないことがある。ユーザー宛の説明も 1 回で十分）

**interrupted（failure）通知への対応:**
- interrupted は idle と区別する。異常事態のシグナルなので、初回の 1 回だけ状況確認 SendMessage を送るのは正当
- 復帰後（available に戻る）に agent が自ら報告するのが正常フロー。復帰後に催促の SendMessage を追加送信しない
- ユーザーが並行して介入している可能性がある（interrupted の原因が「ユーザーが agent を stop した」ケース）。安易に「復帰可否」を lead 判断で決めず、ユーザー説明を待つのが安全

## Context Compaction後の状態復元（CRITICAL）

Context compaction発生時、team-leadの会話履歴が要約に置き換わるが、チームメイトのプロセスとディスク上の状態ファイルは影響を受けない。

### compaction後に必ず実行すること

1. **チーム設定の再確認**:
   ```
   Read(~/.claude/teams/{team-name}/config.json)
   ```

2. **タスク状態の再確認**: `TaskList()`

3. **重複spawnの禁止**:
   - team configに存在するチームメイトは**絶対に再spawnしない**
   - `in_progress` のタスクを持つチームメイトは作業中であり、完了メッセージを待つ

## 注意事項

- 同一ファイルの編集をチームメイト間で分担しない（上書き競合の原因）
- チームメイトはCLAUDE.mdを読み込むが、リードの会話履歴は引き継がない
- agent reviewはreviewerチームメイトがBash経由で自動実行する（@context/agent-cli-guide.md参照）
- チームメイトの名前（name）で参照する（agentIdは使用しない）
- broadcastはコスト高（N人 = N回のAPI呼び出し）、必要な場合のみ使用
- TeamDeleteは全チームメイトのシャットダウン完了後のみ実行可能
