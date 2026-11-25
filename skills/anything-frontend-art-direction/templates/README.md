# 実装例

各 HTML を保存した状態でブラウザーから開いてください。パッケージのインストールやビルドは不要です。MCP Apps の結果受信には対応ホストが必要です。操作や入力に使うデータは例示用です。

| テンプレート | 試すこと | 根拠 |
| --- | --- | --- |
| [ダイアログ](dialog.html) | 開いた直後のフォーカス、Esc、確定ボタン、閉じた後の戻り先を順に確認する。 | [E2-05](../references/e-accessibility.md#e2-05) |
| [フォーム](form.html) | 人数が空のときは登録が止まり、下書きは受け付けられる。1〜8人で登録を再試行する。 | [G7-05](../references/g-state-forms.md#g7-05) |
| [本文への移動](skip-link.html) | 最初の Tab でリンクを表示し、Enter で本文へ移動する。 | [E4-04](../references/e-accessibility.md#e4-04) |
| [配色](theme.html) | ライト・ダークを切り替え、端末に合わせる設定に戻す。ブラウザー標準の入力部品も確認する。 | [B3-07](../references/b-visual.md#b3-07) |
| [状態とモーション](motion.html) | 取り置きを切り替える。端末で動きを減らすと、状態の説明だけが変わる。 | [E3-08](../references/e-accessibility.md#e3-08) |
| [画面切り替え](view-transition.html) | 一覧の順序を逆にする。API が使えない場合や動きを減らす設定では即時に並べ替える。 | [H-06](../references/h-graphics.md#h-06)・[E3-08](../references/e-accessibility.md#e3-08) |
| [カルーセル](carousel.html) | 前後への手動移動と自動送りを試す。自動送り中に Tab またはマウスで領域に入ると停止する。マウスを置いたまま開始を指定した場合は、領域から離れてから開始する。 | [E8-05](../references/e-accessibility.md#e8-05)・[E8-10](../references/e-accessibility.md#e8-10) |
| [仮想リスト](virtual-list.html) | 全1,000件の一行ラベルをスクロールする。可視領域の前後に余分な行を描いている。ページ内検索が必要なときは全件表示に切り替える。 | [F3-13](../references/f-performance.md#f3-13) |
| [楽観的更新](optimistic.html) | 保存失敗を選んでから追加する。即時に切り替わったボタンが、失敗時に最後に保存できた状態へ戻る。保存処理はページ内の模擬処理。 | [D-37](../references/d-interaction.md#d-37) |
| [レスポンシブ画像](responsive-image.html) | 画像の2種類の幅候補、レイアウトの確保、代替テキストを確認する。画像も同梱。 | [B4-03](../references/b-visual.md#b4-03)・[B4-07](../references/b-visual.md#b4-07)・[E7-14](../references/e-accessibility.md#e7-14) |
| [MCP Apps の結果表示](mcp-summary.html) | 単独で開くとホストが必要なことを表示する。埋め込み時はツールの結果から件数を受け取る。 | [J3-13](../references/j-apps.md#j3-13)・[仕様](../sources.md) |

## MCP Apps に組み込む

この例は UI 側の HTML です。対応する MCP サーバーで HTML を `ui://` リソースとして登録し、MIME 型を `text/html;profile=mcp-app` にします。ツール定義の `_meta.ui.resourceUri` に同じ URI を指定してください。ツール結果には非負整数の `structuredContent.count` を入れ、UI を表示できない利用者向けのテキストも返します。

HTML は 2026-01-26 版の初期化手順で親フレームと通信し、初期化を受け付けた親からの結果だけを画面に表示します。入力欄の値や利用者データを外部に送信する機能はありません。[MCP Apps 仕様](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx)

すべてのテンプレートとサンプル画像に [MIT License](../LICENSE) を適用します。[各例の来歴](../NOTICE.md)
