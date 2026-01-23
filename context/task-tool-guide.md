# Taskツール活用ガイド

## 概要

TaskCreate/TaskList/TaskGet/TaskUpdateツールを使用して、タスクの進捗管理と可視化を行う。

## ツール一覧

| ツール | 用途 |
|--------|------|
| TaskCreate | 新しいタスクを作成 |
| TaskList | 全タスクの一覧を表示 |
| TaskGet | 特定タスクの詳細を取得 |
| TaskUpdate | タスクのステータス・内容を更新 |

## 基本パターン

### タスク作成

```
TaskCreate(
  subject: "タスク名",           # 簡潔なタイトル（命令形）
  description: "詳細説明",       # 実行内容の詳細
  activeForm: "〜中"            # スピナーに表示される進行形
)
```

**例:**
```
TaskCreate(
  subject: "Phase 1: 調査",
  description: "既存コードベースとベストプラクティスを調査",
  activeForm: "調査中"
)
```

### 状態更新

```
TaskUpdate(taskId: "1", status: "in_progress")  # 開始
TaskUpdate(taskId: "1", status: "completed")    # 完了
```

**状態遷移:** `pending` → `in_progress` → `completed`

### 依存関係

```
TaskUpdate(taskId: "2", addBlockedBy: ["1"])    # Task 2はTask 1の完了を待つ
```

- blockedByが空でないタスクは実行不可
- 依存タスクが完了すると自動的に実行可能になる

### メタデータ

```
TaskUpdate(taskId: "1", metadata: {key: "value"})  # 追加情報を記録
```

**活用例:**
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

### 4. Claude reviewループ

レビュー履歴の構造化:

```
# 初回
TaskCreate(subject: "Claude review: 計画レビュー", metadata: {loop: 1})

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
Bash(command: "npm test", run_in_background: true) → task_id

# 現在のタスクを完了
TaskUpdate(currentTaskId, status: "completed")

# 次のタスクを確認・開始
TaskList()
TaskUpdate(nextTaskId, status: "in_progress")

# 次のタスクの調査を開始
# ...

# バックグラウンド処理の結果を適宜確認
TaskOutput(task_id, block: false)
```

**活用シーン:**
- `npm install` / `pip install`（依存関係インストール）
- `npm run build`（ビルド）
- `npm test` / `pytest`（テスト実行）
- `claude -p`（Claude review）

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

## 注意事項

- Taskツールの使用は**オプション**（強制ではない）
- 単純なタスクでは不要（3ステップ以下なら省略可）
- 依存関係はタスク作成後にTaskUpdateで設定
- metadataは任意のキー・値を格納可能
