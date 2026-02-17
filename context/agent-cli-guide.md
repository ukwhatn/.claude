# agent cli 使用ガイド

## 概要

agent cliのnon-interactive modeを使用して、別モデル（gpt-5.3-codex-high-fast）によるレビューを実施する。
Claude Codeとは異なる観点からの分析により、計画・実装の品質を向上させる。

**重要**: レビューは「指摘がなくなるまで修正→再レビューを繰り返す」ループで実施する。

## 基本コマンド

```bash
# 初回（session_idを取得）
agent -p "<プロンプト>" --trust --model gpt-5.3-codex-high-fast --output-format json 2>/dev/null | jq -r '.session_id, .result'

# 2回目以降（セッション継続）
agent -p "<プロンプト>" --resume <session_id> --trust --model gpt-5.3-codex-high-fast --output-format json 2>/dev/null | jq -r '.result'
```

### 主要オプション

| オプション | 説明 |
|-----------|------|
| `-p, --print` | 非対話モード、結果を出力 |
| `--trust` | **必須**。ワークスペース信頼を自動承認（省略するとインタラクティブ確認が発生しnon-interactiveモードで失敗する） |
| `--model <model>` | 使用モデル（gpt-5.3-codex-high-fast推奨） |
| `--output-format json` | JSON形式で出力（session_id取得に必須） |
| `--resume <session_id>` | 特定のセッションを再開 |

**CRITICAL: `--output-format stream-json` は使用禁止。バッファリング問題でハングする可能性がある。必ず `json` を使用すること。**

## CRITICAL: diff/ファイル内容の埋め込み禁止

**プロンプトに `$(git diff ...)` や `$(cat ...)` でdiff/ファイル内容を埋め込むことを禁止する。**

agentはツール（Bash等）を持っているため、自分でdiffやファイル内容を取得できる。
プロンプトには「何を取得してレビューすべきか」の指示のみ記載する。

### 理由
- 大きなdiffでトークン上限やコマンドライン長超過が発生する
- バイナリファイルが含まれるとプロンプトが壊れる
- agentが自律的に必要な範囲を判断して読める

### NG例
```bash
# 禁止: diffをプロンプトに埋め込み
agent -p "以下のdiffをレビューしてください。$(git diff main)" ...

# 禁止: ファイル内容をプロンプトに埋め込み
agent -p "以下の計画をレビューしてください。$(cat plan.md)" ...
```

### OK例
```bash
# OK: agentに自分でdiffを取得させる
agent -p "git diff main を実行してコード変更をレビューしてください。" ...

# OK: agentに自分でファイルを読ませる
agent -p "/path/to/plan.md を読んで計画をレビューしてください。" ...
```

## レビュー用コマンド例

### 1. 計画レビュー（Phase 2）

**初回:**
```bash
agent -p "このリポジトリの ${MEMORY_DIR}/memory/<task>/30_plan.md を読んで、計画をレビューしてください。
- 抜け漏れがないか
- リスクや懸念点
- より良いアプローチの提案

指摘がなければ「指摘なし」とだけ回答してください。" \
  --trust --model gpt-5.3-codex-high-fast \
  --output-format json 2>/dev/null | jq -r '.session_id, .result'
```

**2回目以降:**
```bash
agent -p "以下の改善を行いました:
- [改善内容1]
- [改善内容2]

再度レビューしてください。指摘がなければ「指摘なし」とだけ回答してください。" \
  --resume <session_id> --trust \
  --model gpt-5.3-codex-high-fast \
  --output-format json 2>/dev/null | jq -r '.result'
```

### 2. 実装レビュー（Phase 4）

**初回:**
```bash
# BASE_BRANCHはPJ CLAUDE.mdで定義された値を使用
agent -p "このリポジトリで git diff $BASE_BRANCH を実行して、コード変更をレビューしてください。
- バグや論理エラー
- セキュリティ上の問題
- パフォーマンス改善点
- ベストプラクティス違反

指摘がなければ「指摘なし」とだけ回答してください。" \
  --trust --model gpt-5.3-codex-high-fast \
  --output-format json 2>/dev/null | jq -r '.session_id, .result'
```

**2回目以降:**
```bash
agent -p "以下の改善を行いました:
- [改善内容1]
- [改善内容2]

再度レビューしてください。指摘がなければ「指摘なし」とだけ回答してください。" \
  --resume <session_id> --trust \
  --model gpt-5.3-codex-high-fast \
  --output-format json 2>/dev/null | jq -r '.result'
```

### 3. PRレビュー

```bash
agent -p "gh pr diff <番号> を実行して、PRの変更内容をレビューしてください。
- 変更の妥当性
- テストの十分性
- ドキュメントの更新必要性

指摘がなければ「指摘なし」とだけ回答してください。" \
  --trust --model gpt-5.3-codex-high-fast \
  --output-format json 2>/dev/null | jq -r '.session_id, .result'
```

## 出力形式

| 形式 | 説明 | 使用可否 |
|------|------|----------|
| `json` | 構造化JSON | **推奨** |
| `text` | プレーンテキスト | 使用可 |
| `stream-json` | ストリーミングJSON | **使用禁止** |

### JSON出力の構造

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 30000,
  "result": "レビュー結果テキスト",
  "session_id": "uuid-string",
  "request_id": "uuid-string"
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
   - `agent -p`でレビュープロンプトを送信
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
| `gpt-5.3-codex-high-fast` | 高精度+高速（デフォルト） | コードレビュー全般 |

```bash
# モデル一覧を確認
agent --list-models
```

## 注意事項

- `-p`モード（非対話モード）ではスキル（`/commit`等）は使用不可
- セッション継続は必ず`--resume <session_id>`を使用する
- **`--trust`は必須**（省略するとWorkspace Trust確認が発生し、non-interactiveモードで失敗する）
- **`--output-format stream-json`は使用禁止**（ハング問題のため）
- **プロンプトにdiff/ファイル内容を`$()`で埋め込むことは禁止**（トークン超過のため）

### CRITICAL: パイプ実行時のエラーハンドリング

`agent ... | jq` のようにパイプで繋ぐと、agent側のエラー（stderr）がjqのパースエラーに隠蔽される。

**ルール:**
1. **`2>/dev/null`でstderrを分離する**（基本コマンド例の通り）
2. **jqがパースエラーを返した場合、パイプを外して`agent`単体で再実行し、エラーメッセージを確認する**
3. **同じコマンドをjqの書式変更やプロンプト簡素化でリトライすることを禁止する** — jqパースエラーの原因は十中八九agent側のエラー出力であり、jq側の問題ではない
