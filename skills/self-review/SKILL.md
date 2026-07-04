---
name: self-review
description: 自分の作業ブランチのPR提出前セルフレビュー（diff包括チェック）。使用タイミング: (1) 「セルフレビューして」「消し忘れないか確認して」「diffを徹底チェックして」「変更漏れ・削除漏れがないか見て」等の依頼時、(2) PR作成前の最終確認時。境界: 他者PR（番号/URL指定）のレビュー→pr-review、コードベース全体監査→codebase-review、文書レビュー→doc-review。
allowed-tools: Read, Grep, Glob, Bash(git:*), Bash(rg:*)
---

# self-review - PR提出前のセルフレビュー

自分の作業ブランチのdiff全量を包括チェックし、消し忘れ・変更漏れ・意図しない変更を検出する。
コード品質のレビュー（バグ・設計）ではなく、**変更の完全性と純度**の検証に特化する。

## 既存設定との関係

- **Phase 4 品質確認（@context/workflow-rules.md）**: lint/format/typecheck/testを補完する。agent reviewの前に実施すると指摘ノイズが減る
- **pr-reviewスキル**: 他者PRのレビュー用。本スキルは自分のブランチのPR提出前チェック用

## ワークフロー

### 1. ベースの確定とdiff全量取得

```bash
# BASE_BRANCHはPJ CLAUDE.md参照（未定義時: develop→main→master）
git log --oneline <BASE_BRANCH>..HEAD
git diff <BASE_BRANCH>...HEAD --stat
git diff <BASE_BRANCH>...HEAD
git status   # 未コミット変更の確認
```

diffは省略せず全ファイル確認する。一部だけ確認しても意味がない。

### 2. 消し忘れ・残存の検出（必須）

diffで**削除・リネームされた識別子**を抽出し、リポジトリ全体で残存検索する:

- 対象識別子: メソッド名・クラス名・定数・env key・docker service名・キュー名・設定キー・ルーティングパス等
- 検索範囲: コードに加えて config / docker-compose / .env* / CI定義（.github/workflows等）/ docs / テストfixture
- コマンド: `git grep -n "<identifier>"` または `rg -n "<identifier>"`

```bash
# 例: 削除した識別子ごとに実行
git grep -n "konbini-payment-requires-action"
```

- 残存あり → 消し忘れとして報告（削除対象か、意図的に残すのかを判定）
- 逆方向も確認: 削除した機能を参照していた呼び出し元が全て更新されているか

### 3. 意図しない変更の検出

- **format副作用**: 自分のタスクと無関係なファイルの整形のみの変更（`git diff --stat` で変更行数が多い割に意図が不明なファイル）
- **混入**: `.idea/` `.vscode/` `.env*` `*.log` lockファイルの意図しない変更、一時ファイル
- **デバッグ残骸**: `console.log` / `print` / `debugger` / コメントアウトされた試行コード / TODO の置き忘れ
- **無関係コミット**: `git log` に他タスクのコミットが混入していないか（rebase漏れ）

### 4. タスク要件との突合

双方向で確認する:

1. **要件 → diff**: 今回のタスク要件（ユーザー指示・計画書・チケット）の各項目が、diffのどの変更で満たされているか対応付ける。満たされていない要件があれば「漏れ」
2. **diff → 要件**: diffの各変更が要件のどれかに紐づくか。紐づかない変更は「過剰（スコープ外変更）」として報告

### 5. レポート

```markdown
# セルフレビュー: <ブランチ名>

## 対象
- ブランチ: <branch> → <base>（コミットN件、ファイルM件）

## 消し忘れ・残存
- [なし / 検出内容（ファイル:行）]

## 意図しない変更
- [なし / 検出内容と推奨対応（戻す・別コミット化等）]

## 要件との突合
| 要件 | 対応する変更 | 判定 |
|------|------------|------|
| ... | ... | OK / 漏れ / 過剰 |

## 推奨アクション
1. [修正が必要な項目]
```

## 注意事項

- 検出した問題の修正は報告後にユーザー判断を仰ぐ（勝手にファイルを戻さない。特に `git checkout --` は format副作用と断定できるファイルのみ・判断不能時はユーザー確認）
- 「漏れなく」は要件に対する漏れの確認であり、無関係な要素の網羅列挙ではない（スコープ膨張禁止）

## 既存設定への参照

- @context/workflow-rules.md
