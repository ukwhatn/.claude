# GitHub CLI・集計の注意

Read when: 大量ページの `gh api` 取得・PRの状態棚卸し・PR / issueへの画像添付・多バイト文字列の集計の前（AGENTS.mdのRead when一覧から誘導）。

## 画像・動画の添付

- **PR・issueの本文やコメントに画像・動画を貼るときは、ブラウザでアップロードせず `gh` の `--attach` を使う**（`gh pr create` / `gh pr edit` / `gh issue create` / `gh pr comment` 等。gh v2.99.0以降）。ブラウザ操作ツールのプロファイルはGitHubにログインしていないことがあり、アップロードできない。`gh --version` が古ければ先に更新する
  - 本文に `![alt](./shot.png)` と書いて `--body-file` と一緒に `--attach ./shot.png` を渡すと、その参照がアップロード先のURLに置き換わる。本文フラグなしで渡すと既存本文の末尾に追記される
  - 一部の添付だけ失敗しても成功分で更新され、exit codeは非0になる。exit codeを見て、失敗したファイルを再送する

## 取得

- **`gh api --paginate` は大量ページで接続リセットが起きてもexit 0を返し、取得結果が警告なく欠損する**。数千件規模の取得はページ単位で取得し、失敗ページのみリトライする方式にし、取得件数を期待値と突き合わせる

## PRの状態の報告

- PRの状態を棚卸しして報告するときは、未レビュー / approve済み未マージ / 修正済みでre-review未依頼 の3分類で出す。レビュー依頼は個人宛のみを対象とし、チーム宛は除外する
- PRの承認判定は人間レビュワーのApproveのみで行う。`gh pr view` の `reviewDecision` はbotのApproveを含むため、そのまま「承認済み」と報告しない（内訳: `gh api repos/<owner>/<repo>/pulls/<n>/reviews --jq '.[] | "\(.user.login) type=\(.user.type) \(.state)"'`）

## 集計

- **多バイト文字列の集計に `sort | uniq -c` を使わない**（ロケール依存の照合で異なる文字列が統合され、カテゴリ数が実際より少なく出る）。集計はPython等の明示的なカウントで行い、チャンク別と全体の集計が矛盾しないか突き合わせる
