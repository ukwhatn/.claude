---
name: pr-comment
description: PR の特定レビューコメント（discussion）への対応（実装修正と返信）。PR URL に discussion の id を添えて「この指摘に対応して」と依頼された時、PR 番号と特定の指摘内容を示された時に使用。境界: PR 全体のレビューは pr-review、返信文の作成のみは writing-prose。
---

# pr-comment - PRレビューコメント対応

PRに付いた特定のレビューコメント（discussion）を取得し、指摘への対応（実装修正）と返信ドラフト作成までを一括で行う。

## ワークフロー

### 1. アカウント確認（EMU誤アカウント防止）

```bash
gh auth status
```

EMU等で複数アカウントを使い分けている場合は、PJ CLAUDE.mdの指定に従い `gh auth switch` で切り替える。

### 2. コメントの取得

URLから `owner/repo`、PR番号、comment ID（`#discussion_r<id>` の数値部分）を抽出:

```bash
# コメント本文・対象ファイル・行・スレッドを取得
gh api repos/<owner>/<repo>/pulls/comments/<id>

# スレッド全体の文脈が必要な場合（in_reply_to_idを辿る / PR全コメントから該当スレッド抽出）
gh api repos/<owner>/<repo>/pulls/<number>/comments --paginate | jq '[.[] | select(.id == <id> or .in_reply_to_id == <id>)]'
```

comment IDが不明（「◯◯という指摘」等の口頭指定）の場合は、PR全コメントから該当コメントを検索し、複数候補があればユーザーに確認する。

### 3. PR headの特定とcheckout/worktree判断

現在のブランチに直接修正しないこと。

```bash
gh pr view <number> --json headRefName,headRefOid,baseRefName
```

- 修正を伴う場合: PR headブランチをworktreeでcheckoutする（PJ CLAUDE.mdに手段の定義があればそれを使う。作る前に `context/worktree-guide.md` を Read する）
- 対応方針の検討のみ（修正不要と判断される可能性が高い場合）: `git fetch origin <headRefName>` + FETCH_HEADの読解でも可

### 4. 指摘内容の理解と対応方針の提示

- 該当コード（コメントのpath/line周辺）をReadし、指摘の妥当性を判断
- 対応方針を提示: (a) 指摘通り修正 / (b) 代替案で修正 / (c) 修正不要（理由を返信）
- 判断が分かれる場合や指摘が仕様に関わる場合はユーザーに確認する（Claude Code: AskUserQuestion）

### 5. 実装対応

- 修正を実装し、品質チェック（PJ CLAUDE.mdのコマンド）を実行する。変えた挙動はローカルで実際に通して確かめる
- コミットは `/commit` スキルで作る
- push: 自分が出した PR のブランチへは、そのまま push してよい（PR を出した承認に含まれる。AGENTS.md「確認が要るもの」）。他人の PR のブランチへの push は、ユーザーの指示があるときだけ
- push したら、CI の結果と conflict の有無を確かめてから報告する（`gh pr view <number> --json mergeable,mergeStateStatus,statusCheckRollup`）。失敗していれば指摘を待たずに原因を調べる

### 6. 返信ドラフト作成

`/writing-prose` スキルを実行して返信ドラフトを作成し、対応コミットのハッシュを添えて提示する（文体を意識するだけでは GitHub 向けガイドの中身が読み込まれないため、スキルを実行する）。

投稿はドラフトを見たユーザーの承認を得てから行う（相手に見える対外の文なので）:

```bash
# 承認後のみ実行
gh api repos/<owner>/<repo>/pulls/<number>/comments/<id>/replies -f body='<返信本文>'
```

## 注意事項

- 同一PRに複数の指摘対応を依頼された場合は、指摘ごとに対応方針を整理してから着手する（コミットは指摘単位で分割）
- コメントが解決済み（resolved）またはoutdatedの場合はその旨を報告して指示を仰ぐ
