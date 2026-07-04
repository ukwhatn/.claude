#!/bin/sh
# Claude Code status line script
# 表示: model | effort[A] | ctx% (tok/size) | 5h/1w rate | owner/repo | branch (in worktree) | PR #n (state) +a -r | proj -> cwd

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

# セグメントを " | " 区切りで連結 (空はスキップ)
out=""; sep=""
add() { [ -z "$1" ] && return; out="${out}${sep}$1"; sep=" | "; }

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

# 1. model
add "$model"

# 2. effort (+ Adaptive Thinking 時に [A])
if [ -n "$effort" ]; then
  eff="$effort"
  [ "$thinking" = "true" ] && eff="${eff}[A]"
  [ "$fast_mode" = "true" ] && eff="${eff}[F]"
  add "$eff"
fi

# 3. context: used% (tok/size)
if [ -n "$used_pct" ]; then
  ctx="${used_pct}%"
  if [ -n "$in_tok" ] && [ -n "$win" ]; then
    ctx="${ctx} ($(humanize "$in_tok")/$(humanize "$win"))"
  fi
  add "$ctx"
fi

# 4. rate limits: 5h は残り時間 / 1w は絶対時刻
now=$(date +%s)
rate=""
if [ -n "$fh_pct" ]; then
  rem=$((fh_reset - now))
  rate="5h:${fh_pct}%($(fmt_remaining "$rem"))"
fi
if [ -n "$sd_pct" ]; then
  abs=$(date -r "$sd_reset" +"%m/%d %H:%M" 2>/dev/null)
  part="1w:${sd_pct}%(${abs})"
  if [ -n "$rate" ]; then rate="${rate} ${part}"; else rate="$part"; fi
fi
add "$rate"

# 5. owner/repo (native, .git 無し)
add "$repo"

# 6. branch (+ in worktree)
[ -z "$cur" ] && cur="$PWD"
branch=$(git -C "$cur" symbolic-ref --short HEAD 2>/dev/null)
if [ -n "$branch" ]; then
  bseg="⎇ ${branch}"
  [ -n "$worktree" ] && bseg="${bseg} (in worktree)"
  add "$bseg"
elif [ -n "$worktree" ]; then
  add "(in worktree)"
fi

# 7. PR (state) + 変更行数
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
  pr_seg="PR #${pr_num}"
  [ -n "$st_disp" ] && pr_seg="${pr_seg} (${st_disp})"
fi
a=${added:-0}; r=${removed:-0}
if [ "$a" -gt 0 ] || [ "$r" -gt 0 ]; then
  lines="+${a} -${r}"
  if [ -n "$pr_seg" ]; then pr_seg="${pr_seg} ${lines}"; else pr_seg="$lines"; fi
fi
add "$pr_seg"

# 8. project_dir -> current_dir (一致なら project_dir のみ)
[ -z "$proj" ] && proj="$cur"
proj_t=$(printf '%s' "$proj" | sed "s|^${HOME}|~|")
cur_t=$(printf '%s' "$cur" | sed "s|^${HOME}|~|")
if [ "$proj" = "$cur" ]; then
  add "$proj_t"
else
  add "${proj_t} -> ${cur_t}"
fi

printf "%s" "$out"
