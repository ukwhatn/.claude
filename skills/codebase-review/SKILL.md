---
name: codebase-review
description: コードベース包括的レビュー。6観点（perf/sec/test/arch/cq/docs）を並列サブエージェントで実行し、優先度付きissueファイルをメモリディレクトリに生成。使用タイミング: コードベース全体の監査・定期レビュー・リリース前品質確認の依頼時、/codebase-review実行時。境界: PR単位のレビュー→pr-review、自ブランチの提出前確認→self-review、ローカル未コミット変更→/code-review、ドキュメントのレビュー→doc-review。
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

4. コードベース構造の把握

```bash
# ディレクトリ構造を取得
find . -type d -not -path '*/node_modules/*' -not -path '*/.git/*' | head -100

# 主要ファイルタイプの分布を確認
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.md" \) \
  -not -path '*/node_modules/*' | wc -l
```

### Phase 1: 並列サブエージェント実行

6つのサブエージェントを**同時に**起動する（Claude Code: Task ツールを1つのメッセージで6回呼び出す）。順次実行しない。並列サブエージェント機構が無い環境（Codex 等）では、6観点を同一テンプレートで**逐次実行**して代替する。

- Claude Code では `subagent_type=general-purpose` を使用する（`Explore`はファイル書き込み不可でissueファイルを作成できないため）
- 各サブエージェントに渡す情報: メモリディレクトリのフルパス / PJ CLAUDE.mdの内容 / 対象リポジトリのパス / 担当観点とレビュー基準 / Phase 0で取得したコードベース構造

**プロンプトの組み立て:**

1. `references/subagent-prompts.md` をReadし、共通プロンプトテンプレート（タスク1〜4）を取得する
2. `references/review-aspects.md` をReadし、各観点の詳細指示・優先度基準を取得する
3. テンプレートの `## あなたの担当観点` に該当観点の内容を挿入し、6観点分のプロンプトを構築して並列spawnする

タスク1〜4はすべて必須。`--skip-multimodel` が明示指定されない限りタスク3（agent cli並行レビュー）を省略しない（マルチモデル検証を欠くと検出の信頼度が下がるため）。観点別の詳細指示のみを渡すのは不十分で、テンプレート全体を渡すこと。

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

## タスク管理機構による進捗表示（オプション・Claude Code）

6観点のタスクをTaskCreateで作成すると、TaskListで各観点の進捗をリアルタイムに可視化できる（完了・未完了が一目で分かる）。サブエージェント完了後に `TaskUpdate(taskId, status: "completed", metadata: {issues_found: N})` で更新する。詳細: @context/task-tool-guide.md（Codex では plan 機構で代替）

## 注意事項

- サブエージェントは並列で起動し、各々は独立して動作する（他エージェントの結果を待たない）
- issueファイルのタイトルは日本語で具体的に記述する
- 同じ問題が複数観点に該当する場合、最も重要な観点で1つだけ作成する
- 優先度critは本当に即時対応が必要な場合のみ使用する
- コードベース全体を網羅的に確認する（一部だけ見て終わらせると担当観点の問題を見落とすため）
- 問題発見時はcontext7/WebSearchでベストプラクティスを調査する（推測での改善案を避けるため）
- agent cli呼び出しは `--skip-multimodel` が明示指定されない限り実行する（マルチモデル検証を欠くと検出の信頼度が下がるため）
- サブエージェントにはタスク1〜4すべてを含む共通テンプレート全体を渡す（観点別の詳細指示のみでは網羅性・検証が不足するため）
