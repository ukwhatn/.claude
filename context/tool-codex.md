# Codex固有指示

Codex（OpenAI Codex CLI）として動くときの、`@` 参照の解決・Claude Code機構との対応・委譲の差分。Claude Codeはこのファイルを読まない。

## @参照の解決規約

AGENTS.md・skills・context内の `@path` 参照はClaude Codeのimport記法であり、Codexでは自動展開されない。以下の規約で必要時に自分でReadして解決する:

| 表記 | 実体パス |
|---|---|
| `@context/<file>.md` | `~/.claude/context/<file>.md` |
| `@AGENTS.md` / `@CLAUDE.md` | `~/.claude/AGENTS.md`（`CLAUDE.md` は互換symlink） |
| `@CLAUDE.local.md` | `~/.claude/CLAUDE.local.md`（存在すればRead。マシン固有の運用メモ） |
| `@references/<file>.md`（スキル内） | そのスキルのディレクトリ配下 `references/<file>.md` |
| PJ CLAUDE.md | 各プロジェクトルートの `CLAUDE.md`（AGENTS.md不在時は `~/.codex/config.toml` の `project_doc_fallback_filenames` で自動読込） |

AGENTS.md末尾の `@CLAUDE.local.md` は展開されないので、セッション開始時に `~/.claude/CLAUDE.local.md` が存在すれば自分でReadする。AGENTS.mdの「Read when」に挙がったファイルは、Codexでも同じ条件でReadする。

## ツール対応表

指示ファイル・スキルに登場するClaude Codeの機構名と、Codexでの実現手段:

| 指示ファイル上の表記 | Codexでの実現手段 |
|---|---|
| AskUserQuestion（選択肢提示質問） | 番号付き選択肢のテキスト質問で代替（推奨案を先頭に置き「（推奨）」を付す。論点ごとの分け方はAGENTS.md「確認が要るもの」の質問の出し方に従う） |
| Edit / Writeツール | apply_patch（`cat >>` / heredocを使わない意図＝ファイル状態追跡の維持は同じ） |
| EnterWorktree / ExitWorktree | `git worktree add <path> -b feature/<issue_num>-<title-kebab>` / `git worktree remove <path>` を直接実行する。ブランチ名を直接指定できるので、`context/worktree-guide.md` の改名フローは不要。コミット保全・競合回避の原則は同ガイドに従う |
| Skillツール / `/skill-name` | `$skill-name` の明示発動、またはdescriptionによる暗黙発動 |
| サブエージェント委譲（Explore / general-purpose） | Herdrのpane内で動いているならpane委譲（後述「委譲」）。pane外ではmulti-agent機構が利用可能ならそれを使用し、無ければ同じ手順を逐次実行 |
| Agent Teams / Workflowツール | 対応物なし。各スキルの「環境要件」節の代替手順（観点の逐次実行等）に従う |
| WebSearch | Codexのweb search機能 |
| context7 | MCPサーバー（未設定なら `~/.codex/config.toml` の `[mcp_servers.context7]` に追加して使用） |
| 外部レビューCLI（agent review） | cursor（`agent`）を第1選択、無ければclaude（`claude -p`）。codex自身での再帰レビューは行わない（別ベンダーのbias独立性のため。実行主体がClaude Codeの場合の既定はcodex優先だが、実行主体がCodexのときは自分自身を選ばない。コマンド例: `~/.claude/context/agent-cli-guide-details.md`「実行主体がCodexの場合」） |

## 委譲

`bin/herdr-delegate.sh` はherdr CLIを叩くシェルスクリプトなので、Codexからも同じ引数で呼べる。規則は `~/.claude/context/herdr-delegation.md` が真実源で、委譲すると決めた時点でReadする。ここに書くのはCodex固有の差分だけ。

- Herdrのpane内で動いているか（`HERDR_ENV=1` かどうか）で分岐する。pane内ならpane委譲を使う。pane外ではスクリプトが `not_in_herdr` を返し、CodexにはAgent toolが無いので、上のツール対応表に従って逐次実行で進める
- `--lead-name` は渡さない。CodexはClaude CodeのListAgentsに現れないため、この名前を渡すと委譲先が届かない宛先へ問い合わせることになる。省略すれば、委譲先へはpane経由の連絡方法だけが案内される
- 委譲先とのやり取りは `herdr agent prompt <name> "<メッセージ>"` で行う（CodexにはSendMessageが無い）。往復が予想される委譲はtabを残す

## Claude Code専用ガイドの扱い

- Codexでは読まない: `context/tool-claude-code.md`（Claude Code専用機構のガイドで、対応する代替は本ファイルのツール対応表に記載済み）
- 参照された場合のみ読む: `context/claude-customization-guide.md` はClaude Code固有機構の解説を含むが、スキル（create-skill / instructions-audit / update-inst等）が設計原則・rubricの真実源として参照する。該当スキルの実行時はCodexでも参照セクションを読む（常駐は不要）
