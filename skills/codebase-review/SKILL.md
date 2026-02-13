---
name: codebase-review
description: コードベース包括的レビュー。6観点（perf/sec/test/arch/cq/docs）を並列サブエージェントで実行し、優先度付きissueファイルをメモリディレクトリに生成。
---

# コードベース包括的レビュー

## 概要

コードベース全体を6つの観点から並列でレビューし、発見した問題点を優先度付きのissueファイルとして記録する。

## トリガー条件

- ユーザーが `/codebase-review` を実行した場合
- コードベース全体のチェック・監査を依頼された場合
- リリース前の品質確認を依頼された場合

## レビュー観点

| 観点 | 略語 | 説明 |
|------|------|------|
| Performance | perf | N+1、不要な再レンダリング、重い処理等 |
| Security | sec | 脆弱性、認証・認可、入力検証等 |
| Test | test | テストカバレッジ、テストケース不足 |
| Architecture | arch | 責務分割、依存関係、設計パターン |
| Code Quality | cq | 命名、一貫性、可読性、不要コード |
| Documentation | docs | ドキュメント不足、内容の陳腐化 |

## 優先度定義

| 優先度 | 略称 | 説明 | 対応期限 |
|--------|------|------|---------|
| critical | crit | 即座に対応必須（本番障害、重大脆弱性） | 即時 |
| major | maj | 早期対応推奨（バグ、セキュリティリスク） | 次リリースまで |
| minor | min | 改善推奨（設計改善、技術的負債） | 計画的に対応 |
| trivial | triv | 余裕があれば対応（軽微な改善） | 任意 |

※ アルファベット順でソートすると正しい優先度順になる

## 実行手順

### Phase 0: 準備

1. ディレクトリの確認・作成

```bash
# PJ CLAUDE.mdのMEMORY_DIRを確認（未定義なら.local/）
# システムプロンプトのToday's dateから日付を取得（例示をコピーしない）
mkdir -p ${MEMORY_DIR}/memory/YYMMDD_codebase-review
mkdir -p ${MEMORY_DIR}/issues
```

2. 05_log.mdを初期化

3. PJのCLAUDE.mdとcontext/を確認し、アーキテクチャルールを把握

4. **コードベース構造の把握**

```bash
# ディレクトリ構造を取得
find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' | head -100

# 主要ファイルタイプの分布を確認
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.md" \) \
  -not -path '*/node_modules/*' | wc -l
```

### Phase 1: 並列サブエージェント実行

---
**🚨 親エージェント（Claude Code）への警告 🚨**

サブエージェントプロンプト作成時に以下を**絶対に守ること**:

1. `--skip-multimodel` オプションが**明示的に指定されていない限り**、タスク3（agent cliによる並行レビュー）の指示を**削除・省略してはならない**
2. 「時間短縮」「コスト削減」「効率化」を理由にした自己判断でのスキップは**禁止**
3. サブエージェントプロンプトには必ず**タスク1〜4すべて**を含めること

**違反した場合**: レビューは不完全とみなされ、ユーザーに説明責任が発生する

---

**CRITICAL**: 6つのサブエージェントを**同時に**起動する。Taskツールを1つのメッセージで6回呼び出す。

**CRITICAL**: サブエージェントは必ず `subagent_type=general-purpose` を使用すること。
- `Explore`エージェントはファイル探索専用でWriteツールを持たないため、issueファイルを作成できない
- `general-purpose`エージェントは全ツール（Read, Write, Grep, Glob, Bash, WebSearch, context7等）にアクセス可能

各サブエージェントには以下の情報を渡す:
- メモリディレクトリのフルパス
- PJ CLAUDE.mdの内容（アーキテクチャルール等）
- 対象リポジトリのパス
- 担当観点とレビュー基準
- **コードベース構造情報**（Phase 0で取得）

#### サブエージェント共通プロンプトテンプレート

**CRITICAL**: 以下のテンプレート全体をサブエージェントに渡すこと。タスク1〜4はすべて必須。
観点別の詳細指示（後述）は `## あなたの担当観点` セクションに挿入する。

```
あなたは「{観点名}」の専門レビュアーです。

## コンテキスト
- リポジトリ: {リポジトリパス}
- メモリディレクトリ: {メモリディレクトリフルパス}
- PJルール: {CLAUDE.mdの内容}
- コードベース構造: {ディレクトリ構造}

## あなたの担当観点
{観点別の詳細指示}

## タスク

### 1. コードベース全体の網羅的確認（CRITICAL）
以下の手順で**すべてのディレクトリとファイル**を確認すること:

1. まずディレクトリ構造を把握
   ```bash
   find {リポジトリパス} -type d -not -path '*/node_modules/*' -not -path '*/.git/*'
   ```

2. 各ディレクトリ内のファイルを走査
   - apps/, src/, lib/, batch/, misc/ など主要ディレクトリをすべて確認
   - 隠れたサブディレクトリも見落とさない
   - ファイル数が多い場合はGlobで効率的に検索

3. 担当観点に関連するファイルを特定し、すべて読む
   - 「たぶん問題ない」で飛ばさない
   - 類似ファイルも個別に確認

### 2. ベストプラクティスの調査（IMPORTANT）
問題を発見した場合、または問題が疑われる場合:

1. **context7**で関連ライブラリのドキュメントを確認
   - 例: Drizzle ORMのN+1対策、Reactのメモ化ベストプラクティス等
   - resolve-library-id → query-docs の順で実行

2. **WebSearch**で業界標準のベストプラクティスを確認
   - 例: "OWASP timing attack prevention 2025"
   - 例: "React performance optimization best practices 2025"

3. 調査結果をissueファイルの「改善案」「追加情報」に反映

### 3. agent cliによる並行レビュー【必須・スキップ不可】

---
**🚨 このステップは必須です 🚨**

- `--skip-multimodel` オプションが**明示的に指定されていない限り**、以下のコマンドを**必ず実行**すること
- 実行しない場合、レビューは**不完全**とみなされる
- 「問題が少なそう」「時間がない」等の理由でのスキップは**禁止**

---

自分のレビューと並行して、agent cliで同じタスクを実行し、結果を突き合わせる:

1. **agent cliで同じ観点のレビューを実行**

   サブエージェントと同等の情報量でagent cliに指示する:

   ```bash
   agent -p "あなたは「{観点名}」の専門レビュアーです。

   ## コンテキスト
   - リポジトリ: {リポジトリパス}
   - PJルール: {CLAUDE.mdの内容}
   - コードベース構造: {ディレクトリ構造}

   ## あなたの担当観点
   {観点別の詳細指示（レビュー項目一覧）}

   ## 優先度判断基準
   {観点別の優先度基準}

   ## タスク
   1. コードベース全体を網羅的に確認
      - すべてのディレクトリとファイルを走査
      - 担当観点に関連するファイルをすべて読む
      - 「たぶん問題ない」で飛ばさない

   2. 問題を特定し、優先度を付与

   3. 発見した問題をJSON形式で出力:
   {
     \"issues\": [
       {
         \"title\": \"問題のタイトル（日本語）\",
         \"priority\": \"critical|major|minor|trivial\",
         \"files\": [\"ファイルパス:行番号\", ...],
         \"description\": \"問題の詳細説明\",
         \"suggestion\": \"改善案\",
         \"bestPractice\": \"参照したベストプラクティス（あれば）\"
       }
     ],
     \"checkedDirectories\": [\"確認したディレクトリ一覧\"],
     \"summary\": \"レビュー概要\"
   }

   ## 注意事項
   - 問題がない場合は issues: [] で出力
   - 推測ではなく、コードを実際に読んで判断
   - 優先度は厳格に判断（critの乱用禁止）
   - コードベースの一部だけを見て終わりにしない" \
     --model gpt-5.3-codex-high-fast \
     --output-format json | jq -r '.session_id, .result'
   ```

2. **結果を突き合わせ**

   | 状況 | 対応 |
   |------|------|
   | 両者が同じ問題を検出 | 高信頼度として採用 |
   | 自分のみ検出 | 妥当性を再確認、妥当なら採用 |
   | agent cliのみ検出 | 該当コードを確認、妥当なら採用 |
   | 優先度が異なる | 根拠を比較し適切な方を採用 |

3. **マージ結果を記録**
   issueファイルに以下を追記:
   ```markdown
   ## マルチモデル検証
   - Claude Code: 検出
   - agent cli (gpt-5.3-codex-high-fast): 検出/未検出
   - 信頼度: 高/中
   - 優先度差異: なし / あり（Claude Code={X}, agent cli={Y} → 採用: {Z}）
   ```

### 4. 問題の特定と記録
- 各問題に優先度（critical/major/minor/trivial）を付与
- 問題ごとにissueファイルを作成
- ベストプラクティス調査結果を含める
- マルチモデル検証結果を含める

## issueファイル形式
場所: {MEMORY_DIR}/issues/{優先度}-{観点略語}-{日本語タイトル}.md

内容:
```markdown
---
priority: {critical|major|minor|trivial}
category: {観点略語}
type: {bug|improvement|feature}
---

# {タイトル}

## 概要
{問題の簡潔な説明}

## 現状の問題点
{何が問題なのか、どこで発生しているか}
- 対象ファイル: {パス:行番号}
- 対象ファイル: {パス:行番号}

## 改善案
{どう改善すべきか}
- ベストプラクティス: {context7/WebSearchで調査した内容}

## 期待される効果
{改善後のメリット}

## 対象範囲
{影響を受けるファイルや機能}

## 追加情報
- 参考: {調査したドキュメントURL等}
- 関連issue: {あれば}
```

## 注意事項
- 問題がない場合はissueファイルを作成しない
- 推測ではなく、コードを実際に読んで判断する
- 優先度は厳格に判断する（critの乱用禁止）
- **コードベースの一部だけを見て終わりにしない**
- **ベストプラクティス調査は問題発見時に必須**
```

#### 観点別の詳細指示

各観点のレビュー項目・優先度基準の詳細は [references/review-aspects.md](references/review-aspects.md) を参照。
共通テンプレートの `## あなたの担当観点` セクションに、該当観点の内容を挿入すること。

### Phase 2: 結果の集約

サブエージェント完了後:

1. issuesディレクトリのファイルを集計

```bash
ls -la ${MEMORY_DIR}/issues/
```

2. マルチモデル検証の統計を集計（各issueファイルから）

3. サマリーファイルを作成

### Phase 3: サマリー作成

```markdown
# コードベースレビュー サマリー

## 実行日時
YYYY-MM-DD HH:MM

## 統計

| 優先度 | 件数 |
|--------|------|
| critical | X    |
| major    | X    |
| minor    | X    |
| trivial  | X    |
| **合計** | **X** |

| 観点 | crit | maj | min | triv | 計 |
|------|------|-----|-----|------|-----|
| perf | X | X | X | X | X |
| sec  | X | X | X | X | X |
| test | X | X | X | X | X |
| arch | X | X | X | X | X |
| cq   | X | X | X | X | X |
| docs | X | X | X | X | X |

## マルチモデル検証結果
- 両者一致（高信頼度）: X件
- Claude Codeのみ検出: X件
- agent cliのみ検出 → 採用: X件
- 優先度差異あり: X件

## Critical Issues（要即時対応）
...

## Major Issues（要早期対応）
...

## 推奨対応順序
...
```

### Phase 4: ユーザーへの報告

サマリーを提示し、以下を確認:
- 優先度の妥当性
- 対応の優先順位
- GitHub issueへの登録要否

## ファイル構成

```
${MEMORY_DIR}/
├── memory/
│   └── YYMMDD_codebase-review/
│       ├── 05_log.md          # 作業ログ
│       └── summary.md         # レビューサマリー
└── issues/                    # issueファイル（マルチモデル検証済み）
    ├── critical-*.md          # 各issueにマルチモデル検証結果を含む
    ├── major-*.md             # アルファベット順で優先度順にソート
    ├── minor-*.md
    └── trivial-*.md
```

## オプション引数

```
/codebase-review [options]

--scope <path>      対象ディレクトリを限定（例: src/server）
--focus <観点>      特定の観点のみ実行（例: sec,perf）
--priority <level>  指定優先度以上のみ報告（例: major）
--github            issueをGitHubに登録
--skip-multimodel   agent cli並行レビューをスキップ（Claude Codeのみ）
```

## Taskツールによる進捗表示（オプション）

6つのサブエージェント起動前にタスクを作成し、進捗を可視化できる。
詳細: @context/task-tool-guide.md

```
# 各観点のタスクを作成
TaskCreate(subject: "Performance観点レビュー", activeForm: "パフォーマンス分析中")
TaskCreate(subject: "Security観点レビュー", activeForm: "セキュリティ分析中")
TaskCreate(subject: "Test観点レビュー", activeForm: "テスト分析中")
TaskCreate(subject: "Architecture観点レビュー", activeForm: "アーキテクチャ分析中")
TaskCreate(subject: "Code Quality観点レビュー", activeForm: "コード品質分析中")
TaskCreate(subject: "Documentation観点レビュー", activeForm: "ドキュメント分析中")
```

サブエージェント完了後:
```
TaskUpdate(taskId, status: "completed", metadata: {issues_found: 3})
```

**メリット:**
- TaskListで各観点の進捗をリアルタイム確認
- 完了した観点と未完了の観点が一目で分かる

## 注意事項

- サブエージェントは必ず並列で起動する（順次実行しない）
- 各サブエージェントは独立して動作し、他のエージェントの結果を待たない
- issueファイルのタイトル部分は日本語で具体的に記述
- 同じ問題が複数の観点に該当する場合、最も重要な観点で1つだけ作成
- 優先度critは慎重に使用（本当に即時対応が必要な場合のみ）
- **コードベース全体を網羅的に確認すること（一部だけ見て終わりにしない）**
- **問題発見時はcontext7/WebSearchでベストプラクティスを必ず調査**
- **CRITICAL: agent cli呼び出しは `--skip-multimodel` オプションが明示的に指定されない限り必須。自己判断でのスキップは禁止**
- **サブエージェントプロンプトには共通テンプレート全体（タスク1〜4すべて）を含めること。観点別の詳細指示のみでは不十分**
