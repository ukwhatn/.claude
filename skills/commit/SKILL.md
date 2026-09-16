---
name: commit
description: 変更をコミットする。/commit 実行時、「コミットして」「pushして」等の依頼時に使用。--push 引数または「pushして」の依頼で push も行う。
allowed-tools: Bash(git:*)
---

# /commit

変更をコミットする。`--push` 引数でpushも実行。

## 引数

- `--push`: コミット後にpushする（デフォルト: false）

## 自然言語依頼の正規化

- 「pushして」「コミットしてpushして」等のpush依頼は `--push` 相当として扱う
- 未コミットの変更がない状態で「pushして」と依頼された場合は、新規コミットを作らず既存コミットのpushのみ行う（`git status` で判定）

## 実行手順

### 0. 直コミット可否の確認

PJ `CLAUDE.md` / `CLAUDE.local.md` の記載を確認する。記載が無い、または記載と直近の履歴が食い違うなら `references/commit-policy.md` の手順で判定し、結果を永続化してから進む。チーム開発リポジトリで main / develop 直コミット不可なら作業ブランチへ切り替える。

### 1. 現在の状態確認

```bash
git status
git diff --stat
git log --oneline -5
```

### 2. コミットメッセージの決定

変更内容を分析し、git-cz形式でコミットメッセージを作成:

- prefix: feat/fix/docs/refactor/test/chore など
- prefix以外は日本語
- 例: `feat: ユーザー認証機能を追加`

### 3. ステージング

```bash
git add <files>
```

NOTE: CLAUDE.mdがglobal gitignoreされている場合は `git add -f` で追加

### 4. コミット

```bash
git commit -m "$(cat <<'EOF'
<コミットメッセージ>
EOF
)"
```

### 5. push（引数に --push がある場合のみ）

引数に `--push` が含まれる場合:

```bash
git push
```

**rejectされた場合**（別PCから同じリポジトリにpush済みのときに起きる）は、rebaseで取り込んでから再pushする:

```bash
git pull --rebase --autostash && git push
```

rebaseがconflictで停止した場合は `git rebase --abort` で元に戻し、コミットは残したままユーザーに報告する（自動解決しない）。

### 6. push 後の確認（--push の場合のみ）

push したブランチに PR があれば、**CI の結果と conflict の有無を確認してから報告する**。走行中なら完了まで監視する。落ちている・conflict がある場合は、指摘を待たず原因調査に入る。

```bash
gh pr view --json number,mergeable,mergeStateStatus,statusCheckRollup 2>/dev/null
```

PR がまだ無いブランチではこの確認は不要。

### 7. 結果の報告

- コミットハッシュ
- pushした場合はその旨と、PR があれば CI・conflict の状態
