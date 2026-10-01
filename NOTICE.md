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
- plugin や `npx skills add` で導入しない（サプライチェーン攻撃を避けるため）。更新するときは上流を clone し、`diff -r` で差分を全文読んでからコピーし、上の参照commitを書き換える
- ライセンス全文: `skills/yomiyasu/LICENSE`（MIT License, Copyright (c) 2026 nanaism）
