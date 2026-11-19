# ukwhatn/skills

作者が毎日使っている開発の進め方を、Claude Code の plugin にしたものです。文章・コード・原因調査・画面の設計・レビューのスキルと、それらを発動させる任意の hook が入っています。

スキルの本文は日本語です。英語の文章も扱えます（`writing-prose` が英語のメッセージを扱い、`humanizer` を呼びます）。

[English](README.md)

## plugin

### ukwhatn-skills

- `dev-flow`: 作業の進め方。事実を書く前に一次情報を開く、新しく書く前に既存のコードを探す、push や投稿の前に確認する、大きな作業は計画から完了報告までの段階で進める。ほかのスキルはこの節を参照する
- `writing-prose`: メッセージ・PR の本文・レビューのコメント・文書・メールを、一度読めば分かる文で書く。日本語は書き言葉の検査と `yomiyasu`、英語は `humanizer` で推敲する
- `writing-code`: 既存のパターンを踏襲し、deep module で設計し、seam でテストする。コメントは、コードとテストで表せないことだけにする
- `systematic-debugging`: 最初の修正で直らなかったとき、コードを変える前に根本原因を特定する
- `writing-ui-text`: 画面の日本語の文言（ボタン・見出し・エラー・空状態）
- `designing-ui`: ナビゲーション・重ね方・通知・レイアウトの型を決定表で選び、全画面で統一する
- `self-review`: PR を作成する前に、自分のブランチの差分を確認する
- `pr-review`: Claude Code と外部の CLI（既定は Codex）で PR をレビューする
- `grilling`: 計画や設計を問い詰めて、前提と未決の点を洗い出す
- `yomiyasu` と `humanizer`: [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) と [blader/humanizer](https://github.com/blader/humanizer) の無改変のコピー。`writing-prose` が使う

スキルは発動したときだけ読まれるので、`dev-flow` の規則は `CLAUDE.md` のように毎ターン効くわけではありません。常に効かせたい部分は、自分の `CLAUDE.md` に写してください。

### ukwhatn-guards（既定で無効）

- `writing-code` を発動するまでコードの編集を拒否し、`writing-prose` を発動するまで外への投稿（Slack・GitHub のコメント・メールの下書き）を拒否する hook
- 外へ送る日本語の文に話し言葉の動詞や規則に合わない表があれば、1 回だけ修正を求める hook
- output style `ukwhatn-style`（日本語）。`/config` で選ぶまで効かない

この hook はセッションの中でツールの呼び出しを拒否するので、インストールしただけでは有効になりません。スキルの発動を強制したいときだけ有効にしてください。

## 入れ方

```sh
claude plugin marketplace add ukwhatn/skills
claude plugin install ukwhatn-skills@ukwhatn
```

guards もインストールする場合は、続けて次を実行します。

```sh
claude plugin install ukwhatn-guards@ukwhatn
claude plugin enable ukwhatn-guards@ukwhatn
```

`ukwhatn-guards` は `ukwhatn-skills` を前提にしていて、インストールされていなければ一緒にインストールされます。

## 任意のスキル

`designing-ui` は、次のスキルがインストールされていれば使い、無ければその手順を飛ばします。使う場合は上流からインストールしてください。

- [heydamir/unslop](https://github.com/heydamir/unslop): 新しい画面の見た目の仕上げ
- [shadcn-ui/ui](https://github.com/shadcn-ui/ui)（`skills/shadcn`）: shadcn/ui の部品の API
- [GoogleChrome/modern-web-guidance](https://github.com/GoogleChrome/modern-web-guidance): 選んだ型を今の Web の機能で作る方法

## 保守のしかた

原本は作者の Claude Code の設定にあります。スクリプトが、公開するスキルをこの repo に写し、作者の環境にしか当てはまらない部分を外し、スキル間の参照を書き換えます。書き出した内容が変わるたびに version を上げます。

issue と pull request を受け付けます。採用した変更は原本に反映してから書き出し直すので、変更は次の書き出しのコミットに含まれます。

## ライセンス

独自の部分は MIT です（`LICENSE`）。翻案元・同梱したコピーとそれぞれのライセンスは [NOTICE.md](NOTICE.md) にあります。
