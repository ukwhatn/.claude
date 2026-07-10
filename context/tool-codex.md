# Codex 固有指示

Read when: Codex（OpenAI Codex CLI）として動作している場合、セッション開始後・最初の作業前に必ず読む。Claude Code はこのファイルを読む必要はない。

## @参照の解決規約（CRITICAL）

AGENTS.md・skills・context 内の `@path` 参照は Claude Code の import 記法であり、Codex では自動展開されない。以下の規約で必要時に自分で Read して解決する:

| 表記 | 実体パス |
|---|---|
| `@context/<file>.md` | `~/.claude/context/<file>.md` |
| `@AGENTS.md` / `@CLAUDE.md` | `~/.claude/AGENTS.md`（`CLAUDE.md` は互換symlink） |
| `@CLAUDE.local.md` | `~/.claude/CLAUDE.local.md`（存在すれば Read。マシン固有の運用メモ） |
| `@references/<file>.md`（スキル内） | そのスキルのディレクトリ配下 `references/<file>.md` |
| PJ CLAUDE.md | 各プロジェクトルートの `CLAUDE.md`（AGENTS.md 不在時は `~/.codex/config.toml` の `project_doc_fallback_filenames` で自動読込） |

## 常駐相当ファイルの Read 指針

Claude Code では @import で常駐する以下のファイルを、Codex では該当作業の前に Read する:

- `~/.claude/context/workflow-rules.md` — **複雑タスク**（複数ファイル変更・調査+実装・長時間）の開始時に必ず（Phase 0-5 の本体）
- `~/.claude/context/memory-file-formats.md` — メモリディレクトリ（`.local/`）を初めて操作する前に
- `~/.claude/context/cloudflare-development.md` — Cloudflare（wrangler / D1 等）作業の前に
- `~/.claude/CLAUDE.local.md` — セッション開始時に存在すれば（マシン固有の注意）

## ツール対応表

指示ファイル・スキルに登場する Claude Code の機構名と、Codex での実現手段:

| 指示ファイル上の表記 | Codex での実現手段 |
|---|---|
| AskUserQuestion（選択肢提示質問） | 番号付き選択肢のテキスト質問で代替（推奨案を先頭に置き「（推奨）」を付す。1回最大4問の原則も同様） |
| Edit / Write ツール | apply_patch（`cat >>` / heredoc 禁止の意図＝ファイル状態追跡の維持は同じ） |
| EnterWorktree / ExitWorktree | `git worktree add <path> -b feature/<issue_num>-<title-kebab>` / `git worktree remove <path>` を直接実行（原則: `~/.claude/context/worktree-guide.md`） |
| TaskCreate / TaskUpdate / TaskList | 組み込みの plan 機構で代替 |
| Skill ツール / `/skill-name` | `$skill-name` の明示発動、または description による暗黙発動 |
| サブエージェント委譲（Explore / general-purpose） | multi-agent 機構が利用可能ならそれを使用。無ければ同じ手順を逐次実行 |
| Agent Teams / Workflow ツール | 対応物なし。各スキルの「環境要件」節の代替手順（観点の逐次実行等）に従う |
| WebSearch | Codex の web search 機能 |
| context7 | MCP サーバー（未設定なら `~/.codex/config.toml` の `[mcp_servers.context7]` に追加して使用） |
| 外部レビューCLI（agent review） | cursor（`agent`）または claude（`claude -p`）を使用。**codex 自身での再帰レビューは行わない**（別ベンダー bias 独立性のため。コマンド例: `~/.claude/context/agent-cli-guide.md` 冒頭の注記） |

## Claude Code 専用ガイドの扱い

- **Codex では読まない**: `context/tool-claude-code.md` / `context/agent-teams-guide.md` / `context/task-tool-guide.md`（Claude Code 専用機構のガイドで、対応する代替は本ファイルのツール対応表に記載済み）
- **参照された場合のみ読む**: `context/claude-customization-guide.md` は Claude Code 固有機構の解説を含むが、スキル（create-skill / instructions-audit / session-retro 等）が設計原則・rubric の真実源として参照する。**該当スキルの実行時は Codex でも参照セクションを読む**（常駐は不要）
