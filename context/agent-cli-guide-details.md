# agent cli 使用ガイド（詳細: cursor・Codex 主体・pane・reviewer 分離・モデル）

Read when: `context/agent-cli-guide.md` 冒頭の条件に該当したとき（cursor で実行する / 実行主体が Codex / pane でループを回す / reviewer を別 agent に分ける / モデルを既定から変える）。プロンプト本文・打ち切り条件・Severity 判断・注意事項は本体が真実源で、ここには書かない。

## 目次

- 実行主体が Codex の場合
- cursor（`agent` / `cursor-agent`）
- pane でループを回す
- reviewer を別 agent に分ける（Claude Code）
- モデル選択

## 実行主体が Codex の場合

外部レビュー CLI は cursor（`agent`）または claude を使い、codex 自身での再帰レビューは行わない（別ベンダーの bias 独立性が目的のため）。

```bash
# 初回
claude -p "<プロンプト>" --output-format json | jq -r '.session_id, .result'
# 継続
claude -p "<プロンプト>" --resume <session_id> --output-format json | jq -r '.result'
```

## cursor（`agent` / `cursor-agent`）

codex が無い環境の fallback。コマンド名は環境で違うので `CURSOR_CLI="$(command -v cursor-agent || command -v agent)"` で解決し、以下の `agent` を読み替える。

```bash
# 初回（session_id を取得）
agent -p "<プロンプト>" --trust --model gpt-5.6-sol-medium --output-format json 2>/dev/null | jq -r '.session_id, .result'
# 2回目以降
agent -p "<プロンプト>" --resume <session_id> --trust --model gpt-5.6-sol-medium --output-format json 2>/dev/null | jq -r '.result'
```

| オプション | 説明 |
|---|---|
| `-p, --print` | 非対話モード |
| `--trust` | **必須**。省略するとワークスペース信頼の対話確認が出て non-interactive で失敗する |
| `--model <model>` | effort / speed を名前に含む合成 slug（例: `gpt-5.6-sol-medium`）。実在は `agent --list-models` で確認し、無ければ一覧で最も近い gpt-5.6-sol 系を使う |
| `--output-format json` | session_id の取得に必須。**`stream-json` はバッファリングでハングし得るので使わない** |
| `--resume <session_id>` | セッション継続 |

- effort 表記はモデル系列で揺れる（gpt-5.6-sol 系・gpt-5.4 以前・claude 系は `medium` / `xhigh`、gpt-5.5 系の xhigh 相当のみ `extra-high`）
- JSON 出力は `{"type":"result","subtype":"success","is_error":false,"result":"...","session_id":"..."}` の形
- `-p` モードではスキル（`/commit` 等）は使えない

## pane でループを回す

`codex exec` 直叩きは1〜2ラウンドで終える単発レビュー向け。**ラウンドが長引く見込み・進捗を画面で追いたい・指摘と修正のやり取りを lead のコンテキストから分離したい**ときは pane に切り替える（経路選択の一般原則は `context/herdr-delegation.md`「経路の選択」）。

1. `bin/herdr-delegate.sh --kind codex --keep` で起動する。**`--keep` は必須**（無いと完了時に tab が閉じ、次のラウンドを送れない）
2. 初回の指示書に本体「プロンプト」の本文をそのまま渡す
3. 2ラウンド目以降は `herdr agent prompt <name> "<次のプロンプト>"` で同じセッションへ送る（`--resume` 不要）
4. 各ラウンドの結果は別パスに出させ、収束したら `herdr tab close <tab_id>` で閉じる

codex は Claude Code のセッションではないため `SendMessage` は届かない。追加指示も `herdr agent prompt` で送る。モデル・枠の節約の判断軸は `context/herdr-delegation.md`「モデルの選択」。

## reviewer を別 agent に分ける（Claude Code）

Herdr 環境（`HERDR_ENV=1`）では前節の pane が既定。本節は Herdr 外、または reviewer を Claude Code 側の agent に残したい場合に使う。`name` を付けて spawn し、`SendMessage` で連携する。

spawn 指示テンプレート:

```
あなたはこのセッションの reviewer です。
外部 CLI（codex、無ければ cursor の agent）を Bash で実行し、結果を lead に報告する。
0. CLI 判定（command -v codex、無ければ command -v cursor-agent || command -v agent）。どちらも無ければ lead に報告して指示を仰ぐ（fable subagent を自分で立てない）
1. ~/.claude/context/agent-cli-guide.md を末尾まで読み、「基本コマンド」「プロンプト」に従って初回を実行する
2. 結果を Severity 分類付きで lead に SendMessage で報告する
3. lead の修正完了報告を受けたらセッションを継続して再レビューする
4. 同ガイド「レビューループ」の打ち切り条件を満たすまで繰り返す
```

reviewer は計画レビューから実装レビューまで存続させてよい。CLI のセッションは Phase ごとに新規に作るが、reviewer 自体は再利用してコードベースの理解を保つ。

## モデル選択

| CLI | 指定 | 用途 |
|---|---|---|
| codex | `--model gpt-5.6-sol -c model_reasoning_effort="medium"` | レビュー標準 |
| codex | `--model gpt-5.4` | 軽量・低コストの簡易チェック |
| cursor | `--model gpt-5.6-sol-medium`（合成 slug） | fallback 時の標準 |
| fable subagent | `Agent(model: "fable")` | 外部 CLI が両方使えないときの暫定（同一ベンダー） |

codex はモデル slug と reasoning effort を別に指定し、cursor は effort を slug に含める。両者を混同しない。
