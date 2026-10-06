# NOTICE — 第三者ライセンス表示

このリポジトリの以下のファイルは、MITライセンスで公開されている外部リポジトリのコンテンツを翻案（日本語化・本環境の規約への適応・再構成）したものを含む。

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

## nanaism/yomiyasu

- 出典: https://github.com/nanaism/yomiyasu （参照commit: `30ee6041c328ce21d38a7963f667e079a93d7a12`）
- 配置先: `skills/yomiyasu/`（SKILL.md, LICENSE, references/, scripts/yomiyasu_lint.py）。上流のファイルを無改変でコピーしたもので、翻案していない。本環境向けの扱いは `skills/ukwhatn-writing/SKILL.md` 側で上書きする
- plugin や `npx skills add` で導入しない（サプライチェーン攻撃を避けるため）。更新するときは上流を clone し、`diff -r` で差分を全文読んでからコピーし、上の参照commitと `vendor/manifest.json` の `commit` を書き換える
- ライセンス全文: `skills/yomiyasu/LICENSE`（MIT License, Copyright (c) 2026 nanaism）

## shadcn-ui/ui（skills/shadcn）

- 出典: https://github.com/shadcn-ui/ui の `skills/shadcn/` （参照commit: `0e3abd65a97707f4a9cc3ed07bf5006e1cb67b13`）
- 配置先: `skills/shadcn/`（SKILL.md, cli.md, customization.md, mcp.md, registry.md, rules/*.md）。`agents/`・`assets/`・`evals/` は Claude Code の実行に要らないので取り込んでいない
- 改変: `SKILL.md` の、読み込み時に `npx shadcn@latest info --json` を自動で実行する行と、`npx shadcn@latest` の `allowed-tools`（事前承認）を外し、必要なときに実行する手順の文に置き換えた（版を固定しないパッケージが、要らない場面でも確認なしに実行されるのを避けるため）。自動実行の結果を前提にしていた2行も合わせて直した。改変の全体は `vendor/patches/shadcn.patch`。それ以外のファイルは無改変
- 更新するときは、上流の参照commitから最新までの差分を全文読み、上流のファイルを無改変でコピーしてから `git apply vendor/patches/shadcn.patch` で改変を当て直す。当たらなければ改変の趣旨（自動実行と事前承認を外す）に沿ってパッチを作り直す。上の参照commitと `vendor/manifest.json` の `commit` を書き換える
- ライセンス全文: `skills/shadcn/LICENSE.md`（MIT License, Copyright (c) 2023 shadcn）

## 上流の更新の検出

`vendor/manifest.json` に、取り込んだ外部 skill の上流リポジトリ・固定した commit・取り込んだファイルを置く。`bin/vendor-check.py` は、固定した commit と上流の最新とで取り込んだファイルの内容が変わったか、取り込み元のディレクトリにファイルが増えたか、手元の複製が固定した commit と一致するか（改変したファイルを除く）を調べる。`.github/workflows/vendor-check.yml` が週次で実行し、差分があれば issue を立てて ukwhatn に割り当てる（既にあれば本文を更新する）。翻案したもの（obra/superpowers・mattpocock/skills）は台帳に載せていない。
