<!--
雛形の使い方（写した後にこのコメントごと消す）:
- 登録の前に、表とプロンプトの `{{...}}` を全部埋める
- 登録したら schedule_list の内容でこの表を書き直す（定期起動の番号・常設タスクの番号は登録してから決まる）
- プロンプトの「やること」は RUNBOOK の Step の見出しに合わせる。使わないソースの行は消す
-->

# 定期起動の登録内容（taskboard）

| 項目 | 値 |
|---|---|
| 定期起動 | `{{SCHEDULE_NAME}}`（`schedule_list` で確認） |
| 常設タスク | {{STANDING_TASK}}（各回のセッションはここに結ばれる） |
| 規則 | cron `{{CRON}}`（マシンのローカル時刻） |
| cwd | `{{CWD}}` |
| agent | claude（`--dangerously-skip-permissions --model {{MODEL}} --effort {{EFFORT}}`） |
| overlap | skip（前回が動いていればその回は記録だけ残して飛ばす。2回分が同時に state.json を書かないように） |

変更は MCP の `schedule_update`（cron・prompt・有効 / 停止、常設タスクの付け替えは `task_id`）か、アプリのサイドバーの「定期起動」で行う。手順を変えるときはプロンプトではなく RUNBOOK.md を編集する。

## prompt

```
{{JOB_DIR}}/RUNBOOK.md を読み、そこに書かれた手順で1巡だけ実行してください。

これは定期的に動く無人実行です。前回セッションの記憶はありません。引き継ぐ状態は {{JOB_DIR}}/state.json だけです。答える人はその場にいません。

やること（詳細は RUNBOOK.md に全部書いてあります）:
1. state.json を読み、前回成功時刻からの差分範囲を決める
2. {{INSTRUCTION_SOURCE}} にある自分の発言を、{{JOB_NAME}} への指示として読んで実行する
3. taskboard の現状（{{TASKBOARD_CLI}} debug state）と、{{SOURCES}} を差分で巡回する
4. taskboard を MCP（task_create / task_update）で更新する。新規起票と、証拠のある列の「前進」まで。PR の状態による前進は daemon が行うので追わない
5. 前回通知から変化があれば通知 Webhook に1通だけ送る。前回と同じ内容しか無いなら送らない（巡回で何か作業をした場合でも、伝える内容が前回と同じなら送らない）
6. state.json と log/ を更新する

RUNBOOK より優先される絶対条件（RUNBOOK が読めなくてもこれは守ること）:
- 外部サービスへ書き込まない。コメント・レビュー・PR 操作・メッセージ送信・メール送信はすべて禁止。外への出力は通知 Webhook（notify.curl）への curl だけ。例外は RUNBOOK が明示的に許可した書き戻しだけで、RUNBOOK が読めないときは例外も無い
- 完了・見送りなどの終端の列へ自分の判断で移さない。通知して指示を待つ（ユーザーの指示があれば実行してよい）。列を後退させない
- taskboard の task_create は必ず link_session: false で呼ぶ。タスク削除・session_start・session_prompt・schedule_*・doc_publish・ask_user・review_request・他タスクの work_* は使わない。常設タスクの列と作業項目は動かさない
- git 操作とコード変更をしない。書き込んでよいのは {{JOB_DIR}}/ の下だけ
- 会議の文字起こしやメール本文を通知に貼らない。要約と参照先だけにする
- Webhook URL・トークンを表示しない・コマンドラインに載せない
- timeout コマンドは macOS の標準に無い。使わない

RUNBOOK.md が読めなかった場合は、何も変更せず次の1通だけ投げて終了してください:
jq -n --arg m "{{JOB_NAME}}: RUNBOOK.md を読めなかったため実行を中止しました" '{"{{NOTIFY_FIELD}}": $m}' | curl -s -K {{JOB_DIR}}/notify.curl -X POST -H 'Content-Type: application/json' -d @-
（宛先 URL は notify.curl の中にだけあります。中身を表示せず、コマンドラインに URL を足さないこと）

チャットへの出力は最後に1〜3行の結果だけで構いません。
```
