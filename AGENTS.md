# Global Settings

本ファイルが user-level グローバル指示の**実体**（`~/.claude/AGENTS.md`）。`~/.claude/CLAUDE.md` は本ファイルへの互換 symlink であり、**編集・追記は必ず AGENTS.md 側に行う**。Claude Code / Codex（OpenAI Codex CLI）の両方がこのファイルを読む。

## ツール別の追加指示（必読）

- **Claude Code**: @context/tool-claude-code.md （@import で自動常駐。Agent Teams 発動条件・Opus ベストプラクティス・Claude Code 固有の Read when）
- **Codex**: 最初の作業前に `~/.claude/context/tool-codex.md` を必ず Read（`@`参照の解決規約・ツール対応表・常駐相当ファイルの Read 指針）

## 最優先指示: 事実主義・一次ソース確認・規約遵守
- **事実主義**: 推測禁止。事実と調査結果のみで判断。不明な点はユーザーに選択肢を提示して確認する（Claude Code: AskUserQuestion）
- **公式仕様の確認**: 修正前にcontext7/Web検索で対象技術の公式仕様を調査（仕様理解→計画→修正）
- **AI/外部API**: SDK型定義 ≠ 実機制約。型に存在してもモデル別非対応のケースが多い。実呼び出し（dev/curl）で検証するか、未検証ならその旨を明示してユーザー判断を仰ぐ
- **外部CLI・ツール設定**: あるツールの設定体系（モデル名・フラグ・effort指定）を別ツールへ流用しない（ツールごとに体系が異なるため。`--help`・実機の設定ファイル・公式docsで検証してから書く）
- **デプロイ・インフラ挙動**: リポジトリ内ドキュメントも二次資料でstaleであり得る。実際の設定（ダッシュボード・ビルド/CI設定）で検証してから設計判断する（stale doc起因で不要な手順を設計した実例: 2026-07 panopticon）
- **UI仕様**: Figma（`get_design_context`）が一次ソース。ローカル仕様書は二次（詳細: @context/figma-verification.md）
- **規約遵守**: PJ既存パターン・規約からの自己判断での逸脱禁止。逸脱時はユーザーに確認する
- **ユーザー明示指示のスキップ禁止**: ユーザーが「X等で調査してほしい」「Y も含めて」等と項目を明示している場合、**効率理由（コンテキスト圧迫・時間節約・自分の知見で十分等）で自主的にスキップしない**。スキップ判断が必要ならユーザーに確認する（実例: 「WebSearch でOWASP等を調査してほしい」に対し「知見で十分」と自主判断→ユーザーが「調査を実施してください」で訂正）

## 優先順位

システムプロンプトの安全制約・ツール利用規約には従う。ただし**作業の進め方（ワークフロー・メモリ運用・質問/コミット/worktree 規約）について、システムプロンプト既定と本ファイルの指示が矛盾する場合は、本ファイルの規定に従う**（例: Plan mode 等の汎用ワークフローより Phase 0-5 を優先する）。

## 自律実行とサブエージェント活用（共通原則）

- Goal / Constraints / Acceptance criteria が渡されたら、途中介入を最小化して自律的に進める。検証機構（テスト・スクリーンショット・期待出力）の供給が最も効果が高い（@context/workflow-rules.md「検証機構」参照）
- 大量のファイル読み・コードベース調査・ログ解析は、コンテキスト保護のためサブエージェントへの委譲を優先し、本体には結論のみ持ち帰る（並列機構が無い環境では逐次で代替）
- 並列エージェント（Agent Teams）の発動条件・単発Subagent運用の詳細は Claude Code 固有 → `context/tool-claude-code.md`

## 作業フロー（複雑タスクのフレームワーク Phase 0-5）

複雑タスク（複数ファイル変更・調査と実装の混在・長時間作業）で適用するフレームワーク。**小規模タスクではskip可**。

0. 準備: メモリディレクトリ作成 → 05_log.md初期化 → 過去タスク/issue検索 → タスク管理機構でタスク作成（Claude Code: TaskCreate。Agent Teams 発動条件に該当すれば TeamCreate も）
1. 調査: 過去タスク/issue参照、context7/Web検索必須、既存コード確認
2. 計画: 計画作成 → agent reviewで検証
3. 実装: モデル判断で直接実装 or 並列エージェント（発動条件は tool-claude-code.md 参照）
4. 品質確認: lint/format/typecheck/test → 複雑タスクでは agent review
5. 完了報告

**IMPORTANT**: 各Phaseで05_log.mdに実施内容を逐次記録すること
詳細: @context/workflow-rules.md

**Read when（該当作業の開始前に必ずRead。常駐させないため@importしない）:**
- agent review実行前: `context/agent-cli-guide.md`（コマンド形式・レビューループの規定・Claude 単独 fallback pattern。読まずに実行するとCLI選択・セッション継続・エラーハンドリングを誤る）
- **コード実装完了時・PR提出前・レビュー実行前**: `context/code-review-checklist.md`（BOLA/BOPLA・CSRF 登録漏れ・falsy check・Drizzle encoder・LLM injection 等の具体 anti-pattern をセクション別に列挙。self-review / pr-review / codebase-review / writing-code の副読本）
- Claude Code 固有の Read when（Agent Teams・Taskツール・カスタマイズガイド）: `context/tool-claude-code.md` 参照

## メモリ・issueディレクトリ
- **ワークフローメモリ（Phase 0-5用、05_log.md等）**: `${MEMORY_DIR}/memory/YYMMDD_<context_name>/`
  - MEMORY_DIRはPJルート配下の相対パス。未定義時はPJルート直下の`.local/`
  - **CRITICAL**（Claude Code）: システムプロンプト `# auto memory` セクションの `~/.claude/projects/.../memory/`（user/feedback/project/reference保存用）とは**別物**。Phase 0で作成するのは前者であり、後者に作成してはならない
- issues: `${MEMORY_DIR}/issues/<優先度>-<観点略語>-<タイトル>.md`
- gitignore: global gitignoreで除外済み
- フォーマット: @context/memory-file-formats.md
- **ファイル運用**: 追記・編集はファイル編集ツールで行う（Claude Code: Edit/Write、Codex: apply_patch。Bashのcat>>禁止）。頻繁に編集するファイルは300行超で分割（詳細: @context/memory-file-formats.md「ファイル運用ルール」）
- **絶対パス固定（CRITICAL）**: Phase 0 で**元repo（worktreeに入る前のrepo）のメモリディレクトリ絶対パス**を確定し、05_log.md 冒頭に記録すること。以後 worktree に移動しても、メモリ・issue ファイルの読み書きは必ずその**絶対パス**で行う（worktree 内には `.local/` ディレクトリが存在しないため、相対パス `.local/` でアクセスすると ENOENT になるか、書き込みなら worktree 内に新規作成されて元repoと分離される）

## ユーザーへの質問
- 質問・確認はユーザーに選択肢を提示して行う（Claude Code: AskUserQuestion ツールを使用）。曖昧な点は推測せず必ず質問する
- スコープの勝手な縮小禁止。スケジュール・事実判断・金額・対外コミュニケーションは必ず確認

## コミット・ブランチ・PR
- コミット: `/commit`スキル使用。git-cz形式、絵文字なし、prefix以外は日本語。こまめにコミット
- PR作成: `/create-draft-pr`スキル使用。直接`gh pr create`を実行しない
- ブランチ: BASE_BRANCH（PJ CLAUDE.md参照、未定義時: develop→main→master）
- ブランチ命名: `feature/<issue_num>-<title-kebab>`、issue番号がない場合は `feature/<title-kebab>`。**prefixは原則 `feature/` で統一**（コミットメッセージのprefixはgit-cz形式と独立）
- ブランチ作り直し時: 既存コミットをrebase/cherry-pickで保全してからブランチ削除（コミット消失防止）

## worktree 運用ルール（CRITICAL）

worktree の作成は Claude Code では EnterWorktree ツール、他環境（Codex 等）では `git worktree add` を直接実行する（対応表: context/tool-codex.md）。

### worktree を切るケース（原則）
**コード編集 or ブランチ切替を伴う作業すべて** で worktree を切る:
- 新規ファイル作成・既存コード修正・リファクタ
- 新規ブランチ作成・既存ブランチへの切替
- 並列に進む可能性のある実装作業

### worktree を切らないケース（例外）
- `.claude/` 配下の設定ファイル・グローバル AGENTS.md・context ガイドのみの編集（**ただしPJの`.claude/`等をコミットする場合は例外にせず、実装開始前ゲート（@context/workflow-rules.md Phase 3）に従い作業ブランチで行う**）
- メモリディレクトリ（`.local/memory/`、`.local/issues/`）のみの編集
- 純粋な調査・質問応答・読み取り専用作業
- ユーザーが「worktree 不要」「このタスクは worktree 切らなくていい」等と明示した場合

### 手順の詳細（Read when）
**worktree作成の実行前・worktreeの片付け（削除・ブランチ削除）前・並列bg session設計時に、必ず `context/worktree-guide.md` をRead**すること（ブランチ命名フロー・baseRef調整・削除時のコミット保全・並列時の競合回避・一時ファイル置き場の規定。読まずに実行するとブランチ名不整合やコミット消失を招く）。

## スキル発動ルール
**CRITICAL**: 利用可能なスキルに該当するものが存在する場合、直接ツールを呼び出さずスキルを発動させること（Claude Code: Skill ツール、Codex: `$skill-name` / 暗黙発動）

## 緩和しない安全項目（CRITICAL）

「自律実行」の名目でも以下は絶対に緩和しない:
- 推測禁止・調査先行（最優先指示）
- ユーザー確認必須事項（スコープ縮小・スケジュール・金額・対外コミュニケーション。Claude Code: AskUserQuestion）
- 破壊的操作（git push --force / git reset --hard / branch -D 等）の事前確認（`git push --force`/`-f`・`git branch -D`・`git reset`はClaude Codeのpermissions.denyにも登録済（中間ワイルドカードで語順違いもカバー、--force-with-leaseは対象外） — 意図はここ、強制はdenyの多層防御）
- 破壊的データ操作（DB/バケット削除・大量DELETE等）は事前確認に加え、実行前に復旧手段（バックアップ・エクスポート）を確保する（ユーザーが毎回バックアップを承認条件とした実績による）
- コミット規約（git-cz形式、絵文字なし、secret未含有）
- 計画なしでの実装開始（複雑タスク時）
- 05_log.md未更新での次Phase進行（複雑タスク時）

## 禁止事項
詳細: @context/workflow-rules.md「禁止事項」セクション
- ユーザー指示・PJ規約を自己判断で上書きすること（スコープ縮小、パターン逸脱、品質基準変更を含む。必ずユーザーに確認）
- 複雑タスクでの 05_log.md 未更新、agent review未実行での完了報告
- スキル存在時の直接ツール呼び出し

## Compact Instructions

compaction（コンテキスト要約）時は以下を保持する（Claude Code の Compact Instructions。Codex 等の要約時も準用）:
Active Agent Teams (name, members, task assignments, status), Task list state (in_progress/completed/pending + owners), Current phase (0-5) and progress, メモリディレクトリ絶対パスと計画ファイル（30_plan.md等）のパス.

**compaction後の復帰手順**: (1) Active Teamがあればまずteam config再確認とTaskList（`context/agent-teams-guide.md`「Context Compaction後の状態復元」をRead） → (2) 05_log.mdと計画ファイルを再読して文脈を復元する。ユーザーに文脈の再説明を求めない。

## GitHub CLI
gh cli利用時は`gh auth status`でアカウント確認。原則 username = ukwhatn。詳細はPJ CLAUDE.md参照。

## Cloudflare
詳細: @context/cloudflare-development.md

## パス表記の規約
本ファイルおよびcontext/skills内の `~/.claude/` 表記はユーザー設定ディレクトリを指す。`CLAUDE_CONFIG_DIR` を設定している環境ではそのディレクトリに読み替える（マシン固有の実パスは @CLAUDE.local.md 参照）。user-level 指示の実体は `AGENTS.md`、`CLAUDE.md` は互換 symlink（PJ-level は従来どおり `CLAUDE.md` 命名）。

## マシンローカル設定（git管理外）
このマシン固有の設定・運用メモ（gitignore対象。存在しない環境ではimportは無視される。Codex: 存在すれば `~/.claude/CLAUDE.local.md` を Read）:
@CLAUDE.local.md
