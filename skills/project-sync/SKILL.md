---
name: project-sync
description: PJドキュメント同期。PJ CLAUDE.mdの更新依頼時やドキュメント整理依頼時に使用。user-level設定との整合性確認、ドキュメント分離原則の適用、不要ファイル削除を実施。
---

# PJドキュメント同期

## トリガー条件

- PJ CLAUDE.mdの更新を依頼された場合
- ドキュメント構造の整理を依頼された場合
- 「user-level CLAUDE.mdに合わせて」と指示された場合

## ドキュメント分離原則

| 対象 | 配置場所 | 用途 |
|------|---------|------|
| **人間向け** | README.md, docs/ | プロジェクト説明、API仕様、アーキテクチャ図 |
| **エージェント向け** | CLAUDE.md, .claude/context/ | AI向け指示、作業ルール |

## 実行手順

### 1. 現状把握

```bash
# PJ CLAUDE.mdの確認
cat CLAUDE.md 2>/dev/null || echo "CLAUDE.md not found"
wc -l CLAUDE.md 2>/dev/null

# ドキュメント構造の確認
ls -la .claude/ 2>/dev/null
ls -la docs/ 2>/dev/null

# user-level設定の確認
cat ~/.claude/CLAUDE.md
ls ~/.claude/context/
```

### 2. 差分分析

以下を確認:

| 項目 | 確認内容 |
|------|---------|
| CLAUDE.md行数 | 60行以下か |
| 変数定義 | MEMORY_DIR, BASE_BRANCH があるか |
| 品質チェック | lint/format/typecheck/test コマンドがあるか |
| @参照 | 詳細をcontext/に委譲しているか |
| 分離原則 | 人間向け/エージェント向けが分離されているか |

### 3. 更新提案の作成

```markdown
## 更新提案

### CLAUDE.md
**現状:** XX行
**提案:** 以下に簡素化

```markdown
# <PJ名>

## 変数
MEMORY_DIR=.local/
BASE_BRANCH=develop

## 品質チェック
```bash
npm run lint
npm run format
npm run typecheck
npm test
```

## 特記事項
- [PJ固有ルール]
```

### 削除対象
- [ ] <不要ファイル1>（理由: ...）

### 移動対象
- [ ] <ファイル> → <移動先>（理由: ...）

### 新規作成
- [ ] .claude/context/<name>.md（用途: ...）
```

### 4. ユーザー確認

AskUserQuestionで以下を確認:
1. 更新提案の承認
2. 削除対象の確認（誤削除防止）
3. PJ固有の追加要件

### 5. 実行

承認後、以下を実行:

1. CLAUDE.mdの更新（60行以下に）
2. 不要ファイルの削除
3. ファイルの移動・リネーム
4. .claude/context/の作成（必要な場合）

### 6. 検証

```bash
# 行数確認
wc -l CLAUDE.md

# 構造確認
ls -la .claude/

# @参照の動作確認（手動）
```

## CLAUDE.md設計原則

### 60行以下ルール
- 詳細は`@.claude/context/`に委譲
- Progressive Disclosure（段階的開示）を活用

### 必須セクション
```markdown
# <PJ名>

## 変数
MEMORY_DIR=<path>
BASE_BRANCH=<branch>

## 品質チェック
[コマンド一覧]

## 特記事項
[PJ固有ルール - 簡潔に]
```

### オプションセクション（必要な場合のみ）
- アーキテクチャ概要（簡潔に）
- 命名規則
- 禁止事項

## 不要ファイルの判断基準

| 判断 | 条件 |
|------|------|
| **削除** | 古いagent定義、重複ドキュメント、空ファイル |
| **移動** | エージェント向け内容がdocs/にある場合 → .claude/context/ |
| **統合** | 類似内容の複数ファイル → 1ファイルに |
| **保持** | 人間向けドキュメント（README, docs/）、PJ固有設定 |

## チェックリスト

- [ ] CLAUDE.mdが60行以下
- [ ] 変数（MEMORY_DIR, BASE_BRANCH）が定義済み
- [ ] 品質チェックコマンドが記載済み
- [ ] ドキュメント分離原則に従っている
- [ ] 不要ファイルが削除済み
- [ ] @参照が正しく設定済み
