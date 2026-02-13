---
name: pr-review
description: PRレビュー。PR番号・ブランチ名指定時またはレビュー依頼時に使用。Claude CodeとGPT-5.3-Codex-High-FastのマルチモデルレビューでCritical/High/Medium分類の指摘を報告。
---

# PRレビュー

## トリガー条件

- PRレビューを依頼された場合
- PR番号またはブランチ名が指定された場合

## 実行手順

### 1. PR情報の取得

```bash
# PR詳細を取得
gh pr view <番号> --json title,body,author,headRefName,baseRefName,files

# diffを確認（必要に応じて）
gh pr diff <番号>
```

### 2. PJルールの確認

CLAUDE.mdを読み、以下を把握:
- アーキテクチャルール
- 命名規則
- コーディング規約

### 3. Claude Codeによるレビュー

変更された各ファイルについて:
1. Readツールでファイル全体を読む（diffだけでなく）
2. 既存パターンとの整合性を確認
3. 問題点を特定

### 4. agent cliによるレビュー

別モデルの観点を追加。

```bash
agent -p "gh pr diff <番号> を実行してPR #<番号> の変更内容をレビューしてください。
- コードの品質（バグ、セキュリティ、パフォーマンス）
- 設計の妥当性
- テストの十分性
- ドキュメントの必要性

PR情報:
タイトル: <タイトル>
ブランチ: <ブランチ>

指摘がなければ「指摘なし」とだけ回答してください。" \
  --model gpt-5.3-codex-high-fast \
  --output-format json | jq -r '.session_id, .result'
```

### 5. 結果の統合

Claude Codeとagentの両方の指摘を統合し、以下の形式でレポート:

```markdown
# PRレビュー: #<番号>

## 対象
- PR: #<番号> - <タイトル>
- ブランチ: <ブランチ> → <ベース>

## Claude Codeによる指摘

### Critical
- [指摘内容]

### High
- [指摘内容]

## agent (gpt-5.3-codex-high-fast) による指摘

### Critical
- [指摘内容]

### High
- [指摘内容]

## 統合サマリ

| 観点 | Claude Code | agent | 統合判断 |
|------|------------|--------|---------|
| セキュリティ | OK | OK | OK |
| パフォーマンス | 指摘あり | OK | 要確認 |

## 推奨アクション
1. [アクション1]
2. [アクション2]

## マージ推奨: [Yes/No/条件付き]
```

## 問題の分類

| 分類 | 説明 | 対応 |
|-----|------|------|
| Critical | バグ、セキュリティ、破壊的変更 | マージ前に必須修正 |
| High | アーキテクチャ違反、テスト不足 | 強く推奨 |
| Medium | 命名、コメント | 改善推奨 |
| Good | 良い実装 | 賞賛 |
