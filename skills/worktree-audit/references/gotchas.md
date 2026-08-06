# Gotchas: マージ済み判定を誤らせるもの

## 1. three-dot diff の行数は「未反映」の証拠にならない

`git diff origin/main...HEAD` は **merge-base から HEAD への差分**、つまりブランチが加えた変更を丸ごと出す。squash マージで base に取り込まれていても出力は 1 行も減らない。

「大量のファイル・行数の差分が残っている」→「未マージ」と読むのは誤り。この誤読は、完全にマージ済みのブランチを「作業中・削除不可」と誤って報告させる。

反映の有無を見るのは two-dot 比較。

```bash
git diff --name-only origin/main...HEAD > /tmp/f.txt   # ブランチが触ったファイル
cat /tmp/f.txt | xargs git diff --name-status HEAD origin/main --
```

出力が空なら、そのブランチの変更は全て base に入っている。

差分が残った場合、それが「ブランチ側の未反映」か「base 側の後続変更」かは分岐点との三者比較で切り分ける。

```bash
mb=$(git merge-base HEAD origin/main)
# ファイル F について blob hash を比較
#   merge-base == base 側  → ブランチ側だけが変更 = 未反映
#   merge-base == HEAD 側  → base 側が後から変更 = ブランチが古いだけ
#   どちらとも違う          → 両側で変更。実 diff を読んで方向を判断する
```

三者比較で「両側で変更」ばかりになる場合、merge-base が古すぎる。PR の merge commit を基準に取り直すと直接比較できる。

```bash
mc=$(gh pr view <PR番号> --json mergeCommit -q .mergeCommit.oid)
git diff --name-status HEAD "$mc" -- $(cat /tmp/f.txt | tr '\n' ' ')
```

## 2. squash マージは `--merged` で検出できない

squash / rebase マージはコミットが潰れて別 SHA になるため、`git branch --merged` にも `merge-base --is-ancestor` にも引っかからない。**squash マージ運用のリポジトリでは worktree の相当数がこれに該当し、祖先判定だけなら全部「未マージ」に見える**。

PR state を引くのが唯一の確実な検出手段。

```bash
gh pr list --head "$br" --state all --json number,state,headRefOid
```

## 3. PR を持たない統合ブランチは3手法すべてをすり抜ける

複数の feature ブランチを `git merge` で束ねた統合ブランチは、次の全てに該当して「未マージ」に見え続ける。

- PR を作っていない → PR state が空振り
- 内容は別 PR として squash マージされた → SHA も patch-id も base に無い
- マージコミットの塊 → 祖先判定は原理的に通らない

**判定は §1 の two-dot 比較で行う。** この形のブランチは大量の「未反映」行数を見せながら、実際は完全にマージ済みであることがある。

分割 PR を出した後で一本化してマージし直した場合、分割側の PR は `CLOSED`（マージせず破棄）になる。`CLOSED_PR` を機械的に「内容が base に無い」と扱わないこと。一本化先の PR を探す。

## 4. `HEAD_MISMATCH` の確定方法

PR が MERGED でもローカル HEAD が PR head と一致しないケース。原因は2つ。

**(a) PR head object がローカルに無い** — マージ後にリモートブランチが削除され、fetch でも取れない。PR の commits 一覧にローカル HEAD が含まれるかで判定する。

```bash
gh pr view <PR番号> --json commits -q '[.commits[].oid]' | grep "$(git rev-parse HEAD)"
```

含まれていれば、ローカル HEAD は PR の一部。削除して問題ない。

**(b) PR マージ後にローカルで積んだコミットがある** — そのコミットが触ったファイルを base と比較する。base 側で既にファイルごと消えている / 内容が同一なら、保全価値は無い。

```bash
git show --stat <sha>
git diff --stat <sha> origin/main -- $(git show --name-only --format="" <sha> | tr '\n' ' ')
```

## 5. `git worktree remove` が孤立ディレクトリを残す

remove がディレクトリ削除に失敗しても、git 側のメタデータ（`.git/worktrees/<name>`）は先に消えることがある。その後 `git worktree prune` を打つと登録だけが消え、**git 管理外のディレクトリが丸ごと残る**。`git worktree list` には出ないので気づきにくい。

削除後は worktree 置き場を実際に `ls` して確認する。残っていた場合、`.git` ファイルの gitdir 先が既に存在しないため `git status` すら取れない。削除前スナップショットの dirty / untracked が 0 だったことを確認してから `rm -rf` する。

## 6. `MERGED_ANCESTOR` なのに `git branch -d` が拒否する

audit は `origin/<base>` を基準に祖先判定するが、**`git branch -d` は「現在の HEAD または upstream」を基準にする**。ローカルの `main` が `origin/main` より遅れていると、origin/main にマージ済みのブランチでも `-d` は「未マージ」として拒否する。

audit が `MERGED_ANCESTOR` と出しているなら削除して問題ない。ローカル `main` を更新するか、そのまま `-D` を使う。**この理由で `-D` が必要になった場合は、squash マージ由来の `-D` と区別して報告する**（前者は base が古いだけ、後者は実際に祖先でない）。

## 7. 削除した worktree が cwd だと以降のコマンドが全部壊れる

調査で `cd` した worktree を削除すると、シェルの cwd が消えて `getcwd: cannot access parent directories` になる。以降のコマンドが軒並み失敗する。

調査は `git -C <path>` で行い `cd` しない。踏んでしまったら `cd` で有効なディレクトリに戻る。
