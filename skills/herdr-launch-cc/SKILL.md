---
name: herdr-launch-cc
description: Herdrの指定workspaceに新しいtab（明示指定時はpane分割）を作り、fish -c "cc" でClaude Codeを起動してremote controlを有効化する。使用タイミング: (1) /herdr-launch-cc 実行時、(2) 「discordのworkspaceでccを立ち上げて」等、Herdr上でのClaude Code新規起動依頼時。境界: 既存pane・agentの確認や入力送信などの汎用Herdr操作は herdr スキル。HERDR_ENV=1 必須。
---

# Herdr Launch CC

Herdrの指定workspaceに新しいtab（明示指定時はpane分割）を作成し、`fish -c "cc"` でClaude Codeを起動し、remote controlを有効化して接続URLを報告する。

## 既存設定との関係

- **herdr スキル**: herdr CLIの構文・ID規約・状態モデル（idle/done等）の真実源。本スキルは起動フローの固定手順のみを規定する。コマンドの引数に迷ったら該当コマンドグループ（`herdr pane` 等、bareの `herdr` は実行しない）の出力に従う
- **worktree運用**: Herdr操作は読み書きともCLI経由でありコード編集を伴わないため、worktree不要の例外に該当する

## 前提チェック

```bash
test "${HERDR_ENV:-}" = 1
```

失敗したらHerdr外で動いている旨を伝えて停止する。

**完了基準**: `HERDR_ENV=1` を確認済み。

## Step 1: 配置先の確認

1. `herdr workspace list` で一覧を取得する
2. workspaceが未指定なら AskUserQuestion で確認する（一覧の label と workspace_id を選択肢にする）

配置方法のデフォルトは**新規tabの作成**。ユーザーが「paneを分割して」「隣に」等と明示した場合のみpane分割にする（配置方法は質問しない）。

**完了基準**: workspace_id が確定している。

## Step 2: tab / paneの作成

**新規tab（デフォルト）:**

```bash
herdr tab create --workspace <ws_id> --no-focus
```

JSON応答の `result.root_pane.pane_id` と `result.tab.tab_id` を読み取り、`herdr tab rename <tab_id> "cc"` と `herdr pane rename <pane_id> "cc"` でラベルを付ける。

**pane分割（明示指定時のみ）:**

1. `herdr pane list --workspace <ws_id>` と `herdr pane layout --pane <対象pane>` でactive tabのpane矩形を確認する
2. 最も大きいpaneを分割対象とし、幅広（width > height×2 目安）なら `--direction right`、縦長・狭幅なら `--direction down` を選ぶ
3. `herdr pane split <pane_id> --direction <right|down> --no-focus` を実行し、応答の `result.pane.pane_id` を読み取って `herdr pane rename <pane_id> "cc"` する

IDの推測・組み立ては禁止。必ずJSON応答から読む。

**完了基準**: 新pane_idをJSON応答から取得済み。

## Step 3: Claude Code起動

```bash
herdr pane run <pane_id> 'fish -c "cc"'
herdr wait agent-status <pane_id> --status idle --timeout 60000
```

waitがタイムアウト（exit 1）したら、`herdr pane get <pane_id>` と `herdr pane read <pane_id> --source visible --lines 40` で実際の画面を確認してから判断する（`blocked` は入力待ち、`unknown` は未検出）。

**完了基準**: `pane get` で `agent: claude`、`agent_status: idle` を確認済み。

## Step 4: remote control有効化

1. `herdr pane read <pane_id> --source visible --lines 40` で `remote-control is active` または `claude.ai/code/session_` の表示有無を確認する。あれば有効化済みなのでURLを控えてStep 5へ
2. 未有効なら送信し、URL行の出現を待つ:

```bash
herdr pane run <pane_id> "/rc"
herdr wait output <pane_id> --match "claude.ai/code/session_" --timeout 15000
```

3. waitの応答の `matched_line` からセッションURL（`https://claude.ai/code/session_...`）を控える
4. visibleを読み、「Remote Control」ダイアログ（Disconnect / Show QR code / Continue の選択肢）が表示されていたら、`❯` が Continue にあることを確認して `herdr pane send-keys <pane_id> enter` で閉じ、再度visibleでプロンプト（`❯`）復帰を確認する
5. waitがタイムアウトした場合はvisibleを読んで実画面で判断する。「Remote Controlが設定で無効」等を示す場合は、勝手に `/config` を操作せずユーザーに報告して指示を仰ぐ

**完了基準**: セッションURLを取得しプロンプト復帰を確認済み、または無効化状態をユーザーに報告済み。

## Step 5: 報告

workspace（label + ID）・新pane_id・remote controlのセッションURLを報告する。

## Gotchas

- `/rc` はClaude Code側で `/remote-control` に展開されて実行される
- `herdr pane run` はテキストとEnterを一括送信する。起動直後のTUIに送ると失われるため、必ず `idle` を待ってから送る
- bare `herdr` はTUIをattach/起動するため実行しない（discoveryはコマンドグループ出力で行う）
- 応答画面に「N MCP servers need authentication」警告が出ることがある。起動自体は成功なので、報告に含めるだけでよい
- `/rc` 実行後は「is active」の1行表示ではなく、URL・QRコード・Continue選択肢を持つ全画面ダイアログが出ることがある。待つ文字列は「remote-control is active」ではなく必ず `claude.ai/code/session_`（どちらの表示形式でもマッチする）にする
- ダイアログをContinueで閉じた後に「remote-control is active」の行は表示されない。有効化の確認はURL取得＋プロンプト復帰で行う（is active行を待つとタイムアウトする）
