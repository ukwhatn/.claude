---
name: design-feature
description: 抽象的な要件・Biz 要求から要求を深掘りし、コードベース SSoT で既存実装整合性を確認した上で「実装マスタ（01_requirements_skeleton.md）」と「システム要件書（02_system_requirements.md）」を作成する。使用タイミング (1)「○○って機能を作りたい」「このBiz要求を満たす機能を設計して」等の抽象要件提示時、(2) 既存機能の拡張・Phase 分割等の要件定義開始時、(3) `/design-feature ...` 実行時。
---

# Design Feature

抽象的な要求から、実装可能な粒度の「実装マスタ（01）」と、Biz/PdM/RP 向けの「システム要件書（02）」をペアで作るワークフロー。`large-task` 実装フェーズの上流にあたる設計工程を担う。

## 出力物

| ファイル | 内容 | 読み手 |
|---------|------|-------|
| `01_requirements_skeleton.md` | 実装マスタ。What + How。DB スキーマ / API / Usecase / ガード / 影響範囲 / 設計理由 | 実装担当 |
| `02_system_requirements.md` | システム要件書。What のみ。Why は注記程度 | Biz / PdM / RP / CS |

両者は同一プロジェクトの **2 つの顔**。01 を SSoT として 02 を抽出する関係。

## 既存設定との関係

- **Phase 0-5（@context/workflow-rules.md）**: 本スキルは Phase 0-2（準備・調査・計画）を担う。Phase 3 以降の実装は `/large-task` 等に引き継ぐ
- **メモリディレクトリ（@context/memory-file-formats.md）**: 既定保存先は `${MEMORY_DIR}/memory/YYMMDD_<context_name>/`
- **agent review（@context/agent-cli-guide.md）**: 01 確定前の必須プロセス
- **ライティング（`/ukwhatn-writing`）**: 文体・語彙ルールを全章で遵守
- **`/large-task`（既存スキル）**: 本スキルが上流（設計）、`large-task` が下流（実装分割）。明確に分担

## ワークフロー（Phase 0-5）

```
Phase 0: 準備           → メモリディレクトリ・タスク管理
Phase 1: 要求深掘り     → AskUserQuestion で目的・スコープ・制約を確定
Phase 2: 既存実装調査   → コードベース SSoT で関連実装を把握
Phase 3: 01 ドラフト     → 実装マスタを章別に書く
Phase 4: agent review   → cursor agent で Action Required 0 まで反映
Phase 5: 02 抽出         → 01 から What だけ抽出して書き、完了報告
```

各 Phase の具体手順: @references/workflow-detail.md

## 厳守ルール（CRITICAL）

### 1. コードベース SSoT
- 既存実装に関する SSoT は**コードベース**。メモリディレクトリ内資料は outdated 可能性あり
- ドキュメントに事実を書く前に必ず実コードで裏取り
- Explore agent の判断もそのまま信用せず、重要箇所は私が Read で再確認
- 公式仕様は context7 / WebSearch で確認

### 2. 禁止フレーズ
以下を 01 / 02 のいずれにも書かない:

要調査 / TBD / TODO / 要確認 / 要検討 / 追って確認 / 別途決定 / 要相談 / 場合によっては / 必要に応じて

→ 書きたくなったら **Phase 2 で情報を揃える** か **AskUserQuestion で確定** する。チェックリスト: @references/quality-checklist.md

### 3. 設計判断は AskUserQuestion
- 複数案で迷う、スケジュール・金額・対外コミュニケーションが絡む、既存パターンから外れる、スコープ縮小判断 — いずれも勝手に決めない
- 採用案 + 不採用案 + 理由をセットで `30_decisions.md` または `99_history.md` に記録

### 4. ライティング（`/ukwhatn-writing`）
- 常体・簡潔・端的・宣言形
- AI 翻訳調禁止（「〜することが可能」→「〜できる」、「実施する/対応する」の乱用回避）
- 専門用語は原語 + `` `code` `` 表記
- 推測はぼかし、断定は事実のみ
- 自明な前置きを削る

### 5. 既存パターン踏襲
- プロジェクトの既存規約・命名・レイヤー構成から自己判断で逸脱しない
- 逸脱が必要なら必ず AskUserQuestion

### 6. 識別子・用語は正式名称
- システム上の識別子（Cloud Task キュー名 / Scheduler ジョブ名 / enum 値 / procedure 名）は実装から抽出した正式名称で書く。独自の通称・意訳を作らない
- 外部システムの操作は先方の正式 API 名で表現（例: 「カード失効」ではなく「解約（`AM01AE14-解約登録API`）」）
- データ項目は既存スキーマのフィールドと対応させる。スキーマに無い概念語（「表示名」等）を導入しない

### 7. 一覧は SSoT 全件 grep で網羅
- Cloud Task / Scheduler / Webhook / API 等の一覧表は、定義箇所（routers / domain 等の SSoT ファイル）を全件 grep してから作る
- 部分列挙なら「一部抜粋」と明記。grep 検証コマンドと件数を 05_log.md に記録

### 8. 可能な限り既存実装を踏襲できるよう網羅的に調査
- 新アクター（例: 降格者）の挙動は、類似既存アクター（例: 退会者）の現状動作を実コードで網羅的に調査し、追従させるのが原則。対応表を 01 に書く
- 既存実装のガード漏れ・不統一に見えるものを「バグ」「統一修正対象」と独断評価しない。意図的設計の可能性を AskUserQuestion で確認
- 既存挙動の変更・広範囲リファクタをスコープに含めない。必要性を感じたら「後続フェーズ」として分離提示

### 9. 状態変更は内部表現まで特定
- 「無効化」「失効」等の状態変更は、どのフィールド・enum 値で記録するかまで 01 で特定（例: `kycStatus = "reapplication"`）
- 既存関数を流用できるかをまず確認し、流用できる場合は 01 に関数名を明記（例: `invalidateKycStatus` / `reissueMkp` 流用）。02 では「既存処理を流用」程度に言及

## Phase 別の要点

### Phase 0: 準備

1. `MEMORY_DIR` 確認（未定義なら `.local/`）
2. 既存メモリディレクトリ検索 → 同コンテキストなら再利用、新規なら `${MEMORY_DIR}/memory/YYMMDD_<context_name>/` 作成
3. `05_log.md` を初期化 / 追記、ユーザー指示を逐語記録
4. 関連する過去タスク・issue を `findmem` 相当で探索（@context/workflow-rules.md §1.0）
5. TaskCreate で本ワークフローのタスクを構造化
6. **絶対パス固定**: 元 repo のメモリディレクトリ絶対パスを 05_log.md 冒頭に記録（worktree 運用時の事故防止）

### Phase 1: 要求深掘り

AskUserQuestion で以下を **必ず確定** してから次に進む:

1. **目的・解決したい問題**: なぜ作るのか
2. **対象ユーザー / アクター**: 誰が使うか、誰が影響を受けるか（社内 / RP / エンドユーザー）
3. **スコープの境界**: やる / やらない を明示。「全件」「全 RP」等は文字通り全件
4. **既存機能との関係**: 新規 / 拡張 / 置換 / 共存
5. **制約**: スケジュール、依存サービス、法的制約、運用制約
6. **成果物の保存先**: デフォルトは `${MEMORY_DIR}/memory/YYMMDD_<context_name>/`、指定があれば従う
7. **Phase 1 既知バグの取り込み有無**: 機能追加と同時に既知バグを修正するか

質問の粒度・テンプレート: @references/workflow-detail.md §「Phase 1 質問テンプレート」

### Phase 2: 既存実装調査（SSoT 確認）

調査観点:
- 対象機能に関連する既存コードの場所・パターン
- データモデル（DB スキーマ、Domain 型）
- 既存 API / Usecase / Service / Repository / Adapter
- 既存ガード・エラーパターン
- 命名規約・テンプレート・規約同意・通知メールの既存実装
- Cloud Task / Scheduler / Webhook の関連エンドポイント
- 影響範囲（同類画面・同類 procedure）

調査手段:
- **Explore agent を並列 3-5 で起動**してファイル/関数のリストアップ
- **重要箇所は私が Read で直接確認**（agent の判定をそのまま信じない）
- context7 / WebSearch で公式仕様確認（必須）
- 発見は `05_log.md` に逐次記録

並列調査パターン: @references/workflow-detail.md §「Phase 2 並列調査パターン」

### Phase 3: 01 ドラフト作成

実装可能な粒度で What + How を書く。

#### 必須章（プロジェクト次第で調整可、これは DAS 風の例）

1. 概要（メタ情報表 + 親エピック + 参照文書）
2. 状態遷移 / データフロー（あれば）
3. 新機能詳細（usecase / API / 入出力 / 同期処理・afterCommitAction）
4. 既存機能への影響（変更・修正・ガード追加）
5. 外部システム連携（呼び出す API、Webhook、Cloud Task）
6. DB / マイグレーション（新規テーブル・既存変更・enum 追加箇所）
7. エラーハンドリング・ガード一覧
8. やらないこと（スコープ外、理由付き）
9. リリース前チェック項目（外部依存）
10. リリーススケジュール（参考）
11. 更新履歴

詳細テンプレート: @references/doc-templates.md §「01 実装マスタ」

#### Ultracode mode 時の並列化

Workflow で章別並列ドラフト → 統合。並列パターン: @references/workflow-detail.md §「Ultracode 並列化」

### Phase 4: agent review ループ

@context/agent-cli-guide.md に従う:

1. 初回: cursor agent CLI（fallback: codex）で 01 をレビュー
2. Severity 別判断:
   - Action Required → 必ず修正
   - Recommended → 必要性で判断、スキップ時は理由を 05_log.md に記録
   - Minor → スタイル差は許容
3. `--resume <session_id>` で 2 回目以降継続
4. 打ち切り条件:
   - Action Required = 0
   - 同一指摘 2R 連続
   - 安全上限 5R

実コードでの裏取り: agent の指摘も鵜呑みにせず、修正前に Read で事実確認。`Phase 2 で追加する内容を「現状無いから差異」と誤判定する`パターンに注意。

### Phase 5: 02 抽出 + 完了報告

#### 02 抽出ルール

01 から **What のみ** を抽出して `02_system_requirements.md` を書く。

| 書く | 書かない |
|------|---------|
| 機能の存在・挙動・入出力 | クラス名・関数名・ファイルパス・行番号 |
| 状態遷移・分岐条件 | Usecase / Service / Repository / Adapter の構造 |
| API レスポンス・scope / claim 名 | DB のテーブル名・カラム名（最小限可、ただし極力避ける） |
| 画面遷移の概要 | Procedure / queue key / DI 構造 |
| エラーコード（仕様レベル） | エラーメッセージキー・ステータスマッピング詳細 |
| Why は注記程度（1-2 行、「※」「→」） | Why の詳細な設計理由 |

形式: Phase 1 Confluence スタイル相当（章番号 + 箇条書き多用 + サブセクション X.Y / X.Y.Z + 表は最小限）。テンプレ: @references/doc-templates.md §「02 システム要件書」

#### 完了報告

1. 作成ファイルのフルパス
2. 主要設計判断のサマリ
3. agent review ループの結果（Round 数・Action Required 件数）
4. 残課題（あれば。ただし「要調査」は禁止 — 残課題は具体的に書く）

## 既存スキルとの違い

| スキル | 役割 | 本スキルとの関係 |
|--------|------|---|
| `/large-task` | 大規模タスクの実装分割（Phase 3-5） | 本スキルが上流（設計）、`/large-task` が下流（実装） |
| `/codebase-review` | 既存コードの 6 観点並列レビュー | Phase 2 で部分的に活用可。本スキルは新機能設計が主目的 |
| `/doc-review` | 既存ドキュメントのレビュー | 本スキルは新規作成。レビューは agent review CLI で代替 |
| `/ukwhatn-writing` | 文体スキル | 本スキルはこれを内部で遵守 |
| `/project-init` | プロジェクト初期化 | プロジェクト立ち上げ時。本スキルは機能単位 |

## 詳細参照

- @references/workflow-detail.md — Phase 別の具体手順、質問テンプレ、並列化パターン
- @references/doc-templates.md — 01 / 02 のテンプレート構造とサンプル
- @references/quality-checklist.md — 禁止フレーズ・整合性チェック・完了基準

## チェックリスト（完了前に確認）

- [ ] Phase 1 で目的・スコープ・制約・既存機能との関係を AskUserQuestion で確定したか
- [ ] Phase 2 でコードベース SSoT による調査結果を 05_log.md に記録したか
- [ ] 01 / 02 に禁止フレーズが残存していないか（`grep -nE '要調査|TBD|TODO|要確認|要検討|追って確認|別途決定|要相談|場合によっては|必要に応じて|（推定）|推定）|おそらく|と思われる'`）
- [ ] 一覧表（Cloud Task / Scheduler / Webhook / API）は SSoT ファイル全件 grep で網羅確認し、件数を 05_log.md に記録したか
- [ ] 識別子はシステム上の正式名称で書いたか（独自通称・意訳なし、外部 API は正式 API 名）
- [ ] 状態変更は内部表現（フィールド / enum 値 / 流用する既存関数名）まで 01 で特定したか
- [ ] 新アクターの挙動は類似既存アクターの現状動作との対応表で説明したか
- [ ] 設計判断を AskUserQuestion で確定し、理由を 30_decisions.md / 99_history.md に記録したか
- [ ] agent review で Action Required = 0 を達成したか
- [ ] 02 に How（クラス名・関数名・ファイルパス・行番号・queue key）が混入していないか
- [ ] 文体が `/ukwhatn-writing` に準拠しているか
- [ ] 完了報告にファイルパス・主要判断・残課題が含まれるか
