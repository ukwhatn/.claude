# Agent User Settings（Claude Code / Codex 共用）

user-level 設定ファイル集。プロジェクト横断で使うワークフロー・スキル・グローバル指示を定義し、**Claude Code と OpenAI Codex CLI の両方から利用する**。

## 使い方

```bash
git clone <this-repo> ~/.claude
```

## 構成

```
~/.claude/
├── AGENTS.md              # グローバル指示の実体（両ツール共通）
├── CLAUDE.md              # AGENTS.md への互換 symlink
├── CLAUDE.local.md        # マシン固有設定（git管理外）
├── output-styles/         # 応答形式の真実源（Claude Code: system prompt 末尾に追記される）
├── context/               # エージェント向け詳細ガイド
├── skills/                # 自動トリガースキル（Agent Skills 形式・両ツール共用）
├── hooks/                 # SessionStart 等のフックスクリプト
├── templates/project/     # プロジェクト初期化テンプレート
└── settings.json          # 権限・環境変数・hooks・モデル
```

### context/ の役割

`@import` で常駐するもの（AGENTS.md から自動ロード）:

| ファイル | 内容 |
|---|---|
| `tool-claude-code.md` | Claude Code 固有指示（委譲判断・spawn 後の実務） |
| `workflow-rules.md` | Phase 0-5 の詳細 |
| `memory-file-formats.md` | メモリファイルの形式 |
| `figma-verification.md` | Figma を一次ソースとする UI 検証 |
| `cloudflare-development.md` | wrangler / Workers / D1 の実測知見 |

必要時に Read するもの（常駐させない）:

| ファイル | Read するタイミング |
|---|---|
| `code-review-checklist.md` | コード実装完了時・PR 提出前・レビュー実行前 |
| `agent-cli-guide.md` | 外部 CLI（codex / cursor）でレビューする前 |
| `worktree-guide.md` | worktree の作成・片付け前 |
| `task-tool-guide.md` | TaskCreate/TaskUpdate を複雑タスクで初めて使う時 |
| `claude-customization-guide.md` | 指示ファイル・skills・hooks の設計・監査時 |
| `tool-codex.md` | Codex として動作している場合（最初の作業前） |

### skills/

28 スキル。一覧と発動条件は各 `SKILL.md` の frontmatter を参照（Claude Code では `/help` で確認できる）。

主要なもの: `commit` / `create-draft-pr`（コミット・PR）、`writing-code`（実装原則）、`systematic-debugging`（根本原因調査）、`self-review` / `pr-review` / `codebase-review` / `doc-review`（レビュー）、`design-feature`（要件定義）、`update-inst` / `instructions-audit` / `session-retro`（本リポジトリ自体の保守）。

## ワークフロー

Phase 0-5（準備 → 調査 → 計画 → 実装 → 品質確認 → 完了報告）。適用条件と各 Phase の内容は `AGENTS.md`「作業フロー」および `context/workflow-rules.md` を参照。

## Codex CLI との共有

- **グローバル指示**: `~/.codex/AGENTS.md` → `~/.claude/AGENTS.md` の symlink。Codex 固有の読み替え（`@`参照の解決・ツール対応表）は `context/tool-codex.md` に集約
- **skills**: `~/.codex/skills/<name>` → `~/.claude/skills/<name>` のスキル単位 symlink。Claude Code 固有機構に依存するスキルは本文の「環境要件」節に代替手順を記載
- **PJ CLAUDE.md の直読み**: `~/.codex/config.toml` に `project_doc_fallback_filenames = ["CLAUDE.md"]` を設定
- 記述規約: スキル・context 本文はツール中立の語彙で書き、ツール固有機能は「（Claude Code: X、Codex: Y）」の括弧書きで併記する

## メモリディレクトリ

各タスクの作業ログを `.local/memory/YYMMDD_<context_name>/` に保存する（global gitignore で除外済み）。形式は `context/memory-file-formats.md` を参照。

```
.local/
├── memory/YYMMDD_<context_name>/   # 05_log.md（必須）、30_plan.md 等
└── issues/                          # codebase-review が生成
```

## プロジェクト設定

新規プロジェクトでは `/project-init` を実行、または `templates/project/CLAUDE.md` をコピーする。

## ライセンス

MIT
