---
name: taskboard
description: taskboard の MCP tool（board_overview / session_guide / task_get / task_create / task_update / work_list / work_add / work_update / session_list / session_start / session_prompt / doc_publish / doc_list / ask_user / review_request / feedback_list / comment_reply）でタスク・作業項目・文書を扱う。自分のセッションに紐づくタスクの列を進める・起票する時、計画の承認後に作業項目を登録し着手・完了・待ちを更新する時、計画書・設計提案を人に読ませて採否やレビューを求める時、ボードの一覧・状態を確認する時、依頼に taskboard・タスクボード・kanban・作業項目の語がある時に使用。境界: taskboard の外で始まったセッションをタスクに移すのは taskboard-adopt、pane・tab・agent の操作は herdr、作業ログ・調査記録はメモリディレクトリ、ボードの画面操作はユーザーの領域。
---

# Taskboard

タスク 1 件に、エージェントセッション・PR・Issue・チケット・作業項目を束ねるボード。状態は各 Mac の daemon が持ち、セッションは MCP tool（server 名 `taskboard`）で読み書きする。アプリ（Mac / iPad / iPhone）は同じ daemon を見る。

## 前提

ツール一覧に `mcp__taskboard__*` があること。無ければ「taskboard の MCP が繋がっていない（`claude mcp list` で確認）」と伝えて止まる。CLI や API を推測して直接叩かない。

`task_id` を省くと、このセッションに紐づくタスクを使う。セッションは、taskboard の herdr の pane なら pane（`HERDR_PANE_ID`）で、その外の Claude Code なら MCP に渡るセッション ID（`CLAUDE_CODE_SESSION_ID`）で見分ける。taskboard が起動したセッションは SessionStart hook が結ぶ。`work_list` が「紐づくタスクが無い」と返したら `board_overview` で候補を見て、`task_update` の `link_session: true` で結ぶか、`task_create` で起票する。taskboard の外で始まった作業をまとめて移すときは /taskboard-adopt スキルを実行する。

結んだ後の案内（タスク・今の列・案件の列の説明）は `session_guide` で読める。SessionStart の案内が無いセッションで結んだとき、圧縮で案内が消えたと感じたときに読む。

## 列

**列は案件の列の説明に従って選ぶ。** 列の id・名前・説明は案件ごとに違い、人が直せる（既定の列を消した案件、列を足した案件もある）。説明は SessionStart の案内・`session_guide`・`task_get`（今の列）・`task_update`（移した先）・`board_overview` に出る。id をハードコードしない。

新しい案件の既定の列（参考。今の案件の説明が優先する）:

| 列の名前 | 既定の説明 | 標準的な id |
|---|---|---|
| 常設 | 期限なく続く仕事（定常の運用・問い合わせ対応など）。完了にしない | `standing` |
| レビュー依頼 | 他人の PR・チケットのレビューを頼まれたタスク。レビューを出してもマージまでここに置き、自分の作業の列へ移さない | `review_req` |
| 未着手 | やると決めたが、まだ始めていない | `todo` |
| 計画 | 方針・設計を詰めている | `planning` |
| 作業中 | 実装・調査を進めている | `working` |
| レビュー中 | PR を出してレビューを待っている | `review` |
| デプロイ中 | 承認され、反映・リリースを待っている | `deploying` |
| 完了 | 終わった | `done` |
| 見送り | やらないと決めた | `wontfix` |

## 自分のセッションのタスクを進める

**自律的に動かしてよいのは、自分のセッションに紐づくタスクだけ。** 他のタスクの列・作業項目は、ユーザーの指示なしに変えない。

**PR の状態に対応する列の前進は daemon が自動で行う**（PR が ready なら `review`、merge されれば案件の「マージしたら」の列（既定は `deploying`。その列を消した案件では `done`）。前進方向のみで、終端列・常設・足した列は触らず、進める先の列が案件に無ければ動かさない。Stop hook でも同じ判定が走る）。この前進を手で `task_update` しに行かない。手で動かすのは daemon が判断しない列（`planning` / `working` / `wontfix` 等）と、ユーザーから指示された移動だけ。

**`review_req` に入ったタスクは `review_req` と終端列しか取らない。** 紐づいているのは他人の PR なので、自分が approve しても作業段階は進まない。レビューを投稿したらタイトルの頭に `✅ ` を付けて `review_req` に留める。紐づく PR が全部マージかクローズになると daemon が `done` へ進めるので、手で `done` へ移さない。

**紐づくタスクが無い状態で PR が open していれば、Stop hook が自動起票する**（タイトルは PR のタイトル、列は draft なら `working` / ready なら `review`（無ければ常設とレビュー依頼を除く最初の進行中の列）、PR URL をリンク、セッションを紐づけ）。同じ URL のタスクが既にあれば起票せずそれに紐づける。

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
- 列を省くと `todo`、無ければ常設とレビュー依頼を除く最初の進行中の列に入る（`Board.defaultColumn`）
- 起票するとこのセッションが紐づく（`link_session: false` で結ばない）

## 文書を見せる・聞く・レビューしてもらう

ユーザーが後から見返す判断文書（計画書・設計提案・調査結果）はタスクに載せ、アプリの受信箱から読ませる。どの tool もブロックしない。

- **`doc_publish`** で載せる（`path` か `content` + `name`）。同じ `name` への再 publish は新しいリビジョンになり、前の版のコメントは残る。比較軸が 3 つ以上・状態遷移・段階の順序を示す文書は HTML にする（外部の画像・CSS・script は読み込まれないので、全部インラインで書く）
- **`ask_user`** で選択肢を出して聞く。背景・判断材料・trade-off は `context`（markdown）に書き、質問文に詰め込まない。既存の文書に付けるなら `name` にその文書名を渡す。質問は全問に答えるまで送れないので、問いは本当に要るものだけにする
- **`review_request`** で、載せた文書のレビューを頼む（`note` に何を見てほしいか 1 行）
- **回答とレビューは Stop hook がこのセッションに注入する**（ターンを終えると hook が最大 1 時間待ち、届いたら起こす）。聞いたら答えを前提にした作業は止め、答えに依存しない作業だけ進めてターンを終える。返事を待つために tool を繰り返し呼ばない
- 届いたレビューのコメントは 1 件ずつ対応し、**`comment_reply`**（`comment_id` は届いた本文の `commentId`）で何をしたかを返す。直したら `resolve: true`。文書を直したら同じ `name` で `doc_publish` し直す
- Stop hook が無い環境（`claude -p`・herdr の外）では、**`feedback_list`** で届いた分を取る。各項目は 1 回しか返らない

## 別のセッションへ送る・起こす

`session_list` で pane と状態を見て、`session_prompt` で文字を送る。委譲先への指示と、止まっている自分の委譲先への返答に使う。**動いている人のセッション（`working`）と、自分が起こしたのでないセッションには送らない。**

委譲先を新しく起こすときは `session_start`（`task_id` 省略で自分のタスク、`cwd` 省略で自分の cwd、`worktree_branch` で worktree を切る）。エージェントは `kind`（`claude` / `codex`）、Claude Code のモデルと effort は `model`（`opus` / `fable` / `sonnet`）と `effort`（`low` / `medium` / `high` / `xhigh` / `max`）で選び、省略すると `opus` / `medium`。前の版の `preset` も受けるが、`model`・`effort` を渡すとそちらが優先する。daemon が tab と agent を作って起動プロンプト（省略時は列の既定）を送り、そのタスクに結ぶ。進み具合は `session_list` に出る。herdr の `agent start` を自分で叩くより、紐づけと起動プロンプトが揃うこちらを使う。

## Gotchas

- **`work_update` で `wait` にするときは `blocker_kind` か `blocker_text` が必須**（無いとエラー）
- **`task_id` の解決は pane か Claude Code のセッション ID 経由**。どちらも無い所（Codex、CI）では毎回 `task_id` を渡す
- **`/clear` の後の会話は、MCP に `/clear` の前の会話の ID が残る**（MCP の process が起動し直されない）。`/clear` の後に `link_session` で別のタスクへ結ぶと前の会話を結ぶので、`/exit` して `claude --continue` で開き直してから結ぶ
- **タスク番号は削除しても再利用されない。** 一度得た番号は安定した handle として使える
- **同じ文書に未回答の質問は 1 束だけ。** 新しい `questions` を付けて publish すると前の未回答の束は取り下げられる（同じ内容なら作り直さない）
- **文書を消すと、その文書の質問とコメントも消える**
- **daemon が止まっていると tool はエラーを返す。** その旨を伝え、`launchctl kickstart -k gui/$UID/uk.whatn.taskboardd` を案内する（自分では実行しない）

## 既存設定との関係

- **pane・tab・agent そのものの操作**: /herdr（本スキルは taskboard の tool だけを扱う）
- **作業ログ・調査記録**: @context/memory-file-formats.md（note・作業項目と使い分ける）
