# worktree 運用ガイド（詳細手順）

Read when: worktree作成（Claude Code: EnterWorktree）の実行前、worktreeの片付け（ExitWorktree・ブランチ削除）前、並列bg sessionの設計時。
発動条件・例外はAGENTS.md「worktree 運用ルール」を参照（本ファイルは手順の詳細のみ）。

> ツール対応: EnterWorktree / ExitWorktree は Claude Code のツール。Codex 等では `git worktree add <path> -b feature/<issue_num>-<title-kebab>` / `git worktree remove <path>` を直接実行し、本ガイドのブランチ命名・コミット保全・競合回避の原則に従う（この場合、下記の sanitize・改名フローは不要でブランチ名を直接指定できる）。

## 前提（settings.json設定済み）

`worktree.bgIsolation: "none"` / `worktree.baseRef: "fresh"` を設定済み。
- `bgIsolation: "none"` は bg session の自動 worktree 隔離を抑止する設定。これにより bg session は元repoの working directory で起動し、元repoの `.local/memory/` に直接アクセスできる（隔離されると到達不能になるため必要）
- **副作用**: 並列 bg session が同じファイルを編集すると競合する。これは「コード編集を伴う作業では明示的に EnterWorktree を呼ぶ」運用で回避する（foreground/bg session 共通）

## worktree 作成とブランチ命名フロー（新規ブランチの場合）

EnterWorktree の `name` パラメータは sanitize される（`/` → `+`）。さらに **ブランチ名は強制で `worktree-<sanitized-name>`** になるため、`name: 'feature/foo'` を渡してもブランチは `worktree-feature+foo` になり、`feature/` で統一できない。

そのため以下のフローを必ず踏むこと:
1. `git fetch origin` で origin を最新化（baseRef `fresh` の起点を最新に）
2. **ブランチ名衝突確認**: `git branch -a` で、想定する `feature/<issue_num>-<title-kebab>` および一時ブランチ `worktree-<title-kebab>` のどちらも既存と衝突しないことを確認。衝突する場合は title を変えるか、ユーザーに確認（並列 bg session で同じ title を選ぶと EnterWorktree 自体が失敗する）
3. `EnterWorktree(name: '<title-kebab>')` （例: `name: 'add-foo-123'`）→ worktree 作成、ブランチは `worktree-<title-kebab>`
4. **直後に** `git branch -m worktree-<title-kebab> feature/<issue_num>-<title-kebab>` で改名（例: `git branch -m worktree-add-foo-123 feature/123-add-foo`）。改名後のブランチは `git worktree list` にも反映される
5. 以後は `feature/<issue_num>-<title-kebab>` ブランチで作業

## EnterWorktree が使えないケースと回避策（実測）

- **cwd が git 管理外**（例: 複数repoを束ねる親ディレクトリ直下）では EnterWorktree ツール自体が使えない → 対象repo内で `git worktree add <path> -b <branch>` を手動実行し、EnterWorktree には作成済み worktree のパスを渡して移動する
- **既に worktree 内のセッション**からは EnterWorktree(name) による新規作成+改名フローが使えない → 同様に `git worktree add` を手動実行してから EnterWorktree にパスを渡す
- 手動 `git worktree add` の場合は `-b feature/<issue_num>-<title-kebab>` でブランチ名を直接指定できるため、改名ステップは不要

## 既存ブランチで作業を再開する場合

ケースが複雑なため（既存 worktree 残存有無、remote-only ブランチ、別 worktree で checkout 済み等）、固定フローを規定しない。再開時は `git worktree list` と `git branch -a` で現状を確認し、判断に迷う点があればユーザーに方針確認すること。

## baseRef と BASE_BRANCH の不一致

baseRef は `fresh`（origin/<default-branch> 起点）。PJ CLAUDE.md の `BASE_BRANCH` が `origin/<default-branch>` と異なる場合（例: default が `main` だが PR ベースは `develop`）、worktree 起点と PR ベースがずれる。その場合は EnterWorktree 後に `git rebase <BASE_BRANCH>` 等で base を揃えるか、ユーザーに確認すること。

## worktree の片付け（ExitWorktree の注意）

`ExitWorktree(action: 'remove')` は **EnterWorktree が作った元のブランチ名**（`worktree-<sanitized>`）を削除しようとする。上記フローで `feature/...` に改名している場合、改名後のブランチは消えない。
- **基本方針**: 改名後ブランチは残す（PR 作成・マージのため）
- 不要ブランチを削除する場合は AGENTS.md「コミット・ブランチ・PR」の「ブランチ作り直し時」ルールに従う:
  - **`-D`（強制削除）は使用前にユーザー確認必須**（破壊的操作。merge されていないコミットを失う。permissions.deny にも登録済）
  - 未 push のコミットがあれば、rebase/cherry-pick で別ブランチに保全してから削除
  - merge 済み・コミットなしの場合は `git branch -d <name>` （安全削除）を優先

## 並列 bg session の指針

- 各 bg session が自分で EnterWorktree を呼べば、**作業ディレクトリ上での同時編集競合**は回避できる（注: 別ブランチで同じファイルを編集すれば、後続の merge/rebase/PR 統合時には別途競合し得る）
- 各 bg session は独立して起動され（`claude agents` の Agent View から dispatch 等）、自分で Phase 0 を実施して自分の `.local/memory/YYMMDD_<context_name>/` を作るため、`05_log.md` は自然に別ファイルで競合しない
- メモリ・issue ファイルへの書き込みは必ず **Phase 0 で確定した元repoの絶対パス**で行うこと（worktree 内には `.local/` が存在しないため）
- 一時ファイル（スクリプト・クエリ・中間出力等）は `/tmp` ではなく **`$CLAUDE_JOB_DIR`** を使う（並列 bg session が `/tmp` を共有して上書きするため）
