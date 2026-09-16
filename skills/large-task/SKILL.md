---
name: large-task
description: 大規模タスクを複数セッションに分割して実装するワークフロー。複数の独立した機能実装を含む時、ユーザーが「大規模」「複数日」「段階的に」等の語を使った時に自動発火する（ファイル変更数や所要時間の自己推定は単独の発火条件にしない）。境界: 要件定義は design-feature、PR 分割計画書の立案は plan-feature-prs（その計画に基づく実装進行は本スキル）。
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

1. 要件の明確化（ユーザーに選択肢を提示して確認。Claude Code: AskUserQuestion）
2. 包括調査
   - 既存コードベース調査
   - context7/WebSearchで外部情報参照
3. `${MEMORY_DIR}/tasks/YYMMDD_<task_name>/` ディレクトリ作成
   - 必ずdateコマンドで日付を確認すること
4. 00_plan.md作成（全体計画）
5. 01_xxx.md, 02_xxx.md... 作成（個別タスク）
6. 必要なら外部CLIで計画レビュー（@context/agent-cli-guide.md参照）

### /large-task implement <task_num>

**セッション2以降で実行**: 指定タスクを実装

1. **タスクファイルの特定（推測禁止）**
   - **IMPORTANT**: ファイル名を推測しない。必ずGlobでディレクトリ内を確認
   - `Glob("${tasks_dir}/*.md")` でファイル一覧を取得
   - `<task_num>_` で始まるファイルを特定
2. 00_plan.md と 特定したタスクファイルを読込
3. Phase 0-5を適用して実装
   - reference: user-level AGENTS.md, @context/workflow-rules.md
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

テンプレートは [references/task-template.md](references/task-template.md) をReadして使用する。本文には再掲しない（テンプレートの二重管理による記述ずれを避けるため）。

## Phase 0-5との統合

各タスク実装時は、通常のPhase 0-5ワークフローを適用:

1. **Phase 0**: `memory/YYMMDD_<task>/` 作成、05_log.md初期化
2. **Phase 1**: タスクファイルの「作業内容」を元に詳細調査
3. **Phase 2**: 必要に応じて詳細計画（タスクファイルで既に十分なら省略可）
4. **Phase 3**: 実装（4ステップ: 調査→計画→実行→レビュー）
5. **Phase 4**: 品質確認（必要なら外部CLIレビュー - @context/agent-cli-guide.md参照）
6. **Phase 5**: 完了報告、00_plan.mdの状態更新

## agent review

外部CLIは lead が実行する（@context/agent-cli-guide.md）。相互通信を使う構成で reviewer を分けている場合はその agent が実行する。

詳細: @context/agent-cli-guide.md「レビュー専任 agent に分ける場合」

### leadの判断基準
- Action Required → 必ず修正（implementerに委譲）
- Recommended/Minor → 必要性に基づいて判断
- 打ち切り: @context/agent-cli-guide.md「レビューループの流れ」に従う（**レビュー対象が設計文書か実装差分かで上限が異なる**。数値をここに複写しない）

## 既存設定への参照

- ワークフロー詳細: @context/workflow-rules.md
- メモリファイル形式: @context/memory-file-formats.md
- agent cli: @context/agent-cli-guide.md
- PJ固有設定: PJ CLAUDE.md
