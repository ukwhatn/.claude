# アーキテクチャとハイドレーション

表示に必要な処理をサーバーとクライアントのどちらで行うか決める。フレームワーク固有のキャッシュや配信条件は、その製品の資料で確認する。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## アイランドの考え方

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="l1-01"></a>L1-01 | 静的 HTML でページを届け、対話が必要な部分だけに JavaScript を読み込む。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-02"></a>L1-02 | コンポーネントを島に見立てる構成が提唱された経緯。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-03"></a>L1-03 | ページの一部分だけを有効化するハイドレーション方式との関係。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-04"></a>L1-04 | Astro がこの設計をフレームワークの機能として採用した経緯。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-05"></a>L1-05 | ブラウザーで動く島と、サーバーで個別に描画する島の用途を区別する。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-06"></a>L1-06 | 静的ページの中に、対話が必要なウィジェットを組み込む。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-07"></a>L1-07 | 別々に初期化される部品も、必要に応じて状態共有や通信ができる。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-08"></a>L1-08 | Astro の既定でクライアントに JavaScript が送られる範囲を確認する。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-09"></a>L1-09 | 対話部分にだけディレクティブを指定して、ブラウザーで動作させる。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-10"></a>L1-10 | 優先度の低い部品を待たずに、重要な部品の読み込みを進める。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-11"></a>L1-11 | ブラウザーでの初期化が必要な部品を明示して、転送するコードを抑える。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-12"></a>L1-12 | 時間がかかるサーバー処理をページ本体の描画から分離する。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-13"></a>L1-13 | 個別化した部分の準備中でも、ページ本体と代替表示を先に届ける。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-14"></a>L1-14 | 動的な部分を分離することで、共通部分をキャッシュできる範囲を広げる。 | [127](https://docs.astro.build/en/concepts/islands/) |
| <a name="l1-15"></a>L1-15 | 発案者の回顧から、島の設計が最初に説明された背景を確認する。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-16"></a>L1-16 | 独立した動的部品を差し込む位置を、サーバーが返す HTML に用意する。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-17"></a>L1-17 | マイクロフロントエンドとの違いを、HTML による合成方法から確認する。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-18"></a>L1-18 | 個々の部品を必要な時期に読み込み、順次有効化する考え方。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-19"></a>L1-19 | 独立した部品の初期化を、外側のルートの初期化完了まで待たせない。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-20"></a>L1-20 | 画面が見えてから操作できるまでの待ち時間も測る。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-21"></a>L1-21 | サーバー応答の HTML だけで、要求された情報をすぐ読めるようにする。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-22"></a>L1-22 | JavaScript がまだ動かなくても、記事本文など主目的の情報を表示する。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-23"></a>L1-23 | 通常の HTML リンクを使い、支援技術やクローラーにも遷移先を示す。 | [128](https://jasonformat.com/islands-architecture/) |
| <a name="l1-24"></a>L1-24 | 独立配信できる部品に分ける価値と、先に設計する負担を見比べる。 | [128](https://jasonformat.com/islands-architecture/) |

## レンダリングの場所と時機

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="l2-01"></a>L2-01 | Astro のビルド時生成を前提とし、リクエスト時描画が必要なページを選ぶ。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-02"></a>L2-02 | 訪問者の状態や最新データが必要なページを、リクエストごとに描画する。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-03"></a>L2-03 | 動的描画を使う場合は、配信環境に対応するアダプターを用意する。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-04"></a>L2-04 | サイト全体を静的配信しつつ、必要なルートだけビルド時生成から外す。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-05"></a>L2-05 | 動的なルートが多いときはサーバー描画を既定にし、静的な例外を指定する。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-06"></a>L2-06 | サーバーで描画できた HTML を順次送ると、全体の準備を待たずに表示できる。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-07"></a>L2-07 | リクエスト時に描画するページや API で Cookie を読み書きする方法。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-08"></a>L2-08 | Astro で応答ステータスとキャッシュなどのヘッダーを設定する。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-09"></a>L2-09 | 静的生成とリクエスト時描画で、利用できるリクエスト情報を確認する。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-10"></a>L2-10 | サーバー処理を公開する API ルートの定義方法。 | [129](https://docs.astro.build/en/guides/on-demand-rendering/) |
| <a name="l2-11"></a>L2-11 | ルート単位で静的配信と動的描画を分ける構成と、その配信上の利点。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-12"></a>L2-12 | 一つのページで静的な骨格と後から届く動的領域を共存させる。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-13"></a>L2-13 | 部分的な事前描画、部品単位のキャッシュ、再検証を組み合わせる考え方。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-14"></a>L2-14 | 初期表示を早める利点に加え、部品ごとの更新やキャッシュ範囲を検討する。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-15"></a>L2-15 | ビルド時生成だけで済む場合は、静的配信で実行サーバーを省ける。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-16"></a>L2-16 | ルート単位の設計では、動的なルートにだけ実行サーバーが必要になる。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-17"></a>L2-17 | 部品単位の設計では、動的部分を配信しつつ同じ応答内の静的部分を活かす。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-18"></a>L2-18 | 部分配信を支えるストリーミングと、複数インスタンスのキャッシュ調整。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-19"></a>L2-19 | 配信基盤の機能を、段階表示やキャッシュ整合性の要件に照らす。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-20"></a>L2-20 | 単一プロセスの構成から複数インスタンスへ移す際に追加で必要な機能。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-21"></a>L2-21 | 配信環境による対応状況を、アダプターのテストと運用上の性能に分けて確認する。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |
| <a name="l2-22"></a>L2-22 | CDN の機能が揃っていても、事前描画の再開まで処理できるか個別に確認する。 | [130](https://nextjs.org/docs/app/guides/rendering-philosophy) |

## JavaScript の処理とハイドレーション

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="l3-01"></a>L3-01 | V8 の2019年の分析では、ダウンロードと実行が JavaScript の主要コストだった。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-02"></a>L3-02 | 配信量、長いタスク、インラインスクリプトを見直す当時の推奨。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-03"></a>L3-03 | 通信や CPU に余裕のない端末で、大きすぎるバンドルを分割する。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-04"></a>L3-04 | 長い実行タスクと大きなインラインスクリプトが初期化へ与える影響。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-05"></a>L3-05 | 同じページでも回線速度と端末性能のどちらが待ち時間を支配するか測る。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-06"></a>L3-06 | 当時の事例でページの読み込み時間に占めた JavaScript 実行負荷。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-07"></a>L3-07 | 低性能のモバイル端末で処理がどれだけ遅くなるか測った比較例。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-08"></a>L3-08 | メインスレッドを占有する長いタスクを分け、重要な処理を先に進める。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-09"></a>L3-09 | 解析やコンパイルの並列化がメインスレッドの負荷を下げた経緯。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-10"></a>L3-10 | 外部スクリプトの解析開始と、HTML パーサーが待つ条件を確認する。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-11"></a>L3-11 | 大量のデータを JavaScript リテラルと JSON のどちらで渡すか、解析負荷を比べる。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-12"></a>L3-12 | 大きなオブジェクトリテラルは複数回の解析対象になり得る。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-13"></a>L3-13 | 再訪時にファイルキャッシュと V8 のコンパイル結果が再利用される条件。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-14"></a>L3-14 | 転送量や実行負荷を抑え、メモリや電力に余裕のない端末も評価する。 | [131](https://v8.dev/blog/cost-of-javascript-2019) |
| <a name="l3-15"></a>L3-15 | サーバー描画後の対話の接続を、必要な部品と時期に絞る研究提案。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-16"></a>L3-16 | 一括で対話を接続すると、表示されてもイベントを処理できない時間が生じる。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-17"></a>L3-17 | 段階的・部分的なハイドレーションの先行事例と比較上の限界。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-18"></a>L3-18 | React と Next.js で描画と対話の接続を部品ごとに調整する研究構成。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-19"></a>L3-19 | 初期表示の速さと、実際に操作できるまでの時間を別々に測る。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-20"></a>L3-20 | 段階的ハイドレーションでは、部品が操作可能になる時期を分ける。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-21"></a>L3-21 | 静的な部品をハイドレーション対象から外し、クライアント側の実行量を減らす。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-22"></a>L3-22 | 端末や回線に応じて読み込み方法を変える考え方。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-23"></a>L3-23 | サーバーで段階配信する部品と、後で補う部品を分ける研究上の提案。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-24"></a>L3-24 | 部品の重要度と利用環境をもとに、対話を接続するタイミングを決める。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-25"></a>L3-25 | 表示範囲への進入、初回操作、空き時間などの開始条件を選ぶ。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-26"></a>L3-26 | 複数の部品の初期化条件を、一つのクライアント処理で管理する研究例。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-27"></a>L3-27 | 接続状態などのブラウザー情報を使う場合の判断基準を確認する。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-28"></a>L3-28 | Server Components でそもそも転送しないコードと、遅らせるコードを分ける。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-29"></a>L3-29 | 表示速度と応答性に加えて、主要コンテンツが検索から見えるか確かめる。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-30"></a>L3-30 | 単一の商品詳細ページで、一括初期化と優先度付き初期化を比べた実験条件。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-31"></a>L3-31 | 比較実験での転送量と読み込み指標の差を、単一ページの計測結果として読む。 | [132](https://arxiv.org/abs/2504.03884) |
| <a name="l3-32"></a>L3-32 | 対象ページ、端末、回線条件が限られており、他の製品では再計測が必要。 | [132](https://arxiv.org/abs/2504.03884) |

## Astro のアイランド実装

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="l4-01"></a>L4-01 | Astro で他のフレームワークの部品を使う場合も、既定はサーバー描画。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-02"></a>L4-02 | クライアント側の JavaScript が必要な部品をディレクティブで指定する。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-03"></a>L4-03 | 初期読み込み、表示範囲、メディア条件などに応じて有効化の時期を選ぶ。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-04"></a>L4-04 | 複数の UI フレームワークを使うときは、各部品とともに送られるランタイムを確認する。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-05"></a>L4-05 | 操作に必須のアクセシビリティ機能が、有効化を待っている間にも使えるか確認する。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-06"></a>L4-06 | 混在するフレームワークを、ファイルの扱いと統合設定で識別する。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-07"></a>L4-07 | ブラウザーへ送る部品の props は、転送できるデータに絞る。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-08"></a>L4-08 | 子要素と名前付きスロットを受け取る書き方を、部品側のフレームワークに合わせる。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-09"></a>L4-09 | 部品を入れ子にする場合の、異なるフレームワークとコールバックの制約。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-10"></a>L4-10 | クライアントで動く部品と、サーバーで HTML を作る Astro 部品の境界。 | [134](https://docs.astro.build/en/guides/framework-components/) |
| <a name="l4-11"></a>L4-11 | 個別化された情報をサーバーで遅延描画し、共通のページ本体を先に届ける。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-12"></a>L4-12 | 描画を後回しにした部品は、準備中に代替内容を表示できる。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-13"></a>L4-13 | サーバーで個別描画する部品もデータ取得や Cookie の参照ができる。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-14"></a>L4-14 | サーバーで個別描画する部品に渡す値は転送できる形式にする。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-15"></a>L4-15 | 遅延部品が読み込まれるまで、意味のある代替表示を出す。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-16"></a>L4-16 | ビルド時に、遅延部品を要求する小さなスクリプトが用意される。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-17"></a>L4-17 | 遅延部品の HTML は、それぞれのエンドポイントから取得される。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-18"></a>L4-18 | Astro の参照ガイドでは、クエリ込みの URL 全体が2,048バイトを超えると GET から POST に切り替わる。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-19"></a>L4-19 | 専用リクエストで描画する部品は、元ページの URL を直接参照できない場合がある。 | [135](https://docs.astro.build/en/guides/server-islands/) |
| <a name="l4-20"></a>L4-20 | ビルドが切り替わっても遅延部品を取得できるよう、暗号化キーの共有条件を確認する。 | [135](https://docs.astro.build/en/guides/server-islands/) |
