# ライセンスと出典

本プロジェクトで作成した日本語の解説・確認表・索引、コード、サンプル画像・音源は、[MIT License](LICENSE) に従って利用、変更、再配布できます。複製や実質的な部分の再配布には著作権表示と許諾文を含めてください。各作例に取り入れた外部コードと書体の出典も以下に記載しています。

## テンプレートの来歴

| ファイル | 実装と同梱物 | 適用ライセンス |
| --- | --- | --- |
| `dialog.html` | HTML の dialog と form による確認操作 | MIT |
| `form.html` | 登録と下書きで異なる検証を試すフォーム | MIT |
| `skip-link.html` | 文書内リンクで本文へ移る例 | MIT |
| `theme.html` | CSS の色設定とブラウザー標準の選択部品 | MIT |
| `motion.html` | 取り置き状態と動きの設定に応じた CSS | MIT |
| `view-transition.html` | 並べ替え時の遷移と即時更新の分岐 | MIT |
| `carousel.html` | 手動移動・自動送り・停止の状態管理 | MIT |
| `virtual-list.html` | 単一行の高さを基にした可視範囲の計算と全件表示 | MIT |
| `optimistic.html` | 非同期保存の模擬処理と失敗時の復元 | MIT |
| `responsive-image.html`, `assets/circulation-240.png`, `assets/circulation-480.png` | 架空の貸出冊数を使って生成した棒グラフと、それを表示する HTML | MIT |
| `mcp-summary.html` | 公開プロトコルに基づく件数表示。ブラウザーのメッセージ API を使用 | MIT |

`templates/` の11例はブラウザーの標準機能で実装しています。図はサンプル用に作成したものです。

## 作例「潮待ち映画祭」

[単体HTML](examples/shiomachi-film/index.html) のHTML・CSS・JavaScript、映画祭と上映作品の文章、港と映画の場面画像、およびREADMEの画面見本は、このプロジェクトの [MIT License](LICENSE) で配布します。HTMLのソース内の `project-license` に著作権表示と許諾文を収録しています。

HTMLには次の書体を、作例に使う文字に絞ったWOFF2として埋め込んでいます。各書体には [SIL Open Font License 1.1](https://openfontlicense.org/open-font-license-official-text/) が適用されます。各配布元の著作権表示とライセンス全文は同じHTMLの `font-licenses` に収録しています。

| 書体 | 作例での使用箇所 | 配布元のライセンス |
| --- | --- | --- |
| Shippori Mincho B1 | 映画祭名と和文の見出し | [Google Fonts · Shippori Mincho B1](https://github.com/google/fonts/blob/main/ofl/shipporiminchob1/OFL.txt) |
| Cormorant Garamond | 欧文の副題 | [Google Fonts · Cormorant Garamond](https://github.com/google/fonts/blob/main/ofl/cormorantgaramond/OFL.txt) |
| Noto Sans JP | 上映時刻、作品情報、本文 | [Google Fonts · Noto Sans JP](https://github.com/google/fonts/blob/main/ofl/notosansjp/OFL.txt) |

## 作例「DEAD AIR FM」

[単体HTML](examples/dead-air-fm/index.html) には、HTML・CSS・JavaScript、MOSS-Imageで生成したイラスト、各局のためにYuE2（YuE2-3B・YuE2-VAE）で生成した3曲を収めています。曲名は「Midnight Circuit」「Ghost Relay」「Chrome Rush」です。このプロジェクトのコード、画像、音源は [MIT License](LICENSE) で配布します。[MOSS-Imageの配布元](https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT)・[YuE2の配布元と生成物に関する条件](https://huggingface.co/m-a-p/YuE2-3B/blob/main/LICENSE)

選局時の数字の切り替えや波形の描画には [Motion Atlas](https://github.com/RNA4219/motion-atlas) のコードを使用しています。HTMLの `project-license` には本プロジェクトのMITライセンス、`third-party-notices` にはMotion AtlasのMITライセンスと各書体の著作権表示・ライセンス全文を収録しています。

| 埋め込んだ書体 | 使用箇所 | 配布元のライセンス |
| --- | --- | --- |
| Archivo Black | 局名・番組名 | [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/archivoblack/OFL.txt) |
| Space Mono | 周波数・時刻 | [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/spacemono/OFL.txt) |
| Noto Sans JP | 日本語の案内・ボタン | [SIL OFL 1.1](https://github.com/google/fonts/blob/main/ofl/notosansjp/OFL.txt) |

## リンク先の資料

出典番号は参照先を識別するためのものです。[出典一覧](sources.md)の文書や論文には各権利者の条件が適用されます。このパッケージの MIT License が、それらの転載・翻訳・再配布の許諾を与えることはありません。PDF を指すリンクは各掲載元に移動します。製品名、仕様名、API 名は参照先を特定するために記載しています。
