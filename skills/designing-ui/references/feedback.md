# フィードバック・空状態・読み込み・エラー

操作の結果・システムの状態・空の領域・待ち時間・入力の誤りを、どの型で、どこに出すかを決める。文の書き方（エラー文の3要素・空状態の文・完了通知の文）は `/writing-ui-text` の5・6・8節が扱うので、ここでは型と配置だけを書く。

## 目次

1. 判断軸
2. 型の一覧
3. 決定表
4. 空状態
5. 読み込み
6. エラーの配置
7. 出典キー
8. 未確認で外した規則

## 1. 判断軸

型を選ぶ前に、出す内容を次の5軸で判定する。

| 軸 | 値 | 効き方 |
|---|---|---|
| 重大度 | 情報 / 成功 / 警告 / エラー（データ・機能を失う、作業を続けられない） | 重いほど目立ち、作業を止める型にする。ただし作業を止める型は最後の手段にする（割り込みは作業を妨げ、乱発すると通知を読まなくなる）［Carbon-notifpat］ |
| 持続性 | 解決まで残す / 一時的（読めば済む） | 解決まで残す内容に、自動で消える型を使わない［Atl-flag］［Carbon-notifpat］ |
| 操作が要るか | 不要 / 任意の操作が1つ / 続行に操作が必須 | 操作を伴う通知は、利用者が閉じるまで消さない［Carbon-notifpat］ |
| 対象に紐づくか | 項目 / 領域（区画・ダイアログ・表） / 画面全体・アプリ全体 / どこにも紐づかない | 紐づく対象の近くに出す。近いほど関係が伝わる［Primer-notif］［NNg-errors］ |
| 成功が画面の変化で既に分かるか | 分かる / 分からない | 分かるなら通知を出さない［Primer-notif］［Primer-toast］ |

## 2. 型の一覧

| 型 | 用途 | 使う条件 | 使わない条件 | 出典 |
|---|---|---|---|---|
| toast（画面の隅に一時的に出て消える通知） | 直前の操作の軽い結果 | 見逃しても困らず、結果を示す場所が画面に無いとき | エラー・重大な警告・読む必要がある内容・続行に操作が必須の内容 | ［Carbon-notifpat］［Primer-toast］［Atl-flag］ |
| 項目の近くのメッセージ | 項目・ボタン・行に紐づく結果とエラー | 起点が画面に残っていて、そこに結果を出せるとき | 画面全体に効く問題 | ［Primer-notif］［Carbon-notifpat］ |
| 領域内のメッセージ | 区画・ダイアログ・表に効く結果、続行に操作が要る状態 | 対象の領域が決まっていて、解決するまで見せておくとき | 一過性の軽い報告 | ［Primer-notif］［Carbon-notifpat］ |
| 画面上部のバナー | 画面やアプリ全体に効く重大な状態（データ・機能を失う、障害、全体に効く告知） | 特定の作業に紐づかず、見逃すと困るとき | 常用・同じ画面に複数・入力エラーの代わり | ［Atl-banner］［Primer-banner］［GOVUK-notif］ |
| ダイアログ | 作業を止めて判断・対処させるエラー | 重大で、今すぐ対処しないと主な作業を続けられないとき | 軽い報告・成功の知らせ | ［Carbon-notifpat］［NNg-errors］［Primer-toast］ |
| 通知を出さない | — | 結果が画面の変化で分かるとき（一覧に行が増えた、編集後の値が表示に戻った、作成した対象の画面に移った） | 結果が画面に現れない操作 | ［Primer-notif］［Primer-toast］ |

型ごとの規則:

- toast は消えても困らない結果だけに使う。エラー・重大な警告には使わない（自動で消え、読む時間が足りない人・拡大表示の人・別の作業に移った人が見逃す）［Primer-toast］［Atl-flag］［Carbon-notifpat］
- 操作付きの toast は自動で消さない（操作する前に消える）［Carbon-notif］［Carbon-notifpat］
- 通知に付ける操作は1つに絞る（注意を1つの次の手順に向けるため）［Carbon-notifpat］［Primer-banner］
- 項目の近くのメッセージと領域内のメッセージは、解決するか利用者が閉じるまで残す。読み落とすと困る内容には閉じるボタンを付けない［Carbon-notif］［Carbon-notifpat］
- 領域内のメッセージとバナーで他の内容を覆わない（重ねると下の内容と操作を隠す）［Carbon-notifpat］
- バナーは同じ画面に1つだけ出す。複数あるなら1つにまとめるか、最も優先度の高いものだけを出す（重ねると混乱し、通知に慣れて読まなくなる）［Primer-banner］［Atl-banner］［Carbon-notifpat］［GOVUK-notif］
- バナーは控えめに使う（多用すると見逃されやすくなる）［GOVUK-notif］［Atl-banner］［Primer-banner］
- 利用者が解決できる問題を示すバナーは、解決するまで消さない［Primer-banner］［Atl-banner］
- バナーは関係する内容領域の上端に置く。アプリ全体に効くものはグローバルヘッダーの直下、画面に効くものはページの見出しの上に置く［Carbon-notifpat］［GOVUK-notif］［Primer-notif］
- 作業の前に読ませる注意は、通知にせず、本文の該当箇所の近くに常設する（いま行っている作業に直接関係する情報は本文に置く）［Carbon-notifpat］［GOVUK-notif］
- ダイアログで通知するエラーは同時に1つだけ出す［Carbon-notifpat］
- 決めた型はアプリ内で揃える。同じ種類の結果を、画面ごとに別の型で出さない（同じ働きの部品は同じに見えて同じに動く必要がある）［Primer-toast］［GOVUK-notif］

## 3. 決定表

上の行から順に見て、最初に当てはまった行の型を使う。「—」はその軸を問わない。

| 重大度 | 持続性 | 操作 | 紐づく対象 | 成功が画面で分かるか | 型 |
|---|---|---|---|---|---|
| 成功 | — | 不要 | — | 分かる | 通知を出さない（スクリーンリーダーには状態を伝える）［Primer-notif］［Primer-toast］ |
| エラー（入力の誤り） | 解決まで | 必須 | 項目 | — | 項目の近くのメッセージ。項目が複数あるフォームでは、加えてフォーム上部にエラーサマリ（6節）［GOVUK-errmsg］［GOVUK-errsum］［Primer-notif］ |
| エラー（権限が無い・対象外・サービス側の障害で利用者が直せない） | 解決まで | — | 画面・領域 | — | 項目のエラーにせず、理由と次の手順を示す画面か、エラー由来の空状態（4節）［GOVUK-validation］［GOVUK-errmsg］［Carbon-empty］ |
| — | — | — | ダイアログ内の操作 | — | ダイアログ内の上部に領域内のメッセージ。結果が出るまでダイアログを閉じない［Primer-notif］ |
| エラー（原因が分からない、または主な作業を続けるのに今すぐ知る必要がある）で、利用者の操作が起点 | 解決まで | 必須 | — | — | ダイアログ［Primer-notif］［NNg-errors］［Carbon-notifpat］ |
| エラー・警告（データ・機能を失う、障害、全体に効く） | 解決まで | — | 画面全体・アプリ全体 | — | 画面上部のバナー（1つだけ）［Atl-banner］［Carbon-notifpat］［Primer-notif］ |
| エラー・警告 | 解決まで | 任意または必須 | 領域 | — | 領域内のメッセージ［Primer-notif］［Carbon-notifpat］［Atl-flag］ |
| エラー（操作の失敗） | — | 任意（やり直し） | 項目・ボタン・行 | — | 項目の近くのメッセージ［Primer-notif］［NNg-errors］ |
| 成功 | 一時的 | 不要 | 起点が画面に残る | 分からない | 起点の近くのメッセージ（保存ボタンの近くなど）［Primer-notif］ |
| 成功 | — | 不要 | 別の画面に移り、移った先で成功が分からない | 分からない | 移った先の画面上部のバナー［Primer-notif］［GOVUK-notif］ |
| 成功・情報 | 一時的 | 不要か、取り消しなど任意の操作1つ | どこにも紐づかない（起点が画面から消えた） | 分からない | toast。操作を付けたら自動で消さない［Carbon-notifpat］［Carbon-notif］ |
| 長い処理の進行・完了・失敗 | 完了まで | — | — | — | 進行を示すバナーを出し、完了か失敗の内容に置き換える。画面を離れられる処理なら、アプリの通知一覧など画面の外の経路でも知らせる［Primer-notif］［Primer-toast］［Carbon-loading］ |

## 4. 空状態

### 種類

空になった理由で種類を分け、種類ごとに置く要素を変える。

| 種類 | 何が起きているか | 主操作 |
|---|---|---|
| 初回 | まだ1件も作っていない | 作成を始める操作か、機能への導線［Carbon-empty］［Primer-empty］［Atl-empty］ |
| データ無し | 機能の性質上、いまは空（未読の通知が無い、処理待ちが全部済んだ） | 無くてよい［Carbon-empty］［Primer-empty］［Atl-empty］ |
| 絞り込み・検索の結果0件 | データはあるが条件に合わない | 条件を変える・解除する操作［Carbon-empty］［Atl-empty］ |
| エラー由来 | データはあるが出せない（権限・障害・設定が必要・未対応の操作） | 解決する操作、詳しい情報、助けを求める経路のどれか［Carbon-empty］［Primer-empty］ |

- 初回とデータ無しと0件を同じ表示にしない（理由が違えば、次に取る操作が違う）［Carbon-empty］［Atl-empty］
- エラー由来の空状態を、データ無しの空状態に見せかけない。出せない理由を示す［Carbon-empty］［Primer-empty］

### 構成要素

- 置くのは、空である理由（何が無いか・なぜ無いか）と、次に取る主操作1つ。補足と副次の導線は任意［Carbon-empty］［Primer-empty］［Atl-empty］
- 主操作は1つに絞る。取れる操作が複数あるなら最も重要なものを選び、他は優先度が分かる形で下げる（複数の操作を並べると、どれを押すか迷う）［Carbon-empty］［Primer-empty］［Atl-empty］
- 行き止まりにしない。次に取れる手順があれば必ず置く［Carbon-empty］［Primer-empty］
- 空状態は、本来そこに出る要素と置き換える。空の表なら列見出しと表の下部を出さない（スクリーンリーダーが空の表を読み上げてから空のメッセージに届くのを避ける）［Carbon-empty］
- 空状態はデータが欠けている場所そのもの（ページ・表・タイル・側面パネル）に出す［Carbon-empty］［Atl-empty］
- 1画面に空状態が複数並びうるときは、主操作のボタンを控えめな見た目にし、絵を省いて文字だけにする（主操作が複数並ぶのを避け、繰り返しで目立たなくなるのを避ける）［Carbon-empty］
- 絵は任意で、装飾として扱う。情報を持たない絵には代替テキストを付けない。狭い場所では絵を省く［Atl-empty］［Carbon-empty］
- エラー由来の空状態の絵は、遊びのある絵にしない［Primer-empty］［Carbon-empty］

## 5. 読み込み

### 時間とインジケータ

| 待ち時間 | 出すもの |
|---|---|
| 1秒未満で終わる | 何も出さない（一瞬出て消える表示は、かえって遅く感じさせる）［NNg-progress］［NNg-skeleton］［Primer-loading］ |
| 1秒以上で、進捗を測れない、または3秒未満で終わる | 不確定型（スピナー・スケルトン）［NNg-progress］［Primer-loading］ |
| 3秒以上かかり、進捗を測れる | 確定型（進捗率か、何件目かを示す）［Primer-loading］［NNg-progress］ |
| 進捗を測れず、10秒を超えうる | 処理をバックグラウンドに回して他の操作を止めないか、確定型にする（終わりの見えない回転は、止まったのか動いているのか区別できない）［NNg-progress］［Primer-loading］ |

- 操作を受け付けたことは、待ち時間にかかわらずすぐに見た目で返す（押した状態の表示など。反応が無いと利用者はもう一度押す）［NNg-progress］
- 時間のかかる処理には中止する手段を付ける［NNg-progress］
- 動かない文字だけ（「読み込み中」の表示だけ）で待たせない（止まっても利用者が気付けない）［NNg-progress］
- 待ち時間を見積もれないときは、確定型に切り替える境目を早めに取る（見積もりの振れが大きいほど早める）［NNg-progress］
- 部品に読み込みの状態が組み込まれていれば、独自の表示を作らずにそれを使う［Primer-loading］

### スケルトンとスピナー

- 画面全体の読み込みにはスケルトン、1つの区画・部品の読み込みにはスピナーを使う［NNg-skeleton］
- スケルトンは、カード・表・一覧・タイルのような内容を入れる部品にだけ使う。ボタン・入力欄など操作の部品にはふつう要らない［Carbon-loading］
- toast・メニュー・ドロップダウンの項目・モーダル自体・読み込み表示自体をスケルトンにしない。モーダルの中身はスケルトンにしてよい［Carbon-loading］
- ヘッダーと背景だけの枠のスケルトンにしない（内容の構造を示さず、待たせると壊れていると思われる）［NNg-skeleton］
- アップロード・変換など、ページの読み込み以外の処理にスケルトンを使わない。進捗バーか手順の表示にする［NNg-skeleton］
- 小さな区画で読み込み表示が並ぶときは、1つにまとめる［Primer-loading］

### レイアウトを動かさない

- スケルトンは、読み込まれる内容と同じ形と大きさにする（読み込み後にレイアウトが跳ぶのを防ぐ）［Atl-skeleton］［Vercel-WIG］［Primer-loading］
- 読み込み表示は、代わりに立っている内容のすぐそばに置く。広い領域では領域の中央に置き、画面内に見える位置を保つ［Primer-loading］
- 内容かエラーが用意できたら、すぐに読み込み表示と置き換える［Primer-loading］［Atl-skeleton］

### 読めた分から出す

- 一覧は、全件を待たずに読めた項目から出す。重要なデータから先に読む［Primer-loading］
- 遅い画面（複数の取得元を持つダッシュボード、条件を変えた表）は、骨組み→内容の順に段階的に出す［Carbon-loading］

### 送信ボタン

- 送信ボタンは入力が揃う前から有効にしておく（押せば入力エラーが分かる）［Vercel-WIG］
- 送信が始まったら、送信中は二重送信を止め、ボタンに読み込み表示を出す。ボタンの元のラベルは残す［Vercel-WIG］［Primer-loading］
- 「二度押さないでください」の注意書きで二重送信を防がない。押したことを受け付けた表示で防ぐ［NNg-progress］
- 送信中に入力欄を無効にするのは、送信中の変更が保存されるのか迷わせるときに限る［Primer-loading］

### 読み上げ

- 読み込み表示には、何を読み込んでいるかを示す読み上げ用のラベルを付ける［Primer-loading］
- スケルトンが並ぶときは、読み上げを1回にまとめる［Primer-loading］
- 処理の開始・進行・完了・失敗を、画面の変化で分からない場合は `role="status"` か `aria-live` の領域で伝える。その領域は、読み上げる前から描画しておく［Primer-loading］
- 更新が終わるまでは更新中の領域に `aria-busy="true"` を付け、途中の内容を読み上げさせない［Primer-loading］
- 絞り込みの結果は、件数を読み上げる［Primer-loading］

## 6. エラーの配置

### 項目の直近

- 入力エラーは、その項目の近くに出す。色だけで示さず、文字と、項目の枠などの目印を併用する［NNg-errors］［GOVUK-errmsg］［Vercel-WIG］
- 入力エラーを画面上部のバナーや toast で知らせない［GOVUK-notif］［Primer-toast］
- 項目のエラーに加えてエラーサマリを出すとき、両方に同じ文を出す［GOVUK-errsum］

### 検証のタイミング

- 検証は送信したときに行う。項目からフォーカスが離れた時点で検証しない（入力を試している途中でエラーを出すと、責められたように感じさせる）［GOVUK-validation］［NNg-errors］
- 入力の途中で検証するのは、誤りやすく、先に知らせると手戻りが減る入力（パスワードの条件・文字数の上限など）に限る［NNg-errors］［GOVUK-validation］

### エラーサマリとフォーカス

- 項目が複数あるフォームで送信時にエラーがあれば、フォームの上部（パンくず・戻るリンクの下、見出しの上）にエラーサマリを出し、フォーカスをサマリに移す。エラーが1件でも出す［GOVUK-errsum］［GOVUK-validation］［Primer-notif］
- サマリの各項目は、エラーのある項目へのリンクにする。複数の入力欄からなる項目は、最初の誤りの欄へリンクする［GOVUK-errsum］
- サマリを出さないフォーム（入力欄が1つなど）では、送信時に最初のエラー項目へフォーカスを移す［Vercel-WIG］
- エラーサマリとバナーを同じ画面に出さない。サマリだけを出す［GOVUK-notif］
- エラーのある状態で画面を出し直すときは、ページタイトルの先頭でエラーがあることを示す（スクリーンリーダーが最初に読み上げる）［GOVUK-validation］［GOVUK-errsum］
- 処理が失敗してメッセージを出したら、フォーカスをメッセージ内の最初の操作できる要素に移す［Primer-loading］

### 入力を保持する

- エラーを出しても入力を消さない。誤った値も正しい値も残し、直すだけで済むようにする［GOVUK-errmsg］［GOVUK-validation］［NNg-errors］
- 貼り付けを禁止しない［Vercel-WIG］

### 楽観的な更新

- 成功する見込みが高い操作は、画面を先に更新し、サーバーの応答で合わせる。失敗したら元に戻してエラーを出すか、取り消しを出す［Vercel-WIG］

### `aria-live`

- 非同期の更新（toast・項目の検証結果）は `aria-live="polite"` で読み上げる［Vercel-WIG］
- 割り込んで読み上げる `role="alert"` は、重要なメッセージに限る（作業を中断させ、うるさい）［Atl-banner］
- 操作の失敗は、必ず支援技術に伝える。成功は画面の変化で分からないときに伝える［Primer-toast］［Primer-loading］

## 7. 出典キー

| キー | URL | 原文の確認 | 原文の該当文 |
|---|---|---|---|
| Carbon-notif | https://carbondesignsystem.com/components/notification/usage/ | 確認済み | "If you're using toast-notification style for an actionable notification, the notification should remain on screen until the user dismisses it." |
| Carbon-notifpat | https://carbondesignsystem.com/patterns/notification-pattern/ | 確認済み | "Only send notifications where necessary. Confine each notification to the portion of the interface and workflow it is relevant to." |
| Atl-flag | https://atlassian.design/components/flag/usage | 確認済み | "Never use auto dismiss flags for any critical warning or error messages, or anything else where it's important that people don't miss the message." |
| Atl-banner | https://atlassian.design/components/banner/usage | 確認済み | "Banners should appear one at a time, are not dismissible, and only disappear when no longer required." |
| Primer-banner | https://primer.style/product/components/banner/guidelines/ | 確認済み | "Do not display more than one banner (full-width or otherwise) on a single page at the same time." |
| Primer-notif | https://primer.style/product/ui-patterns/notification-messaging/ | 確認済み | "Prioritize showing messaging inside the Dialog after an action rather than closing the Dialog and showing a Banner on the page." |
| Primer-toast | https://primer.style/accessibility/toasts | 確認済み | "Toasts pose significant accessibility concerns and are not recommended for use." |
| GOVUK-notif | https://design-system.service.gov.uk/components/notification-banner/ | 確認済み | "Use notification banners sparingly. There's evidence that people often miss them, and using them too often is likely to make this problem worse." |
| Carbon-empty | https://carbondesignsystem.com/patterns/empty-states-pattern/ | 確認済み | "Empty states should replace the element that would ordinarily show." |
| Primer-empty | https://primer.style/product/ui-patterns/empty-states/ | 確認済み | "Blankslates can and are encouraged to use one primary link or action." |
| Atl-empty | https://atlassian.design/components/empty-state/usage | 確認済み | "Consider all scenarios that could cause the empty state to occur, and use that to inform the tone of your writing" |
| NNg-progress | https://www.nngroup.com/articles/progress-indicators/ | 確認済み | "The main guideline is to use a looped indicator for delays of 2–9 seconds and a percent-done indicator for delays of 10 seconds or more." |
| NNg-skeleton | https://www.nngroup.com/articles/skeleton-screens/ | 確認済み | "Spinners are typically best used on a single module, like a video or a card which is on a dashboard." |
| Primer-loading | https://primer.style/product/ui-patterns/loading/ | 確認済み | "Less than 1 second: Don't show a loading state." |
| Carbon-loading | https://carbondesignsystem.com/patterns/loading-pattern/ | 確認済み | "Never represent toast notifications, overflow menus, dropdown items, modals, and loaders with skeleton states." |
| Atl-skeleton | https://atlassian.design/components/skeleton/usage | 確認済み | "Match the size and shape of the expected content so the page does not jump when loading completes." |
| GOVUK-errsum | https://design-system.service.gov.uk/components/error-summary/ | 確認済み | "Always show an error summary when there is a validation error, even if there's only one." |
| GOVUK-validation | https://design-system.service.gov.uk/patterns/validation/ | 確認済み | "Do not validate when the user moves away from a field." |
| GOVUK-errmsg | https://design-system.service.gov.uk/components/error-message/ | 確認済み | "Do not clear any form fields when showing the Error message component." |
| NNg-errors | https://www.nngroup.com/articles/error-message-guidelines/ | 確認済み | "Display the error message close to the error's source." |
| Vercel-WIG | https://github.com/vercel-labs/web-interface-guidelines | 確認済み（README.md を raw で取得） | "Keep submit enabled until submission starts; then disable during the in-flight request, show a spinner, & include an idempotency key." |

## 8. 未確認で外した規則

| 規則（調査時の要約の記述） | 外した理由 |
|---|---|
| toast は同時に1つ | 原文に無い。Carbon は toast を縦に積む（"Multiple toasts stack vertically"）、Atlassian も flag を積む前提で書いており、むしろ食い違う |
| toast の操作は undo / retry 1つまで | 「1つ」は Carbon の actionable notification の規則で、toast 固有ではない。Atlassian flag は "A maximum of two links"。本文では通知全般の「操作は1つに絞る」として入れ、toast 固有の数としては入れない |
| 解決できない告知のバナーは閉じられる | Primer は "This should be used for Banners that inform about something that the user can not solve." と書くが、Atlassian は "Banners ... are not dismissible" で食い違う。1出典かつ他と矛盾するので外した。本文には両者が一致する「解決できる問題は解決まで残す」だけを入れた |
| M3 snackbar の表示秒数（4〜10秒） | m3.material.io の本文を取得できず、原文を確認していない |
| toast を5秒で自動で消す（Carbon） | 原文にはあるが1出典の数値で、他の出典と一致を確認できない。秒数はスキルに持たない |
| スピナー・スケルトンの表示遅延（約150〜300ms）と最小表示時間（約300〜500ms）（Vercel） | 原文にはあるが1出典の ms の数値で、sources.md の採否（ms を持たない）に合わない。本文には「1秒未満は出さない」だけを入れた |
| 成功の置き場所は、SPA では toast 系 | 出典に文言が無い。本文の決定表は Primer の流れ図（起点の近く・移った先のバナー）に従った |
| 補足文と副次の導線の置き方（図・主文・補足・主操作・副操作リンクの順） | 要素の構成は Carbon・Primer・Atlassian で確認したが、並び順と見た目は部品の領域なので本文に入れなかった |
