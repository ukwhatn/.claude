# Workflow Detail

`design-feature` スキルの Phase 別具体手順。SKILL.md と併用。

## Phase 0: 準備

### 0.1 メモリディレクトリ確定

```bash
# 1. MEMORY_DIR を確認
# PJ CLAUDE.md に MEMORY_DIR 定義がなければ ${PJ_ROOT}/.local/ を使う

# 2. 既存ディレクトリ検索
ls ${MEMORY_DIR}/memory/ | grep -i "<キーワード>"

# 3-a. 同コンテキスト既存あり → 再利用、05_log.md に新日付セクション追記
# 3-b. なければ新規作成
mkdir -p ${MEMORY_DIR}/memory/YYMMDD_<context_name>/
```

context_name は kebab-case で短く（例: `instant-account`, `corp-login`, `bankpay-error`）。日付は **今日の日付**（システムプロンプトの Today から取得、例示の日付をコピーしない）。

### 0.2 絶対パス固定（CRITICAL）

worktree 運用時の事故防止のため、05_log.md 冒頭に必ず記録:

```markdown
# 作業ログ

**メモリディレクトリ絶対パス**: /Users/yuki.c.watanabe/dev/sol/das/.local/memory/260609_xxx/

## YYYY-MM-DD HH:MM - 初期指示
...
```

EnterWorktree で worktree に入っても、メモリの読み書きは**必ずこの絶対パスを使う**。worktree 内に `.local/` は存在しない。

### 0.3 タスク管理

TaskCreate で本ワークフローのタスクを構造化:

```
Task 1: Phase 1 要求深掘り
Task 2: Phase 2 既存実装調査（並列）
Task 3: Phase 3 01 ドラフト作成
Task 4: Phase 4 agent review ループ
Task 5: Phase 5 02 抽出 + 完了報告
```

依存関係を `addBlockedBy` で連鎖させる。

## Phase 1: 要求深掘り

### 1.1 質問テンプレート（AskUserQuestion 用）

抽象要件を受けたら、以下を **1〜2 回の AskUserQuestion** で確定する（一度に 4 つまで、multi-select で複数項目を一括で聞く）。

#### Q1: スコープ確定（multi-select）
- 解決したい問題は何か
- 対象アクター（エンドユーザー / RP / 社内 CS / Biz / 開発者）
- 新規 / 既存拡張 / 置換 / 共存 のどれか
- 既知バグ修正をスコープに含むか

#### Q2: 制約・優先度
- リリース希望時期
- 必須機能 / 任意機能 / スコープ外 の切り分け
- 法的制約・規約・対外コミュニケーションの有無
- 依存サービス（外部 API・他チーム）

#### Q3: 既存実装との関係
- 関連する既存機能・画面・API（既知のもの）
- 過去の関連タスク・issue（再開なら）
- メモリディレクトリのコンテキスト名（既存再利用 or 新規）

#### Q4: 出力先
- メモリディレクトリパス（デフォルト確認）
- 01 / 02 以外に作る必要があるサブドキュメント（PRD、Confluence 投稿用、社内向け FAQ 等）

質問の **粒度は具体的に**。「○○についてどうしますか」ではなく「A / B / C / その他」の選択肢を提示。

### 1.2 「曖昧なまま着手しない」原則

回答が曖昧（「適当に」「いい感じで」等）の場合、再質問する。**Step 2 以降を着手しない**。

### 1.3 05_log.md 記録

質問内容と回答を逐語記録:

```markdown
## YYYY-MM-DD HH:MM - Phase 1 要求深掘り

**AskUserQuestion Q1: スコープ確定**
- 質問: ...
- ユーザー回答: ...

**確定事項:**
- 目的: ...
- スコープ: 入る / 入らない を箇条書き
- 制約: ...
```

## Phase 2: 既存実装調査（コードベース SSoT）

### 2.1 並列調査パターン

Explore agent を 3-5 並列で起動。各 agent に **明確な検証クレーム** を渡す（「○○を調べて」ではなく「ドキュメント記述 X が実コード Y と一致するか」）。

```text
Agent 1: 対象機能に関連する既存コードの所在・パターン
Agent 2: データモデル（schema.prisma / domain 型）の現状
Agent 3: 既存ガード・procedure 階層・middleware
Agent 4: 関連する Cloud Task / Scheduler / Webhook（定義ファイル全件 grep で網羅確認、総件数を報告させる）
Agent 5: テンプレート・命名規約・規約同意・通知メール
```

各 agent への指示には「特定エントリの調査」と「対象カテゴリ全件の網羅確認」を分けて明記する。網羅確認を省くと一覧表の漏れに直結する（§2.5）。

### 2.2 Agent 判定の検証（CRITICAL）

Explore agent の判定をそのまま信用しない:

- **重要な「差異あり」報告は Read で実コードを直接確認する**
- agent は **Phase X で追加する内容を「現状無いから差異」と誤判定** する傾向あり
- 関数内部だけ見て**呼び出し元のガードを見落とす**こともある

### 2.3 公式仕様確認（必須）

対象技術の仕様は context7 または WebSearch で取得:

```bash
# 例: Prisma の特定機能の仕様
context7 → resolve-library-id("prisma") → get-library-docs(...)

# 例: OIDC backchannel logout の仕様
WebSearch("OIDC backchannel logout token spec")
```

SDK 型定義 ≠ 実機制約。AI / 外部 API 系は実呼び出しで検証 or ユーザー判断を仰ぐ。

### 2.4 調査結果の記録

`05_log.md` に逐次記録:

```markdown
**Phase 2 調査結果:**
- 既存 X は `path/to/file.ts:L<n>` で定義。パターンは ...
- Y は `path/to/g.ts` で実装されていないことを確認（grep 0 件）
- 公式仕様 Z: `<source URL>` 参照、要点は ...
```

`20_implementation_notes.md` に詳細を別記してもよい（後で 01 を書くときの参照源）。

### 2.5 一覧対象の網羅確認（CRITICAL）

01 / 02 に一覧表（Cloud Task / Scheduler / Webhook / API / メールテンプレート等）を載せる場合、定義箇所の SSoT ファイルを全件 grep してから作る:

```bash
# 例: Cloud Scheduler の全 procedure（一覧表のエントリ数と一致するか突合）
grep -cE 'cloudOidcTokenProcedure' src/server/routers/scheduler.ts
grep -nE 'path:\s+"/scheduler/' src/server/routers/scheduler.ts

# 例: Cloud Task の全 queue
grep -nE '^\s+"[a-z-]+":' src/server/domain/cloud_task.ts
```

- grep 件数 ≠ 一覧表エントリ数 なら漏れ。差分を特定して埋める
- 検証コマンドと件数を 05_log.md に記録
- 関連 usecase に複数ハンドラがまとまっているケース（例: `NegativeBalanceUsecase` 配下に 3 Scheduler）を見落としやすい。usecase 単位ではなく **router 定義単位** で数える
- 部分列挙が意図なら「一部抜粋（全 N 件中）」と明記

## Phase 3: 01 ドラフト作成

### 3.1 単独 vs 並列

#### 単独（通常）
小〜中規模なら、章順に Write で書き進める。

#### Ultracode 並列化
大規模なら Workflow で章別並列ドラフト → 統合:

```
Phase: Draft (parallel)
  - Agent A: 章 1-2（概要 + 状態遷移）
  - Agent B: 章 3（主要機能）
  - Agent C: 章 4-5（影響範囲 + 外部連携）
  - Agent D: 章 6-7（DB + エラー）
  - Agent E: 章 8-11（やらないこと + リリース）

Phase: Synthesize
  - Agent F: ドラフト統合・文体統一・章番号通し
```

各 agent への共通指示:
- ライティング規約（/ukwhatn-writing）
- 禁止フレーズリスト
- 既存実装の参照源（05_log.md / 20_implementation_notes.md）
- プロジェクトのアーキテクチャ参照（@.context/architecture-detail.md 等）

### 3.2 章構成（DAS 風の例。プロジェクトに応じて調整）

詳細テンプレ: doc-templates.md §「01 実装マスタ」

### 3.3 設計判断の確定

複数案で迷うときは AskUserQuestion で確定。

- 採用案 + 不採用案 + 理由をセット
- `30_decisions.md` または `99_history.md` に記録（既存ファイルがあれば追記、無ければ新規）
- 01 本文には**結論のみ**書く（背景は 30/99 に逃がす）

### 3.4 「別途決定」を残さない

Phase 2 調査または AskUserQuestion で必ず決め切る。残しそうになったら:

1. 既存パターン（同類実装）を Phase 2 で再調査
2. それでも決まらないなら AskUserQuestion
3. それでも決まらないなら「やらないこと」セクションに移す（理由付き）

## Phase 4: agent review ループ

@context/agent-cli-guide.md に従う。要点のみ:

### 4.1 CLI 選択

```bash
# cursor 優先、なければ codex
CURSOR_CLI="$(command -v cursor-agent || command -v agent)"
if [ -n "$CURSOR_CLI" ]; then
  REVIEW_CLI=cursor
elif command -v codex >/dev/null 2>&1; then
  REVIEW_CLI=codex
fi
```

### 4.2 初回プロンプト例

```text
このリポジトリの {ABSOLUTE_PATH}/01_requirements_skeleton.md を読んで、計画をレビューしてください。
関連する Phase 1 メモ {ABSOLUTE_PATH}/<phase1 関連ファイル> も参照してください。
コードベース全体（{REPO_ROOT}/src/）も SSoT として参照してください。

レビュー観点:
- 抜け漏れ
- 既存実装との不整合
- 設計上のリスク
- より良いアプローチの提案

指摘は以下で分類:
- Action Required: バグ / 不整合 / データ損失リスク
- Recommended: 改善推奨
- Minor: スタイル

指摘がなければ「指摘なし」とだけ回答。
```

### 4.3 ループ

```bash
# 初回
agent -p "$PROMPT" --trust --model gpt-5.5-xhigh-fast --output-format json 2>/dev/null | jq -r '.session_id, .result'

# 2 回目以降（同一 session）
agent -p "以下の改善を行いました: <差分>。再度レビューしてください。" \
  --resume <session_id> --trust --model gpt-5.5-xhigh-fast --output-format json 2>/dev/null | jq -r '.result'
```

打ち切り:
- Action Required = 0
- 同一指摘 2R 連続
- 安全上限 5R

### 4.4 指摘の実コード裏取り（CRITICAL）

agent の Action Required を反映する前に、Read で実コードを直接確認する:

- 関数の処理順序
- 呼び出し元のガード（関数内部だけでなく）
- 「Phase 2 で追加する内容」を「現状無いから差異」と誤判定していないか
- メソッドのアクセス修飾子（public/private）

事実と異なる Action Required は反映せず、05_log.md に「agent 誤判定」として記録。

## Phase 5: 02 抽出 + 完了報告

### 5.1 抽出アプローチ

#### 単独
01 を章順に走査し、What だけ抽出して 02 に書く。

#### Ultracode 並列化
Workflow で章別並列抽出 → 統合:

```
Phase: Draft chapters (parallel)
  - 各 agent に「Phase 1 Confluence スタイルのサンプル」と「01 の該当章」を渡す
  - 出力: 章ごとの What のみ Markdown

Phase: Synthesize
  - 統合・文体統一・章番号通し
  - メタ情報表追加、末尾にリリーススケジュール
```

### 5.2 抽出ルール（再掲）

| 書く | 書かない |
|------|---------|
| 機能の存在・挙動・入出力 | クラス名 / 関数名 / ファイルパス / 行番号 |
| 状態遷移・分岐条件 | Usecase / Service / Repository の構造 |
| API レスポンスのフィールド名 | DB テーブル名（最小限可、極力避ける） |
| scope / claim 名 | Procedure / queue key |
| 画面遷移の概要 | DI 構造 / middleware |
| エラーコード（仕様レベル） | エラーキー / status マッピング詳細 |
| Why は注記程度（「※」「→」、1-2 行） | Why の詳細な設計理由（30/99 に） |

### 5.3 完了確認の grep

```bash
# 禁止フレーズ
grep -nE '要調査|TBD|TODO|要確認|要検討|追って確認|別途決定|要相談|場合によっては|必要に応じて' \
  ${MEMORY_DIR}/memory/<dir>/{01_requirements_skeleton,02_system_requirements}.md

# 02 への How 混入チェック
grep -nE 'Usecase|Repository|Service|Adapter|procedure\.ts|router\.ts|@injectable|prisma\.\w+\.\w+' \
  ${MEMORY_DIR}/memory/<dir>/02_system_requirements.md
```

両方とも 0 件が完了基準。

### 5.4 完了報告フォーマット

```markdown
## 完了報告

### 作成ファイル
- `${MEMORY_DIR}/memory/<dir>/01_requirements_skeleton.md`（<N> 行）
- `${MEMORY_DIR}/memory/<dir>/02_system_requirements.md`（<N> 行）

### 主要設計判断
- Q1: 採用案 X（不採用案 Y、理由: ...）
- Q2: ...

### agent review
- Round <N> で Action Required = 0 達成
- 反映件数: 計 <N> 件

### 残課題（あれば）
- 具体的な未解決事項。「要調査」と書かず、必要なアクションを明示
    - 例「○○の運用フローを CS と合意（次セッションで実施）」
```
