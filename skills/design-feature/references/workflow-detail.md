# Workflow Detail

`design-feature` スキルの Step 別の具体手順。SKILL.md と併せて読む。

## 目次

- Step 1: 準備
- Step 2: 要求深掘り
- Step 3: 既存実装調査（コードベースが正本）
- Step 4: 01 ドラフト作成
- Step 5: 外部レビュー
- Step 6: 02 抽出 + 完了報告

## Step 1: 準備

### 1.1 メモリディレクトリ確定

```bash
# 1. MEMORY_DIR を確認
# PJ CLAUDE.md に MEMORY_DIR 定義がなければ ${PJ_ROOT}/.local/ を使う

# 2. 既存ディレクトリ検索
ls ${MEMORY_DIR}/memory/ | grep -i "<キーワード>"

# 3-a. 同コンテキスト既存あり → 再利用、05_log.md に新日付セクション追記
# 3-b. なければ新規作成
mkdir -p ${MEMORY_DIR}/memory/YYMMDD_<context_name>/
```

context_name は kebab-case で短く（例: `<機能名>-spec`, `<画面名>-login`, `<機能名>-error`）。日付はシステムプロンプトの Today's date から取る（例示の日付をコピーしない）。

### 1.2 絶対パスの記録

05_log.md の冒頭に記録する。

```markdown
# 作業ログ

**メモリディレクトリ絶対パス**: <PJルートの絶対パス>/.local/memory/YYMMDD_<context_name>/

## YYYY-MM-DD HH:MM - 初期指示
...
```

EnterWorktree で worktree に入っても、メモリの読み書きはこの絶対パスで行う。worktree 内に `.local/` は無い。

### 1.3 作業項目

Step 2〜6 を作業項目として登録する（taskboard が繋がっていれば `/taskboard`、Codex は plan 機構）。Step 3 は Step 2 と並行してよく、Step 4 以降は前の Step の完了を待つ。

## Step 2: 要求深掘り

### 2.1 質問テンプレート（AskUserQuestion 用）

抽象要件を受けたら、以下を1〜2回の AskUserQuestion で確定する。1回に複数の question を出すときは、各 question の文に背景と推奨の理由を1文ずつ入れて自己完結させる（AGENTS.md「確認が要るもの」の質問の出し方）。

#### Q1: スコープ確定（multi-select）
- 解決したい問題は何か
- 対象アクター（エンドユーザー / 連携先 / サポート担当 / 企画・事業側 / 開発者）
- 新規 / 既存拡張 / 置換 / 共存 のどれか
- 既知バグ修正をスコープに含むか

#### Q2: 制約・優先度
- リリース希望時期
- 必須機能 / 任意機能 / スコープ外 の切り分け
- 法的制約・規約・対外コミュニケーションの有無
- 依存サービス（外部API・他チーム）

#### Q3: 既存実装との関係
- 関連する既存機能・画面・API（既知のもの）
- 過去の関連タスク・issue（再開なら）
- メモリディレクトリのコンテキスト名（既存再利用 or 新規）

#### Q4: 出力先
- メモリディレクトリパス（デフォルト確認）
- 01 / 02以外に作る必要があるサブドキュメント（PRD、ドキュメントツール投稿用、関係者向けFAQ等）

「○○についてどうしますか」ではなく「A / B / C / その他」の選択肢を示す。

### 2.2 曖昧なまま着手しない

回答が曖昧（「適当に」「いい感じで」等）なら再質問し、Step 3 以降に入らない。

### 2.3 05_log.md への記録

質問と回答を逐語で記録する。

```markdown
## YYYY-MM-DD HH:MM - Step 2 要求深掘り

**AskUserQuestion Q1: スコープ確定**
- 質問: ...
- ユーザー回答: ...

**確定事項:**
- 目的: ...
- スコープ: 入る / 入らない を箇条書き
- 制約: ...
```

## Step 3: 既存実装調査（コードベースが正本）

### 3.1 並列調査パターン

Agent tool で `subagent_type: "Explore"`・`model: "sonnet"` を3〜5並列で起動する。各 agent には検証できる主張を渡す（「○○を調べて」ではなく「ドキュメントの記述 X が実コード Y と一致するか」）。

```text
Agent 1: 対象機能に関連する既存コードの所在・パターン
Agent 2: データモデル（スキーマ定義 / domain 型）の現状
Agent 3: 既存ガード・procedure 階層・middleware
Agent 4: 関連する非同期ジョブ / 定期実行 / Webhook（定義ファイルを全件 grep し、総件数を報告させる）
Agent 5: テンプレート・命名規約・規約同意・通知メール
```

各 agent への指示には「特定エントリの調査」と「対象カテゴリ全件の網羅確認」を分けて書く。網羅確認を省くと一覧表に漏れが出る（3.5）。各指示の末尾に「列挙した調査項目を全部調べ終えるまで止まらず、終わったら報告して止まる。修正や依頼外の提案はしない」を入れる。

### 3.2 agent の報告の突き合わせ

結論を左右する「差異あり」の報告は、Read で実コードを直接確かめてから採用する。agent が誤りやすい型は次の2つ。

- 後続フェーズで足す内容を「現状に無いから差異」と判定する
- 関数の内部だけ見て、呼び出し元のガードを見落とす

### 3.3 公式仕様の確認

対象技術の仕様は context7 か WebSearch で取る。

```bash
# 例: ORM の特定機能の仕様
context7 → resolve-library-id("<ライブラリ名>") → get-library-docs(...)

# 例: プロトコル仕様
WebSearch("OIDC backchannel logout token spec")
```

SDK の型定義は実機の制約を保証しない。AI・外部 API 系は実際に呼んで確かめるか、ユーザーの判断を仰ぐ。

### 3.4 調査結果の記録

結論を左右する発見だけを `05_log.md` に記録する。

```markdown
**Step 3 調査結果:**
- 既存 X は `path/to/file.ts:L<n>` で定義。パターンは ...
- Y は `path/to/g.ts` で実装されていないことを確認（grep 0 件）
- 公式仕様 Z: `<source URL>` 参照、要点は ...
```

詳細は `20_implementation_notes.md` に別記してよい（01を書くときの参照源）。

### 3.5 一覧対象の網羅確認

01 / 02に一覧表（非同期ジョブ / 定期実行 / Webhook / API / メールテンプレート等）を載せるなら、定義箇所のファイルを全件 grep してから作る。

```bash
# 例: 定期実行の全エンドポイント（一覧表のエントリ数と突き合わせる）
grep -cE '<定期実行の procedure を作る関数名>' <定期実行の router 定義ファイル>
grep -nE 'path:\s+"/<定期実行のパス接頭辞>/' <定期実行の router 定義ファイル>

# 例: 非同期ジョブの全キュー
grep -nE '^\s+"[a-z-]+":' <キュー定義ファイル>
```

- grep の件数と一覧表のエントリ数が違えば漏れがある。差分を特定して埋める
- 検証コマンドと件数を05_log.md に記録する
- 1つの usecase に複数のハンドラがまとまっていると見落としやすい。usecase 単位ではなく router 定義単位で数える
- 部分列挙が意図なら「一部抜粋（全N件中）」と書く

## Step 4: 01 ドラフト作成

### 4.1 単独か並列か

#### 単独（通常）
章順に Write で書き進める。

#### 並列化（ユーザー指示時のみ）
ユーザーが `ultracode` の語を使ったか並列化を明示したときだけ、Workflow で章別に並列ドラフトして統合する。規模を理由に自分で起動しない。

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
- プロジェクトのアーキテクチャ参照（PJ の `.claude/context/` 等）

### 4.2 章構成

プロジェクトに合わせて調整する。テンプレートは doc-templates.md「01実装マスタ」。

### 4.3 設計判断の確定

複数案で迷うときは AskUserQuestion で確定する。

- 採用案・不採用案・理由をセットにする
- `30_decisions.md` か `99_history.md` に記録する（既存ファイルがあれば追記）
- 01本文には結論だけを書く（背景は30・99に書く）

### 4.4 「別途決定」を残さない

Step 3 の調査か AskUserQuestion で決め切る。残しそうになったら次の順で扱う。

1. 既存パターン（同類の実装）を Step 3 の手順で調べ直す
2. それでも決まらないなら AskUserQuestion
3. それでも決まらないなら「やらないこと」セクションに理由付きで移す

## Step 5: 外部レビュー

CLI の選択・呼び出し・`resume` による継続・Severity 別の判断・打ち切り条件は `context/agent-cli-guide.md` に従う（設計文書のラウンド上限は同ガイド「レビューループ」）。

### 5.1 初回プロンプト例

```text
このリポジトリの {ABSOLUTE_PATH}/01_requirements_skeleton.md を読んで、計画をレビューしてください。
関連する要求深掘りのメモ {ABSOLUTE_PATH}/<関連ファイル> も参照してください。
コードベース全体（{REPO_ROOT}/src/）も正本として参照してください。

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

### 5.2 指摘の実コードでの裏取り

Action Required を反映する前に、Read で実コードを確かめる。

- 関数の処理順序
- 呼び出し元のガード（関数内部だけでなく）
- 後続フェーズで足す内容を「現状に無いから差異」と判定していないか
- メソッドのアクセス修飾子（public/private）

事実と異なる Action Required は反映せず、05_log.md に「agent 誤判定」として記録する。

## Step 6: 02 抽出 + 完了報告

### 6.1 抽出のやり方

#### 単独
01 を章順に走査し、What だけを抽出して02に書く。

#### 並列化（ユーザー指示時のみ）
ユーザーが `ultracode` の語を使ったか並列化を明示したときだけ、Workflow で章別に並列抽出して統合する。

```
Phase: Draft chapters (parallel)
  - 各 agent に「既存フェーズのシステム要件書のサンプル」と「01 の該当章」を渡す
  - 出力: 章ごとの What のみ Markdown

Phase: Synthesize
  - 統合・文体統一・章番号通し
  - メタ情報表追加、末尾にリリーススケジュール
```

### 6.2 抽出ルール

SKILL.md「Step 6」の表に従う。

### 6.3 完了確認の grep

```bash
# 禁止フレーズ
grep -nE '要調査|TBD|TODO|要確認|要検討|追って確認|別途決定|要相談|場合によっては|必要に応じて' \
  ${MEMORY_DIR}/memory/<dir>/{01_requirements_skeleton,02_system_requirements}.md

# 02 への How 混入チェック
grep -nE 'Usecase|Repository|Service|Adapter|procedure\.ts|router\.ts|@injectable|prisma\.\w+\.\w+' \
  ${MEMORY_DIR}/memory/<dir>/02_system_requirements.md
```

両方とも0件が完了基準。

### 6.4 完了報告フォーマット

```markdown
## 完了報告

### 作成ファイル
- `${MEMORY_DIR}/memory/<dir>/01_requirements_skeleton.md`（<N> 行）
- `${MEMORY_DIR}/memory/<dir>/02_system_requirements.md`（<N> 行）

### 主要設計判断
- Q1: 採用案 X（不採用案 Y、理由: ...）
- Q2: ...

### 外部レビュー
- Round <N> で Action Required = 0 達成
- 反映件数: 計 <N> 件

### 残課題（あれば）
- 具体的な未解決事項。「要調査」と書かず、必要なアクションを明示
    - 例「○○の運用フローをサポート担当と合意（次セッションで実施）」
```
