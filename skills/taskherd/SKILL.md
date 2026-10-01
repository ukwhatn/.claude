---
name: taskherd
description: taskherd CLI（セッション・PR・チケットをタスク単位で束ねるローカル kanban）の操作。自分のセッションに紐づくタスクの列を進める・note を残す時、新しいタスクを起票する時、ボードのタスク一覧・状態を確認する時、依頼に taskherd・タスクボード・kanban の語がある時に使用。CLI のみを扱い、board / picker の TUI 操作はユーザーの領域。境界: セッション内の作業ステップ管理は対象外、pane・tab・agent の操作は herdr。
allowed-tools: Bash(taskherd:*), Bash(herdr:*), Bash(jq:*)
---

# Taskherd

タスク1件に、エージェントセッション・PR・Issue・チケット・noteを束ねるローカルkanban。状態は `~/.local/state/taskherd/tasks.json`（`taskherd config path` で確認）にあり、CLIからもボードTUIからも同じデータを見る。

## 前提

```bash
command -v taskherd
```

見つからなければ、その旨を伝えて止まる。パスを推測して直接バイナリを実行しない。

`session link` / `start` / `jump` はherdrサーバに問い合わせるため、herdrが動いていない環境では失敗する。`--current` はさらに `HERDR_PANE_ID` を必要とするので、herdrのpaneの中からしか使えない。

## `--json` の契約

**非対話で使うときは常に `--json` を付ける。**

| | |
|---|---|
| 成功 | stdoutに単一のJSONオブジェクト、stderrは空、exit 0 |
| 失敗 | stderrに `{"error": ..., "hint": ...}`、stdoutは空、exitは非0 |

- `--json` では一切対話しない。入力が要る状況はエラーで終了する。`rm` は `--yes`、`note` は `--set` か `--append` が必須
- `hint` を必ず読む。無効な列idを渡したときは有効なidの一覧が `hint` に入る
- **例外は `start`**。途中で止まっても結果をstdoutに出してexitが非0になる。成否はexit codeではなく `stage`（`started` → `waited` → `linked` → `prompted`）と `linked` / `prompt_sent` で判定する

## 列

列はconfigの `[[columns]]` 次第。idをハードコードせず、その環境の定義を見る:

```bash
sed -n '/^\[\[columns\]\]/,/^$/p' "$(taskherd config path --json | jq -r .config)"
```

`taskherd list` の2カラム目にも列idが出るが、**タスクが1件も無い列は行ごと現れない**ので一覧の代わりにはならない。無効な列idを渡したときのエラーの `hint` には常に全idが入るので、そちらでも確認できる。

**`add` の既定列はconfigの先頭列**。先頭が受け口用の列だと起票したものが意図しない場所に入るので、**起票時は常に `--status` を明示する**。

役割で選ぶ。idはその環境の定義に読み替える:

| 状況 | 列の役割 | 標準的なid |
|---|---|---|
| 他人のPR・チケットのレビューを頼まれた | 受け口（レビュー投稿後もマージまで留まる） | `review_req` |
| やると決まったが未着手 | 待ち | `todo` |
| 方針・設計を詰めている | 計画 | `planning` |
| 実装・調査を実際に進めている | 作業中 | `working` |
| PRを出してレビュー待ち | レビュー | `review` |
| approve済みで反映・リリース待ち | 反映待ち | `deploying` |
| 完了した | 終端 | `done` |
| やらないと決めた | 終端 | `wontfix` |

## 自分のセッションのタスクを進める

**自律的に動かしてよいのは、自分のセッションに紐づくタスクだけ。** 他のタスクの列は、ユーザーの指示なしに変えない。

**PRの状態に対応する列の前進はStop hook（`hooks/taskherd-sync.py`）が自動で行う。** PRがReadyになればreview、mergeされればdeployingへ、ターン終了時に前進する（前進方向のみ・終端列は触らない）。この2つを手で `move` しに行く必要はない。手で動かすのはhookが判断しない列（planning / working / wontfix等）と、ユーザーから指示された移動だけ。

**レビュー依頼の受け口（`review_req`）に入ったタスクは、`review_req` と終端列（`done` / `wontfix`）しか取らない。** 紐づいているのは他人のPRなので、自分がapproveしても作業段階は進まない。**レビューを投稿したらタイトルの頭に `✅ ` を付けて `review_req` に留め、`done` へ移すのはリンク先のPRがマージされてから。** マージされるまでは「レビュー済み・マージ待ち」であり、タイトルの `✅ ` がその状態を表す。中間列（`working` / `review` / `deploying`）へは動かさない（Stop hookもreview_reqのタスクは前進させない）。

**紐づくタスクが無い状態でPRがopenしていれば、同hookがStopで自動起票する**（タイトルはPRのタイトル、列はdraftならworking / readyならreview、PR URLをlink、セッションを紐づけ）。同じURLのタスクが既にあれば起票せずそれに紐づけるので、手で起票し直さない。

PRがまだ無い段階で実装が進んでいる場合は、同hookがUserPromptSubmitで1回だけ起票を促す。促されたら下記「起票する」に従う（この経路だけは自分でタイトルとnoteを決める）。

### 1. 自分に紐づくタスクを引く

```bash
sid=$(herdr pane current --current | jq -r '.result.pane.agent_session.value')
taskherd list --all --json | jq --arg s "$sid" \
  '[.tasks[] | select(any(.sessions[]?; .session_id == $s)) | {id,title,status}]'
```

空配列なら、このセッションはまだどのタスクにも紐づいていない。

### 2. 紐づける

```bash
taskherd session link <ID> --current --json
```

### 3. 列を進める

```bash
taskherd move <ID> <STATUS> --json
```

**確認できた事実に対応する遷移だけ行う。** 自分が実行した操作（PRを出した・mergeした）と `taskherd show <ID> --json` のlive状態は根拠になる。根拠なく先の列へ進めない。判断がつかないときは動かさず、ユーザーに聞く。

完了基準: `move` の応答の `task.status` が意図した列idと一致している。

## 起票する

### 重複を避ける

**起票の前に、紐づけるURLで既存タスクを引く。** 同一性の判断はURLで行う（タイトルは表記が揺れて照合できない）:

```bash
taskherd list --all --json | jq --arg u "$URL" \
  '[.tasks[] | select(any(.links[]?; .url == $u)) | {id,title,status}]'
```

ヒットしたら新規に作らず、そのタスクに `link` / `note` を足すか列を動かす。

### 作る

```bash
taskherd add "<TITLE>" --status <COL> --link <URL> --note "<WHY>" --json
```

- **粒度は「1タスク = 1つの完了判定」**。PR 1本・チケット1件・調査1件が単位。複数PRにまたがる1つの作業は、束ねる1タスクにリンクを複数付ける（PRごとに割らない）
- **タイトルは、何が終われば完了かが読み取れる形にする。** チケット由来ならチケット側の表題をそのまま使う（後から照合できるため）
- `--link` は複数回指定できる。PR / Issue / チケットの種別はURLから自動判別する
- `--note` には**セッションをまたいで必要になる文脈だけ**を書く（決めた方針・詰まっている点・再開条件）。作業ログはメモリディレクトリ側（@context/memory-file-formats.md）に書く

完了基準: `add` の応答で `task.status` が意図した列idになっていて、`task.links` に渡したURLが入っている。

### 後から足す

```bash
taskherd link <ID> <URL> --json
taskherd unlink <ID> <URL> --json
taskherd note <ID> --append "<TEXT>" --json     # --set で全置換
taskherd edit <ID> --title "<NEW>" --due YYYY-MM-DD --json
```

## セッションを起こす・戻る

ユーザーがタスクから作業を始めたい・戻りたいときに使う。

```bash
taskherd start <ID> --json      # 新しい pane で agent を起こし、紐づけて初期プロンプトを送る
taskherd jump <ID> --json       # 紐づいたセッションへ移動する（消えていれば resume 起動）
```

`start` は前回同じタスクで起こしたagentがidleで残っていればそれを回収する（応答の `reused: true`）。意図的に2つ目を起こすなら `--new`。cwdの候補が定まらなければ `--cwd` が必須で、前回と違うcwdを渡した場合は回収も新規起動もせず案内を返す。

## Gotchas

- **`--json` を省くと `note` と `rm` が対話に入る。** エージェントから実行するときは必ず付ける
- **`start` はexit codeだけで成否を判断しない**（stdoutの `stage` を読む）
- **`show` のlive状態はキャッシュ**（configの `cache_ttl_minutes`）。最新が要るなら `taskherd refresh <ID> --json` を先に実行する
- **タスクidは削除しても再利用されない**（`next_id` は単調増加）。一度得たidは安定したhandleとして使える
- **`taskherd board` をエージェントから起動しない。** TUIはユーザーが開くもので、非対話の実行では無意味にpaneを占有する

## 既存設定との関係

- **pane・tab・agentそのものの操作**: /herdr（本スキルはtaskherd CLIだけを扱う）
- **作業ログ・調査記録**: @context/memory-file-formats.md（noteと使い分ける）
