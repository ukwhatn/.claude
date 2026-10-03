---
name: taskboard
description: taskboard の MCP tool（board_overview / task_get / task_create / task_update / work_list / work_add / work_update / session_list / session_prompt）でタスクと作業項目を扱う。自分のセッションに紐づくタスクの列を進める・起票する時、計画の承認後に作業項目を登録し着手・完了・待ちを更新する時、ボードの一覧・状態を確認する時、依頼に taskboard・タスクボード・kanban・作業項目の語がある時に使用。境界: pane・tab・agent の操作は herdr、作業ログ・調査記録はメモリディレクトリ、ボードの画面操作はユーザーの領域。
---

# Taskboard

タスク 1 件に、エージェントセッション・PR・Issue・チケット・作業項目を束ねるボード。状態は各 Mac の daemon が持ち、セッションは MCP tool（server 名 `taskboard`）で読み書きする。アプリ（Mac / iPad / iPhone）は同じ daemon を見る。

## 前提

ツール一覧に `mcp__taskboard__*` があること。無ければ「taskboard の MCP が繋がっていない（`claude mcp list` で確認）」と伝えて止まる。CLI や API を推測して直接叩かない。

`task_id` を省くと、このセッションに紐づくタスクを使う。紐づけは SessionStart hook が herdr の pane（`HERDR_PANE_ID`）経由で行うので、herdr の pane の外では `task_id` が必須。`work_list` が「紐づくタスクが無い」と返したら `board_overview` で候補を見て、`task_update` の `link_session: true` で結ぶか、`task_create` で起票する。

## 列

列の id はボードごとに違うことがある。`board_overview` が返す id を使い、ハードコードしない。役割で選ぶ:

| 状況 | 列の役割 | 標準的な id |
|---|---|---|
| 他人の PR・チケットのレビューを頼まれた | 受け口（レビュー投稿後もマージまで留まる） | `review_req` |
| やると決まったが未着手 | 待ち | `todo` |
| 方針・設計を詰めている | 計画 | `planning` |
| 実装・調査を実際に進めている | 作業中 | `working` |
| PR を出してレビュー待ち | レビュー | `review` |
| approve 済みで反映・リリース待ち | 反映待ち | `deploying` |
| 完了した | 終端 | `done` |
| やらないと決めた | 終端 | `wontfix` |

## 自分のセッションのタスクを進める

**自律的に動かしてよいのは、自分のセッションに紐づくタスクだけ。** 他のタスクの列・作業項目は、ユーザーの指示なしに変えない。

**PR の状態に対応する列の前進は daemon が自動で行う**（PR が ready なら `review`、merge されれば `deploying`。前進方向のみ、終端列と `review_req` は触らない。Stop hook でも同じ判定が走る）。この 2 つを手で `task_update` しに行かない。手で動かすのは daemon が判断しない列（`planning` / `working` / `wontfix` 等）と、ユーザーから指示された移動だけ。

**`review_req` に入ったタスクは `review_req` と終端列しか取らない。** 紐づいているのは他人の PR なので、自分が approve しても作業段階は進まない。レビューを投稿したらタイトルの頭に `✅ ` を付けて `review_req` に留め、`done` へ移すのはリンク先の PR がマージされてから。

**紐づくタスクが無い状態で PR が open していれば、Stop hook が自動起票する**（タイトルは PR のタイトル、列は draft なら `working` / ready なら `review`、PR URL をリンク、セッションを紐づけ）。同じ URL のタスクが既にあれば起票せずそれに紐づける。

列を動かすのは**確認できた事実に対応する遷移だけ**。自分が実行した操作（PR を出した・merge した）と `task_get` の内容が根拠になる。根拠なく先の列へ進めない。判断がつかないときは動かさず、ユーザーに聞く。

## 作業項目

タスクの中の計画を daemon に持たせ、ボードのカード・タスク画面・iPhone に「今どこまで進んで、何を待っているか」を出す。

- **計画が承認されたら、全項目を `work_add` で登録する**（Phase 2 の計画書の作業項目と 1 対 1。1 項目 = PR 1 本か、PR 内の 1 段階）。順序は計画順。前の項目が終わらないと始められないものは `depends_on`
- **着手で `state: doing`、終わったら `state: done`** と成果物（`deliverable_kind` / `deliverable_ref`: PR の URL、コミットの SHA、ファイルのパス、文書の id）
- **待ちに入ったら `state: wait` と `blocker_kind`**（`approval` 自分の承認か回答 / `review` 他者のレビュー / `ci` / `deploy` / `item` 別の項目 / `external`）と `blocker_text` 1 行。待ちが解けて作業に戻るときに `doing` へ動かすと blocker は消える
- **委譲した項目は `owner`** に委譲先の名前（herdr の agent 名）。自分なら省く
- やらないと決めた項目は `state: drop`（母数から外れる）
- `work_list` は計画順に状態・待ち理由・成果物・依存を返す。再開・compaction 復帰の後は、メモリの記録より先にこれを読んで今の状態を取る

完了基準: `work_update` の応答が意図した状態になっている。

## 起票する

**起票の前に、紐づける URL で既存タスクを引く**（`board_overview` に PR の短縮名が出る。同一性は URL で判断し、タイトルでは照合しない）。`task_create` は同じ URL のタスクがあればエラーで止まるので、そのときは返ってきた番号に `task_update` で足す。

- **粒度は「1 タスク = 1 つの完了判定」**。PR 1 本・チケット 1 件・調査 1 件が単位。複数 PR にまたがる 1 つの作業は、束ねる 1 タスクにリンクを複数付ける（PR ごとに割らない。PR ごとの進みは作業項目で表す）
- **タイトルは、何が終われば完了かが読み取れる形にする。** チケット由来ならチケット側の表題をそのまま使う
- `note` には**セッションをまたいで必要になる文脈だけ**を書く（決めた方針・詰まっている点・再開条件）。作業ログはメモリディレクトリ側に書く
- 起票するとこのセッションが紐づく（`link_session: false` で結ばない）

## 別のセッションへ送る

`session_list` で pane と状態を見て、`session_prompt` で文字を送る。委譲先への指示と、止まっている自分の委譲先への返答に使う。**動いている人のセッション（`working`）と、自分が起こしたのでないセッションには送らない。**

## Gotchas

- **`work_update` で `wait` にするときは `blocker_kind` か `blocker_text` が必須**（無いとエラー）
- **`task_id` の解決は herdr の pane 経由**。herdr の外（CI・単発の `claude -p`）では毎回 `task_id` を渡す
- **タスク番号は削除しても再利用されない。** 一度得た番号は安定した handle として使える
- **daemon が止まっていると tool はエラーを返す。** その旨を伝え、`launchctl kickstart -k gui/$UID/uk.whatn.taskboardd` を案内する（自分では実行しない）

## 既存設定との関係

- **pane・tab・agent そのものの操作**: /herdr（本スキルは taskboard の tool だけを扱う）
- **作業ログ・調査記録**: @context/memory-file-formats.md（note・作業項目と使い分ける）
