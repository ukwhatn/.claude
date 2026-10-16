# PJ CLAUDE.md の雛形と提案の書式

project-sync の手順3（更新提案）と手順5（反映）で使う。

## CLAUDE.md の雛形

必須セクションは「変数」「品質チェック」「検証方針」「レビュー方針」「PJ固有ルール」。`<...>` は PJ の実値で埋める。

```markdown
# <PJ名>

## 変数
MEMORY_DIR=<path>
BASE_BRANCH=<branch>

## 品質チェック
```bash
<lint command>
<format command>
<typecheck command>
<test command>
```

## 検証方針
- ローカル起動: <dev server / CLI の起動コマンド>
- テストコード: <test command>
- E2Eテスト: <e2e command>（あれば）
- スクリーンショット: <撮る対象の画面と撮り方>
- 期待出力: <主要コマンド・API の fixture の置き場>（あれば）

## レビュー方針
- critical不変条件: <...>
- 検証境界: <...>
- エラーハンドリング方式: <...>
- 却下類型: <...>

## PJ固有ルール
- <PJ固有ルール。簡潔に>
```

オプションセクション（必要な場合のみ）:

- アーキテクチャ概要（簡潔に）
- 命名規則
- 禁止事項

## 書かない内容

- サブエージェント呼び出しの強制（「quality-checker / pr-reviewer を必ず呼び出せ」等）。user-level の `~/.claude/context/tool-claude-code.md`「委譲判断」と重複・矛盾するため
- Phase 0-5 の再定義。user-level の `context/workflow-rules.md` に任せる
- 「こまめに」「必ず」等の強制表現の多用。理由が書いてあれば足り、多用すると適用しすぎを招く

## 更新提案の書式

````markdown
## 更新提案

### CLAUDE.md
**現状:** XX行
**提案:** <上の雛形に沿った全文、または差分>

### コンテキスト除外（必要な場合のみ）
**提案:** 秘匿・不要パスを `.claude/settings.json` の `permissions.deny` に追加
```json
{ "permissions": { "deny": ["Read(secrets/**)", "Read(*.pem)"] } }
```

### .claude/rules/（パス固有ルールがある場合）
**提案:** 以下を作成
```yaml
---
paths:
  - "src/api/**/*.ts"
---
# API開発ルール
```

### 削除対象
- [ ] <不要ファイル1>（理由: ...）

### 移動対象
- [ ] <ファイル> → <移動先>（理由: ...）
````
