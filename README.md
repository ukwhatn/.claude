# Claude Code User Settings

Claude Codeのuser-level設定ファイル集。プロジェクト横断で使用するワークフロー、スキル、コマンドを定義。

## 使い方

```bash
# ~/.claude/ にクローン
git clone <this-repo> ~/.claude

# または既存の~/.claude/にマージ
```

## 構成

```
~/.claude/
├── CLAUDE.md              # グローバル設定（ワークフロー、変数）
├── agents/                # カスタムエージェント定義
│   ├── researcher.md      # 調査専門
│   ├── implementer.md     # 実装専門
│   ├── code-reviewer.md   # レビュー専門
│   ├── test-writer.md     # テスト作成専門
│   └── planner.md         # 計画策定専門
├── commands/              # ユーザー実行コマンド
│   ├── commit.md          # /commit
│   └── pr.md              # /pr
├── context/               # エージェント向けコンテキスト
│   ├── agent-teams-guide.md
│   ├── workflow-rules.md
│   ├── task-tool-guide.md
│   └── ...
├── skills/                # 自動トリガースキル
│   ├── codebase-review/
│   ├── create-skill/
│   ├── database-migration/
│   ├── documentation/
│   ├── large-task/
│   ├── pr-review/
│   ├── project-init/
│   ├── project-sync/
│   ├── ui-ux-design/
│   └── update-inst/
└── templates/             # プロジェクト初期化テンプレート
    └── project/
```

## スキル一覧

| スキル | 説明 | トリガー |
|--------|------|----------|
| **codebase-review** | 6観点（perf/sec/test/arch/cq/docs）で並列レビュー | `/codebase-review`、品質監査依頼時 |
| **pr-review** | Claude + GPT-5.3 Codexマルチモデルレビュー | PRレビュー依頼時 |
| **project-init** | CLAUDE.md・.claude/の初期設定 | PJ初期化依頼時 |
| **project-sync** | CLAUDE.mdとcontext/の整合性確保 | ドキュメント整理依頼時 |
| **documentation** | コード変更に伴うドキュメント更新 | API/環境変数追加検出時 |
| **database-migration** | ORM検出、マイグレーション作成支援 | スキーマ変更依頼時 |
| **large-task** | 複数セッションにまたがる大規模タスク分割 | 大規模実装時 |
| **create-skill** | 既存設定と整合したスキル自動作成 | `/create-skill <内容>` |
| **update-inst** | 間違いの再発防止ルール追加 | `/update-inst <間違えた内容>` |
| **ui-ux-design** | プロダクショングレードのUI/UX生成 | UI構築依頼時 |

## カスタムエージェント一覧

| エージェント | 説明 | ツール制限 |
|------------|------|-----------|
| **researcher** | 調査専門（context7/WebSearch活用） | Write/Edit不可 |
| **implementer** | 実装専門（計画に従った実装） | 制限なし |
| **code-reviewer** | レビュー専門（バグ/セキュリティ/パフォーマンス） | Write/Edit不可 |
| **test-writer** | テスト作成専門（既存パターン踏襲） | 制限なし |
| **planner** | 計画策定専門（リスク評価、実装計画） | Write/Edit不可 |

Agent TeamsまたはSubagentとして使用可能。詳細: `context/agent-teams-guide.md`

## コマンド一覧

| コマンド | 説明 | 引数 |
|----------|------|------|
| `/commit` | git-cz形式でコミット | `--push`: コミット後push |
| `/pr` | Draft PR作成 | `[base-branch]`: マージ先 |

## ワークフロー

CLAUDE.mdで定義された6フェーズワークフロー:

1. **Phase 0: 準備** - メモリディレクトリ作成、過去タスク検索
2. **Phase 1: 調査** - context7/WebSearch必須、既存コード確認
3. **Phase 2: 計画** - agent reviewで検証（指摘なくなるまで）
4. **Phase 3: 実装** - 調査→計画→実行→レビューの4ステップ
5. **Phase 4: 品質確認** - lint/format/typecheck/test + agent review
6. **Phase 5: 完了報告**

## メモリディレクトリ

各タスクの作業ログを `.local/memory/YYMMDD_<task_name>/` に保存:

```
.local/
├── memory/
│   └── YYMMDD_<task>/
│       ├── 05_log.md      # 作業ログ（必須）
│       ├── 30_plan.md     # 実装計画
│       └── ...
└── issues/                # codebase-reviewで生成
```

## agent cli連携

別モデル（GPT-5.3-Codex-High-Fast）によるレビューを実施:

```bash
agent -p "<prompt>" --model gpt-5.3-codex-high-fast --output-format json | jq -r '.session_id, .result'
```

- 修正すべき点がなくなるまでループ
- `--resume <session_id>`でセッション継続

## プロジェクト設定

新規プロジェクトでは `/project-init` を実行、または `templates/project/CLAUDE.md` をコピー:

```markdown
# <プロジェクト名>

## 変数
MEMORY_DIR=.local/
BASE_BRANCH=develop

## 品質チェック
npm run lint
npm run format
npm run typecheck
npm test

## 特記事項
- [PJ固有のルール]
```

## ライセンス

MIT
