#!/bin/sh
# Claude Code status line script (2 rows)
#   row1 (予算): model | effort | ctx | 5h now→着地 (残り) | 1w now→着地 (reset) | codex 月次枠
#   row2 (位置): owner/repo | branch | PR (state) +a -r | proj -> cwd

input=$(cat)

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

# --- JSON を 1 回で抽出 (empty 保持のため US=0x1f 区切り) ---
US=$(printf '\037')
fields=$(echo "$input" | jq -r '[
  .model.display_name // "",
  .effort.level // "",
  (.thinking.enabled // false),
  (.context_window.used_percentage // "" | if type == "number" then floor else . end),
  .context_window.total_input_tokens // "",
  .context_window.context_window_size // "",
  (.rate_limits.five_hour.used_percentage // "" | if type == "number" then floor else . end),
  .rate_limits.five_hour.resets_at // "",
  (.rate_limits.seven_day.used_percentage // "" | if type == "number" then floor else . end),
  .rate_limits.seven_day.resets_at // "",
  (if .workspace.repo then (.workspace.repo.owner + "/" + .workspace.repo.name) else "" end),
  .workspace.git_worktree // "",
  .workspace.project_dir // "",
  (.workspace.current_dir // .cwd // ""),
  .pr.number // "",
  .pr.review_state // "",
  .cost.total_lines_added // 0,
  .cost.total_lines_removed // 0,
  (.fast_mode // false)
] | map(tostring) | join("")')

IFS="$US" read -r model effort thinking used_pct in_tok win \
  fh_pct fh_reset sd_pct sd_reset repo worktree proj cur \
  pr_num pr_state added removed fast_mode <<EOF
$fields
EOF

now=$(date +%s)

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
  if [ "$show_sd_abs" -eq 1 ]; then
    abs=$(date -r "$sd_reset" +"%m/%d %H:%M" 2>/dev/null)
    [ -n "$abs" ] && seg="${seg} ${C_DIM}${abs}${C_OFF}"
  fi
  add1 "$(ic "$I_CAL") ${seg}"
fi

# 5. codex の月次クレジット枠 (キャッシュを読むだけ。古ければ裏で更新をキックする)
cdx_cache="$HOME/.cache/claude-statusline/codex-usage.json"
CDX_STALE_SEC=300
CDX_AGE_VISIBLE_SEC=1800
cdx_pct=""; cdx_reset=""; cdx_fetched=""
if [ -f "$cdx_cache" ]; then
  cdx_fields=$(jq -r '[(.pct // ""), (.resets_at // ""), (.fetched_at // "")]
    | map(tostring) | join("")' "$cdx_cache" 2>/dev/null)
  IFS="$US" read -r cdx_pct cdx_reset cdx_fetched <<EOF
$cdx_fields
EOF
fi
if [ -n "$cdx_pct" ]; then
  seg="$(limit_color "$cdx_pct")${cdx_pct}%${C_OFF}"
  if [ "$show_cdx_reset" -eq 1 ] && [ -n "$cdx_reset" ]; then
    cdx_abs=$(date -r "$cdx_reset" +"%-m/%-d" 2>/dev/null)
    [ -n "$cdx_abs" ] && seg="${seg} ${C_DIM}${cdx_abs}${C_OFF}"
  fi
  # codex を動かしていない間は値が動かないため、古いことが読み取れるようにする
  if [ -n "$cdx_fetched" ]; then
    cdx_age=$((now - cdx_fetched))
    [ "$cdx_age" -ge "$CDX_AGE_VISIBLE_SEC" ] &&
      seg="${seg} ${C_DIM}~$(fmt_remaining "$cdx_age")${C_OFF}"
  fi
  add1 "$(ic "$I_CASH") ${seg}"
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
proj_t=$(printf '%s' "$proj" | sed "s|^${HOME}|~|")
cur_t=$(printf '%s' "$cur" | sed "s|^${HOME}|~|")
if [ "$proj" = "$cur" ]; then
  path_disp="$proj_t"
else
  path_disp="${proj_t} -> ${cur_t}"
fi
add2 "$(ic "$I_FOLDER") ${C_DIM}${path_disp}${C_OFF}"

# Why not: 行を C_OFF で閉じずに出力しない。Claude Code は N 行目の先頭に
# 1..N-1 行目の SGR を連結するため、閉じ忘れると色が次の行へ漏れる
printf "%s%s\n%s%s" "$row1" "$C_OFF" "$row2" "$C_OFF"
