# worktree運用ガイド（詳細手順）

worktreeの作成・ブランチ命名・片付け・並列bg sessionの手順。worktreeを切るかどうかはAGENTS.md「コミット・ブランチ・PR」のworktreeの項、Codexでの扱いは `context/tool-codex.md` のツール対応表。

## 前提（settings.json設定済み）

`worktree.bgIsolation: "none"` / `worktree.baseRef: "fresh"` を設定済み。
- `bgIsolation: "none"` はbg sessionの自動worktree隔離を抑止する設定。これによりbg sessionは元repoのworking directoryで起動し、元repoの `.local/memory/` に直接アクセスできる（隔離されると到達不能になるため必要）
- 副作用: 並列bg sessionが同じファイルを編集すると競合する。これは「コード編集を伴う作業では明示的にEnterWorktreeを呼ぶ」運用で回避する（foreground/bg session共通）

## worktree作成とブランチ命名フロー（新規ブランチの場合）

EnterWorktreeの `name` パラメータはsanitizeされる（`/` → `+`）。さらにブランチ名は強制で `worktree-<sanitized-name>` になるため、`name: 'feature/foo'` を渡してもブランチは `worktree-feature+foo` になり、`feature/` で統一できない。

そのため次のフローで作る:
1. `git fetch origin` でoriginを最新化（baseRef `fresh` の起点を最新に）
2. ブランチ名衝突確認: `git branch -a` で、想定する `feature/<issue_num>-<title-kebab>` および一時ブランチ `worktree-<title-kebab>` のどちらも既存と衝突しないことを確認。衝突する場合はtitleを変えるか、ユーザーに確認（並列bg sessionで同じtitleを選ぶとEnterWorktree自体が失敗する）
3. `EnterWorktree(name: '<title-kebab>')` （例: `name: 'add-foo-123'`）→ worktree作成、ブランチは `worktree-<title-kebab>`
4. 直後に `git branch -m worktree-<title-kebab> feature/<issue_num>-<title-kebab>` で改名（例: `git branch -m worktree-add-foo-123 feature/123-add-foo`）。改名後のブランチは `git worktree list` にも反映される
5. 以後は `feature/<issue_num>-<title-kebab>` ブランチで作業

## EnterWorktreeが使えないケースと回避策（実測）

- **cwdがgit管理外**（例: 複数repoを束ねる親ディレクトリ直下）ではEnterWorktreeツール自体が使えない → 対象repo内で `git worktree add <path> -b <branch>` を手動実行し、EnterWorktreeには作成済みworktreeのパスを渡して移動する
- **既にworktree内のセッション**からはEnterWorktree(name) による新規作成+改名フローが使えない → 同様に `git worktree add` を手動実行してからEnterWorktreeにパスを渡す
- 手動 `git worktree add` の場合は `-b feature/<issue_num>-<title-kebab>` でブランチ名を直接指定できるため、改名ステップは不要

## 既存ブランチで作業を再開する場合

ケースが複雑なため（既存worktree残存有無、remote-onlyブランチ、別worktreeでcheckout済み等）、固定フローを規定しない。再開時は `git worktree list` と `git branch -a` で現状を確認し、判断に迷う点があればユーザーに方針を確かめる。

## baseRefとBASE_BRANCHの不一致

baseRefは `fresh`（origin/<default-branch> 起点）。PJ CLAUDE.mdの `BASE_BRANCH` が `origin/<default-branch>` と異なる場合（例: defaultが `main` だがPRベースは `develop`）、worktree起点とPRベースがずれる。その場合はEnterWorktree後に `git rebase <BASE_BRANCH>` 等でbaseを揃えるか、ユーザーに確かめる。

## worktreeとブランチの片付け

後片付けは確認を待たずに行う（AGENTS.md「進め方の既定」）。次の全てを満たすworktreeは削除し、マージ済みのブランチは `git branch -d` で消す:

- 実機検証・動作確認が完了している、またはworktreeでの作業自体が終わっている
- 未コミットの変更がない（`git status` で確認）
- そのブランチのコミットがマージ済み、またはpush済みでPRに載っている（未pushのコミットがあるなら消さずに報告する。保全が先）

`git branch -d` はマージされていないブランチを消さないので、確認なしで使ってよい。`git branch -D`（強制削除）はマージされていないコミットを失うので、実行前にユーザーに確かめる（AGENTS.md「確認が要るもの」の緩和しない安全項目）。未pushのコミットを持つブランチを消したいときは、rebase / cherry-pickで別ブランチに保全してから消す。

`ExitWorktree(action: 'remove')` は、EnterWorktreeが作った元のブランチ名（`worktree-<sanitized>`）を削除しようとする。上記フローで `feature/...` に改名している場合、改名後のブランチは消えない。改名後のブランチはPR作成・マージまで残し、マージされたら `git branch -d` で消す。

## EnterWorktree/ExitWorktreeの状態管理（実測トラブルシュート）

以下のエラーパターンが頻出する。いずれも「今どのworktree状態にいるか」の見失いが原因。

- **`Already in a worktree session`**: 既にEnterWorktree済みのセッションで再度EnterWorktreeしようとした。新規worktreeが必要なら先にExitWorktree（またはpathを渡して切替）する
- **`No-op: there is no active EnterWorktree session to exit`**: ExitWorktreeが対応するセッションを特定できていない（compaction後に多い）。実行前に`git worktree list`で実際の状態を確認してから判断する
- **`Worktree has N commits. Removing will discard this work permanently`**: ExitWorktreeはコミット済み作業があるとworktreeの削除を止める。`git log`でコミット有無とマージ・push状況を確認する。マージ済みかpush済みなら `discard_changes: true` で消してよい。未pushのコミットが残るなら `action: "keep"` 相当で残し、報告する

## 並列bg sessionの指針

- 各bg sessionが自分でEnterWorktreeを呼べば、作業ディレクトリ上での同時編集競合は回避できる（注: 別ブランチで同じファイルを編集すれば、後続のmerge/rebase/PR統合時には別途競合し得る）
- 各bg sessionは独立して起動され（`claude agents` のAgent Viewからdispatch等）、自分でPhase 0を実施して自分の `.local/memory/YYMMDD_<context_name>/` を作るため、`05_log.md` は自然に別ファイルで競合しない
- **共有リソース（開発サーバー・DB・ブラウザ自動化）を使う検証は、開始前に使用中かを機械的に確認する**（ポートの占有・プロセスの生存）。使用中なら他セッションが検証中と判断して開始を控える。worktreeを分けても、ローカルの検証環境は分かれない
