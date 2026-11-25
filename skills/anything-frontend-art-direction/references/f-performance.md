# 性能と配信

遅い場所を、入力への応答、主要コンテンツの表示、レイアウトの変化のいずれかに絞る。その後、計測条件と対処を結び付ける。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## 利用者側で測る性能

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="f-01"></a>F-01 | 読み込み速度、操作への応答、表示の安定性を Core Web Vitals で評価する。 | [004](https://web.dev/articles/vitals) |
| <a name="f-02"></a>F-02 | LCP は実測で 2.5 秒以内を目標にする。 | [004](https://web.dev/articles/vitals) |
| <a name="f-03"></a>F-03 | INP は実測で 200 ミリ秒以下を目標にする。 | [004](https://web.dev/articles/vitals) |
| <a name="f-04"></a>F-04 | CLS は実測で 0.1 以下を目標にする。 | [004](https://web.dev/articles/vitals) |
| <a name="f-05"></a>F-05 | モバイルとデスクトップを分け、各指標の75パーセンタイルを見る。 | [004](https://web.dev/articles/vitals) |
| <a name="f-06"></a>F-06 | Core Web Vitals の公開段階と FID から INP への移行経緯。 | [004](https://web.dev/articles/vitals) |
| <a name="f-07"></a>F-07 | web-vitals を使い、訪問の75%以上で目標値を満たすか確かめる。 | [004](https://web.dev/articles/vitals) |
| <a name="f-08"></a>F-08 | 操作なしのラボ測定では INP が得られない。TBT は診断の補助に使える。 | [004](https://web.dev/articles/vitals) |
| <a name="f-09"></a>F-09 | 指標の定義や閾値が変わる場合の公開方針。 | [004](https://web.dev/articles/vitals) |

## 主要な性能指標

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="f2-01"></a>F2-01 | INP は訪問中の操作から、次のフレームを表示できるまでの遅れを評価する。 | [049](https://web.dev/articles/inp) |
| <a name="f2-02"></a>F2-02 | INP の遅い操作の選び方と、ページビュー間での75パーセンタイル集計。 | [049](https://web.dev/articles/inp) |
| <a name="f2-03"></a>F2-03 | 一回のタップが複数のイベントを起こしても、論理的には一つの操作として扱う。 | [049](https://web.dev/articles/inp) |
| <a name="f2-04"></a>F2-04 | INP の良好・要改善・不良の境界を端末別の実測で適用する。 | [049](https://web.dev/articles/inp) |
| <a name="f2-05"></a>F2-05 | クリック、タップ、キー操作が対象。iframe 内の操作は計測方法によって観測範囲が異なる。 | [049](https://web.dev/articles/inp) |
| <a name="f2-06"></a>F2-06 | 入力待ち、処理、描画待ちのどこで操作が遅れているか分けて調べる。 | [049](https://web.dev/articles/inp) |
| <a name="f2-07"></a>F2-07 | FID は最初の入力待ち、INP は訪問中の操作から次の描画までを対象にする。 | [049](https://web.dev/articles/inp) |
| <a name="f2-08"></a>F2-08 | Event Timing の記録しきい値、ページ復元、iframe を考慮した INP の計測。 | [049](https://web.dev/articles/inp) |
| <a name="f2-09"></a>F2-09 | LCP で主要な可視コンテンツが描画された時点を確認する。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-10"></a>F2-10 | 端末別の実測 LCP で、75パーセンタイルが2.5秒以下かを見る。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-11"></a>F2-11 | 画像、動画、背景画像、テキストが LCP 候補になる条件を確かめる。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-12"></a>F2-12 | 透明要素やプレースホルダーが Chromium の LCP 候補から外れる場合。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-13"></a>F2-13 | LCP の面積にはビューポート内の可視部分を使い、余白や枠は含めない。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-14"></a>F2-14 | 後からより大きい候補が描画されるため、分析には最後の LCP 候補を採用する。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-15"></a>F2-15 | クロスオリジン画像の描画時刻と Timing-Allow-Origin の関係を確認する。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-16"></a>F2-16 | バックグラウンド、復元、iframe、事前レンダリング時の LCP 集計方法。 | [050](https://web.dev/articles/lcp) |
| <a name="f2-17"></a>F2-17 | CLS は連続する予期しないずれのうち、合計スコアが最大の区間で決まる。 | [051](https://web.dev/articles/cls) |
| <a name="f2-18"></a>F2-18 | 要素の追加やサイズ変更で、既存の可視要素まで移動したか確認する。 | [051](https://web.dev/articles/cls) |
| <a name="f2-19"></a>F2-19 | CLS の各シフトは影響を受けた画面面積と移動距離の両方で評価する。 | [051](https://web.dev/articles/cls) |
| <a name="f2-20"></a>F2-20 | 読み込みが長引く操作では、最終結果の領域を早めに確保する。 | [051](https://web.dev/articles/cls) |
| <a name="f2-21"></a>F2-21 | 配置を変えずに動かすなら transform を検討し、減動設定を尊重する。 | [051](https://web.dev/articles/cls) |
| <a name="f2-22"></a>F2-22 | CLS の集計ではバックグラウンド、復元、iframe を個別に考慮する。 | [051](https://web.dev/articles/cls) |

## リストの仮想化

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="f3-01"></a>F3-01 | TanStack Virtual は描画する項目を選ぶ仕組みを提供し、HTML とスタイルは利用側で決める。 | [057](https://raw.githubusercontent.com/TanStack/virtual/main/docs/introduction.md) |
| <a name="f3-02"></a>F3-02 | 縦横のリスト、グリッド、チャットのような末尾基準リストの構成を選ぶ。 | [057](https://raw.githubusercontent.com/TanStack/virtual/main/docs/introduction.md) |
| <a name="f3-03"></a>F3-03 | 仮想化の設定に項目数、スクロール要素、サイズの見積もりを渡す。 | [057](https://raw.githubusercontent.com/TanStack/virtual/main/docs/introduction.md) |
| <a name="f3-04"></a>F3-04 | スクロール領域と全体寸法を用意し、各項目を計算位置に描画する。 | [057](https://raw.githubusercontent.com/TanStack/virtual/main/docs/introduction.md) |
| <a name="f3-05"></a>F3-05 | 要素スクロールとウィンドウスクロールで、必要な設定を確認する。 | [058](https://raw.githubusercontent.com/TanStack/virtual/main/docs/framework/react/react-virtual.md) |
| <a name="f3-06"></a>F3-06 | スクロール中に同期更新が必要か、性能と見た目の許容差で判断する。 | [058](https://raw.githubusercontent.com/TanStack/virtual/main/docs/framework/react/react-virtual.md) |
| <a name="f3-07"></a>F3-07 | DOM 直接更新では主軸位置と内側コンテナの寸法をライブラリに任せる。 | [058](https://raw.githubusercontent.com/TanStack/virtual/main/docs/framework/react/react-virtual.md) |
| <a name="f3-08"></a>F3-08 | transform 方式と位置指定方式を選ぶときは固定配置の子要素への影響を見る。 | [058](https://raw.githubusercontent.com/TanStack/virtual/main/docs/framework/react/react-virtual.md) |
| <a name="f3-09"></a>F3-09 | 項目数、スクロール先、サイズ推定が揃っているか確認する。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-10"></a>F3-10 | 表示後に高さや幅を測るなら、事前の推定を小さくしすぎない。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-11"></a>F3-11 | 画面外に追加描画する量は、スクロール時の空白と描画負荷を見て調整する。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-12"></a>F3-12 | 挿入や並べ替えがあるリストには、項目の安定した一意キーを使う。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-13"></a>F3-13 | 固定ヘッダーなどを描画範囲に追加する際は既定の先読み範囲も意識する。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-14"></a>F3-14 | 実寸計測に使う要素へインデックスを設定し、計測用の参照を渡す。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-15"></a>F3-15 | 同じ項目に手動サイズ設定と自動計測を重ねない。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-16"></a>F3-16 | 実寸が判明するたびに仮想リスト全体の寸法が変わり得る。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-17"></a>F3-17 | 滑らかな移動では、目的位置から離れた項目の再計測によるずれを避ける。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-18"></a>F3-18 | スクロール復元にはオフセットと計測済み項目の情報を保存する。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-19"></a>F3-19 | 同じピクセル位置への復元でも、手前の項目が変わると見える項目は変わり得る。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-20"></a>F3-20 | 追記時は直前まで末尾を読んでいた人だけを新しい末尾に追従させる。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |
| <a name="f3-21"></a>F3-21 | スクロール停止の検出にネイティブイベントと時間待ちのどちらを用いるか確認する。 | [059](https://raw.githubusercontent.com/TanStack/virtual/main/docs/api/virtualizer.md) |

## ストリーミング配信

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="f4-01"></a>F4-01 | React の Web Streams 向けサーバーレンダリング API と実行環境ごとの使い分け。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-02"></a>F4-02 | 起動スクリプト、モジュール、キャッシュなど、配信側から渡せる設定。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-03"></a>F4-03 | ストリームのヘッダー上限、名前空間、CSP nonce を指定する場所。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-04"></a>F4-04 | サーバーエラーとリソースヒントを扱うコールバック。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-05"></a>F4-05 | 最初の HTML が描画できた時点と全体が準備できた時点を区別する。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-06"></a>F4-06 | 同じ React ツリーをサーバーで描画し、クライアントで再接続する。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-07"></a>F4-07 | ビルドで決まるアセット URL を取得し、サーバー描画とクライアントでそろえる。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-08"></a>F4-08 | 遅い部分を Suspense で囲み、先にページ骨格を届ける。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-09"></a>F4-09 | 最初の HTML に残す骨格を決める。React が shell と呼ぶのはすべての Suspense 境界の外側。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream#specifying-what-goes-into-the-shell) |
| <a name="f4-10"></a>F4-10 | 回復可能な失敗を含め、サーバー側の描画エラーを記録する。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-11"></a>F4-11 | 初期 HTML の生成に失敗した場合の代替応答を用意する。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-12"></a>F4-12 | 境界内の描画に失敗した場合は読み込み表示を送り、クライアントで再試行する。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-13"></a>F4-13 | 初期レスポンスを送る前に HTTP ステータスを決める。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-14"></a>F4-14 | 見つからない文書とサーバー障害に対して異なる応答を返す。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-15"></a>F4-15 | 静的生成などで全体の完了を待つ場合、段階的な配信は行われない。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream) |
| <a name="f4-16"></a>F4-16 | 中断には AbortController を使う。描画時に signal を渡し、期限に達したらコントローラーの abort() を呼ぶ。 | [116](https://react.dev/reference/react-dom/server/renderToReadableStream#aborting-server-rendering) |

## バンドルと事前キャッシュ

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="f5-01"></a>F5-01 | コード分割で初期実行に必要なコードと後から使うコードを分ける。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-02"></a>F5-02 | 入口を手動で分ける場合、複数バンドルへの依存モジュールの重複を調べる。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-03"></a>F5-03 | 複数エントリーで共有する依存と実行時コードの扱いを設定する。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-04"></a>F5-04 | 共通依存を共有チャンクに抽出する設定を確認する。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-05"></a>F5-05 | 操作後に必要な機能を動的 import で読み込む。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-06"></a>F5-06 | CommonJS モジュールを動的に読み込むときの既定エクスポートの参照方法。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-07"></a>F5-07 | 分割ファイルの読み込み失敗ではネットワークやスクリプトのエラーも確認する。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-08"></a>F5-08 | 現在の画面に必要な先読みと、次に使いそうなファイルの取得を区別する。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-09"></a>F5-09 | ビルド結果を分析し、モジュールが意図したバンドルに入ったか確かめる。 | [119](https://webpack.js.org/guides/code-splitting/) |
| <a name="f5-10"></a>F5-10 | Service Worker のインストール時にオフラインで必要なファイルを用意する。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-11"></a>F5-11 | 既にバージョン付きの URL と、ビルド時にリビジョンを付ける URL を区別する。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-12"></a>F5-12 | 再訪時には更新分をインストール時に取得し、キャッシュの整理は有効化時に行う。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-13"></a>F5-13 | 事前キャッシュのルートを登録する順序と、キャッシュ欠落時の扱い。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-14"></a>F5-14 | URL が既に内容を特定できるアセットと、別途リビジョンを要する HTML を分ける。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-15"></a>F5-15 | 変更を検出できるようにビルド時に事前キャッシュ一覧を生成する。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-16"></a>F5-16 | クエリや末尾スラッシュが付いた URL が、事前キャッシュにどう照合されるか確認する。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-17"></a>F5-17 | キャッシュの追加とライフサイクルを自分で組み立てる場合の PrecacheController。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-18"></a>F5-18 | 事前キャッシュ済みの応答を直接取得するときは対応するキャッシュキーを引く。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-19"></a>F5-19 | Workbox の移行時に互換性を失った旧キャッシュを片付ける。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
| <a name="f5-20"></a>F5-20 | 配信ファイルの完全性検証に失敗した場合のキャッシュ投入時の挙動。 | [120](https://developer.chrome.com/docs/workbox/modules/workbox-precaching/) |
