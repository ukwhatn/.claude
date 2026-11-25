# 描画とレイアウト

幅で崩れるか、画面更新のタイミングで崩れるかを先に切り分ける。CSS の適用条件とブラウザーの処理順は別々に追う。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## ブラウザーの描画工程

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="a-01"></a>A-01 | 画面のリフレッシュ間隔のうち、ページ側で使える時間はどのくらいか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-02"></a>A-02 | 連続アニメと単発の操作応答では、同じ時間目標で測るべきか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-03"></a>A-03 | 見た目の変化は、どの描画工程を通って画面に届くか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-04"></a>A-04 | 開発者ツールのペイント計測には、描画命令とピクセル化の両方が含まれるか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-05"></a>A-05 | 寸法、背景、合成レイヤーを動かす場合で、発生する処理はどう違うか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-06"></a>A-06 | 処理を速くする前に、そもそも省ける描画作業はないか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-07"></a>A-07 | 読み込み後の操作も含めて、反応の速さをどう評価するか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-08"></a>A-08 | 操作から見た目が変わるまでの間に、自前と外部のコードは何をしているか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-09"></a>A-09 | 視覚的な変化をCSSだけで表現できる場面はどこか | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-10"></a>A-10 | 親の寸法変更が子へ波及する範囲と、再描画される面を調べる | [017](https://web.dev/articles/rendering-performance) |
| <a name="a-11"></a>A-11 | 引っかかりや反応遅れを生む処理を、記録から切り分ける | [017](https://web.dev/articles/rendering-performance) |

## コンテナクエリ

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="a2-01"></a>A2-01 | コンテナクエリを調べるとき、どの仕様の版を起点にするか | [020](https://drafts.csswg.org/css-contain-3/) |
| <a name="a2-02"></a>A2-02 | 仕様移管の前後で、値や問い合わせの書き方が変わった箇所を探す | [020](https://drafts.csswg.org/css-contain-3/) |
| <a name="a2-03"></a>A2-03 | 部品の配置先に合わせる条件と、端末環境に合わせる条件を分ける | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-04"></a>A2-04 | サイズやスクロール状態を問い合わせるために、どの要素へ型を指定するか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-05"></a>A2-05 | 問い合わせ対象の型と名前は、軸ごとのコンテナ選択にどう関わるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-06"></a>A2-06 | 複数条件や入れ子の問い合わせで、どの祖先が選ばれるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-07"></a>A2-07 | コンテナの寸法が動くとき、問い合わせ結果はいつ更新されるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-08"></a>A2-08 | 後続要素や子孫の有無を、現在の要素の選択条件にできるか | [019](https://www.w3.org/TR/selectors-4/) |
| <a name="a2-09"></a>A2-09 | 関係を調べるセレクターに、別の関係条件や疑似要素を入れられるか | [019](https://www.w3.org/TR/selectors-4/) |
| <a name="a2-10"></a>A2-10 | 値や比較演算子を省いたコンテナ条件は何を調べるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-11"></a>A2-11 | サイズ条件の判定に必要なボックスと軸が存在するか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-12"></a>A2-12 | 条件式で参照する相対値や変数を、どの要素を基準に解決するか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-13"></a>A2-13 | 同じ条件式でも配置先によって実際のしきい値が変わる例を探す | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-14"></a>A2-14 | 幅と高さの判定に、余白や枠線が含まれるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-15"></a>A2-15 | 横書きと縦書きの双方に対応する寸法条件を選ぶ | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-16"></a>A2-16 | コンテナの縦横比や向きを、何から計算するか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-17"></a>A2-17 | 親のプロパティ値を条件に、部品の見た目を変えられるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-18"></a>A2-18 | 値あり、値なし、範囲比較の各スタイル条件を読み分ける | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-19"></a>A2-19 | 一括指定プロパティやカスケードに依存する値を条件にできるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-20"></a>A2-20 | スクロールさせる要素と、スクロールの影響を受ける要素を区別する | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-21"></a>A2-21 | スクロール状態が変わった結果を、どの描画サイクルで参照するか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-22"></a>A2-22 | sticky要素が軸上のどちらの端に寄っているかを判定する | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-23"></a>A2-23 | 現在または次のスナップ先かどうかを、軸ごとに調べる | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-24"></a>A2-24 | その方向にユーザー操作で到達できる隠れた領域があるか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-25"></a>A2-25 | 直近のスクロール方向を条件に使うとき、論理方向をどう読むか | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-26"></a>A2-26 | コンテナに比例する単位の使い分けを調べる | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-27"></a>A2-27 | 対象コンテナがないときの代替寸法と、軸ごとの参照先を確認する | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-28"></a>A2-28 | 長い機能判定を名前で参照する仕組みと、名前の衝突時に採用される定義を調べる | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-29"></a>A2-29 | 複数条件のコンテナルールをCSSOMから取り出して扱う | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-30"></a>A2-30 | 要素を基準にコンテナ条件をJavaScriptから確かめる | [021](https://drafts.csswg.org/css-conditional-5/) |
| <a name="a2-31"></a>A2-31 | コンテナ条件の文字列表現と、その時点の一致結果の違いを調べる | [021](https://drafts.csswg.org/css-conditional-5/) |

## イベントループ

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="a3-01"></a>A3-01 | ウィンドウ、ワーカー、ワークレットのうち、処理を進めるループを特定する | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-02"></a>A3-02 | タスクが登録された順と、実際に取り出される順の違いを調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-03"></a>A3-03 | イベント配送などを管理するタスクに、どんな情報が付随するか | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-04"></a>A3-04 | 実行中のタスクとマイクロタスクを、どの状態で区別するか | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-05"></a>A3-05 | タスクがどのキューに登録され、文書とどう関連付くかを追う | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-06"></a>A3-06 | 対象のグローバル環境を起点にタスクの行き先を特定する | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-07"></a>A3-07 | マイクロタスクが通常のタスクとは異なる列に入る仕組みを調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-08"></a>A3-08 | 別エージェントへ処理を渡す際、イベントループを推定できない理由を調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-09"></a>A3-09 | 実行可能なタスクの選択、マイクロタスク処理、長時間処理の計測を追う | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-10"></a>A3-10 | アイドル処理が次の描画やタイマーと競合する場合の締切を調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-11"></a>A3-11 | ワーカー側でフレームコールバックが実行される条件を確認する | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-12"></a>A3-12 | 描画の機会を検出してから描画タスクを登録するまでを追う | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-13"></a>A3-13 | 描画対象から非表示の文書や変化のない文書を除く条件を確認する | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-14"></a>A3-14 | Canvas 2D の contextlost がキャンセルされると復元手順は中止される。通知の順序も確認する。 | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-15"></a>A3-15 | スタイル計算とサイズ変化の通知が反復する条件を調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-16"></a>A3-16 | 描画の機会が固定間隔にならない理由を調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-17"></a>A3-17 | マイクロタスクを処理し終えるまでの流れと再入時の保護を確認する | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-18"></a>A3-18 | 並行処理が同期的に進める時点まで待つ仕組みを調べる | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-19"></a>A3-19 | 進行中の処理がイベントループへ一時的に制御を返す挙動を追う | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-20"></a>A3-20 | 同期的な待機が発生した場合に、止まる処理を見分ける | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
| <a name="a3-21"></a>A3-21 | 入力イベントとDOM操作で、タスクの登録先をどう使い分けるか | [114](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) |
