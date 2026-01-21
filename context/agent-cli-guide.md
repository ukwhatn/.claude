# agent cli 使用ガイド

## 概要

agent cliのnon-interactive modeを使用して、別モデル（gpt-5.2-high）によるレビューを実施する。
Claude Codeとは異なる観点からの分析により、計画・実装の品質を向上させる。

**重要**: レビューは「指摘がなくなるまで修正→再レビューを繰り返す」ループで実施する。

## 基本コマンド

```bash
agent -p "<プロンプト>" --model gpt-5.2-high --output-format stream-json
```

### パラメータ

| パラメータ | 説明 |
|-----------|------|
| `-p, --print` | non-interactiveモード、結果を出力 |
| `--model <model>` | 使用モデル（gpt-5.2-high推奨） |
| `--output-format <format>` | 出力形式（json/text/stream-json） |
| `--resume <session_id>` | 前回セッションを継続 |
| `--list-models` | 利用可能モデル一覧 |

## レビューループの実施方法

すべてのレビューは以下のループで実施:

**初回**:
1. メモリディレクトリのフルパスを明示してagent cliでレビュー実行
2. `result`フィールドから指摘を抽出（`jq -r .result`）
3. `session_id`を記録

**2回目以降**（セッション継続）:
4. 「絶対にやるべき」指摘は必ず修正
5. それ以外の指摘はやる/やらない判断、または AskUserQuestion で確認
6. `--resume <session_id>`で継続し「改善したこと」を伝達
7. 修正すべき点がなくなるまで繰り返し

**終了条件**: 修正すべき点がなくなる（「指摘なし」または対応不要の指摘のみ）

## ユースケース

### 1. 計画レビュー（Phase 2）

```bash
agent -p "メモリディレクトリ /path/to/.local/memory/<task>/ の内容を読み、以下の実装計画をレビューしてください:
- 抜け漏れがないか
- リスクや懸念点
- より良いアプローチの提案

指摘がなければ「指摘なし」とだけ回答してください。

計画内容:
$(cat .local/memory/<task>/30_plan.md)" \
  --model gpt-5.2-high \
  --output-format stream-json
```

### 2. 実装レビュー（Phase 4）

```bash
# BASE_BRANCHはPJ CLAUDE.mdで定義された値を使用
agent -p "メモリディレクトリ /path/to/.local/memory/<task>/ の内容を読み、以下のコード変更をレビューしてください:
- バグや論理エラー
- セキュリティ上の問題
- パフォーマンス改善点
- ベストプラクティス違反

指摘がなければ「指摘なし」とだけ回答してください。

変更内容:
$(git diff $BASE_BRANCH)" \
  --model gpt-5.2-high \
  --output-format stream-json
```

### 3. PRレビュー

```bash
agent -p "以下のPRをレビューしてください:
- 変更の妥当性
- テストの十分性
- ドキュメントの更新必要性

指摘がなければ「指摘なし」とだけ回答してください。

PR diff:
$(gh pr diff <番号>)" \
  --model gpt-5.2-high \
  --output-format stream-json
```

### 4. セッション継続

```bash
agent --resume <session_id> -p "以下の改善を行いました:
- [改善内容1]
- [改善内容2]

再度レビューしてください。指摘がなければ「指摘なし」とだけ回答してください。" \
  --model gpt-5.2-high \
  --output-format stream-json
```

## 出力形式

### stream-json形式（推奨）

ストリーミング形式でJSONが出力される。最終行に結果が含まれる。

```bash
# 最終行から結果を抽出
agent -p "..." --model gpt-5.2-high --output-format stream-json | tail -1 | jq -r .result

# session_idの抽出
agent -p "..." --model gpt-5.2-high --output-format stream-json | tail -1 | jq -r .session_id
```

**NOTE:** `stream-json`は`json`より高速（長時間処理でタイムアウトしにくい）

### 結果の活用

1. `result`フィールドからレビュー内容を抽出
2. `session_id`を記録（2回目以降の`--resume`で使用）
3. 「指摘なし」でなければ修正を実施
4. 指摘事項をメモリディレクトリ（80_review.md）に記録
5. 修正後、`--resume`で再度レビューを実行
6. 「指摘なし」になるまで繰り返し
