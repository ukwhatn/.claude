# Gotchas: マージ済み判定を誤らせるもの

## 1. three-dot diffの行数は「未反映」の証拠にならない

`git diff origin/main...HEAD` は **merge-baseからHEADへの差分**、つまりブランチが加えた変更を丸ごと出す。squashマージでbaseに取り込まれていても出力は1行も減らない。

「大量のファイル・行数の差分が残っている」→「未マージ」と読むのは誤り。この誤読をすると、完全にマージ済みのブランチを「作業中・削除不可」と誤って報告する。

反映の有無を見るのはtwo-dot比較。

```bash
git diff --name-only origin/main...HEAD > /tmp/f.txt   # ブランチが触ったファイル
cat /tmp/f.txt | xargs git diff --name-status HEAD origin/main --
```

出力が空なら、そのブランチの変更は全てbaseに入っている。

差分が残った場合、それが「ブランチ側の未反映」か「base側の後続変更」かは分岐点との三者比較で切り分ける。

```bash
mb=$(git merge-base HEAD origin/main)
# ファイル F について blob hash を比較
#   merge-base == base 側  → ブランチ側だけが変更 = 未反映
#   merge-base == HEAD 側  → base 側が後から変更 = ブランチが古いだけ
#   どちらとも違う          → 両側で変更。実 diff を読んで方向を判断する
```

三者比較で「両側で変更」ばかりになる場合、merge-baseが古すぎる。PRのmerge commitを基準に取り直すと直接比較できる。

```bash
mc=$(gh pr view <PR番号> --json mergeCommit -q .mergeCommit.oid)
git diff --name-status HEAD "$mc" -- $(cat /tmp/f.txt | tr '\n' ' ')
```

## 2. squashマージは `--merged` で検出できない

squash / rebaseマージはコミットが作り直されて別SHAになるため、`git branch --merged` でも `merge-base --is-ancestor` でも検出されない。**squashマージ運用のリポジトリではworktreeの相当数がこれに該当し、祖先判定だけなら全部「未マージ」に見える**。

PR stateを引くのが唯一の確実な検出手段。

```bash
gh pr list --head "$br" --state all --json number,state,headRefOid
```

## 3. PRを持たない統合ブランチは3手法すべてをすり抜ける

複数のfeatureブランチを `git merge` で束ねた統合ブランチは、次の全てに該当して「未マージ」に見え続ける。

- PRを作っていない → PR stateの検索結果が空
- 内容は別PRとしてsquashマージされた → SHAもpatch-idもbaseに無い
- マージコミットの塊 → 祖先判定は原理的に通らない

**判定は §1のtwo-dot比較で行う。** この形のブランチは大量の「未反映」行数が出ていても、実際は完全にマージ済みであることがある。

分割PRを出した後で一本化してマージし直した場合、分割側のPRは `CLOSED`（マージせず破棄）になる。`CLOSED_PR` を機械的に「内容がbaseに無い」と扱わないこと。一本化先のPRを探す。

## 4. `HEAD_MISMATCH` の確定方法

PRがMERGEDでもローカルHEADがPR headと一致しないケース。原因は2つ。

**(a) PR head objectがローカルに無い** — マージ後にリモートブランチが削除され、fetchでも取れない。PRのcommits一覧にローカルHEADが含まれるかで判定する。

```bash
gh pr view <PR番号> --json commits -q '[.commits[].oid]' | grep "$(git rev-parse HEAD)"
```

含まれていれば、ローカルHEADはPRの一部。削除して問題ない。

**(b) PRマージ後にローカルで積んだコミットがある** — そのコミットが触ったファイルをbaseと比較する。base側で既にファイルごと消えている / 内容が同一なら、保全価値は無い。

```bash
git show --stat <sha>
git diff --stat <sha> origin/main -- $(git show --name-only --format="" <sha> | tr '\n' ' ')
```

## 5. `git worktree remove` が孤立ディレクトリを残す

removeがディレクトリ削除に失敗しても、git側のメタデータ（`.git/worktrees/<name>`）は先に消えることがある。その後 `git worktree prune` を実行すると登録だけが消え、**git管理外のディレクトリが丸ごと残る**。`git worktree list` には出ないので気づきにくい。

削除後はworktree置き場を実際に `ls` して確認する。残っていた場合、`.git` ファイルのgitdir先が既に存在しないため `git status` すら取れない。削除前スナップショットのdirty / untrackedが0だったことを確認してから `rm -rf` する。

## 6. `MERGED_ANCESTOR` なのに `git branch -d` が拒否する

auditは `origin/<base>` を基準に祖先判定するが、**`git branch -d` は「現在のHEADまたはupstream」を基準にする**。ローカルの `main` が `origin/main` より遅れていると、origin/mainにマージ済みのブランチでも `-d` は「未マージ」として拒否する。

auditが `MERGED_ANCESTOR` と出しているなら削除して問題ない。ローカル `main` を更新するか、そのまま `-D` を使う。**この理由で `-D` が必要になった場合は、squashマージ由来の `-D` と区別して報告する**（前者はbaseが古いだけ、後者は実際に祖先でない）。

## 7. 削除したworktreeがcwdだと以降のコマンドが全部壊れる

調査で `cd` したworktreeを削除すると、シェルのcwdが消えて `getcwd: cannot access parent directories` になる。以降のコマンドが軒並み失敗する。

調査は `git -C <path>` で行い `cd` しない。この状態になったら `cd` で有効なディレクトリに戻る。
