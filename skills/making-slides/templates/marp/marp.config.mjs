// Marp CLI の設定。テーマ・ブラウザ・HTML の許可をここに集め、コマンドで重ねて渡さない
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";

// Marp CLI は OS の一時ディレクトリの HTML から変換するので、テーマの CSS に相対パスを書いても解決できない。
// 書体の CSS はこの設定ファイルの場所から絶対パスにして、slides-fonts テーマとして渡す
const fontCss = (weight) =>
  pathToFileURL(resolve(import.meta.dirname, `node_modules/@fontsource/noto-sans-jp/${weight}.css`)).href;

export default {
  themeSet: "./themes",
  // auto はブラウザの探索で止まることがあるので明示する
  browser: "chrome",
  allowLocalFiles: true,
  html: true,
  // 既定の inline SVG だと PDF の文字が Type3 になり、verify_pdf.py が書体を判定できない
  options: { inlineSVG: false },
  engine: ({ marp }) => {
    marp.themeSet.add(`/* @theme slides-fonts */\n@import url("${fontCss(400)}");\n@import url("${fontCss(700)}");\n`);
    return marp;
  },
};
