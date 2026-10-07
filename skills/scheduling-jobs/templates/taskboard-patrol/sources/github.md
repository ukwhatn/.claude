# ソース部品: GitHub

自分の PR・レビュー依頼・merge 済みの PR の新規検出と、release tag による本番到達の確認（任意）。既存タスクの PR の状態は RUNBOOK の 1-1（`.tb-state.json` の `links[]`）で読むので、ここでは新しく起票するものだけを探す。

## 固定値の行

| 対象 | 値 |
|---|---|
| GitHub | `{{GITHUB_HOST}}` だけ（`gh auth status` の active account = `{{GITHUB_ACCOUNT}}`） |

## 収集（1-2〜 に貼る）

### 1-N. GitHub（新規検出だけ）

```bash
gh search prs --author=@me --state=open --limit 30 --json url,title,repository,isDraft,createdAt,updatedAt
gh search prs --review-requested=@me --state=open --limit 30 --json url,title,repository,createdAt,updatedAt
gh search prs --author=@me --merged --merged-at ">=<since の日付>" --limit 30 --json url,title,closedAt
```

- `gh search prs` の `--json` に `reviewDecision` は**無い**。個別の詳細が要るときだけ、件数を絞ってから `gh pr view <url> --json state,isDraft,reviewDecision,mergedAt` を使う
- `--review-requested=@me` は GitHub の仕様上、**チーム宛の依頼を含まない**。{{REVIEW_SCOPE}}
  <!-- 埋め方の例: 「バイネームの依頼だけを対象にする。--review-requested=<org>/<team> を足さず、チーム宛が出ないことを取りこぼしとして報告しない」か「チーム <org>/<team> 宛も対象にする。同じクエリを --review-requested=<org>/<team> でも投げる」 -->

### 1-N. release tag（本番到達の確認。任意）

merge だけでは「どの環境まで出たか」が分からない。「マージしたら」の列に滞留するタスクの完了候補は、ここで取る。リリースノートにそのリリースに乗った PR の URL が並ぶ運用のリポジトリでだけ使う（並ばないなら、この節と 2-1 の行を貼らない）。

```bash
gh release list -R {{RELEASE_REPO}} --limit 5
gh release view <TAG> -R {{RELEASE_REPO}} --json tagName,publishedAt,body
```

- タグ名の形: `{{RELEASE_TAG_FORMAT}}`（環境がタグ名のどこに出るか。本番を表す値: `{{PROD_ENV}}`）
- **`since` 以降に publish されたタグだけ** `view` する（毎回全タグを開かない）

## 2-1 に足す判定

release tag が取れたタスク:

| live 状態 | 扱い |
|---|---|
| リンク PR が本番（`{{PROD_ENV}}`）のタグに含まれる | **完了候補 → 通知だけ** |
| リンク PR が本番以外のタグに含まれる | 列は動かさない。note に「<TAG> に入った」を追記する |
| どのタグにも含まれない | 判断の材料にしない（列は PR・チケットの表で決める） |

## 起票の既定

| 由来 | 動作 | 列 |
|---|---|---|
| 自分の open PR で、taskboard に無いもの | **自動で起票する**（`seen.decision = "created"`） | draft なら作業中、それ以外はレビュー中 |
| レビュー依頼の PR で、taskboard に無いもの | **自動で起票する** | レビュー依頼 |
| merge 済みの自分の PR で、taskboard に無いもの | **自動で起票する** | 案件の「マージしたら」の列 |

- `seen` のキー: PR の URL
- 起票の前に RUNBOOK 2-2 の URL の重複判定と、調査・計画タスクとの領域の突き合わせを通す（ほかのセッションの Stop hook が open の PR から自動で起票していることがある）

## cursor

- `github_merged_from`（初期値 null）: merged の検索の `since`。GitHub の取得が全部成功した回だけ進める

## 上限

| 項目 | 上限 |
|---|---|
| GitHub | 各クエリ30件 |
| release tag の `view` | リポジトリごとに3件 |

## 禁止事項

- GitHub へ書き込まない（コメント・レビュー・approve・PR の作成と編集・merge・ラベル・issue の操作。`gh` の `create` / `edit` / `comment` / `review` / `merge` / `api -X POST|PATCH|PUT|DELETE` を実行しない）
