#!/bin/sh
# Claude Code status line script

input=$(cat)

model=$(echo "$input" | jq -r '.model.display_name // "Unknown"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')

used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

if [ -n "$used_pct" ]; then
  ctx_str=$(printf "%.0f%%" "$used_pct")
else
  ctx_str="--"
fi

# Git info (remote org/repo + branch)
git_str=""
if [ -n "$cwd" ] && [ -d "$cwd/.git" ] || git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null)
  remote_url=$(git -C "$cwd" remote get-url origin 2>/dev/null)
  if [ -n "$remote_url" ]; then
    # Extract org/repo from SSH or HTTPS URL
    # SSH:   git@github.com:org/repo.git
    # HTTPS: https://github.com/org/repo.git
    repo=$(echo "$remote_url" | sed -E 's|.*[:/]([^/]+/[^/]+)(\.git)?$|\1|')
    if [ -n "$branch" ]; then
      git_str=" | ${repo} | ⎇ ${branch}"
    else
      git_str=" | ${repo}"
    fi
  elif [ -n "$branch" ]; then
    git_str=" | ⎇ ${branch}"
  fi
fi

printf "%s | %s%s" "$model" "$ctx_str" "$git_str"
