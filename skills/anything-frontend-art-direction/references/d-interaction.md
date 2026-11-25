# 入力と操作への応答

入力装置からアプリの状態が変わるまでを追う。送信結果を待たずに表示を変えた場合は、失敗時に利用者が見る状態も決める。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## 動き・フィードバック・非同期更新

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="d-01"></a>D-01 | アニメーション作法がどんな制作現場から生まれたかを調べる | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-02"></a>D-02 | 手描きのための知見を、デジタルで活かせる場面を選ぶ | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-03"></a>D-03 | 変形させた物体が、不自然に大きくなったり小さくなったりしないか | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-04"></a>D-04 | 大きな動きへ移る前に、見る人の注意をどこへ向けるか | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-05"></a>D-05 | 構図や光で、場面のどこを見るべきかが伝わるか | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-06"></a>D-06 | 連続して描く方法と、主要な姿勢を先に決める方法を使い分ける | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-07"></a>D-07 | 本体が止まった後も、付属部分が動き続ける表現を調整する | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-08"></a>D-08 | 開始と停止で速度が急に変わる動きを見直す | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-09"></a>D-09 | 曲線を描く動作で、軌跡が不自然に直線化されていないか | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-10"></a>D-10 | 主となる動きの邪魔をせず、状況を補う動作を考える | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-11"></a>D-11 | 同じ軌跡でも、時間配分で重さや速度の印象が変わるか | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-12"></a>D-12 | 写実性と強調のどちらを優先するか、表現の狙いから決める | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-13"></a>D-13 | 立体の向きや重さが、姿勢の変化を通じても伝わるか | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-14"></a>D-14 | 好感とは別に、登場人物が印象に残る表現を考える | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-15"></a>D-15 | アニメーション原則の出典と、解説資料の位置づけを確認する | [003](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation) |
| <a name="d-16"></a>D-16 | プラットフォームの標準動作はどんな状態を伝えるために使われるか | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-17"></a>D-17 | 追加する動きが利用者にとってどんな役割を持つかを問う | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-18"></a>D-18 | 動きを知覚できない場合にも、重要な変化が伝わるか | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-19"></a>D-19 | 操作方向に対応した短い動きで、起きたことを伝えられるか | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-20"></a>D-20 | 繰り返し操作で毎回アニメーション終了を待つ必要がないか | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-21"></a>D-21 | 没入型画面で、視野の端や大きな物体の動きが不快感を招かないか | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-22"></a>D-22 | 対象プラットフォームや発行時期に応じて、動きの指針を確認する | [010](https://developer.apple.com/design/human-interface-guidelines/motion.md) |
| <a name="d-23"></a>D-23 | アニメーションの長短を既定の時間トークンから選ぶ | [011](https://raw.githubusercontent.com/material-components/material-web/v2.5.0/tokens/versions/latest/sass/_md-sys-motion.scss) |
| <a name="d-24"></a>D-24 | 登場、退出、強調の違いに応じた速度曲線を調べる | [011](https://raw.githubusercontent.com/material-components/material-web/v2.5.0/tokens/versions/latest/sass/_md-sys-motion.scss) |
| <a name="d-25"></a>D-25 | 移動と視覚効果で、ばねの設定値を使い分ける | [011](https://raw.githubusercontent.com/material-components/material-web/v2.5.0/tokens/versions/latest/sass/_md-sys-motion.scss) |
| <a name="d-26"></a>D-26 | デザイン指針と実装トークンの版が対応しているかを調べる | [011](https://raw.githubusercontent.com/material-components/material-web/v2.5.0/tokens/versions/latest/sass/_md-sys-motion.scss) |
| <a name="d-27"></a>D-27 | 画面サイズや遷移の種類ごとに、時間がどう調整されるかを見る | [012](https://m1.material.io/motion/duration-easing.html) |
| <a name="d-28"></a>D-28 | 標準的な速度変化を異なる実行環境でどう表現するか | [012](https://m1.material.io/motion/duration-easing.html) |
| <a name="d-29"></a>D-29 | 細かな相互作用を扱う設計論の入口を探す | [013](https://jnd.org/microinteractions-my-foreword/) |
| <a name="d-30"></a>D-30 | 全体の機能が揃っていても、日常操作の細部に支障がないか | [013](https://jnd.org/microinteractions-my-foreword/) |
| <a name="d-31"></a>D-31 | 問題を伝える画面から、すぐ実行できる修復手段へ進めるか | [013](https://jnd.org/microinteractions-my-foreword/) |
| <a name="d-32"></a>D-32 | 繰り返し起こるつまずきを観察し、操作の発端から結果までを設計する | [013](https://jnd.org/microinteractions-my-foreword/) |
| <a name="d-33"></a>D-33 | 利用状況に応じて、手動で繰り返す調整を減らせないか | [013](https://jnd.org/microinteractions-my-foreword/) |
| <a name="d-34"></a>D-34 | 確定を待たずUIに結果を見せる方法を、キャッシュ更新と表示上の仮置きから選ぶ | [036](https://raw.githubusercontent.com/tanstack/query/main/docs/framework/react/guides/optimistic-updates.md) |
| <a name="d-35"></a>D-35 | 読み直し中や失敗後にも、送信した仮の項目をどう表示するか | [036](https://raw.githubusercontent.com/tanstack/query/main/docs/framework/react/guides/optimistic-updates.md) |
| <a name="d-36"></a>D-36 | 複数の保留中の更新を、別コンポーネントから区別して表示する | [036](https://raw.githubusercontent.com/tanstack/query/main/docs/framework/react/guides/optimistic-updates.md) |
| <a name="d-37"></a>D-37 | 再取得が失敗しても元の状態に戻す必要があるか | [036](https://raw.githubusercontent.com/tanstack/query/main/docs/framework/react/guides/optimistic-updates.md) |
| <a name="d-38"></a>D-38 | 古い再取得の結果が楽観更新を上書きしないよう制御する | [036](https://raw.githubusercontent.com/tanstack/query/main/docs/framework/react/guides/optimistic-updates.md) |
| <a name="d-39"></a>D-39 | リモート処理の前に、現在のキャッシュから仮の表示内容を作る | [037](https://swr.vercel.app/docs/mutation) |
| <a name="d-40"></a>D-40 | 仮の値を戻す場合と、実際の応答で更新する場合を区別する | [037](https://swr.vercel.app/docs/mutation) |
| <a name="d-41"></a>D-41 | 画面復帰による再検証と書き込みが競合したときの表示を調べる | [037](https://swr.vercel.app/docs/mutation) |
| <a name="d-42"></a>D-42 | 同じ識別子の確定値を保持しながら、仮の応答を提示する | [038](https://raw.githubusercontent.com/apollographql/apollo-client/main/docs/source/performance/optimistic-ui.mdx) |
| <a name="d-43"></a>D-43 | 成功と失敗で、Apolloの仮データがいつ消えるかを確かめる | [038](https://raw.githubusercontent.com/apollographql/apollo-client/main/docs/source/performance/optimistic-ui.mdx) |
| <a name="d-44"></a>D-44 | 入力や条件によって楽観表示を行わない場合を選ぶ | [038](https://raw.githubusercontent.com/apollographql/apollo-client/main/docs/source/performance/optimistic-ui.mdx) |

## ポインターとジェスチャ

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="d2-01"></a>D2-01 | マウス、ペン、タッチで共通して追跡できる情報を確認する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-02"></a>D2-02 | 入力方式を抽象化する目的と、ブラウザの直接操作を分けて考える | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-03"></a>D2-03 | 複数接触を識別する値を長期的な識別子にできるか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-04"></a>D2-04 | 接触面の大きさや圧力が入力機器によってどう表現されるか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-05"></a>D2-05 | ペンの傾き、回転、横方向の圧力をどう解釈するか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-06"></a>D2-06 | デバイス種別と、その種別の主ポインターかどうかを区別する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-07"></a>D2-07 | ボタンの組み合わせや接触で、入力開始がいつ通知されるか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-08"></a>D2-08 | ブラウザが入力列を打ち切ったとき、どのイベントを処理するか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-09"></a>D2-09 | まとめて通知された移動から、途中の座標を取得できるか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-10"></a>D2-10 | ブラウザのパンやズームをどの段階で許可するか | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-11"></a>D2-11 | スクロールを担当する祖先と、ジェスチャー許可の関係を確認する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-12"></a>D2-12 | 境界の外へ動いた後も、移動イベントを同じ要素で受け取る | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-13"></a>D2-13 | 直接操作でキャプチャが暗黙に始まる条件と、入力終了時の解除を確認する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-14"></a>D2-14 | 入力の細かい時系列が必要な場合に、合成前のイベントを取り出す | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-15"></a>D2-15 | 予測座標を一時的に表示する場合、確定した入力との違いを管理する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-16"></a>D2-16 | ポインター入力と互換マウス入力の両方を受ける場合に重複を確認する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-17"></a>D2-17 | 開始イベントをキャンセルしても残る互換通知を調べる | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-18"></a>D2-18 | ホバーのない入力で、マウス互換イベントが出る順序を確認する | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-19"></a>D2-19 | 接触の精度を上げることと、デバイス特定につながる情報量の関係を調べる | [053](https://www.w3.org/TR/pointerevents3/) |
| <a name="d2-20"></a>D2-20 | ドラッグ中の視覚表示と、ドロップ先の受付条件を分ける | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-21"></a>D2-21 | ページの内外をまたいで移動するとき、データの送り元と受け先を確認する | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-22"></a>D2-22 | ドラッグ操作の各段階を、適切なイベントで追跡する | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-23"></a>D2-23 | OSから持ち込んだファイルで、ページ側のどのイベントが起きるか | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-24"></a>D2-24 | リンクや画像の既定のドラッグと、独自部品のドラッグを区別する | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-25"></a>D2-25 | ドラッグ可能な領域で、文字選択に必要な操作が妨げられないか | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-26"></a>D2-26 | 異なる受け手が識別できる形式で、ドラッグデータを渡す | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-27"></a>D2-27 | ドラッグを開始した時点と、ドロップ時点で読み取れるデータを確認する | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-28"></a>D2-28 | 対象がドロップを受け付けるようにする処理を確認する | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |
| <a name="d2-29"></a>D2-29 | イベント、転送データ全体、個々の転送項目のAPIを使い分ける | [054](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API) |

## ピンチ操作とタッチイベント

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="d4-01"></a>D4-01 | 二つのポインターの間隔を使って、ピンチ操作を判別する | [075](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events/Pinch_zoom_gestures) |
| <a name="d4-02"></a>D4-02 | 接触開始から終了まで、追跡対象と前回の間隔を保つ | [075](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events/Pinch_zoom_gestures) |
| <a name="d4-03"></a>D4-03 | 間隔が広がる場合と狭まる場合を区別して拡大縮小する | [075](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events/Pinch_zoom_gestures) |
| <a name="d4-04"></a>D4-04 | ブラウザのスクロールや拡大を抑えるCSSを、例のどこに指定しているか | [075](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events/Pinch_zoom_gestures) |
| <a name="d4-05"></a>D4-05 | マウス互換の通知だけでは、同時に触れた複数の点を追えるか | [076](https://www.w3.org/TR/touch-events/) |
| <a name="d4-06"></a>D4-06 | 全接触点、対象上の接触点、今回変わった点を取り分ける | [076](https://www.w3.org/TR/touch-events/) |
| <a name="d4-07"></a>D4-07 | 始点でタッチイベントをキャンセルした場合、既定動作がどうなるか | [076](https://www.w3.org/TR/touch-events/) |
| <a name="d4-08"></a>D4-08 | UAがタッチを中断したときに、追跡中の状態を片付ける | [076](https://www.w3.org/TR/touch-events/) |
| <a name="d4-09"></a>D4-09 | タッチとマウスの双方が通知される場合、先に処理されるものを確かめる | [076](https://www.w3.org/TR/touch-events/) |
| <a name="d4-10"></a>D4-10 | 接触点の追跡を開始・終了するイベントを確認する | [076](https://www.w3.org/TR/touch-events/) |

## 操作に応じた状態選択

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="d5-01"></a>D5-01 | HTMLの動的な状態をCSSのセレクターがどう参照するか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-02"></a>D5-02 | リンクの訪問状態を使った見た目に、プライバシー上どんな限界があるか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-03"></a>D5-03 | フォーカスできる要素とできない要素で、押下中の判定がどう違うか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-04"></a>D5-04 | 押された要素の祖先や、ラベルとコントロールの関連にも表示が及ぶか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-05"></a>D5-05 | ポインターを置いた要素の周囲や、関連するラベルの状態を調べる | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-06"></a>D5-06 | フォーカスが要素自身やシャドウツリーのホストでどう扱われるか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-07"></a>D5-07 | 文書内を指すリンクで、現在の対象だけにスタイルを当てられるか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-08"></a>D5-08 | モーダルや書き方向の状態を、対応する疑似クラスから確認する | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-09"></a>D5-09 | 複数レベルの見出しを一つのセレクターで対象にできるか | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-10"></a>D5-10 | メディア再生、シーク、読み込み待ちの違いを状態で表す | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="d5-11"></a>D5-11 | 展開中の要素と、表示中のポップオーバーを選び分ける | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
