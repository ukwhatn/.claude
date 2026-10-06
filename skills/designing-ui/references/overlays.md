# 重ね方（オーバーレイ）の選び方

画面の上に何かを重ねるか、ページを移るか、その場で広げるかを選ぶための判断表。確認ダイアログの文言（タイトル・ボタン名・本文）は `/writing-ui-text` の「7. 確認ダイアログ」が扱う。操作結果の通知（toast・banner）は 通知の参照 が扱う。

## 目次

1. 判断軸
2. 型の一覧
3. 決定表
4. 横断原則
5. フォーカス・キーボード・a11y
6. 出典キー
7. 未確認で外した規則

## 1. 判断軸

型を選ぶ前に、次の6つを決める。決定表はこの値で引く。

| 軸 | 取りうる値 | 効く理由 |
|---|---|---|
| 内容の量・作業の長さ | 一言 / 少量の情報と数個の操作 / 短い単一作業 / 長い・多段・大きな表 | 重ねる型は狭く、長い作業を入れると元の文脈を見失う［NNg-modal］［HIG-modality］ |
| 元の画面を見ながら操作するか | 見ない / 見るだけ / 見ながら操作もする | モーダルは背景を隠して操作を止める。背景を参照する作業を入れられない［NNg-modal］［ATL-drawer］ |
| URLで共有・再訪したいか | したい / しない | 重ねた面をURLで開くと、どの画面の上か分かりにくい［Primer-dialog］［Vercel-WIG］ |
| 破壊的か・元に戻せるか | 破壊的でない / 破壊的だが戻せる / 破壊的で戻せない | 戻せる操作に確認を挟むと、確認が習慣で押されるようになる［NNg-confirm］［HIG-alerts］ |
| 中断してよいか | 今の作業を止めてでも答えが要る / 後でよい / 無視してよい | 作業を止める型は、止める価値があるときだけ使う［NNg-modal］［Carbon-modal］ |
| 画面幅 | 広い / 狭い | 起点の横に浮かべる型は狭い幅で使えない［HIG-popovers］［Primer-dialog］。区切りの値はPJ・CSSフレームワークのものを使う |

## 2. 型の一覧

### ページ遷移

- 用途: 長い作業・多段の手順・大きなフォーム・大きな表・URLで共有する内容［NNg-modal］［Carbon-modal］［Primer-dialog］
- 使う: 手順が複数段に分かれる作業はページにする（段の多いモーダルは元の作業から離れる時間を延ばす）［NNg-modal］［Carbon-modal］
- 使う: ダイアログの中にサイドナビゲーションが要る機能は、ページにする［Primer-dialog］
- 使う: 繰り返し行う作業は、モーダルに出さず元の画面で完了できるようにする［Carbon-modal］
- 使う: リンクで直接開かれたい内容は、ダイアログでなくページか画面内に置く（背景が暗くなり、どの文脈か分からなくなる）［Primer-dialog］

### モーダルダイアログ

- 用途: 続行に必須の短い入力、単一の短い作業、作業の喪失や重大なエラーの警告［NNg-modal］［ATL-modal］［Carbon-modal］
- **控えめに使う**（作業を中断させ、閉じるという余計な目的を増やす）［M3-dialog］［HIG-modality］［Carbon-modal］
- 使わない: 複雑な操作・大きな表・中で画面遷移する手順［ATL-modal］
- 使わない: 判断に要る情報がモーダルの外（隠れた背景や別の画面）にある作業［NNg-modal］［ATL-modal］
- 使わない: 今の作業に関係しない情報・宣伝［NNg-modal］
- 使わない: 購入・送信など中断されると困る手順の途中に割り込ませる［NNg-modal］
- 中身は1カラムにし、ページ1枚分をダイアログに入れない［Primer-dialog］
- 中の項目は作業に要るものだけにする［ATL-modal］［Carbon-modal］
- 入力エラーがあればモーダルを開いたまま、項目の近くにエラーを出す［Carbon-modal］
- 狭い幅では、下から出るシートか全画面にする。入力欄を含むダイアログは全画面にする［Primer-dialog］

### 確認（alert）ダイアログ

- 用途: まれで、元に戻せない破壊的な操作の直前［HIG-alerts］［NNg-confirm］［Carbon-modal］
- **よくある操作・元に戻せる操作には出さない。破壊的でも戻せるならundoを用意して確認を省く**（毎回出すと内容を読まずに押されるようになる）［HIG-alerts］［NNg-confirm］［Vercel-WIG］
- 使わない: 情報を伝えるだけで、利用者が取る操作が無いとき。関連する場所に表示する［HIG-alerts］
- 使わない: アプリを開いた直後［HIG-alerts］
- 初期フォーカスは最も破壊的でない操作に置き、破壊的な操作を既定の答え（Enterで押されるボタン）にしない［APG-dialog］［NNg-confirm］
- 特に危険でまれな操作は、ボタンを押すだけでなく対象名の入力など普段しない操作を求める。多用すると効果が消えるので限る［NNg-confirm］
- 意図して始めた操作に付随する選択肢（破棄・保存・編集に戻る）を出すときは、警告でなく選択肢の一覧として出す［HIG-action-sheets］
- 文言は `/writing-ui-text` の「7. 確認ダイアログ」に従う

### 側面パネル（非モーダル）

- 用途: 元の画面を見ながら・操作しながら使う詳細・フィルタ・プレビュー［M3-side-sheet］［HIG-sheets］［ATL-drawer］
- 開いている間も背景を操作できるようにする（背景と同時に見て操作するための型）［M3-side-sheet］
- 作成・編集の長いフォームや情報量の多い手順は入れず、ページにする［Primer-dialog］

### 側面パネル（モーダル）

- 中央のモーダルダイアログと同じ条件で使い、同じく控えめにする［ATL-drawer］［Primer-dialog］
- 背景を参照しながら進める作業を入れない（背景は操作もフォーカスもできない）［ATL-drawer］
- 作成・編集のフォームや情報量の多い手順は入れず、ページにする［Primer-dialog］
- 画面全体に近い幅にしない（モーダルの中にいると気付きにくくなる）［ATL-drawer］

### 下から出るシート

- 標準（非モーダル）: 主画面と同時に見て操作する補助の内容に使う［M3-bottom-sheet］［HIG-sheets］
- モーダル: 狭い幅で、メニューや簡単なダイアログの代わりに使う［M3-bottom-sheet］［Primer-dialog］
- 長い作業・複雑な手順には使わず、全画面かページにする［HIG-sheets］
- 1つのシートから別のシートを開かない。開くなら先に閉じる［HIG-sheets］
- 下へのドラッグで閉じられるようにする。未保存の変更があれば閉じる前に確認する［HIG-sheets］［M3-bottom-sheet］

### ポップオーバー

- 用途: 起点に紐づく少量の情報と、数個の関連操作［HIG-popovers］［Carbon-popover］
- クリックかEnterで開き、外側のクリックかEscで閉じる［ATL-popup］［Carbon-popover］［HIG-popovers］
- 使わない: 警告（見落とされる、誤って閉じられる）。確認ダイアログを使う［HIG-popovers］
- 使わない: 必須の入力欄（外側のクリックで閉じて入力が消える）［ATL-popup］
- 使わない: スクロールが要る量の内容。モーダルかページにする［ATL-popup］
- 小さな作業を完了させる用途ならモーダルダイアログにする［ATL-popup］
- 起点の要素と、使う間に見る必要がある内容を覆わない位置に出す［HIG-popovers］
- 狭い幅では使わず、下から出るシートか全画面にする［HIG-popovers］
- 外側のクリックで自動で閉じるときも入力は保存し、破棄するのは明示のキャンセルだけにする［HIG-popovers］

### メニュー（ドロップダウン・コンテキスト）

- 用途: 起点に紐づく操作・選択肢の一覧。ボタンから開くものがドロップダウン、対象の右クリック・長押しで開くものがコンテキストメニュー［APG-menubutton］［HIG-menus］［HIG-context-menus］
- よく使う項目を先頭に置き、関連する項目を区切り線でまとめる［HIG-menus］
- サブメニューは控えめにし、1段までにする［HIG-menus］［HIG-context-menus］
- コンテキストメニューの項目は、画面上の別の場所（ツールバー・ドロップダウン）からも実行できるようにする（隠れていて気付かれない）［HIG-context-menus］
- コンテキストメニューは、今の対象に関係する項目だけを出し、使えない項目は隠す［HIG-context-menus］
- 破壊的な項目はメニューの末尾に置き、破壊的だと分かる見た目にする［HIG-context-menus］
- 意図した操作に付随する確認の選択肢をメニューで出さない（メニューは利用者が開くときに出るもの）［HIG-action-sheets］

### ツールチップ

- 用途: アイコンだけのボタンの名前、操作要素の短い補足、省略された文字列の全文、キーボードショートカット［ATL-tooltip］［Carbon-tooltip］［NNg-tooltip］
- **作業の完了に必須の情報（入力の条件・警告）を入れない**（消えるので覚えておく必要があり、タッチ端末では出せない）［NNg-tooltip］［ATL-tooltip］［Carbon-tooltip］
- 中にリンク・ボタンなど操作できる要素を置かない。必要ならポップオーバーにする［ATL-tooltip］［Carbon-tooltip］［APG-tooltip］
- 画面に見えているラベルと同じ内容を出さない［NNg-tooltip］［ATL-tooltip］
- 操作できる要素にだけ付ける。無効化した要素に付けない（フォーカスできず出せない）［ATL-tooltip］
- マウスのホバーとキーボードのフォーカスの両方で出す［NNg-tooltip］［APG-tooltip］［Carbon-tooltip］
- 関連する内容を覆わない位置に出す［NNg-tooltip］［Carbon-tooltip］
- 付けるなら同種の要素すべてに付ける（一部だけだと存在に気付かれない）［NNg-tooltip］

### ホバーカード

- 用途: リンクや対象の上にホバーかフォーカスで出す、操作できる要素を含む補足の面。ツールチップでなく非モーダルのダイアログとして作る［APG-tooltip］
- ホバーで出す内容は、ポインタを動かさずに閉じられ、ポインタを内容の上へ動かしても消えず、利用者が離れるか閉じるまで出し続ける［WCAG-1.4.13］
- ホバーでしか出ない経路にしない。タッチ端末にはホバーが無い［NNg-tooltip］

### その場の展開（disclosure・accordion）

- 用途: 一部の人だけが読む補足・詳細設定を、同じ画面のまま隠しておく［HIG-disclosure］［NNg-accordion］
- 控えめに使う（隠した内容は見落とされ、開く手間が増える）［Primer-disclosure］［NNg-accordion］
- 利用者が内容の大半を読む画面では折りたたまず、全部を出す［NNg-accordion］［NNg-accordion-complex］
- 独立した複数の節から一部だけを読む画面（よくある質問など）と、狭い幅の長い画面ではaccordionにする［NNg-accordion］
- 複数の節を同時に開けるようにし、開閉の状態は利用者が変えるまで保つ［NNg-accordion-complex］
- 開閉の操作には、何が出てくるか分かるラベルを付け、出てくる内容の近くに置く［HIG-disclosure］
- 開いたときに利用者の注目位置が大きく動かないようにする［Primer-disclosure］

## 3. 決定表

上の行から順に見て、最初に当てはまった行の型を使う。

| 内容・作業 | 元の画面 | その他の条件 | 型 |
|---|---|---|---|
| どれでも | どれでも | URLで共有・再訪したい | ページ |
| 長い・多段・大きな表・中でナビゲーションが要る | どれでも | — | ページ |
| 繰り返し行う作業 | どれでも | — | 元の画面に組み込む |
| 破壊的で戻せない操作の直前 | 見ない | まれな操作 | 確認ダイアログ |
| 破壊的だが戻せる操作 | どれでも | — | 確認せず実行し、undoを出す（通知の型は 通知の参照） |
| 作業の喪失・重大なエラーの警告 | 見ない | 今止めてでも答えが要る | モーダルダイアログ |
| 詳細・フィルタ・プレビュー | 見ながら操作もする | 広い幅 | 非モーダルの側面パネル |
| 補助の内容 | 見ながら操作もする | 狭い幅 | 標準（非モーダル）の下から出るシート |
| 続行に必須の短い入力・短い単一作業 | 見ない | 広い幅 | モーダルダイアログ |
| 続行に必須の短い入力・短い単一作業 | 見ない | 狭い幅 | 下から出るシート（入力欄があれば全画面） |
| 少量の情報＋数個の関連操作（必須入力・警告を含まない） | 見るだけ | 広い幅 | ポップオーバー |
| 少量の情報＋数個の関連操作 | 見るだけ | 狭い幅 | 下から出るシート |
| 起点に紐づく操作・選択肢の一覧 | 見るだけ | ボタンから開く | ドロップダウンメニュー |
| 選択した対象への操作の一覧 | 見るだけ | 対象から直接開く。項目は画面上にも置く | コンテキストメニュー |
| 操作要素の名前・短い補足（無くても作業を完了できる） | 見るだけ | 中に操作要素が無い | ツールチップ |
| 対象の補足で、中に操作要素がある | 見るだけ | ホバーかフォーカスで出す | ホバーカード（非モーダルのダイアログ） |
| 一部の人だけが読む補足・詳細 | 同じ画面のまま | 大半の人は読まない | その場の展開 |
| 作業に必須の情報・警告 | 同じ画面のまま | — | 重ねずに画面に常に出す |

## 4. 横断原則

- **確認よりundoを優先する。確認ダイアログは戻せない操作に限る**［NNg-confirm］［HIG-alerts］［Vercel-WIG］
- **モーダルの上に別のモーダルを開かない。モーダル内の操作で別のモーダルが要るなら、先に閉じてから開く**（どこに戻るか分からなくなる）［ATL-modal］［HIG-modality］［HIG-sheets］
  - 例外は、閉じると作業が失われるときの確認ダイアログ1枚だけ。モーダルの上に重ねてよいが、確認の上にさらに重ねない［HIG-modality］［HIG-sheets］
- ポップオーバーを入れ子にしない。ポップオーバーから別のポップオーバーを出さない［HIG-popovers］［Carbon-popover］［ATL-popup］
- **同じ種類の重なりを同時に複数出さない**（モーダル・シート・ポップオーバー・確認ダイアログ）［HIG-modality］［HIG-sheets］［HIG-popovers］［Carbon-popover］［ATL-modal］
- **モーダル・シート・側面パネルには、何の作業かを示すタイトルを付ける**。見た目に出さない場合も読み上げ用の名前は付ける［APG-dialog］［ATL-modal］［ATL-drawer］［Primer-dialog］［HIG-modality］
- **閉じると利用者の入力が失われるときは、閉じる前に確認する**。閉じる手段（ボタン・スワイプ・Esc・背景のクリック）を問わない［HIG-modality］［HIG-sheets］
- 未保存の入力を持ちうるダイアログは、背景のクリックで閉じない［Primer-dialog］
- 閉じる手段を複数用意し、見える閉じるボタン（×かキャンセル）を必ず置く［APG-dialog］［ATL-modal］［HIG-modality］
- **ツールチップ・ポップオーバーに必須の情報・警告を入れない**。必須の情報は画面に常に出す［NNg-tooltip］［ATL-tooltip］［Carbon-tooltip］［HIG-popovers］
- 同じ目的の重なりには、アプリ全体で同じ型を使う（一部の画面だけにあると存在に気付かれない）［NNg-tooltip］［HIG-context-menus］

## 5. フォーカス・キーボード・a11y

### モーダルダイアログ［APG-dialog］

- 開いたらフォーカスをダイアログの中へ移す。既定は最初の操作要素
- 中身が長い・表や段落など構造を持つときは、先頭の静的要素（タイトル等）に `tabindex="-1"` を付けてそこへフォーカスする
- 戻しにくい操作の最終段では、最も破壊的でない操作に初期フォーカスを置く
- Tab / Shift+Tab はダイアログ内で循環させ、外へ出さない
- Escで閉じる
- 閉じたらフォーカスを開いた要素へ戻す。その要素が消えていれば、作業の流れで次に来る要素へ移す
- `role="dialog"` を付け、見えるタイトルを `aria-labelledby` で指す（見えるタイトルが無いときだけ `aria-label`）
- 説明が単純な文のときだけ `aria-describedby` を付ける。表・リスト・複数段落を含むなら付けない
- `aria-modal="true"` は、外側を実際に操作不能にし、見た目でも覆っているときだけ付ける（付けたのに外を操作できると、支援技術の利用者だけ外が見えなくなる）

### 確認（alert）ダイアログ［APG-alertdialog］

- `role="alertdialog"` を付ける。キーボード操作はモーダルダイアログと同じ
- 確認の本文を `aria-describedby` で必ず指す

### ツールチップ［APG-tooltip］［WCAG-1.4.13］

- フォーカスかホバーで出し、Escで消す。フォーカスは起点の要素に残す
- フォーカスで出したものはフォーカスが外れたら消す。ホバーで出したものは、ポインタが起点かツールチップの上にある間は出し続ける
- `role="tooltip"` を付け、起点の要素から `aria-describedby` で指す
- ツールチップ自体はフォーカスを受けない
- APGのtooltipパターンは作業中（task force の合意前）なので、WCAG 1.4.13 の3条件（ポインタを動かさずに閉じられる・内容の上にポインタを動かせる・離れるまで出し続ける）を満たすことを確かめる

### その場の展開［APG-disclosure］［APG-accordion］

- 開閉する要素は `role="button"`（`<button>`）にし、Enter と Space で開閉する
- 開いていれば `aria-expanded="true"`、閉じていれば `false`。任意で `aria-controls` で中身を指す
- accordion の見出しの間は Tab で移る（中の操作要素もページのTab順に入る）
- 閉じた中身は、見た目だけでなく操作上も届かないようにする［NNg-accordion］

### メニューボタン・メニュー［APG-menubutton］［APG-menu］

- 開くボタンに `aria-haspopup="menu"`（または `true`）、開閉に合わせて `aria-expanded` を付ける。中身は `role="menu"`
- Enter / Space で開いて最初の項目へフォーカスする。下矢印で最初、上矢印で最後の項目へ開いてもよい
- メニュー内は上下矢印で移動し、Tab では項目間を移らない。Tab はメニューを閉じて外へ出る
- Escでメニューを閉じ、開いた要素へフォーカスを戻す
- Enter で項目を実行してメニューを閉じる

### ポップオーバー

- 中に操作要素があるポップオーバーは、名前を持つダイアログとして作る［ATL-popup］［APG-tooltip］
- Enter で開き、Esc で閉じる［ATL-popup］［Carbon-popover］

## 6. 出典キー

| キー | URL | 原文確認 | 原文の該当文 |
|---|---|---|---|
| APG-dialog | https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ | 確認済み | If a dialog contains the final step in a process that is not easily reversible, such as deleting data or completing a financial transaction, it may be advisable to set focus on the least destructive action |
| APG-alertdialog | https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/ | 確認済み | The element with role alertdialog has a value set for aria-describedby that refers to the element containing the alert message. |
| APG-tooltip | https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/ | 確認済み | A hover that contains focusable elements can be made using a non-modal dialog. |
| APG-disclosure | https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ | 確認済み | When the content is visible, the element with role button has aria-expanded set to true. |
| APG-accordion | https://www.w3.org/WAI/ARIA/apg/patterns/accordion/ | 確認済み | Tab: Moves focus to the next focusable element; all focusable elements in the accordion are included in the page Tab sequence. |
| APG-menubutton | https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/ | 確認済み | The element with role button has aria-haspopup set to either menu or true. |
| APG-menu | https://www.w3.org/WAI/ARIA/apg/patterns/menubar/ | 確認済み | Escape: Close the menu that contains focus and return focus to the element or context, e.g., menu button or parent menuitem, from which the menu was opened. |
| WCAG-1.4.13 | https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html | 確認済み | If pointer hover can trigger the additional content, then the pointer can be moved over the additional content without the additional content disappearing |
| NNg-modal | https://www.nngroup.com/articles/modal-nonmodal-dialog/ | 確認済み | Avoid modal dialogs for complex decision making that requires additional sources of information unavailable in the modal. |
| NNg-confirm | https://www.nngroup.com/articles/confirmation-dialog/ | 確認済み | Do not use confirmation dialogs for routine actions. |
| NNg-tooltip | https://www.nngroup.com/articles/tooltip-guidelines/ | 確認済み | Don't use tooltips for information that is vital to task completion. |
| NNg-accordion | https://www.nngroup.com/articles/accordions-on-desktop/ | 確認済み | If you expect users to need information from several accordions at once, it is better to display all the content at once (even if it results in a longer page). |
| NNg-accordion-complex | https://www.nngroup.com/articles/accordions-complex-content/ | 確認済み | If you do use accordions, make sure to give people the capability to open multiple sections at a time so that different chunks of content are readily available. |
| Primer-dialog | https://primer.style/product/components/dialog/guidelines/ | 確認済み | Don't use side sheets to present create/edit forms, or flows that may contain a lot of information. For that, use a page instead. |
| Primer-disclosure | https://primer.style/product/ui-patterns/progressive-disclosure/ | 確認済み | They should be used sparingly, only when it's necessary to truncate information. |
| ATL-modal | https://atlassian.design/components/modal-dialog/usage | 確認済み | Don't use dialogs to trigger other dialogs, as this is inaccessible and confusing. |
| ATL-drawer | https://atlassian.design/components/drawer/usage | 確認済み | Unless there are significant benefits to interrupting a task with a drawer modal, we recommend choosing a new page experience or non-modal dialog instead. |
| ATL-popup | https://atlassian.design/components/popup/usage | 確認済み | Avoid putting required fields inside popups in case the popup is dismissed on click. |
| ATL-tooltip | https://atlassian.design/components/tooltip/usage | 確認済み | Never use tooltips on disabled buttons, as these are not interactive. |
| Carbon-modal | https://carbondesignsystem.com/components/modal/usage/ | 確認済み | Therefore, if a user needs to repeatably perform a task, consider making the task completable on the main page. |
| Carbon-popover | https://carbondesignsystem.com/components/popover/usage/ | 確認済み | Avoid nesting popovers or placing popovers within other popovers. |
| Carbon-tooltip | https://carbondesignsystem.com/components/tooltip/usage/ | 確認済み | Since a tooltip disappears when a user hovers away, do not include pertinent information for the user to complete their task. |
| HIG-modality | https://developer.apple.com/design/human-interface-guidelines/modality | 確認済み（JSON） | Although an alert can appear on top of all other content — including other modal views — you never want to display more than one alert at the same time. |
| HIG-alerts | https://developer.apple.com/design/human-interface-guidelines/alerts | 確認済み（JSON） | Avoid displaying alerts for common, undoable actions, even when they're destructive. |
| HIG-sheets | https://developer.apple.com/design/human-interface-guidelines/sheets | 確認済み（JSON） | If people have unsaved changes in the sheet when they begin swiping to dismiss it, use an action sheet to let them confirm their action. |
| HIG-popovers | https://developer.apple.com/design/human-interface-guidelines/popovers | 確認済み（JSON） | Avoid using a popover to show a warning. |
| HIG-action-sheets | https://developer.apple.com/design/human-interface-guidelines/action-sheets | 確認済み（JSON） | Use an action sheet — not a menu — to provide choices related to an action. |
| HIG-menus | https://developer.apple.com/design/human-interface-guidelines/menus | 確認済み（JSON） | It can be difficult for people to reveal multiple levels of hierarchical submenus, so it's generally best to restrict them to a single level. |
| HIG-context-menus | https://developer.apple.com/design/human-interface-guidelines/context-menus | 確認済み（JSON） | Always make context menu items available in the main interface, too. |
| HIG-disclosure | https://developer.apple.com/design/human-interface-guidelines/disclosure-controls | 確認済み（JSON） | Place a disclosure button near the content that it shows and hides. |
| M3-dialog | https://github.com/material-components/material-components-android/blob/master/docs/components/Dialog.md | 確認済み | Dialogs are purposefully interruptive, so they should be used sparingly. |
| M3-bottom-sheet | https://github.com/material-components/material-components-android/blob/master/docs/components/BottomSheet.md | 確認済み | They are an alternative to inline menus and simple dialogs on mobile devices, providing additional room for content, iconography, and actions. |
| M3-side-sheet | https://github.com/material-components/material-components-android/blob/master/docs/components/SideSheet.md | 確認済み | Standard side sheets co-exist with the screen's main UI region and allow for simultaneously viewing and interacting with both regions. |
| Vercel-WIG | https://github.com/vercel-labs/web-interface-guidelines | 確認済み | Confirm destructive actions. Require confirmation or provide Undo with a safe window. |

HIG は `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<slug>.json` を取得して読んだ。

### 出典間の食い違いと採否

| 論点 | 食い違い | 採った規則 |
|---|---|---|
| モーダルの入れ子 | Primer は2段まで許容 / Atlassian・HIG（モーダル・シート）は禁止。Carbon は modal の入れ子に明文なし（ポップオーバーの入れ子は禁止）。HIG は alert だけ他のモーダルの上に出してよいとする | 原則禁止。例外は閉じると作業が失われるときの確認ダイアログ1枚だけ（HIG modality・HIG sheets に従う）。Atlassian の例外なしの禁止は不採用 |
| 側面パネルのモーダル性 | Primer は side sheet を常にモーダルとし「背景と操作できる side sheet は避ける」/ M3 標準 side sheet・HIG の非モーダル sheet・Atlassian（非モーダルのダイアログを推奨）は背景と同時に操作する型を持つ | 元の画面を見ながら使う詳細・フィルタは非モーダルの側面パネル（sources.md の採否どおり）。Primer は不採用 |
| Atlassian drawer | 非推奨化を予告し、modal を使えとする | モーダルの側面パネルは中央のモーダルと同じ条件に限り、控えめにする |

## 7. 未確認で外した規則

| 規則案 | 外した理由 |
|---|---|
| Carbon side panel の使い分け | 出典ページが404で原文を開けなかった |
| GOV.UK はモーダル・drawer・ツールチップを部品に持たない（使わない方針） | 部品一覧に無いことは確認できるが、使わない方針の明文を確認できなかった |
| モーダルを開いている間は背景のスクロールを止める | どの出典にも明文が無かった（Vercel は `overscroll-behavior: contain` を挙げるのみ） |
| ホバーカードの使いどころ（リンク先の先読みに限る等） | 用途を定める一次出典が見つからなかった。本文はa11yの条件と操作要素の扱いだけにした |
| ポップオーバーの幅の上限（Carbon「4カラムまで」） | 確認済みだが、Carbon のグリッドに依存する数値で他の出典に無い。画面寸法の数値を持たないsources.md の採否に合わせて外した |
| 確認ダイアログのボタン数の上限（HIG alert 3つまで、action sheet 4つまで）、サブメニューの項目数（HIG 約5） | 確認済みだが HIG 単独の数値で、他の出典に対応する値が無い |
| 狭い幅で中央のダイアログを下から出るシートに替える区切りの値 | 区切りの値はスキルに持たない（sources.md の採否） |
| 確認ダイアログに既定ボタンを一切置かない（NN/g「既定の答えを持たない方が良い」、HIG「読ませたいなら既定ボタンを置かない」） | HIG は利用者が意図して選んだ破壊的操作（ゴミ箱を空にする等）の確認では Return で確定できる既定ボタンを認めており、一律の禁止とは食い違う。本文は「破壊的な操作を既定にしない」までに留めた |
| シートをアプリ内の移動に使わない（HIG） | 確認済みだが watchOS の節にだけある規則で、Web に一般化できるか判断できなかった |
| 追加の入力が要るメニュー項目の末尾に「…」を付ける（HIG） | 確認済みだが項目の文言の規則なので writing-ui-text の領域として外した |
