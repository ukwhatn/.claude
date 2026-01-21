# Claude review ガイド

## 概要

別セッションのClaude Code（`claude -p`）を使用して、計画・実装のレビューを実施する。
同一セッションではなく別セッションでレビューすることで、異なる視点からの分析が可能になる。

## 基本コマンド

```bash
# 初回（session_idを取得）
claude -p "<プロンプト>" --output-format json | jq -r '.session_id, .result'

# 2回目以降（セッション継続）
claude -p "<プロンプト>" --resume <session_id> --output-format json | jq -r '.result'
```

### 主要オプション

| オプション | 説明 |
|-----------|------|
| `-p, --print` | 非対話モード、結果を出力 |
| `--output-format json` | JSON形式で出力（session_id取得に必須） |
| `--model <model>` | モデル指定（sonnet/opus/haiku） |
| `--resume <session_id>` | 特定のセッションを再開 |

## レビュー用コマンド例

### 1. 計画レビュー（Phase 2）

**初回:**
```bash
claude -p "以下の計画をレビューしてください。
- 抜け漏れがないか
- リスクや懸念点
- より良いアプローチの提案

指摘がなければ「指摘なし」とだけ回答してください。

計画内容:
$(cat ${MEMORY_DIR}/memory/<task>/30_plan.md)" --output-format json | jq -r '.session_id, .result'
```

**2回目以降:**
```bash
claude -p "以下の改善を行いました:
- [改善内容1]
- [改善内容2]

再度レビューしてください。指摘がなければ「指摘なし」とだけ回答してください。" \
  --resume <session_id> --output-format json | jq -r '.result'
```

### 2. 実装レビュー（Phase 4）

**初回:**
```bash
# BASE_BRANCHはPJ CLAUDE.mdで定義された値を使用
claude -p "以下のコード変更をレビューしてください。
- バグや論理エラー
- セキュリティ上の問題
- パフォーマンス改善点
- ベストプラクティス違反

指摘がなければ「指摘なし」とだけ回答してください。

変更内容:
$(git diff $BASE_BRANCH)" --output-format json | jq -r '.session_id, .result'
```

**2回目以降:**
```bash
claude -p "以下の改善を行いました:
- [改善内容1]
- [改善内容2]

再度レビューしてください。指摘がなければ「指摘なし」とだけ回答してください。" \
  --resume <session_id> --output-format json | jq -r '.result'
```

### 3. PRレビュー

```bash
claude -p "以下のPRをレビューしてください。
- 変更の妥当性
- テストの十分性
- ドキュメントの更新必要性

指摘がなければ「指摘なし」とだけ回答してください。

PR diff:
$(gh pr diff <番号>)" --output-format json | jq -r '.session_id, .result'
```

## 出力形式

| 形式 | 説明 | 用途 |
|------|------|------|
| `json` | 構造化JSON（推奨） | session_id取得、スクリプト連携 |
| `text` | プレーンテキスト | 単発レビュー |
| `stream-json` | ストリーミングJSON | 長時間処理 |

### JSON出力の構造

```json
{
  "session_id": "uuid-string",
  "result": "レビュー結果テキスト",
  "usage": {
    "input_tokens": 1000,
    "output_tokens": 500
  }
}
```

### jqでの抽出例

```bash
# session_idとresultを取得
... | jq -r '.session_id, .result'

# resultのみ取得
... | jq -r '.result'

# session_idのみ取得（変数に保存用）
session_id=$(... | jq -r '.session_id')
```

## レビューループの流れ

1. **初回レビュー実行**
   - `claude -p`でレビュープロンプトを送信
   - `--output-format json`でsession_idを取得
   - 結果を確認

2. **指摘への対応**
   - 「絶対にやるべき」指摘は必ず修正
   - それ以外はやる/やらない判断
   - 不明点はAskUserQuestionで確認

3. **再レビュー（セッション継続）**
   - `--resume <session_id>`でセッション継続
   - 改善内容を伝えて再度レビューを依頼
   - 指摘がなくなるまで繰り返し

## モデル選択ガイド

| モデル | 特徴 | 推奨用途 |
|--------|------|----------|
| `sonnet` | バランス型（デフォルト） | 一般的なレビュー |
| `opus` | 高精度 | 複雑なアーキテクチャレビュー |
| `haiku` | 高速・軽量 | 軽微な変更のレビュー |

```bash
# Opusでレビュー
claude -p "..." --model opus --output-format json | jq -r '.session_id, .result'
```

## 注意事項

- `-p`モード（非対話モード）ではスキル（`/commit`等）は使用不可
- 大きなdiffはトークン制限に注意
- セッション継続は必ず`--resume <session_id>`を使用する
