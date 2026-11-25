// reveal.js のデッキを ?print-pdf で開き、reveal.js の印刷用レイアウトのまま PDF にする。
//
//   node html_to_pdf.mjs <deck/index.html> <out.pdf>
//
// デッキのディレクトリの playwright-core（テンプレートの devDependencies）で、システムの Chrome を操作する。
// reveal.js は印刷用のページを読み込みの後に JS で組むので、読み込み直後に印刷する Chrome の --print-to-pdf では、組む前の状態（1ページなど）で出力される。
// 動きを減らす設定で開き、CSS の動きを最終状態で止めて印刷する（初期状態が透明の動きはそのままだと PDF から消える）。
import { createRequire } from "node:module";
import { existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [deck, out] = process.argv.slice(2);
if (!deck || !out) {
  console.error("usage: node html_to_pdf.mjs <deck/index.html> <out.pdf>");
  process.exit(2);
}
const deckPath = resolve(deck);

function loadChromium() {
  for (const base of [dirname(deckPath), process.cwd()]) {
    for (const name of ["playwright-core", "playwright"]) {
      try {
        return createRequire(join(base, "package.json"))(name).chromium;
      } catch {}
    }
  }
  console.error("playwright-core が見つからない。デッキのディレクトリで npm install -D playwright-core を実行する");
  process.exit(2);
}

const chrome = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].find((path) => path && existsSync(path));

const browser = await loadChromium().launch(chrome ? { executablePath: chrome } : { channel: "chrome" });
try {
  const page = await browser.newPage({ reducedMotion: "reduce" });
  const url = `${pathToFileURL(deckPath).href}?print-pdf`;
  await page.goto(url, { waitUntil: "load" });
  // reveal.js は ready の後に印刷用のページ（.pdf-page）を組み、pdf-ready を出して loading-scroll-mode を外す。
  // ready だけを待つと、組む前の1ページで印刷してしまう
  await page.waitForFunction(
    () => document.querySelector(".pdf-page") !== null && document.querySelector(".loading-scroll-mode") === null,
  );
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  console.log(out);
} finally {
  await browser.close();
}
