---
name: taskherd
description: taskherd CLI（エージェントセッション・PR・チケットをタスク単位で束ねるローカル kanban）の操作。使用タイミング (1) 自分のセッションに紐づくボードのタスクの列を進める・note を残す時、(2) 作業中に新しいタスクが確定して起票する時、(3) ボード上のタスク一覧・状態を確認する時、(4) 依頼に taskherd・タスクボード・kanban の語がある時。境界: セッション内の作業ステップ管理（TaskCreate / TodoWrite）は対象外。pane・tab・agent そのものの操作は herdr、実装タスクのスキル連鎖の管理は task。board / picker の TUI 操作はユーザーの領域で、本スキルは CLI だけを扱う。
allowed-tools: Bash(taskherd:*), Bash(herdr:*), Bash(jq:*)
---

# Taskherd

タスク 1 件に、エージェントセッション・PR・Issue・チケット・note を束ねるローカル kanban。状態は `~/.local/state/taskherd/tasks.json`（`taskherd config path` で確認）にあり、CLI からもボード TUI からも同じデータを見る。

## 前提

```bash
command -v taskherd
```

見つからなければ、その旨を伝えて止まる。パスを推測して直接バイナリを叩かない。

`session link` / `start` / `jump` は herdr サーバに問い合わせるため、herdr が動いていない環境では失敗する。`--current` はさらに `HERDR_PANE_ID` を必要とするので、herdr の pane の中からしか使えない。

## `--json` の契約

**非対話で使うときは常に `--json` を付ける。**

| | |
|---|---|
| 成功 | stdout に単一の JSON オブジェクト、stderr は空、exit 0 |
| 失敗 | stderr に `{"error": ..., "hint": ...}`、stdout は空、exit は非 0 |

- `--json` では一切対話しない。入力が要る状況はエラーで落ちる。`rm` は `--yes`、`note` は `--set` か `--append` が必須
- `hint` を必ず読む。無効な列 id を渡したときは有効な id の一覧が `hint` に入る
- **例外は `start`**。途中で止まっても結果を stdout に出して exit が非 0 になる。成否は exit code ではなく `stage`（`started` → `waited` → `linked` → `prompted`）と `linked` / `prompt_sent` で判定する

## 列

列は config の `[[columns]]` 次第。id をハードコードせず、その環境の定義を見る:

```bash
sed -n '/^\[\[columns\]\]/,/^$/p' "$(taskherd config path --json | jq -r .config)"
```

`taskherd list` の 2 カラム目にも列 id が出るが、**タスクが 1 件も無い列は行ごと現れない**ので一覧の代わりにはならない。無効な列 id を渡したときのエラーの `hint` には常に全 id が入るので、そちらでも確認できる。

**`add` の既定列は config の先頭列**。先頭が受け口用の列だと起票したものが意図しない場所に入るので、**起票時は常に `--status` を明示する**。

役割で選ぶ。id はその環境の定義に読み替える:

| 状況 | 列の役割 | 標準的な id |
|---|---|---|
| 他人の PR・チケットのレビューを頼まれた | 受け口 | `review_req` |
| やると決まったが未着手 | 待ち | `todo` |
| 方針・設計を詰めている | 計画 | `planning` |
| 実装・調査を実際に進めている | 作業中 | `working` |
| PR を出してレビュー待ち | レビュー | `review` |
| approve 済みで反映・リリース待ち | 反映待ち | `deploying` |
| 完了した | 終端 | `done` |
| やらないと決めた | 終端 | `wontfix` |

## 自分のセッションのタスクを進める

**自律的に動かしてよいのは、自分のセッションに紐づくタスクだけ。** 他のタスクの列は、ユーザーの指示なしに変えない。

**PR の状態に対応する列の前進は Stop hook（`hooks/taskherd-sync.py`）が自動で行う。** PR が Ready になれば review、merge されれば deploying へ、ターン終了時に前進する（前進方向のみ・終端列は触らない）。この2つを手で `move` しに行く必要はない。手で動かすのは hook が判断しない列（planning / working / wontfix 等）と、ユーザーから指示された移動だけ。

**紐づくタスクが無い状態で PR が open していれば、同 hook が Stop で自動起票する**（タイトルは PR のタイトル、列は draft なら working / ready なら review、PR URL を link、セッションを紐づけ）。同じ URL のタスクが既にあれば起票せずそれに紐づけるので、手で起票し直さない。

PR がまだ無い段階で実装が進んでいる場合は、同 hook が UserPromptSubmit で1回だけ起票を促す。促されたら下記「起票する」に従う（この経路だけは自分でタイトルと note を決める）。

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

**確認できた事実に対応する遷移だけ行う。** 自分が実行した操作（PR を出した・merge した）と `taskherd show <ID> --json` の live 状態は根拠になる。根拠なく先の列へ進めない。判断がつかないときは動かさず、ユーザーに聞く。

完了基準: `move` の応答の `task.status` が意図した列 id と一致している。

## 起票する

### 重複を避ける

**起票の前に、紐づける URL で既存タスクを引く。** 同一性の判断は URL で行う（タイトルは表記が揺れて照合できない）:

```bash
taskherd list --all --json | jq --arg u "$URL" \
  '[.tasks[] | select(any(.links[]?; .url == $u)) | {id,title,status}]'
```

ヒットしたら新規に作らず、そのタスクに `link` / `note` を足すか列を動かす。

### 作る

```bash
taskherd add "<TITLE>" --status <COL> --link <URL> --note "<WHY>" --json
```

- **粒度は「1 タスク = 1 つの完了判定」**。PR 1 本・チケット 1 件・調査 1 件が単位。複数 PR にまたがる 1 つの作業は、束ねる 1 タスクにリンクを複数付ける（PR ごとに割らない）
- **タイトルは、何が終われば完了かが読み取れる形にする。** チケット由来ならチケット側の表題をそのまま使う（後から照合できるため）
- `--link` は複数回指定できる。PR / Issue / チケットの種別は URL から自動判別する
- `--note` には**セッションをまたいで必要になる文脈だけ**を書く（決めた方針・詰まっている点・再開条件）。作業ログはメモリディレクトリ側（@context/memory-file-formats.md）に書く

完了基準: `add` の応答で `task.status` が意図した列 id になっていて、`task.links` に渡した URL が入っている。

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

`start` は前回同じタスクで起こした agent が idle で残っていればそれを回収する（応答の `reused: true`）。意図的に 2 つ目を起こすなら `--new`。cwd の候補が定まらなければ `--cwd` が必須で、前回と違う cwd を渡した場合は回収も新規起動もせず案内を返す。

## Gotchas

- **`--json` を省くと `note` と `rm` が対話に入る。** エージェントから叩くときは必ず付ける
- **`start` は exit code だけで成否を判断しない**（stdout の `stage` を読む）
- **`show` の live 状態はキャッシュ**（config の `cache_ttl_minutes`）。最新が要るなら `taskherd refresh <ID> --json` を先に叩く
- **タスク id は削除しても再利用されない**（`next_id` は単調増加）。一度得た id は安定した handle として使える
- **`taskherd board` をエージェントから起動しない。** TUI はユーザーが開くもので、非対話の実行では無意味に pane を占有する

## 既存設定との関係

- **pane・tab・agent そのものの操作**: /herdr（本スキルは taskherd CLI だけを扱う）
- **実装タスクのスキル連鎖の管理**: /task（本スキルはボード上の状態管理だけを扱う）
- **作業ログ・調査記録**: @context/memory-file-formats.md（note と使い分ける）
