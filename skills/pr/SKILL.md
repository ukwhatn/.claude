---
name: pr
description: Draft PRを作成。`/pr`で実行。引数にベースブランチを指定可能。
allowed-tools: Bash(git:*), Bash(gh:*)
---

# /pr

Draft PRを作成する。

## 引数

- ベースブランチ名（省略時: PJ CLAUDE.mdのBASE_BRANCH）

## 実行手順

### 1. 現在の状態確認

```bash
git branch --show-current
git status
git log <base-branch>..HEAD --oneline
```

### 2. PRテンプレートの確認

```bash
ls .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
```

### 3. 変更内容の確認

```bash
git diff <base-branch> --name-only
git diff <base-branch>
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
  --base <base-branch> \
  --title "<タイトル>" \
  --body "$(cat <<'EOF'
<本文>
EOF
)"
```

### 6. 結果の報告

作成されたPRのURLを報告。
