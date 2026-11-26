---
name: taskboard
description: taskboard の MCP tool でタスク・作業項目・文書と、案件・定期起動・セッション・受信箱を扱う。依頼を受けて作業に入る時（紐づくタスクが無ければ起票する）、状況を聞かれた時、自分のセッションに紐づくタスクの列を進める・起票する時、計画の承認後に作業項目を登録し着手・完了・待ちを更新する時、計画書・設計提案を人に読ませて採否やレビューを求める時、ボードの一覧・状態を確認する時、オーケストレーターとして全体の health を見回る時、案件・定期起動・セッションを作る・変える・止める・削除する時、依頼に taskboard・タスクボード・kanban・作業項目の語がある時に使用。境界: taskboard の外で始まったセッションをタスクに移すのは taskboard-adopt、複数のタスクの会話を lead として束ねて回すのは lead、pane・tab・agent の操作は herdr、作業ログ・調査記録はメモリディレクトリ、ボードの画面操作はユーザーの領域、新しい定期起動の中身（仕組みの選択・手順書・プロンプト・状態ファイル）の設計は scheduling-jobs。
---

# Taskboard

タスク 1 件に、エージェントセッション・PR・Issue・チケット・作業項目を束ねるボード。状態は各 Mac の daemon が持ち、セッションは MCP tool（server 名 `taskboard`）で読み書きする。アプリ（Mac / iPad / iPhone）は同じ daemon を見る。

## 前提

ツール一覧に `mcp__taskboard__*` があること。無ければ「taskboard の MCP が繋がっていない（`claude mcp list` で確認）」と伝えて止まる。CLI や API を推測して直接呼び出さない。

`task_id` を省くと、このセッションに紐づくタスクを使う。セッションは、taskboard の会話なら会話の id（`TASKBOARD_CONVERSATION_ID`）で、普段使いの端末の Claude Code なら MCP に渡るセッション ID（`CLAUDE_CODE_SESSION_ID`）で見分ける。taskboard が起動したセッションは SessionStart hook が結ぶ。`work_list` が「紐づくタスクが無い」と返したら `board_overview` で候補を見て、`task_update` の `link_session: true` で結ぶか、`task_create` で起票する。taskboard の外で始まった作業をまとめて移すときは /taskboard-adopt スキルを実行する。

結んだ後の案内（タスク・今の列・案件の列の説明）は `session_guide` で読める。SessionStart の案内が無いセッションで結んだとき、圧縮で案内が消えたと感じたときに読む。

## 列

**列は案件の列の説明に従って選ぶ。** 列の id・名前・説明は案件ごとに違い、人が修正できる（既定の列を削除した案件、列を追加した案件もある）。説明は SessionStart の案内・`session_guide`・`task_get`（今の列）・`task_update`（移した先）・`board_overview` に出る。id をハードコードしない。

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

- **依頼を受けて作業に入るとき、紐づくタスクが無ければ、着手の前に起票して作業中の列に置く**（PR を待たない。下の Stop hook の自動起票は PR がある場合だけで、それまでの作業がボードに出ないため）。起票の手順は「起票する」。**受付の会話は、紐づくタスクがあっても、返答だけで済む質問以外の依頼ごとに起票して会話を起こす**（下の「受付の会話の依頼を切り出す」。規則は `context/tool-claude-code.md`「受付の会話」）
- **状況を聞かれたら**（いまどうなっているか・何待ちか・残り）、`task_get` と `work_list` を開き、その結果を一次情報として答える。メモリの記録や会話の記憶は書いた時点の状態なので、そこから答えない

**PR の状態に対応する列の前進は daemon が自動で行う**（PR が ready なら `review`、merge されれば案件の「マージしたら」の列（既定は `deploying`。その列を削除した案件では `done`）。前進方向のみで、終端列・常設・追加した列は触らず、進める先の列が案件に無ければ動かさない。Stop hook でも同じ判定が走る）。この前進を手で `task_update` しに行かない。手で動かすのは daemon が判断しない列（`planning` / `working` / `wontfix` 等）と、ユーザーから指示された移動だけ。

**`review_req` に入ったタスクは `review_req` と終端列しか取らない。** 紐づいているのは他人の PR なので、自分が approve しても作業段階は進まない。レビューを投稿しても `review_req` に留める（「レビュー済み」は daemon が PR の状態から出すので、タイトルに印を付けない）。紐づく PR が全部マージかクローズになると daemon が `done` へ進めるので、手で `done` へ移さない。

**紐づくタスクが無い状態で PR が open していれば、Stop hook が自動起票する**（タイトルは PR のタイトル、列は draft なら `working` / ready なら `review`（無ければ常設とレビュー依頼を除く最初の進行中の列）、PR URL をリンク、セッションを紐づけ）。同じ URL のタスクが既にあれば起票せずそれに紐づける。

列を動かすのは**確認できた事実に対応する遷移だけ**。自分が実行した操作（PR を出した・merge した）と `task_get` の内容が根拠になる。根拠なく先の列へ進めない。判断がつかないときは動かさず、ユーザーに聞く。

## 作業項目

タスクの中の計画を daemon に持たせ、ボードのカード・タスク画面・iPhone に「今どこまで進んで、何を待っているか」を出す。

- **計画が承認されたら、全項目を `work_add` で登録する**（Phase 2 の計画書の作業項目と 1 対 1。1 項目 = PR 1 本か、PR 内の 1 段階）。順序は計画順。前の項目が終わらないと始められないものは `depends_on`
- **着手で `state: doing`、終わったら `state: done`** と成果物（`deliverable_kind` / `deliverable_ref`: PR の URL、コミットの SHA、ファイルのパス、文書の id）
- **待ちに入ったら `state: wait` と `blocker_kind`**（`approval` 自分の承認か回答 / `review` 他者のレビュー / `ci` / `deploy` / `item` 別の項目 / `external`）と `blocker_text` 1 行。待ちが解けて作業に戻るときに `doing` へ動かすと blocker は消える
- **利用者に手作業（実機での確認・ケーブルの接続・ログイン）を頼むときは、その項目を `state: wait`・`blocker_kind: manual` にし、`blocker_text` に頼む作業を 1 文で書く**。受信箱に手作業の依頼として出て、利用者が［対応済みにする］を押すと項目は作業中に戻り、「taskboard で手作業を済ませました」が質問の回答と同じ経路で届く。応答の文だけで頼んだことは受信箱に出ない。判断は manual でなく `ask_user` か AskUserQuestion で聞く
- **委譲した項目は `owner`** に委譲先の名前（会話の題か id の先頭 8 字）。自分なら省く
- やらないと決めた項目は `state: drop`（母数から外れる）
- `work_list` は計画順に状態・待ち理由・成果物・依存を返す。再開・compaction 復帰の後は、メモリの記録より先にこれを読んで今の状態を取る

## 起票する

**起票の前に、紐づける URL で既存タスクを検索する**（`board_overview` に PR の短縮名が出る。同一性は URL で判断し、タイトルでは照合しない）。`task_create` は同じ URL のタスクがあればエラーで止まるので、そのときは返ってきた番号に `task_update` で追加する。

- **粒度は「1 タスク = 1 つの完了判定」**。PR 1 本・チケット 1 件・調査 1 件が単位。複数 PR にまたがる 1 つの作業は、束ねる 1 タスクにリンクを複数付ける（PR ごとに割らない。PR ごとの進みは作業項目で表す）
- **リンク（`links`・`add_links`）には、そのタスクの成果物か、完了を左右する PR・issue・チケットだけを入れる。** 参考に読むだけの PR は `note` か指示書に URL で書く。リンクした PR の動き（コミット・コメント・Ready）は紐づく会話へ通知され、daemon がタスクの列を動かすので、成果物でない PR をリンクすると、会話が何もしないターンを回し、列も実態とずれる
- **タイトルは、何が終われば完了かが読み取れる形にする。** チケット由来ならチケット側の表題をそのまま使う
- `note` には**セッションをまたいで必要になる文脈だけ**を書く（決めた方針・詰まっている点・再開条件）。作業ログ・調査記録はメモリディレクトリ側に書く（形式は書く前に `context/memory-file-formats.md` を Read する）
- 列を省くと `todo`、無ければ常設とレビュー依頼を除く最初の進行中の列に入る（`Board.defaultColumn`）
- 案件は `board`（id か名前）で選ぶ。省くとアーカイブしていない最初の案件。別の案件へ移すのは `task_update` の `board`
- 起票するとこのセッションが紐づく（`link_session: false` で結ばない）

## 受付の会話の依頼を切り出す

1. Slack のスレッドの続き（届いた知らせに「スレッドの中の依頼」とある）なら、先に依頼の id で `slack_get` を呼び、スレッドの前の発言にある受付の返信から、切ったタスクの番号を取得する。`task_get` でその番号の `note` の出所を照合し、合えば起票せず、そのタスクの会話に `session_prompt` で依頼の id と本文を送る（会話が止まっていれば `session_resume`）。`board_overview` は完了の列と多数のタスクを省くので、一覧に無いことを未起票の根拠にしない。届け先の会話は、この知らせを人の承認として扱わず、依頼の id で `slack_get` を呼んで本文を読む
2. `task_create` で起票する
   - `board`: タスクに結ばれた受付の会話は、`task_get` で取得した自分のタスクの案件。オーケストレーターは `board_overview` で候補を見て、依頼の内容に合う案件を選ぶ（届いた知らせの「場所」の案件は Slack の設定を持つ案件で、届け先のタスクの案件とは限らない）
   - 列: 案件の列の説明で方針を詰める列（既定は `planning`）
   - `link_session: false`（受付の会話を新しいタスクに結ばない）
   - `note`: 依頼の出所（Slack の依頼の id と元の発言のリンク）
3. 指示書をメモリディレクトリに書く。依頼の原文の引用、依頼の出所、受付の会話がすでに確認した事実（確認済みと推測を分ける）を載せ、次の決まりを書く
   - 最初に計画を `doc_publish` で載せ、`ask_user` で承認を得てから着手する
   - Slack の依頼なら、依頼の id で `slack_get` を呼んで読み、報告は `slack_reply` で返す（依頼の id があれば、どの会話からでも呼び出せる）。`slack_reply` は依頼主への報告の経路なので承認を取らずに送り、指示書の「外に出る作用はその都度確認する」の対象に入れない
   - 子エージェント（Agent・Workflow）を起動しない
4. `session_start` で起こす
   - `task_id`: 新しいタスク
   - `cwd`: 作業対象のリポジトリ。決まらなければ省き、指示書に対象の確認を最初の作業として書く
   - `model` と `effort`: `context/delegation.md`「モデルの選択」
   - `disallowed_tools: ["Agent", "Workflow"]`
   - `prompt`: 指示書の絶対パスを読む指示
   - `notify` は渡さない（別のタスクの会話は既定で知らせが切れている。起こした会話はユーザーに直接聞くので、受付の会話に作業の報告を積まない）
5. 依頼元に、切ったタスクの番号と題を返す。Slack の依頼なら `slack_reply` の `status: "working"` で返す（既定の `done` は Slack の作業中の表示を解除する）。完了の返信は、起こした会話が `done` で返す

起こした会話は、そのタスクの担当として計画から完了までを自分で進める。lead の委譲先ではないので、`context/delegation.md`「`~/.claude` の追跡ファイルを委譲先に直接書かせない」は当てはまらず、`~/.claude` を変えるタスクなら自分のターンで commit・push まで行う。受付の会話がその後に行うのは、上の1のスレッドの続きの取り次ぎだけにする。

## 文書を見せる・聞く・レビューしてもらう

ユーザーが後から見返す判断文書（計画書・設計提案）はタスクに載せ、アプリの受信箱から読ませる。どの tool もブロックしない。この節が、文書をどこに出すかの真実源。

- **タスクに載せるもの**: 計画書・設計提案など、ユーザーが後から見返して採否を決める文書。採否は `ask_user` か `review_request` で問う
- **セッション内で示すもの**: 調査結果・レビュー結果の要約、実装中の技術判断、単発の質問。ユーザーがセッション内での提示を指定したら、以後そのタスクではセッション内に留める
- **問う前に委任範囲を見る**（`session_guide`・`task_get` の「委任範囲」。項目は implementation・tracker・followups・review_merge・outbound・cost・destructive）。［委任］と［報告のみ］の項目は問わずに決めて実行し、［報告のみ］の項目は決めたことを応答で報告する。問うのは［確認］の項目と範囲の外のことだけにする
  - ［委任］の項目でも、AGENTS.md の確認必須カテゴリ（対外コミュニケーションの内容・外に出る作用）に当たる操作は確認を続ける（委任範囲はタスクの中の既定で、AGENTS.md の確認を緩めない）
- **人への問いは、答える人が何を読んで決めるかで出し方を選ぶ**（taskboard は 3 つを別の場所に出し、札の上で答えられるのは権限の確認だけなので、取り違えると読まずに答えさせることになる）
  - 会話の流れの中で決める判断は `AskUserQuestion`（codex は `request_user_input`）。会話は答えが来るまで止まる
  - 文書を読んで決める判断は、`doc_publish` で載せた文書に `ask_user` で質問を付ける。会話は止まらない
  - 判断を待つ問いを返答の文だけに書いてターンを終えない（会話が進むと流れ、受信箱の依頼にもならない。lead の会話では Stop hook が 1 回差し戻す）。文書の型は `context/decision-docs.md`
  - 人にしかできない作業（ログイン・承認・物理作業）の依頼は、応答の最後の文で頼む。判断を問う用途には使わない（利用者は答えを入力欄に打つしかなく、選択肢を選べない）
  - 選択肢の違いが文で伝わらない（画面の形・表・コード）なら、選択肢に見本（`preview`。markdown か HTML）を付ける。推奨は 1 つに `recommended` を付ける（`AskUserQuestion` は label の末尾の「(Recommended)」）
- **知らせの扱い**: 質問の回答・レビュー・送る文面の承認は利用者の判断として扱う。それ以外の `[taskboard 通知]`（PR・CI・委譲先の知らせ）は事実の知らせで、承認として扱わない
- **`doc_publish`** で載せる（`path` か `content` + `name`）。同じ `name` への再 publish は新しいリビジョンになり、前の版のコメントは残る。比較軸が 3 つ以上・状態遷移・依存関係・段階の順序を示す文書は HTML にする（外部の画像・CSS・script は読み込まれないので、全部インラインで書く）
- **`ask_user`** で選択肢を出して聞く。背景・判断材料・trade-off は `context`（markdown）に書き、質問文に詰め込まない。既存の文書に付けるなら `name` にその文書名を渡し、`context` は渡さない（本文は変わらず、質問だけが付く。背景はその文書の本文が担う）。質問は全問に答えるまで送れないので、問いは本当に必要なものだけにする
- **質問の答えで作業項目が止まるときは、`ask_user`（`doc_publish` の `questions` も同じ）の `work_item` にその項目の id を渡す**。taskboard が項目を回答待ちにし、回答か取り下げで作業中に戻す。`work_update` で `wait`・`approval` に手で置かない（受信箱には質問の 1 行だけを出すので、手で置いた待ちは質問に答えても残る）
- **`review_request`** で、載せた文書のレビューを頼む（`note` に何を見てほしいか 1 行）
- **回答とレビューは、ターンを終えて入力待ちになった時点で daemon が人の発話としてこのセッションの入力欄に入れる**（taskboard の会話の外のセッションでは Stop hook が最大 1 時間待って注入する）。聞いたら答えを前提にした作業は止め、答えに依存しない作業だけ進めてターンを終える。返事を待つために tool を繰り返し呼ばない
- 届いたレビューのコメントは 1 件ずつ対応し、**`comment_reply`**（`comment_id` は届いた本文の `commentId`）で何をしたかを返す。修正したら `resolve: true`。文書を修正したら同じ `name` で `doc_publish` し直す
- Stop hook が無い環境（`claude -p`、hook を入れていない Mac）では、**`feedback_list`** で届いた分を取る。各項目は 1 回しか返らない

## 別のセッションへ送る・起こす

`session_list` で会話と状態を見て、`session_prompt` で文字を送る。委譲先への指示と、止まっている自分の委譲先への返答に使う。**動いている人のセッション（`working`）と、自分が起こしたのでないセッションには送らない。**

送れるのは会話（daemon が stream-json で動かす Claude Code・codex。端末を持たない）だけ。tool には `conversation_id`（先頭 8 字以上）を渡す（`session_prompt`・`session_stop`・`session_resume`・`session_history`・`session_rename`）。普段使いの端末の Claude Code は hook でタスクに結ばれるが、`session_list` には出ず、送れない。

- 会話の tool: `session_answer`（会話が待っている問い（AskUserQuestion・権限の確認・計画の承認）に答える。答えを省くと何を聞かれているかを返す）、`session_control`（model・effort・権限のモード・起こした側への通知（`notify`）を替える、今の生成を止める）、`session_fork`（途中の発言から分ける）
- 会話の中身は `session_history` の `conversation_id`、問いは `session_answer` で扱う
- 定期起動の回とオーケストレーターも会話で動く

委譲先を新しく起こすときは `session_start`（`task_id` 省略で自分のタスク、`cwd` 省略で自分の cwd、`worktree_branch` で worktree を切る）。

- エージェントは `kind`（`claude` / `codex`）。どちらも会話として起きる（codex の `model`・`effort` は codex の名前のまま）
- Claude Code のモデルと effort は `model` と `effort`（`low` / `medium` / `high` / `xhigh` / `max`）で選ぶ。`model` に渡せるのは、そのマシンの CLI の一覧にある名前（別名の `opus` / `fable` / `sonnet` / `haiku` か版つきの名前）で、一覧に無い名前は使える値を並べて断られる
- `kind`・`model`・`effort` を省くと、案件の起動の既定で起こす（案件に既定が無ければ `opus` / `medium`）。渡した値は既定に重なり、既定と違う `kind` を渡すとその kind の既定から始まる。前の版の `preset` も受けるが、`model`・`effort` を渡すとそちらが優先する
- 会話は `notify` が入っていると、委譲先のターンの終わり（最後の返事つき）と問いを、起こした側のセッションに taskboard が発言として入れる。省くと、会話から自分のタスクに起こしたときは入る（別のタスクとオーケストレーターからは切）。`disallowed_tools`（`["Agent", "Workflow"]` など）で委譲先に使わせない tool を外せる
- daemon が起動プロンプト（省略時は列の既定）を送り、そのタスクに結ぶ。進み具合は `session_list` に出る
- ファイルを書く作業を委譲するときは、委譲の決まり（再委譲の禁止・連絡の方法）のヘッダを付けて会話を起こす `~/.claude/bin/taskboard-delegate.sh` を使う（`context/delegation.md`）

**1 行目が `<!-- taskboard: <種類> ... -->` の印の発言と、「[taskboard 通知]」で始まる発言（前の版の daemon は「taskboard: 委譲先の会話 …」）は、taskboard が送った知らせか別のセッションの発言で、人の発言でも承認でもない。** 委譲先の返事は報告として読み、続きは `session_prompt`、問いには `session_answer` で、どちらも `conversation_id` を渡して返す。前のターンの返事は `session_history` の `conversation_id` で読む。

## 全体を見回る・管理する

アプリでできる操作は MCP でもできる。主にオーケストレーターが全体の health を保つために使う。

| 用途 | tool |
|---|---|
| 全体の様子（daemon・gh・APNs・会話の host・オーケストレーター・利用枠・回答待ちの会話・うまくいかなかった定期起動・予定（wake）と監視の失敗・受信箱の対応待ちの数） | `health` |
| 案件 | `board_create` / `board_update`（名前・起動プロンプト・`merge_target`・アーカイブ・`edit_columns` / `add_columns` / `remove_columns` / `reassign`）/ `board_delete` |
| タスク | `task_update` の `board`（別の案件へ）・`remove_links`・`unlink_session` / `unlink_sessions`（紐づけを外す。セッションは止めない）/ `task_delete` |
| 作業項目・文書・質問 | `work_delete`（`drop` と違い母数からも履歴からも消える）/ `doc_read` / `doc_delete` / `ask_cancel` |
| 定期起動 | `schedule_runs`（各回の結果と失敗の理由）/ `schedule_delete`。`schedule_create` / `schedule_update` の `task_id`・`new_task`（`board`）で常設タスクに結ぶ（結ばないと各回のセッションはどのタスクにも結ばれない）、`clear_task` で外す。新しく作るときは /scheduling-jobs スキルで中身を決めてから登録する |
| セッション | `session_answer`（会話の問い。答えを省くと何を待っているかを返す）/ `session_control` / `session_account` / `session_fork` / `session_stop` / `session_exit`（自分の会話をこのターンの後に終了する）/ `session_resume` / `session_history` / `session_rename` |
| マシン | `orchestrator_status` / `orchestrator_start` / `orchestrator_prompt` / `orchestrator_restart` / `settings_get` / `settings_update` / `inbox_list` / `inbox_dismiss` / `inbox_restore` / `prs_list` / `prs_refresh` / `usage_get` |

- **見回りの順**: `health` → 回答待ちの会話は `session_answer`（答えを省く）で何を待っているかを読む → 失敗・スキップした定期起動は `schedule_runs` で理由を見る → 戻すなら `session_stop`・`session_resume`・`schedule_run`
- **削除する tool（`task_delete`・`board_delete`・`work_delete`・`doc_delete`・`schedule_delete`）と `session_stop` の `force` は、1 回目は何が消える（止まる）かを返すだけで実行しない。** 中身を読んで、削除してよいと確認してから同じ引数に `confirm: true` を付けて呼び直す。削除するのも PR の操作も、人の指示があるときだけ
- 自分のセッションに紐づくタスク以外の列・作業項目は、health のために動かすときだけ触り、理由をそのタスクの `note` に 1 行追加する（`note` は丸ごと置き換わるので、`task_get` で今の備考を読んでから追記する）
- `orchestrator_restart` はオーケストレーターを止め、今の会話を破棄して新しく起こす（引数なし。常駐を切っていても起こす。設定の引数と起動プロンプトで、`--resume` なし）。会話が長くなった・様子がおかしいときに使う。元に戻せないので、人に確認してから呼ぶ。オーケストレーター自身から呼ぶと、自分の会話が止まって応答は届かない
- `session_stop`・`session_prompt`・`session_answer` は自分の会話には使えない。用済みになった自分の会話は `session_exit` で、報告を書いてターンを終えた後に終了する
- 利用枠の上限で止まった会話には、taskboard が戻った時刻に「利用枠が戻ったので、止まったところから続けてください。」を送る（`session_list` に予定の時刻が出る）。送らせないときは `session_stop`（止まっている会話でも予定を削除する）

## Gotchas

- **`work_update` で `wait` にするときは `blocker_kind` か `blocker_text` が必須**（無いとエラー）
- **`task_delete` は `task_id` を省けない**（このセッションのタスクを暗に削除しない）
- **案件を削除できるのはタスクが 0 件のときだけ。** 残っていれば `task_update` の `board` でほかの案件へ移すか `task_delete` で削除してから
- **`task_id` の解決は会話の id か Claude Code のセッション ID 経由**。どちらも無い所（Codex、CI）では毎回 `task_id` を渡す
- **`/clear` の後の会話は、MCP に `/clear` の前の会話の ID が残る**（MCP の process が起動し直されない）。`/clear` の後に `link_session` で別のタスクへ結ぶと前の会話を結ぶので、`/exit` して `claude --continue` で開き直してから結ぶ
- **タスク番号は削除しても再利用されない。** 一度得た番号は安定した handle として使える
- **同じ文書に未回答の質問は 1 束だけ。** 新しい `questions` を付けて publish すると前の未回答の束は取り下げられる（同じ内容なら再作成しない）
- **文書を削除すると、その文書の質問とコメントも消える**
- **daemon が止まっていると tool はエラーを返す。** その旨を伝え、`launchctl kickstart -k gui/$UID/uk.whatn.taskboardd` を案内する（自分では実行しない）
