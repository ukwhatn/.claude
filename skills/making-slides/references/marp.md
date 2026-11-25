# Marp で作る

目次: 1 セットアップ / 2 ビルドと検証 / 3 テーマ / 4 記法 / 5 遷移と段階表示 / 6 既知の罠 / 7 ページに収める

## 1. セットアップ

デッキのディレクトリに `templates/marp/` の中身を複製し、依存をインストールする。

```bash
cp -R <このスキルのディレクトリ>/templates/marp/. <デッキのディレクトリ>/
cd <デッキのディレクトリ> && npm install
```

```
<デッキのディレクトリ>/
├── marp.config.mjs     テーマ・ブラウザ・書体の設定
├── package.json        @marp-team/marp-cli と @fontsource/noto-sans-jp
├── themes/slides-basic.css
├── deck.md             骨格。複製して書く
└── build/              生成物（PDF・PNG）
```

- 書体は `@fontsource/noto-sans-jp` の固定ウェイト（400・700）を node_modules から読む。システムの和文書体（ヒラギノ）は CFF 形式で、Chrome の PDF で Type3 になり書体名が消える。可変フォントと疑似太字も Type3 になる
- Marp CLI は OS の一時ディレクトリの HTML から変換するので、テーマの CSS に相対パスの `@import` や `url()` を書いても解決されない。書体の CSS は `marp.config.mjs` が絶対パスにして `slides-fonts` テーマとして渡し、`slides-basic.css` が `@import 'slides-fonts';` で読む
- `npm install` の後はオフラインでビルドできる

## 2. ビルドと検証

デッキのディレクトリで実行する。

```bash
npx marp --no-stdin --pdf -o build/deck.pdf deck.md < /dev/null
uv run --with pymupdf python3 <このスキルのディレクトリ>/scripts/verify_pdf.py build/deck.pdf --expect-pages <設計表のページ数>
uv run --with pymupdf python3 <このスキルのディレクトリ>/scripts/pdf_to_png.py build/deck.pdf build/png/
```

- `--no-stdin` と `< /dev/null` は両方付ける（ハーネスから起動すると標準入力を待って止まる）
- 発表者ノートを PDF の注釈に含めるなら `--pdf-notes`、しおりを付けるなら `--pdf-outlines`
- 編集中の確認は `npx marp --no-stdin --preview deck.md`（遷移と段階表示はこちらで見る）
- `verify_pdf.py` は書体（許容する名前の正規表現は `--allow-fonts`）・本文の下端のはみ出し（フッターの帯の上端は `--footer-top`、既定 0.92）・スライド外・文字の重なり・ページ数を見る。0件でも `build/png/` を全ページ開く
- 目視で見るもの: 見出しが1行か、2段の割り当て、表の列の潰れ、注記とページ番号の位置、`**` などの生の記法の残り、画像の切れ

## 3. テーマ

`themes/slides-basic.css` は 1280×720px（16:9）。PJ のブランドに合わせるときは、先頭の `:root` の色と書体だけを書き換える。

- （なし）
  - 用途: 標準のページ
  - 書き方: `#` で主張の見出し、下に箇条書き・図・表
- `lead`
  - 用途: 表紙
  - 書き方: `<!-- _class: lead -->` と `<!-- _paginate: false -->`。`#` が題、段落が発表者と日付
- `chapter`
  - 用途: 章扉
  - 書き方: `# 1. 章の題` だけを置く
- `cols`
  - 用途: 2段
  - 書き方: 見出しの後の2つのまとまり（図と箇条書きなど）を左右に置く。3つ目以降は次の行に回る
- `metric`
  - 用途: 大きな数値
  - 書き方: `**数値**` を1つ置き、下の段落で比べた値と条件を書く
- `doc`
  - 用途: 読む資料
  - 書き方: 本文を 24px にして文で書く。表も小さくなる

- `_class` は `class` を上書きし、合成しない。2つ使うなら `<!-- _class: "cols doc" -->` と1行に書く
- 注記・出典は `<p class="note">` で書き、ページの最後に置く（下端に寄る）
- ページだけの CSS は `<style scoped>` に書く。テーマと同じ詳細度だと負けるので、`section.cols table td` のように1段上げる
- テーマの先頭のコメント `@theme`・`@size`・`@auto-scaling` はテーマの定義なので消さない。`@auto-scaling` は見出しの `<!-- fit -->` と数式の縮小だけを有効にしてある（コードの自動縮小は、はみ出しを隠して検査に出なくなるので外した）

## 4. 記法

- ページの区切りは `---`。先頭の front matter で `marp: true`・`theme`・`size`・`paginate`
- 画像: `![説明](パス)`、大きさは `![w:600](パス)`、背景は `![bg](パス)`、背景を右半分に置くなら `![bg right:40%](パス)`
- 発表者ノート: ページの中の HTML コメント `<!-- ... -->`（ディレクティブとして解釈されない文）
- ディレクティブ: `<!-- _paginate: false -->` のように `_` を付けるとそのページだけに効く
- 図に文字を置くなら、Markdown の本文に書くか、PNG にする。SVG 画像の中の文字はページの書体が効かず、PDF で Type3 になり、検査の書体に出る

## 5. 遷移と段階表示

どちらも HTML 出力（`npx marp --no-stdin -o build/deck.html deck.md`）と `--preview` だけで効き、PDF には出ない。

- 遷移: front matter か `<!-- transition: fade -->` で、そのページの次の境界に効く。`<!-- _transition: none -->` でそのページだけ無効にする。同じ `view-transition-name` を持つ要素は、隣のページの同じ要素へ形を変えて移る（View Transition API。Chrome・Edge 111 以降、Safari 18.2 以降、Firefox 144 以降）。OS で動きを減らす設定のときは fade に落ちる
- 箇条書きの段階表示: `-` の代わりに `*` で書くと、1項目ずつ表示する
- 動きが主張の中心になるなら HTML 経路（`references/html.md`）を選び直す

## 6. 既知の罠

- 和文が Type3 になり書体名が消える
  - 原因: CFF 形式・可変フォント・疑似太字の書体
  - 対処: テンプレートの書体の読み方（§1）を変えない。太字は 700 を読み込んである
- テーマの `@import` や `url()` が効かない
  - 原因: 一時ディレクトリの HTML から変換している
  - 対処: `marp.config.mjs` で絶対パスにする（§1）
- 文字や後続のページが消えた。ページ数が減った
  - 原因: `<` の直後が ASCII 英字の文字列が HTML タグとして解釈された。閉じられないタグは以降を飲み込む
  - 対処: `&lt;` にするかコードにする。ビルド後にページ数を比べる
- PDF の書体の検査が全部 Type3 になる
  - 原因: `inlineSVG` が既定の true のまま
  - 対処: `marp.config.mjs` の `options: { inlineSVG: false }` を残す
- PDF の変換が止まる
  - 原因: ブラウザの自動探索、標準入力の待ち
  - 対処: `browser: "chrome"` を残す。`--no-stdin` と `< /dev/null`
- ページ番号が注記より上に浮く
  - 原因: Marp の既定が `section::after { padding: inherit }`
  - 対処: テーマで `padding: 0` にしてある。独自のテーマでも同じにする
- `_header: 01` が `1` になる
  - 原因: YAML が数値として解釈した
  - 対処: `_header: "01"` と引用符で囲む
- 見出しが語の途中で改行される
  - 原因: 幅に対して長い
  - 対処: 主張を短くするか `<br>` を文の切れ目に置く

## 7. ページに収める

検査のはみ出しが出たら、次の順で修正する。テーマの文字の大きさ・行間・余白を1ページのために変えない（ページごとに読み心地が変わる）。

1. 見出しを1行にする（修飾を削り、主張は残す）
2. 箇条書きの各項目を短くし、補足を発表者ノートか注記に移す
3. 表の列名と分類名を短くする
4. ページを分ける（同じクラスで 1/2・2/2）
5. 読む資料なら `doc` クラスに替える（投影のページには使わない）
