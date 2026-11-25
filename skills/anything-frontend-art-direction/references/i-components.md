# コンポーネント基盤

見た目のトークンと、ブラウザーが扱う状態を分けて設計する。独自部品をフォームに参加させる場合は検証と送信の両方を試す。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## テーマとコンポーネントライブラリ

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="i-01"></a>I-01 | shadcnコンポーネントの配色をCSS変数で管理する設定 | [024](https://ui.shadcn.com/docs/theming) |
| <a name="i-02"></a>I-02 | 面とその上に載る文字やアイコンの色を対で定義する方法 | [024](https://ui.shadcn.com/docs/theming) |
| <a name="i-03"></a>I-03 | ライトとダークのトークンをTailwindへ公開する方法 | [024](https://ui.shadcn.com/docs/theming) |
| <a name="i-04"></a>I-04 | 一つの基準値から角丸の段階を作る方法 | [024](https://ui.shadcn.com/docs/theming) |
| <a name="i-05"></a>I-05 | 初期テーマに使う色のセットを選ぶ設定 | [024](https://ui.shadcn.com/docs/theming) |
| <a name="i-06"></a>I-06 | CSS変数を使わない場合にCLIが出力するクラス | [024](https://ui.shadcn.com/docs/theming) |
| <a name="i-07"></a>I-07 | Radixの部品を組み合わせて独自APIを作る自由度 | [025](https://www.radix-ui.com/primitives/docs/overview/getting-started) |
| <a name="i-08"></a>I-08 | Radix Popoverの開閉状態と位置調整 | [025](https://www.radix-ui.com/primitives/docs/overview/getting-started) |
| <a name="i-09"></a>I-09 | ARIA・フォーカス・キーボード操作をRadixが担う範囲 | [026](https://www.radix-ui.com/primitives/docs/overview/accessibility) |
| <a name="i-10"></a>I-10 | 標準外の操作部品にアクセシブルな名前を付ける方法 | [026](https://www.radix-ui.com/primitives/docs/overview/accessibility) |
| <a name="i-11"></a>I-11 | 確認ダイアログでキャンセルに初期フォーカスを置く理由 | [026](https://www.radix-ui.com/primitives/docs/overview/accessibility) |
| <a name="i-12"></a>I-12 | Tailwindのユーティリティで部品を組み立てる利点 | [027](https://tailwindcss.com/docs/styling-with-utility-classes) |
| <a name="i-13"></a>I-13 | インラインスタイルにはない状態・画面幅の指定 | [027](https://tailwindcss.com/docs/styling-with-utility-classes) |
| <a name="i-14"></a>I-14 | テーマ別のクラスを組み合わせ、反復を管理する方法 | [027](https://tailwindcss.com/docs/styling-with-utility-classes) |

## フォーム関連カスタム要素

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="i2-01"></a>I2-01 | カスタム要素が内部機能を取得できる条件 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-02"></a>I2-02 | ElementInternalsが提供する送信・検証・ラベルのAPI | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-03"></a>I2-03 | ElementInternalsからシャドウルートを得られる場合 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-04"></a>I2-04 | 送信用の値と復元用の値を設定する方法 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-05"></a>I2-05 | カスタム要素が送信または復元に渡せる値の型 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-06"></a>I2-06 | 入力の復元と自動補完で呼ばれるコールバック | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-07"></a>I2-07 | 表示上の入力と送信形式を別々に保存する用途 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-08"></a>I2-08 | カスタム要素の妥当性とエラー表示先の内部状態 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-09"></a>I2-09 | カスタム要素のエラーメッセージが取得できる条件 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-10"></a>I2-10 | 単一値と複数項目をフォームに追加する規則 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-11"></a>I2-11 | カスタム要素が既定のARIA属性を提供する方法 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-12"></a>I2-12 | attachInternalsを拒否する条件と初期化の手順 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-13"></a>I2-13 | ElementInternalsのshadowRoot判定順序 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-14"></a>I2-14 | FormDataを送信用または復元用に保存する際の複製 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-15"></a>I2-15 | setValidityの入力条件とエラー表示の参照先 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-16"></a>I2-16 | 妥当性メッセージの取得時に検査される要素の種類 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-17"></a>I2-17 | 項目名がないカスタムコントロールのフォーム送信 | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |
| <a name="i2-18"></a>I2-18 | ElementInternalsによる既定のARIAロールと上書き | [094](https://html.spec.whatwg.org/multipage/custom-elements.html#element-internals) |

## 独自状態の公開

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="i3-01"></a>I3-01 | 独自の状態をCSSへ公開する仕組み | [096](https://html.spec.whatwg.org/multipage/custom-elements.html#exposing-custom-element-states) |
| <a name="i3-02"></a>I3-02 | チェック状態を属性に映さずCSSから選ぶ例 | [096](https://html.spec.whatwg.org/multipage/custom-elements.html#exposing-custom-element-states) |
| <a name="i3-03"></a>I3-03 | 公開されたシャドウ部品を独自状態で選ぶ方法 | [096](https://html.spec.whatwg.org/multipage/custom-elements.html#exposing-custom-element-states) |
| <a name="i3-04"></a>I3-04 | カスタム状態の一覧を操作するメソッド | [097](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-state-pseudo-class) |
| <a name="i3-05"></a>I3-05 | カスタム要素の状態集合の初期値と型 | [097](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-state-pseudo-class) |
| <a name="i3-06"></a>I3-06 | 複数の排他的な状態をCSSに公開する方法 | [097](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-state-pseudo-class) |

## カスタム状態の CSS 選択

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="i4-01"></a>I4-01 | :stateが一致するカスタム要素の条件 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="i4-02"></a>I4-02 | カスタム状態の定義とCSS照合を引く場所 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) · [097](https://html.spec.whatwg.org/multipage/custom-elements.html#custom-state-pseudo-class) |
| <a name="i4-03"></a>I4-03 | Chromiumの旧カスタム状態構文から移行する方法 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) · [096](https://html.spec.whatwg.org/multipage/custom-elements.html#exposing-custom-element-states) · [X02](https://groups.google.com/a/chromium.org/g/blink-dev/c/LkeOaFI5xVc) · [X03](https://developer.chrome.com/release-notes/127) |
