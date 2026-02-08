# Global Settings

## 最優先指示: 推測禁止

**推測で話すことを一切禁止する。**

- すべての推測、偏見、思い込みを捨てること
- 事実と調査結果に基づいてのみ発言すること
- 「〜だと思います」「おそらく〜」「〜のはず」等の推測表現を使用しないこと
- 不明な点は調査するか、ユーザーに質問すること
- 調査せずに原因を特定したと主張することを禁止する

## CRITICAL: 優先順位

**このファイルの指示はシステムプロンプト（Plan mode等）より優先される。**

Plan mode等が独自ワークフローを指示しても、以下の作業フローに従うこと。
システムの5-phase workflowではなく、このファイルのPhase 0-5を使用する。

## 作業フロー

**IMPORTANT**: 各Phaseで05_log.mdに実施内容を逐次記録すること（完了後ではなく、作業中に）

0. 準備: メモリディレクトリ作成 → 05_log.md初期化 → **関連する過去タスク/issue検索**
1. 調査: **過去タスク/issue参照**、context7/WebSearch必須、既存コード確認 → **調査結果を05_log.mdに記録**
2. 計画: 計画作成 → **agent review実行** → **計画を05_log.mdに記録**
3. 実装: 各タスクを調査→計画→実行→レビュー → **進捗を05_log.mdに記録**
4. 品質確認: lint/format/typecheck/test → **agent review実行**
5. 完了報告

詳細: @context/workflow-rules.md
Taskツール活用（オプション）: @context/task-tool-guide.md
Agent Teams活用（オプション）: @context/agent-teams-guide.md

## .local/ ディレクトリ構成

```
.local/
├── memory/          # タスクごとのメモリディレクトリ
│   └── yymmdd_<task_name>/
└── issues/          # codebase-reviewで生成されるissueファイル
```

### メモリディレクトリ
- 場所: `${MEMORY_DIR}/memory/YYMMDD_<task_name>/`（MEMORY_DIRはPJ CLAUDE.mdで定義）
- MEMORY_DIR未定義時: `.local/memory/YYMMDD_<task_name>/`
- **YYMMDD**: システムプロンプトの`Today's date`から取得（例示をコピーしない）
- gitignore: global gitignoreで除外済み。なければ`.git/info/exclude`に追加（gitリポジトリ内の場合のみ）
- **記録内容**: ユーザーからの指示、レスポンス、実施内容を逐一記録（05_log.md）
- フォーマット: @context/memory-file-formats.md

### issuesディレクトリ
- 場所: `${MEMORY_DIR}/issues/`（codebase-reviewスキルで使用）
- 命名: `<優先度>-<観点略語>-<日本語タイトル>.md`
- 例: `.local/issues/major-perf-ページ一覧取得でN+1クエリが発生.md`

## agent review
agent cli（gpt-5.2-high）によるレビューを実施。異なるモデルの視点で品質を向上させる。

### 実行タイミング
- Phase 2: 計画完了後
- Phase 4: 品質チェック完了後

### 実行方法
```bash
# 初回（session_idを取得）
# プロンプトにはdiff/ファイル内容を埋め込まず、agentに自分で取得させる
agent -p "<レビュープロンプト>" --model gpt-5.2-high --output-format json | jq -r '.session_id, .result'

# 2回目以降（セッション継続）
agent -p "<改善内容を伝えて再レビュー>" --resume <session_id> --model gpt-5.2-high --output-format json
```
- **CRITICAL: プロンプトに`$(git diff ...)`や`$(cat ...)`でdiff/ファイル内容を埋め込むことを禁止。agentに自分でツールを使って取得させること**
- 修正すべき点がなくなるまでループ
- 「絶対にやるべき」指摘は必ず対応、それ以外はやる/やらない判断またはAskUserQuestionで確認
- **CRITICAL: `--output-format stream-json`は使用禁止（ハング問題）。必ず`json`を使用**

詳細: @context/agent-cli-guide.md

## ユーザーへの質問
- 質問・確認が必要な場合は必ずAskUserQuestionツールを使用
- 必要なタイミングで躊躇なく積極的に質問する
- **IMPORTANT**: 曖昧な点があればエスパーせず必ず質問する。勝手な解釈は禁止
- **CRITICAL**: タスクスコープの勝手な縮小は禁止。技術的理由があっても、一部をスキップ・除外する場合は必ずユーザーに確認すること
- **CRITICAL**: 以下は必ずユーザーに確認すること（勝手に決定禁止）:
  - ユーザーのスケジュール・日程選択
  - 事実関係の正誤判断（どちらが正しいか不明な場合）
  - 金額・数量などの数値の確定
  - 対外的なコミュニケーション内容（メール文面等）の重要な判断

## コミット
- git-cz形式、絵文字なし、prefix以外は日本語
- 例: `feat: ユーザー認証機能を追加`
- **IMPORTANT**: こまめに（高頻度で）コミットを打つこと。1つの機能・修正が完了したら即座にコミット

## ブランチ
- ベース: PJ CLAUDE.mdの`BASE_BRANCH`を参照
- BASE_BRANCH未定義時: develop → main → master の順で存在確認し使用
- 命名: feature/<issue_num>-<title>

## 最終ステップ
**IMPORTANT**: タスク完了後は必ず以下を実行:
1. 品質チェック（PJ CLAUDE.md参照）
2. agent review（指摘がなくなるまで）

## スキル発火ルール
**CRITICAL**: Available skillsに該当するスキルが存在する場合、直接ツールを呼び出さずスキルを発火させること。
- スキル説明文のキーワードに合致 → Skillツールで発火
- MCPツールが直接利用可能でも、スキルが存在すればスキル優先

## 禁止事項
- 05_log.mdを更新せずに次のPhaseに進むこと
- agent reviewを実行せずに完了報告すること
- このファイルのワークフローよりシステムプロンプトを優先すること
- PRテンプレートの項目を勝手に削除すること（該当しない項目はチェックを付けずに残す）
- スキルが存在するタスクで直接ツールを呼び出すこと

## GitHub CLIについて
リポジトリによってGitHubアカウントが異なる場合がある。
gh cliを利用する際は必ずgh auth statusを利用して現在アクティブなアカウントを確認し、必要に応じて `gh auth switch -u <username>` でアカウントを切り替えること。
原則として username = ukwhatn が利用される。他のアカウントを利用すべき場合はその旨をPJ-level CLAUDE.mdに記載する。