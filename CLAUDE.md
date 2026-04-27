# Global Settings

## 最優先指示: 推測禁止・調査先行・規約遵守
- 推測を一切禁止。事実と調査結果に基づいてのみ発言すること
- プロジェクトの既存パターン・規約を自己判断で上書き・逸脱しないこと。逸脱が必要な場合はAskUserQuestionで確認
- 修正前に対象技術の公式仕様をcontext7/WebSearchで調査すること（仕様理解→計画→修正）
- **UI仕様の確認時はFigma（`get_design_context`）を一次ソースとすること。ローカル仕様書は二次ソース**（詳細: @context/figma-verification.md）
- 不明な点は調査するか、AskUserQuestionで質問すること

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
4. 品質確認: lint/format/typecheck/test → 必要に応じて agent review
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

## ユーザーへの質問
- AskUserQuestionツールを使用。曖昧な点は推測せず必ず質問する
- スコープの勝手な縮小禁止。スケジュール・事実判断・金額・対外コミュニケーションは必ず確認

## コミット・ブランチ・PR
- コミット: `/commit`スキル使用。git-cz形式、絵文字なし、prefix以外は日本語。こまめにコミット
- PR作成: `/create-draft-pr`スキル使用。直接`gh pr create`を実行しない
- ブランチ: BASE_BRANCH（PJ CLAUDE.md参照、未定義時: develop→main→master）、命名: feature/<issue_num>-<title>
- ブランチ作り直し時: 既存コミットをrebase/cherry-pickで保全してからブランチ削除（コミット消失防止）

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
