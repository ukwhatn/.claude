# NOTICE — 第三者ライセンス表示

このリポジトリは、外部リポジトリのコンテンツを翻案（日本語化・本環境の規約への適応・再構成）したものと、外部リポジトリのファイルをコピーしたもの（改変はパッチで管理する）を含む。各項目に出典・ライセンス・改変の有無を書く。

## obra/superpowers

- 出典: https://github.com/obra/superpowers （参照commit: `d884ae04edebef577e82ff7c4e143debd0bbec99`）
- 翻案先: `skills/systematic-debugging/`（SKILL.md, references/techniques.md）、`skills/writing-code/SKILL.md`（テスト規律のmock指針の一部。testing-anti-patterns由来）

```
MIT License

Copyright (c) 2025 Jesse Vincent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## mattpocock/skills

- 出典: https://github.com/mattpocock/skills （参照commit: `66f92b61f5b1434a1c7422f6fbd8efc5ee0c0214`）
- 翻案先: `skills/writing-code/`（SKILL.md, references/typescript.md, references/python.md, references/go.md）

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## DietrichGebert/ponytail

- 出典: https://github.com/DietrichGebert/ponytail （参照commit: `09c434ab73ca43761c5d8b0c5d341926c2fba710`）
- 翻案先: `AGENTS.md`（進め方の既定「新しく作る前に」）、`skills/writing-code/SKILL.md`（設計原則7、コメントの近道の書式）、`skills/pr-review/SKILL.md`（手順3の5）、`skills/self-review/SKILL.md`（手順4の3）

```
MIT License

Copyright (c) 2026 DietrichGebert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## cursor/plugins（pstack）

- 出典: https://github.com/cursor/plugins の `pstack/` （参照commit: `8838150c6b4829ea3c01782631213776d86df14a`）
- 翻案先: `AGENTS.md`（事実の扱いの数値の確認し、進め方の既定の前提の書き出しとスクリプト化）、`output-styles/ukwhatn-style.md`（推奨と判断軸の率直な評価）、`skills/writing-code/SKILL.md`（設計原則8、テストの2つの想像上の変更、再実行に耐える操作、アンチパターン表の Scattered State）

```
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## nanaism/yomiyasu

- 出典: https://github.com/nanaism/yomiyasu の `skills/yomiyasu/` （参照commit: `5b7cacc7749e9195338d7305635c06871fc6daf1`）
- 配置先: `skills/yomiyasu/`（SKILL.md, LICENSE, UNICODE-LICENSE.txt, references/, scripts/）。上流のファイルを無改変でコピーしたもので、翻案していない。`.codex-plugin/` と `assets/` は Claude Code の実行に不要なので取り込んでいない。本環境向けの扱いは `skills/writing-prose/SKILL.md` 側で上書きする
- `scripts/yomiyasu_hook.py` は設定ファイルに手で登録したときだけ動く hook で、本環境では登録していない
- plugin や `npx skills add` で導入しない（サプライチェーン攻撃を避けるため）。更新するときは上流を clone し、`diff -r` で差分を全文読んでからコピーし、上の参照commitと `vendor/manifest.json` の `commit` を書き換える
- ライセンス全文: `skills/yomiyasu/LICENSE`（MIT License, Copyright (c) 2026 nanaism）

## blader/humanizer

- 出典: https://github.com/blader/humanizer （参照commit: `225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8`）
- 配置先: `skills/humanizer/`（SKILL.md, LICENSE）。上流のファイルを無改変でコピーしたもので、翻案していない。plugin の定義・README・検証スクリプトは Claude Code の実行に不要なので取り込んでいない。本環境向けの扱いは `skills/writing-prose/SKILL.md` 側で上書きする
- plugin や `npx skills add` で導入しない（サプライチェーン攻撃を避けるため）。更新するときは上流を clone し、`diff -r` で差分を全文読んでからコピーし、上の参照commitと `vendor/manifest.json` の `commit` を書き換える
- ライセンス全文: `skills/humanizer/LICENSE`（MIT License, Copyright (c) 2025 Siqi Chen）

## shadcn-ui/ui（skills/shadcn）

- 出典: https://github.com/shadcn-ui/ui の `skills/shadcn/` （参照commit: `daaf156ee00ed91cc7e6bdd937c1b4973152d141`）
- 配置先: `skills/shadcn/`（SKILL.md, cli.md, customization.md, mcp.md, registry.md, design-system.md, design-system-page.md, rules/*.md, assets/showcase/*, scripts/showcase-coverage.mjs）。`agents/`・`evals/` と、`assets/` の直下にあるロゴ画像は Claude Code の実行に不要なので取り込んでいない
- 改変: `SKILL.md` の、読み込み時に `npx shadcn@latest info --json` を自動で実行する行と、`npx shadcn@latest` の `allowed-tools`（事前承認）を外し、必要なときに実行する手順の文に置き換えた（版を固定しないパッケージが、不要な場面でも確認なしに実行されるのを避けるため）。自動実行の結果を前提にしていた2行も合わせて修正した。改変の全体は `vendor/patches/shadcn.patch`。それ以外のファイルは無改変
- 更新するときは、上流の参照commitから最新までの差分を全文読み、上流のファイルを無改変でコピーしてから `git apply vendor/patches/shadcn.patch` で改変を当て直す。当たらなければ改変の趣旨（自動実行と事前承認を外す）に沿ってパッチを再作成する。上の参照commitと `vendor/manifest.json` の `commit` を書き換える
- ライセンス全文: `skills/shadcn/LICENSE.md`（MIT License, Copyright (c) 2023 shadcn）

## heydamir/unslop

- 出典: https://github.com/heydamir/unslop の `skills/unslop/` （参照commit: `97daa3eb365670ea3f87ed85356cbfcee18105a5`）。作者: Damir Sokolovsky（https://x.com/heydamir）
- 配置先: `skills/unslop/`（SKILL.md, references/, scripts/, agents/openai.yaml, LICENSE）。上流の最上位にある LICENSE を `skills/unslop/LICENSE` に置いた。`examples/`・`test/` は Claude Code の実行に不要なので取り込んでいない
- ライセンス: Creative Commons Attribution 4.0 International（CC BY 4.0、https://creativecommons.org/licenses/by/4.0/ ）。SKILL.md と references にある作者のクレジット行は削除しない
- 改変: `SKILL.md` の description の末尾に、本環境のほかのスキルとの境界を1文追加し、`## Run it` の前に `## Precedence in this environment` の節を追加し、frontmatter の直後に改変した旨の注記を1行追加した（PJ のデザインシステム・日本語の文言・チャート・画面の型の選択を本環境のスキルに譲り、課金や外部送信のある画像生成を事前に確認するため）。改変の全体は `vendor/patches/unslop.patch`。それ以外のファイルは無改変
- 更新するときは、上流の参照commitから最新までの差分を全文読み、上流のファイルを無改変でコピーしてから `git apply vendor/patches/unslop.patch` で改変を当て直す。当たらなければ改変の趣旨（境界の1文と優先順位の節）に沿ってパッチを再作成する。上の参照commitと `vendor/manifest.json` の `commit` を書き換える

## GoogleChrome/modern-web-guidance

- 出典: https://github.com/GoogleChrome/modern-web-guidance の `skills/modern-web-guidance/` （参照commit: `4dd968349e54ca45a05dd5c818fb035c9054b022`）
- 配置先: `skills/modern-web-guidance/`（SKILL.md, LICENSE）。`guides/` は SKILL.md の手順どおり CLI が実行時に取得するので取り込んでいない。plugin 定義・`skills/chrome-extensions/` も取り込んでいない
- 改変: `SKILL.md` の description の「MANDATORY: Execute FIRST for all HTML/CSS and clientside JS tasks」を、ブラウザ側の機能の作り方を決める前に使う旨と designing-ui との境界の文に置き換えた（CSS の小さな修正でも毎回 CLI がネットワークに出るのを避けるため）。応答の末尾に `### Modern Web Guidance` 節を付けさせる Step 4 を外した（応答の書き方は output style が決めるため）。frontmatter の直後に、改変した旨の注記を1行追加した（Apache License 2.0 の 4(b)）。改変の全体は `vendor/patches/modern-web-guidance.patch`
- CLI は `npx -y modern-web-guidance@latest` のまま実行させる。`~/.npmrc` の `min-release-age` が公開から日の浅い版を除外するので、版をここで固定しない
- `vendor/manifest.json` の `watch_dirs` は空にしてある（取り込まない `guides/` の追加で毎週 issue が立つのを避けるため）。SKILL.md の `--skill-version` は上流の更新ごとに変わるので、更新は SKILL.md の差分で検出できる
- 更新するときは、上流の参照commitから最新までの SKILL.md の差分を全文読み、無改変でコピーしてから `git apply vendor/patches/modern-web-guidance.patch` で改変を当て直す。上の参照commitと `vendor/manifest.json` の `commit` を書き換える
- ライセンス全文: `skills/modern-web-guidance/LICENSE`（Apache License 2.0）

## 上流の更新の検出

`vendor/manifest.json` に、取り込んだ外部 skill の上流リポジトリ・固定した commit・取り込んだファイルを置く。`bin/vendor-check.py` は、固定した commit と上流の最新とで取り込んだファイルの内容が変わったか、取り込み元のディレクトリにファイルが増えたか、手元の複製が固定した commit と一致するか（改変したファイルを除く）を調べる。`.github/workflows/vendor-check.yml` が週次で実行し、差分があれば issue を立てて ukwhatn に割り当てる（既にあれば本文を更新する）。翻案したもの（obra/superpowers・mattpocock/skills・DietrichGebert/ponytail・cursor/plugins の pstack）は台帳に載せていない。
