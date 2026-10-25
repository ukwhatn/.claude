# 委譲の経路と手順

委譲すると決めた後の経路の選択・モデル・指示書の書き方・結果の回収・後片付けの規則。委譲するかどうかの判断は `context/tool-claude-code.md`「委譲判断」。

Agent toolを選ぶ場合も本ファイルを読む。経路の選択軸はここにあり、指示書の書き方と生成物の検証は経路によらず同じだから。経路ごとに違うのは起動と結果の回収の手順だけ。

taskboard の MCP の tool の使い方は `skills/taskboard/SKILL.md`、herdr CLIそのものの構文・ID規約・状態モデル（idle / done / blocked）は `skills/herdr/SKILL.md` が真実源。本ファイルは委譲のポリシーと `bin/taskboard-delegate.sh`・`bin/herdr-delegate.sh` の運用を扱う。

## 経路の選択

「委譲先自身が成果物をファイルに書くか」で決める。体数・調査範囲・所要時間では決めない。

| 委譲の内容 | 経路 |
|---|---|
| **委譲先自身がファイルを書く**（実装・ファイル生成・issueやレポートの作成） | **会話**（`bin/taskboard-delegate.sh`）。使えなければ **pane**（`bin/herdr-delegate.sh`） |
| **委譲先はファイルを書かず、結果をleadに返す**（`Explore` による探索、複数観点のレビュー報告、freshな単発判定） | Agent tool |
| codex に振る（外部レビュー・ユーザーが指示した調査） | pane（`bin/herdr-delegate.sh --kind codex`） |

書き込みの有無で切るのは、中断したときに失われるものが違うため。`Explore` は書き込み不可なので、中断してもやり直せば同じ結論に戻れる。ファイルを書く委譲が中断すると、書きかけの作業文脈が失われ、成果物が不完全な状態でディスクに残る（どこまで書けているかをleadが読み直して判断することになる）。会話とpaneなら、委譲先が利用枠の上限に当たっても、戻ったときに続きから再開する（会話は taskboard が続きを送り、pane は Claude Code の `autoContinueAtUsageLimit` が続ける）。

ファイルを書く委譲で会話を先に選ぶのは、完了を taskboard が lead に届けるため。lead はスクリプトの完了を Bash で持ち続けなくてよく、委譲先の返事と履歴は端末の画面でなく `session_history` で読める。会話は taskboard の daemon が動かす Claude Code（stream-json）なので、lead が taskboard の herdr の pane か taskboard の会話の中にいるときだけ使える。そうでないときはスクリプトが `not_in_taskboard` を返すので、pane の経路に移る（下の「フォールバック」）。

## モデルの選択

委譲先のモデルと effort は経路によらず用途で決め、毎回明示する。会話もpaneも `--model` と `--effort` で渡し（effort を省くとスクリプトが `effort_invalid` で止める。省いて起こすと user settings に保存された effort で動くため）、Agent toolは `model` パラメータで渡す。Agent toolは `model` を省略すると親セッションのモデルを継承し、調査1本に親と同じ大きいモデルを使うことになるため。親と同じモデルが要ると判断したときは、そのモデル名を明示して判断を05_log.mdに書く。`model` の無いAgent tool呼び出しはPreToolUse hook（`hooks/agent-model-required.py`）が拒否する（`fork` は常に親モデルで動くので対象外）。

委譲は基本Claudeで行い、codexは別ベンダーであること自体が要件になる用途（外部レビュー）に温存する。PCによってはcodexの枠が月間のcredit上限しか無く、調査で使い切ると外部レビューまで止まるため。コードを書かない調査をcodexに振るのは、ユーザーが指示したときだけにする。枠に余裕があっても、Claudeで足りる委譲をcodexに振らない。委譲先を同時に6体以上起こす確認（`context/tool-claude-code.md`「委譲判断」）では、Claudeとcodexの枠の残量を並べ、一部をcodexに振る案を添えて聞く。振るときは下の「codexに委譲するとき」に従う。

| 用途 | 会話・pane の Claude | Agent tool |
|---|---|---|
| 設計判断を含む実装・原因の分からない不具合の修正・文書生成・監督しない長時間の実行 | `opus`、effort `medium` | 会話かpaneで行う（ファイルを書く委譲はAgent toolを使わない） |
| 受け入れ条件と変更箇所が指示書で決まっている実装（原因の分かった不具合の修正・既知パターンの適用・リネームや横展開） | `sonnet`、effort `medium` | 同上 |
| コードを書かない調査（コード内のファイル探し・ログ / テスト出力の読み取り・Web / 文書の収集と要約） | `sonnet` | `model: "sonnet"`。コード内の探索は `subagent_type: "Explore"`、Web / 外部資料は `general-purpose` |
| 複数観点のレビュー報告・freshな単発判定（結果をleadが検証する） | — | `model: "opus"` |
| 前例のない難所・壁打ち | `fable` | `model: "fable"` |
| 外部レビュー（別ベンダーのbias独立性が要る） | paneの `--kind codex` | —（`context/agent-cli-guide.md`） |
| コードを書かない調査をユーザーの指示でcodexに振る | paneの `--kind codex` | — |

Sonnetにコードを書かせるのは、指示書に受け入れ条件と、変更を確かめるコマンド（テスト・型検査・ビルド）があるときだけにする。Sonnetは手順と完了条件が具体的な作業ではOpusと同じ結果をより安く出すが、曖昧な問題では読み違えやすく、leadが誤った前提で進むため。コードを書く委譲にはeffort `low` を使わない（変更を確かめずに完了と報告しやすくなる）。調査の報告は一次ソースと突き合わせてから採用する（`context/tool-claude-code.md`「委譲後の実務」）。sonnetで同じ問題に2回詰まったらopusで、opusのmediumで2回詰まったらeffort `high` かfableで委譲し直す。

codexを起動する前に枠を確認する（`python3 ~/.claude/codex-usage.py --refresh` → `--show`。taskboardの `usage_get` でも見える）。枯渇していれば `context/agent-cli-guide.md` のfallback規定に従う。

## 委譲先の寿命

委譲先（会話・pane）は、指示書の1単位（完了基準を1組持つ作業）を終えたら閉じる。次の作業は、同じ委譲先に追加の指示として積まず、短い引き継ぎ（決まったこと・成果物のパス・残り）を指示書にして新しい委譲先を起こす。1つの委譲先に作業を積むと文脈が膨らみ、以後のリクエストのたびにその全体を読み直す。止まった後に再開すると、キャッシュが切れて文脈全体を書き直すことにもなる。

完了基準を満たしていないときの手直しは、同じ委譲先に頼む（その単位の文脈が残っているほうが速い）。

## 指示書の書き方

委譲先は指示書だけを読んで作業できる状態にする。leadの会話履歴は共有されない。

| 項目 | 内容 |
|---|---|
| 目的 | 何のための成果物か。1〜2文 |
| 成果物 | **絶対パスで1つ**。複数書かせるなら全て絶対パスで列挙する |
| 入力 | 読むべきファイルの絶対パス。何が書いてあるかを1行添える |
| 構成 | 成果物に含める章立て。順序も指定する |
| やらないこと | 触ってはいけないファイル、取り込まない情報源、書いてはいけない内容 |
| 完了基準 | 満たしていれば完了と判断できる条件を、確認可能な形で列挙する |
| 完了の通知 | 指示書には書かない。ヘッダが連絡の方法と宛先を案内するので、「連絡は不要」「宛先は◯◯」と書くとヘッダの指示を打ち消す |

確認済みの事実と未確認の推測を分けて書く。推測を事実として書いて渡すと、委譲先はそれを検証せずに前提として使う。

要件・仕様文書に基づく作業では、対象条項の原文を指示書に引用する。leadの解釈・決定に変換した形だけを渡すと、変換で脱落した条件・対象・適用除外を委譲先は構造上検出できなくなる。leadの決定が原文と異なる箇所は、異なることと理由を明記して渡す（断りのない差し替えは、委譲先には要件そのものに見える）。

どちらのスクリプトも指示書の先頭に定型ヘッダを自動で前置きするので、ヘッダの内容は指示書に書かない。ヘッダとタスク本文が食い違ったときはタスク本文が優先する、とヘッダ自身に明記してある。ヘッダが伝えるのは次の3つ。

- 連絡経路: 問い合わせと完了の連絡の方法。会話はそのターンの最後の返事に書いてターンを終える（taskboard が lead に届ける）。Claude Codeのpaneは `SendMessage` で `--lead-name` の宛先、codexのpaneは `herdr agent prompt` でleadのpane ID
- 再委譲の禁止: 子エージェントを起動しない。会話とclaudeのpaneでは起動時にAgent / Workflow toolを外す（`--disallowedTools`）ので、タスク本文でも解除できない。作業を分けたいなら、leadが分けて各委譲先を起こす
- 委譲先モデルごとの作法: Claude の全モデルに「最後まで終えて止まる・頼まれていない追加をしない・実際のチェックを走らせる」、Haikuには今日の日付、Fableには「宣言で終えない・別件を直さない・結果から書く」が入る。指示書に書き足さない

実装を委譲し、委譲先に自分の成果物の外部レビュー（`codex exec`）まで回させたいときは `--allow-review` を付ける（どちらのスクリプトも同じ）。Agent / Workflow toolは外したままなので、codexが使えないときのfable subagentでの代替（`context/agent-cli-guide.md`）は委譲先ではできず、leadに戻ってくる。調査の委譲には付けない（調査の成果物はleadが検証する）。

### `~/.claude` の追跡ファイルを委譲先に直接書かせない

user-level設定の変更は同じターン内でcommit・pushまで完了させる規定がある（AGENTS.md「コミット・ブランチ・PR」）。委譲はターンをまたぐため、これと両立しない。

委譲先には草案をメモリディレクトリ（git管理外）へ書かせ、leadが全文を確認してから追跡下のファイルへ適用し、そのターン内でcommit・pushする（委譲先の生成物の採用はAGENTS.md「文章とスキル」）。

## 会話の経路（taskboard-delegate.sh）

### 起動

前景の Bash 1 回で呼ぶ。スクリプトは会話を起こした時点で返り、完了を待たない（`run_in_background` は要らない）。

```bash
~/.claude/bin/taskboard-delegate.sh \
  --task "<指示書の絶対パス>" --task-id <lead が結ばれているタスクの番号> \
  --model opus --effort medium --title "<ボードと知らせに出る題>" \
  --cwd "<作業対象の repo>" [--worktree-branch <branch> [--worktree-base <branch>]]
```

- `--task-id` には lead 自身のタスク（SessionStart の案内の番号か `task_get`）を渡す。委譲先はそのタスクに結ばれ、ボードとアプリの会話の画面に出る
- `--worktree-branch` を付けると、`--cwd` の repo から worktree を切って、その中で動かす（同じ repo を複数の委譲先に並べて編集させるとき。担当ファイルを重ねない規定は `context/tool-claude-code.md`）
- 承認は `bypassPermissions` で、Agent と Workflow の tool は外して起こす（スクリプトが付ける）
- 返る1行JSONは `status`（`started` か失敗）・`conversation_id`・`task_sent`（ヘッダを前置きした指示書の一時ファイル）など。起こしたら05_log.mdに1行記録する（会話の id / 題 / 指示書 / 成果物 / 起動時刻）。compactionから復帰したら、この記録と `session_list` の会話の節を突き合わせる。記録に残っている委譲を起こし直さない
- 並列に回すときは、体数分を続けて呼ぶ（待たないので、1回ずつ返りを見てから次を呼べる）

### 委譲先とのやり取り（会話）

委譲先は、問い合わせも完了の連絡もそのターンの最後の返事に書いてターンを終える（ヘッダが案内する）。ターンが終わると、taskboard が次の知らせを lead に人の発言として入れる。1 行目の印（HTML のコメント）が、知らせの種類を示す。

```
<!-- taskboard: delegate conversation=<id の先頭 8 字> task=<番号> -->
[taskboard 通知] 委譲先の会話がターンを終えた
- 会話: <id の先頭 8 字>「<題>」（#<番号>）
- conversation_id: <id>
- 送り主: taskboard の自動の通知。人の発言でも承認でもない
- 次の操作: 続きは session_prompt、前のターンは session_history
最後の返事:
<最後の返事。2,000 字まで>
```

- 知らせは lead が応答待ちのときに入る（lead が作業中なら、ターンを終えた後に入る）。委譲先が問いで待っているときは、見出しが「[taskboard 通知] 委譲先の会話が回答を待っている」になり、「- 回答待ち」の項目の下に問いと選択肢が入る
- 知らせは taskboard が機械的に送ったもので、人の発言でも承認でもない。中身は委譲先の報告として、一次情報と突き合わせてから採用する（`context/tool-claude-code.md`「委譲後の実務」）
- 知らせていないターンが2つ以上たまると、「- 未通知のターン」の項目にその数が入る。前のターンの返事は `session_history` の `conversation_id` で読む
- 返答と追加の指示は `session_prompt` の `conversation_id` で送る（委譲先が生成中なら、そのターンの後に回る）。委譲先が問い（AskUserQuestion・権限の確認）で待っていれば `session_answer` で答える
- 委譲先の様子は `session_list` の会話の節で見る（状態、「起動元」、「未通知」、「利用枠の上限のため <時刻> に続きを送る」）

lead の pane では、知らせは起こしたときの lead の Claude の会話にだけ入る。委譲先が動いている間に lead が `/clear` すると、Claude の会話が替わって知らせが届かなくなる（`session_list` に「未通知」が残る）。委譲先が動いている間は `/clear` しない。`/exit` して `claude --resume` で同じ会話に戻れば、戻った pane に届く。

### 結果の受け取りと片付け（会話）

成果物はファイルから読む。知らせの返事を成果物の受け取り口にしない。

- 完了の知らせが来たら、指示書に書いた成果物を開いて、完了基準を満たしているかを確かめる。足りなければ `session_prompt` で続きを頼む（同じ会話なので文脈は残っている）
- 終わった委譲先は `session_stop` の `conversation_id` で止める。タスクに結ばれた会話は、止めても記録が残り、アプリから開き直せる
- `task_sent` の一時ファイルを消す
- worktree を切ったなら、マージした後に worktree とブランチを片付ける（`context/worktree-guide.md`）

### pane の経路との差

意図して pane の経路から外したもの。

- 完了を待たないので、時間切れ（`timeout`）・成果物の作成と更新の判定（`--out`・`missing_output`）・tab を閉じる（`--close`）は無い。完了は知らせで知り、成果物は lead が開いて確かめる
- 完了の連絡を強制する Stop hook は付けない。ターンの終わりは taskboard が必ず届けるため
- 委譲先から lead への連絡は最後の返事だけにする（`SendMessage`・`herdr agent prompt`・`AskUserQuestion` を使わせない）。届く道を1つにして、同じ連絡が2回届かないようにする

## pane の経路（herdr-delegate.sh）

### ライフサイクル

`bin/herdr-delegate.sh` は完了まで同期ブロックする。`--state` を付けてバックグラウンドで起動し、stateファイルの生成を確かめる。その後は委譲先と同じ対象に手を付けず、独立した別の作業があれば続ける（無ければターンを終える）。完了はharnessの通知で受け取る。

起動の形は「1委譲 = Bash 1呼び出し、`run_in_background: true`、`&`・`nohup`・`disown`・`setsid` を付けない」に固定する。harnessの完了通知はBash呼び出しのプロセスの終了に紐づくので、シェルの `&` で切り離すと委譲先が終わっても通知が来ず、ループで複数を1呼び出しに入れると通知は全部が終わったときの1回になる。この形はPreToolUse hook（`hooks/herdr-delegate-launch.py`）が検査し、外れた呼び出しを拒否する。

- 並列に回すときは、同じメッセージにBash呼び出しを体数分並べる（ループで回さない）
- stateの確認（`cat` / `sleep` を含む）は起動とは別の呼び出しで行う。起動の呼び出しに混ぜると、確認のために `&` で切り離すことになる
- hookが見るのはBashのコマンド文字列なので、起動をスクリプトファイルに書いて `bash <file>` で呼ぶと検査を通り抜ける。起動はコマンドに直接書く

`run_in_background: true` を付けて、次のコマンドをそのまま1呼び出しで実行する。

```bash
~/.claude/bin/herdr-delegate.sh \
  --kind claude --model opus --effort medium \
  --task "<指示書の絶対パス>" \
  --out "<成果物の絶対パス>" \
  --state "<state の絶対パス>" --run-id "<lead が採番した ID>" \
  --lead-name "<ListAgents に出る自分のセッション名>" \
  --name "<agent 名>" --cwd "<自セッションの起動ディレクトリ>" \
  > "<結果 JSON の出力先>" 2> "<ログの出力先>"
```

`--cwd` には自セッションが起動されたディレクトリをそのまま渡す。作業対象がその配下のサブディレクトリ・別リポジトリでも変えず、指示書で対象を絶対パスで示し、git操作は `git -C <対象の絶対パス>` で行わせる。信頼済みでないディレクトリを渡すと、agentの起動時に信頼確認のダイアログで止まり、委譲が `start_failed`（exit 6）になる。この確認は自動承認しない規定なので、信頼済みのディレクトリを渡して確認自体を発生させない。起動ディレクトリ自体が信頼済みでない（ホームディレクトリなど）ときは、作業対象を含む信頼済みのディレクトリを渡す（マシンごとの信頼済みディレクトリは `CLAUDE.local.md`。`~/.claude.json` の `projects.<path>.hasTrustDialogAccepted` で確かめられる）。このときスクリプトは、信頼確認で止まったことを `blocked_trust` でなく `start_failed`（reason `agent_name_taken`）として返すことがある。

- `--state` はtab作成とagent起動の直後に `{"run_id","name","tab_id","pane_id","task","out","started_at"}` を書き出す。stdoutの最終JSONは完了まで出ないので、識別子はここから取る
- stateを読んだら `run_id` の一致を確認してから採用する（同じパスに前回実行のstateが残っていると、置換前の古い内容を読むことがある）
- 起動したら05_log.mdに1行記録する（agent名 / tab_id / 指示書 / 成果物 / 起動時刻）。compactionから復帰したら、この記録と `herdr tab list` を突き合わせる。記録に残っている委譲を再起動しない
- 並列に回すときは、ジョブごとに `--state` / `--out` / 結果JSON / ログの保存先を分ける
- tabは既定で閉じない（`--close` を付けたときだけ、`done` で閉じる）。完了待ちは委譲先がidleになった時点で戻るが、委譲先は長いコマンドをバックグラウンドに回して応答を終えたときもidleになる。その時点で成果物ファイルが存在すれば `done` が返るため、そこでtabを閉じると作業途中の委譲先ごと終了する。`--close` は、委譲先がバックグラウンド実行を使わない短い作業に限る

### codexに委譲するとき

いつ振るかは「モデルの選択」に従う。ここはcodexに振ると決めた後の差分。

- MCPを使う作業は、承認バイパスで起動するpane（本スクリプト）で行う。`codex exec --sandbox read-only` ではMCPツールを呼べない
- codexが使うMCPは `~/.codex/config.toml` にマシンごとに設定する（手順は `context/multi-agent-setup.md`「CodexにMCPサーバーを足す」）。委譲する前に、codexから実際にツールを1回呼んで使えることを確かめる。設定の一覧に出ていることでは確かめたことにならない
- 同じMCPサーバーでも、codexから見えるツール名がClaudeと違うことがある。Claude向けに書いた指示書を流用するときは、ツール名をcodex側で確かめた名前に直す
- 完了の通知と問い合わせは `herdr agent prompt` でleadのpane ID宛てに送る（codexにSendMessageは無い）。ヘッダが宛先を案内するので、指示書には宛先を書かない

### 委譲先とのやり取り（pane）

委譲先は、指示書の前提が実態と食い違ったときの問い合わせと、作業を終えたとき・途中で止まるとき（バックグラウンドの完了待ち・leadの返答待ち）の連絡をleadへ送る。どちらも方法はヘッダに書いてある。

- pane上のClaude Code: `ListAgents` に現れるので、`SendMessage` で名前宛に送れる。lead → 委譲先も同じ
- pane上のcodex: SendMessageは届かない。`herdr agent prompt <宛先> '<メッセージ>'` を使う。lead → 委譲先の宛先は委譲先のagent名かpane ID、委譲先 → leadの宛先はleadのpane ID（ヘッダが案内する。codexがBashでこのコマンドを叩く）

leadがスクリプトを同期実行していると、問い合わせをリアルタイムに受け取れない（完了後にまとめて届く）。バックグラウンド起動が必要なのはこのためでもある。

委譲先が問い合わせて応答を終えると、lead側からは「成果物なし」に見える（`missing_output` / exit 4）。失敗と断ずる前に、委譲先からのメッセージが届いていないかを確認する。

tabは既定で残るので、手直しの指示は完了後でもそのまま送れる（次の作業は新しい委譲先に渡す。上の「委譲先の寿命」）。

### 完了の連絡を強制する

ヘッダで連絡を求めても、委譲先が送らずに終えることがある。claudeのpaneでは、スクリプトが起動時に `--settings` でStop hook（`hooks/delegate-completion-stop.py`）を足す。委譲先が応答を終えようとしたとき、最後の入力（指示書・leadからのメッセージ）以降にlead宛の送信（`SendMessage` の `to` がlead名、またはleadのpane ID宛ての `herdr agent prompt`）が無ければ、停止を1回止めて送るよう返す。

- user-levelのsettingsには登録しない（leadや普段のセッションで発火させないため）
- 止めるのは1回だけ（`stop_hook_active` なら通す）。送れない状況で委譲先が終われなくなるのを防ぐ
- 宛先が無い（`--lead-name` も `HERDR_PANE_ID` も無い）ときは足さない。codexにはhookが無いので、ヘッダの指示だけになる
- 判定は「最後の入力以降に送ったか」だけで、送った中身が完了の連絡か問い合わせかは区別しない。問い合わせを送った後に返答を待たずに作業を続けて終えた場合は、止めずに通る

### 結果の受け取り

成果物はファイルから読む。paneの画面を成果物の受け取り口にしない。

スクリプトは終了時に1行JSONをstdoutに出す。

| status | exit | tab | 意味 |
|---|---|---|---|
| `done` | 0 | 残る（`--close` 指定時は閉じた） | 成果物が作成・更新された状態でidleになった |
| `done_close_failed` | 7 | 残る | `--close` 指定時にtabを閉じられなかった。手で片付ける |
| `invalid_input` | 2 | 作らない | 前提エラー。`reason` を見る |
| `blocked_trust` | 3 | 残る | 作業ディレクトリの信頼確認で止まった。**自動承認していない** |
| `blocked_unknown` | 3 | 残る | 未知の画面で止まった。画面を読んで判断する |
| `missing_output` | 4 | 残る | `--out` が作成も更新もされていない |
| `timeout` | 5 | 残る | 完了待ちが上限に達した |
| `create_failed` / `start_failed` / `prompt_failed` | 6 | 作成後なら残る | herdrの操作そのものが失敗した |

`out` の各要素は `created` / `updated` / `unchanged` / `absent` を返す。存在確認では通さず、実行前の `st_mtime_ns` と比較しているので、実行前から置いてあったファイルが更新されなければ失敗になる。

`create_failed` / `start_failed` / `prompt_failed` の `reason` にはherdrのエラーコード（`invalid_agent_name`・`agent_not_found` 等）が入る。agent名の制約違反は、tabを作る前に `invalid_input`（reason `name_invalid`）で止まる。

失敗した委譲を送り直すときは、tabを閉じてスクリプトごと起動し直す。手で送るなら、元の指示書ではなく `task_sent`（ヘッダを前置きした指示書。結果のJSONとstateに出る）を送る。元の指示書を送ると連絡経路と再委譲禁止のヘッダが欠ける。`task_sent` の一時ファイルは `done` のときだけ消える（JSONでは `null`）。

**`done` は作業の完了を保証しない。** 判定しているのは「idleになった時点で成果物ファイルが作成・更新されていた」ことだけで、書きかけ（骨組み・プレースホルダ）の保存でも満たす。逆に `missing_output` でも、委譲先がバックグラウンドの完了を待って作業を続けていることがある。どちらのstatusでも、成果物を採用する前に次の2つを確かめる。

- 委譲先から完了の連絡（ヘッダが求めるSendMessage等）が届いている
- `herdr pane get <pane_id>` の `agent_status` が `working` でない

満たさなければ作業中として扱い、成果物を採用せず、委譲をやり直さずに連絡を待つ。届いた連絡が「バックグラウンドの完了を待っている」等の途中経過なら、その完了の連絡を待つ。

`agent_status` がidleのまま連絡が届かないとき（codexのpane、Stop hookの1回を経ても送らなかった）は、待ち続けずに `herdr pane read` で画面の最後の応答を読み、完了か途中かを判断する。

### 調査と後片付け

tabはstatusによらず残る（`--close` 指定時の `done` を除く）。失敗した委譲ではpaneの画面が唯一の調査材料になる。

```bash
herdr pane read <pane_id> --source recent-unwrapped --lines 120
herdr pane get <pane_id>
```

tabはleadが閉じる。閉じてよいのは、上の「結果の受け取り」の2条件を満たして成果物を読み終えたとき、または失敗の調査を終えたとき。閉じるには `herdr tab close <tab_id>` を使う。放置したtabを残さない（次の委譲の画面が埋まり、どれが実行中の委譲か分からなくなる）。

## フォールバック

会話を使えないときは pane に、pane も使えない（`HERDR_ENV != 1`）ときはAgent toolに移る（委譲の必要性は環境で消えないため）。Codex実行時はAgent toolが無いので、`context/tool-codex.md` の逐次実行規定に従う。

移ってよい失敗は、スクリプトが返す `reason` で判別する。

| スクリプト | reason | 意味 | 扱い |
|---|---|---|---|
| taskboard-delegate.sh | `not_in_taskboard` | lead が taskboard の会話でも taskboard の herdr の pane でもない | pane へ |
| taskboard-delegate.sh | `taskboard_unavailable` | `taskboard` が無い | pane へ |
| taskboard-delegate.sh | `taskboard_outdated` | taskboard が知らせの届け先を受け付けない古い版 | pane へ |
| taskboard-delegate.sh | `start_failed` | 会話を起こせなかった。`detail` に taskboard の文が入る（会話の枠の上限・確かめた版が無いなど） | `detail` を読む。枠や版の問題なら pane へ |
| taskboard-delegate.sh | `unexpected_output` | 会話は起きたかもしれないが、id を読めなかった | `session_list` の会話の節で探す。見つかれば起こし直さない |
| herdr-delegate.sh | `not_in_herdr` | Herdrの外で実行された | Agent toolへ |
| herdr-delegate.sh | `herdr_unavailable` | `herdr` がPATHに無い | Agent toolへ |
| herdr-delegate.sh | `workspace_missing` | workspaceを特定できない | Agent toolへ |
| herdr-delegate.sh | `agent_cli_unavailable` | `--kind` に対応するCLIが無い | **条件付き**（下記） |
| 両方 | `task_invalid` / `task_id_invalid` / `model_invalid` / `effort_invalid` / `arg_invalid` / `python3_unavailable` | 呼び出し側の誤り | 直して再実行する |

フォールバックは、元のタスクが要求するモデル・ベンダーの条件を保てるときに限る。`--kind codex` が別ベンダーによる外部レビューを目的にしているなら、ClaudeのAgent toolへ切り替えるとbias独立性という品質ゲートを満たさないまま進むことになる。外部レビュー用途では `context/agent-cli-guide.md` のfallback規定（fable subagentで暫定。別ベンダーのレビューとはみなさず、不可逆な変更を含むときは復旧後に裏取り）が優先する。

## 実機で確定している挙動

推測で回避策を書かないための記録。変わり得るので、挙動が違ったらここを更新する。

### 会話の経路

- **委譲先のターンが終わると、数秒で lead に知らせが入る。** lead が taskboard の会話なら、知らせが次の人の発言になってターンが走る
- **スクリプトは会話を起こした時点で数秒で返る。** 委譲先の Claude Code は `--permission-mode bypassPermissions --disallowedTools Agent Workflow` で起き、成果物を書いて最後の返事で報告した（haiku で確認）
- **委譲先の会話は `--task-id` のタスクに結ばれる。** `session_list` の会話の節に「起動元」（lead の pane ID か会話の id の先頭 8 字）が出て、知らせを届けるまでは「未通知」が付く
- **lead が taskboard の herdr の pane なら、知らせは lead が入力待ちになったときに人の発言として入る。** lead が作業を続けている間は残り、その間に daemon を入れ替えても落ちない。届けると `session_list` の「未通知」が消える

### pane の経路

- **herdrはエラーをstderrにJSONで出す**（`{"error":{"code":...,"message":...}}`）。exitも非0で、stdoutは空になる。`2>/dev/null` で捨てると失敗の理由が一切取れない
- **`herdr agent start` は起動時ダイアログで止まっているpaneに対して `agent_not_ready` を返す。** これは「起動できなかった」ではなく「画面を見て分類すべき状態」。ダイアログを抜けた後に `agent start` を再実行しないとagent名が登録されず、以後の `agent prompt <name>` が使えない
- **codexの更新通知には選択ダイアログと通知バナーの2形態がある。** 「次のバージョンまでスキップ」を一度選ぶと、以後はバナーとして表示され続ける。`Update available!` の文字列だけでは区別できないので、選択待ちの目印は `Press enter to continue` で判定する
- **codexの承認バイパス（`--dangerously-bypass-approvals-and-sandbox`）は、作業ディレクトリの信頼確認ダイアログをバイパスしない。** 信頼確認は自動承認しない（プロンプトインジェクション耐性を落とすため）。信頼済みのディレクトリを `--cwd` に渡すか、`~/.codex/config.toml` の `[projects."<path>"]` に登録する
- **herdrのagent名は「小文字で始まり、小文字・数字・`-`・`_` だけの1〜32字」。** 違反すると `herdr agent start` が `invalid_agent_name` を返し、paneはシェルのまま残る（スクリプトは事前に検証する）
- **`herdr agent prompt` の宛先にはpane IDを使える。** Claude Codeのセッション名（SendMessageの宛先名）はherdrのagent名とは別物で、宛先にすると `agent_not_found` になる
- **codexに `-c` で設定を渡すと、共有のバックグラウンドサーバーを使わないembeddedモードで起動する**（起動時の警告に出る。スクリプトは更新確認を切るために `-c` を付けている）。embeddedモードでも起動・agent名の登録・MCPツールの呼び出しは通る
- **`codex exec --sandbox read-only` ではMCPツールを呼べず、`--dangerously-bypass-approvals-and-sandbox` では呼べる**（同じツール呼び出しで比較）
- **`claude --disallowedTools Agent Workflow` で両toolが外れ、SendMessage・ListAgentsは残る**（`-p` の起動時のtools一覧と、本スクリプト経由で起動したpaneのツール一覧の両方で確認。`-p` ではAgent toolが `Task` の名で出るが、`Agent` の指定で外れる。`TaskCreate` 等のタスク管理toolは残るが子エージェントは起動しない）。完了通知の経路はこれで壊れない
- **承認プロンプトのバイパスは既定で付く**（claude: `--dangerously-skip-permissions` / codex: `--dangerously-bypass-approvals-and-sandbox`）。承認待ちで止まると委譲が進まないため。追加のフラグは `--agent-arg` で透過的に渡せる
- **Bashの `run_in_background: true` はPreToolUse hookの `tool_input` に載り、前景の呼び出しでは項目自体が無い**（`claude -p` に記録用hookを足して確認）
- **`claude --settings '<JSON>'` で足したhookは、user-levelのhookを置き換えずに併用される**（委譲先のpaneで、足したStop hookとuser-levelのSessionStart・UserPromptSubmitが両方動いた）
- **Stop hookで1回止めると、委譲先は指示書に「連絡は不要」とあっても連絡を送る**（sonnetで確認）。ヘッダだけの委譲先は、hookが止める前に自分から `SendMessage` で送った
- **委譲先が `herdr agent prompt <lead pane>` で送った連絡は、leadの画面にユーザーの入力として入る**（cross-session messageの表示にならない）。送り主の区別が付きにくいので、ヘッダとStop hookはSendMessageを先に案内する
- `herdr pane run` と `herdr agent prompt` はテキストとEnterを一括送信する。改行を含む長文を直接渡すと途中で送信されるので、指示書はファイルに書いてパスだけを渡す（スクリプトがこれを行う）

## 未検証の経路

スクリプトに実装はあるが実機で通していない経路。ここに当たったら、挙動を確認してこのファイルを更新する。

- 会話の経路の `--worktree-branch`（MCP の `session_start` の `worktree_branch` では、worktree の中で動くことを確かめた）
- 委譲先が問いで待っているときの知らせと `session_answer`、知らせていないターンが2つ以上たまったときの数
- `--allow-review`
- 委譲先が利用枠の上限に当たった後の続きの送信（taskboard のテストでだけ確かめた）
- lead の pane で `/clear` した後に知らせが残ること、`/exit` と `claude --resume` で戻った pane に届くこと
- `start_failed`・`unexpected_output`
- `done_close_failed`（`--close` 指定時のtab closeの失敗）
- 起動タイムアウトによる `blocked_unknown`
- codexの更新選択ダイアログの自動スキップ（バナー形態しか再現できていない）。選択ダイアログ（更新する／スキップ／このバージョンをスキップの3択）が出たpaneは、自動スキップが効かずに `prompt_failed`（agent名が未登録）で落ちた例がある。対策として、スクリプトはcodexを `-c check_for_update_on_startup=false` で起動し、ダイアログ自体を出さない。ダイアログが出なくなることは次の更新が来るまで確かめられないので、それでも出たら画面（`herdr pane read`）を保存してから判定を直す
