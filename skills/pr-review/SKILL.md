---
name: pr-review
description: PRレビュー。PR番号・URL・ブランチ名・Slackリンク等を添えてPRの「レビュー」を依頼された時に使用（PRのレビュー依頼ではビルトインの/reviewでなく本スキルを使う。ローカル未コミット変更のレビュー→/code-review、自ブランチの提出前チェック→self-review、特定レビューコメントへの対応→pr-comment、PRの状態確認・PR作成相談では使わない）。Claude Codeと外部CLI（cursor agent / codex）のマルチモデルレビューでCritical/High/Medium分類の指摘を報告。
---

# PRレビュー

## トリガー条件

- PRのレビューを依頼された場合（「レビューして」「見ておいて」等）
- 対象はPR番号・URL・ブランチ名・Slack/Confluenceリンクのいずれでも指定され得る
- 非トリガー: PRのCI状態確認、マージ可否の事務確認、PR作成の相談

## 実行手順

### 0. 入力の正規化（対象PRの特定）

PR番号/URL以外の形式で依頼された場合、まず対象PRを特定する:

- **Slackリンク**: Slack MCPでスレッドを読み、本文・返信からPR URLを抽出
- **Confluenceリンク**: ページを取得し、関連PRリンクを抽出
- **ブランチ名のみ**: `gh pr list --head <branch>` でPRを特定
- 複数PRが見つかった場合や特定できない場合は、推測せずユーザーに確認

### 1. PR情報の取得

```bash
# PR詳細を取得
gh pr view <番号> --json title,body,author,headRefName,baseRefName,files

# diffを確認（必要に応じて）
gh pr diff <番号>
```

### 2. checkout / worktree の判断

| ケース | 対応 |
|-------|------|
| diff読解 + `git grep`/`rg` での静的確認で足りる | checkout不要（現在のブランチのまま） |
| ビルド・テスト実行・型チェック等の動的検証が必要 | PJのworktree手段でPR headをcheckout（PJ CLAUDE.mdに定義された手段を使用） |

**注意**: checkoutを省略した場合でも、Step 4の「削除・リネームの残存確認」は必ず全リポジトリ検索で実施する（diffに現れないファイルの見落とし防止）。その際、現在のローカルツリーではなく**PR headのツリーを検索対象にする**こと:

```bash
git fetch origin pull/<番号>/head
git grep -n "<identifier>" FETCH_HEAD
```

### 3. PJルールの確認

CLAUDE.mdを読み、以下を把握:
- アーキテクチャルール
- 命名規則
- コーディング規約

### 4. Claude Codeによるレビュー

変更された各ファイルについて:
1. Readツールでファイル全体を読む（diffだけでなく）
2. 既存パターンとの整合性を確認
3. 問題点を特定
4. **削除・リネームの残存確認（必須）**: diffで削除・リネームされた識別子（メソッド名・クラス名・定数・env key・docker service名・キュー名・設定キー等）を `git grep` / `rg` で**PR headのツリー全体**から検索する（checkout済みならそのツリー、未checkoutなら Step 2 の `git grep <pattern> FETCH_HEAD` 方式）。検索対象にはコードだけでなく config / docker-compose / .env / CI定義 / docs を含める。残存があればCriticalに昇格（過去実績: diffのみの確認でdocker-compose 2ファイルのキュー定義残存を見落とし）

### 5. 外部CLIによるレビュー（cursor優先 / codex fallback）

別モデルの観点を追加。**cursorの`agent`を優先し、無い環境ではcodexにfallback**（CLI判定: @context/agent-cli-guide.md「使用するCLIの選択」）。プロンプト本文は両CLI共通。

```bash
# cursor優先
agent -p "gh pr diff <番号> を実行してPR #<番号> の変更内容をレビューしてください。
- コードの品質（バグ、セキュリティ、パフォーマンス）
- 設計の妥当性
- テストの十分性
- ドキュメントの必要性

PR情報:
タイトル: <タイトル>
ブランチ: <ブランチ>

指摘がなければ「指摘なし」とだけ回答してください。" \
  --trust --model gpt-5.5-high-fast \
  --output-format json 2>/dev/null | jq -r '.session_id, .result'

# codex fallback（同じプロンプトを渡す）
codex exec --model gpt-5.4 -c model_reasoning_effort="high" --json "<上と同じプロンプト>" 2>/dev/null \
  | jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'
```

### 6. 結果の統合

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

## agent（外部CLI）による指摘

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
