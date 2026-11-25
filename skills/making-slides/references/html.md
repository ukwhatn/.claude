# HTML（reveal.js）で作る

目次: 1 セットアップ / 2 構造 / 3 動きの作り方 / 4 動きを減らす設定 / 5 発表 / 6 PDF / 7 確認 / 8 既知の罠

## 1. セットアップ

デッキのディレクトリに `templates/html/` の中身を複製し、依存をインストールする。

```bash
cp -R <このスキルのディレクトリ>/templates/html/. <デッキのディレクトリ>/
cd <デッキのディレクトリ> && npm install
```

```
<デッキのディレクトリ>/
├── index.html      デッキ本体。reveal.js の初期化と数値の変化の処理を含む
├── theme.css       色・書体・余白。reveal.js の white テーマの上に重ねる
├── package.json    reveal.js・@fontsource/noto-sans-jp・playwright-core
└── node_modules/   会場へはこのディレクトリごと持っていく
```

- reveal.js と書体を node_modules から読む。CDN から読むと、オフラインの会場で表示できない
- `playwright-core` は PDF の出力（§6）だけに使う。ブラウザはシステムの Chrome を使うので、ブラウザのダウンロードは発生しない
- reveal.js の版はテンプレートの `package.json` で固定する。メジャーの版を上げるときは、§6 の印刷の手順が動くか確認する

## 2. 構造

- 1ページは `<div class="slides">` の中の `<section>` 1つ。縦に並べる子ページは `<section>` を入れ子にする（使うのは補足や付録を下に置くときだけ）
- 見出しは `<h1>` に主張の文を書く。注記は `<p class="note">`
- 発表者ノートは `<aside class="notes">`。`S` キーで発表者表示を開く
- 大きさは `Reveal.initialize` の `width: 1280, height: 720`。端の余白は `margin`（幅に対する割合）で取り、section に `padding` を付けない（印刷用の CSS が 0 にする）

## 3. 動きの作り方

主張に関係する変化（状態・順序・因果・同じものの移動）だけを動かす。規則は `references/visual.md` §6。

- 同じ要素がページをまたいで移る・大きさを変える
  - 使うもの: auto-animate
  - 書き方: 隣り合う2つの `<section data-auto-animate>` に、同じ `data-id` の要素を置く
- 1回の操作で1段階ずつ見せる
  - 使うもの: fragment
  - 書き方: 要素に `class="fragment"`（`fade-in`・`fade-up`・`highlight-blue` など）
- 段階に合わせて数値や図を動かす
  - 使うもの: fragment のイベント
  - 書き方: `Reveal.on("fragmentshown", ...)` で処理する（テンプレートの `data-count`）
- 図の中の要素を順に描く・線を伸ばす
  - 使うもの: CSS のアニメーション、Web Animations API
  - 書き方: `.present` のページか fragment のイベントで開始する
- 動くデモを見せる
  - 使うもの: `<iframe>` かページに組み込んだ JS
  - 書き方: 会場の回線に頼らないよう、デモもローカルで動かす

- 動きの実装をブラウザの機能（View Transitions・`@starting-style`・scroll-driven animation）で作るときは、`/modern-web-guidance` で作り方とブラウザの対応を確認する
- 本文には最終状態の値と図を書き、動きはそこへ至る途中だけにする（テンプレートの数値の変化は、最終の値をマークアップに書き、表示したときに 0 から数える）。こうすると PDF・動きを減らす設定・JS の失敗のどれでも最終状態が残る
- auto-animate は位置・大きさ・色・不透明度を補間する。要素の対応は `data-id` で明示する（`data-id` が無いと、reveal.js は要素の種類と文字で対応を推定するので、意図しない要素どうしが結ばれることがある）

## 4. 動きを減らす設定

テンプレートは `prefers-reduced-motion: reduce` のとき、ページの遷移を `none`、auto-animate を無効にし、fragment の切り替えを即時にし、数値の変化を停止する。独自の動きを追加したときも、同じ条件で停止するか即時の切り替えにする。

## 5. 発表

- `index.html` をブラウザで開く。全画面は `F`、発表者表示は `S`、全体の一覧は `Esc`
- 発表者表示は別のウインドウを開くので、ポップアップを許可しておく
- 会場の画面の比率が 16:9 でないときは、reveal.js が縦横比を保って縮小する。事前に会場の解像度を確認する
- 発表の前に、本番の PC とブラウザで最初から最後まで送る（拡張機能・書体・音の有無で挙動が変わる）

## 6. PDF

```bash
node <このスキルのディレクトリ>/scripts/html_to_pdf.mjs index.html build/deck.pdf
uv run --with pymupdf python3 <このスキルのディレクトリ>/scripts/verify_pdf.py build/deck.pdf --expect-pages <ページ数>
uv run --with pymupdf python3 <このスキルのディレクトリ>/scripts/pdf_to_png.py build/deck.pdf build/png/
```

- `html_to_pdf.mjs` は `?print-pdf` を開き、reveal.js が印刷用のページ（`.pdf-page`）を組み終えてから、CSS の `@page` の大きさで印刷する
- テンプレートは `pdfSeparateFragments: false` で、fragment を最終状態の1ページにまとめる。段階ごとにページを分けたいなら `true` にし、`--expect-pages` を段階の数に合わせる
- auto-animate の途中と CSS の動きは PDF に出ない。`html_to_pdf.mjs` は動きを減らす設定（`prefers-reduced-motion: reduce`）でページを開くので、CSS の動きには、その設定で最終状態を出す規則を必ず書く（無いと、透明から表示する要素が PDF から消える）。各ページの最終状態で主張が伝わるかを PNG で確認する
- 1ページが縦に長いと複数ページに分かれる。`pdfMaxPagesPerSlide: 1` で1ページに切る（はみ出した分は消えるので、検査とPNGで確認する）

## 7. 確認

- ブラウザで最初から最後まで送り、各ページと各段階のスクリーンショットを撮る。動きは、途中（遷移の時間の半分ほど）と最後で撮って、意図した要素が動いたかを見る
- `prefers-reduced-motion: reduce` を有効にしたブラウザでも送り、動かずに最終状態が出るかを見る
- 撮影は Playwright（MCP か `playwright-core`）の `page.keyboard.press("ArrowRight")` とスクリーンショットで行える。動きを減らす設定は、新しいページを `reducedMotion: "reduce"` で開いて再現する
- PDF 版は §6 の検査と PNG の目視

## 8. 既知の罠

- PDF が1ページだけになる、用紙の大きさが違う
  - 原因: reveal.js は印刷用の `@page` とページ（`.pdf-page`）を読み込みの後に JS で組む。読み込み直後（Chrome のコマンドラインの `--print-to-pdf`）や `Reveal.isReady()` の直後に印刷すると、組み終える前の状態で出力される
  - 対処: `scripts/html_to_pdf.mjs` を使う（`.pdf-page` が組まれ、`loading-scroll-mode` が外れるまで待ち、`preferCSSPageSize` で印刷する）
- PDF で端の余白が消える
  - 原因: 印刷用の CSS が section の `padding` を 0 にする
  - 対処: 余白は `margin` の設定で取る
- ページ番号が PDF の書体の検査で Helvetica として出る
  - 原因: reveal.js のページ番号の既定の書体
  - 対処: テンプレートの `theme.css` で本文の書体にしてある
- 画面のページ番号が送りの矢印と重なる
  - 原因: どちらも右下にある
  - 対処: テンプレートでページ番号を左下に置いてある
- オフラインで表示が崩れる
  - 原因: CDN や Web フォントのサービスから読んでいる
  - 対処: reveal.js と書体を node_modules から読む
- 和文が Type3 になる
  - 原因: システムの和文書体（CFF 形式）か可変フォントを使った
  - 対処: `@fontsource/noto-sans-jp` の固定ウェイトを読む
