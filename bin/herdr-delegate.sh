#!/usr/bin/env bash
# herdr pane へ作業を委譲する。tab 作成 → agent 起動 → 指示書の投入 → 完了待ち → 成果物の判定 → tab の片付け。
# 規定と使い方: ~/.claude/context/herdr-delegation.md
#
# 終了時は必ず1行 JSON を stdout に出す（SIGKILL 等の異常終了を除く）。

set -u

KIND=""
TASK=""
MODEL=""
NAME=""
LABEL=""
CWD="$PWD"
WORKSPACE="${HERDR_WORKSPACE_ID:-}"
STATE=""
RUN_ID=""
LEAD_NAME=""
LEAD_PANE="${HERDR_PANE_ID:-}"
WORK_TASK=""
TIMEOUT=1800000
START_TIMEOUT=120000
KEEP=0
OUTS=""        # 改行区切り
AGENT_ARGS=""  # 改行区切り

TAB_ID=""
PANE_ID=""
TAB_CLOSED="false"
OUT_STATES=""  # "path<TAB>state" の改行区切り

usage() {
  cat >&2 <<'USAGE'
usage: herdr-delegate.sh --kind <claude|codex> --task <指示書の絶対パス> [options]

  --model MODEL        claude: opus|sonnet|haiku|fable / codex: -m に渡す値
  --agent-arg VALUE    エージェントの argv に透過で渡す（複数回指定可）
                       ※ 承認のバイパスは既定で付く
                          claude: --dangerously-skip-permissions
                          codex:  --dangerously-bypass-approvals-and-sandbox
  --name NAME          agent 名（既定: delegate-<epoch>-<pid>-<乱数>）
  --label TEXT         tab のラベル（既定: --name の値）
  --cwd PATH           作業ディレクトリ（既定: $PWD）
  --workspace WS       herdr workspace（既定: $HERDR_WORKSPACE_ID）
  --out PATH           期待する成果物の絶対パス（複数回指定可）
  --state PATH         起動直後に識別子を書き出すファイル（--run-id と同時指定）
  --run-id ID          state に埋める識別子（呼び出し側が採番する）
  --lead-name NAME     委譲先が SendMessage で lead を呼ぶときの宛先名
                       （ListAgents に出る自分のセッション名。省略時は pane 経由の連絡だけ案内する）
  --timeout MS         完了待ちの上限（既定: 1800000）
  --start-timeout MS   起動と入力可能判定の上限（既定: 120000）
  --keep               完了しても tab を閉じない
USAGE
}

# 全ての終了はここを通す。$1=status $2=exit $3=reason(省略可)
finalize() {
  FIN_STATUS="$1" FIN_CODE="$2" FIN_REASON="${3:-}" \
  FIN_NAME="$NAME" FIN_KIND="$KIND" FIN_TAB="$TAB_ID" FIN_PANE="$PANE_ID" \
  FIN_CLOSED="$TAB_CLOSED" FIN_OUTS="$OUT_STATES" \
  python3 -c '
import json, os
outs = []
for line in os.environ.get("FIN_OUTS", "").split("\n"):
    if not line.strip():
        continue
    path, _, state = line.partition("\t")
    outs.append({"path": path, "state": state})
def orn(v):
    return v if v else None
print(json.dumps({
    "name": orn(os.environ.get("FIN_NAME")),
    "kind": orn(os.environ.get("FIN_KIND")),
    "tab_id": orn(os.environ.get("FIN_TAB")),
    "pane_id": orn(os.environ.get("FIN_PANE")),
    "status": os.environ["FIN_STATUS"],
    "reason": orn(os.environ.get("FIN_REASON")),
    "exit": int(os.environ["FIN_CODE"]),
    "out": outs,
    "tab_closed": os.environ.get("FIN_CLOSED") == "true",
}, ensure_ascii=False))
' 2>/dev/null || printf '{"status":"%s","exit":%s,"note":"json_emit_failed"}\n' "$1" "$2"
  exit "$2"
}

# JSON からドット区切りのパスの値を取り出す（stdin）
json_get() {
  python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
for key in sys.argv[1].split("."):
    if not isinstance(d, dict) or key not in d:
        sys.exit(1)
    d = d[key]
print(d)
' "$1" 2>/dev/null
}

# herdr を実行する。結果は $HERDR_OUT / $HERDR_ERR に入れる（コマンド置換で呼ぶとサブシェルに
# なって変数が親へ戻らないため、戻り値だけを見る形にしている）。
# herdr はエラー JSON を stderr に出すので、失敗の理由は $HERDR_ERR 側にある。
HERDR_OUT=""
HERDR_ERR=""
herdr_call() {
  local rc out_file err_file
  out_file="$(mktemp "${TMPDIR:-/tmp}/herdr-out.XXXXXX")"
  err_file="$(mktemp "${TMPDIR:-/tmp}/herdr-err.XXXXXX")"
  "$@" >"$out_file" 2>"$err_file"
  rc=$?
  HERDR_OUT="$(cat "$out_file" 2>/dev/null)"
  HERDR_ERR="$(cat "$err_file" 2>/dev/null)"
  rm -f "$out_file" "$err_file"
  [ $rc -ne 0 ] && return 1
  [ -z "$HERDR_OUT" ] && return 1
  printf '%s' "$HERDR_OUT" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
sys.exit(1 if "error" in d else 0)
' 2>/dev/null
}

# herdr の応答（stdout 優先、無ければ stderr）から値を取り出す
herdr_field() {
  local v
  v="$(printf '%s' "$HERDR_OUT" | json_get "$1")"
  [ -n "$v" ] || v="$(printf '%s' "$HERDR_ERR" | json_get "$1")"
  printf '%s' "$v"
}

is_positive_int() {
  case "$1" in
    ''|*[!0-9]*) return 1 ;;
    *) [ "$1" -gt 0 ] ;;
  esac
}

# --- 引数のパース ---
while [ $# -gt 0 ]; do
  case "$1" in
    --kind)          KIND="${2:-}"; shift 2 ;;
    --task)          TASK="${2:-}"; shift 2 ;;
    --model)         MODEL="${2:-}"; shift 2 ;;
    --agent-arg)     AGENT_ARGS="${AGENT_ARGS}${2:-}
"; shift 2 ;;
    --name)          NAME="${2:-}"; shift 2 ;;
    --label)         LABEL="${2:-}"; shift 2 ;;
    --cwd)           CWD="${2:-}"; shift 2 ;;
    --workspace)     WORKSPACE="${2:-}"; shift 2 ;;
    --out)           OUTS="${OUTS}${2:-}
"; shift 2 ;;
    --state)         STATE="${2:-}"; shift 2 ;;
    --run-id)        RUN_ID="${2:-}"; shift 2 ;;
    --lead-name)     LEAD_NAME="${2:-}"; shift 2 ;;
    --timeout)       TIMEOUT="${2:-}"; shift 2 ;;
    --start-timeout) START_TIMEOUT="${2:-}"; shift 2 ;;
    --keep)          KEEP=1; shift ;;
    -h|--help)       usage; exit 0 ;;
    *)               usage; NAME=""; finalize invalid_input 2 arg_invalid ;;
  esac
done

# --- 事前検証（tab を作る前に全部行う） ---
[ "${HERDR_ENV:-}" = "1" ] || finalize invalid_input 2 not_in_herdr
command -v herdr >/dev/null 2>&1 || finalize invalid_input 2 herdr_unavailable
command -v python3 >/dev/null 2>&1 || finalize invalid_input 2 python3_unavailable

case "$KIND" in
  claude|codex) ;;
  *) finalize invalid_input 2 arg_invalid ;;
esac
command -v "$KIND" >/dev/null 2>&1 || finalize invalid_input 2 agent_cli_unavailable

[ -n "$WORKSPACE" ] || finalize invalid_input 2 workspace_missing

case "$TASK" in
  /*) ;;
  *) finalize invalid_input 2 task_invalid ;;
esac
[ -f "$TASK" ] && [ -r "$TASK" ] || finalize invalid_input 2 task_invalid

[ -d "$CWD" ] || finalize invalid_input 2 arg_invalid
is_positive_int "$TIMEOUT" || finalize invalid_input 2 arg_invalid
is_positive_int "$START_TIMEOUT" || finalize invalid_input 2 arg_invalid

printf '%s' "$OUTS" | while IFS= read -r p; do
  [ -z "$p" ] && continue
  case "$p" in /*) ;; *) exit 9 ;; esac
done
[ $? -eq 9 ] && finalize invalid_input 2 arg_invalid

# --state と --run-id は同時指定
if [ -n "$STATE" ] || [ -n "$RUN_ID" ]; then
  [ -n "$STATE" ] && [ -n "$RUN_ID" ] || finalize invalid_input 2 arg_invalid
  case "$STATE" in /*) ;; *) finalize invalid_input 2 arg_invalid ;; esac
  state_dir="$(dirname "$STATE")"
  [ -d "$state_dir" ] && [ -w "$state_dir" ] || finalize invalid_input 2 arg_invalid
  # task / out と同一パスにしない（指示書の破壊・成果物の偽陽性を防ぐ）
  [ "$STATE" = "$TASK" ] && finalize invalid_input 2 arg_invalid
  printf '%s' "$OUTS" | grep -qxF "$STATE" && finalize invalid_input 2 arg_invalid
fi

[ -n "$NAME" ] || NAME="delegate-$(date +%s)-$$-$(od -An -N2 -tu2 /dev/urandom | tr -d ' ')"
[ -n "$LABEL" ] || LABEL="$NAME"

# --out の実行前スナップショット
OUT_BEFORE="$(OB_LIST="$OUTS" python3 -c '
import os
for path in os.environ.get("OB_LIST", "").split("\n"):
    if not path.strip():
        continue
    try:
        print("%s\t%d" % (path, os.stat(path).st_mtime_ns))
    except OSError:
        print("%s\t-1" % path)
')"

# --- 指示書に委譲ヘッダを前置きする（連絡経路を毎回渡すため） ---
WORK_TASK="$(mktemp "${TMPDIR:-/tmp}/herdr-delegate.XXXXXX")" || finalize invalid_input 2 arg_invalid
cat > "$WORK_TASK" <<'HEADER'
# 委譲の前提

あなたは lead から作業を委譲された実行担当です。**lead とは双方向にやり取りできます。**

この節は委譲スクリプトが機械的に前置きする定型文です。**この節と下のタスク本文が食い違ったら、タスク本文を優先してください。** その食い違いだけを理由に lead へ問い合わせる必要はありません。

## 判断に迷ったら lead に聞く

次のいずれかに当たったら、**推測で進めずに作業を止め、lead に連絡して返答を待ってください**。

- 指示書の前提が、実際のコード・ファイル・データと食い違っている
- 指示書に書かれていない判断が必要になった（スコープの変更・設計の選択・破壊的操作）
- 指示書が指す入力（ファイル・パス・URL）が存在しない、または読めない
- 指示書の想定より大幅に広い変更が必要だと分かった
- 指示書の記述が互いに矛盾している

連絡には次を必ず含めてください。

1. 何が食い違っているか（観測した事実。ファイルパスと行、コマンドの出力）
2. 進め方の選択肢を2つ以上
3. あなたの推奨と、その理由

指示書どおりに進められる範囲は、いちいち確認せずに進めてください。連絡するのは上の5つに当たったときです。

### 連絡の方法
HEADER

{
  echo
  if [ -n "$LEAD_NAME" ]; then
    printf 'SendMessage ツールで `to: "%s"` に送る。\n\n' "$LEAD_NAME"
  fi
  if [ -n "$LEAD_PANE" ]; then
    if [ -n "$LEAD_NAME" ]; then
      echo 'SendMessage が使えない場合は、Bash で次を実行する。'
    else
      echo 'Bash で次を実行する。'
    fi
    echo
    echo '```bash'
    printf 'herdr agent prompt "%s" "<メッセージ本文>"\n' "$LEAD_PANE"
    echo '```'
    echo
  fi
  cat <<'HEADER2'
連絡したら、返答が届くまで待ってください。返答は同じ画面に届きます。

## 完了したら

成果物を書き終えたら応答を終了してください。lead はファイルを読んで結果を受け取ります。タスク本文が成果物のパスを指定している場合、**それを書かずに応答を終えると lead 側では失敗として扱われます**。

lead に質問を投げるときも、応答を終えた時点で lead 側は「成果物なし」の状態を見ます。lead はそこで質問の有無を確認するので、質問は必ず上記の方法で送ってから応答を終えてください。

---

HEADER2
  cat "$TASK"
} >> "$WORK_TASK" || finalize invalid_input 2 arg_invalid

# --- 1. tab の作成 ---
herdr_call herdr tab create --workspace "$WORKSPACE" --cwd "$CWD" --label "$LABEL" --no-focus \
  || finalize create_failed 6
TAB_ID="$(herdr_field result.tab.tab_id)"
PANE_ID="$(herdr_field result.root_pane.pane_id)"
[ -n "$TAB_ID" ] && [ -n "$PANE_ID" ] || finalize create_failed 6

herdr pane rename "$PANE_ID" "$LABEL" >/dev/null 2>&1

# --- 2. agent の起動 ---
# 承認プロンプトで止まると委譲が進まないため、確認のバイパスを既定にする。
# 委譲先は lead が書いた指示書の範囲で動く前提。
START_CMD=(herdr agent start "$NAME" --kind "$KIND" --pane "$PANE_ID" --timeout "$START_TIMEOUT" --)
if [ "$KIND" = "codex" ]; then
  [ -n "$MODEL" ] && START_CMD=("${START_CMD[@]}" -m "$MODEL")
  START_CMD=("${START_CMD[@]}" --dangerously-bypass-approvals-and-sandbox)
else
  [ -n "$MODEL" ] && START_CMD=("${START_CMD[@]}" --model "$MODEL")
  START_CMD=("${START_CMD[@]}" --dangerously-skip-permissions)
fi
old_ifs="$IFS"; IFS='
'
for a in $AGENT_ARGS; do
  [ -n "$a" ] && START_CMD=("${START_CMD[@]}" "$a")
done
IFS="$old_ifs"

# 起動時ダイアログで止まっていると herdr は agent_not_ready を返す。
# これは失敗ではなく「画面を見て分類すべき状態」なので、判定ループへ回す。
START_BLOCKED=0
if ! herdr_call "${START_CMD[@]}"; then
  err_code="$(herdr_field error.code)"
  [ "$err_code" = "agent_not_ready" ] || finalize start_failed 6
  START_BLOCKED=1
fi

# --- 3. state の書き出し（tab_id / pane_id が確定した直後） ---
if [ -n "$STATE" ]; then
  ST_RUN="$RUN_ID" ST_NAME="$NAME" ST_TAB="$TAB_ID" ST_PANE="$PANE_ID" \
  ST_TASK="$TASK" ST_OUTS="$OUTS" ST_PATH="$STATE" \
  python3 -c '
import json, os, time
outs = [p for p in os.environ.get("ST_OUTS", "").split("\n") if p.strip()]
data = {
    "run_id": os.environ["ST_RUN"], "name": os.environ["ST_NAME"],
    "tab_id": os.environ["ST_TAB"], "pane_id": os.environ["ST_PANE"],
    "task": os.environ["ST_TASK"], "out": outs,
    "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
}
path = os.environ["ST_PATH"]
tmp = path + ".tmp"
with open(tmp, "w") as f:
    json.dump(data, f, ensure_ascii=False)
os.replace(tmp, path)
' 2>/dev/null || finalize start_failed 6
fi

# --- 4. 入力可能状態の判定ループ ---
screen_has() {
  case "$1" in
    *"$2"*) return 0 ;;
  esac
  return 1
}

# 選択待ちのモーダルが出ているか（"Press enter to continue" が選択待ちの目印）。
# codex の更新通知は選択肢を伴わないバナーとしても出るため、文字列だけでは判別できない。
is_modal() {
  screen_has "$1" "Press enter to continue"
}

is_ready() {
  local s="$1" st
  is_modal "$s" && return 1
  if [ "$KIND" = "codex" ]; then
    screen_has "$s" "/model to change" && return 0
    screen_has "$s" "Ask Codex" && return 0
    return 1
  fi
  # 起動がブロックされていた場合は agent が未登録で status を引けないので、画面だけで判定する
  [ "$START_BLOCKED" -eq 1 ] && return 0
  # claude は起動時モーダルを出さないため、agent_status が idle であることを条件にする
  st="$(herdr pane get "$PANE_ID" 2>/dev/null | json_get result.pane.agent_status)"
  [ "$st" = "idle" ] || [ "$st" = "done" ]
}

deadline=$(( $(date +%s) + START_TIMEOUT / 1000 + 1 ))
update_handled=0
ready=0
while [ "$(date +%s)" -lt "$deadline" ]; do
  screen="$(herdr pane read "$PANE_ID" --source visible --lines 40 2>/dev/null)"
  # 入力を受け付けられるなら、通知バナーが残っていても先へ進む
  if is_ready "$screen"; then
    ready=1
    break
  fi
  if is_modal "$screen"; then
    if screen_has "$screen" "Do you trust the contents"; then
      finalize blocked_trust 3
    fi
    if screen_has "$screen" "Update available!"; then
      if [ "$update_handled" -eq 1 ]; then
        finalize blocked_unknown 3   # 処理後も選択待ちのまま。再送しない
      fi
      herdr pane send-keys "$PANE_ID" Down Down Enter >/dev/null 2>&1 || finalize blocked_unknown 3
      update_handled=1
      sleep 1.5
      continue
    fi
    finalize blocked_unknown 3   # 未知のモーダルは自動操作しない
  fi
  sleep 1.5
done
[ "$ready" -eq 1 ] || finalize blocked_unknown 3

# ブロックを抜けた場合は agent 名がまだ登録されていないので、ここで登録し直す
if [ "$START_BLOCKED" -eq 1 ]; then
  herdr_call "${START_CMD[@]}" || finalize start_failed 6
fi

# --- 5. 指示書の投入と完了待ち ---
herdr_call herdr agent prompt "$NAME" \
  "指示書 $WORK_TASK を読み、そこに書かれた作業だけを実行してください。" \
  --wait --until "done" --until idle --timeout "$TIMEOUT" >/dev/null
prompt_rc=$?
if [ $prompt_rc -ne 0 ]; then
  # タイムアウトか、それ以外の失敗かを agent の状態で切り分ける
  st="$(herdr pane get "$PANE_ID" 2>/dev/null | json_get result.pane.agent_status)"
  if [ "$st" = "working" ] || [ "$st" = "blocked" ]; then
    finalize timeout 5
  fi
  finalize prompt_failed 6
fi

# --- 6. 成果物の判定 ---
if [ -n "$OUTS" ]; then
  OUT_STATES="$(OA_LIST="$OUTS" OA_BEFORE="$OUT_BEFORE" python3 -c '
import os
before = {}
for line in os.environ.get("OA_BEFORE", "").split("\n"):
    if not line.strip():
        continue
    path, _, mtime = line.partition("\t")
    before[path] = int(mtime)
for path in os.environ.get("OA_LIST", "").split("\n"):
    if not path.strip():
        continue
    prev = before.get(path, -1)
    try:
        now = os.stat(path).st_mtime_ns
    except OSError:
        print("%s\tabsent" % path)
        continue
    if prev == -1:
        print("%s\tcreated" % path)
    elif now > prev:
        print("%s\tupdated" % path)
    else:
        print("%s\tunchanged" % path)
')"
  OS_LIST="$OUT_STATES" python3 -c '
import os, sys
for line in os.environ.get("OS_LIST", "").split("\n"):
    if not line.strip():
        continue
    if line.rsplit("\t", 1)[-1] in ("absent", "unchanged"):
        sys.exit(1)
' 2>/dev/null || finalize missing_output 4
fi

# --- 7. 片付け ---
if [ "$KEEP" -eq 0 ]; then
  if herdr_call herdr tab close "$TAB_ID"; then
    TAB_CLOSED="true"
  else
    finalize done_close_failed 7
  fi
fi

rm -f "$WORK_TASK"   # 失敗時は残す（何を渡したかが調査材料になる）
finalize "done" 0
