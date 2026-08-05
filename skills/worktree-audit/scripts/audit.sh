#!/usr/bin/env bash
# このマシン上の git worktree を横断で棚卸しし、削除可否を TSV で出力する。
#
# usage: audit.sh [--root DIR]... [--no-fetch] [--no-pr] [--branches]
#   --root DIR   探索起点（複数可。既定: $HOME/workspace $HOME/.claude $HOME/.dotfiles）
#   --no-fetch   origin を取得しない（オフライン時。判定は古い remote-tracking 基準になる）
#   --no-pr      gh による PR 判定を行わない（第1段の祖先判定のみ）
#   --branches   worktree ではなく全ローカルブランチを対象にする
#
# 出力（TSV, 1行目はヘッダ）:
#   repo  path_or_branch  branch  base  dirty  untracked  unmerged  verdict  detail
#
# verdict:
#   MERGED_ANCESTOR  base の祖先。--merged と同じ。そのまま削除可
#   MERGED_SQUASH    PR が MERGED。squash/rebase マージのため祖先判定は通らない
#   HEAD_MISMATCH    PR は MERGED だがローカル HEAD が PR head と不一致（要確認）
#   OPEN_PR          PR が OPEN。作業中のため削除不可
#   CLOSED_PR        PR がマージされずクローズ。内容が base に無い可能性（要判断）
#   NO_PR            PR が存在せず未マージ（統合ブランチ・作業残骸。要判断）
#   DETACHED         detached HEAD（unmerged 列で可否を判断する）
#
# bash 3.2 互換で書くこと（macOS 既定。連想配列 declare -A は使えない）。

set -u

ROOTS=""
DO_FETCH=1
DO_PR=1
MODE="worktree"

while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOTS="$ROOTS $2"; shift 2;;
    --no-fetch) DO_FETCH=0; shift;;
    --no-pr) DO_PR=0; shift;;
    --branches) MODE="branches"; shift;;
    *) echo "unknown option: $1" >&2; exit 2;;
  esac
done
[ -z "$ROOTS" ] && ROOTS="$HOME/workspace $HOME/.claude $HOME/.dotfiles"

# --- リポジトリ探索 -----------------------------------------------------------
# .git ディレクトリ = メインリポジトリ。linked worktree の .git はファイルなので拾わない。
discover_repos() {
  for root in $ROOTS; do
    [ -d "$root" ] || continue
    if command -v fd >/dev/null 2>&1; then
      fd -H -I --max-depth 6 --type d '^\.git$' "$root" 2>/dev/null
    else
      find "$root" -maxdepth 6 -type d -name .git 2>/dev/null
    fi
  done | sed 's|/\.git/*$||' | sort -u
}

REPOS=$(discover_repos)
[ -z "$REPOS" ] && { echo "リポジトリが見つかりません: $ROOTS" >&2; exit 1; }

# --- fetch（並列） ------------------------------------------------------------
if [ "$DO_FETCH" = "1" ]; then
  echo "fetching..." >&2
  for r in $REPOS; do
    git -C "$r" fetch --quiet origin 2>/dev/null &
  done
  wait
fi

# base ブランチを決める（develop → main → master の順）
resolve_base() {
  for b in develop main master; do
    if git -C "$1" rev-parse --verify --quiet "refs/remotes/origin/$b" >/dev/null 2>&1; then
      echo "origin/$b"; return
    fi
  done
  echo ""
}

# PR 判定（第2段）。gh の結果を "state<TAB>number<TAB>headRefOid" で返す。
pr_lookup() {
  repo="$1"; br="$2"
  ( cd "$repo" 2>/dev/null || exit 0
    gh pr list --head "$br" --state all --limit 1 \
      --json number,state,headRefOid \
      -q '.[0] | "\(.state)\t\(.number)\t\(.headRefOid)"' 2>/dev/null )
}

# 1 ブランチ分を判定して 1 行出力する。
emit() {
  repo="$1"; label="$2"; br="$3"; base="$4"; ref="$5"; dirty="$6"; untracked="$7"
  name=$(basename "$repo")

  if [ -z "$base" ]; then
    printf "%s\t%s\t%s\t-\t%s\t%s\t?\tNO_BASE\torigin/develop|main|master が無い\n" \
      "$name" "$label" "$br" "$dirty" "$untracked"
    return
  fi

  unmerged=$(git -C "$repo" rev-list --count "$base..$ref" 2>/dev/null)
  [ -z "$unmerged" ] && unmerged="?"

  if [ "$br" = "DETACHED" ]; then
    v="DETACHED"; d="HEAD=$(git -C "$repo" rev-parse --short "$ref" 2>/dev/null)"
  elif [ "$unmerged" = "0" ]; then
    v="MERGED_ANCESTOR"; d="-"
  elif [ "$DO_PR" = "0" ]; then
    v="NO_PR"; d="PR判定スキップ"
  else
    info=$(pr_lookup "$repo" "$br")
    state=$(printf "%s" "$info" | cut -f1)
    num=$(printf "%s" "$info" | cut -f2)
    oid=$(printf "%s" "$info" | cut -f3)
    case "$state" in
      MERGED)
        local_sha=$(git -C "$repo" rev-parse "$ref" 2>/dev/null)
        if [ "$local_sha" = "$oid" ]; then
          v="MERGED_SQUASH"; d="PR#$num head一致"
        elif git -C "$repo" cat-file -e "$oid" 2>/dev/null &&
             [ "$(git -C "$repo" rev-list --count "$oid..$ref" 2>/dev/null)" = "0" ]; then
          # ローカル HEAD が PR head の祖先 = ローカル固有のコミットは無い
          v="MERGED_SQUASH"; d="PR#$num head祖先"
        else
          v="HEAD_MISMATCH"; d="PR#$num とローカルHEADが不一致。gotchas.md 参照"
        fi
        ;;
      OPEN)   v="OPEN_PR";   d="PR#$num";;
      CLOSED) v="CLOSED_PR"; d="PR#${num}（マージせずクローズ）";;
      *)      v="NO_PR";     d="PRなし";;
    esac
  fi

  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
    "$name" "$label" "$br" "$base" "$dirty" "$untracked" "$unmerged" "$v" "$d"
}

printf "repo\tpath_or_branch\tbranch\tbase\tdirty\tuntracked\tunmerged\tverdict\tdetail\n"

for repo in $REPOS; do
  base=$(resolve_base "$repo")

  if [ "$MODE" = "branches" ]; then
    cur=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
    git -C "$repo" branch --format='%(refname:short)' 2>/dev/null | while read -r br; do
      case "$br" in main|master|develop|dev) continue;; esac
      [ "$br" = "$cur" ] && continue
      emit "$repo" "$br" "$br" "$base" "refs/heads/$br" 0 0
    done
  else
    main_wt=$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)
    git -C "$repo" worktree list --porcelain 2>/dev/null \
      | awk '/^worktree /{wt=substr($0,10)}
             /^branch /{print wt"\t"substr($0,8)}
             /^detached/{print wt"\tDETACHED"}' \
      | while IFS="$(printf '\t')" read -r wt br; do
          [ "$wt" = "$main_wt" ] && continue
          [ -d "$wt" ] || { printf "%s\t%s\t?\t-\t?\t?\t?\tPRUNABLE\tディレクトリ不在。git worktree prune 対象\n" "$(basename "$repo")" "$wt"; continue; }
          brs="${br#refs/heads/}"
          dirty=$(git -C "$wt" status --porcelain --untracked-files=no 2>/dev/null | wc -l | tr -d ' ')
          untr=$(git -C "$wt" ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
          if [ "$brs" = "DETACHED" ]; then ref="HEAD"; else ref="refs/heads/$brs"; fi
          emit "$repo" "$wt" "$brs" "$base" "$ref" "$dirty" "$untr"
        done
  fi
done
