---
name: worktree-audit
description: マシン上の git worktree とローカルブランチを横断で棚卸しし、マージ済みかを3段階で判定して安全に削除する。使用タイミング (1) 「worktreeを整理して」「マージ済みブランチを消して」「worktreeを全部リストして」等の依頼時、(2) worktree が増えすぎた時の定期棚卸し、(3) /worktree-audit 実行時。境界: 単一 worktree の作成・命名・片付け手順は context/worktree-guide.md、コミット前の diff 確認は self-review、コードベースの品質監査は codebase-review。
allowed-tools: Bash, Read, Grep, Glob
---

# Worktree Audit

複数リポジトリにまたがる worktree とブランチを棚卸しし、削除可否を判定する。

**この skill の核心は「マージ済みの判定を1手法で済ませないこと」。** `git branch --merged` だけで判断すると、squash マージされたブランチが軒並み「未マージ」に見え、掃除できないまま溜まる。逆に three-dot diff の行数を根拠にすると、マージ済みのブランチを「未反映」と誤って報告する。

## ワークフロー

### 1. 棚卸し

```bash
bash ~/.claude/skills/worktree-audit/scripts/audit.sh > /tmp/audit.tsv
column -t -s $'\t' /tmp/audit.tsv
```

スクリプトはリポジトリ探索 → `git fetch` → 3段判定を行い TSV を返す。**出力だけが文脈に入る**（スクリプト本体は読まなくてよい）。

主なオプション:

| オプション | 用途 |
|---|---|
| `--branches` | worktree ではなく全ローカルブランチを対象にする |
| `--no-fetch` | オフライン時。判定は古い remote-tracking 基準になる |
| `--root DIR` | 探索起点を指定（既定: `$HOME/workspace` `$HOME/.claude` `$HOME/.dotfiles`） |

**完了基準**: TSV の全行に verdict が入っている。`NO_BASE` や `?` が出た行は、そのリポジトリの base ブランチ名を個別に確認して埋める。

### 2. 分類

verdict をそのまま3群に畳む。

| 群 | verdict | 扱い |
|---|---|---|
| 削除可 | `MERGED_ANCESTOR` `MERGED_SQUASH` | dirty / untracked が 0 ならそのまま消せる |
| 要判断 | `HEAD_MISMATCH` `CLOSED_PR` `NO_PR` | 内容が base にあるか個別確認（→ 3へ） |
| 削除不可 | `OPEN_PR` | 作業中 |

`dirty` / `untracked` が 0 でない行は、マージ済みでも削除で変更が失われる。群に関わらず退避対象として別に数える。

**完了基準**: 全行がいずれかの群に入り、要判断の行数を数え上げている。

### 3. 要判断の行を確定させる

ここを飛ばすと誤って消すか、逆に消せるものを残す。判定方法は references/gotchas.md に集約してある。**要判断の行が1件でもあれば必ず読むこと。**

要点だけ先に言うと、`git diff base...HEAD`（three-dot）の行数は反映有無の証拠にならない。実際に確認するのは次のいずれか。

```bash
# ブランチが触ったファイルだけを base と実比較する（差分ゼロなら反映済み）
cd <worktree>
git diff --name-only origin/main...HEAD > /tmp/f.txt
cat /tmp/f.txt | xargs git diff --name-status HEAD origin/main --
```

**完了基準**: 要判断だった全行が「削除可」「削除不可」のどちらかに移っている。判断がつかない行はユーザーに提示する。

### 4. 承認を取る

削除は破壊的操作。AGENTS.md「緩和しない安全項目」に従い、**実行前にユーザー確認を取る**（ユーザーが「確認不要」と明示した場合を除く）。

提示するもの: 削除対象の件数、リポジトリ別内訳、残すものとその理由、失われる未コミット変更の有無。

**完了基準**: ユーザーが対象範囲に同意している。

### 5. 退避してから削除

未コミット変更・untracked がある worktree は、破棄前に patch と tar で退避する。

```bash
git -C "$wt" diff > "$BK/$name.patch"
git -C "$wt" ls-files --others --exclude-standard > "$BK/$name.untracked.txt"
(cd "$wt" && tar czf "$BK/$name.untracked.tar.gz" -T "$BK/$name.untracked.txt")
```

ブランチを消す場合は **削除前に SHA を記録する**。`git branch <名前> <SHA>` で復元できる唯一の手がかりになる（とくに `CLOSED_PR` のブランチは内容が base に存在しない）。

```bash
git -C "$repo" rev-parse "refs/heads/$br" >> "$BK/deleted-branches-sha.tsv"
```

削除の順序は worktree → ブランチ。worktree が生きているブランチは削除できない。

```bash
git -C "$repo" worktree remove "$wt"        # dirty なら --force
git -C "$repo" branch -d "$br"              # squash マージ分は -D が必要
```

`-D` は permissions.deny 登録済みの破壊的操作。承認済みの範囲でのみ使う。

`MERGED_ANCESTOR` の行で `-d` が拒否されることがある。`branch -d` の基準が origin ではなくローカル HEAD だからで、削除自体は安全（→ references/gotchas.md §6）。

**完了基準**: 退避ファイルが存在し、削除コマンドの失敗が 0 件。失敗した行は個別に原因を報告する。

### 6. 検証

```bash
git -C "$repo" worktree prune
git -C "$repo" worktree list
git -C "$repo" branch
```

`git worktree remove` はディレクトリ削除に失敗しても git 側のメタデータを先に消すことがある。その後 `prune` すると、**git 管理外の孤立ディレクトリだけが残る**。worktree 置き場に想定外のディレクトリが残っていないか実際に `ls` して確かめる。

**完了基準**: 残存 worktree・ブランチが承認した内容と一致し、worktree 置き場に孤立ディレクトリが無い。

## 判定の3段階

スクリプトが内部で行っていること。手で追う必要が出た時のために。

1. **祖先判定** — `git rev-list --count "$base..$ref"` が 0。merge commit で取り込まれたものはここで確定する
2. **PR state** — 非該当を `gh pr list --head "$br" --state all` に通す。squash / rebase マージはコミット SHA が base に存在しないため、ここでしか検出できない
3. **PR head 一致** — MERGED でも、PR 作成後にローカルで積んだコミットが残っていることがある。`headRefOid` とローカル HEAD を比較し、不一致なら `HEAD_MISMATCH` として要判断へ落とす

## Gotchas

判定を誤らせる既知の罠は references/gotchas.md に集約してある。とくに次のどれかに当たったら読む。

- three-dot diff の行数を根拠にしようとした時
- `NO_PR` の統合ブランチ（マージコミットの塊）が出た時
- `HEAD_MISMATCH` が出た時
- 削除したはずのディレクトリが残っていた時

## 関連

- worktree の作成・命名・単一 worktree の片付け: context/worktree-guide.md
- 破壊的操作の確認規定: AGENTS.md「緩和しない安全項目」
- ブランチ命名・コミット規約: AGENTS.md「コミット・ブランチ・PR」
