---
name: doc-review
description: Agent Teamsによる多角的ドキュメントレビュー。設計書・仕様書・計画書等のドキュメントを6 Agent（通常4 + Devil's Advocate + agent CLI）で並列レビュー。使用タイミング: (1) /doc-review 明示実行時、(2) 「チームでレビューして」「多角的にレビューして」等の明示依頼時（Agent Teams発動条件(c)相当）。通常の「レビューして」だけの依頼では発火しない（単独レビューまたはagent CLIで対応し、必要なら本スキルを提案する）。
---

# doc-review - Agent Teams ドキュメントレビュー

Agent Teamsを活用し、6つの独立したAgentが異なる観点からドキュメントをレビューする。
複数のAIインスタンスが独立して分析することで、単一視点では見落としがちな問題を検出する。

## 既存設定との関係

- **Agent Teams（@context/agent-teams-guide.md）**: TeamCreate/SendMessage/TeamDeleteで構成
- **agent CLI（@context/agent-cli-guide.md）**: 外部CLI（cursor agent / codex）による第三者レビュー
- **Phase 0-5（@context/workflow-rules.md）**: Phase 2（計画レビュー）やPhase 4（品質確認）で使用可能
- **codebase-reviewスキル**: コードベース対象（本スキルはドキュメント対象で競合しない）

## 引数

```
/doc-review <ファイルパス>                          # 初回レビュー
/doc-review <ファイルパス> --ref <参照ファイル>      # 参照ドキュメント付き
/doc-review <ファイルパス> --prev <前回80_review.md> # 継続レビュー（前回結果を引き継ぎ）
```

- 参照ファイル（--ref）: レビュー対象が基づいている要件書・仕様書等。整合性チェックに使用。
- 前回レビュー（--prev）: 前回の80_review.mdを指定。前回指摘のフォローアップ・修正副作用チェック・影響範囲の網羅性チェックが追加される。

## ワークフロー

### Step 1: レビュー対象の確認

1. 対象ファイルを読み込む
2. 参照ファイルがあれば読み込む
3. ドキュメントの種類を判定（設計書/仕様書/計画書/提案書/その他）
4. **--prev指定時: 前回レビュー結果を読み込み、Step 1.5を実行**

### Step 1.5: 前回レビューの分析（--prev指定時のみ）

前回レビュー結果を分析し、以下を準備する:

1. **前回AR修正の確認リスト**: 前回のAction Required全件が設計書で修正されているか確認
2. **未対応R/Mリスト**: 前回のRecommended/Minor指摘のうち、設計書に反映されていないものを抽出
3. **修正箇所リスト**: 前回指摘に対して修正された箇所を特定（Step 4の追加指示に使用）

この情報は全Agentへの共通指示に含める。

### Step 2: レビュー観点の決定

ドキュメントの種類に応じて、通常Agent 4つのレビュー観点を動的に決定する。

**設計書の場合:**
| Agent | 観点 |
|-------|------|
| reviewer-1 | アーキテクチャ（構造、パターン、拡張性） |
| reviewer-2 | セキュリティ（認証・認可、データ保護、不正利用） |
| reviewer-3 | 整合性（要件カバレッジ、矛盾検出、Phase分割） |
| reviewer-4 | 実装可能性（技術リスク、影響範囲、テスト戦略） |

**仕様書/要件書の場合:**
| Agent | 観点 |
|-------|------|
| reviewer-1 | 完全性（要件の漏れ、曖昧な表現、未定義項目） |
| reviewer-2 | 実現可能性（技術的制約、コスト、スケジュール） |
| reviewer-3 | ユーザビリティ（UX、エッジケース、エラーハンドリング） |
| reviewer-4 | ビジネス整合性（目的との一致、ROI、リスク） |

**計画書/提案書の場合:**
| Agent | 観点 |
|-------|------|
| reviewer-1 | 実現可能性（技術的実現性、リソース、依存関係） |
| reviewer-2 | リスク分析（想定リスク、軽減策、代替案） |
| reviewer-3 | スケジュール・スコープ（粒度、依存関係、マイルストーン） |
| reviewer-4 | 品質・テスト戦略（検証方法、受け入れ基準、KPI） |

**共通（全ドキュメント種別）:**
| Agent | 観点 |
|-------|------|
| devils-advocate | 根本的な前提への挑戦、見落とされたリスク、代替案 |
| agent-cli-reviewer | 外部CLI（cursor agent / codex）による第三者レビュー |

### Step 3: チーム作成

```
TeamCreate(team_name: "doc-review-<YYMMDD>", description: "ドキュメントレビュー: <対象ファイル名>")
TaskCreate × 6（各Agentのタスク）
```

### Step 4: 共通指示テンプレート

全Agentに以下の共通コンテキストを渡す:

```
## レビュー対象
<対象ファイルのパス>

## 参照ドキュメント（ある場合）
<参照ファイルのパス>

## 未実装設計の扱い（重要: 設計と現状コードの差分を指摘対象にしない）
対象が設計書・計画書の場合、以下を明示する:
「この設計/計画はこれから実装する新機能であり、まだコードベースには存在しない。
『現在の実装との差分』は実装対象であり、指摘対象ではない。
レビューの観点は『設計の妥当性・完全性・一貫性』である。」

## 指摘の分類
- **Action Required**: 重大な問題（マージ不可レベル）
- **Recommended**: 改善推奨だが動作に直接影響しない
- **Minor**: 軽微な指摘

## 影響範囲の網羅性チェック（全Agentに適用）

問題を発見した場合、**その箇所だけでなく、同種のパターンが存在する全箇所**を調査すること（1箇所の修正では同種の問題が残存し、レビューの網羅性が損なわれるため）。

具体的な手順:
1. 問題を検出する
2. その問題の「パターン」を抽出する（例: 「nullableフィールドをdecryptに渡している」）
3. コードベース全体をGrepで検索し、同じパターンが存在する全箇所を列挙する
4. 指摘には「検出箇所」と「同種パターンの全箇所」を両方記載する

例:
- NG: 「profile2User()でdecrypt(null)クラッシュの可能性がある」
- OK: 「profile2User()でdecrypt(null)クラッシュの可能性がある。同種のパターンが以下にも存在: toSearchUsersResult()(user.ts:538), toSearchUsersResultForConsole()(user.ts:603), findUserByIdForConsole()(user.ts:926)」

## 修正の副作用チェック（全Agentに適用）

設計書内のコード例や処理フローが変更されている箇所を見つけた場合、以下を確認すること（変更が不変条件や呼び出し元を壊す副作用を見逃さないため）:

1. **その変更が既存の不変条件を壊さないか** - 例: セキュリティチェックの順序変更、エラーハンドリングの追加位置
2. **その変更が呼び出し元に型エラーや動作変更を引き起こさないか** - 例: 引数追加、戻り値型変更、optional化
3. **その変更が既存テストや外部API契約に影響しないか** - 例: レスポンス形式の変更、フィールドの追加/削除

## 出力形式
leadにSendMessageで以下を報告:
1. 各観点ごとの分析結果
2. 指摘リスト（Severity分類付き）
3. 総合評価
```

### Step 4.5: 継続レビュー用の追加指示（--prev指定時のみ）

共通指示テンプレートに以下を**追加**する:

```
## 前回レビューからの継続チェック

### 前回AR修正の確認
以下の前回Action Requiredが適切に修正されているか確認してください:
<前回ARのリスト（Step 1.5で準備）>

確認観点:
- 修正が指摘の意図を正しく反映しているか
- 修正が新たな問題を生んでいないか（副作用）
- 修正が「その箇所だけ」に留まっていないか（同種の問題が他に残存していないか）

### 前回未対応R/Mの確認
以下の前回Recommended/Minor指摘が未対応です。改めて確認し、
対応されている場合はスキップ、未対応のまま放置すると問題が深刻化する場合はSeverityを再評価してください:
<未対応R/Mリスト（Step 1.5で準備）>

特に以下の場合はARに昇格してください:
- 2ラウンド連続でR以上で指摘されたが未対応の場合
- 放置することでランタイムクラッシュ、型エラー、セキュリティ問題に直結する場合

### 修正箇所の副作用チェック
前回指摘への対応として以下の箇所が修正されています:
<修正箇所リスト（Step 1.5で準備）>

各修正箇所について:
1. 修正によって新たな整合性問題が生じていないか
2. 修正によって既存の呼び出し元に影響がないか
3. 修正位置が処理フロー上適切か（例: セキュリティチェックの順序）
```

### Step 5: Agent spawn（並列）

全6 Agentを並列でspawnする。モデルは指定しない（セッションのモデルを継承）。

```
Task(subagent_type: "code-reviewer", team_name: ..., name: "reviewer-1", prompt: ...)
Task(subagent_type: "code-reviewer", team_name: ..., name: "reviewer-2", prompt: ...)
Task(subagent_type: "code-reviewer", team_name: ..., name: "reviewer-3", prompt: ...)
Task(subagent_type: "code-reviewer", team_name: ..., name: "reviewer-4", prompt: ...)
Task(subagent_type: "code-reviewer", team_name: ..., name: "devils-advocate", prompt: ...)
Task(subagent_type: "general-purpose", team_name: ..., name: "agent-cli-reviewer", prompt: ...)
```

**agent-cli-reviewerの特別指示:**

外部CLIをBash経由で実行し、第三者レビューをleadに報告する。CLI判定（cursor優先／codex fallback）・コマンド形式・セッション継続は @context/agent-cli-guide.md「使用するCLIの選択」「基本コマンド」に従う。
- プロンプトにはレビュー対象のファイルパスのみを渡す（ファイル内容の埋め込みは禁止。CLIに自分で読ませるため）
- 外部CLIのモデルはagent-cli-guide準拠の固定値（Agent spawn時の「モデル指定なし」とは別系統）

### Step 6: 結果収集・統合

全Agentの結果をSendMessageで受信後:

1. 指摘をSeverity別に集約
2. 複数Agentが独立検出した指摘を特定（重複排除 + 検出数記録）
3. **Lead検証**: ARレベルの指摘について、leadがコードベースを確認して妥当性を検証
4. **Severity調整**: Lead判断に基づいてSeverityの昇格/格下げを実施（理由を明記）
5. 統合レポートを作成

### Step 7: 統合レポート出力

統合レポートをメモリディレクトリの `80_review.md` に保存する。出力形式は [references/output-formats.md](references/output-formats.md) の「統合レポート」節をReadして使う。

- 初回: レビュー結果サマリー表 + Action Required / Recommended / Minor の各指摘
- 継続（--prev指定時）: 上記の冒頭に「前回レビューからのフォローアップ」（前回AR修正状況・R/M再評価・AR推移）を追加

### Step 7.5: レビュートラッキングファイルの更新

初回・継続を問わず全ラウンドで実行する（ラウンドを跨いだ指摘の再燃・解決を追跡するため、初回でも起点として作成する）。対象ドキュメントのメモリディレクトリに `81_review_tracking.md` を作成/更新する。形式と更新ルールは [references/output-formats.md](references/output-formats.md) の「レビュートラッキング」節を参照。

次回の `--prev` では 80_review.md に加えてこの 81_review_tracking.md も読み込み、トラッキング情報を引き継ぐこと（引き継がないと再燃検出が機能しないため）。

### Step 8: クリーンアップ

全Agentにshutdown_request → TeamDelete

### Step 9: 収束判定（継続レビューの場合）

AR修正後、収束状況をユーザーに報告する。報告形式（収束状況テーブルと収束条件チェックリスト）は [references/output-formats.md](references/output-formats.md) の「収束状況の報告」節を参照。

## Devils' Advocate Agent 指示テンプレート

通常のレビューアーとは異なり、以下の挑戦的な問いかけを行う:

1. **根本的な前提への挑戦** - 「本当に最善か？」「将来破綻しないか？」
2. **見落とされたリスクシナリオ** - 最悪のケースを想定
3. **代替案の提示** - 「もっとシンプルな方法はないか？」
4. **Phase分割のリスク** - 中途半端な状態が本番に出ないか
5. **修正の連鎖リスク** - 「この修正が別の問題を引き起こさないか？」（継続レビュー時に特に重視）

ただし指摘は correctness / security / data integrity / 明示要件に影響するgapに限定する（健全な設計へのgap捏造・over-engineering指摘を抑制するため）。

## 注意事項

- 全Agentの完了を待つ際、sleepやポーリングループは使用禁止（ターンを終了して待機）
- agent CLIの`--output-format stream-json`は使用禁止（ハングリスク）
- agent CLIプロンプトに`$(cat ...)` / `$(git diff ...)`でファイル内容を埋め込むことは禁止
- レビュー対象が未実装の設計の場合、「現在の実装との差分」を指摘対象として認識しないよう明示すること
- モデルは特に指定がない限りセッションのモデルを継承（spawn時に明示指定しない）
- 影響範囲の網羅性チェックと修正副作用チェックはStep 4の共通指示に含まれるため、--prev有無にかかわらず常に実行される（--prev指定時のStep 4.5追加指示とは独立）
