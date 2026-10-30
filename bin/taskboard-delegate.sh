#!/usr/bin/env bash
# taskboard の会話（daemon が stream-json で動かす Claude Code）へ作業を委譲する。
# 指示書に委譲ヘッダを前置きして一時ファイルに置き、会話を起こして最初の発言で読ませる。完了は待たない。
# 委譲先のターンが終わるたびに、taskboard が最後の返事を lead（この会話）に人の発言として入れる。
# 規定と使い方: ~/.claude/context/delegation.md
#
# 終了時は必ず1行 JSON を stdout に出す（SIGKILL 等の異常終了を除く）。

set -u

TASK=""
TASK_ID=""
MODEL=""
EFFORT=""
TITLE=""
CWD="$PWD"
WORKTREE_BRANCH=""
WORKTREE_BASE=""
ALLOW_REVIEW=0

WORK_TASK=""
CONVERSATION_ID=""
DETAIL=""

usage() {
  cat >&2 <<'USAGE'
usage: taskboard-delegate.sh --task <指示書の絶対パス> --task-id <taskboard のタスク番号> --model <model> --effort <effort> [options]

  --model MODEL            haiku|sonnet|opus|fable
  --effort EFFORT          low|medium|high|xhigh|max
  --title TEXT             会話の題（ボードと知らせに出る）
  --cwd PATH               作業ディレクトリ（既定: $PWD）
  --worktree-branch NAME   --cwd の repo から worktree を切り、その中で動かす
  --worktree-base NAME     worktree の元にするブランチ（--worktree-branch と使う）
  --allow-review           委譲先が自分の成果物を外部 CLI（codex）でレビューすることを許す
                           （Agent / Workflow tool は外したまま）

  承認は bypassPermissions、Agent と Workflow の tool は外して起こす（再委譲の禁止）。
  lead はこのスクリプトを呼んだ taskboard の会話。
USAGE
}

# 全ての終了はここを通す。$1=status $2=exit $3=reason(省略可)
finalize() {
  FIN_STATUS="$1" FIN_CODE="$2" FIN_REASON="${3:-}" FIN_DETAIL="$DETAIL" \
  FIN_ID="$CONVERSATION_ID" FIN_TASK_ID="$TASK_ID" FIN_MODEL="$MODEL" FIN_EFFORT="$EFFORT" \
  FIN_TITLE="$TITLE" FIN_CWD="$CWD" FIN_SENT="$WORK_TASK" \
  python3 -c '
import json, os
def orn(v):
    return v if v else None
print(json.dumps({
    "status": os.environ["FIN_STATUS"],
    "reason": orn(os.environ.get("FIN_REASON")),
    "detail": orn(os.environ.get("FIN_DETAIL")),
    "exit": int(os.environ["FIN_CODE"]),
    "conversation_id": orn(os.environ.get("FIN_ID")),
    "task_id": int(os.environ["FIN_TASK_ID"]) if os.environ.get("FIN_TASK_ID", "").isdigit() else None,
    "model": orn(os.environ.get("FIN_MODEL")),
    "effort": orn(os.environ.get("FIN_EFFORT")),
    "title": orn(os.environ.get("FIN_TITLE")),
    "cwd": orn(os.environ.get("FIN_CWD")),
    "task_sent": orn(os.environ.get("FIN_SENT")),
}, ensure_ascii=False))
' 2>/dev/null || printf '{"status":"%s","exit":%s,"note":"json_emit_failed"}\n' "$1" "$2"
  exit "$2"
}

# 起こす前に失敗したら、委譲先が読むことのない一時ファイルを残さない
abort() {
  [ -n "$WORK_TASK" ] && rm -f "$WORK_TASK"
  WORK_TASK=""
  finalize "$@"
}

# --- 引数のパース ---
while [ $# -gt 0 ]; do
  case "$1" in
    --task)            TASK="${2:-}"; shift 2 ;;
    --task-id)         TASK_ID="${2:-}"; shift 2 ;;
    --model)           MODEL="${2:-}"; shift 2 ;;
    --effort)          EFFORT="${2:-}"; shift 2 ;;
    --title)           TITLE="${2:-}"; shift 2 ;;
    --cwd)             CWD="${2:-}"; shift 2 ;;
    --worktree-branch) WORKTREE_BRANCH="${2:-}"; shift 2 ;;
    --worktree-base)   WORKTREE_BASE="${2:-}"; shift 2 ;;
    --allow-review)    ALLOW_REVIEW=1; shift ;;
    -h|--help)         usage; exit 0 ;;
    *)                 usage; finalize invalid_input 2 arg_invalid ;;
  esac
done

# --- 事前検証（会話を起こす前に全部行う） ---
command -v python3 >/dev/null 2>&1 || finalize invalid_input 2 python3_unavailable
TASKBOARD="$(command -v taskboard 2>/dev/null)"
[ -n "$TASKBOARD" ] || { [ -x "$HOME/.local/bin/taskboard" ] && TASKBOARD="$HOME/.local/bin/taskboard"; }
[ -n "$TASKBOARD" ] || finalize invalid_input 2 taskboard_unavailable
# 知らせの届け先（parent）を受け付けない古い taskboard では、委譲先が終わっても lead に届かない
"$TASKBOARD" conversation start --help 2>&1 | grep -q -- '--parent-from-env' || finalize invalid_input 2 taskboard_outdated
# 届け先は taskboard の会話だけ。印が無ければ CLI に聞くまでもない
[ -n "${TASKBOARD_CONVERSATION_ID:-}" ] || finalize invalid_input 2 not_in_taskboard

case "$TASK" in
  /*) ;;
  *) finalize invalid_input 2 task_invalid ;;
esac
[ -f "$TASK" ] && [ -r "$TASK" ] || finalize invalid_input 2 task_invalid
case "$TASK_ID" in
  ''|*[!0-9]*) finalize invalid_input 2 task_id_invalid ;;
esac
case "$MODEL" in
  haiku|sonnet|opus|fable) ;;
  *) finalize invalid_input 2 model_invalid ;;
esac
# 省くと taskboard と user settings の既定で起きるため、表で決めた値を毎回渡させる
case "$EFFORT" in
  low|medium|high|xhigh|max) ;;
  *) finalize invalid_input 2 effort_invalid ;;
esac
[ -d "$CWD" ] || finalize invalid_input 2 arg_invalid
CWD="$(cd "$CWD" && pwd)"
[ -z "$WORKTREE_BASE" ] || [ -n "$WORKTREE_BRANCH" ] || finalize invalid_input 2 arg_invalid

# --- 指示書に委譲ヘッダを前置きする ---
WORK_TASK="$(mktemp "${TMPDIR:-/tmp}/taskboard-delegate.XXXXXX")" || finalize invalid_input 2 arg_invalid
{
  cat <<'HEADER'
# 委譲の前提

あなたは lead から作業を委譲された実行担当です。taskboard の会話として動いていて、lead とは taskboard を通してやり取りします。

この節は委譲スクリプトが機械的に前置きする定型文です。**この節と下のタスク本文が食い違ったら、タスク本文を優先してください**（「作業は自分で行う」の節だけは例外で、タスク本文より優先します）。その食い違いだけを理由に lead へ問い合わせる必要はありません。

## 作業は自分で行う（さらに委譲しない）

この委譲の中で、子エージェントや別のセッションを起こさないでください。この会話では Agent tool と Workflow tool を外してあります。taskboard の MCP の `session_start` も使わないでください。Bash から `taskboard-delegate.sh`・`herdr-delegate.sh`・`taskboard conversation start`・`herdr agent start`・`claude`・`codex` を起動して作業を分けることもしないでください。

子エージェントはセッションの使用量を lead・他の委譲先と分け合います。使用量の上限に当たると子エージェントは作業途中で失敗し、それまでに使った分が無駄になります。

作業が1つのコンテキストに収まりそうにないときは、成果物ファイルへ途中経過を書き出しながら進めてください。それでも収まらない、または分けたほうがよいと判断したら、下の方法で lead に分け方を提案してください。分けるかどうかと、分けた作業の起動は lead が決めます。
HEADER

  if [ "$ALLOW_REVIEW" -eq 1 ]; then
    cat <<'REVIEW'

外部レビューは例外として許可されています。規定（`~/.claude/context/agent-cli-guide.md`）で外部レビューが必要になったら、自分の成果物を `codex exec` でレビューしてかまいません。codex が使えない（不在・枠の枯渇）ときは、Agent tool での代替はできないので、レビュー未実施のまま lead に伝えてください。
REVIEW
  else
    cat <<'REVIEW'

外部レビュー（別ベンダーの CLI）が規定上必要になったときも、実行せずに lead へ伝えてください。
REVIEW
  fi

  # 途中で止まる・頼まれていない追加をする癖がモデルごとに違うため
  cat <<'PACE'

## 進め方

- 指示書の作業を全部終えるまで止まらないでください。止まるのは、下の「判断に迷ったら lead に聞く」に当たったときだけです
- 終えて確かめたら、報告して止まってください。頼まれていない機能・テスト・ファイル・文書・リファクタは足さず、役に立ちそうなものは報告の最後に書いてください
- コードを変えたら、変更を実際に通すチェック（PJ のテスト・型検査・ビルド、または変えたコマンドそのもの）を走らせてから完了にしてください。構文だけのチェックと、起動に失敗したチェックは数えません。走らせられなかったときは、何を走らせなかったかと理由を報告に書いてください
- 頼まれていないレビューの周回や、レビュー担当の起動はしないでください
PACE
  case "$MODEL" in
    haiku)
      printf -- '- 今日の日付は %s です。版・価格・規則のように変わり得る事実は、知っているつもりでも検索して確かめてください\n' "$(date +%F)"
      ;;
    fable)
      cat <<'PACE'
- 次にやることを宣言してターンを終えないでください。最後の段落が計画・約束・次の手順の列挙になっていたら、それを実行してから終えてください
- 作業中に気づいた別件（既存の不具合、指示書に無い改善）は直さず、報告に書いてください
- 完了の連絡は、途中を見ていない lead に向けて、結果から書いてください
PACE
      ;;
  esac

  cat <<'HEADER'

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

指示書どおりに進められる範囲は、いちいち確認せずに進めてください。問い合わせるのは上の5つに当たったときです。

## lead への連絡の方法

問い合わせと、下の「完了したら」の完了の連絡は、どちらもそのターンの最後の返事に書いて、ターンを終えてください。ターンが終わると、taskboard が最後の返事を lead に届けます。lead の返答は、この会話の次の発言として届きます。

- lead に届くのは最後の返事の 2,000 字までです。長い内容は成果物のファイルに書き、返事にはそのパスと要点を書いてください
- `SendMessage`・`herdr agent prompt` では送らないでください。taskboard の知らせと別の道で届くと、lead に同じ連絡が 2 回届きます
- 問い合わせに `AskUserQuestion` を使わないでください。返事に書けば、食い違いと選択肢と推奨を一度に lead に渡せます
- lead の返答を待つためにターンを終えるときは、何を待っているかを返事に書いてください

## 完了したら

成果物を書き終えたら、最後の返事に成果物のパスと要点を数行書いて、ターンを終えてください。lead はこの返事で完了を知り、成果物はファイルから読みます。

タスク本文が成果物のパスを指定している場合、**それを書かずにターンを終えると lead 側では失敗として扱われます**。

---

HEADER
  cat "$TASK"
} > "$WORK_TASK" || abort invalid_input 2 arg_invalid

# --- 会話を起こす ---
START_CMD=("$TASKBOARD" conversation start
  --task "$TASK_ID" --cwd "$CWD" --model "$MODEL"
  --permission-mode bypassPermissions --disallowed-tools Agent,Workflow
  --parent-from-env --notify)
START_CMD=("${START_CMD[@]}" --effort "$EFFORT")
[ -n "$TITLE" ] && START_CMD=("${START_CMD[@]}" --title "$TITLE")
[ -n "$WORKTREE_BRANCH" ] && START_CMD=("${START_CMD[@]}" --worktree-branch "$WORKTREE_BRANCH")
[ -n "$WORKTREE_BASE" ] && START_CMD=("${START_CMD[@]}" --worktree-base "$WORKTREE_BASE")
START_CMD=("${START_CMD[@]}" -- "$WORK_TASK を読み、そこに書かれた作業だけを実行してください。")

err_file="$(mktemp "${TMPDIR:-/tmp}/taskboard-delegate-err.XXXXXX")" || abort invalid_input 2 arg_invalid
out="$("${START_CMD[@]}" 2>"$err_file")"
rc=$?
DETAIL="$(head -c 500 "$err_file" 2>/dev/null | tr '\n' ' ' | sed 's/ *$//')"
rm -f "$err_file"
if [ $rc -ne 0 ]; then
  # このシェルが taskboard の会話でないと CLI が断る
  case "$DETAIL" in
    *--parent-from-env:*) abort invalid_input 2 not_in_taskboard ;;
  esac
  abort start_failed 6
fi
CONVERSATION_ID="${out%% *}"
[[ "$CONVERSATION_ID" =~ ^[0-9A-Za-z-]+$ ]] || { CONVERSATION_ID=""; DETAIL="$out"; finalize start_failed 6 unexpected_output; }
DETAIL=""
finalize started 0
