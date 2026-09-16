# 直コミット可否の判定

`/commit` の実行前に、対象リポジトリで main / develop へ直接コミットしてよいかを判定する手順。PJ `CLAUDE.md` / `CLAUDE.local.md` に判定結果の記載があればそれに従う。記載が無ければ次の事実を集め、**このリポジトリで自分が実際どう運用してきたか**を読み取って判断する（閾値で機械的に決めない）。判断後は結果を永続化してからコミットする（次回以降の再判定を省くため）。

## 1. ブランチ保護 / ruleset を確認する

履歴からの推測より確実。`pull_request` ルールがあれば直コミットは物理的に不可能:

```bash
BASE=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || echo origin/main)
gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/rules/branches/${BASE#origin/}"
```

- `pull_request` を含むルールが返る → **PR 運用確定**。作業ブランチ必須
- `[]` が返る、または `gh` が使えない → 2 へ

## 2. 履歴を集める

`$BASE` を必ず明示する。省略すると `HEAD` が対象になり、**worktree 内では feature branch の履歴を「base の履歴」として誤読する**:

```bash
MY=$(git config user.email)
git log "$BASE" --format='%ae' | sort | uniq -c | sort -rn | head    # 誰が書いているか
git log "$BASE" --first-parent --no-merges --author="$MY" --format='%h %ce %s' | head -20
                                                                     # 自分の commit が base に直接載っているか
git log "$BASE" --first-parent -20 --format='%h %ce %s'              # 直近の変更がどう入っているか
```

読み取り方:

- 自分のコミットが main に直接並び、PR / merge の痕跡がほとんどない → **直コミット運用**
- 自分のコミットが merge commit 経由、または squash（committer が `noreply@github.com`）でしか入っていない → **PR 運用**。作業ブランチ必須
- 他の書き手が PR を使っていても、自分がほぼ直コミットしているなら直コミット運用として扱う（判定するのは自分の運用実態であって、リポジトリの人数ではない）
- 過去と直近で運用が変わっている場合は直近を優先する（PR 運用へ移行済みの repo で、過去の直コミットを根拠にしない）
- 直コミットと PR が拮抗していて読み取れない場合は、推測せずユーザーに確認する
- 永続化した判定は陳腐化する。記載に従う場合も、記載と直近履歴が食い違うとき（PR 運用へ移行した等）は再判定して記載を更新する

## 3. 判定結果を永続化する

| 書き手 | 永続化先 | 理由 |
|---|---|---|
| 自分のみ | PJ `CLAUDE.md` | 自分しか使わないため、コミットされて問題ない |
| 他にもいる | `CLAUDE.local.md` | 他メンバーの運用に影響させない（git 管理外） |

記載例:

```markdown
## コミット運用
全コミットが自分の直コミットで、PR/merge の痕跡なし（判定日: YYYY-MM-DD）。main への直コミットを許容する。
```

## ブランチ作り直し時

既存コミットを rebase / cherry-pick で保全してからブランチを削除する（コミット消失防止。手順の詳細は `context/worktree-guide.md`）。
