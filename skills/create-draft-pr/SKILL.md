---
name: create-draft-pr
description: PRを作成（原則Draft）。使用タイミング: PR作成を依頼された時、実装が一段落しPR化する時、/create-draft-prで実行。引数にベースブランチを指定可能。境界: 直接gh pr createは実行せず本スキルを使う。特定レビューコメントへの対応はpr-comment、PRレビューはpr-review。
allowed-tools: Bash(git:*), Bash(gh:*)
---

# /create-draft-pr

PRを作成する。

## 引数

- ベースブランチ名（省略時: PJ CLAUDE.mdのBASE_BRANCH）
- `--no-draft`: Draft以外で作成する場合に指定

## 実行手順

### 1. 現在の状態確認

```bash
git branch --show-current
git status
git log <base-branch>..HEAD --oneline
```

### 2. PRテンプレートの確認

```bash
cat .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null || cat .github/pull_request_template.md 2>/dev/null
```

**CRITICAL**: テンプレートが存在する場合、すべてのセクションを埋める。セクションを削除しない（レビュアーが記入を前提にした項目が欠けると差し戻しの原因になり、テンプレートの意図が損なわれるため）。

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

**読みやすさ（IMPORTANT）**: 1 つの箇条書きに複数の論点を詰め込まない。What+Why+詳細が 1 文に連なって長くなる場合は文を分割し、設定値・理由・根拠はネストした箇条書きに逃がす。項目が多く雑多になったら `###` 小見出しでグループ化する。

### 5. PR作成

```bash
gh pr create --draft \
  --base <base-branch> \
  --title "<タイトル>" \
  --assignee @me \
  --body "$(cat <<'EOF'
<本文>
EOF
)"
```

**CRITICAL**: `--assignee @me` を必ず付ける（未アサインのPRはレビュー担当・追跡の割り当てが漏れるため）。
`--no-draft` 引数が指定された場合のみ `--draft` を外す。

### 6. 結果の報告

作成されたPRのURLを報告。

---

## PJ固有の運用ルール

hotfix等で複数のベースブランチへのPR作成運用（sync PR等）がPJ固有で定義されている場合は、PJ側スキル（例: `release-deploy`）の指示を優先すること。
