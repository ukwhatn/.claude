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
├── CLAUDE.md              # グローバル設定（ワークフロー、変数、Agent Teams発動条件）
├── context/               # エージェント向けコンテキスト
│   ├── workflow-rules.md         # Phase 0-5 詳細
│   ├── agent-teams-guide.md      # Agent Teams 発動条件と構成例
│   ├── task-tool-guide.md        # TaskCreate/TaskUpdate
│   ├── agent-cli-guide.md        # 別モデル（GPT-5.4-High-Fast）レビュー
│   ├── claude-customization-guide.md  # CLAUDE.md設計原則, Opus 4.7 BP
│   ├── memory-file-formats.md
│   ├── figma-verification.md
│   └── cloudflare-development.md
├── skills/                # 自動トリガースキル
│   ├── codebase-review/
│   ├── commit/
│   ├── create-draft-pr/
│   ├── create-skill/
│   ├── database-migration/
│   ├── doc-review/
│   ├── documentation/
│   ├── findmem/
│   ├── large-task/
│   ├── pr-review/
│   ├── project-init/
│   ├── project-sync/
│   ├── ui-ux-design/
│   └── update-inst/
├── templates/             # プロジェクト初期化テンプレート
│   └── project/
└── settings.json          # 権限・環境変数・hooks
```

## スキル一覧

| スキル | 説明 | トリガー |
|--------|------|----------|
| **codebase-review** | 6観点（perf/sec/test/arch/cq/docs）で並列レビュー | `/codebase-review`、品質監査依頼時 |
| **doc-review** | Agent Teamsによる多角的ドキュメントレビュー | ドキュメントレビュー依頼時 |
| **pr-review** | Claude + GPT-5.4-High-Fastマルチモデルレビュー | PRレビュー依頼時 |
| **project-init** | CLAUDE.md・.claude/の初期設定 | PJ初期化依頼時 |
| **project-sync** | CLAUDE.mdとcontext/の整合性確保 | ドキュメント整理依頼時 |
| **documentation** | コード変更に伴うドキュメント更新 | API/環境変数追加検出時 |
| **database-migration** | ORM検出、マイグレーション作成支援 | スキーマ変更依頼時 |
| **large-task** | 複数セッションにまたがる大規模タスク分割 | 大規模実装時 |
| **create-skill** | 既存設定と整合したスキル自動作成 | `/create-skill <内容>` |
| **update-inst** | 間違いの再発防止ルール追加 | `/update-inst <間違えた内容>` |
| **ui-ux-design** | プロダクショングレードのUI/UX生成 | UI構築依頼時 |
| **commit** | git-cz形式のコミット | `/commit [--push]` |
| **create-draft-pr** | Draft PR作成 | `/create-draft-pr [base-branch]` |
| **findmem** | メモリディレクトリ検索 | `/findmem <keyword>` |

## エージェントロール

カスタムエージェント定義ファイルは廃止済み。general-purpose サブエージェントにインライン指示でロールを付与する。

| ロール | 用途 |
|------|------|
| **researcher** | 調査専門（context7/WebSearch活用） |
| **implementer** | 実装専門（計画に従った実装） |
| **reviewer** | レビュー専門（バグ/セキュリティ/パフォーマンス） |
| **test-writer** | テスト作成専門 |

詳細: `context/agent-teams-guide.md`

## ワークフロー

CLAUDE.mdで定義された 6 フェーズフレームワーク（**複雑タスク向け**。小規模はskip可）:

1. **Phase 0: 準備** - メモリディレクトリ作成、過去タスク検索、TaskCreate（必要ならTeamCreate）
2. **Phase 1: 調査** - context7/WebSearch必須、既存コード確認
3. **Phase 2: 計画** - agent reviewで検証（Action Required ゼロまで）
4. **Phase 3: 実装** - モデル判断で直接実装 or Agent Teams（発動条件参照）
5. **Phase 4: 品質確認** - lint/format/typecheck/test + 必要に応じて agent review
6. **Phase 5: 完了報告**

## Agent Teams 発動条件

Opus 4.7 ベストプラクティスに従い、Agent Teams は**限定発動**:
- (a) 5+ファイル並列変更が見込まれる
- (b) 独立タスク3つ以上
- (c) ユーザーが明示的に「チームで」指示

それ以外はモデル判断（直接実装または単発Subagent）。詳細: `context/agent-teams-guide.md`

## メモリディレクトリ

各タスクの作業ログを `.local/memory/YYMMDD_<context_name>/` に保存:

```
.local/
├── memory/
│   └── YYMMDD_<context_name>/
│       ├── 05_log.md      # 作業ログ（必須）
│       ├── 30_plan.md     # 実装計画
│       └── ...
└── issues/                # codebase-reviewで生成
```

## agent cli連携

別モデル（GPT-5.4-High-Fast）によるレビューを実施:

```bash
agent -p "<prompt>" --trust --model gpt-5.4-high-fast --output-format json | jq -r '.session_id, .result'
```

- 修正すべき点がなくなるまでループ
- `--resume <session_id>`でセッション継続

## プロジェクト設定

新規プロジェクトでは `/project-init` を実行、または `templates/project/CLAUDE.md` をコピー。

## ライセンス

MIT
