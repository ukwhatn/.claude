---
name: codebase-review
description: コードベース全体のレビュー・監査。perf/sec/test/arch/cq/docs の6観点を並列委譲し、優先度付き issue ファイルと観点サマリをメモリディレクトリに生成する。コードベース全体の監査・定期レビュー・リリース前品質確認の依頼時、/codebase-review 実行時に使用。境界: PR 単位は pr-review、自ブランチの提出前確認は self-review。
allowed-tools: Read, Write, Grep, Glob, Bash(mkdir:*), Bash(find:*), Bash(ls:*), Bash(~/.claude/bin/herdr-delegate.sh:*), Bash(herdr:*)
---

# コードベース包括的レビュー

コードベース全体を6観点で並列にレビューし、見つけた問題を優先度付きの issue ファイルに記録する。このスキルの起動が、6観点の並列委譲の実行依頼にあたる。

## レビュー観点

| 観点 | 略語 | 説明 |
|------|------|------|
| Performance | perf | N+1、不要な再レンダリング、重い処理等 |
| Security | sec | 脆弱性、認証・認可、入力検証等 |
| Test | test | テストカバレッジ、テストケース不足 |
| Architecture | arch | 責務分割、依存関係、設計パターン |
| Code Quality | cq | 命名、一貫性、可読性、不要コード |
| Documentation | docs | ドキュメント不足、内容の陳腐化 |

## 優先度

| 優先度 | 略称 | 説明 | 対応期限 |
|--------|------|------|---------|
| critical | crit | 即座に対応必須（本番障害、重大脆弱性） | 即時 |
| major | maj | 早期対応推奨（バグ、セキュリティリスク） | 次リリースまで |
| minor | min | 改善推奨（設計改善、技術的負債） | 計画的に対応 |
| trivial | triv | 余裕があれば対応（軽微な改善） | 任意 |

ファイル名をアルファベット順に並べると優先度順になる。

## 手順

### Phase 0: 準備

1. PJ CLAUDE.md の MEMORY_DIR（未定義なら `.local/`）の下に `memory/YYMMDD_codebase-review/` と `issues/` を作る。日付はシステムプロンプトの Today's date から取る
2. 05_log.md を初期化する
3. PJ の CLAUDE.md・context/ と主要ディレクトリの構成を把握する

### Phase 1: 6観点の並列委譲

各観点の担当は issue ファイルと観点サマリを自分で書くので、herdr pane へ委譲する。経路・起動・結果の回収・失敗時の調査は `context/herdr-delegation.md` に従う。Herdr 外では同ファイル「Herdr外でのフォールバック」に従い、Claude Code では Agent tool の `subagent_type: "general-purpose"`・`model: "opus"` で代替する（`Explore` はファイルを書けない）。並列の機構が無い環境（Codex 等）では、6観点を同じテンプレートで逐次実行する。

**指示書の組み立て（観点ごとに1ファイル）:**

1. `references/subagent-prompts.md` の指示書テンプレート（タスク1〜5）と、`references/review-aspects.md` の該当観点の詳細・優先度基準を読む
2. テンプレートの `## あなたの担当観点` に該当観点を挿入し、`{...}` を実値で埋めて `<メモリディレクトリ>/task-<観点略語>.md` に書き出す
3. 埋める値: メモリディレクトリ・対象リポジトリ・`references/subagent-prompts.md` の絶対パス、PJ CLAUDE.md の内容、担当観点とレビュー基準、Phase 0 で把握した構成。パスはすべて絶対パスにする（委譲先は lead の会話を共有しないので、相対パスの起点が伝わらない）

テンプレートは観点の詳細だけでなく全体を渡す。タスク3（外部 CLI との並行レビュー）は `--skip-multimodel` の指定が無い限り省かない（別モデルとの突き合わせが無いと検出の信頼度が下がるため）。

**起動（6並列）:**

- 全観点を `--kind claude --model opus` で起動する（issue ファイルを書く文書生成のため。外部 CLI は担当の中でタスク3として呼ばれるので、kind を分けない）
- `--out` には観点サマリ `<メモリディレクトリ>/aspect-<観点略語>.md` を指定する（issue は0件になり得るので、完了判定に使えるのは観点サマリだけ）
- 指示書・観点サマリ・state・結果 JSON・ログの保存先は観点ごとに分ける
- 起動時刻・成果物パス・完了の有無を、観点ごとに1行ずつ05_log.md に記録する

### Phase 2: 結果の集約

1. 6観点の観点サマリを読み、確認した範囲と issue 件数を把握する。観点サマリが無い観点は未完了として扱い、結果 JSON の `status` と pane を確かめる
2. issues ディレクトリのファイルを集計し、観点サマリの件数と突き合わせる。食い違いは書き漏れか、観点間の重複を統合した痕跡のどちらかなので、どちらかを確かめてからサマリーに反映する
3. 各 issue ファイルからマルチモデル検証の統計を集計する

### Phase 3: サマリー作成

`<メモリディレクトリ>/summary.md` に書く。

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

サマリーを示し、優先度の妥当性・対応の順序・GitHub issue への登録の要否を確かめる。

## ファイル構成

```
${MEMORY_DIR}/
├── memory/
│   └── YYMMDD_codebase-review/
│       ├── 05_log.md              # 作業ログ
│       ├── task-<観点略語>.md      # 観点ごとの指示書（leadが生成）
│       ├── aspect-<観点略語>.md    # 観点サマリ（委譲先が生成。issue 0件でも1つ）
│       └── summary.md             # レビューサマリー
└── issues/                        # issueファイル（マルチモデル検証済み）
    ├── critical-*.md
    ├── major-*.md
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
