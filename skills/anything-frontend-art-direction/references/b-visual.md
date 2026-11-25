# 配色・文字・画像

視覚表現を変える前に、読みやすさ、意味の伝わり方、端末が読み込む画像の三点を調べる。

新しい画面で色・書体・余白・構図そのものを決めるときは、[題材から画面を設計する](visual-direction.md)から始める。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## 文字とコントラスト

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="b-01"></a>B-01 | 文字サイズや用途によって、どの最低コントラスト条件が適用されるか | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-02"></a>B-02 | 文字の色相と、背景から明るさで区別できることを分けて評価する | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-03"></a>B-03 | コントラスト判定で大きい文字と扱える書体とサイズを確認する | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-04"></a>B-04 | 基準値にわずかに届かない配色や、細い字をどう評価するか | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-05"></a>B-05 | 最低コントラスト比の数値がどんな視認条件を想定したかを調べる | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-06"></a>B-06 | ブランド表示と、操作中に読む必要がある文言の例外を切り分ける | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-07"></a>B-07 | 表示機器の明るさと、コンテンツの相対的な明暗の比を区別する | [039](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| <a name="b-08"></a>B-08 | 初期スタイルでも読める行長と余白に収まるかを確かめる | [040](https://web.dev/learn/design/typography) |
| <a name="b-09"></a>B-09 | 画面幅に応じた文字サイズの切替が、読書距離とどう関わるか | [040](https://web.dev/learn/design/typography) |
| <a name="b-10"></a>B-10 | 可変の文字サイズがユーザーの拡大設定にも追従するか | [040](https://web.dev/learn/design/typography) |
| <a name="b-11"></a>B-11 | 文字列が横に伸びすぎないよう、行の最大幅を調整する | [040](https://web.dev/learn/design/typography) |
| <a name="b-12"></a>B-12 | 行の長さに対して、次の行頭を見失わない行間を探る | [040](https://web.dev/learn/design/typography) |
| <a name="b-13"></a>B-13 | Webフォントの取得待ちと、代替書体からの切替による揺れを検討する | [040](https://web.dev/learn/design/typography) |

## レスポンシブな配置

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="b2-01"></a>B2-01 | 狭い画面で文書を上から読んだとき、内容の順序が自然か | [080](https://web.dev/learn/design/macro-layouts) |
| <a name="b2-02"></a>B2-02 | 広い画面で主欄と副欄の幅をまとめて定義する | [080](https://web.dev/learn/design/macro-layouts) |
| <a name="b2-03"></a>B2-03 | カードの最小幅を基準に、本数が自然に変わる列配置を選ぶ | [080](https://web.dev/learn/design/macro-layouts) |
| <a name="b2-04"></a>B2-04 | レイアウトの切替を、ブラウザの自動配置に任せられるか | [080](https://web.dev/learn/design/macro-layouts) |
| <a name="b2-05"></a>B2-05 | 本文と副欄のどちらに置いても部品が収まるか | [079](https://web.dev/learn/design/micro-layouts) |
| <a name="b2-06"></a>B2-06 | 見出しや画像付きブロックの内部に、どの配置方式が合うか | [079](https://web.dev/learn/design/micro-layouts) |
| <a name="b2-07"></a>B2-07 | 画面幅だけでは判別できないコンポーネントの配置条件を見極める | [079](https://web.dev/learn/design/micro-layouts) |
| <a name="b2-08"></a>B2-08 | 親のインライン寸法を部品の切替条件に使う場合の境界を確認する | [079](https://web.dev/learn/design/micro-layouts) |
| <a name="b2-09"></a>B2-09 | ページ全体と各部品に、別々の切替条件を持たせる | [079](https://web.dev/learn/design/micro-layouts) |

## テーマと色の知覚

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="b3-01"></a>B3-01 | ブラウザの外枠にサイトの色を反映する必要があるか | [081](https://web.dev/learn/design/theming) |
| <a name="b3-02"></a>B3-02 | ホーム画面から起動するWebアプリで使われる色の指定先を確認する | [081](https://web.dev/learn/design/theming) |
| <a name="b3-03"></a>B3-03 | 端末の配色の好みに、サイトのテーマを合わせる | [081](https://web.dev/learn/design/theming) |
| <a name="b3-04"></a>B3-04 | ブラウザ外枠やSVG内でも、ライトとダークで色を切り替える | [081](https://web.dev/learn/design/theming) |
| <a name="b3-05"></a>B3-05 | テーマの値をまとめ、同じスタイルを二重に管理する箇所を減らす | [081](https://web.dev/learn/design/theming) |
| <a name="b3-06"></a>B3-06 | ダークテーマで写真やイラストの見え方を個別に調整する | [081](https://web.dev/learn/design/theming) |
| <a name="b3-07"></a>B3-07 | フォームのブラウザ既定色にも、対応する配色を伝える | [081](https://web.dev/learn/design/theming) · [X01](https://html.spec.whatwg.org/multipage/semantics.html#meta-color-scheme) |
| <a name="b3-08"></a>B3-08 | 視力や色の見分け方の違いを、永続的な条件に限らず考える | [082](https://web.dev/learn/accessibility/color-contrast) |
| <a name="b3-09"></a>B3-09 | 色相、彩度、明度を分けて配色候補を調整する | [082](https://web.dev/learn/accessibility/color-contrast) |
| <a name="b3-10"></a>B3-10 | 色覚に差がある人にも区別できる配色かを確認する | [082](https://web.dev/learn/accessibility/color-contrast) |
| <a name="b3-11"></a>B3-11 | 相対輝度から、文字色と背景色の組み合わせを計算で確認する | [082](https://web.dev/learn/accessibility/color-contrast) |
| <a name="b3-12"></a>B3-12 | 文字と操作アイコンで評価対象がどう変わるかを調べる | [082](https://web.dev/learn/accessibility/color-contrast) |
| <a name="b3-13"></a>B3-13 | 色が見分けられなくても、状態や操作の違いを判別できるか | [082](https://web.dev/learn/accessibility/color-contrast) |
| <a name="b3-14"></a>B3-14 | コントラストの好みとライト・ダークの好みを別々に扱う | [082](https://web.dev/learn/accessibility/color-contrast) · [028](https://www.w3.org/TR/mediaqueries-5/#prefers-contrast) |

## 画像の読み込み

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="b4-01"></a>B4-01 | 画像の固有幅が狭い画面を押し広げないかを確認する | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-02"></a>B4-02 | 枠内へ収める、切り抜く、切り抜く位置を選ぶ場合を分ける | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-03"></a>B4-03 | 画像の取得前に必要な表示領域を確保できるか | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-04"></a>B4-04 | 最初に見える画像の取得を、遅延設定で後回しにしていないか | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-05"></a>B4-05 | 取得優先度を上げる画像が、他の重要な取得を妨げないか | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-06"></a>B4-06 | 初期HTMLから見つからない画像を先読みする必要があるか | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-07"></a>B4-07 | 同じ画像の異なる幅の候補をブラウザへ渡す | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-08"></a>B4-08 | 配信する画像を選ぶために、レイアウト上の表示幅を伝える | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-09"></a>B4-09 | 端末のピクセル密度に応じた素材を用意する | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-10"></a>B4-10 | 装飾のための画像と、意味を伝える画像を識別する | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-11"></a>B4-11 | CSSでの見せ方と、HTMLが提供する取得時の情報を分ける | [085](https://web.dev/learn/design/responsive-images) |
| <a name="b4-12"></a>B4-12 | 画像を追加する前に、領域、素材の種類、意味を見直す | [085](https://web.dev/learn/design/responsive-images) |

## アイコンと画像形式

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="b5-01"></a>B5-01 | 同じ構図の候補を渡すか、構図自体を切り替えるかを決める | [089](https://web.dev/learn/design/picture-element) |
| <a name="b5-02"></a>B5-02 | 画像形式を複数示した場合、利用可能な最初の候補が何かを調べる | [089](https://web.dev/learn/design/picture-element) |
| <a name="b5-03"></a>B5-03 | ビューポートの境界ちょうどで、どの構図が選ばれるかを確かめる | [089](https://web.dev/learn/design/picture-element) |
| <a name="b5-04"></a>B5-04 | 狭い画面で主題が埋もれる場合に、別の切り抜きを用意する | [089](https://web.dev/learn/design/picture-element) |
| <a name="b5-05"></a>B5-05 | 追加要素による画像選択の制御が本当に必要かを判断する | [089](https://web.dev/learn/design/picture-element) |
| <a name="b5-06"></a>B5-06 | アイコンが周囲の文字とともに拡大し、自然に使えるかを確かめる | [090](https://web.dev/learn/design/icons) |
| <a name="b5-07"></a>B5-07 | アイコン素材ごとに、複数の解像度を用意する必要があるかを調べる | [090](https://web.dev/learn/design/icons) |
| <a name="b5-08"></a>B5-08 | 同じ文書に図形を置く場合と、外部ファイルで取得する場合を比べる | [090](https://web.dev/learn/design/icons) |
| <a name="b5-09"></a>B5-09 | アイコンの一部をCSSで変える必要があるかを確認する | [090](https://web.dev/learn/design/icons) |
