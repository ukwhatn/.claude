# Agent User Settings（Claude Code / Codex 共用）

user-level設定ファイル集。プロジェクト横断で使用するワークフロー、スキル、グローバル指示を定義し、**Claude Code と OpenAI Codex CLI の両方から利用する**。

## 使い方

```bash
# ~/.claude/ にクローン
git clone <this-repo> ~/.claude

# または既存の~/.claude/にマージ
```

## 構成

```
~/.claude/
├── AGENTS.md              # グローバル指示の実体（両ツール共通。ワークフロー、変数）
├── CLAUDE.md              # AGENTS.md への互換 symlink（Claude Code はこちらを読む）
├── context/               # エージェント向けコンテキスト
│   ├── tool-claude-code.md       # Claude Code 固有指示（Agent Teams発動条件・Opus BP。@importで常駐）
│   ├── tool-codex.md             # Codex 固有指示（@参照解決規約・ツール対応表。Read when）
│   ├── workflow-rules.md         # Phase 0-5 詳細
│   ├── agent-teams-guide.md      # Agent Teams 発動条件と構成例（Claude Code専用）
│   ├── task-tool-guide.md        # TaskCreate/TaskUpdate（Claude Code専用）
│   ├── agent-cli-guide.md        # 外部CLI（cursor agent / codex / claude）レビュー
│   ├── claude-customization-guide.md  # 指示ファイル設計原則（Claude Code固有機構）
│   ├── memory-file-formats.md
│   ├── figma-verification.md
│   └── cloudflare-development.md
├── skills/                # 自動トリガースキル（Agent Skills 形式・両ツール共用）
│   ├── codebase-review/
│   ├── commit/
│   ├── create-draft-pr/
│   ├── create-skill/
│   ├── database-migration/
│   ├── design-feature/
│   ├── doc-review/
│   ├── findmem/
│   ├── large-task/
│   ├── pr-comment/
│   ├── pr-review/
│   ├── project-init/
│   ├── project-sync/
│   ├── self-review/
│   ├── ui-ux-design/
│   ├── ukwhatn-writing/
│   └── update-inst/
├── templates/             # プロジェクト初期化テンプレート
│   └── project/
└── settings.json          # 権限・環境変数・hooks
```

## スキル一覧

| スキル | 説明 | トリガー |
|--------|------|----------|
| **codebase-review** | 6観点（perf/sec/test/arch/cq/docs）で並列レビュー | `/codebase-review`、品質監査依頼時 |
| **doc-review** | Agent Teamsによる多角的ドキュメントレビュー | `/doc-review`、「チームでレビュー」等の明示依頼時 |
| **pr-review** | Claude + 外部CLI（cursor agent / codex）マルチモデルレビュー | PRレビュー依頼時 |
| **pr-comment** | PRの特定レビューコメントへの対応（取得→実装→返信ドラフト） | PR URL+discussion指定の対応依頼時 |
| **self-review** | 自ブランチのPR提出前チェック（消し忘れ・変更漏れ・要件突合） | 「セルフレビューして」「diffを徹底チェック」時 |
| **design-feature** | 抽象要件から要件定義・システム要件書を作成 | `/design-feature`、機能設計依頼時 |
| **project-init** | CLAUDE.md・.claude/の初期設定 | PJ初期化依頼時 |
| **project-sync** | CLAUDE.mdとcontext/の整合性確保 + コード変更後のドキュメント同期 | ドキュメント整理・同期依頼時 |
| **database-migration** | ORM検出、マイグレーション作成・統合（squash）・同値性確認 | スキーマ変更・統合依頼時 |
| **large-task** | 複数セッションにまたがる大規模タスク分割 | 大規模実装時 |
| **create-skill** | 既存設定と整合したスキル自動作成 | `/create-skill <内容>` |
| **update-inst** | user/PJ-level指示・スキルの更新（再発防止・知見反映） | `/update-inst <内容>` |
| **ui-ux-design** | プロダクショングレードのUI/UX生成 | UI構築依頼時 |
| **ukwhatn-writing** | 本人の文体での日本語文章作成・推敲 | PR概要・レビュー返信・社内文書作成時 |
| **commit** | git-cz形式のコミット | `/commit [--push]`、「コミットして」時 |
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

AGENTS.mdで定義された 6 フェーズフレームワーク（**複雑タスク向け**。小規模はskip可）:

1. **Phase 0: 準備** - メモリディレクトリ作成、過去タスク検索、タスク管理機構でタスク作成（Claude Code: TaskCreate、Codex: plan）
2. **Phase 1: 調査** - context7/Web検索必須、既存コード確認
3. **Phase 2: 計画** - agent reviewで検証（Action Required ゼロまで）
4. **Phase 3: 実装** - モデル判断で直接実装 or 並列エージェント（Claude Code: Agent Teams。発動条件参照）
5. **Phase 4: 品質確認** - lint/format/typecheck/test + 必要に応じて agent review
6. **Phase 5: 完了報告**

## Agent Teams 発動条件（Claude Code）

Opus 4.7 ベストプラクティスに従い、Agent Teams は**限定発動**:
- (a) 5+ファイル並列変更が見込まれる
- (b) 独立タスク3つ以上
- (c) ユーザーが明示的に「チームで」指示

それ以外はモデル判断（直接実装または単発Subagent）。詳細: `context/tool-claude-code.md`「Agent Teams 発動条件」、`context/agent-teams-guide.md`

## Codex CLI との共有

このrepoは OpenAI Codex CLI からも同じ資産を使えるよう構成している:

- **グローバル指示**: `~/.codex/AGENTS.md` → `~/.claude/AGENTS.md` の symlink。Codex 固有の読み替え（`@`参照の解決・ツール対応表）は `context/tool-codex.md` に集約
- **skills**: `~/.codex/skills/<name>` → `~/.claude/skills/<name>` のスキル単位 symlink（Codex はスキル走査時に symlink を辿る）。Claude Code 固有機構に依存するスキル（doc-review 等）は本文の「環境要件」節に代替手順を記載
- **PJ CLAUDE.md の直読み**: `~/.codex/config.toml` に `project_doc_fallback_filenames = ["CLAUDE.md"]` を設定（AGENTS.md が無いプロジェクトで CLAUDE.md を読む）
- 記述規約: スキル・context 本文はツール中立の語彙で書き、ツール固有機能は「（Claude Code: X、Codex: Y）」の括弧書きで併記する

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

## 外部CLIレビュー連携（cursor優先 / codex fallback）

別モデルによるレビューを実施。**cursorの`agent` CLIを優先し、無い環境ではcodex CLIにfallback**:

```bash
# cursor（agent / cursor-agent）優先
agent -p "<prompt>" --trust --model gpt-5.5-high-fast --output-format json | jq -r '.session_id, .result'

# codex fallback（cursorが無い環境）
codex exec --model gpt-5.4 -c model_reasoning_effort="high" --json "<prompt>" \
  | jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'
```

- 修正すべき点がなくなるまでループ
- セッション継続: cursorは `--resume <session_id>`、codexは `codex exec resume --last`
- 詳細・CLI判定ロジック: `context/agent-cli-guide.md`「使用するCLIの選択」

## プロジェクト設定

新規プロジェクトでは `/project-init` を実行、または `templates/project/CLAUDE.md` をコピー。

## ライセンス

MIT
