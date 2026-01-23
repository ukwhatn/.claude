---
name: project-init
description: プロジェクト初期化。CLAUDE.mdや.claude/がない場合にテンプレートを適用し、PJ固有設定を促す。
---

# プロジェクト初期化

## トリガー条件

以下のいずれかの場合に使用:
- プロジェクトルートにCLAUDE.mdが存在しない
- .claude/ディレクトリが存在しない
- ユーザーがプロジェクト初期化を要求した

## 実行手順

### 1. テンプレートの確認

```bash
ls ~/.claude/templates/project/
```

### 2. CLAUDE.mdの作成

PJルートに以下の内容でCLAUDE.mdを作成:

```markdown
# <プロジェクト名>

## 変数
MEMORY_DIR=.local/
BASE_BRANCH=develop

## 品質チェック
```bash
npm run lint      # または適切なコマンド
npm run format
npm run typecheck
npm test
```

## 特記事項
- [PJ固有のルール]
```

### 3. gitignore設定

`.local/`がgitに追跡されないよう設定:

```bash
# global gitignoreに.local/があるか確認
if git config --global core.excludesfile &>/dev/null; then
  GLOBAL_GITIGNORE=$(git config --global core.excludesfile)
  if grep -q "^\.local/$" "$GLOBAL_GITIGNORE" 2>/dev/null; then
    echo "global gitignoreで.local/は除外済み"
  else
    # gitリポジトリ内かどうか確認
    if git rev-parse --git-dir &>/dev/null; then
      # gitリポジトリ内の場合、.git/info/excludeに追加
      echo ".local/" >> "$(git rev-parse --git-dir)/info/exclude"
      echo ".git/info/excludeに.local/を追加"
    else
      # gitリポジトリ外（複数リポジトリの親ディレクトリ等）の場合はスキップ
      echo "gitリポジトリ外のため、gitignore設定をスキップ"
    fi
  fi
fi
```

### 4. ユーザーへの確認（AskUserQuestion使用）

AskUserQuestionツールで以下を確認:
1. メモリディレクトリの場所（モノレポの場合は調整が必要）
2. 品質チェックコマンド
3. ベースブランチ
4. PJ固有のルール

### 5. 設定の調整

ユーザーの回答に基づいてCLAUDE.mdを調整。

## モノレポの場合

モノレポでは、メモリディレクトリの場所を明確に指定:

```markdown
## 変数
MEMORY_DIR=<monorepo-root>/.local/
```

これにより、サブディレクトリで作業中も正しい場所にメモリディレクトリが作成される。

## 複数gitリポジトリの親ディレクトリで作業する場合

親ディレクトリ自体がgitリポジトリでない場合、gitignore設定は不要（各子リポジトリで個別対応）。

