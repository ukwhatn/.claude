# ソース部品: Jira（Cloud）

自分が担当のチケットの新規検出と、ステータスと列の対応。Jira のステータスへの書き戻しは**既定で許可しない**。許可するなら「2-1c ステータスの同期」の表を埋めて貼る。

## 固定値の行

| 対象 | 値 |
|---|---|
| Jira | `{{JIRA_SITE}}`（Cloud）だけ |
| Jira の API トークン | `{{JIRA_TOKEN_FILE}}`（権限 600。中身を表示しない） |
| Jira の MCP（遷移を許可するときだけ） | `{{JIRA_MCP}}` |

## 収集（1-2〜 に貼る）

### 1-N. Jira（新規検出だけ）

MCP ではなく REST を使う。MCP の検索は同じクエリでアバターの URL 等を含む大きな JSON を返し、毎回の実行には重い。トークンをコマンドラインの引数に載せないため、`curl --config -` で標準入力から渡す:

```bash
printf 'user = "{{JIRA_USER}}:%s"\n' "$(cat {{JIRA_TOKEN_FILE}})" | curl -s --config - -G \
  --data-urlencode 'jql=assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC' \
  --data-urlencode 'fields=summary,status,duedate,priority,updated' \
  --data-urlencode 'maxResults=50' \
  'https://{{JIRA_SITE}}/rest/api/3/search/jql' \
  | jq -r '.issues[] | "\(.key)\t\(.fields.status.name)\t\(.fields.duedate // "-")\t\(.fields.updated)\t\(.fields.summary)"'
```

## 2-1 に足す判定

Jira がリンクされたタスク。ステータスの名前はプロジェクトのワークフローで決まるので、分類（`category`）で決まる行は固定、名前で決まる行は埋める:

| live 状態 | 列 |
|---|---|
| `category=new` | 未着手 |
| `statusName` が {{JIRA_STATUS_WORKING}} | 作業中 |
| `statusName` が {{JIRA_STATUS_REVIEW}} | レビュー中 |
| `statusName` が {{JIRA_STATUS_DEPLOYING}} | 「マージしたら」の列（デプロイ待ち） |
| `category=done` | **完了候補 → 通知だけ** |

表に無いステータスでは列を動かさない。

## 2-1c ステータスの同期（任意。許可した遷移だけ）

taskboard の列を動かすのと同じ観測値で、Jira のステータスも追わせる。許可するのは「自分の手を離れた事実の反映」だけにする。

**実行してよい遷移（無確認・事後報告）**:

| ワークフロー | 今の status_name | 遷移名 | 遷移先 | 発火条件 |
|---|---|---|---|---|
| {{JIRA_WORKFLOW}} | {{FROM_STATUS}} | {{TRANSITION_NAME}} | {{TO_STATUS}} | {{TRIGGER}}（例: リンク PR が `state=MERGED`） |

**表に入れない遷移**（見つけたら「■ 要判断」に出して指示を待つ）:

- assignee を他の人へ移す遷移（他者への作業依頼に等しい）
- 本番での確認・人による動作確認が済んだことを前提にする遷移（タグの到達だけでは根拠にならない）
- 完了・Close・対応しない等の終端（禁止事項3と同じ）
- 差し戻し・後退（列を後退させない原則と同じ）
- 遷移の時にフィールドの記入を伴う遷移

**実行の条件**:

- **今の status_name が表の「今」と完全に一致するときだけ実行する。** 一致しなければ何もしない（想定外の位置にいる、または人が既に動かしている）
- **PR が複数リンクされている場合は、最も手前の PR が発火条件を満たすまで実行しない**（1本が merge されても、別の1本が draft なら実装は終わっていない）
- `decisions[<タスク番号>]` が `hold` / `pin_column` のタスクは対象外
- 1回の遷移は上限3件（超える分は次の回に回し「■ 打ち切り」に書く）

**手順**（Step 3 に貼る）:

1. `.tb-state.json` の `links[].jira.statusName` で今のステータスを確かめ、表の「今」と一致することを確かめる
2. `getTransitionsForJiraIssue` で使える遷移を取り、**表の遷移名に一致するものの id を取る**（遷移の id は今の状態で変わるので、固定値として持たない。一致する遷移名が無ければ実行せず「■ エラー」に書く）
3. `transitionJiraIssue` で遷移する
4. note に「Jira <KEY> を <遷移前> → <遷移後> へ同期（根拠: <PR URL> が MERGED）」を追記する
5. 通知の「■ 外部への書き戻し」に `<KEY> <遷移前> → <遷移後>  (#<タスク番号> / <根拠>)` を1行出す

`{{JIRA_MCP}}` が繋がっていなければ遷移をスキップし、「■ エラー」に書いて次の回に回す（推測で REST を叩かない）。

## 起票の既定

- **`since` 以降に更新された**、どのタスクにもリンクされていないチケットを**自動で起票する**（`seen.decision = "created"`）。列は 2-1 の対応に従う
- **全件は起票しない**。未完了のチケットは常に十数件あり、全部入れるとボードが埋まる
- タイトルはチケットの表題をそのまま使う
- `seen` のキー: チケットの URL
- `due` はチケットの `duedate` を入れる

## cursor

なし（`since` で絞る）。

## 上限

| 項目 | 上限 |
|---|---|
| Jira の検索 | 50件 |
| 1回の Jira の遷移 | 3件 |

## 禁止事項

- Jira へ書き込まない（コメント・フィールドの編集・assignee の変更・課題の作成）。**例外は 2-1c の表で許可した遷移だけ**。表を貼っていない、または手順書が読めないときは、Jira へ何も書かない
