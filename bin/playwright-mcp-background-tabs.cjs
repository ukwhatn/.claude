// playwright がタブを作る CDP 呼び出し（Target.createTarget）に background: true を付ける。
// Chrome は background の無いタブ作成で自分を前面に出し、macOS では仮想デスクトップも移る。
// playwright に設定が無いので、playwright-mcp-server.sh が NODE_OPTIONS の --require でこのファイルを読み込ませ、
// coreBundle.js の読み込み時にソースを書き換える（npx のキャッシュのファイルは変えない）。
// 書き換える箇所が見つからなければ警告を出して何もしない（タブが前面に出る今の動作に戻るだけ）。
const Module = require("module");
const path = require("path");

const TARGET_FILE = path.join("playwright-core", "lib", "coreBundle.js");
const PATTERN = '"Target.createTarget", { url: "about:blank", browserContextId: this._browserContextId }';
const REPLACEMENT = '"Target.createTarget", { url: "about:blank", browserContextId: this._browserContextId, background: true }';

const compile = Module.prototype._compile;
Module.prototype._compile = function (content, filename) {
  if (filename.endsWith(TARGET_FILE)) {
    if (content.includes(PATTERN)) {
      content = content.replace(PATTERN, REPLACEMENT);
      console.error(`[background-tabs] applied: ${filename}`);
    } else {
      console.error(`[background-tabs] pattern not found, tabs will come to front: ${filename}`);
    }
  }
  return compile.call(this, content, filename);
};
