---
name: large-task
description: 大規模タスクを複数セッションに分割して実装するワークフロー。自動発火条件 - 以下のいずれかに該当する場合は自動的にこのスキルを使用すること。(1) 5つ以上のファイル変更が見込まれる、(2) 複数の独立した機能実装が含まれる、(3) 調査だけで30分以上かかりそう、(4) ユーザーが「大規模」「複数日」「段階的に」等のキーワードを使用。
---

# Large Task Workflow

大規模タスクを複数セッションに分割して効率的に実装するためのワークフロー。

## 既存ワークフローとの関係

- **Phase 0-5（@context/workflow-rules.md）を補完・拡張**
- 通常タスク: Phase 0-5をそのまま使用
- 大規模タスク: このスキルでタスク分割 → 各タスクでPhase 0-5を適用

## ディレクトリ構成

```
${MEMORY_DIR}/
├── memory/YYMMDD_<task>/    # 通常のメモリディレクトリ（既存Phase 0-5）
└── tasks/YYMMDD_<task_name>/       # 大規模タスク専用（本スキル）
    ├── 00_plan.md           # 全体計画
    ├── 01_<subtask>.md      # 個別タスク1
    ├── 02_<subtask>.md      # 個別タスク2
    └── ...
```

- MEMORY_DIR: PJ CLAUDE.mdで定義（未定義時: `.local/`）
- task_name: タスクを識別する短い名前（例: `data-site`, `auth-refactor`）

## サブコマンド

### /large-task plan

**セッション1で実行**: 包括調査 → 全体計画 + 個別タスクファイル作成

1. 要件の明確化（AskUserQuestionで確認）
2. 包括調査
   - 既存コードベース調査
   - context7/WebSearchで外部情報参照
3. `${MEMORY_DIR}/tasks/YYMMDD_<task_name>/` ディレクトリ作成
   - 必ずdateコマンドで日付を確認すること
4. 00_plan.md作成（全体計画）
5. 01_xxx.md, 02_xxx.md... 作成（個別タスク）
6. agent reviewで計画検証（**ユーザーに実行を依頼** - 下記「agent review」セクション参照）

### /large-task implement <task_num>

**セッション2以降で実行**: 指定タスクを実装

1. **タスクファイルの特定（推測禁止）**
   - **IMPORTANT**: ファイル名を推測しない。必ずGlobでディレクトリ内を確認
   - `Glob("${tasks_dir}/*.md")` でファイル一覧を取得
   - `<task_num>_` で始まるファイルを特定
2. 00_plan.md と 特定したタスクファイルを読込
3. Phase 0-5を適用して実装
   - reference: user-level CLAUDE.md, @context/workflow-rules.md
   - Phase 0: memory/YYMMDD_<task>/ にメモリディレクトリ作成
   - Phase 1-4: タスクファイルに従って実装
   - Phase 5: 完了報告

## ファイルフォーマット

### 00_plan.md（全体計画）

```markdown
# <タスク名> 実装計画

## 概要
[1-2文で全体像を説明]

## 背景・目的
[なぜこの実装が必要か]

## タスク一覧

| # | タスク | 依存 | 状態 |
|---|--------|------|------|
| 01 | <タスク名> | - | pending |
| 02 | <タスク名> | 01 | pending |
| ... | ... | ... | ... |

状態: pending / in_progress / completed

## 全体アーキテクチャ
[図や説明]

## リスク・懸念事項
| リスク | 影響度 | 対策 |
|-------|-------|------|

## agent reviewの結果
[計画フェーズでのagent指摘と対応]
```

### 個別タスクファイル（01_xxx.md等）

テンプレート: [references/task-template.md](references/task-template.md)

```markdown
# Task XX: <タスク名>

## 目的
[このタスクで何を達成するか]

## 前提条件
- [ ] 依存タスク（あれば）
- [ ] 必要な環境・設定

## 完了条件
- [ ] 検証可能な条件1
- [ ] 検証可能な条件2

## 作業内容
### 変更対象ファイル
- path/to/file1.ts
- path/to/file2.ts

### 詳細手順
1. [手順1]
2. [手順2]
3. ...

### コミット
- `feat: ...`

## 検証手順
```bash
# 検証コマンド
bun run typecheck
bun run test
```

## 注意事項
- [ハマりポイント1]
- [ハマりポイント2]
```

## Phase 0-5との統合

各タスク実装時は、通常のPhase 0-5ワークフローを適用:

1. **Phase 0**: `memory/YYMMDD_<task>/` 作成、05_log.md初期化
2. **Phase 1**: タスクファイルの「作業内容」を元に詳細調査
3. **Phase 2**: 必要に応じて詳細計画（タスクファイルで既に十分なら省略可）
4. **Phase 3**: 実装（4ステップ: 調査→計画→実行→レビュー）
5. **Phase 4**: 品質確認 + agent review（**ユーザーに実行を依頼** - 下記「agent review」セクション参照）
6. **Phase 5**: 完了報告、00_plan.mdの状態更新

## agent review

**IMPORTANT**: agent reviewは自分で実行せず、ユーザーにコマンドを提示して実行を依頼すること。

### コマンドテンプレート

```bash
cd <project_root> && agent -p "メモリディレクトリ <memory_dir_full_path> の内容を読み、
git diff HEAD -- <changed_dir>/ を実行してコード変更をレビューしてください。
バグ、セキュリティ、パフォーマンス、ベストプラクティスの観点から指摘してください。
指摘がなければ「指摘なし」とだけ回答してください。" \
  --model gpt-5.3-codex-high-fast \
  --output-format json | jq -r '.session_id, .result'
```

### 実行依頼の例

```
agent reviewコマンドを実行してください:

\`\`\`bash
cd /path/to/project && agent -p "..." --model gpt-5.3-codex-high-fast --output-format json | jq -r '.session_id, .result'
\`\`\`

レビュー結果を教えてください。
```

### レビュー結果への対応

1. ユーザーからレビュー結果を受け取る
2. 「絶対にやるべき」指摘は必ず修正
3. それ以外の指摘はやる/やらない判断、または AskUserQuestion で確認
4. 修正後、再度agent reviewを依頼（指摘がなくなるまで）

## Taskツールとの統合（オプション）

タスク分割後、TaskCreate/TaskUpdate/TaskListを使用して進捗管理を強化できる。
詳細: @context/task-tool-guide.md

### /large-task plan での使用

タスク分割後、各サブタスクをTaskCreateで登録:

```
# 各サブタスクを作成
TaskCreate(
  subject: "Task 01: <タスク名>",
  description: "<タスクファイルの内容サマリー>",
  activeForm: "<タスク名>を実装中"
)

# 依存関係を設定
TaskUpdate(taskId: "2", addBlockedBy: ["1"])
```

**メリット:**
- TaskListで全タスクの状態を即座に確認
- 依存関係（blockedBy）で実行可能なタスクを判定
- セッション間でタスク状態が保持される

### /large-task implement での使用

```
# タスク開始時
TaskUpdate(taskId, status: "in_progress")

# タスク完了時
TaskUpdate(taskId, status: "completed")
```

**注意:** 00_plan.mdの状態更新と併用すること（置き換えではない）

## 既存設定への参照

- ワークフロー詳細: @context/workflow-rules.md
- メモリファイル形式: @context/memory-file-formats.md
- Taskツール活用: @context/task-tool-guide.md
- agent cli: @context/agent-cli-guide.md
- PJ固有設定: PJ CLAUDE.md
