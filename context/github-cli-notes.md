# GitHub CLI・集計の注意

Read when: 大量ページの `gh api` 取得・PR の状態棚卸し・多バイト文字列の集計の前（AGENTS.md の Read when 一覧から誘導）。

## 取得

- **`gh api --paginate` は大量ページで接続リセットが起きても exit 0 を返し、取得が静かに欠損する**。数千件規模の取得はページ単位で取得し、失敗ページのみリトライする方式にし、取得件数を期待値と突き合わせる

## PR の状態の報告

- PR の状態を棚卸しして報告するときは、未レビュー / approve 済み未マージ / 修正済みで re-review 未依頼 の 3 分類で出す。レビュー依頼は個人宛のみを対象とし、チーム宛は除外する
- PR の承認判定は人間レビュワーの Approve のみで行う。`gh pr view` の `reviewDecision` は bot の Approve を含むため、そのまま「承認済み」と報告しない（内訳: `gh api repos/<owner>/<repo>/pulls/<n>/reviews --jq '.[] | "\(.user.login) type=\(.user.type) \(.state)"'`）

## 集計

- **多バイト文字列の集計に `sort | uniq -c` を使わない**（ロケール依存の照合で異なる文字列が統合され、カテゴリ数が実際より少なく出る）。集計は Python 等の明示的なカウントで行い、チャンク別と全体の集計が矛盾しないか突き合わせる
