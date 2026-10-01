# worktree運用ガイド（詳細手順）

Read when: worktree作成（Claude Code: EnterWorktree）の実行前、worktreeの片付け（ExitWorktree・ブランチ削除）前、並列bg sessionの設計時。
発動条件・例外はAGENTS.md「worktree運用ルール」を参照（本ファイルは手順の詳細のみ）。

> ツール対応: EnterWorktree / ExitWorktreeはClaude Codeのツール。Codex等では `git worktree add <path> -b feature/<issue_num>-<title-kebab>` / `git worktree remove <path>` を直接実行し、本ガイドのブランチ命名・コミット保全・競合回避の原則に従う（この場合、下記のsanitize・改名フローは不要でブランチ名を直接指定できる）。

## 前提（settings.json設定済み）

`worktree.bgIsolation: "none"` / `worktree.baseRef: "fresh"` を設定済み。
- `bgIsolation: "none"` はbg sessionの自動worktree隔離を抑止する設定。これによりbg sessionは元repoのworking directoryで起動し、元repoの `.local/memory/` に直接アクセスできる（隔離されると到達不能になるため必要）
- **副作用**: 並列bg sessionが同じファイルを編集すると競合する。これは「コード編集を伴う作業では明示的にEnterWorktreeを呼ぶ」運用で回避する（foreground/bg session共通）

## worktree作成とブランチ命名フロー（新規ブランチの場合）

EnterWorktreeの `name` パラメータはsanitizeされる（`/` → `+`）。さらに **ブランチ名は強制で `worktree-<sanitized-name>`** になるため、`name: 'feature/foo'` を渡してもブランチは `worktree-feature+foo` になり、`feature/` で統一できない。

そのため以下のフローを必ず踏むこと:
1. `git fetch origin` でoriginを最新化（baseRef `fresh` の起点を最新に）
2. **ブランチ名衝突確認**: `git branch -a` で、想定する `feature/<issue_num>-<title-kebab>` および一時ブランチ `worktree-<title-kebab>` のどちらも既存と衝突しないことを確認。衝突する場合はtitleを変えるか、ユーザーに確認（並列bg sessionで同じtitleを選ぶとEnterWorktree自体が失敗する）
3. `EnterWorktree(name: '<title-kebab>')` （例: `name: 'add-foo-123'`）→ worktree作成、ブランチは `worktree-<title-kebab>`
4. **直後に** `git branch -m worktree-<title-kebab> feature/<issue_num>-<title-kebab>` で改名（例: `git branch -m worktree-add-foo-123 feature/123-add-foo`）。改名後のブランチは `git worktree list` にも反映される
5. 以後は `feature/<issue_num>-<title-kebab>` ブランチで作業

## EnterWorktreeが使えないケースと回避策（実測）

- **cwdがgit管理外**（例: 複数repoを束ねる親ディレクトリ直下）ではEnterWorktreeツール自体が使えない → 対象repo内で `git worktree add <path> -b <branch>` を手動実行し、EnterWorktreeには作成済みworktreeのパスを渡して移動する
- **既にworktree内のセッション**からはEnterWorktree(name) による新規作成+改名フローが使えない → 同様に `git worktree add` を手動実行してからEnterWorktreeにパスを渡す
- 手動 `git worktree add` の場合は `-b feature/<issue_num>-<title-kebab>` でブランチ名を直接指定できるため、改名ステップは不要

## 既存ブランチで作業を再開する場合

ケースが複雑なため（既存worktree残存有無、remote-onlyブランチ、別worktreeでcheckout済み等）、固定フローを規定しない。再開時は `git worktree list` と `git branch -a` で現状を確認し、判断に迷う点があればユーザーに方針確認すること。

## baseRefとBASE_BRANCHの不一致

baseRefは `fresh`（origin/<default-branch> 起点）。PJ CLAUDE.mdの `BASE_BRANCH` が `origin/<default-branch>` と異なる場合（例: defaultが `main` だがPRベースは `develop`）、worktree起点とPRベースがずれる。その場合はEnterWorktree後に `git rebase <BASE_BRANCH>` 等でbaseを揃えるか、ユーザーに確認すること。

## worktreeの片付け（ExitWorktreeの注意）

**消して良い状況なら、確認を待たずにworktreeを削除する**（ユーザーの恒久指示）。消して良い状況とは、次の全てを満たすとき:

- 実機検証・動作確認が完了している、またはworktreeでの作業自体が終わっている
- 未コミットの変更がない（`git status` で確認）
- そのブランチのコミットがpush済み、またはPRに載っている（未pushのコミットがあるなら削除しない。保全が先）

**worktreeの削除は確認不要だが、ブランチの削除は別扱い**（`-D` は破壊的操作として事前確認が必要。下記）。

`ExitWorktree(action: 'remove')` は **EnterWorktreeが作った元のブランチ名**（`worktree-<sanitized>`）を削除しようとする。上記フローで `feature/...` に改名している場合、改名後のブランチは消えない。
- **基本方針**: 改名後ブランチは残す（PR作成・マージのため）
- 不要ブランチを削除する場合は `/commit` スキルの `references/commit-policy.md`（ブランチ作り直し時）に従う:
  - **`-D`（強制削除）は使用前にユーザー確認必須**（破壊的操作。mergeされていないコミットを失う。permissions.denyにも登録済）
  - 未pushのコミットがあれば、rebase/cherry-pickで別ブランチに保全してから削除
  - merge済み・コミットなしの場合は `git branch -d <name>` （安全削除）を優先

## EnterWorktree/ExitWorktreeの状態管理（実測トラブルシュート）

以下のエラーパターンが頻出する。いずれも「今どのworktree状態にいるか」の見失いが原因。

- **`Already in a worktree session`**: 既にEnterWorktree済みのセッションで再度EnterWorktreeしようとした。新規worktreeが必要なら先にExitWorktree（またはpathを渡して切替）する
- **`No-op: there is no active EnterWorktree session to exit`**: ExitWorktreeが対応するセッションを特定できていない（compaction後に多い）。実行前に`git worktree list`で実際の状態を確認してから判断する
- **`Worktree has N commits. Removing will discard this work permanently`**: ExitWorktreeはコミット済み作業があるとworktreeの削除を止める。`git log`でコミット有無を確認し、残す場合は`action: "keep"`相当、破棄してよいとユーザーに確認済みの場合のみ`discard_changes: true`を明示する
- **compaction対策**: 現在worktree内にいるか・そのpath/ブランチ名はcompactionで失われやすい状態情報。長時間タスクではcompaction前に05_log.mdへ明記する（AGENTS.mdのCompact Instructions参照）

## 並列bg sessionの指針

- 各bg sessionが自分でEnterWorktreeを呼べば、**作業ディレクトリ上での同時編集競合**は回避できる（注: 別ブランチで同じファイルを編集すれば、後続のmerge/rebase/PR統合時には別途競合し得る）
- 各bg sessionは独立して起動され（`claude agents` のAgent Viewからdispatch等）、自分でPhase 0を実施して自分の `.local/memory/YYMMDD_<context_name>/` を作るため、`05_log.md` は自然に別ファイルで競合しない
- メモリ・issueファイルへの書き込みは必ず **Phase 0で確定した元repoの絶対パス**で行うこと（worktree内には `.local/` が存在しないため）
- 一時ファイル（スクリプト・クエリ・中間出力等）は `/tmp` ではなく **システムプロンプトが示すscratchpadディレクトリ**に置く（並列bg sessionが `/tmp` を共有して上書きするため）
- **共有リソース（開発サーバー・DB・ブラウザ自動化）を使う検証は、開始前に使用中かを機械的に確認する**（ポートの占有・プロセスの生存）。使用中なら他セッションが検証中と判断して開始を控える。worktreeを分けても、ローカルの検証環境は分かれない
