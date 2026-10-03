# herdr paneへの委譲

Read when: 作業の委譲を検討した時点。経路の選択・指示書の書き方・結果の回収・後片付けの規則はここが真実源。

**Agent toolを選ぶ場合も本ファイルを読む。** 経路の選択軸はここにあり、指示書の書き方と生成物の検証は経路によらず同じだから。pane固有なのは起動と結果の回収の手順だけ。

herdr CLIそのものの構文・ID規約・状態モデル（idle / done / blocked）は `skills/herdr/SKILL.md` が真実源。本ファイルは委譲のポリシーと `bin/herdr-delegate.sh` の運用を扱う。

## 経路の選択

**「委譲先自身が成果物をファイルに書くか」で決める。体数・調査範囲・所要時間では決めない。**

| 委譲の内容 | 経路 |
|---|---|
| **委譲先自身がファイルを書く**（実装・ファイル生成・issueやレポートの作成） | **pane**（`bin/herdr-delegate.sh`） |
| **委譲先はファイルを書かず、結果をleadに返す**（`Explore` による探索、複数観点のレビュー報告、freshな単発判定） | Agent tool |

書き込みの有無で切るのは、中断したときに失われるものが違うため。`Explore` は書き込み不可なので、中断してもやり直せば同じ結論に戻れる。ファイルを書く委譲が中断すると、書きかけの作業文脈が失われ、成果物が不完全な状態でディスクに残る（どこまで書けているかをleadが読み直して判断することになる）。

paneを選ぶ利点は3つ。レートリミットに当たってもpane側のClaude Codeが `autoContinueAtUsageLimit` で継続し、失敗で終わらない。進捗がpaneの画面にそのまま出る。他ベンダーのエージェントを同じ手順で扱える。

委譲するかどうか自体の判断（1体で足りるか、自分でやるほうが速いか）は `context/tool-claude-code.md`「委譲判断」に従う。本ファイルは「委譲すると決めた後」を扱う。

## モデルの選択

**委譲先のモデルは経路によらず用途で決め、毎回明示する。** paneは `--model`、Agent toolは `model` パラメータで渡す。Agent toolは `model` を省略すると親セッションのモデルを継承するので、fableのセッションから省略して委譲すると調査1本にfableを使うことになる。省略してよいのは「親と同じモデルが要る」と判断したときだけで、その判断を05_log.mdに書く。

**委譲は基本Claude（`--kind claude`）で行う。** codexはsubscriptionの枠が小さいので、**別ベンダーであること自体が要件になる用途（外部レビュー）に温存する**。

| 用途 | pane（`bin/herdr-delegate.sh`） | Agent tool |
|---|---|---|
| 設計判断を含む実装・文書生成 | `--kind claude --model opus`（effortは既定のmedium） | paneで行う（ファイルを書く委譲はAgent toolを使わない） |
| パターンが確立した実装・横展開（リネーム・既知パターンの適用） | `--kind claude --model opus --agent-arg --effort --agent-arg low` | 同上 |
| コードを書かない調査（コード内のファイル探し・ログ / テスト出力の読み取り・Web / 文書の収集と要約） | `--kind claude --model sonnet` | `model: "sonnet"`。コード内の探索は `subagent_type: "Explore"`、Web / 外部資料は `general-purpose` |
| 複数観点のレビュー報告・freshな単発判定（結果をleadが検証する） | — | `model: "opus"` |
| 前例のない難所・監督しない長時間の実行・壁打ち | `--kind claude --model fable` | `model: "fable"` |
| 外部レビュー（別ベンダーのbias独立性が要る） | `--kind codex` | —（`context/agent-cli-guide.md`） |

Sonnetにはコードを書かせない。小さいモデルが読み違えるとleadが誤った前提で進むため、結果の誤りに気づきやすい作業に限る。調査をsonnetに任せるときは、報告の事実を一次ソースで突き合わせてから採用する（`AGENTS.md`「自律実行と委譲」）。opusのmediumで同じ問題に2回詰まったら、`--agent-arg --effort --agent-arg high` かfableで委譲し直す。

codexを起動する前に枠を確認する（`python3 ~/.claude/codex-usage.py --refresh` → `--show`）。枯渇していれば `context/agent-cli-guide.md` のfallback規定に従う。**枠に余裕があっても、Claudeで足りる委譲にcodexを使わない。**

## Herdr外でのフォールバック

`HERDR_ENV != 1` の環境ではpaneを使えない。このときは **Agent toolにフォールバックする**（委譲の必要性は環境で消えないため）。Codex実行時はAgent toolが無いので、`context/tool-codex.md` の逐次実行規定に従う。

フォールバックしてよい失敗は、スクリプトが返す `reason` で判別する。

| reason | 意味 | 扱い |
|---|---|---|
| `not_in_herdr` | Herdrの外で実行された | Agent toolへ |
| `herdr_unavailable` | `herdr` がPATHに無い | Agent toolへ |
| `workspace_missing` | workspaceを特定できない | Agent toolへ |
| `agent_cli_unavailable` | `--kind` に対応するCLIが無い | **条件付き**（下記） |
| `task_invalid` / `arg_invalid` / `python3_unavailable` | 呼び出し側の誤り | 直して再実行する |

**フォールバックは、元のタスクが要求するモデル・ベンダーの条件を保てるときに限る。** `--kind codex` が別ベンダーによる外部レビューを目的にしているなら、ClaudeのAgent toolへ切り替えるとbias独立性という品質ゲートを満たさないまま進むことになる。**外部レビュー用途では `context/agent-cli-guide.md` のfallback規定（fable subagentで暫定。別ベンダーのレビューとはみなさず、不可逆な変更を含むときは復旧後に裏取り）が優先する。**

## ライフサイクル

`bin/herdr-delegate.sh` は完了まで同期ブロックする。**`--state` を付けてバックグラウンドで起動し、stateファイルの生成を確認してからそのターンを終える。** 完了はharnessの通知で受け取る。

```bash
~/.claude/bin/herdr-delegate.sh \
  --kind claude --model opus \
  --task "<指示書の絶対パス>" \
  --out "<成果物の絶対パス>" \
  --state "<state の絶対パス>" --run-id "<lead が採番した ID>" \
  --lead-name "<ListAgents に出る自分のセッション名>" \
  --name "<agent 名>" --cwd "<自セッションの起動ディレクトリ>" \
  > "<結果 JSON の出力先>" 2> "<ログの出力先>"
```

**`--cwd` には自セッションが起動されたディレクトリをそのまま渡す。** 作業対象がその配下の
サブディレクトリ・別リポジトリでも変えない。指示書で対象を絶対パスで示し、git操作は
`git -C <対象の絶対パス>` で行わせる。

起動ディレクトリ以外を渡すと、そのディレクトリが信頼済みでない場合にagentの起動時
信頼確認ダイアログで止まり、委譲が `start_failed`（exit 6）になる。この確認は自動承認しない
規定なので、渡すディレクトリを起動ディレクトリに揃えることで確認自体を発生させない。

- `--state` はtab作成とagent起動の直後に `{"run_id","name","tab_id","pane_id","task","out","started_at"}` を書き出す。stdoutの最終JSONは完了まで出ないので、識別子はここから取る
- **stateを読んだら `run_id` の一致を確認してから採用する**（同じパスに前回実行のstateが残っていると、置換前の古い内容を読むことがある）
- **起動したら05_log.mdに1行記録してからターンを終える**（agent名 / tab_id / 指示書 / 成果物 / 起動時刻）。compactionから復帰したら、この記録と `herdr tab list` を突き合わせる。**記録に残っている委譲を再起動しない**
- 並列に回すときは、ジョブごとに `--state` / `--out` / 結果JSON / ログの保存先を分ける

### `~/.claude` の追跡ファイルをpaneに直接書かせない

user-level設定の変更は同じターン内でcommit・pushまで完了させる規定がある（`AGENTS.md`「コミット・ブランチ・PR」）。pane委譲はターンをまたぐため、これと両立しない。

**paneには草案をメモリディレクトリ（git管理外）へ書かせ、leadが全文を確認してから追跡下のファイルへ適用し、そのターン内でcommit・pushする。** これは「委譲先の生成物をそのまま成果物にしない」規定（`AGENTS.md`「自律実行と委譲」）とも一致する。

## 指示書の書き方

**委譲先は指示書だけを読んで作業できる状態にする。** leadの会話履歴は共有されない。

| 項目 | 内容 |
|---|---|
| 目的 | 何のための成果物か。1〜2文 |
| 成果物 | **絶対パスで1つ**。複数書かせるなら全て絶対パスで列挙する |
| 入力 | 読むべきファイルの絶対パス。何が書いてあるかを1行添える |
| 構成 | 成果物に含める章立て。順序も指定する |
| やらないこと | 触ってはいけないファイル、取り込まない情報源、書いてはいけない内容 |
| 完了基準 | 満たしていれば完了と判断できる条件を、確認可能な形で列挙する |
| 完了の通知 | **成果物を書き終えたらleadへ完了を送ってから終了する**（Claude Codeのpaneなら `SendMessage` で `--lead-name` の宛先へ、codexなら `herdr agent prompt`）。送る内容は成果物のパスと要点数行。これが無いと委譲先はstandaloneで止まり、leadは完了を検知できずに待ち続ける |

**確認済みの事実と未確認の推測を分けて書く。** 推測を事実として書いて渡すと、委譲先はそれを検証せずに前提として使う。

**要件・仕様文書に基づく作業では、対象条項の原文を指示書に引用する。** leadの解釈・決定に変換した形だけを渡すと、変換で脱落した条件・対象・適用除外を委譲先は構造上検出できなくなる。leadの決定が原文と異なる箇所は、異なることと理由を明記して渡す（断りのない差し替えは、委譲先には要件そのものに見える）。

`herdr-delegate.sh` は指示書の先頭に**連絡経路の定型ヘッダを自動で前置きする**ので、指示書側に書く必要はない。ヘッダとタスク本文が食い違ったときは**タスク本文が優先する**とヘッダ自身に明記してある。

## 委譲先とのやり取り

委譲先は、指示書の前提が実態と食い違ったときにleadへ問い合わせる。問い合わせの方法はヘッダに書いてある。

- **pane上のClaude Code**: `ListAgents` に現れるので、`SendMessage` で名前宛に送れる。lead → 委譲先も同じ
- **pane上のcodex**: SendMessageは届かない。`herdr agent prompt <name> "<メッセージ>"` を使う（委譲先からleadへも、codexがBashでこのコマンドを叩く）

**leadがスクリプトを同期実行していると、問い合わせをリアルタイムに受け取れない**（完了後にまとめて届く）。バックグラウンド起動が必要なのはこのためでもある。

**委譲先が問い合わせて応答を終えると、lead側からは「成果物なし」に見える**（`missing_output` / exit 4）。失敗と断ずる前に、委譲先からのメッセージが届いていないかを確認する。

追加指示を送るにはtabが残っている必要があるので、やり取りが予想される委譲は `--keep` を付ける。

## 結果の受け取り

**成果物はファイルから読む。paneの画面を成果物の受け取り口にしない。**

スクリプトは終了時に1行JSONをstdoutに出す。

| status | exit | tab | 意味 |
|---|---|---|---|
| `done` | 0 | 閉じた | 正常終了 |
| `done_close_failed` | 7 | 残る | 作業は完了したがtabを閉じられなかった。手で片付ける |
| `invalid_input` | 2 | 作らない | 前提エラー。`reason` を見る |
| `blocked_trust` | 3 | 残る | 作業ディレクトリの信頼確認で止まった。**自動承認していない** |
| `blocked_unknown` | 3 | 残る | 未知の画面で止まった。画面を読んで判断する |
| `missing_output` | 4 | 残る | `--out` が作成も更新もされていない |
| `timeout` | 5 | 残る | 完了待ちが上限に達した |
| `create_failed` / `start_failed` / `prompt_failed` | 6 | 作成後なら残る | herdrの操作そのものが失敗した |

`out` の各要素は `created` / `updated` / `unchanged` / `absent` を返す。**存在確認では通さず、実行前の `st_mtime_ns` と比較している**ので、実行前から置いてあったファイルが更新されなければ失敗になる。

## 失敗時の調査と後片付け

失敗した委譲はtabを残す。paneの画面が唯一の調査材料になるため。

```bash
herdr pane read <pane_id> --source recent-unwrapped --lines 120
herdr pane get <pane_id>
```

調べ終えたら `herdr tab close <tab_id>` で閉じる。**放置したtabを残さない**（次の委譲の画面が埋まり、どれが実行中の委譲か分からなくなる）。

## 実機で確定している挙動

推測で回避策を書かないための記録。**変わり得るので、挙動が違ったらここを更新する。**

- **herdrはエラーをstderrにJSONで出す**（`{"error":{"code":...,"message":...}}`）。exitも非0で、stdoutは空になる。`2>/dev/null` で捨てると失敗の理由が一切取れない
- **`herdr agent start` は起動時ダイアログで止まっているpaneに対して `agent_not_ready` を返す。** これは「起動できなかった」ではなく「画面を見て分類すべき状態」。ダイアログを抜けた後に `agent start` を**再実行**しないとagent名が登録されず、以後の `agent prompt <name>` が使えない
- **codexの更新通知には選択ダイアログと通知バナーの2形態がある。** 「次のバージョンまでスキップ」を一度選ぶと、以後はバナーとして表示され続ける。`Update available!` の文字列だけでは区別できないので、**選択待ちの目印は `Press enter to continue`** で判定する
- **codexの承認バイパス（`--dangerously-bypass-approvals-and-sandbox`）は、作業ディレクトリの信頼確認ダイアログをバイパスしない。** 信頼確認は自動承認しない（プロンプトインジェクション耐性を落とすため）。信頼済みのディレクトリを `--cwd` に渡すか、`~/.codex/config.toml` の `[projects."<path>"]` に登録する
- **承認プロンプトのバイパスは既定で付く**（claude: `--dangerously-skip-permissions` / codex: `--dangerously-bypass-approvals-and-sandbox`）。承認待ちで止まると委譲が進まないため。追加のフラグは `--agent-arg` で透過的に渡せる
- `herdr pane run` と `herdr agent prompt` はテキストとEnterを一括送信する。**改行を含む長文を直接渡すと途中で送信される**ので、指示書はファイルに書いてパスだけを渡す（スクリプトがこれを行う）

## 未検証の経路

スクリプトに実装はあるが実機で通していない経路。ここに当たったら、挙動を確認してこのファイルを更新する。

- `done_close_failed`（tab closeの失敗）
- 起動タイムアウトによる `blocked_unknown`
- codexの更新**選択ダイアログ**の自動スキップ（バナー形態しか再現できていない）
