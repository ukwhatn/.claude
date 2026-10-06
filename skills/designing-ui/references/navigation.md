# ナビゲーション

アプリの中で利用者が「どこへ行くか」「何を切り替えるか」の型を選ぶための参照。文言（ラベル・項目名）は `/writing-ui-text`、外枠の寸法と畳み方の全体は 外枠とトークンの参照、重ねて開く面は 重ね方の参照 が扱う。

## 目次

1. 判断軸
2. グローバルナビの型
3. ローカルナビの型
4. 位置と移動の補助
5. 決定表
6. 一貫性の原則
7. URL・キーボード・a11y
8. 出典キー
9. 未確認で外した規則

## 1. 判断軸

上から順に決める。先の軸の答えで、後の軸の候補が絞られる。

1. **目的地の集合か、作業中の集合か**
   - 目的地: アプリが固定で持つ行き先（設定・一覧・ダッシュボード）。項目は開発者が決め、利用者は増減させない。階層として縦に並べ、常時見せなくてよい（畳んでも項目と順序は変わらない）［MS-navview］［MS-tabview］［HIG-sidebars］
   - 作業中の集合: 利用者が開いて切り替えている対象（開いたドキュメント・スレッド・レコード）。利用者が開く・閉じる・並べ替える。横に並べて常時見せ、各項目にアイコン・色・状態（未保存・実行中）を付ける。作業中の集合を見せている間は、目的地のサイドバーを畳んで本文やプレビューに幅を回してよい［MS-tabview］［HIG-sidebars］
   - 2つを1つの部品に混ぜない。目的地を作業中の横タブに並べず、開いた対象を目的地のサイドバーに足さない（項目が固定か可変かで、閉じる・並べ替えの操作の有無が変わるから）［MS-tabview］
2. **アプリ全体の行き先か、1つの画面の中の切り替えか**: 全体ならグローバルナビ（2節）、画面の中ならローカルナビ（3節）
3. **階層かフラットか、何段か**: 2段までならサイドバーの中で開閉する。3段目は画面の中に置く（2節「サイドバー」）
4. **項目数と増える見込み**: 少数で増えないなら横、多い・増えるなら縦［NNg-vertical］［MS-navview］
5. **同時に見比べるか**: 見比べるならタブやセグメントで隠さず、並べて見せる［NNg-tabs］［GOVUK-tabs］［Carbon-tabs］
6. **URLが変わるか**: 共有・再読込・戻るで復元したい状態はURLに載せる（7節）。URLが変わる切り替えと変わらない切り替えを1列に混ぜない［Primer-nav］
7. **画面幅**: 狭い幅での畳み方を型ごとに決める。区切りの数値はPJ・CSSフレームワークの値を使い、本ファイルでは持たない

## 2. グローバルナビの型

アプリの主な行き先を、どの画面からでも同じ位置に出す。1つのアプリでは下の型のうち1つ（狭い幅と広い幅で1組）だけを使う。

### ボトムタブ（狭い幅）

- 主な行き先の切り替えに使う。現在の画面への操作（作成・共有）を置かない（操作はツールバーに置く）［HIG-tabbars］
- **項目は5以下にする**（狭い幅で全部が見え、ラベルが付けられる数）［MCA-navbar］［HIG-tabbars］
- 全画面で表示し続ける。例外は一時的なモーダルが覆うときだけ（隠すと今どこにいるかを見失うから）［HIG-tabbars］
- 中身が無い項目も無効化・非表示にしない。空である理由をその画面で示す（項目が出たり消えたりすると不安定に見えるから）［HIG-tabbars］［GOVUK-tabs］
- 溢れた項目を「その他」タブにまとめない。収まらないなら型をサイドバーに変える（隠れた項目は見つけにくいから）［HIG-tabbars］［NNg-tabs］
- 各項目にアイコンとラベルを付ける［MCA-navbar］［HIG-tabbars］

### レール（中くらいの幅）

- サイドバーをアイコン幅に畳んだもの。広い幅の展開したサイドバーと同じ項目・同じ順序にして切り替える（展開したレールがドロワーを置き換える方針）［MCA-rail］［MCA-drawer］［MS-navview］
- アイコンだけの表示にするのは、毎日使う業務アプリに限る。たまに使うサイトではラベルを隠さない（アイコンだけでは意味が伝わらず、ナビ自体が使われなくなるから）［NNg-vertical］
- アイコンだけの項目にはアクセシブルな名前を付ける（7節）

### サイドバー（広い幅の縦ナビ）

- 項目が多いとき、増える見込みがあるとき、頻繁に切り替えるときに使う［NNg-vertical］［MS-navview］［Carbon-shell］
- **階層は2段までにする**。3段目はページの中のタブか、サイドバーと詳細の間に一覧を挟む2ペインにする［HIG-sidebars］［Carbon-shell］［Fluent-nav］
- 2段目は開閉できるグループにする［HIG-sidebars］［Fluent-nav］
- 利用者が隠せるようにする。ただし初期状態で隠さない（見つけられなくなるから）［HIG-sidebars］
- 重要な項目と操作を末尾に置かない。長い一覧では重要度の低いものを下に置く（下端は画面外に出やすいから）［HIG-sidebars］［NNg-vertical］
- 左に置く（左から右に読む言語の場合）［NNg-vertical］

### 上部ナビ（広い幅の横ナビ）

- 同じ重さの行き先が少数で増えず、全部を1行に見せられ、本文の幅を優先したいときに使う［MS-navview］［NNg-vertical］
- 項目を詰めるために文字を小さくしたり、ラベルを不自然に縮めたり、行き先の分類を減らしたりしない。収まらないならサイドバーにする［NNg-vertical］
- 幅が狭くなって項目が溢れるなら、溢れた分だけをメニューに逃がさず、全体を畳んだメニュー（下）に切り替える（同じ重さの項目の一部だけが隠れるから）［MS-navview］

### 狭い幅で畳んだメニュー

- 狭い幅でだけ使う退避先にする。**広い幅でグローバルナビをメニューの中に隠さない**（隠したナビは見つけにくく、作業も遅くなるから）［NNg-hamburger］［NNg-vertical］
- 狭い幅で行き先が少ないなら、畳まずに見せる（ボトムタブにする）［NNg-hamburger］
- 同じ項目を横のナビと畳んだメニューの両方に置かない［NNg-vertical］

## 3. ローカルナビの型

1つの画面（または1つの対象）の中で、表示を切り替える。

### タブ

- 同じ文脈の中の、関連するがはっきり分かれた内容を切り替えるのに使う［NNg-tabs］［Carbon-tabs］［Atlassian-tabs］
- 使う条件を全部満たすときだけ使う:
  - 内容を短いラベルで分けられる［NNg-tabs］［GOVUK-tabs］
  - 1枚目が最もよく使われる。1枚目以外は補助の内容である（1枚目以外は見落とされやすいから）［NNg-tabs］［GOVUK-tabs］［Atlassian-tabs］
  - 利用者が複数のタブの内容を同時に見る必要がない［NNg-tabs］［GOVUK-tabs］
- 使わない:
  - 内容を見比べる必要があるとき（行き来して覚える負担がかかるから）。1ページに見出しで並べる［NNg-tabs］［GOVUK-tabs］［Carbon-tabs］
  - 順に全部読む内容・手順。手順はステッパー（4節）にする［GOVUK-tabs］［Carbon-tabs］
  - 同じ内容の別表現・絞り込み・並べ替え。セグメント（下）にする［Carbon-tabs］［Carbon-cs］
  - 別のページへの移動の代わり（6節）［Atlassian-tabs］［GOVUK-tabs］
- 数の上限は数値で決めない。ラベルが1行に収まり全部が見える数までにし、溢れたり折り返したりするなら型を変える（隠れたタブは見つけにくいから）［NNg-tabs］［GOVUK-tabs］［Carbon-tabs］
- 中身が無いタブを無効化しない。消すか、選んだときに理由を示す［GOVUK-tabs］
- 全タブに共通する見出し・情報はタブの列より上に置く［Atlassian-tabs］
- 各パネルの先頭にタブのラベルと同じ見出しを置く（狭い幅と読み上げで位置が分かるから）［GOVUK-tabs］
- タブの列の中にタブの列を重ねない［NNg-tabs］

### セグメント（表示切替）

- 同じ内容の表示形式（一覧・カード・表）の切り替え、絞り込み、並べ替えに使い、選んだら即時に反映する［Primer-seg］［Primer-nav］［Carbon-cs］
- 中身の違う領域の切り替えには使わない（それはタブ）［Carbon-cs］
- オン・オフや はい・いいえ の入力に使わない（それはスイッチ）［Carbon-cs］
- タブと併用するときは、タブの中の下位の切り替えとして置く［Carbon-tabs］［Carbon-cs］

### ローカルのサイドナビ

- 1つの区分の中の兄弟ページを縦に並べる。グローバルナビと合わせて逆L字の外枠にする（上がグローバル、左がローカル）［NNg-local］［Linear-redesign］
- **グローバルナビより目立たせない**。ただし見えるようにする（目立ちすぎると利用者がグローバルナビと取り違えるから）［NNg-local］
- 階層の上限はサイドバーと同じ2段［HIG-sidebars］［Carbon-shell］
- 狭い幅での畳み方は、出典に規則が無い。PJ の既存に合わせ、既存が無ければユーザーに確認する

## 4. 位置と移動の補助

### パンくず

- 階層の中の現在位置を示す補助にする。グローバルナビ・ローカルナビの代わりにしない［NNg-breadcrumbs］
- 閲覧の履歴ではなく、階層の経路を示す。親が複数ある対象は、代表の経路を1本だけ出す［NNg-breadcrumbs］
- 各段は実在するページへのリンクにする。現在のページを出すならリンクにしない［NNg-breadcrumbs］［APG-breadcrumb］
- 1〜2段の平坦な構造と、一本道の手続きでは使わない［NNg-breadcrumbs］［GOVUK-breadcrumbs］
- 狭い幅で折り返すなら短くする（親1段だけ、または先頭と末尾だけ）［NNg-breadcrumbs］［GOVUK-breadcrumbs］
- 親から子のページへ移ったら、子のページには親へ戻る導線（パンくずか戻るリンク）を置く［Primer-nav］

### 一覧と詳細の2ペイン

- 一覧から選んだ対象の詳細を、一覧を残したまま見せる。サイドバーの3段目の代わりにもなる［HIG-splitviews］［HIG-sidebars］［Primer-nav］
- 詳細に繋がる選択を、各ペインで選択中として表示し続ける（ペイン間の関係が分かるから）［HIG-splitviews］
- 狭い幅では2ペインを並べず、一覧と詳細を別画面に切り替える。詳細から一覧に戻る導線を置き、深い階層ならパンくずを置く［HIG-splitviews］［Primer-nav］
- 編集の領域を広げるためにペインを隠せるようにするなら、戻す手段を複数（ボタンとキーボードショートカット）用意する［HIG-splitviews］

### 作業中の対象の横タブ

- 利用者が対象を開く・閉じる・並べ替える・直接開くときに使う（ブラウザのタブと同じ期待を持たれる）［MS-tabview］
- 固定の行き先を並べるのに使わない。固定の項目が多いならグローバルナビにする［MS-tabview］
- 常にどれか1つを選択中にする。選択中のタブを閉じたら隣のタブを選択中にする［MS-tabview］［APG-tabs］
- 全部閉じられるなら、最後のタブを閉じた後のフォーカス先を決めておく［APG-tabs］
- 各タブの中身が自分の URL を持つなら、タブの列はリンクの列（`nav` とリンクと `aria-current`）として作り、`tablist` にしない。閉じるボタンは各リンクの隣に別のボタンとして置く。URL を持たないなら `tablist` で作り、7節のキーボード操作に従う［Primer-nav］［MDN-aria-current］［APG-tabs］
- タブが溢れたときと狭い幅での扱いは、出典に規則が無い。PJ の既存に合わせ、既存が無ければユーザーに確認する

### ステッパー

- 3段階以上の一本道の手続きに使う［Carbon-progress］
- 使わない: 3段階未満、順不同で進められる、条件で段階の数が変わる［Carbon-progress］
- 戻る・次への操作を置き換えず、補う［Carbon-progress］

### コマンドパレット（補助の導線）

- 行き先への移動・検索・コマンドの実行をキーボードから呼ぶ補助にする。呼び出しは Ctrl+K / Cmd+K を既定にし、現在地を候補の範囲にする［GH-cmdpalette］
- パレットからしか行けない行き先を作らない。全ての行き先を見えるナビにも置く（隠れた導線は見つけにくいという調査結果の適用）［NNg-hamburger］

## 5. 決定表

| 判断軸の値 | 型 |
|---|---|
| アプリ全体の固定の行き先・狭い幅・5以下 | ボトムタブ |
| アプリ全体の固定の行き先・狭い幅・6以上 | 畳んだメニュー（広い幅ではサイドバー） |
| アプリ全体の固定の行き先・中くらいの幅 | レール（広い幅のサイドバーと同じ項目・順序） |
| アプリ全体の固定の行き先・広い幅・多いか増える・頻繁に切り替える | サイドバー |
| アプリ全体の固定の行き先・広い幅・少数で増えない・本文の幅を優先 | 上部ナビ |
| 1つの区分の中の兄弟ページ | ローカルのサイドナビ（グローバルより控えめ） |
| 階層の3段目 | ページの中のタブ、または一覧と詳細の2ペイン |
| 利用者が開いて切り替えている対象 | 作業中の対象の横タブ |
| 一覧から選んだ対象を一覧を残して見る・広い幅 | 一覧と詳細の2ペイン |
| 同じ画面の、はっきり分かれた内容・同時に見ない・1枚目が主 | タブ |
| 同じ内容の表示形式・絞り込み・並べ替え | セグメント |
| 内容を見比べる・順に全部読む | タブにせず1ページに見出しで並べる |
| 3段階以上の一本道の手続き | ステッパー |
| 3段以上の階層の中の現在位置（補助） | パンくず |
| キーボードで素早く移動・実行（補助） | コマンドパレット（見えるナビと併置） |

## 6. 一貫性の原則

- **同じ種類の移動には、全画面で同じ型を使う**（1つの目的に1つの型）。画面ごとに型を選び直さない（同じ機能が同じ姿で現れると、別の画面で覚えたことが使えるから）［WCAG-324］［NNg-tabs］［Primer-nav］
- **グローバルナビは全画面で同じ位置・同じ順序に出す**。利用者が自分で変えたときだけ変わってよい［WCAG-323］［NNg-local］
- ローカルナビはグローバルナビより目立たせない［NNg-local］
- タブを階層やページ遷移の代わりにしない。画面の中の切り替え（URLが変わらないタブ）と、別ページへのリンクを1つの列に混ぜない［NNg-tabs］［Primer-nav］［Atlassian-tabs］
- 同じ行き先を複数のナビに重複して置かない［NNg-vertical］
- ナビの要素の数は、必要な行き先が見つかる範囲で最小にする［Primer-nav］
- ナビの部品は、それが動かす内容のすぐ近くに置く（タブは対象の内容の直上）［Primer-nav］

## 7. URL・キーボード・a11y

### URL

- 共有・再読込・戻る/進むで復元したい状態（選択中のタブ・絞り込み・ページ番号・開いたパネル）をURLに載せる［Vercel-guidelines］［Primer-nav］
- 移動はリンク（`<a>`）で作る。ボタンやクリック可能な `div` で代用しない（新しいタブで開く・中クリックが効かなくなるから）［Vercel-guidelines］
- パンくず・ページ送りの各項目はURLを変える［Primer-nav］
- 見た目がタブでもURLが変わるなら、それはリンクの列として作る（`nav` + リンク + `aria-current`）。`tablist` にしない［Primer-nav］［MDN-aria-current］
- 未保存の変更があるページから移動するときは警告する［Vercel-guidelines］［Primer-nav］

### キーボード（画面の中のタブ）

- `tablist` / `tab` / `tabpanel` を使い、選択中のタブに `aria-selected="true"` を付ける。タブに `aria-current` を使わない［APG-tabs］［MDN-aria-current］
- 横向きは左右の矢印でタブ間を移動し、端で反対の端に回り込む。上下の矢印は拾わない（ページのスクロールに残す）［APG-tabs］
- 縦向きは `aria-orientation="vertical"` を付け、上下の矢印で移動する［APG-tabs］
- Tab キーはタブの列からパネルへ移る。タブを1つずつ Tab で辿らせない［APG-tabs］［Atlassian-tabs］
- フォーカスで即座に切り替える（自動）のは、パネルが遅延なく表示できるときだけ。読み込みが要るなら、Enter / Space で切り替える（手動）にする（自動にするとフォーカス移動が遅くなるから）［APG-tabs］
- 閉じられるタブは Delete で閉じられるようにしてよい。同じ操作をコンテキストメニューにも置く［APG-tabs］

### ランドマークと現在位置

- ナビは `nav` ランドマークに入れる。1画面に複数あるなら、それぞれに異なる名前を付ける。名前に「ナビゲーション」を含めない（読み上げで重複するから）［APG-landmarks］
- 現在のページを指すナビのリンクに `aria-current="page"` を付ける。1つのナビの中で1つだけにする［APG-breadcrumb］［MDN-aria-current］
- パンくずは名前付きの `nav` の中に置く［APG-breadcrumb］
- アイコンだけの項目・ボタンにはアクセシブルな名前を付ける［Vercel-guidelines］
- ナビ項目の補助の操作を、ホバーやフォーカスのときだけ DOM に出さない。常に DOM に置くか、コンテキストメニューからも呼べるようにする（読み上げ・音声操作で届かなくなるから）［Fluent-nav］

## 8. 出典キー

| キー | URL | 確認 | 原文の該当文 |
|---|---|---|---|
| HIG-tabbars | https://developer.apple.com/design/human-interface-guidelines/tab-bars | 確認済み（JSON） | "Use a tab bar to support navigation, not to provide actions." / "Don't disable or hide tab bar buttons, even when their content is unavailable." / "Avoid overflow tabs." / "aim for a default list of five or fewer to preserve continuity between compact and regular view sizes." |
| HIG-sidebars | https://developer.apple.com/design/human-interface-guidelines/sidebars | 確認済み（JSON） | "In general, show no more than two levels of hierarchy in a sidebar. When a data hierarchy is deeper than two levels, consider using a split view interface that includes a content list between the sidebar items and detail view." / "Avoid hiding the sidebar by default to ensure that it remains discoverable." / "Avoid putting critical information or actions at the bottom of a sidebar." |
| HIG-splitviews | https://developer.apple.com/design/human-interface-guidelines/split-views | 確認済み（JSON） | "To support navigation, persistently highlight the current selection in each pane that leads to the detail view." / "Prefer using a split view in a regular — not a compact — environment." / "Provide multiple ways to reveal hidden panes." |
| MCA-navbar | https://github.com/material-components/material-components-android/blob/master/docs/components/BottomNavigation.md | 確認済み | "Navigation bars can have three to five destinations." |
| MCA-rail | https://github.com/material-components/material-components-android/blob/master/docs/components/NavigationRail.md | 確認済み | "The expanded nav rail is meant to replace the navigation drawer." / "The collapsed and expanded navigation rails match visually and can transition" |
| MCA-drawer | https://github.com/material-components/material-components-android/blob/master/docs/components/NavigationDrawer.md | 確認済み | "The navigation drawer is being deprecated. Use the expanded navigation rail instead." |
| NNg-hamburger | https://www.nngroup.com/articles/hamburger-menus/ | 確認済み | "Do not use hidden navigation (such as hamburger icons) in desktop user interfaces." / "If your site has 4 or fewer top-level navigation links, display them as visible links." |
| NNg-vertical | https://www.nngroup.com/articles/vertical-nav/ | 確認済み | "Vertical navigation is a good fit for broad or growing IAs, but takes up more space than horizontal navigation." / "Don't duplicate the menu both vertically and horizontally." / "Don't hide the navigation behind icons." / "In long menus, place less-important ones at the bottom." |
| NNg-tabs | https://www.nngroup.com/articles/tabs-used-right/ | 確認済み | "When users don't need to simultaneously see information presented under different tabs." / "Mixing in-page and navigation tabs within one tab control will disorient users." / "Websites and simple apps should avoid stacking tab lists within one tab control." |
| NNg-local | https://www.nngroup.com/articles/local-navigation/ | 確認済み | "local navigation should not be more salient than the global navigation, because, if that happens, users may mistake the local navigation for the global one." / "The global navigation is stable" |
| NNg-breadcrumbs | https://www.nngroup.com/articles/breadcrumbs/ | 確認済み | "Breadcrumbs Should Not Replace the Global Navigation Bar or the Local Navigation Within a Section." / "Breadcrumbs Aren't Necessary (or Useful) for Sites With Flat Hierarchies That Are Only 1 or 2 Levels Deep, or Sites That Are Linear in Structure." |
| GOVUK-tabs | https://design-system.service.gov.uk/components/tabs/ | 確認済み | "Do not use tabs if your users might need to: read through all of the content in order ... compare information in different tabs" / "Do not disable tabs" / "Avoid tabs that wrap over more than one line" / "Include a heading at the beginning of each tab that duplicates the information in the tab label." |
| GOVUK-breadcrumbs | https://design-system.service.gov.uk/components/breadcrumbs/ | 確認済み | "Do not use the breadcrumbs component on websites with a flat structure, or to show progress through a linear journey or transaction." / "configure the component to only show the first and last items on mobile devices." |
| Carbon-tabs | https://carbondesignsystem.com/components/tabs/usage/ | 確認済み | "Tabs should not be used if the user needs to compare information in different groups" / "When toggling between different formats of the same content or filtering the same content, use content switcher instead." / "horizontal tabs should not wrap to multiple lines" |
| Carbon-cs | https://carbondesignsystem.com/components/content-switcher/usage/ | 確認済み | "When navigating between distinct content areas like subpages, use tabs instead of a content switcher." / "should not be used as a binary input control." |
| Carbon-progress | https://carbondesignsystem.com/components/progress-indicator/usage/ | 確認済み | "When not to use: When a process or form has fewer than three steps. When the process may be completed in any order. When the number of steps may change based on conditional logic." |
| Carbon-shell | https://carbondesignsystem.com/components/UI-shell-left-panel/usage/ | 確認済み | "Use the left panel if there are more than five secondary navigation items, or if you expect a user to switch between secondary items frequently." / "The left panel does not support three tiers of navigation. If you have additional content to display beneath a sub-menu, use tabs within the page." |
| Atlassian-tabs | https://atlassian.design/components/tabs/usage | 確認済み | "Don't use tabs to navigate to different pages, or states." / "Don't use information that applies to all tabs underneath the tab line." |
| Primer-nav | https://primer.style/product/ui-patterns/navigation/ | 確認済み | "you can't mix tabs that change the URL with tabs just switch the visible tab panel." / "Minimize the number of navigational elements" / "Navigational elements should be laid out in close proximity to the content they affect." |
| Primer-seg | https://primer.style/product/components/segmented-control/ | 確認済み | "SegmentedControl is used to pick one choice from a linear set of closely related choices, and immediately apply that selection." |
| MS-navview | https://learn.microsoft.com/en-us/windows/apps/design/controls/navigationview | 確認済み | "We recommend top navigation when: You have 5 or fewer top-level navigation categories that are equally important" / "We recommend left navigation when: You have 5-10 equally important top-level navigation categories." / "it can provide a better user experience to switch the PaneDisplayMode from Top to LeftMinimal navigation, rather than letting all the items collapse into the overflow menu." |
| MS-tabview | https://learn.microsoft.com/en-us/windows/apps/design/controls/tab-view | 確認済み | "We recommend TabView when users will be able to: Dynamically open, close, or rearrange tabs. Open documents or web pages directly into tabs." / "if there are more than a few static navigation items, consider using a NavigationView control." / "there should always be an active tab." |
| Fluent-nav | https://fluent2.microsoft.design/components/web/react/core/nav/usage | 確認済み | "Navs can be organized with up to two levels of hierarchy." / "Secondary actions need to be in the DOM at all times, not only on hover or focus." |
| Linear-redesign | https://linear.app/now/how-we-redesigned-the-linear-ui | 確認済み | "I started to focus on this inverted L-shape. It's the global chrome of the application that controls the content in the main view." |
| GH-cmdpalette | https://docs.github.com/en/get-started/accessibility/github-command-palette | 確認済み | "Use the command palette to navigate, search, and run commands directly from your keyboard." / "it shows your location at the top left and uses it as the scope for suggestions" |
| WCAG-323 | https://www.w3.org/WAI/WCAG22/Understanding/consistent-navigation.html | 確認済み | "Navigational mechanisms that are repeated on multiple web pages within a set of web pages occur in the same relative order each time they are repeated, unless a change is initiated by the user." |
| WCAG-324 | https://www.w3.org/WAI/WCAG22/Understanding/consistent-identification.html | 確認済み | "Components that have the same functionality within a set of web pages are identified consistently." |
| APG-tabs | https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ | 確認済み | "It is recommended that tabs activate automatically when they receive focus as long as their associated tab panels are displayed without noticeable latency." / "If the tab list is horizontal, it does not listen for Down Arrow or Up Arrow" |
| APG-breadcrumb | https://www.w3.org/WAI/ARIA/apg/patterns/breadcrumb/ | 確認済み | "Breadcrumb trail is contained within a navigation landmark region." / "The link to the current page has aria-current set to page." |
| APG-landmarks | https://www.w3.org/WAI/ARIA/apg/practices/landmark-regions/ | 確認済み | "If a specific landmark role is used more than once on a page, provide each instance of that landmark with a unique label." / "Do not use the landmark role as part of the label." |
| MDN-aria-current | https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Attributes/aria-current | 確認済み | "Don't use aria-current as a substitute for aria-selected in gridcell, option, row or tab." / "Only mark one element in a set of elements as current with aria-current" |
| Vercel-guidelines | https://github.com/vercel-labs/web-interface-guidelines | 確認済み（README） | "Deep-link everything. Filters, tabs, pagination, expanded panels, anytime useState is used." / "Links are links. Use <a> or <Link> for navigation" / "Icon-only buttons are named." / "Unsaved changes. Warn before navigation when data could be lost." |
| shadcn-post | shadcn の X 投稿（縦タブはナビゲーション、横タブは作業中の集合） | 未確認（x.com を取得できない） | 判断軸「目的地の集合か、作業中の集合か」の着想元。規則は MS-tabview と HIG-sidebars で裏付けた範囲だけを書いた |

## 9. 未確認で外した規則

| 規則 | 外した理由 |
|---|---|
| 縦ナビへの切り替えの目安「トップ項目が7〜9を超えたら」（NN/g vertical-nav とされたもの） | NN/g vertical-nav の原文に該当する数値が無かった |
| レールの項目数（Android docs 3〜7 / Flutter 3〜5） | 出典間で食い違う。sources.md の採否にレールの数値の行が無いので、条件（広い幅のサイドバーと同じ項目）で書いた |
| 上部ナビは5以下・サイドバーは5〜10（MS NavigationView） | 原文は確認済みだが Windows アプリの1出典の数値で、sources.md の採否（数値でなく条件で書く）に合わせて条件だけ採った |
| Carbon left panel「二次ナビが5件を超えたら」 | 原文は確認済み。同上の理由で数値を採らず、「多い・頻繁に切り替える」の条件に含めた |
| 作業中の横タブのショートカット（Ctrl+T / Ctrl+W / Ctrl+Shift+T / Ctrl+1〜9、MS TabView） | 原文は確認済みだが Windows アプリ向け。Web ではブラウザが同じキーを使うため、Web アプリでの可否を確かめていない |
| HIG「sidebar と tab bar を併用せず単一 tab view で切り替える」（調査時の要約） | HIG の原文は「tab bar を sidebar に変換できる型を使う」で、併用の禁止は書かれていない。visionOS ではタブの中のサイドバーを認めている |
| GOV.UK はタブの矢印操作を外した（APG との食い違い、調査時の要約） | 原文で外したのは上下の矢印だけ。APG も横向きのタブでは上下を拾わないと書いており、食い違いではなかった |
| Atlassian の top nav 56px・side nav の幅・1024px 未満で overlay、Fluent 2 の 640px で overlay、M3 の dp の区切り | sources.md の採否どおり、画面幅の区切りと寸法はスキルに持たない |
| Atlassian「nav の名前に navigation を含めない」 | Atlassian の該当ページを開いていない。同じ規則を APG-landmarks の原文で確認したので、出典は APG にした |
| GOV.UK step-by-step navigation / task list | 原文で GOV.UK サイトの手続き案内に用途を限っており（"not for use within transactional services"）、アプリの汎用の型として一般化できない |
| 作業中の横タブが溢れたとき・狭い幅のときの扱い、ローカルのサイドナビの狭い幅での畳み方 | どの出典にも規則が見当たらなかった |
| コマンドパレットの「ナビ・検索・コマンドの3モード」 | GitHub docs 1出典の製品仕様で、型の規則として一般化する根拠が他に無い。移動・検索・実行を呼ぶ補助という用途だけ採った |
