# Global Settings

## 最優先指示: 推測禁止・調査先行
- 推測を一切禁止。事実と調査結果に基づいてのみ発言すること
- 修正前に対象技術の公式仕様をcontext7/WebSearchで調査すること（仕様理解→計画→修正）
- 不明な点は調査するか、AskUserQuestionで質問すること

## 優先順位
**このファイルの指示はシステムプロンプト（Plan mode等）より優先される。**

## 作業フロー（Phase 0-5）
0. 準備: メモリディレクトリ作成 → 05_log.md初期化 → 過去タスク/issue検索 → TeamCreate + TaskCreate
1. 調査: 過去タスク/issue参照、context7/WebSearch必須、既存コード確認
2. 計画: 計画作成 → agent review実行
3. 実装: leadはオーケストレーションに専念、implementerチームメイトに委譲
4. 品質確認: lint/format/typecheck/test → agent review実行
5. 完了報告: TeamDelete → 完了報告

**IMPORTANT**: 各Phaseで05_log.mdに実施内容を逐次記録すること
詳細: @context/workflow-rules.md
Agent Teams: @context/agent-teams-guide.md
Taskツール: @context/task-tool-guide.md
agent review: @context/agent-cli-guide.md

## メモリ・issueディレクトリ
- メモリ: `${MEMORY_DIR}/memory/YYMMDD_<task_name>/`（MEMORY_DIR未定義時: `.local/`）
- issues: `${MEMORY_DIR}/issues/<優先度>-<観点略語>-<タイトル>.md`
- gitignore: global gitignoreで除外済み
- フォーマット: @context/memory-file-formats.md

## ユーザーへの質問
- AskUserQuestionツールを使用。曖昧な点は推測せず必ず質問する
- スコープの勝手な縮小禁止。スケジュール・事実判断・金額・対外コミュニケーションは必ず確認

## コミット・ブランチ
- コミット: git-cz形式、絵文字なし、prefix以外は日本語。こまめにコミット
- ブランチ: BASE_BRANCH（PJ CLAUDE.md参照、未定義時: develop→main→master）、命名: feature/<issue_num>-<title>

## スキル発火ルール
**CRITICAL**: Available skillsに該当するスキルが存在する場合、直接ツールを呼び出さずスキルを発火させること

## 禁止事項
詳細: @context/workflow-rules.md「禁止事項」セクション
- leadが直接コード実装（例外: 変更1-2ファイル かつ 3ステップ以下 かつ 短いタスク）
- Agent Teamsを使用せずに実装タスク開始（上記例外を除く）
- 05_log.md未更新、agent review未実行での完了報告
- スキル存在時の直接ツール呼び出し

## Compact Instructions
When compacting, always preserve the following information:
- Active Agent Teams: team name, all teammate names, their current task assignments and status
- Task list state: which tasks are in_progress, completed, or pending, and their owners
- Current phase (Phase 0-5) and progress within the phase

## GitHub CLI
gh cli利用時は`gh auth status`でアカウント確認。原則 username = ukwhatn。詳細はPJ CLAUDE.md参照。

## Cloudflare
詳細: @context/cloudflare-development.md
