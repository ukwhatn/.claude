# アクセシビリティ

最初に適用する達成基準の本文を確認する。部品のキーボード操作を設計するときは APG の該当パターンも開く。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## WCAG の適用範囲

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e-01"></a>E-01 | 参照するWCAGの版と、先行版の位置づけを確認する | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-02"></a>E-02 | 縦に読む文書は幅320 CSS px、横に読む文書は高さ256 CSS px相当で確認する。二次元配置が欠かせない部分には例外がある。 | [002](https://www.w3.org/TR/WCAG22/#reflow) |
| <a name="e-03"></a>E-03 | 固定ヘッダーなどがキーボードフォーカスを完全に隠さないか | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-04"></a>E-04 | より厳しい遮蔽条件で、フォーカス対象のどの部分も隠れずに見えるかを確認する | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-05"></a>E-05 | フォーカスの印を、その面積と状態間のコントラストから測る | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-06"></a>E-06 | ドラッグ以外の単一ポインター操作で同じ結果に到達できるか | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-07"></a>E-07 | 押す領域が小さい場合に、間隔や代替手段による例外を確認する | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-08"></a>E-08 | 複数ページを使っていても、同じヘルプを予測できる場所で見つけられるか | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-09"></a>E-09 | 同じ手続きで入力済みの情報を、選択や自動入力で再利用できるか | [002](https://www.w3.org/TR/WCAG22/#redundant-entry) |
| <a name="e-10"></a>E-10 | 認証に記憶や識別の課題がある場合、使える代替や支援を確認する | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-11"></a>E-11 | 厳しい水準の認証基準で、どの例外が適用されるかを区別する | [002](https://www.w3.org/TR/WCAG22/) |
| <a name="e-12"></a>E-12 | 文字以外のコントラスト、文字間隔、ホバー表示の達成基準を参照する | [002](https://www.w3.org/TR/WCAG22/) |

## ダイアログ・タブ・コンボボックス

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e2-01"></a>E2-01 | ダイアログが出ている間、背後の画面に何ができるかを確認する | [006](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| <a name="e2-02"></a>E2-02 | ダイアログ内でTabを押し続けたとき、次の移動先を確認する | [006](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| <a name="e2-03"></a>E2-03 | ダイアログが開いた直後のフォーカスとEscape操作を検証する | [006](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| <a name="e2-04"></a>E2-04 | 一覧や表を含むダイアログの導入を、どこから読めるようにするか | [006](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| <a name="e2-05"></a>E2-05 | ダイアログを閉じた後、作業に戻るためのフォーカス先を決める | [006](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| <a name="e2-06"></a>E2-06 | モーダルだと通知する前に、背後の操作と表示がどう制限されているかを調べる | [006](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) |
| <a name="e2-07"></a>E2-07 | 一連の操作を中断する通知に、利用者の応答が必要かを判定する | [007](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/) |
| <a name="e2-08"></a>E2-08 | 重要な確認ダイアログの名前とメッセージが、支援技術に伝わるか | [007](https://www.w3.org/WAI/ARIA/apg/patterns/alertdialog/) |
| <a name="e2-09"></a>E2-09 | タブを選び直したとき、対応する表示領域が一つに切り替わるか | [008](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) |
| <a name="e2-10"></a>E2-10 | タブの向きや削除操作に応じて、キー入力と次のフォーカス先を確認する | [008](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) |
| <a name="e2-11"></a>E2-11 | フォーカス移動だけでタブを切り替えても、パネルの表示待ちが操作を妨げないか | [008](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) |
| <a name="e2-12"></a>E2-12 | タブと領域を関連付け、パネル本体がキーボード経路に必要な場合を確認する | [008](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) |
| <a name="e2-13"></a>E2-13 | 選択肢のポップアップを持つ部品で、自由入力を許す必要があるか | [009](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) |
| <a name="e2-14"></a>E2-14 | 入力途中に出す候補を、提示のみ、自動選択、欄内補完のどれにするか | [009](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) |
| <a name="e2-15"></a>E2-15 | フォーカスを実際に移す場合と、候補の位置だけを支援技術に知らせる場合を分ける | [009](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) |
| <a name="e2-16"></a>E2-16 | 候補の移動、確定、取り消しを、それぞれどのキーで行うかを確認する | [009](https://www.w3.org/WAI/ARIA/apg/patterns/combobox/) |

## 動きを減らす設定

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e3-01"></a>E3-01 | 動きを抑えたいユーザー設定をCSSから検出できるか | [028](https://www.w3.org/TR/mediaqueries-5/) |
| <a name="e3-02"></a>E3-02 | 動きを減らすことで、身体的な不快感と注意の妨げの双方を減らせるか | [028](https://www.w3.org/TR/mediaqueries-5/) |
| <a name="e3-03"></a>E3-03 | 透けるレイヤーが見づらい場合に、透明表現を減らす設定を調べる | [028](https://www.w3.org/TR/mediaqueries-5/) |
| <a name="e3-04"></a>E3-04 | 高低どちらのコントラストを望む場合にも役立つ装飾の整理を考える | [028](https://www.w3.org/TR/mediaqueries-5/) |
| <a name="e3-05"></a>E3-05 | 大きな拡大や画面移動を、より穏やかな表現に置き換えられるか | [029](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) |
| <a name="e3-06"></a>E3-06 | モーション設定の値を省略したとき、どの条件が成り立つか | [029](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) |
| <a name="e3-07"></a>E3-07 | 利用する端末ごとに、動きを抑える設定を検証できる場所を確認する | [029](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) |
| <a name="e3-08"></a>E3-08 | 低減モードでCSSの動きを差し替え、設定変更をスクリプトでも受け取る | [029](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion) · [030](https://web.dev/articles/prefers-reduced-motion) |
| <a name="e3-09"></a>E3-09 | 操作を説明する動きと、演出のためだけの動きを分ける | [030](https://web.dev/articles/prefers-reduced-motion) |
| <a name="e3-10"></a>E3-10 | 背景と前景のずれた動きで不快感が起こる場合を見直す | [030](https://web.dev/articles/prefers-reduced-motion) |
| <a name="e3-11"></a>E3-11 | JavaScriptで開始したアニメーションを、設定変更時にどう扱うか | [030](https://web.dev/articles/prefers-reduced-motion) |
| <a name="e3-12"></a>E3-12 | アニメ画像の静止版を端末設定に応じて配信できるか | [030](https://web.dev/articles/prefers-reduced-motion) |
| <a name="e3-13"></a>E3-13 | 低減設定が見つからないことを、強い動きへの同意として扱っていないか | [031](https://www.smashingmagazine.com/2020/09/design-reduced-motion-sensitivities/) |
| <a name="e3-14"></a>E3-14 | どの画面効果を低減対象として確認するかを決める | [031](https://www.smashingmagazine.com/2020/09/design-reduced-motion-sensitivities/) |
| <a name="e3-15"></a>E3-15 | 大きな移動を省いても、遷移したことが伝わる別の見せ方を探す | [031](https://www.smashingmagazine.com/2020/09/design-reduced-motion-sensitivities/) |
| <a name="e3-16"></a>E3-16 | 視差や強い自動スクロールを外した後も、目標の内容に到達できるか | [031](https://www.smashingmagazine.com/2020/09/design-reduced-motion-sensitivities/) |
| <a name="e3-17"></a>E3-17 | 動きが主題のサイトで、端末の好みを尊重しながらサイト側の切替も提供する | [031](https://www.smashingmagazine.com/2020/09/design-reduced-motion-sensitivities/) |

## キーボードと文書内移動

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e4-01"></a>E4-01 | ページを開くたびに現れる同じ案内を、操作順で飛ばせるか | [043](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html) |
| <a name="e4-02"></a>E4-02 | 対象のページ集合とブラウザの移動機能を踏まえ、追加のスキップ操作が必要かを判断する | [043](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html) |
| <a name="e4-03"></a>E4-03 | 繰り返すナビゲーションで、読み上げやキー入力の負担がどれほど増えるか | [043](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html) |
| <a name="e4-04"></a>E4-04 | 直接移動するリンクと、見出しや領域で構造を示す方法を選ぶ | [043](https://www.w3.org/WAI/WCAG22/Understanding/bypass-blocks.html) |
| <a name="e4-05"></a>E4-05 | ポインターなしで操作する場合に使えない機能を探す | [044](https://webaim.org/techniques/keyboard/) |
| <a name="e4-06"></a>E4-06 | キーボードの現在位置が、背景の上で明瞭に見えるか | [044](https://webaim.org/techniques/keyboard/) |
| <a name="e4-07"></a>E4-07 | 画面の見た目だけで順序を整えた結果、Tab移動が不自然になっていないか | [044](https://webaim.org/techniques/keyboard/) |
| <a name="e4-08"></a>E4-08 | 操作できない要素をTab経路に足さず、独自コントロールには必要な操作を与える | [044](https://webaim.org/techniques/keyboard/) |
| <a name="e4-09"></a>E4-09 | 繰り返す案内を飛ばせる方法と、キー操作で閉じ込められない方法を用意する | [044](https://webaim.org/techniques/keyboard/) |
| <a name="e4-10"></a>E4-10 | リンク、ボタン、選択部品を、それぞれ期待どおりのキーで操作できるか | [044](https://webaim.org/techniques/keyboard/) |

## フォーカスの扱い

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e5-01"></a>E5-01 | ブラウザがフォーカスの見える表示を選ぶ条件を確認する | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-02"></a>E5-02 | 既定のフォーカス枠を変更したことで、現在位置を見失わないか | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-03"></a>E5-03 | クリックされたボタンと入力欄で、既定の表示が異なる場合を調べる | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-04"></a>E5-04 | フォーカスの状態と、印を描く条件を区別してスタイルを指定する | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-05"></a>E5-05 | ページの色に対して、フォーカスリングの強さを確認する | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-06"></a>E5-06 | マウスとキーボードを切り替えても、印の挙動を理解できるか | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-07"></a>E5-07 | フォーカス表示条件を定めるセレクター仕様を参照する | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-08"></a>E5-08 | 同じボタンをクリックとTabで操作し、スタイルの違いを比較する | [055](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Selectors/:focus-visible) |
| <a name="e5-09"></a>E5-09 | スクリプトでフォーカスを指定した際に、画面移動と印がどう変わるか | [056](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) |
| <a name="e5-10"></a>E5-10 | 利用者の表示位置を動かさず、フォーカスだけを移す必要があるか | [056](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) |
| <a name="e5-11"></a>E5-11 | フォーカスの印をブラウザに任せる場合と、意図的に表示する場合を選ぶ | [056](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) |
| <a name="e5-12"></a>E5-12 | プログラムでフォーカスしたボタンや入力欄で、印の見え方を個別に試す | [056](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) |
| <a name="e5-13"></a>E5-13 | 押下イベントから移したフォーカスが、ブラウザの既定動作で戻らないか | [056](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) |
| <a name="e5-14"></a>E5-14 | シャドウツリーをまたぐTab順を、HTMLのフォーカス規則と照らす | [056](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/focus) |

## 点滅・動きの制御

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e6-01"></a>E6-01 | 画面の動きが、不快感やタスクからの注意の逸れを招く場面を探す | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-02"></a>E6-02 | 任意の1秒間にフラッシュが3回以下か、一般フラッシュと赤色フラッシュの両閾値を下回る場合に達成基準を満たす。 | [086](https://web.dev/learn/accessibility/motion) · [002](https://www.w3.org/TR/WCAG22/#three-flashes-or-below-threshold) |
| <a name="e6-03"></a>E6-03 | 他の内容と並行して長く続く自動の動きを止められるか | [086](https://web.dev/learn/accessibility/motion) · [002](https://www.w3.org/TR/WCAG22/#pause-stop-hide) |
| <a name="e6-04"></a>E6-04 | 動きを止める設定を、対象部品だけに効かせるかサイト全体に効かせるかを考える | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-05"></a>E6-05 | 似た端末設定でも、オンにしたときの意味が異なる場合を確認する | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-06"></a>E6-06 | 必須でないアニメーションは、静止表示から追加する構成にできるか | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-07"></a>E6-07 | 配色、コントラスト、動きの好みを独立に組み合わせる | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-08"></a>E6-08 | 動きを望むか利用者自身が選べる切替を設ける | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-09"></a>E6-09 | 連続する動きに、ループを避ける方法と終了する手段を用意する | [086](https://web.dev/learn/accessibility/motion) |
| <a name="e6-10"></a>E6-10 | 強い点滅を含む映像の検査に、専用評価ツールを使う場面を確認する | [086](https://web.dev/learn/accessibility/motion) |

## 画像の目的と代替テキスト

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e7-01"></a>E7-01 | テキスト付コントロールのアイコンが、読み上げを重複させないか | [090](https://web.dev/learn/design/icons) |
| <a name="e7-02"></a>E7-02 | 文字なしボタンの意図が伝わるか、表示とアクセシブル名を確かめる | [090](https://web.dev/learn/design/icons) |
| <a name="e7-03"></a>E7-03 | 画像の用途に応じて代替テキストを選ぶ資料を探す | [115](https://www.w3.org/WAI/tutorials/images/decision-tree/) |
| <a name="e7-04"></a>E7-04 | 画像にしかない文字を、周囲の実テキストで補えるか | [115](https://www.w3.org/WAI/tutorials/images/decision-tree/) |
| <a name="e7-05"></a>E7-05 | 画像を取り除くとリンク先や操作が不明になるかを判断する | [115](https://www.w3.org/WAI/tutorials/images/decision-tree/) |
| <a name="e7-06"></a>E7-06 | 写真や図が伝える内容を、短い代替や本文でどう伝えるかを選ぶ | [115](https://www.w3.org/WAI/tutorials/images/decision-tree/) |
| <a name="e7-07"></a>E7-07 | 飾りに過ぎない画像で、読み上げが不要かを確認する | [115](https://www.w3.org/WAI/tutorials/images/decision-tree/) |
| <a name="e7-08"></a>E7-08 | 画像を使った操作部品では、実行内容が伝わる名前を付ける | [117](https://www.w3.org/WAI/tutorials/images/functional/) |
| <a name="e7-09"></a>E7-09 | 画像だけのホームリンクから、移動先を理解できる名前を付ける | [117](https://www.w3.org/WAI/tutorials/images/functional/) |
| <a name="e7-10"></a>E7-10 | リンクに移動先の文字がある場合、添えた画像の説明を重ねない | [117](https://www.w3.org/WAI/tutorials/images/functional/) |
| <a name="e7-11"></a>E7-11 | リンクが新しいウィンドウを開くとき、その追加情報を伝えるかを判断する | [117](https://www.w3.org/WAI/tutorials/images/functional/) |
| <a name="e7-12"></a>E7-12 | 印刷などの操作画像について、図柄より操作結果が分かるかを確認する | [117](https://www.w3.org/WAI/tutorials/images/functional/) |
| <a name="e7-13"></a>E7-13 | 機能画像の解説と、対応する達成基準や技法の位置を調べる | [117](https://www.w3.org/WAI/tutorials/images/functional/) |
| <a name="e7-14"></a>E7-14 | 情報を伝える画像では、見た形の逐一説明と伝えたい内容を区別する | [118](https://www.w3.org/WAI/tutorials/images/informative/) |
| <a name="e7-15"></a>E7-15 | 隣の情報を区別するアイコンに、どの種類の値かを伝える名前を付ける | [118](https://www.w3.org/WAI/tutorials/images/informative/) |
| <a name="e7-16"></a>E7-16 | 画像だけが持つ情報を、隣の本文に重ならない形で補う | [118](https://www.w3.org/WAI/tutorials/images/informative/) |
| <a name="e7-17"></a>E7-17 | 作業の手順を示す図が伝える操作を、文章でも理解できるようにする | [118](https://www.w3.org/WAI/tutorials/images/informative/) |
| <a name="e7-18"></a>E7-18 | 雰囲気を伝えるだけの画像を、意味ある内容として扱う必要があるか | [118](https://www.w3.org/WAI/tutorials/images/informative/) |
| <a name="e7-19"></a>E7-19 | 形式を選べるダウンロードで、アイコンだけの識別に頼っていないか | [118](https://www.w3.org/WAI/tutorials/images/informative/) |
| <a name="e7-20"></a>E7-20 | 情報画像の解説に関連する達成基準や技法を調べる | [118](https://www.w3.org/WAI/tutorials/images/informative/) |

## カルーセルの操作

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="e8-01"></a>E8-01 | 自動切替や画面外のスライドが、読み上げや移動の妨げにならないか | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-02"></a>E8-02 | 前後へ移動でき、自動回転がある場合は利用者が止められるか | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-03"></a>E8-03 | 前後ボタン方式とタブ方式の実例を比較する | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-04"></a>E8-04 | スライドを選ぶ手段と、自動回転を管理する手段を区別する | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-05"></a>E8-05 | カルーセルにフォーカスが入ったら自動回転を止め、明示操作まで再開しないかを確認する | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-06"></a>E8-06 | スライドを選ぶ部品の有無とTab経路を踏まえて方式を決める | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-07"></a>E8-07 | カルーセル全体を示す領域の名前と、ランドマークに含める必要性を確認する | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-08"></a>E8-08 | 回転を切り替えるボタンの名前が、次に起きる操作を伝えるか | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-09"></a>E8-09 | 個々のスライドを支援技術で区別できる名前を付ける | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-10"></a>E8-10 | 自動回転中と停止中で、スライド更新の読み上げを切り替える場合を検討する | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-11"></a>E8-11 | タブで選択するスライドを、タブパネルとして関連付ける | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
| <a name="e8-12"></a>E8-12 | 個別の選択ボタンで、表示中のスライドと他の候補を区別する | [109](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/) |
