---
allowed-tools: Bash(git:*)
argument-hint: [--push]
description: 変更をコミット
---

# /commit コマンド

変更をコミットします。`--push` 引数でpushも実行。

## 引数

- `--push`: コミット後にpushする（デフォルト: false）

## 実行手順

### 1. 現在の状態確認

```bash
git status
git diff --stat
git log --oneline -5
```

### 2. コミットメッセージの決定

変更内容を分析し、git-cz形式でコミットメッセージを作成:

- prefix: feat/fix/docs/refactor/test/chore など
- 絵文字なし
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

$ARGUMENTS に `--push` が含まれる場合:

```bash
git push
```

### 6. 結果の報告

- コミットハッシュ
- pushした場合はその旨
