# Taskツール活用ガイド

> Claude Code 専用（TaskCreate/TaskUpdate/TaskList/TaskGet は Claude Code のツール）。Codex では組み込みの plan 機構で代替し、本ガイドは読まなくてよい。

## 概要

TaskCreate/TaskList/TaskGet/TaskUpdateツールを使用して、タスクの進捗管理と可視化を行う。

> 各ツールの引数・状態遷移・依存関係の指定方法はツール自体の説明を参照（TaskCreate/TaskUpdate/TaskList/TaskGetの説明に記載済み）。以下はこのPJでの活用パターンのみを扱う。

## metadataのキー命名例

汎用の使い方はツール説明に記載済み。このPJでの命名慣習の例:
- レビュー結果: `{issues_found: 3, critical: 1}`
- ループ回数: `{loop: 2, session_id: "xxx"}`

## メモリファイルとの関係

| 項目 | メモリファイル | Taskツール |
|------|---------------|-----------|
| 用途 | 詳細な作業ログ | リアルタイム進捗表示 |
| 永続性 | ファイルとして残る | セッション内 |
| 参照 | 後から振り返り | 現在の状態確認 |

**IMPORTANT:** 両方を併用する。Taskツールはメモリファイルを「置き換え」ない。

- 05_log.mdへの記録は引き続き必須
- Taskツールはメモリファイルを「補完」するもの

## 使用場面

### 1. Phase 0-5ワークフロー

各Phaseをタスクとして管理:

```
# Phase 0で全タスクを作成
TaskCreate(subject: "Phase 1: 調査", activeForm: "調査中")
TaskCreate(subject: "Phase 2: 計画", activeForm: "計画中")
TaskCreate(subject: "Phase 3: 実装", activeForm: "実装中")
TaskCreate(subject: "Phase 4: 品質確認", activeForm: "品質確認中")
TaskCreate(subject: "Phase 5: 完了報告", activeForm: "完了報告作成中")

# 依存関係を設定
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
TaskUpdate(taskId: "3", addBlockedBy: ["2"])
...

# 各Phase開始時
TaskUpdate(taskId, status: "in_progress")

# 各Phase完了時
TaskUpdate(taskId, status: "completed")
```

### 2. large-task

サブタスクの依存関係と進捗管理:

```
# /large-task plan でタスク作成
TaskCreate(subject: "Task 01: DB設計", ...)
TaskCreate(subject: "Task 02: API実装", ...)
TaskUpdate(taskId: "2", addBlockedBy: ["1"])

# /large-task implement でタスク更新
TaskUpdate(taskId, status: "in_progress")
# ... 実装 ...
TaskUpdate(taskId, status: "completed")
```

### 3. codebase-review

6観点の並列レビュー進捗表示:

```
# 6つのサブエージェント起動前
TaskCreate(subject: "Performance観点レビュー", activeForm: "パフォーマンス分析中")
TaskCreate(subject: "Security観点レビュー", activeForm: "セキュリティ分析中")
...

# 各サブエージェント完了後
TaskUpdate(taskId, status: "completed", metadata: {issues_found: 3})
```

### 4. agent reviewループ

レビュー履歴の構造化:

```
# 初回
TaskCreate(subject: "agent review: 計画レビュー", metadata: {loop: 1})

# 指摘対応後
TaskUpdate(taskId, metadata: {
  loop: 2,
  session_id: "xxx",
  指摘1: "対応済み",
  指摘2: "スキップ（理由: ...）"
})

# 完了
TaskUpdate(taskId, status: "completed", metadata: {total_loops: 3})
```

## バックグラウンド処理との組み合わせ

ビルド/テスト中の待ち時間を有効活用:

```
# ビルド/テストをバックグラウンドで実行
Bash(command: "npm test", run_in_background: true) → 出力ファイルパスを返す

# 現在のタスクを完了
TaskUpdate(currentTaskId, status: "completed")

# 次のタスクを確認・開始
TaskList()
TaskUpdate(nextTaskId, status: "in_progress")

# 次のタスクの調査を開始
# ...

# バックグラウンド処理の完了は、開始時に返された出力ファイルパスを含む通知で届く
```

**結果取得の注意（IMPORTANT）:**
- bash タスクは開始時に出力ファイルパスが返り、完了時に同じパスを含む通知が来るので、**そのファイルパスをReadで読む**
- **local_agent タスク（Agent toolのサブエージェント）は、Agentの結果を直接使う。`.output`をReadしてはならない**（サブエージェントの全会話transcriptへのsymlinkであり、コンテキストを溢れさせる）
- ログのパターンマッチ等、特定条件の発生を監視したい場合は`Monitor`ツールを使う（stdoutの各行が通知イベントになる）。実行中のバックグラウンドタスク・Monitor・サブエージェントを早期停止したい場合は`TaskStop`（task_idにタスクID/エージェント名/`name@team`のいずれかを渡す）

**活用シーン:**
- `npm install` / `pip install`（依存関係インストール）
- `npm run build`（ビルド）
- `npm test` / `pytest`（テスト実行）
- `claude -p`（agent review）

## セッション間でのタスクリスト共有

タスクリストは`~/.claude/tasks/<task_list_id>/`に保存される。
`CLAUDE_CODE_TASK_LIST_ID`環境変数でセッション間共有が可能。

### 並列実行の推奨

大規模タスクで並列実行可能な場合、ユーザーにタスクリストIDを提示して並列実行を推奨する：

```
このタスクは並列実行可能です。別ターミナルで以下を実行すると並行作業できます：

CLAUDE_CODE_TASK_LIST_ID=<task_list_id> claude

または非対話モード：
CLAUDE_CODE_TASK_LIST_ID=<task_list_id> claude -p "Task 3を実装してください"
```

**推奨場面:**
- large-taskで依存関係のないタスクが複数ある場合
- codebase-reviewの後、複数issueを並行修正する場合

### タスクリストIDの取得

TaskCreateやTaskList実行後、内部的にタスクリストIDが割り当てられる。
IDは`~/.claude/tasks/`ディレクトリ内のUUIDディレクトリ名。

## 委譲時の連携

タスクリストはセッション内で共有される（spawn したサブエージェントも同じリストを読み書きする）。

**依存関係のあるタスクを順序付ける構成**では: TaskCreate（依存関係付き）→ `Agent` で spawn（`name` 指定）→ `SendMessage` で指示・情報共有 → 各体が TaskUpdate で完了 → 全員に `shutdown_request`。各体は TaskList で次に着手できるタスクを自律的に取得できる。

**各体が独立して結論を返す構成**（相互通信なし）では、タスクリストは lead の進捗管理用に留まる。この場合 TaskCreate は必須ではない。

コストは体数に比例する（各体が独立したインスタンス）。構成の決め方: @context/tool-claude-code.md「委譲判断」

## 注意事項

- 使用要否は `context/workflow-rules.md`「適用範囲」の基準に従う
