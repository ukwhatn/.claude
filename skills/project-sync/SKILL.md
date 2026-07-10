---
name: project-sync
description: PJドキュメント同期。PJ CLAUDE.mdの更新依頼時、ドキュメント整理依頼時、およびコード変更後のドキュメント同期（npm script/環境変数/API追加のCLAUDE.md・README・API仕様への反映）依頼時に使用。user-level設定との整合性確認、ドキュメント分離原則の適用、不要ファイル削除を実施。
---

# PJドキュメント同期

## トリガー条件

- PJ CLAUDE.mdの更新を依頼された場合
- ドキュメント構造の整理を依頼された場合
- 「user-level CLAUDE.md / AGENTS.md に合わせて」と指示された場合
- コード変更後にドキュメント更新が必要な場合（npm script追加・環境変数追加・APIエンドポイント追加/変更・アーキテクチャ変更を検出した場合）

## コード変更起点のドキュメント同期（旧documentationスキル統合）

コード変更後の依頼では、フル同期でなく変更起点の差分同期を行う:

1. **変更内容の確認**: `git diff <base-branch> --name-only` と `git diff <base-branch>`
2. **更新対象のマッピング**:

| カテゴリ | 例 | 更新対象 |
|---------|-----|---------|
| コマンド変更 | npm script追加 | CLAUDE.md, README.md |
| API変更 | エンドポイント追加 | API仕様書 |
| 設定変更 | 環境変数追加 | README.md |
| アーキテクチャ変更 | 新規レイヤー | CLAUDE.md |

3. **更新不要の判断**: 内部実装のみの変更・テストコードのみの変更・機能変更のないリファクタリングは更新不要
4. 更新提案を提示し、承認後に反映

## ドキュメント分離原則

| 対象 | 配置場所 | 用途 |
|------|---------|------|
| **人間向け** | README.md, docs/ | プロジェクト説明、API仕様、アーキテクチャ図 |
| **エージェント向け** | CLAUDE.md, .claude/context/, .claude/rules/ | AI向け指示、作業ルール |

## 実行手順

### 1. 現状把握

```bash
# PJ CLAUDE.mdの確認
cat CLAUDE.md 2>/dev/null || echo "CLAUDE.md not found"
wc -l CLAUDE.md 2>/dev/null

# ドキュメント構造の確認
ls -la .claude/ 2>/dev/null
ls -la .claude/rules/ 2>/dev/null
ls -la docs/ 2>/dev/null

# コンテキスト除外設定の確認（permissions.deny の Read ルール / claudeMdExcludes）
cat .claude/settings.json 2>/dev/null || echo ".claude/settings.json not found"

# user-level設定の確認（実体はAGENTS.md。CLAUDE.mdは互換symlink）
cat ~/.claude/AGENTS.md
ls ~/.claude/context/
```

### 2. 差分分析

以下を確認:

| 項目 | 確認内容 |
|------|---------|
| CLAUDE.mdのサイズ | 肥大せず簡潔か（@context/claude-customization-guide.md §3 参照） |
| 変数定義 | MEMORY_DIR, BASE_BRANCH があるか |
| 品質チェック | lint/format/typecheck/test コマンドがあるか |
| 検証方針 | テスト/E2E/スクショ/期待出力の指針があるか |
| @参照 | 詳細をcontext/に委譲しているか |
| 分離原則 | 人間向け/エージェント向けが分離されているか |
| コンテキスト除外 | 秘匿・不要パスがpermissions.denyのReadルールで除外されているか（.claudeignoreは公式機能に存在しない。残存していれば削除提案） |
| .claude/rules/ | パス固有ルールが活用されているか |
| **user-level設定との重複** | 「サブエージェント呼び出し時の追加情報」「Agent Teams必須」等、user-level AGENTS.md/context/に既にある内容が重複していないか |
| **過度な指示** | 「こまめに」「必ず」「逐次」等の過度な強制表現がないか（Opus 4.7 自律実行ベストプラクティス参照） |

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

## 検証方針
- テストコード: <test command>
- E2Eテスト: <e2e command>（あれば）
- スクリーンショット: docs/screenshots/ に変更前後を保存
- 期待出力: tests/fixtures/ 等に主要コマンド/APIのfixture
- Stop Hook: 必要なら .claude/settings.json で設定

## PJ固有ルール
- [PJ固有ルール - サブエージェント呼び出しの強制は記載しない]
```

### コンテキスト除外（必要な場合のみ）
**提案:** 秘匿・不要パスを `.claude/settings.json` の `permissions.deny` に追加
```json
{ "permissions": { "deny": ["Read(secrets/**)", "Read(*.pem)"] } }
```
（`.claudeignore`は公式機能に存在しない。残存していれば削除を提案する）

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
```

### 4. ユーザー確認

ユーザーに選択肢を提示して以下を確認（Claude Code: AskUserQuestion）:
1. 更新提案の承認
2. 削除対象の確認（誤削除防止）
3. PJ固有の追加要件

### 5. 実行

承認後、以下を実行:

1. CLAUDE.mdの更新（肥大させず簡潔に。@context/claude-customization-guide.md §3 参照）
2. コンテキスト除外設定の更新（必要な場合。permissions.denyのReadルール）
3. .claude/rules/の作成（必要な場合）
4. 不要ファイルの削除
5. ファイルの移動・リネーム
6. .claude/context/の作成（必要な場合）

### 6. 検証

```bash
# 行数確認
wc -l CLAUDE.md

# 構造確認
ls -la .claude/
```

## CLAUDE.md設計原則

### サイズ・記述の原則
- CLAUDE.md のサイズ・強調・命令形・理由付け等の設計原則は @context/claude-customization-guide.md §3 に従う（公式目標は1ファイル200行未満。肥大させず、詳細は `@.claude/context/` へ委譲する）

### 必須セクション
```markdown
# <PJ名>

## 変数
MEMORY_DIR=<path>
BASE_BRANCH=<branch>

## 品質チェック
[コマンド一覧]

## 検証方針
[テスト/E2E/スクショ/期待出力の指針]

## PJ固有ルール
[PJ固有ルール - 簡潔に。サブエージェント呼び出しの強制は記載しない]
```

### オプションセクション（必要な場合のみ）
- アーキテクチャ概要（簡潔に）
- 命名規則
- 禁止事項

### 記載してはいけない内容
- **サブエージェント呼び出しの強制** (`quality-checker / pr-reviewer 等を必ず呼び出せ` 等): user-level の `~/.claude/context/tool-claude-code.md` 「Agent Teams 発動条件」と重複・矛盾するため
- **Phase 0-5 の重複定義**: user-level の workflow-rules.md に委譲
- **過度な強制表現** (`こまめに`、`必ず`、`絶対に` 等の多用): Opus 4.7 の自律実行前提に反する

## 不要ファイルの判断基準

| 判断 | 条件 |
|------|------|
| **削除** | 古いagent定義、重複ドキュメント、空ファイル、user-level重複指示（サブエージェント呼び出しの追加情報等） |
| **移動** | エージェント向け内容がdocs/にある場合 → .claude/context/ |
| **統合** | 類似内容の複数ファイル → 1ファイルに |
| **保持** | 人間向けドキュメント（README, docs/）、PJ固有設定 |

## チェックリスト

- [ ] CLAUDE.mdが肥大せず簡潔（@context/claude-customization-guide.md §3 準拠）
- [ ] 変数（MEMORY_DIR, BASE_BRANCH）が定義済み
- [ ] 品質チェックコマンドが記載済み
- [ ] 検証方針セクションがある（テスト/E2E/スクショ/期待出力）
- [ ] ドキュメント分離原則に従っている
- [ ] 不要ファイルが削除済み
- [ ] @参照が正しく設定済み
- [ ] コンテキスト除外（必要な場合のpermissions.deny Readルール）を確認済み
- [ ] .claude/rules/が活用されている（パス固有ルールがある場合）
- [ ] user-level設定との重複指示がない
- [ ] 「こまめに」「必ず」等の過度な強制表現がない
