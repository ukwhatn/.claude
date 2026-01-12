---
allowed-tools: Bash(git:*), Bash(gh:*)
argument-hint: [base-branch]
description: Draft PRを作成
---

# /pr コマンド

Draft PRを作成します。

## 実行手順

### 1. 現在の状態確認

```bash
git branch --show-current
git status
git log $ARGUMENTS..HEAD --oneline
```

### 2. PRテンプレートの確認

```bash
ls .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
```

### 3. 変更内容の確認

```bash
git diff $ARGUMENTS --name-only
git diff $ARGUMENTS
```

### 4. PR本文の作成

テンプレートがあれば使用、なければ以下:

```markdown
## 概要
[変更内容の概要]

## やったこと
- 変更1
- 変更2

## やらなかったこと
- スコープ外の内容

## 影響範囲
- 影響を受ける画面・処理

## テスト方法
[動作確認方法]

## チェックリスト
- [ ] 型チェック通過
- [ ] Lint通過
- [ ] テスト通過
```

### 5. Draft PR作成

```bash
gh pr create --draft \
  --base $ARGUMENTS \
  --title "<タイトル>" \
  --body "$(cat <<'EOF'
<本文>
EOF
)"
```

### 6. 結果の報告

作成されたPRのURLを報告。
