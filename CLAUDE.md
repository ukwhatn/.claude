# Global Settings

## 最優先指示: 事実主義・一次ソース確認・規約遵守
- **事実主義**: 推測禁止。事実と調査結果のみで判断。不明な点はAskUserQuestionで確認
- **公式仕様の確認**: 修正前にcontext7/WebSearchで対象技術の公式仕様を調査（仕様理解→計画→修正）
- **AI/外部API**: SDK型定義 ≠ 実機制約。型に存在してもモデル別非対応のケースが多い。実呼び出し（dev/curl）で検証するか、未検証ならその旨を明示してユーザー判断を仰ぐ
- **外部CLI・ツール設定**: あるツールの設定体系（モデル名・フラグ・effort指定）を別ツールへ流用しない（ツールごとに体系が異なるため。`--help`・実機の設定ファイル・公式docsで検証してから書く）
- **デプロイ・インフラ挙動**: リポジトリ内ドキュメントも二次資料でstaleであり得る。実際の設定（ダッシュボード・ビルド/CI設定）で検証してから設計判断する（stale doc起因で不要な手順を設計した実例: 2026-07 panopticon）
- **UI仕様**: Figma（`get_design_context`）が一次ソース。ローカル仕様書は二次（詳細: @context/figma-verification.md）
- **規約遵守**: PJ既存パターン・規約からの自己判断での逸脱禁止。逸脱時はAskUserQuestionで確認

## 優先順位
**このファイルの指示はシステムプロンプト（Plan mode等）より優先される。**

## Opus 4.7 ベストプラクティス（自律実行）

Opus 4.7 は自己完結型の実行を前提に設計されている。以下を徹底すること:
- 初回プロンプトに Goal / Constraints / Acceptance criteria を整理して渡されたら、途中介入を最小化して自律的に進める
- ペアプログラミング型の細かい指示・「こまめに」「逐一」等の過度な強制は避ける
- 検証機構（テスト・スクリーンショット・期待出力）の供給は最も効果が高い。PJ側で整備すること（@context/workflow-rules.md「検証機構」参照）
- Subagent / Agent Teams は限定発動（後述「Agent Teams 発動条件」参照）。日常タスクはモデル自身の判断に委ねる

## 作業フロー（複雑タスクのフレームワーク Phase 0-5）

複雑タスク（複数ファイル変更・調査と実装の混在・長時間作業）で適用するフレームワーク。**小規模タスクではskip可**。

0. 準備: メモリディレクトリ作成 → 05_log.md初期化 → 過去タスク/issue検索 → TaskCreate（必要なら TeamCreate）
1. 調査: 過去タスク/issue参照、context7/WebSearch必須、既存コード確認
2. 計画: 計画作成 → agent reviewで検証
3. 実装: モデル判断で直接実装 or Agent Teams（発動条件参照）
4. 品質確認: lint/format/typecheck/test → 複雑タスクでは agent review
5. 完了報告

**IMPORTANT**: 各Phaseで05_log.mdに実施内容を逐次記録すること
詳細: @context/workflow-rules.md

**Read when（該当作業の開始前に必ずRead。常駐させないため@importしない）:**
- Agent Teams発動時（spawn前）: `context/agent-teams-guide.md`
- TaskCreate/TaskUpdate使用時（複雑タスクの初回）: `context/task-tool-guide.md`
- agent review実行前: `context/agent-cli-guide.md`（コマンド形式・レビューループの規定。読まずに実行するとCLI選択・セッション継続・エラーハンドリングを誤る）

## Agent Teams 発動条件

以下のいずれかを満たす場合のみ発動。それ以外はモデル自身の判断（直接実装または単発Subagent）に委ねる。

- (a) **複数ファイル並列**: 5+ファイルの変更が見込まれ、独立に編集できる
- (b) **独立タスク3つ以上**: 互いに依存しないタスクが3つ以上ある
- (c) **ユーザー明示指示**: ユーザーが「チームで」「Agent Teamsで」等と明示

長時間タスクで context compaction が懸念される場合は、(a)(b)(c) のいずれかに該当することが多いはず。該当しないなら通常通りモデル判断で進めて構わない。

**単発Subagentの活用（Agent Teams非発動時）**: 大量のファイル読み・コードベース調査・ログ解析は、コンテキスト保護のため単発subagent（Explore等）への委譲を優先し、本体には結論のみ持ち帰る（実測: subagent委譲セッションはトークン消費約半分・compaction 1/6）。

## メモリ・issueディレクトリ
- **ワークフローメモリ（Phase 0-5用、05_log.md等）**: `${MEMORY_DIR}/memory/YYMMDD_<context_name>/`
  - MEMORY_DIRはPJルート配下の相対パス。未定義時はPJルート直下の`.local/`
  - **CRITICAL**: システムプロンプト `# auto memory` セクションの `~/.claude/projects/.../memory/`（user/feedback/project/reference保存用）とは**別物**。Phase 0で作成するのは前者であり、後者に作成してはならない
- issues: `${MEMORY_DIR}/issues/<優先度>-<観点略語>-<タイトル>.md`
- gitignore: global gitignoreで除外済み
- フォーマット: @context/memory-file-formats.md
- **ファイル運用**: 追記・編集はEdit/Writeツールで行う（Bashのcat>>禁止）。頻繁に編集するファイルは300行超で分割（詳細: @context/memory-file-formats.md「ファイル運用ルール」）
- **絶対パス固定（CRITICAL）**: Phase 0 で**元repo（worktreeに入る前のrepo）のメモリディレクトリ絶対パス**を確定し、05_log.md 冒頭に記録すること。以後 EnterWorktree で worktree に移動しても、メモリ・issue ファイルの読み書きは必ずその**絶対パス**で行う（worktree 内には `.local/` ディレクトリが存在しないため、相対パス `.local/` でアクセスすると ENOENT になるか、書き込みなら worktree 内に新規作成されて元repoと分離される）

## ユーザーへの質問
- AskUserQuestionツールを使用。曖昧な点は推測せず必ず質問する
- スコープの勝手な縮小禁止。スケジュール・事実判断・金額・対外コミュニケーションは必ず確認

## コミット・ブランチ・PR
- コミット: `/commit`スキル使用。git-cz形式、絵文字なし、prefix以外は日本語。こまめにコミット
- PR作成: `/create-draft-pr`スキル使用。直接`gh pr create`を実行しない
- ブランチ: BASE_BRANCH（PJ CLAUDE.md参照、未定義時: develop→main→master）
- ブランチ命名: `feature/<issue_num>-<title-kebab>`、issue番号がない場合は `feature/<title-kebab>`。**prefixは原則 `feature/` で統一**（コミットメッセージのprefixはgit-cz形式と独立）
- ブランチ作り直し時: 既存コミットをrebase/cherry-pickで保全してからブランチ削除（コミット消失防止）

## worktree 運用ルール（CRITICAL）

### EnterWorktree を呼ぶケース（原則）
**コード編集 or ブランチ切替を伴う作業すべて** で EnterWorktree を呼ぶ:
- 新規ファイル作成・既存コード修正・リファクタ
- 新規ブランチ作成・既存ブランチへの切替
- 並列に進む可能性のある実装作業

### EnterWorktree を呼ばないケース（例外）
- `.claude/` 配下の設定ファイル・グローバル CLAUDE.md・context ガイドのみの編集（**ただしPJの`.claude/`等をコミットする場合は例外にせず、実装開始前ゲート（@context/workflow-rules.md Phase 3）に従い作業ブランチで行う**）
- メモリディレクトリ（`.local/memory/`、`.local/issues/`）のみの編集
- 純粋な調査・質問応答・読み取り専用作業
- ユーザーが「worktree 不要」「このタスクは worktree 切らなくていい」等と明示した場合

### 手順の詳細（Read when）
**EnterWorktree実行前・worktreeの片付け（ExitWorktree/ブランチ削除）前・並列bg session設計時に、必ず `context/worktree-guide.md` をRead**すること（ブランチ命名フロー・baseRef調整・削除時のコミット保全・並列時の競合回避・一時ファイル置き場の規定。読まずに実行するとブランチ名不整合やコミット消失を招く）。

## スキル発火ルール
**CRITICAL**: Available skillsに該当するスキルが存在する場合、直接ツールを呼び出さずスキルを発火させること

## 緩和しない安全項目（CRITICAL）

「自律実行」の名目でも以下は絶対に緩和しない:
- 推測禁止・調査先行（最優先指示）
- AskUserQuestionでの確認必須事項（スコープ縮小・スケジュール・金額・対外コミュニケーション）
- 破壊的操作（git push --force / git reset --hard / branch -D 等）の事前確認（`git push --force`/`-f`・`git branch -D`・`git reset`はpermissions.denyにも登録済（中間ワイルドカードで語順違いもカバー、--force-with-leaseは対象外） — 意図はここ、強制はdenyの多層防御）
- 破壊的データ操作（DB/バケット削除・大量DELETE等）は事前確認に加え、実行前に復旧手段（バックアップ・エクスポート）を確保する（ユーザーが毎回バックアップを承認条件とした実績による）
- コミット規約（git-cz形式、絵文字なし、secret未含有）
- 計画なしでの実装開始（複雑タスク時）
- 05_log.md未更新での次Phase進行（複雑タスク時）

## 禁止事項
詳細: @context/workflow-rules.md「禁止事項」セクション
- ユーザー指示・PJ規約を自己判断で上書きすること（スコープ縮小、パターン逸脱、品質基準変更を含む。必ずAskUserQuestion）
- 複雑タスクでの 05_log.md 未更新、agent review未実行での完了報告
- スキル存在時の直接ツール呼び出し

## Compact Instructions
When compacting, preserve: Active Agent Teams (name, members, task assignments, status), Task list state (in_progress/completed/pending + owners), Current phase (0-5) and progress, メモリディレクトリ絶対パスと計画ファイル（30_plan.md等）のパス.

**compaction後の復帰手順**: (1) Active Teamがあればまずteam config再確認とTaskList（`context/agent-teams-guide.md`「Context Compaction後の状態復元」をRead） → (2) 05_log.mdと計画ファイルを再読して文脈を復元する。ユーザーに文脈の再説明を求めない。

## GitHub CLI
gh cli利用時は`gh auth status`でアカウント確認。原則 username = ukwhatn。詳細はPJ CLAUDE.md参照。

## Cloudflare
詳細: @context/cloudflare-development.md

## パス表記の規約
本ファイルおよびcontext/skills内の `~/.claude/` 表記はユーザー設定ディレクトリを指す。`CLAUDE_CONFIG_DIR` を設定している環境ではそのディレクトリに読み替える（マシン固有の実パスは @CLAUDE.local.md 参照）。

## マシンローカル設定（git管理外）
このマシン固有の設定・運用メモ（gitignore対象。存在しない環境ではimportは無視される）:
@CLAUDE.local.md
