# 英語の文章（国際的なコミュニティの運営間チャット・技術者間のやり取り）

各国・各言語の運営チームが集まるチャットで、自分のチームを代表して書く英語の型。母語話者でない読み手も多いので、短い文と普通の語で書く。

目次: 1. 声の全体像 / 2. 場面ごとの型 / 3. 文の作り方 / 4. 避けるもの

---

## 1. 声の全体像

- **チームとして話す**: 主語は `we` / `our staff` / `<チーム名>`（`<チーム名> is still discussing, but we generally agree.`）。個人の見解は `I think` / `in my opinion` で分ける
- **用件が1行目に来る**: 呼びかけ（メンション）の直後に、何の投稿かを書く。前置きの挨拶・自己紹介は置かない（初めてのスレッドでも `Hi <名前>, <チーム名> here again.` 程度）
- **事実は言い切り、知っている範囲は明示する**: `as far as we understand` / `If that's accurate,` / `We don't know if ...`。推測を事実の形で書かない
- **相手の判断を尊重して頼む**: 提案は具体案（差し替える文の例）まで出し、採否は相手に返す（`If you think it fits, ...` / `I'd leave it to you whether ...` / `but I understand if you'd rather ...`）
- **チャットの口調**: 短縮形（`we're` `don't` `it's`）を使う。太字・見出しは使わない。絵文字は感謝・依頼の末尾に1個まで（🙏 😢 🤔）で、報告・提案では付けない

## 2. 場面ごとの型

### 2-1. 情報共有（相手に対応を求めない）

```
@<相手チーム>
Heads-up from <チーム名> about <対象>. This is just for your info, we're not asking for any action on your side.

<対象が何者か・何が起きたかを1〜2文>

How we know <根拠の対象>: <根拠を1〜2文。リンク付き>

<経緯の見出し>:
<時期>: <出来事>
<時期>: <出来事>

<相手側に関係する事実を1〜2文>

Happy to share more, like <出せる資料>, if that helps.
```

- 経緯は `<時期>: <出来事>` の行を並べる。1行に1つの出来事
- ラベル行（`How we know it's them:` `Their history on <チーム名>:`）は小文字始まりの文で、コロンで終える
- 締めは、追加で出せるものを1つ具体的に挙げた申し出にする

### 2-2. 他チームの草稿への提案

```
@<草稿の担当者>
<相手の方針への理解を1文>, and I think that's reasonable. Still, I'd like to raise one point.

<懸念を、読み手に何が起きるかで1〜2文>

To make sure we understand it correctly: is <確認したい点> roughly <要約>?

<確認点1>
<確認点2>

If that's right, would it be possible to <具体的な変更>? For example:

"<差し替え案の文>"

<採否を相手に返す1文>
```

- 先に相手の制約（短くしたい・法的に慎重でいたい等）を認め、そのうえで1点だけ出す
- 誤読の起こり方は、読み手が実際にどう読むかで書く（`Some people believe X, so Y is not obvious to them.`）
- 他チームの意見に触れるときは名指しで言及する（`I'm also aware of <チーム>'s point about ...`）

### 2-3. 質問への回答（自チームの方針・運用の説明）

```
On <チーム名>, our policy (<URL>) <方針を1文>, on the grounds that <理由>. <許されていること>.

When <場面>:
<条件>: <自チームの扱い>
<条件>: <自チームの扱い>
```

- 方針は公開ページのリンクを添えて1文で言い、理由を `on the grounds that` で続ける
- 運用は条件ごとに1行。個別の件の対象者名・内部の議論は書かない（運営内の非公開情報）

### 2-4. 短い返信

- 受領・感謝: `Thanks for handling this quickly, and for letting us know.` / `Thank you for the update.`
- 自チームの対応の予告: `Our translation is ready and we're finalizing internal approval now. We plan to post it in about <時間> (<現地の時間帯>).`
- 完了の知らせ: `FYI: <成果物> is posted <URL>`
- 相手チームへの依頼: `Could you <依頼>?` の1文に理由を1文添える

## 3. 文の作り方

- 1文に1つの論点。従属節を重ねない。日本語の下書きを訳すときは、英語の語順で書き直す
- 普通の語を選ぶ（`use` `help` `show` `check`）。ラテン系の硬い語（`utilize` `facilitate` `endeavor`）を使わない
- 条件・理由は文頭に出す（`Since <理由>, ...` / `If <条件>, ...`）
- 引用する文・提案する文は二重引用符で囲み、独立した行に置く
- リンクは Markdown の `[テキスト](URL)`。Discord で展開させたくないリンクは `<URL>` で囲む

## 4. 避けるもの

- 謝罪・感謝の過剰な重ね（`We sincerely apologize for any inconvenience this may cause`）
- 同意を演出する定型（`Great point!` `Absolutely!`）
- 相手が既に知っている経緯の言い直し。返信は判断・回答から始める
- 自チームの内部手続き（承認の回数・担当者名）の細部。相手の行動に関わる時刻・期限だけ書く
