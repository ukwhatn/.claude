# Quality Checklist

## 目次

- 禁止フレーズ（01 / 02共通）
- 02へのHow混入チェック
- コードベースSSoT整合性チェック
- 設計判断の記録基準
- ライティング（`/ukwhatn-writing` 準拠）
- 完了基準

`design-feature` スキルの品質基準・チェックリスト・禁止フレーズ。

---

## 禁止フレーズ（01 / 02共通）

以下は01 / 02のいずれにも書かない。書く前にPhase 2で情報を揃えるか、AskUserQuestionで確定する。

| 禁止フレーズ | 代替アクション |
|------------|-------------|
| 要調査 | Phase 2で実コード確認 / context7 / WebSearch |
| TBD / TODO | AskUserQuestionで確定 |
| 要確認 / 要相談 | AskUserQuestionで確定 |
| 要検討 | 代替案を出して採否を判断、または「やらないこと」に移す |
| 追って確認 | 確認してから書く（書く前提を満たさない箇所は書かない） |
| 別途決定 | Phase 2 / AskUserQuestionで確定するか、「やらないこと」に移す |
| 場合によっては | 条件を具体化（「○○の場合」と書く） |
| 必要に応じて | 必要な条件を具体化、または削除 |
| （推定） / おそらく / と思われる | 原典（実コード / 公式仕様）で確定してから書く。確定できないならAskUserQuestion |

### 例外（許容ケース）

- 「やらないこと」セクション内で**スコープ外と明示した上で**「将来必要になれば検討」を示す場合は許容。ただし「要検討」とは書かず、具体的に「<トリガー条件> が発生した時点で再検討」と書く
- 既知バグ修正の説明で「Phase 1で問題化しなかった理由」のように**事実説明**として「検討」「確認」を使うのは可

### 一括チェック

```bash
grep -nE '要調査|TBD|TODO|要確認|要検討|追って確認|別途決定|要相談|場合によっては|必要に応じて|（推定）|推定）|おそらく|と思われる' \
  ${MEMORY_DIR}/memory/<dir>/{01_requirements_skeleton,02_system_requirements}.md
```

---

## 02へのHow混入チェック

02はWhatのみ。以下が混入していないか確認:

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

### 02で許容される技術的識別子

- APIレスポンスのフィールド名（例: `isEnabled`、`account_type`）
- scope / claim名（例: `<feature>_allowed`、`account_type=<value>`）
- エラーコード（例: `<FEATURE>_NOT_ALLOWED`）
- 画面URLのパス例（例: `/instant/register`）
- 仕様上必要なテーブル名（最小限。極力削る）

---

## コードベースSSoT整合性チェック

01を書いた後、agent reviewに渡す前に以下を確認:

### 1. 引用した既存コードの正確性

01で `path:Lnum` 引用したコードが実コードと一致しているか:

```bash
# 引用箇所をリストアップ
grep -nE '`[^`]+\.ts:?L?[0-9]+`?' 01_requirements_skeleton.md

# 各引用先を Read で確認（行数が大きく変わっていれば 01 を更新）
```

### 2. メソッド名のアクセス修飾子

privateメソッド名を01に直書きしていないか確認:

- 既存実装で **public method** がある場合はpublic名を使う
- private名を書いてはいけない（agent reviewでも指摘される）

### 3. 「現状無いから差異」誤判定の予防

01で「Phase Xで追加する」と書いた箇所は、実コードに **無いのが正しい**。agent reviewでこれを「差異あり」と誤判定されないよう、表現を「Phase Xで新規追加する」「現状未実装 → 追加する」と明示する。

### 4. 呼び出し元のガード見落とし予防

ある関数がフラグ有効時に動作するかを判定するとき、関数内部のチェックだけでなく**呼び出し元のガード**も見る:

- 呼び出し元にフラグの早期returnガードがあれば、呼ばれる側にチェックが無くても実際には全スキップされている
- このパターンはagentでも見落としやすい。01 / 02のレビュー時に再確認

### 5. 一覧表の網羅性検証

Cloud Task / Scheduler / Webhook / API等の一覧表は、SSoTファイル全件grepの結果と突合する:

```bash
# 例: Cloud Scheduler の全 procedure を抽出（一覧表の行数と一致するか確認）
grep -cE 'cloudOidcTokenProcedure' src/server/routers/scheduler.ts
grep -nE 'path:\s+"/scheduler/' src/server/routers/scheduler.ts

# 例: Cloud Task の全 queue を抽出
grep -nE '^\s+"[a-z-]+":' src/server/domain/cloud_task.ts
```

- grep件数と一覧表のエントリ数が一致しなければ漏れあり
- 検証コマンドと件数を05_log.mdに記録
- 部分列挙が意図なら「一部抜粋（全N件中）」と明記

### 6. 状態変更の内部表現特定

「無効化」「失効」「解約」等の状態変更語を01に書くときは、以下を特定済みであること:

- 記録先のフィールド / enum値（例: `kycStatus = "reapplication"`）
- 流用できる既存関数（例: `invalidateKycStatus` / `reissueMkp`）の有無。あれば関数名を01に明記
- 外部システム操作なら先方の正式API名（例: `AM01AE14-解約登録API`）

### 7. 新アクターの挙動は類似既存アクターとの対応表

新アクター（例: 降格者）の応答パターンは、類似既存アクター（例: 退会者）の現状動作を実コードで確認し、対応表（エントリ / 退会者の現状 / 新アクターの対応）として01に書く。既存実装のガード漏れに見える箇所を「バグ」と独断評価せずAskUserQuestion。

---

## 設計判断の記録基準

AskUserQuestionで確定した設計判断は必ず記録する。

### 30_decisions.mdに書く

- 採用案
- 不採用案（複数なら複数）
- 各案のpros / cons
- 採用理由
- 関連する既存パターン（`path:Lnum` 引用）

### 99_history.mdに書く

- 確定までの経緯（チャット / ドキュメントのコメント等のソース）
- 確定日時
- 確定者（ユーザー / 他チーム）

両ファイルが既存ならそのまま追記、なければ新規作成（30か99のどちらかでよい）。

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
- コード識別子は `` `code` `` 表記（`isEnabled`、`POST /api/v1/foo`）
- 一般語は日本語で（「ユーザー」「アカウント」「画面」）

### 自明な前置きを削る

| ✗ | ✓ |
|---|---|
| まず最初に、ユーザーがログインすると | ユーザーがログインすると |
| 重要なポイントとして、〜 | 〜 |
| 上記の通り、〜である | （削除） |

### AI翻訳調の例

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

- [ ] Phase 1でAskUserQuestionによる要求深掘りを実施し、05_log.mdに記録した
- [ ] Phase 2でコードベースSSoT調査を実施し、05_log.mdまたは20_implementation_notes.mdに記録した
- [ ] 01_requirements_skeleton.mdに禁止フレーズが残存していない（grep 0件）
- [ ] 02_system_requirements.mdに禁止フレーズが残存していない（grep 0件）
- [ ] 02にHow（クラス名・関数名・パス・行番号・queue key）が混入していない（grep 0件）
- [ ] 一覧表（Cloud Task / Scheduler / Webhook / API）をSSoT全件grepで網羅確認し、件数を05_log.mdに記録した
- [ ] 識別子はシステム上の正式名称で書いた（独自通称・意訳なし、外部APIは正式API名）
- [ ] 状態変更は内部表現（フィールド / enum値 / 流用する既存関数名）まで特定した
- [ ] 新アクターの挙動は類似既存アクターの現状動作との対応表で説明した
- [ ] 設計判断を30_decisions.mdまたは99_history.mdに記録した
- [ ] agent reviewでAction Required = 0を達成した（打ち切り条件は @context/agent-cli-guide.md「レビューループ」。打ち切った場合は残課題を05_log.mdに記録）
- [ ] ライティングが `/ukwhatn-writing` に準拠している
- [ ] 完了報告にファイルパス・主要判断・残課題が含まれる
- [ ] 残課題は「要調査」と書かず、具体的な次アクションとして書く
