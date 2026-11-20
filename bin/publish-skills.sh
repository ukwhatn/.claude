#!/bin/bash
# 公開するスキルを marketplace の repo（ukwhatn/skills）に書き出し、検査を通ったときだけ 1 コミットで push する。
# 定期起動「.claude update」の最後に呼ぶ。
#
# 使い方: publish-skills.sh <公開 repo の作業ツリー> <ジョブのディレクトリ>
#   ジョブのディレクトリ（git の追跡外）に置くもの:
#     scan_public.py   公開前の検査（社内の名前の一覧を含むので、公開する repo には置かない）
#     agents-checked   AGENTS.md を最後に確認した ~/.claude の commit
#     logs/            実行ごとのログ
#
# 出力の行:
#   PUSHED <sha> <版>      push した
#   UNCHANGED              書き出した内容に変更が無い
#   AGENTS_CHANGED <範囲>  AGENTS.md が前回の確認から変わった。dev-flow への反映の要否を人が確かめる
# 終了コード:
#   0 = push した、または変更なし
#   3 = 前提が合わず中断した（何も変えていない）
#   4 = 書き出しか検査に落ち、作業ツリーを origin/main に戻して中断した
#   5 = push に失敗した（手元のコミットは残る。次の回は前提の確認で中断する）
set -u

dst=${1:?公開 repo の作業ツリーを渡す}
job=${2:?ジョブのディレクトリを渡す}
src="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
mkdir -p "$job/logs"
exec > >(tee -a "$job/logs/$(date +%Y%m%d-%H%M%S).log") 2>&1

abort() { echo "中断: $1"; exit 3; }
restore() {
  # 検査に落ちた内容をコミットとして残さない。作業ツリーの中だけを origin の状態に戻す
  git -C "$dst" reset -q --hard origin/main && git -C "$dst" clean -qfd
  echo "origin/main に戻して中断: $1"
  exit 4
}

[ -d "$dst/.git" ] || abort "$dst は git の作業ツリーでない"
[ -f "$job/scan_public.py" ] || abort "$job/scan_public.py が無い"

# AGENTS.md は dev-flow の原本だが、書き出しは節の見出ししか照合しない。変わったら人が反映の要否を見る
now=$(git -C "$src" rev-parse HEAD)
checked=$(cat "$job/agents-checked" 2>/dev/null || true)
if [ -n "$checked" ] && ! git -C "$src" diff --quiet "$checked" "$now" -- AGENTS.md; then
  echo "AGENTS_CHANGED ${checked:0:7}..${now:0:7}"
fi
echo "$now" > "$job/agents-checked"

git -C "$dst" fetch -q origin || abort "fetch に失敗した"
[ "$(git -C "$dst" rev-parse HEAD)" = "$(git -C "$dst" rev-parse origin/main)" ] || abort "作業ツリーの HEAD が origin/main と違う"
[ -z "$(git -C "$dst" status --porcelain)" ] || abort "作業ツリーに変更か未追跡のファイルがある"
# 書き出しは原本の作業ツリーを読むので、コミットしていない変更があると、それが公開される
[ -z "$(git -C "$src" status --porcelain -- skills context hooks output-styles publish vendor bin/export-skills.py)" ] \
  || abort "~/.claude の公開する範囲にコミットしていない変更がある"

python3 "$src/bin/export-skills.py" "$dst" || restore "書き出しの検査"
git -C "$dst" add -A
if git -C "$dst" diff --cached --quiet; then
  echo "UNCHANGED"
  exit 0
fi
python3 "$job/scan_public.py" "$dst" --no-ocr || restore "公開前の検査"
(cd "$dst" && gitleaks dir --no-banner --redact .) || restore "gitleaks"

GIT_AUTHOR_NAME="Yuki Watanabe" GIT_AUTHOR_EMAIL="ukwhatn@gmail.com" \
GIT_COMMITTER_NAME="Yuki Watanabe" GIT_COMMITTER_EMAIL="ukwhatn@gmail.com" \
  git -C "$dst" commit -q -m "chore: ~/.claude ${now:0:7} から書き出し" || restore "コミット"
git -C "$dst" push -q origin HEAD:main || { echo "push に失敗した"; exit 5; }
echo "PUSHED $(git -C "$dst" rev-parse --short HEAD) $(jq -r '.name + " " + .version' "$dst"/plugins/*/.claude-plugin/plugin.json | tr '\n' ' ')"
