# Global Settings

## 最優先指示: 事実主義・一次ソース確認・規約遵守
- **事実主義**: 推測禁止。事実と調査結果のみで判断。不明な点はAskUserQuestionで確認
- **公式仕様の確認**: 修正前にcontext7/WebSearchで対象技術の公式仕様を調査（仕様理解→計画→修正）
- **AI/外部API**: SDK型定義 ≠ 実機制約。型に存在してもモデル別非対応のケースが多い。実呼び出し（dev/curl）で検証するか、未検証ならその旨を明示してユーザー判断を仰ぐ
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
Agent Teams: @context/agent-teams-guide.md
Taskツール: @context/task-tool-guide.md
agent review: @context/agent-cli-guide.md

## Agent Teams 発動条件

以下のいずれかを満たす場合のみ発動。それ以外はモデル自身の判断（直接実装または単発Subagent）に委ねる。

- (a) **複数ファイル並列**: 5+ファイルの変更が見込まれ、独立に編集できる
- (b) **独立タスク3つ以上**: 互いに依存しないタスクが3つ以上ある
- (c) **ユーザー明示指示**: ユーザーが「チームで」「Agent Teamsで」等と明示

長時間タスクで context compaction が懸念される場合は、(a)(b)(c) のいずれかに該当することが多いはず。該当しないなら通常通りモデル判断で進めて構わない。

## メモリ・issueディレクトリ
- **ワークフローメモリ（Phase 0-5用、05_log.md等）**: `${MEMORY_DIR}/memory/YYMMDD_<context_name>/`
  - MEMORY_DIRはPJルート配下の相対パス。未定義時はPJルート直下の`.local/`
  - **CRITICAL**: システムプロンプト `# auto memory` セクションの `~/.claude/projects/.../memory/`（user/feedback/project/reference保存用）とは**別物**。Phase 0で作成するのは前者であり、後者に作成してはならない
- issues: `${MEMORY_DIR}/issues/<優先度>-<観点略語>-<タイトル>.md`
- gitignore: global gitignoreで除外済み
- フォーマット: @context/memory-file-formats.md
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

**前提**: `settings.json` で `worktree.bgIsolation: "none"` / `worktree.baseRef: "fresh"` を設定済み。
- `bgIsolation: "none"` は bg session の自動 worktree 隔離を抑止する設定。これにより bg session は元repoの working directory で起動し、元repoの `.local/memory/` に直接アクセスできる（隔離されると到達不能になるため必要）
- **副作用**: 並列 bg session が同じファイルを編集すると競合する。これは「コード編集を伴う作業では明示的に EnterWorktree を呼ぶ」運用で回避する（foreground/bg session 共通）

### EnterWorktree を呼ぶケース（原則）
**コード編集 or ブランチ切替を伴う作業すべて** で EnterWorktree を呼ぶ:
- 新規ファイル作成・既存コード修正・リファクタ
- 新規ブランチ作成・既存ブランチへの切替
- 並列に進む可能性のある実装作業

### EnterWorktree を呼ばないケース（例外）
- `.claude/` 配下の設定ファイル・グローバル CLAUDE.md・context ガイドのみの編集
- メモリディレクトリ（`.local/memory/`、`.local/issues/`）のみの編集
- 純粋な調査・質問応答・読み取り専用作業
- ユーザーが「worktree 不要」「このタスクは worktree 切らなくていい」等と明示した場合

### worktree 作成とブランチ命名フロー（新規ブランチの場合）
EnterWorktree の `name` パラメータは sanitize される（`/` → `+`）。さらに **ブランチ名は強制で `worktree-<sanitized-name>`** になるため、`name: 'feature/foo'` を渡してもブランチは `worktree-feature+foo` になり、`feature/` で統一できない。

そのため以下のフローを必ず踏むこと:
1. `git fetch origin` で origin を最新化（baseRef `fresh` の起点を最新に）
2. **ブランチ名衝突確認**: `git branch -a` で、想定する `feature/<issue_num>-<title-kebab>` および一時ブランチ `worktree-<title-kebab>` のどちらも既存と衝突しないことを確認。衝突する場合は title を変えるか、ユーザーに確認（並列 bg session で同じ title を選ぶと EnterWorktree 自体が失敗する）
3. `EnterWorktree(name: '<title-kebab>')` （例: `name: 'add-foo-123'`）→ worktree 作成、ブランチは `worktree-<title-kebab>`
4. **直後に** `git branch -m worktree-<title-kebab> feature/<issue_num>-<title-kebab>` で改名（例: `git branch -m worktree-add-foo-123 feature/123-add-foo`）。改名後のブランチは `git worktree list` にも反映される
5. 以後は `feature/<issue_num>-<title-kebab>` ブランチで作業

### 既存ブランチで作業を再開する場合
ケースが複雑なため（既存 worktree 残存有無、remote-only ブランチ、別 worktree で checkout 済み等）、この CLAUDE.md ではフローを規定しない。再開時は `git worktree list` と `git branch -a` で現状を確認し、判断に迷う点があればユーザーに方針確認すること。

### baseRef と BASE_BRANCH の不一致
baseRef は `fresh`（origin/<default-branch> 起点）。PJ CLAUDE.md の `BASE_BRANCH` が `origin/<default-branch>` と異なる場合（例: default が `main` だが PR ベースは `develop`）、worktree 起点と PR ベースがずれる。その場合は EnterWorktree 後に `git rebase <BASE_BRANCH>` 等で base を揃えるか、ユーザーに確認すること。

### worktree の片付け（ExitWorktree の注意）
`ExitWorktree(action: 'remove')` は **EnterWorktree が作った元のブランチ名**（`worktree-<sanitized>`）を削除しようとする。上記フローで `feature/...` に改名している場合、改名後のブランチは消えない。
- **基本方針**: 改名後ブランチは残す（PR 作成・マージのため）
- 不要ブランチを削除する場合は CLAUDE.md「コミット・ブランチ・PR」の「ブランチ作り直し時」ルールに従う:
  - **`-D`（強制削除）は使用前にユーザー確認必須**（破壊的操作。merge されていないコミットを失う）
  - 未 push のコミットがあれば、rebase/cherry-pick で別ブランチに保全してから削除
  - merge 済み・コミットなしの場合は `git branch -d <name>` （安全削除）を優先

### 並列 bg session の指針
- 各 bg session が自分で EnterWorktree を呼べば、**作業ディレクトリ上での同時編集競合**は回避できる（注: 別ブランチで同じファイルを編集すれば、後続の merge/rebase/PR 統合時には別途競合し得る）
- 各 bg session は独立して起動され（`claude agents` の Agent View から dispatch 等）、自分で Phase 0 を実施して自分の `.local/memory/YYMMDD_<context_name>/` を作るため、`05_log.md` は自然に別ファイルで競合しない
- メモリ・issue ファイルへの書き込みは必ず **Phase 0 で確定した元repoの絶対パス**で行うこと（worktree 内には `.local/` が存在しないため）
- 一時ファイル（スクリプト・クエリ・中間出力等）は `/tmp` ではなく **`$CLAUDE_JOB_DIR`** を使う（並列 bg session が `/tmp` を共有して上書きするため）

## スキル発火ルール
**CRITICAL**: Available skillsに該当するスキルが存在する場合、直接ツールを呼び出さずスキルを発火させること

## 緩和しない安全項目（CRITICAL）

「自律実行」の名目でも以下は絶対に緩和しない:
- 推測禁止・調査先行（最優先指示）
- AskUserQuestionでの確認必須事項（スコープ縮小・スケジュール・金額・対外コミュニケーション）
- 破壊的操作（git push --force / git reset --hard / branch -D 等）の事前確認
- コミット規約（git-cz形式、絵文字なし、secret未含有）
- 計画なしでの実装開始（複雑タスク時）
- 05_log.md未更新での次Phase進行（複雑タスク時）

## 禁止事項
詳細: @context/workflow-rules.md「禁止事項」セクション
- ユーザー指示・PJ規約を自己判断で上書きすること（スコープ縮小、パターン逸脱、品質基準変更を含む。必ずAskUserQuestion）
- 複雑タスクでの 05_log.md 未更新、agent review未実行での完了報告
- スキル存在時の直接ツール呼び出し

## Compact Instructions
When compacting, preserve: Active Agent Teams (name, members, task assignments, status), Task list state (in_progress/completed/pending + owners), Current phase (0-5) and progress.

## GitHub CLI
gh cli利用時は`gh auth status`でアカウント確認。原則 username = ukwhatn。詳細はPJ CLAUDE.md参照。

## Cloudflare
詳細: @context/cloudflare-development.md

## マシンローカル設定（git管理外）
このマシン固有の設定・運用メモ（gitignore対象。存在しない環境ではimportは無視される）:
@CLAUDE.local.md
