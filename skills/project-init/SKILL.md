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

PJルートに以下の内容でCLAUDE.mdを作成（`~/.claude/templates/project/CLAUDE.md` と同期）:

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

## 検証方針

Opus 4.7 では検証機構の供給が最も効果が高い。PJで以下を整備:

- **テストコード**: 主要ロジックのユニット/統合テスト
- **E2Eテスト**: PJに応じてPlaywright/Cypress等
- **スクリーンショット**: UI変更時は `docs/screenshots/` に変更前後を保存
- **期待出力**: 主要コマンド/APIの fixture を `tests/fixtures/` 等に配置
- **Stop Hook**: 必要に応じて `.claude/settings.json` の `Stop` でテスト自動実行

## PJ固有ルール
- [PJ固有のルール]

<!--
注意: PJ独自のサブエージェント呼び出し慣習（quality-checker / pr-reviewer 等を明示的に呼ぶ等）は記述しない。
Subagent / Agent Teams の発動はuser-level設定（~/.claude/CLAUDE.md「Agent Teams 発動条件」）に従う。
-->
```

### 3. .claudeignoreの作成

コンテキスト最適化のため、`.claudeignore`を作成する（**最大の単一改善**）:

```bash
# プロジェクトの技術スタックに応じて作成
cat > .claudeignore << 'EOF'
# Lock files (30K-80K tokens)
package-lock.json
pnpm-lock.yaml
bun.lockb
yarn.lock

# Build output
dist/
build/
.next/
out/

# Dependencies
node_modules/

# Minified files
*.min.js
*.min.css

# Generated
*.generated.*
EOF
```

### 4. gitignore設定

`.local/`がgitに追跡されないよう設定:

```bash
# global gitignoreに.local/があるか確認
if git config --global core.excludesfile &>/dev/null; then
  GLOBAL_GITIGNORE=$(git config --global core.excludesfile)
  if grep -q "^\.local/$" "$GLOBAL_GITIGNORE" 2>/dev/null; then
    echo "global gitignoreで.local/は除外済み"
  else
    if git rev-parse --git-dir &>/dev/null; then
      echo ".local/" >> "$(git rev-parse --git-dir)/info/exclude"
      echo ".git/info/excludeに.local/を追加"
    else
      echo "gitリポジトリ外のため、gitignore設定をスキップ"
    fi
  fi
fi
```

### 5. ユーザーへの確認（AskUserQuestion使用）

AskUserQuestionツールで以下を確認:
1. メモリディレクトリの場所（モノレポの場合は調整が必要）
2. 品質チェックコマンド
3. ベースブランチ
4. PJ固有のルール
5. .claudeignoreに追加すべきパターン

### 6. 設定の調整

ユーザーの回答に基づいてCLAUDE.mdと.claudeignoreを調整。

## モノレポの場合

モノレポでは、メモリディレクトリの場所を明確に指定:

```markdown
## 変数
MEMORY_DIR=<monorepo-root>/.local/
```

## 複数gitリポジトリの親ディレクトリで作業する場合

親ディレクトリ自体がgitリポジトリでない場合、gitignore設定は不要（各子リポジトリで個別対応）。

## .claude/rules/の活用（オプション）

パス固有のルールがある場合、`.claude/rules/`を作成:

```bash
mkdir -p .claude/rules
```

```yaml
# .claude/rules/api-rules.md
---
paths:
  - "src/api/**/*.ts"
---
# API開発ルール
- すべてのAPIエンドポイントに入力バリデーションを含めること
```
