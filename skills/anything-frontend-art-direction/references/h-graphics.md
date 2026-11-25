# グラフィックスとアニメーション

何を描くか、時間がどう進むか、途中で止まると何が通知されるかを個別に確かめる。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## 画面の切り替え

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h-01"></a>H-01 | 切り替え前後の画面の関係を伝える遷移 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-02"></a>H-02 | 新旧DOMを同時に出す遷移が抱える操作上の課題 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-03"></a>H-03 | 遷移中に描画される旧画像と新状態 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-04"></a>H-04 | 遷移のレイヤーと要素名による対応付け | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-05"></a>H-05 | 遷移の擬似要素にアニメーションを設定できる時点 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-06"></a>H-06 | 演出を作れなかった場合のDOM更新 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-07"></a>H-07 | 画面遷移の演出が支援技術や入力に及ぼす影響 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-08"></a>H-08 | 既定の遷移がレイアウトを使う理由と性能 | [014](https://raw.githubusercontent.com/WICG/view-transitions/main/explainer.md) |
| <a name="h-09"></a>H-09 | 同一文書と文書間の遷移に使うAPI | [015](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API) |
| <a name="h-10"></a>H-10 | 初回描画をそろえるリンクと遷移用CSS | [015](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API) |
| <a name="h-11"></a>H-11 | 複数のアニメーション機構を説明する共通モデル | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h-12"></a>H-12 | 時刻から進捗、進捗からスタイルを求める順序 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h-13"></a>H-13 | 反復時間と遅延から終了時刻を求める方法 | [016](https://drafts.csswg.org/web-animations-1/) |

## アニメーションの時間計算

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h2-01"></a>H2-01 | 時刻だけで効果を再計算できる性質 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-02"></a>H2-02 | ローカル時刻から反復内の時刻への変換 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-03"></a>H2-03 | アニメ効果が再生される区間の始点と長さ | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-04"></a>H2-04 | 終了後の遅延が次の効果に与える意味 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-05"></a>H2-05 | 再生範囲の前・中・後を判別する条件 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-06"></a>H2-06 | 再生範囲外のスタイルを扱うfill指定 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-07"></a>H2-07 | fillを使い続けず最終スタイルに反映する理由 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-08"></a>H2-08 | 一回の反復と全反復に要する時間 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-09"></a>H2-09 | 反復回数と先頭を途中から始める設定 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-10"></a>H2-10 | 区間が切り替わる境界とfillでの例外 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-11"></a>H2-11 | 順再生・逆再生・交互再生の指定 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-12"></a>H2-12 | 反復全体とキーフレーム区間のイージング | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-13"></a>H2-13 | 各種の時刻と進捗が求まる順序 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-14"></a>H2-14 | 開始前・終了後に計算するアクティブ時刻 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-15"></a>H2-15 | 端数を含む全体の反復進捗 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-16"></a>H2-16 | 一回分の進捗と終点の特殊な扱い | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-17"></a>H2-17 | 現在の反復番号の計算 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-18"></a>H2-18 | 再生方向を進捗に反映する計算 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-19"></a>H2-19 | 進捗にイージングを適用する際の境界 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h2-20"></a>H2-20 | 確定した進捗からプロパティの値を決める段階 | [016](https://drafts.csswg.org/web-animations-1/) |

## Canvas・WebGL・WebGPU

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h3-01"></a>H3-01 | canvasで二次元の絵を描く用途 | [066](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) |
| <a name="h3-02"></a>H3-02 | 描いた図を支援技術にも伝えるための代替 | [066](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) |
| <a name="h3-03"></a>H3-03 | canvasから描画コンテキストを取り出す手順 | [066](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) |
| <a name="h3-04"></a>H3-04 | 描画の仕様と上位ライブラリを選ぶ入口 | [066](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) |
| <a name="h3-05"></a>H3-05 | WebGLによるGPU描画と機器の対応条件 | [067](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) |
| <a name="h3-06"></a>H3-06 | WebGL 2で使える追加の描画機能 | [067](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) |
| <a name="h3-07"></a>H3-07 | WebGLのコンテキスト名とGPU側の制約 | [067](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) |
| <a name="h3-08"></a>H3-08 | WebGLが提供する低水準の描画操作 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-09"></a>H3-09 | 描画バッファの寸法・初期値・精度 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-10"></a>H3-10 | 高密度画面に合わせたcanvasの解像度 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-11"></a>H3-11 | WebGLコンテキスト作成時に選ぶ属性 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-12"></a>H3-12 | 描画結果の保持と読み出しで生じる負荷 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-13"></a>H3-13 | canvasをリサイズした後の描画範囲 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-14"></a>H3-14 | WebGLリソースが生存する条件と明示的な破棄 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-15"></a>H3-15 | GPUメモリの初期化と画像の出所に関する制約 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-16"></a>H3-16 | シェーダーで使える構文と長い描画の対策 | [068](https://registry.khronos.org/webgl/specs/latest/1.0/) |
| <a name="h3-17"></a>H3-17 | WebGPUで描画と汎用計算を行う用途 | [069](https://gpuweb.github.io/gpuweb/explainer/) |
| <a name="h3-18"></a>H3-18 | WebGPUが対象にするプラットフォームと設計目標 | [069](https://gpuweb.github.io/gpuweb/explainer/) |
| <a name="h3-19"></a>H3-19 | GPUに処理を渡す仕組みとメモリの見え方 | [069](https://gpuweb.github.io/gpuweb/explainer/) |
| <a name="h3-20"></a>H3-20 | アダプター選択・デバイス制約・非同期検証 | [069](https://gpuweb.github.io/gpuweb/explainer/) |
| <a name="h3-21"></a>H3-21 | WebGPUのデバイスにcanvasを接続する方法 | [069](https://gpuweb.github.io/gpuweb/explainer/) |

## SVG と座標系

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h4-01"></a>H4-01 | SVGで記述できる図形と文書構文 | [072](https://www.w3.org/TR/SVG2/intro.html) |
| <a name="h4-02"></a>H4-02 | SVGをアニメーションさせたり操作対象にしたりする方法 | [072](https://www.w3.org/TR/SVG2/intro.html) |
| <a name="h4-03"></a>H4-03 | 図のアクセシビリティと元データへの導線 | [072](https://www.w3.org/TR/SVG2/intro.html) |
| <a name="h4-04"></a>H4-04 | HTML・CSS・DOMからSVGを利用する方法 | [072](https://www.w3.org/TR/SVG2/intro.html) |
| <a name="h4-05"></a>H4-05 | SVGのビューポートとユーザー座標 | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-06"></a>H4-06 | viewBoxから移動量と倍率を計算する規則 | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-07"></a>H4-07 | viewBoxにゼロや負の寸法を指定した場合 | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-08"></a>H4-08 | SVGの縦横比を保って収めるか覆うか | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-09"></a>H4-09 | SVGの中で新たなビューポートを作る要素 | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-10"></a>H4-10 | SVG内の長さをパーセントで指定したときの基準 | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-11"></a>H4-11 | 拡大縮小で線幅を保つSVGプロパティ | [073](https://www.w3.org/TR/SVG2/coords.html) |
| <a name="h4-12"></a>H4-12 | SVGを画像として指定できる要素やCSS | [074](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image) |
| <a name="h4-13"></a>H4-13 | 画像として埋め込んだSVGの機能制限 | [074](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image) |

## 再生・停止・待機

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h5-01"></a>H5-01 | アニメーションが効果とタイムラインをつなぐ仕組み | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-02"></a>H5-02 | 再生位置が決まる条件と未確定になる条件 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-03"></a>H5-03 | 効果やタイムラインを差し替えたときの時刻 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-04"></a>H5-04 | currentTimeを変更して再生位置を移す処理 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-05"></a>H5-05 | startTimeの指定で変わる保留時刻 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-06"></a>H5-06 | 再生準備の完了を待つPromise | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-07"></a>H5-07 | 再生開始時に先頭や末尾へ戻る条件 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-08"></a>H5-08 | 一時停止した時点の位置を決める規則 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-09"></a>H5-09 | 再生の終点と範囲外に移動した場合 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-10"></a>H5-10 | 終了状態を更新して完了を通知する手順 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-11"></a>H5-11 | 保留中の ready を待っているときに cancel() を呼ぶと、その待機が棄却され得る。既に idle の場合と分けて追う。 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-12"></a>H5-12 | 再生速度ゼロと一時停止状態の違い | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-13"></a>H5-13 | 再生位置を飛ばさずに速度を変える方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-14"></a>H5-14 | 逆再生と再生状態を判定する順序 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h5-15"></a>H5-15 | アニメーションイベントを配信するキュー | [016](https://drafts.csswg.org/web-animations-1/) |

## キーフレームの合成

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h6-01"></a>H6-01 | 反復の進捗から効果の値を求める方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-02"></a>H6-02 | CSSプロパティによって異なる補間方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-03"></a>H6-03 | 登録されたカスタムプロパティの補間 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-04"></a>H6-04 | キーフレームが適用される要素や擬似要素 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-05"></a>H6-05 | キーフレームの位置・値・区間イージング | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-06"></a>H6-06 | キーフレーム値を解決する際の他のスタイルへの依存 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-07"></a>H6-07 | 位置未指定のキーフレームを等間隔に補う手順 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-08"></a>H6-08 | プロパティのキーフレームから効果値を求める方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-09"></a>H6-09 | 同じプロパティの複数の効果を重ねる仕組み | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-10"></a>H6-10 | CSSとAPIから作成した効果の重ね順 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-11"></a>H6-11 | 効果の順序を種類と作成順で決める規則 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-12"></a>H6-12 | 置換・加算・累積による効果の合成 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-13"></a>H6-13 | 置き換えられたアニメーションの自動除去 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-14"></a>H6-14 | 古いアニメーションが除去対象になる条件 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h6-15"></a>H6-15 | アニメーションが重ね合わせに与える副作用 | [016](https://drafts.csswg.org/web-animations-1/) |

## Web Animations API

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="h7-01"></a>H7-01 | 既存のアニメーションの調査と新規作成に使うAPI | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-02"></a>H7-02 | Animationの構築時に与える効果とタイムライン | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-03"></a>H7-03 | Animationを停止・完了・再生制御するメソッド | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-04"></a>H7-04 | 現在のアニメーション結果をインラインスタイルに残す方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-05"></a>H7-05 | 再生状態と置換状態の列挙値 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-06"></a>H7-06 | 指定したタイミングと計算済みタイミングの参照 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-07"></a>H7-07 | 遅延・反復回数・長さなどのタイミング設定 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-08"></a>H7-08 | 再生方向と区間外の効果を指定する列挙値 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-09"></a>H7-09 | タイミング設定を更新できない入力 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-10"></a>H7-10 | キーフレーム効果を作成・複製する方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-11"></a>H7-11 | 合成設定と解決済みキーフレームの参照 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-12"></a>H7-12 | アニメーションを生成する書き方の比較 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-13"></a>H7-13 | キーフレームを配列またはプロパティ別に渡す方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-14"></a>H7-14 | キーフレーム入力を正規化する手順 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-15"></a>H7-15 | 効果全体の合成と擬似要素の指定 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-16"></a>H7-16 | 効果とキーフレームで使える合成演算 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-17"></a>H7-17 | 要素をanimateで再生したときの効果とタイムライン | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-18"></a>H7-18 | 文書やシャドウルートのアニメーションを取得する方法 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-19"></a>H7-19 | 再生イベントに記録される二種類の時刻 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-20"></a>H7-20 | 変更をタイミング計算とスタイルに反映する規則 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-21"></a>H7-21 | メディアの時刻指定とアニメーションの連携 | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-22"></a>H7-22 | 仕様に記載されたプライバシー・セキュリティの扱い | [016](https://drafts.csswg.org/web-animations-1/) |
| <a name="h7-23"></a>H7-23 | 既存のCSSプロパティに対する補間方式の例外 | [016](https://drafts.csswg.org/web-animations-1/) |
