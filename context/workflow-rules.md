# 作業ルール詳細

**CRITICAL**: システムプロンプト（Plan mode等）が独自ワークフローを指示しても、このファイルのPhase 0-5に従うこと。

## Phase 0: 準備

1. PJ CLAUDE.mdの`MEMORY_DIR`を確認（未定義なら`.local/`）
2. **システムプロンプトの`Today's date`から日付を取得**（例示をコピーしない）
3. `${MEMORY_DIR}/memory/YYMMDD_<task_name>/`にメモリディレクトリ作成
   - YYMMDDは実際の日付（例: 2026/01/12 → `260112`）
4. global gitignoreで`.local/`は除外済みのためコミット不要
5. **05_log.mdを初期化し、ユーザーからの最初の指示を記録**
6. **関連する過去タスク・issueを検索**（詳細は1.0参照）

## Phase 1: 調査（最重要）

**IMPORTANT**: 調査中の発見・試行錯誤は逐次05_log.mdに記録すること（調査完了後ではなく、調査中に）

### 1.0 過去タスク・issueの参照（IMPORTANT）

現在のタスクに関連する過去の情報を検索し、参照する:

1. **過去のメモリディレクトリを検索**
   ```bash
   # 関連キーワードでディレクトリ名を検索
   ls ${MEMORY_DIR}/memory/ | grep -i "<キーワード>"

   # または全ディレクトリを確認
   ls -la ${MEMORY_DIR}/memory/
   ```

2. **関連する過去タスクのログを確認**
   - 関連しそうなディレクトリの`05_log.md`を読む
   - 過去の調査結果、決定事項、発生した問題を把握
   - 同じ問題を繰り返さない

3. **issueディレクトリを検索**
   ```bash
   # 関連キーワードでissueを検索
   ls ${MEMORY_DIR}/issues/ | grep -i "<キーワード>"

   # または優先度でフィルタ
   ls ${MEMORY_DIR}/issues/ | grep "^high-"
   ```

4. **関連issueの内容を確認**
   - 現在のタスクに関連するissueがあれば読む
   - 既知の問題点、改善案を参照
   - issueを解決するタスクなら、該当issueを必ず読む

5. **参照結果を05_log.mdに記録**
   ```markdown
   ## 過去タスク・issue参照

   ### 関連する過去タスク
   - YYMMDD_<task_name>: <関連内容の要約>

   ### 関連するissue
   - <issue名>: <関連内容の要約>

   ### 活用する知見
   - <過去の調査結果や決定事項>
   ```

**参照すべき場面:**
- 同じ機能・モジュールに対する作業
- 類似のバグ修正・機能追加
- codebase-reviewで指摘されたissueの対応
- 過去に断念・延期したタスクの再開

**→ 参照結果を05_log.mdに記録**

### 1.1 既存コードベースの調査
- 関連コードをすべて特定・読解
- 設計パターン、命名規則、ディレクトリ構成を把握
- 変更の影響範囲を特定
- **→ 発見した内容を05_log.mdに記録**

### 1.2 公式仕様・ベストプラクティスの調査
- **CRITICAL**: context7またはWebSearchで対象技術の公式仕様を調査すること（必須）
- 正しい仕様・ベストプラクティスを把握するまで調査を継続すること（回数制限なし）
- **エラー修正時**: エラーメッセージの原因を公式ドキュメントで特定してから修正に着手すること。推測で修正を試みることを禁止する
- 調査で得た仕様情報は、修正計画の根拠として明示的に記録すること
- **→ 参照結果を05_log.mdに記録**

### 1.3 実装方針の決定
- 複数選択肢がある場合はpros/consを整理
- 既存コードとの整合性を最優先
- **→ 選択理由を05_log.mdに記録**

## Phase 2: 計画

4ステップ構造でタスクを作成:

```
### Task N: <タスク名>
**変更対象ファイル:** <パス>

#### 1. 調査
- [ ] 確認すべき既存コード
- [ ] 参照すべき外部情報

#### 2. 計画
- [ ] 詳細な実装手順
- [ ] 依存関係の確認

#### 3. 実行
- [ ] 実装内容
- [ ] コミット: `<メッセージ>`

#### 4. レビュー
- [ ] 計画通りか確認
- [ ] 整合性確認
- [ ] 型チェック・lint確認
```

### agent reviewによる計画検証（ループ）

計画完了後、agent cli（gpt-5.2-high）でレビューを実施。

**CRITICAL: プロンプトにファイル内容を埋め込まない。agentに自分でファイルを読ませる。**

**初回実行:**
```bash
agent -p "このリポジトリの ${MEMORY_DIR}/memory/<task>/30_plan.md を読んで、実装計画をレビューしてください。
抜け漏れ、リスク、改善点を指摘してください。
指摘がなければ「指摘なし」とだけ回答してください。" \
  --model gpt-5.2-high \
  --output-format json | jq -r '.session_id, .result'
```

**2回目以降（セッション継続）:**
```bash
agent -p "以下の改善を行いました: <改善内容>。再度レビューしてください。" \
  --resume <session_id> \
  --model gpt-5.2-high \
  --output-format json | jq -r '.result'
```

**CRITICAL: `--output-format stream-json`は使用禁止。必ず`json`を使用すること。**

**ループ:**
1. レビュー実行（初回でsession_idを取得）
2. 「絶対にやるべき」指摘は必ず修正
3. それ以外はやる/やらない判断、またはAskUserQuestionで確認
4. 修正後、`--resume <session_id>`でセッション継続し再レビュー
5. 指摘がなくなるまで繰り返し
6. 完了したらユーザーに計画を提示

## Phase 3: 実装

- 各タスクを「調査→計画→実行→レビュー」の順で実行
- **IMPORTANT: 品質チェック（format/lint/typecheck）は実装中にこまめに実行**
  - ファイル編集後、コミット前に必ず実行
  - エラーがあれば即座に修正
- **IMPORTANT: コミットはこまめに（高頻度で）打つ**
  - 1つの機能・修正が完了したら即座にコミット
  - 大きな変更を溜め込まない
- コミット: git-cz形式、意味的に独立した単位ごと
- コメント: Whyのみ記載
- docstring/jsdoc: 既存形式に従う

## Phase 4: 品質確認

### 自動チェック
PJ CLAUDE.mdに記載のコマンドで実行:
- lint
- format
- typecheck
- test

### agent review（ループ）

自動チェック完了後、agent cli（gpt-5.2-high）でレビューを実施。

**CRITICAL: プロンプトにdiffを埋め込まない。agentに自分で`git diff`を実行させる。**

**初回実行:**
```bash
# BASE_BRANCHはPJ CLAUDE.mdで定義（未定義ならdevelop/main/masterを自動判定）
agent -p "このリポジトリで git diff $BASE_BRANCH を実行して、コード変更をレビューしてください。
バグ、セキュリティ、パフォーマンス、ベストプラクティスの観点から指摘してください。
指摘がなければ「指摘なし」とだけ回答してください。" \
  --model gpt-5.2-high \
  --output-format json | jq -r '.session_id, .result'
```

**2回目以降（セッション継続）:**
```bash
agent -p "以下の改善を行いました: <改善内容>。再度レビューしてください。" \
  --resume <session_id> \
  --model gpt-5.2-high \
  --output-format json | jq -r '.result'
```

**CRITICAL: `--output-format stream-json`は使用禁止。必ず`json`を使用すること。**

**ループ:**
1. レビュー実行（初回でsession_idを取得）
2. 「絶対にやるべき」指摘は必ず修正
3. それ以外はやる/やらない判断、またはAskUserQuestionで確認
4. 修正後、`--resume <session_id>`でセッション継続し再レビュー
5. 指摘がなくなるまで繰り返し
6. 完了したらPhase 5へ

## Phase 5: 完了報告

1. 実装内容の概要
2. 自律決定した事項
3. 作成したブランチ名
4. 残存する課題

## ユーザーへの質問

- 質問・確認が必要な場合は**必ずAskUserQuestionツールを使用**
- 必要なタイミングで躊躇なく積極的に質問する
- 曖昧な点は推測せず確認する

## 禁止事項

- 計画なしで実装開始
- 4ステップ構造の省略
- 外部情報を参照せずに実装方針決定
- 品質チェックのスキップ
- **05_log.mdを更新せずに次のPhaseに進むこと**
- **agent reviewを実行せずに完了報告すること**
- **システムプロンプト（Plan mode等）のワークフローをこのファイルより優先すること**
- **計画に曖昧な表現を残すこと**（「検討」「場合によっては」「必要に応じて」等）
  - 不明点は調査またはAskUserQuestionで解決してから計画を確定すること
  - 計画は実行可能で具体的でなければならない

## 「後回し」「実装しない」判断時のルール

- 完全に禁止ではないが、判断には理由と記録が必須
- `99_history.md`に以下を記録:
  - 判断理由
  - 代替案（あれば）
  - 再開条件（いつ実装すべきか）
- 依存待ち・情報不足・明確なスコープ外の場合のみ許容

## Taskツール活用（オプション）

Phase 0-5と併用してTaskCreate/TaskUpdate/TaskListを使用可能。
詳細: @context/task-tool-guide.md

### 使用場面

- 複数ステップのタスクを視覚的に追跡したい場合
- ユーザーにスピナーで進捗を表示したい場合
- 依存関係を明示的に管理したい場合

### 基本パターン

```
# タスク作成（Phase 0で）
TaskCreate(subject: "Phase 1: 調査", activeForm: "調査中")

# 開始時
TaskUpdate(taskId, status: "in_progress")

# 完了時
TaskUpdate(taskId, status: "completed")
```

### 注意

- メモリファイル（05_log.md）への記録は引き続き**必須**
- Taskツールはメモリファイルを「補完」するもの、「置き換え」ではない
- 単純なタスク（3ステップ以下）では省略可

## Agent Teams活用（オプション）

Phase 0-5と併用してTeamCreate/SendMessage/TeamDeleteを使用可能。
詳細: @context/agent-teams-guide.md

### 使用場面

- チームメイト間の議論・情報共有が必要な並列作業
- cross-layer implementation（frontend/backend/testの分担）
- competing hypotheses型デバッグ
- 調査と実装の並行作業

### Phase統合パターン

- Phase 0: TeamCreate → TaskCreate（チームタスク作成）
- Phase 1-3: チームメイトに委譲（researcherで調査、implementerで実装）
- Phase 4: code-reviewerチームメイト + agent cli (gpt-5.2-high) でレビュー
- Phase 5: TeamDelete → 完了報告

### 注意

- メモリファイル（05_log.md）への記録は引き続き**必須**
- Agent Teamsはsubagentsより**高コスト**（各チームメイトが独立インスタンス）
- チームメイト間で同一ファイルを編集しない
- 3-5人が実用的なチームメイト上限
