#!/bin/bash
# ディスクの棚卸し。再生成できるものと片付け条件を満たすworktreeを消し、判断が要るものは報告に載せる。
#
# 使い方: disk-inventory.sh [--apply] [--scheduled]
#   既定はdry-run（消す対象を報告に載せるだけで消さない）。--apply で実際に消す
#   --scheduled: 前回の完了から INTERVAL_DAYS 経っておらず、空きが MIN_FREE_GB 以上なら何もせず終わる
#                （launchdから毎時起動し、「週1回」と「空きがしきい値を切ったとき」の両方を拾うため）
#
# 設定: ~/.config/disk-inventory/config.sh（マシン固有のパス・しきい値。無ければ下の既定値で動く）
# 報告: ~/Library/Logs/disk-inventory/latest.md
#
# 自動で消すもの（いずれも、プロセスが開いているパス配下と PROTECT_PATHS 配下は消さない）:
#   - Docker: STALE_DAYS より古いbuild cacheと未使用image（volumeは消さない）
#   - npm / uv / Homebrew のキャッシュ
#   - バージョン別に並ぶディレクトリのうち、最新以外で STALE_DAYS より古いもの
#   - BUILD_SCAN_ROOTS 配下のビルド成果物ディレクトリのうち、STALE_DAYS 更新が無いもの
#   - WORKTREE_REPOS のworktreeのうち、未コミット変更・未pushコミットが無く、PRがmerge済みのもの
#     （PRが無い場合は、基準ブランチに取り込み済みで STALE_DAYS 触られていないもの）。ブランチは残す
set -u
shopt -s nullglob

CONFIG="${DISK_INVENTORY_CONFIG:-$HOME/.config/disk-inventory/config.sh}"
STATE_DIR="$HOME/Library/Logs/disk-inventory"

MIN_FREE_GB=50
INTERVAL_DAYS=7
STALE_DAYS=14
GROWTH_REPORT_GB=3
# 要素は "リポジトリのパス" か "リポジトリのパス:基準ブランチ"（省略時は origin/HEAD）
WORKTREE_REPOS=()
BUILD_SCAN_ROOTS=()
BUILD_DIR_NAMES=(.next 'DerivedData*')
# 子ディレクトリがすべて同じものの別バージョンであるディレクトリ（glob可）
VERSIONED_PARENTS=("$HOME/.claude/plugins/cache/*/*")
# 子ディレクトリが「名前+バージョン番号」で並ぶディレクトリ。末尾の番号を除いた名前ごとに最新を残す
VERSIONED_PREFIX_PARENTS=("$HOME/Library/Caches/Google" "$HOME/Library/Caches/JetBrains")
# 存在すれば「判断が必要なもの」に載せるパス（glob可）
REVIEW_GLOBS=("$HOME/Library/Application Support/*.old*" "$HOME/Library/Application Support/*/*.old*")
GROWTH_DIRS=("$HOME" "$HOME/Library/Application Support" "$HOME/Library/Caches" "$HOME/Library/Containers" "$HOME/Library/Group Containers")
PROTECT_PATHS=()

# shellcheck source=/dev/null
[ -f "$CONFIG" ] && . "$CONFIG"

APPLY=0
SCHEDULED=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --scheduled) SCHEDULED=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

mkdir -p "$STATE_DIR"

free_gb() { df -k "$HOME" | awk 'NR==2 { print int($4 / 1048576) }'; }
now=$(date +%s)

if [ "$SCHEDULED" = 1 ]; then
  # 空き不足をきっかけにした実行は1日1回まで（消せるものが無いまま毎時の全走査が続かないように）
  last=$(cat "$STATE_DIR/last_run" 2>/dev/null || echo 0)
  retry_at=$(cat "$STATE_DIR/retry_at" 2>/dev/null || echo 0)
  elapsed=$((now - last))
  if [ "$elapsed" -lt $((INTERVAL_DAYS * 86400)) ] \
    && { [ "$elapsed" -lt 86400 ] || [ "$(free_gb)" -ge "$MIN_FREE_GB" ]; } \
    && { [ "$retry_at" = 0 ] || [ "$now" -lt "$retry_at" ]; }; then
    exit 0
  fi
fi

LOCK="$STATE_DIR/lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "another run is in progress ($LOCK)" >&2
  exit 0
fi
TMP=$(mktemp -d)
trap 'rm -rf "$TMP" "$LOCK"' EXIT

DELETED="$TMP/deleted.tsv"   # size_kb \t 対象 \t 理由
REVIEW="$TMP/review.tsv"     # size_kb \t 対象 \t 理由
KEPT="$TMP/kept.tsv"         # 対象 \t 理由（自動削除の条件に当たったが残したもの）
NOTES="$TMP/notes.txt"
: > "$DELETED"; : > "$REVIEW"; : > "$KEPT"; : > "$NOTES"

free_before=$(free_gb)
FAILED=0   # 削除コマンドが1つでも失敗したら、1日後に再試行する（retry_at）

# プロセスが開いているファイルとcwdの一覧。削除フェーズごとに取り直し、取得に失敗したら全パスを使用中とみなす
OPEN_PATHS_OK=0
refresh_open_paths() {
  if lsof -w -Fn > "$TMP/lsof.raw" 2>/dev/null; then
    sed -n 's/^n//p' "$TMP/lsof.raw" | sort -u > "$TMP/open_paths"
    OPEN_PATHS_OK=1
  else
    OPEN_PATHS_OK=0
    echo "lsof が失敗したため、使用中の判定ができないパスは消さなかった" >> "$NOTES"
    FAILED=1
  fi
}

size_kb() { du -sk "$1" 2>/dev/null | cut -f1; }
in_use() {
  [ "$OPEN_PATHS_OK" = 1 ] || return 0
  awk -v p="$1" 'index($0, p "/") == 1 || $0 == p { found = 1; exit } END { exit !found }' "$TMP/open_paths"
}
# 保護パス自身・その配下に加え、保護パスを内包する親も保護する
is_protected() {
  local p
  for p in ${PROTECT_PATHS[@]+"${PROTECT_PATHS[@]}"}; do
    p="${p%/}"
    case "$1" in "$p" | "$p"/*) return 0 ;; esac
    case "$p" in "$1"/*) return 0 ;; esac
  done
  return 1
}
# 消してはいけない理由を返す（消してよければ空）。root を渡したら、その配下であることも求める
deny_reason() {
  local path="$1" root="${2:-}"
  case "$path" in /?*) ;; *) echo "絶対パスでない"; return ;; esac
  case "$path" in *$'\n'*) echo "パスに改行を含む"; return ;; esac
  if [ -n "$root" ]; then
    case "$root" in /?*) ;; *) echo "起点（$root）が絶対パスでない"; return ;; esac
    case "$path" in "${root%/}"/?*) ;; *) echo "起点（$root）の外"; return ;; esac
  fi
  if is_protected "$path"; then echo "PROTECT_PATHSに含まれる"; return; fi
  if in_use "$path"; then echo "プロセスが使用中"; return; fi
}
# 子の名前に改行を含むディレクトリは、改行区切りの列挙で別のパスに化けるので丸ごと飛ばす
has_newline_child() {
  local c
  for c in "$1"/*$'\n'*; do
    echo "$1: 名前に改行を含む子があるため飛ばした" >> "$NOTES"; return 0
  done
  return 1
}
# 最終更新が STALE_DAYS 以内のエントリが深さ2までに1つでもあれば「最近使われている」とみなす
is_fresh() { [ -n "$(find "$1" -maxdepth 2 -mtime "-$STALE_DAYS" -print -quit 2>/dev/null)" ]; }
# 改行区切りで出力するので、改行を含む設定値・展開結果は出さない（分割されて別のパスになるため）
expand_globs() {
  local IFS=$'\n' g p
  for g in "$@"; do
    case "$g" in *$'\n'*) echo "設定値に改行を含むため飛ばした: ${g//$'\n'/\\n}" >> "$NOTES"; continue ;; esac
    for p in $g; do
      case "$p" in *$'\n'*) echo "展開結果に改行を含むため飛ばした: ${p//$'\n'/\\n}" >> "$NOTES"; continue ;; esac
      printf '%s\n' "$p"
    done
  done
}

remove_path() {
  local path="$1" reason="$2" root="$3" why size
  why=$(deny_reason "$path" "$root")
  if [ -n "$why" ]; then printf '%s\t%s\n' "${path//$'\n'/\\n}" "$why" >> "$KEPT"; return; fi
  size=$(size_kb "$path")
  if [ "$APPLY" = 1 ]; then
    rm -rf "$path" || { printf '%s\t%s\n' "$path" "削除に失敗" >> "$KEPT"; FAILED=1; return; }
  fi
  printf '%s\t%s\t%s\n' "${size:-0}" "$path" "$reason" >> "$DELETED"
}

# --- Docker ---------------------------------------------------------------
docker_prune() {
  local label="$1" out; shift
  if out=$("$@" 2>&1); then
    echo "$label: $(printf '%s\n' "$out" | tail -1)" >> "$NOTES"
  else
    echo "$label: 失敗（$(printf '%s\n' "$out" | tail -1)）" >> "$NOTES"
    FAILED=1
  fi
}
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  until_filter="until=$((STALE_DAYS * 24))h"
  if [ "$APPLY" = 1 ]; then
    docker_prune "Docker build cache（${STALE_DAYS}日より古いもの）" docker builder prune -a -f --filter "$until_filter"
    docker_prune "Docker 未使用image（${STALE_DAYS}日より古いもの）" docker image prune -a -f --filter "$until_filter"
  else
    docker system df --format '{{.Type}}: {{.Size}}（回収可能 {{.Reclaimable}}）' 2>/dev/null \
      | sed 's/^/Docker /' >> "$NOTES"
  fi
  vol=$(docker system df --format '{{.Type}}\t{{.Reclaimable}}' 2>/dev/null | awk -F'\t' '$1 == "Local Volumes" { print $2 }')
  [ -n "$vol" ] && case "$vol" in 0B*) ;; *) printf '0\tDocker 未使用volume\t回収可能 %s。消すなら docker volume prune -a\n' "$vol" >> "$REVIEW" ;; esac
else
  echo "Docker: 起動していないため飛ばした" >> "$NOTES"
fi

# --- パッケージマネージャのキャッシュ --------------------------------------
cache_clean() {
  local label="$1" dir="$2"; shift 2
  [ -d "$dir" ] || return
  local why before after
  why=$(deny_reason "$dir")
  if [ -n "$why" ]; then printf '%s\t%s\n' "$dir" "$why" >> "$KEPT"; return; fi
  before=$(size_kb "$dir")
  if [ "$APPLY" = 1 ]; then
    if ! "$@" >/dev/null 2>&1; then
      echo "$label のキャッシュ削除に失敗した" >> "$NOTES"; FAILED=1; return
    fi
    after=$(size_kb "$dir")
    printf '%s\t%s\t%s\n' "$(( ${before:-0} - ${after:-0} ))" "$dir" "$label のキャッシュ" >> "$DELETED"
  else
    printf '%s\t%s\t%s\n' "${before:-0}" "$dir" "$label のキャッシュ（全量。実際に減る量はこれ以下）" >> "$DELETED"
  fi
}
refresh_open_paths
# npm cache clean が消すのは設定値 cache の下の _cacache
command -v npm >/dev/null 2>&1 && cache_clean npm "$(npm config get cache 2>/dev/null)/_cacache" npm cache clean --force
command -v uv >/dev/null 2>&1 && cache_clean uv "$(uv cache dir 2>/dev/null)" uv cache prune
# brew cleanup はキャッシュに加えて旧版のformula本体も消すので使わず、キャッシュ配下の古いファイルだけを消す
if command -v brew >/dev/null 2>&1; then
  brew_cache=$(brew --cache 2>/dev/null)
  case "$brew_cache" in
    "$HOME"/?*) cache_clean Homebrew "$brew_cache" find "$brew_cache" -mindepth 1 -type f -mtime "+$STALE_DAYS" -delete ;;
  esac
fi

# --- バージョン別ディレクトリ ----------------------------------------------
# 残す1つを決めたあと、残りのうち STALE_DAYS 以内に使われていないものだけを消す
remove_old_version() {
  if is_fresh "$1"; then return; fi
  remove_path "$1" "$2" "$3"
}
refresh_open_paths
# 子の名前がハッシュ等で順序を持たないため、ディレクトリの更新日時が最も新しいものを残す
while IFS= read -r parent; do
  [ -d "$parent" ] || continue
  has_newline_child "$parent" && continue
  newest=""
  while IFS= read -r child; do
    child="${child%/}"
    if [ -z "$newest" ]; then newest="$child"; continue; fi
    remove_old_version "$child" "最新版（$(basename "$newest")）以外の旧版" "$parent"
  done < <(ls -1td "$parent"/*/ 2>/dev/null)
done < <(expand_globs ${VERSIONED_PARENTS[@]+"${VERSIONED_PARENTS[@]}"})

# 末尾のバージョン番号を除いた名前ごとに、番号が最も大きいものを残す
while IFS= read -r parent; do
  [ -d "$parent" ] || continue
  has_newline_child "$parent" && continue
  prev_key=""
  while IFS=$'\t' read -r key name; do
    if [ "$key" != "$prev_key" ]; then prev_key="$key"; continue; fi
    remove_old_version "$parent/$name" "$key の最新版以外" "$parent"
  done < <(for c in "$parent"/*/; do
             n=$(basename "$c")
             k=$(printf '%s' "$n" | sed -E 's/[0-9][0-9._-]*$//')
             [ -n "$k" ] && printf '%s\t%s\n' "$k" "$n"
           done | sort -t$'\t' -k1,1 -k2,2rV)
done < <(expand_globs ${VERSIONED_PREFIX_PARENTS[@]+"${VERSIONED_PREFIX_PARENTS[@]}"})

# --- ビルド成果物 ----------------------------------------------------------
refresh_open_paths
if [ ${#BUILD_SCAN_ROOTS[@]} -gt 0 ]; then
  name_expr=()
  for n in "${BUILD_DIR_NAMES[@]}"; do
    [ ${#name_expr[@]} -gt 0 ] && name_expr+=(-o)
    name_expr+=(-name "$n")
  done
  while IFS= read -r root; do
    [ -d "$root" ] || continue
    while IFS= read -r -d '' d; do
      if is_fresh "$d"; then continue; fi
      remove_path "$d" "ビルド成果物（${STALE_DAYS}日更新なし）" "$root"
    done < <(find "$root" \( -name node_modules -o -name .git \) -prune -o -type d \( "${name_expr[@]}" \) -print0 -prune 2>/dev/null)
  done < <(expand_globs "${BUILD_SCAN_ROOTS[@]}")
fi

# --- worktree --------------------------------------------------------------
review_wt() { printf '%s\t%s\t%s\n' "$(size_kb "$1")" "$1" "$2" >> "$REVIEW"; }

# gitディレクトリ全体ではなく logs/HEAD を見る。直前の git status がindexの更新日時を書き換えるため
wt_fresh() {
  local head_log
  head_log="$(git -C "$1" rev-parse --absolute-git-dir)/logs/HEAD"
  is_fresh "$1" || { [ -f "$head_log" ] && [ -n "$(find "$head_log" -mtime "-$STALE_DAYS" 2>/dev/null)" ]; }
}

check_worktree() {
  local repo="$1" base="$2" wt="$3" branch="$4" pr state
  if [ -n "$(git -C "$wt" status --porcelain 2>/dev/null | head -1)" ]; then
    review_wt "$wt" "未コミットの変更あり（${branch:-detached}）"; return
  fi
  if [ "$(git -C "$wt" rev-list --count HEAD --not --remotes=origin 2>/dev/null || echo 1)" != 0 ]; then
    review_wt "$wt" "未pushのコミットあり（${branch:-detached}）"; return
  fi
  if [ -n "$branch" ]; then
    # 同名ブランチの過去のPRを拾わないよう、今のHEADを先頭に持つPRだけを見る
    local head_sha
    head_sha=$(git -C "$wt" rev-parse HEAD)
    if ! pr=$(cd "$repo" && gh pr list --head "$branch" --state all --limit 20 --json state,number,headRefOid \
      -q "map(select(.headRefOid == \"$head_sha\")) | .[0] | if . == null then \"\" else \"\(.state) #\(.number)\" end" 2>/dev/null); then
      review_wt "$wt" "PRの状態を取得できない（$branch）"; return
    fi
    state="${pr%% *}"
    case "$state" in
      MERGED)
        if wt_fresh "$wt"; then
          printf '%s\t%s\n' "$wt" "PR ${pr#* } はmerge済みだが${STALE_DAYS}日以内に使われている" >> "$KEPT"
        else
          remove_worktree "$repo" "$wt" "PR ${pr#* } がmerge済み（$branch）"
        fi
        return ;;
      OPEN) printf '%s\t%s\n' "$wt" "PR ${pr#* } がOPEN" >> "$KEPT"; return ;;
      CLOSED) review_wt "$wt" "PR ${pr#* } がmergeされずにCLOSED（$branch）"; return ;;
    esac
  fi
  # PRが無いブランチとdetached HEADは、基準ブランチに取り込み済みで、しばらく触られていなければ消す
  if git -C "$wt" merge-base --is-ancestor HEAD "$base" 2>/dev/null; then
    if wt_fresh "$wt"; then
      printf '%s\t%s\n' "$wt" "${base}に取り込み済みだが${STALE_DAYS}日以内に使われている" >> "$KEPT"
    else
      remove_worktree "$repo" "$wt" "${base}に取り込み済み・${STALE_DAYS}日使われていない（${branch:-detached}）"
    fi
    return
  fi
  review_wt "$wt" "PRが無く、${base}にも取り込まれていない（${branch:-detached}）"
}

remove_worktree() {
  local repo="$1" wt="$2" reason="$3" why size
  why=$(deny_reason "$wt")
  if [ -n "$why" ]; then printf '%s\t%s\n' "$wt" "$why" >> "$KEPT"; return; fi
  size=$(size_kb "$wt")
  if [ "$APPLY" = 1 ]; then
    git -C "$repo" worktree remove "$wt" 2>>"$NOTES" || { printf '%s\t%s\n' "$wt" "git worktree removeに失敗" >> "$KEPT"; FAILED=1; return; }
  fi
  printf '%s\t%s\t%s\n' "${size:-0}" "$wt" "worktree: $reason" >> "$DELETED"
}

refresh_open_paths
for entry in ${WORKTREE_REPOS[@]+"${WORKTREE_REPOS[@]}"}; do
  repo="${entry%%:*}"
  base="${entry#*:}"; [ "$base" = "$entry" ] && base=""
  [ -d "$repo" ] || continue
  if ! git -C "$repo" fetch -q --prune origin 2>/dev/null; then
    echo "worktree: $repo の fetch に失敗したため飛ばした" >> "$NOTES"; continue
  fi
  [ -n "$base" ] || base=$(git -C "$repo" symbolic-ref -q --short refs/remotes/origin/HEAD)
  [ -n "$base" ] || { echo "worktree: $repo の基準ブランチが決まらないため飛ばした" >> "$NOTES"; continue; }
  main_wt=$(git -C "$repo" rev-parse --show-toplevel)
  wt=""; branch=""; locked=0
  while IFS= read -r line; do
    case "$line" in
      "worktree "*) wt="${line#worktree }"; branch=""; locked=0 ;;
      "branch refs/heads/"*) branch="${line#branch refs/heads/}" ;;
      locked*) locked=1 ;;
      "")
        if [ -n "$wt" ] && [ "$wt" != "$main_wt" ] && [ "$locked" = 0 ] && [ -d "$wt" ]; then
          check_worktree "$repo" "$base" "$wt" "$branch"
        fi
        wt="" ;;
    esac
  done < <(git -C "$repo" worktree list --porcelain; echo)
done

# --- 判断が必要なもの -------------------------------------------------------
while IFS= read -r p; do
  [ -e "$p" ] && printf '%s\t%s\t%s\n' "$(size_kb "$p")" "$p" "退避コピーらしき名前" >> "$REVIEW"
done < <(expand_globs ${REVIEW_GLOBS[@]+"${REVIEW_GLOBS[@]}"})

# --- サイズの記録と前回との比較（削除後の状態で取る） -----------------------
SNAPSHOT="$STATE_DIR/snapshot.tsv"
for d in ${GROWTH_DIRS[@]+"${GROWTH_DIRS[@]}"}; do
  [ -d "$d" ] && du -k -d 1 "$d" 2>/dev/null
done | awk -F'\t' '!seen[$2]++' > "$TMP/snapshot.tsv"
GROWN="$TMP/grown.tsv"
: > "$GROWN"
if [ -f "$SNAPSHOT" ]; then
  awk -F'\t' -v th=$((GROWTH_REPORT_GB * 1048576)) -v home="$HOME" \
    'NR == FNR { prev[$2] = $1; next } $2 != home && ($2 in prev) && $1 - prev[$2] >= th { printf "%d\t%d\t%s\n", $1 - prev[$2], $1, $2 }' \
    "$SNAPSHOT" "$TMP/snapshot.tsv" | sort -rn > "$GROWN"
fi
[ "$APPLY" = 1 ] && cp "$TMP/snapshot.tsv" "$SNAPSHOT"

# --- 報告 ------------------------------------------------------------------
human() { awk -v k="$1" 'BEGIN { if (k >= 1048576) printf "%.1fG", k / 1048576; else printf "%dM", k / 1024 }'; }
free_after=$(free_gb)
deleted_kb=$(awk -F'\t' '{ s += $1 } END { print s + 0 }' "$DELETED")
mode=$([ "$APPLY" = 1 ] && echo "削除を実行" || echo "dry-run（消していない）")
REPORT="$STATE_DIR/report-$(date +%Y%m%d-%H%M).md"
{
  echo "# ディスク棚卸し $(date '+%Y-%m-%d %H:%M')"
  echo
  echo "- モード: $mode"
  echo "- 空き: ${free_before}G → ${free_after}G"
  echo "- 自動削除$([ "$APPLY" = 1 ] && echo "した" || echo "の対象"): $(human "$deleted_kb")（Dockerは下の「その他」に別記）"
  echo
  echo "## 自動削除$([ "$APPLY" = 1 ] && echo "したもの" || echo "の対象")"
  echo
  if [ -s "$DELETED" ]; then
    echo "| サイズ | 対象 | 理由 |"; echo "|---|---|---|"
    sort -rn "$DELETED" | while IFS=$'\t' read -r k p r; do echo "| $(human "$k") | \`$p\` | $r |"; done
  else echo "なし"; fi
  echo
  echo "## 判断が必要なもの（自動では消さない）"
  echo
  if [ -s "$REVIEW" ]; then
    echo "| サイズ | 対象 | 理由 |"; echo "|---|---|---|"
    sort -rn "$REVIEW" | while IFS=$'\t' read -r k p r; do echo "| $([ "$k" = 0 ] && echo - || human "$k") | \`$p\` | $r |"; done
  else echo "なし"; fi
  echo
  echo "## 前回から ${GROWTH_REPORT_GB}G 以上増えた場所"
  echo
  if [ -s "$GROWN" ]; then
    echo "| 増加 | 現在 | 場所 |"; echo "|---|---|---|"
    while IFS=$'\t' read -r g k p; do echo "| +$(human "$g") | $(human "$k") | \`$p\` |"; done < "$GROWN"
  elif [ -f "$SNAPSHOT" ]; then echo "なし"
  else echo "前回の記録が無い（初回）"; fi
  echo
  echo "## 大きい順（上位20）"
  echo
  echo "| サイズ | 場所 |"; echo "|---|---|"
  awk -F'\t' -v home="$HOME" '$2 != home' "$TMP/snapshot.tsv" | sort -rn | head -20 \
    | while IFS=$'\t' read -r k p; do echo "| $(human "$k") | \`$p\` |"; done
  echo
  echo "## 条件に当たったが残したもの"
  echo
  if [ -s "$KEPT" ]; then
    while IFS=$'\t' read -r p r; do echo "- \`$p\`: $r"; done < "$KEPT"
  else echo "なし"; fi
  echo
  echo "## その他"
  echo
  if [ -s "$NOTES" ]; then sed 's/^/- /' "$NOTES"; else echo "なし"; fi
} > "$REPORT" || { echo "failed to write $REPORT" >&2; exit 1; }
ln -sfn "$REPORT" "$STATE_DIR/latest.md"
reports=("$STATE_DIR"/report-*.md)
if [ ${#reports[@]} -gt 10 ]; then
  ls -1t "${reports[@]}" | tail -n +11 | while IFS= read -r old; do rm -f "$old"; done
fi

if [ "$APPLY" = 1 ]; then
  echo "$now" > "$STATE_DIR/last_run"
  if [ "$FAILED" = 0 ]; then rm -f "$STATE_DIR/retry_at"
  else echo $((now + 86400)) > "$STATE_DIR/retry_at"; fi
  review_count=$(wc -l < "$REVIEW" | tr -d ' ')
  osascript -e 'on run argv' -e 'display notification (item 1 of argv) with title "ディスク棚卸し"' -e 'end run' \
    "空き ${free_before}G → ${free_after}G。判断が必要なもの ${review_count}件（${STATE_DIR}/latest.md）" >/dev/null 2>&1
fi
echo "$REPORT"
