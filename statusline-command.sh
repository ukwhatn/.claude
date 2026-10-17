#!/bin/sh
# Claude Code status line script (2 rows)
#   row1 (予算): model | effort | ctx | 5h now→着地 (残り) | 1w now→着地 (reset) | codex 枠
#   row2 (位置): owner/repo | branch | PR (state) +a -r | proj -> cwd
# Why not: 外部コマンドを増やさない。refreshInterval ごとに全セッションで走り、社用 Mac では
# exec のたびにセキュリティエージェントが動くため、日付の整形・codex キャッシュの読み込みも
# 1 回の jq にまとめる (外部コマンドは cat / jq / git / taskboard だけ)

input=$(cat)

# taskboard の daemon に使用枠と context を渡す（taskboard を入れた Mac だけ）
# Why not: 前景で待たない・stdout をつながない。出力をパイプで読む側は EOF まで待つので、
# 裏の子が stdout を握っていると描画が遅れる
if [ -x "$HOME/.local/bin/taskboard" ]; then
  (printf '%s' "$input" | "$HOME/.local/bin/taskboard" hook statusline >/dev/null 2>&1 &)
fi

# --- helpers ---
# 数値を k / M 表記に丸める (76393 -> 76k, 1000000 -> 1M)
humanize() {
  n=$1
  [ -z "$n" ] && return
  if [ "$n" -ge 1000000 ]; then
    whole=$((n / 1000000)); frac=$(((n % 1000000) / 100000))
    if [ "$frac" -gt 0 ]; then printf "%d.%dM" "$whole" "$frac"; else printf "%dM" "$whole"; fi
  elif [ "$n" -ge 1000 ]; then
    printf "%dk" $((n / 1000))
  else
    printf "%d" "$n"
  fi
}

# 残り秒を 2h13m / 45m 表記に
fmt_remaining() {
  secs=$1
  [ "$secs" -lt 0 ] && secs=0
  h=$((secs / 3600)); m=$(((secs % 3600) / 60))
  if [ "$h" -gt 0 ]; then printf "%dh%02dm" "$h" "$m"; else printf "%dm" "$m"; fi
}

# --- 色 (truecolor) ---
# Why not: テーマの palette 番号を使わない。GitHub Light の palette 3 は #4d2d00 で
# 白背景では茶色に見え、警告色として機能しないため、意味色を直接指定する
ESC=$(printf '\033')
C_OFF="${ESC}[0m"; C_BLD="${ESC}[1m"
if [ "$CC_STATUSLINE_THEME" = "dark" ]; then
  C_DIM="${ESC}[38;2;139;148;158m"; C_FG="${ESC}[38;2;230;237;243m"
  C_GRN="${ESC}[38;2;63;185;80m";   C_AMB="${ESC}[38;2;210;153;34m"
  C_RED="${ESC}[38;2;248;81;73m";   C_BLU="${ESC}[38;2;88;166;255m"
else
  C_DIM="${ESC}[38;2;101;109;118m"; C_FG="${ESC}[38;2;31;35;40m"
  C_GRN="${ESC}[38;2;26;127;55m";   C_AMB="${ESC}[38;2;154;103;0m"
  C_RED="${ESC}[38;2;207;34;46m";   C_BLU="${ESC}[38;2;9;105;218m"
fi

# --- OSC 8 ハイパーリンク ---
# Why not: 常時有効の前提にしない。Claude Code がそのまま端末へ渡すかは未確認のため、
# 剥がれてもラベルだけで意味が通る呼び方にしつつ、ここ1箇所 (USE_OSC8) で切替できるようにする
USE_OSC8=1
osc8() {
  if [ "$USE_OSC8" = "1" ] && [ -n "$1" ]; then
    printf '\033]8;;%s\033\\%s\033]8;;\033\\' "$1" "$2"
  else
    printf "%s" "$2"
  fi
}

# --- アイコン (Material Design Icons / U+F0000 以降) ---
# Why not: BMP の Private Use Area (U+E000-F8FF) のグリフを使わない。East Asian Width が
# Ambiguous のため CJK フォント側に回され、そこにグリフが無く描画に失敗する
I_MODEL=$(printf '\363\260\232\251')
I_EFFORT=$(printf '\363\260\211\201')
I_THINK=$(printf '\363\260\233\250')
I_FAST=$(printf '\363\260\221\243')
I_CTX=$(printf '\363\260\215\233')
I_CLOCK=$(printf '\363\260\205\222')
I_CAL=$(printf '\363\260\203\255')
I_CASH=$(printf '\363\260\204\224')
I_REPO=$(printf '\363\260\263\217')
I_BRANCH=$(printf '\363\260\230\254')
I_TREE=$(printf '\363\260\231\205')
I_PR=$(printf '\363\260\223\202')
I_FOLDER=$(printf '\363\260\211\213')
ARROW=$(printf '\342\206\222')

# アイコンを dim で装飾して返す
ic() { printf "%s%s%s" "$C_DIM" "$1" "$C_OFF"; }

# rate limit 系の閾値 (80/100)
limit_color() {
  if   [ "$1" -ge 100 ]; then printf "%s%s" "$C_BLD" "$C_RED"
  elif [ "$1" -ge 80 ];  then printf "%s%s" "$C_BLD" "$C_AMB"
  else                        printf "%s" "$C_GRN"
  fi
}

# 窓終了時点の消費率を窓平均ペースから外挿し、色付きで返す
# $1:現在% $2:残り秒 $3:窓長秒 $4:予測を出す最小経過秒
# Why not: 直近増分からの外挿にしない。statusline は数秒間隔で呼ばれるためノイズが乗り、
# アイドル中は増分ゼロで着地0%に振れて警告として機能しなくなる
project() {
  _now=$1; _rem=$2; _total=$3; _min=$4
  [ "$_rem" -lt 0 ] && _rem=0
  _elapsed=$((_total - _rem))
  [ "$_elapsed" -lt "$_min" ] && return
  _p=$((_now * _total / _elapsed))
  [ "$_p" -gt 999 ] && _p=999
  printf "%s%d%%%s" "$(limit_color "$_p")" "$_p" "$C_OFF"
}

# 窓長 (秒) を 5h / 1w のラベルにする
window_label() {
  if   [ $(($1 % 604800)) -eq 0 ]; then printf "%dw" $(($1 / 604800))
  elif [ $(($1 % 86400))  -eq 0 ]; then printf "%dd" $(($1 / 86400))
  else                                  printf "%dh" $(($1 / 3600))
  fi
}

# 着地予測を出し始める最小経過秒
# Why not: 窓長の一定割合にしない。1w 窓に 5h 窓と同じ割合 (1/10) を当てると
# 2 日以上経つまで予測が出ず、週枠の警告として遅すぎるため
project_min() {
  if [ "$1" -ge 604800 ]; then printf 21600; else printf "%d" $(($1 / 10)); fi
}

# codex の rate limit 窓を "5h 13%→18% 4h12m" の形にする
# $1:現在% $2:窓長秒 $3:リセット時刻 $4:現在時刻 $5:リセット日を出すか $6:リセット日 (m/d)
codex_window() {
  [ -z "$1" ] && return
  _cw_pct=$1; _cw_win=$2; _cw_reset=$3; _cw_now=$4; _cw_abs=$5; _cw_d=$6
  if [ -n "$_cw_win" ]; then
    _cw_out="${C_FG}$(window_label "$_cw_win") ${_cw_pct}%${C_OFF}"
  else
    _cw_out="${C_FG}${_cw_pct}%${C_OFF}"
  fi
  if [ -n "$_cw_win" ] && [ -n "$_cw_reset" ]; then
    _cw_rem=$((_cw_reset - _cw_now))
    _cw_pj=$(project "$_cw_pct" "$_cw_rem" "$_cw_win" "$(project_min "$_cw_win")")
    [ -n "$_cw_pj" ] && _cw_out="${_cw_out}${C_DIM}${ARROW}${C_OFF}${_cw_pj}"
    # Why not: 窓長によらず残り時間で出さない。1w 窓では "148h30m" となり
    # いつ空くかが読み取れないため、日をまたぐ窓は日付で出す
    if [ "$_cw_win" -ge 86400 ]; then
      if [ "$_cw_abs" -eq 1 ]; then
        [ -n "$_cw_d" ] && _cw_out="${_cw_out} ${C_DIM}${_cw_d}${C_OFF}"
      fi
    else
      _cw_out="${_cw_out} ${C_DIM}$(fmt_remaining "$_cw_rem")${C_OFF}"
    fi
  fi
  printf "%s" "$_cw_out"
}

# context window の閾値 (40% 超で警告、60% 以上で危険)
ctx_color() {
  if   [ "$1" -ge 60 ]; then printf "%s%s" "$C_BLD" "$C_RED"
  elif [ "$1" -gt 40 ]; then printf "%s%s" "$C_BLD" "$C_AMB"
  else                       printf "%s" "$C_GRN"
  fi
}

# セグメントを2スペース区切りで連結 (空はスキップ)
row1=""; sep1=""
add1() { [ -z "$1" ] && return; row1="${row1}${sep1}$1"; sep1="  "; }
row2=""; sep2=""
add2() { [ -z "$1" ] && return; row2="${row2}${sep2}$1"; sep2="  "; }

# --- JSON と codex のキャッシュを 1 回の jq で抽出 (empty 保持のため US=0x1f 区切り) ---
# codex の利用枠はキャッシュを読むだけ。古ければ後段で裏の更新をキックする
cdx_cache="$HOME/.cache/claude-statusline/codex-usage.json"
US=$(printf '\037')
# Why not: キャッシュが無いときにファイル名を渡さない。jq が開けずに exit 2 となるため
set -- -
[ -f "$cdx_cache" ] && set -- - "$cdx_cache"
fields=$(printf '%s' "$input" | jq -rn '
  def d($f): if type == "number" then (localtime | strftime($f)) else "" end;
  input as $i | (try input catch {}) as $c | [
  $i.model.display_name // "",
  $i.effort.level // "",
  ($i.thinking.enabled // false),
  ($i.context_window.used_percentage // "" | if type == "number" then floor else . end),
  $i.context_window.total_input_tokens // "",
  $i.context_window.context_window_size // "",
  ($i.rate_limits.five_hour.used_percentage // "" | if type == "number" then floor else . end),
  $i.rate_limits.five_hour.resets_at // "",
  ($i.rate_limits.seven_day.used_percentage // "" | if type == "number" then floor else . end),
  $i.rate_limits.seven_day.resets_at // "",
  ($i.rate_limits.seven_day.resets_at | d("%m/%d %H:%M")),
  (if $i.workspace.repo then ($i.workspace.repo.owner + "/" + $i.workspace.repo.name) else "" end),
  $i.workspace.git_worktree // "",
  $i.workspace.project_dir // "",
  ($i.workspace.current_dir // $i.cwd // ""),
  $i.pr.number // "",
  $i.pr.review_state // "",
  $i.cost.total_lines_added // 0,
  $i.cost.total_lines_removed // 0,
  ($i.fast_mode // false),
  (now | floor),
  ($c.monthly.pct // ""), ($c.monthly.used // ""), ($c.monthly.limit // ""), ($c.monthly.resets_at | d("%-m/%-d")),
  ($c.primary.pct // ""), ($c.primary.window_sec // ""), ($c.primary.resets_at // ""), ($c.primary.resets_at | d("%-m/%-d")),
  ($c.secondary.pct // ""), ($c.secondary.window_sec // ""), ($c.secondary.resets_at // ""), ($c.secondary.resets_at | d("%-m/%-d")),
  ($c.credits.unlimited // false), ($c.credits.balance // ""),
  ($c.reset_credits // ""), ($c.fetched_at // "")
] | map(tostring) | join("\u001f")' "$@" 2>/dev/null)

IFS="$US" read -r model effort thinking used_pct in_tok win \
  fh_pct fh_reset sd_pct sd_reset sd_abs repo worktree proj cur \
  pr_num pr_state added removed fast_mode now \
  cdx_m_pct cdx_m_used cdx_m_limit cdx_m_date \
  cdx_p_pct cdx_p_win cdx_p_reset cdx_p_date \
  cdx_s_pct cdx_s_win cdx_s_reset cdx_s_date \
  cdx_unlim cdx_bal cdx_tickets cdx_fetched <<EOF
$fields
EOF

# 端末幅に応じた段階的縮退 (COLUMNS 未設定・0 は広いものとして扱う)
cols=${COLUMNS:-0}
[ "$cols" -eq 0 ] && cols=999
show_sd_abs=1; show_ctx_tok=1; show_cdx_reset=1
[ "$cols" -lt 100 ] && show_sd_abs=0
[ "$cols" -lt 88 ]  && show_ctx_tok=0
[ "$cols" -lt 76 ]  && show_cdx_reset=0

# ---------- row1: 予算 ----------

# 1. model
[ -n "$model" ] && add1 "$(ic "$I_MODEL") ${C_FG}${model}${C_OFF}"

# 2. effort (+ Adaptive Thinking / fast mode をアイコンで併記)
if [ -n "$effort" ]; then
  eff="${C_FG}${effort}${C_OFF}"
  [ "$thinking" = "true" ] && eff="${eff} $(ic "$I_THINK")"
  [ "$fast_mode" = "true" ] && eff="${eff} $(ic "$I_FAST")"
  add1 "$(ic "$I_EFFORT") ${eff}"
fi

# 3. context: used% (tok/size)
if [ -n "$used_pct" ]; then
  ctx="$(ctx_color "$used_pct")${used_pct}%${C_OFF}"
  if [ "$show_ctx_tok" -eq 1 ] && [ -n "$in_tok" ] && [ -n "$win" ]; then
    ctx="${ctx} ${C_DIM}$(humanize "$in_tok")/$(humanize "$win")${C_OFF}"
  fi
  add1 "$(ic "$I_CTX") ${ctx}"
fi

# 4. rate limits: 現在% -> 窓終了時の着地予測 (残り時間 / 絶対時刻)
if [ -n "$fh_pct" ]; then
  rem=$((fh_reset - now))
  seg="${C_FG}5h ${fh_pct}%${C_OFF}"
  pj=$(project "$fh_pct" "$rem" 18000 1800)
  [ -n "$pj" ] && seg="${seg}${C_DIM}${ARROW}${C_OFF}${pj}"
  add1 "$(ic "$I_CLOCK") ${seg} ${C_DIM}$(fmt_remaining "$rem")${C_OFF}"
fi
if [ -n "$sd_pct" ]; then
  rem=$((sd_reset - now))
  seg="${C_FG}1w ${sd_pct}%${C_OFF}"
  pj=$(project "$sd_pct" "$rem" 604800 21600)
  [ -n "$pj" ] && seg="${seg}${C_DIM}${ARROW}${C_OFF}${pj}"
  if [ "$show_sd_abs" -eq 1 ] && [ -n "$sd_abs" ]; then
    seg="${seg} ${C_DIM}${sd_abs}${C_OFF}"
  fi
  add1 "$(ic "$I_CAL") ${seg}"
fi

# 5. codex の利用枠 (値は上の jq でキャッシュから読んだもの)
#    枠の構成は契約で変わる (個人契約は月次枠 + 5h/1w 窓、team 契約は窓のみ) ため、
#    キャッシュに載っているものだけを出す
CDX_STALE_SEC=300
CDX_AGE_VISIBLE_SEC=1800
cdx=""
cdx_add() {
  [ -z "$1" ] && return
  [ -n "$cdx" ] && cdx="${cdx} ${C_DIM}|${C_OFF} "
  cdx="${cdx}$1"
}

# 月次クレジット枠 (個人契約でのみ返る)
if [ -n "$cdx_m_pct" ]; then
  seg="$(limit_color "$cdx_m_pct")${cdx_m_pct}%${C_OFF}"
  if [ "$show_cdx_reset" -eq 1 ]; then
    if [ -n "$cdx_m_used" ] && [ -n "$cdx_m_limit" ]; then
      # Why not: humanize で k 表記に丸めない。単位がクレジットで桁感が読めず、
      # 1234/4000 が 1k/4k になると残量の判断に使えないため
      seg="${seg} ${C_DIM}$(printf '%.0f' "$cdx_m_used")/$(printf '%.0f' "$cdx_m_limit")${C_OFF}"
    fi
    [ -n "$cdx_m_date" ] && seg="${seg} ${C_DIM}${cdx_m_date}${C_OFF}"
  fi
  cdx_add "$seg"
fi

cdx_add "$(codex_window "$cdx_p_pct" "$cdx_p_win" "$cdx_p_reset" "$now" "$show_cdx_reset" "$cdx_p_date")"
cdx_add "$(codex_window "$cdx_s_pct" "$cdx_s_win" "$cdx_s_reset" "$now" "$show_cdx_reset" "$cdx_s_date")"

if [ "$cdx_unlim" = "true" ]; then
  cdx_add "${C_GRN}unlimited${C_OFF}"
elif [ -n "$cdx_bal" ]; then
  cdx_add "${C_FG}bal ${cdx_bal}${C_OFF}"
fi
[ -n "$cdx_tickets" ] && cdx_add "${C_DIM}reset x${cdx_tickets}${C_OFF}"

if [ -n "$cdx" ]; then
  # codex を動かしていない間は値が動かないため、古いことが読み取れるようにする
  if [ -n "$cdx_fetched" ]; then
    cdx_age=$((now - cdx_fetched))
    [ "$cdx_age" -ge "$CDX_AGE_VISIBLE_SEC" ] &&
      cdx="${cdx} ${C_DIM}~$(fmt_remaining "$cdx_age")${C_OFF}"
  fi
  add1 "$(ic "$I_CASH") ${C_DIM}cdx${C_OFF} ${cdx}"
fi
if [ -z "$cdx_fetched" ] || [ $((now - cdx_fetched)) -ge "$CDX_STALE_SEC" ]; then
  # detach して待たない。多重起動は codex-usage.py 側のロックが吸収する
  (python3 "$HOME/.claude/codex-usage.py" --refresh >/dev/null 2>&1 &)
fi

# ---------- row2: 位置 ----------

# 6. owner/repo (native, .git 無し)
[ -n "$repo" ] && add2 "$(ic "$I_REPO") ${C_FG}${repo}${C_OFF}"

# 7. branch (worktree 内はアイコンで区別)
[ -z "$cur" ] && cur="$PWD"
branch=$(git -C "$cur" symbolic-ref --short HEAD 2>/dev/null)
if [ -n "$worktree" ]; then bicon="$I_TREE"; else bicon="$I_BRANCH"; fi
if [ -n "$branch" ]; then
  add2 "$(ic "$bicon") ${C_FG}${branch}${C_OFF}"
elif [ -n "$worktree" ]; then
  add2 "$(ic "$I_TREE") ${C_DIM}${worktree}${C_OFF}"
fi

# 8. PR (state) + 変更行数
pr_seg=""
if [ -n "$pr_num" ]; then
  case "$pr_state" in
    draft)              st_disp="draft" ;;
    pending)            st_disp="open" ;;
    changes_requested)  st_disp="changes requested" ;;
    approved)           st_disp="approved" ;;
    "")                 st_disp="" ;;
    *)                  st_disp="$pr_state" ;;
  esac
  pr_seg="$(ic "$I_PR") ${C_BLU}#${pr_num}${C_OFF}"
  [ -n "$st_disp" ] && pr_seg="${pr_seg} ${C_DIM}${st_disp}${C_OFF}"
fi
a=${added:-0}; r=${removed:-0}
if [ "$a" -gt 0 ] || [ "$r" -gt 0 ]; then
  lines="${C_GRN}+${a}${C_OFF} ${C_RED}-${r}${C_OFF}"
  if [ -n "$pr_seg" ]; then pr_seg="${pr_seg}  ${lines}"; else pr_seg="$lines"; fi
fi
add2 "$pr_seg"

# 9. project_dir -> current_dir (一致なら project_dir のみ)
[ -z "$proj" ] && proj="$cur"
# ホームを ~ にする
tilde() { case "$1" in "$HOME"|"$HOME"/*) printf '~%s' "${1#"$HOME"}" ;; *) printf '%s' "$1" ;; esac; }
proj_t=$(tilde "$proj")
cur_t=$(tilde "$cur")
if [ "$proj" = "$cur" ]; then
  path_disp="$proj_t"
else
  path_disp="${proj_t} -> ${cur_t}"
fi
add2 "$(ic "$I_FOLDER") ${C_DIM}${path_disp}${C_OFF}"

# Why not: 行を C_OFF で閉じずに出力しない。Claude Code は N 行目の先頭に
# 1..N-1 行目の SGR を連結するため、閉じ忘れると色が次の行へ漏れる
printf "%s%s\n%s%s" "$row1" "$C_OFF" "$row2" "$C_OFF"
