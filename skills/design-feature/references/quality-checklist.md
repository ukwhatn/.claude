# Quality Checklist

`design-feature` スキルの品質基準・チェックリスト・禁止フレーズ。

---

## 禁止フレーズ（01 / 02 共通）

以下は 01 / 02 のいずれにも書かない。書く前に Phase 2 で情報を揃えるか、AskUserQuestion で確定する。

| 禁止フレーズ | 代替アクション |
|------------|-------------|
| 要調査 | Phase 2 で実コード確認 / context7 / WebSearch |
| TBD / TODO | AskUserQuestion で確定 |
| 要確認 / 要相談 | AskUserQuestion で確定 |
| 要検討 | 代替案を出して採否を判断、または「やらないこと」に移す |
| 追って確認 | 確認してから書く（書く前提を満たさない箇所は書かない） |
| 別途決定 | Phase 2 / AskUserQuestion で確定するか、「やらないこと」に移す |
| 場合によっては | 条件を具体化（「○○の場合」と書く） |
| 必要に応じて | 必要な条件を具体化、または削除 |
| （推定） / おそらく / と思われる | 原典（実コード / 公式仕様）で確定してから書く。確定できないなら AskUserQuestion |

### 例外（許容ケース）

- 「やらないこと」セクション内で**スコープ外と明示した上で**「将来必要になれば検討」を示す場合は許容。ただし「要検討」とは書かず、具体的に「<トリガー条件> が発生した時点で再検討」と書く
- 既知バグ修正の説明で「Phase 1 で問題化しなかった理由」のように**事実説明**として「検討」「確認」を使うのは可

### 一括チェック

```bash
grep -nE '要調査|TBD|TODO|要確認|要検討|追って確認|別途決定|要相談|場合によっては|必要に応じて|（推定）|推定）|おそらく|と思われる' \
  ${MEMORY_DIR}/memory/<dir>/{01_requirements_skeleton,02_system_requirements}.md
```

---

## 02 への How 混入チェック

02 は What のみ。以下が混入していないか確認:

```bash
# クラス・関数・ファイル名・行番号
grep -nE 'Usecase|Repository|Service|Adapter|procedure\.ts|router\.ts|usecase\.ts|repository\.ts|service\.ts|@injectable|prisma\.\w+\.\w+' \
  02_system_requirements.md

# パス・行番号
grep -nE ':L?[0-9]+|/src/|/usecase/|/repository/|/service/|/adapter/|/routers/' \
  02_system_requirements.md

# キュー名・middleware
grep -nE 'queue|middleware|protectedProcedure|publicProcedure|instantAllowedProcedure' \
  02_system_requirements.md
```

### 02 で許容される技術的識別子

- API レスポンスのフィールド名（例: `isInstant`、`account_type`）
- scope / claim 名（例: `instant_account_allowed`、`account_type=instant`）
- エラーコード（例: `INSTANT_ACCOUNT_NOT_ALLOWED`）
- 画面 URL のパス例（例: `/instant/register`）
- 仕様上必要なテーブル名（最小限。極力削る）

---

## コードベース SSoT 整合性チェック

01 を書いた後、agent review に渡す前に以下を確認:

### 1. 引用した既存コードの正確性

01 で `path:Lnum` 引用したコードが実コードと一致しているか:

```bash
# 引用箇所をリストアップ
grep -nE '`[^`]+\.ts:?L?[0-9]+`?' 01_requirements_skeleton.md

# 各引用先を Read で確認（行数が大きく変わっていれば 01 を更新）
```

### 2. メソッド名のアクセス修飾子

private メソッド名を 01 に直書きしていないか確認:

- 既存実装で **public method** がある場合は public 名を使う
- private 名を書いてはいけない（agent review でも指摘される）

### 3. 「現状無いから差異」誤判定の予防

01 で「Phase X で追加する」と書いた箇所は、実コードに **無いのが正しい**。agent review でこれを「差異あり」と誤判定されないよう、表現を「Phase X で新規追加する」「現状未実装 → 追加する」と明示する。

### 4. 呼び出し元のガード見落とし予防

ある関数が `isInstant=true` で動作するかを判定するとき、関数内部のチェックだけでなく**呼び出し元のガード**も見る:

- `inactivateAsync:435` の `if (!isInstant)` ガード → `finalizeFullAccountResources` 自体には isInstant チェックなし、でも全スキップは事実
- このパターンは agent でも見落としやすい。01 / 02 のレビュー時に再確認

### 5. 一覧表の網羅性検証

Cloud Task / Scheduler / Webhook / API 等の一覧表は、SSoT ファイル全件 grep の結果と突合する:

```bash
# 例: Cloud Scheduler の全 procedure を抽出（一覧表の行数と一致するか確認）
grep -cE 'cloudOidcTokenProcedure' src/server/routers/scheduler.ts
grep -nE 'path:\s+"/scheduler/' src/server/routers/scheduler.ts

# 例: Cloud Task の全 queue を抽出
grep -nE '^\s+"[a-z-]+":' src/server/domain/cloud_task.ts
```

- grep 件数と一覧表のエントリ数が一致しなければ漏れあり
- 検証コマンドと件数を 05_log.md に記録
- 部分列挙が意図なら「一部抜粋（全 N 件中）」と明記

### 6. 状態変更の内部表現特定

「無効化」「失効」「解約」等の状態変更語を 01 に書くときは、以下を特定済みであること:

- 記録先のフィールド / enum 値（例: `kycStatus = "reapplication"`）
- 流用できる既存関数（例: `invalidateKycStatus` / `reissueMkp`）の有無。あれば関数名を 01 に明記
- 外部システム操作なら先方の正式 API 名（例: `AM01AE14-解約登録API`）

### 7. 新アクターの挙動は類似既存アクターとの対応表

新アクター（例: 降格者）の応答パターンは、類似既存アクター（例: 退会者）の現状動作を実コードで確認し、対応表（エントリ / 退会者の現状 / 新アクターの対応）として 01 に書く。既存実装のガード漏れに見える箇所を「バグ」と独断評価せず AskUserQuestion。

---

## 設計判断の記録基準

AskUserQuestion で確定した設計判断は必ず記録する。

### 30_decisions.md に書く

- 採用案
- 不採用案（複数なら複数）
- 各案の pros / cons
- 採用理由
- 関連する既存パターン（`path:Lnum` 引用）

### 99_history.md に書く

- 確定までの経緯（Slack / Confluence コメント等のソース）
- 確定日時
- 確定者（ユーザー / 他チーム）

両ファイルが既存ならそのまま追記、なければ新規作成（30 か 99 のどちらかでよい）。

---

## ライティング（`/ukwhatn-writing` 準拠）

### 常体・簡潔・端的・宣言形

| ✗ | ✓ |
|---|---|
| 〜することが可能 | 〜できる |
| 〜が実施される | 〜する |
| 〜に対応する | 〜する |
| 〜を活用する | 〜を使う |
| 〜することにより、〜になる | 〜なら〜になる |
| なお、〜である | 〜である |
| 必要に応じて〜する | 〜の場合は〜する（条件を具体化） |

### 専門用語

- 原語で書く（「OAuth」「Hydra」「webhook」等）
- コード識別子は `` `code` `` 表記（`isInstant`、`POST /api/v1/foo`）
- 一般語は日本語で（「ユーザー」「アカウント」「画面」）

### 自明な前置きを削る

| ✗ | ✓ |
|---|---|
| まず最初に、ユーザーがログインすると | ユーザーがログインすると |
| 重要なポイントとして、〜 | 〜 |
| 上記の通り、〜である | （削除） |

### AI 翻訳調の例

| ✗ | ✓ |
|---|---|
| このシステムにおいては | この機能では |
| 実装することが推奨される | 実装する / 推奨する |
| 〜という形になる | 〜になる |
| 〜となっている | 〜である |
| 〜を行う / 〜の実施 | 〜する |

---

## 完了基準

以下すべてを満たして完了:

- [ ] Phase 1 で AskUserQuestion による要求深掘りを実施し、05_log.md に記録した
- [ ] Phase 2 でコードベース SSoT 調査を実施し、05_log.md または 20_implementation_notes.md に記録した
- [ ] 01_requirements_skeleton.md に禁止フレーズが残存していない（grep 0 件）
- [ ] 02_system_requirements.md に禁止フレーズが残存していない（grep 0 件）
- [ ] 02 に How（クラス名・関数名・パス・行番号・queue key）が混入していない（grep 0 件）
- [ ] 一覧表（Cloud Task / Scheduler / Webhook / API）を SSoT 全件 grep で網羅確認し、件数を 05_log.md に記録した
- [ ] 識別子はシステム上の正式名称で書いた（独自通称・意訳なし、外部 API は正式 API 名）
- [ ] 状態変更は内部表現（フィールド / enum 値 / 流用する既存関数名）まで特定した
- [ ] 新アクターの挙動は類似既存アクターの現状動作との対応表で説明した
- [ ] 設計判断を 30_decisions.md または 99_history.md に記録した
- [ ] agent review で Action Required = 0 を達成した（同一指摘 2R 連続 or 5R 安全上限で打ち切った場合は残課題を 05_log.md に記録）
- [ ] ライティングが `/ukwhatn-writing` に準拠している
- [ ] 完了報告にファイルパス・主要判断・残課題が含まれる
- [ ] 残課題は「要調査」と書かず、具体的な次アクションとして書く
