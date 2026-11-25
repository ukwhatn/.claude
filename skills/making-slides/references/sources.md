# 出典と採否

本スキルの規則の根拠と、出典どうしが食い違う点の採否。確認日は 2026-11-25。

## 出典

- duarte
  - 出典: Duarte「The slides you deliver versus the Slidedoc you leave behind」 https://www.duarte.com/?p=41191 、「Slidedocs visual documents」 https://kinstastg.duarte.com/resources/slidedocs-visual-documents/
  - 使った箇所: 投影と読む資料の文字量（40語以下と150〜200語）、2版を作る、ノートから配布版を作る
- fowler
  - 出典: martinfowler.com「Do you even need a presentation?」（never-send-slides の連載） https://martinfowler.com/articles/never-send-slides/need-presentation.html
  - 使った箇所: 伝えるだけなら文書が既定、ライブの発表は相互作用が必要なとき
- alley
  - 出典: Penn State「Scientific Presentations」（Alley の assertion-evidence の研究） https://writing.engr.psu.edu/research.html
  - 使った箇所: 見出しを主張の文にし、下に視覚的な根拠を置く
- farkas
  - 出典: Farkas「Assessment of Alley's Slide Design」 https://faculty.washington.edu/farkas/dfpubs/Farkas-Assessment%20Of%20Alleys%20Slide%20Design.pdf
  - 使った箇所: 全ページに視覚的な根拠を要求する理由は無いという反論
- monoist
  - 出典: MONOist「『見せる』プレゼン資料と『読ませる』配布資料」 https://monoist.itmedia.co.jp/mn/articles/2109/09/news014.html
  - 使った箇所: 投影用の資料が稟議に添付されて独り歩きする、配布用は別に作る
- hokudai
  - 出典: 北海道大学の学修支援の資料（HUSCAP、academicskil06.pdf） https://eprints.lib.hokudai.ac.jp/repo/huscap/all/59537/academicskil06.pdf
  - 使った箇所: 1スライド1トピック
- sales
  - 出典: Highspot https://www.highspot.com/blog/how-to-create-a-sales-pitch-deck/ 、Pitch https://pitch.com/guides/sales/sales-presentation-structure 、First Round Review https://review.firstround.com/building-your-best-sales-deck-starts-here/
  - 使った箇所: 課題 → 解決 → 証拠 → 次の一手（1つ）
- a11y
  - 出典: NYC「Accessible Slidedecks Guide」 https://www.nyc.gov/site/mopd/publications/guides/accessible-slidedecks-guide.page 、UCL https://www.ucl.ac.uk/isd/services/websites-apps/creating-accessible-content/slides 、North Dakota「Accessible Presentation Guide」 https://www.arts.nd.gov/sites/www/files/documents/resources/Electronic%20Accessibility%20-%20Accessible%20Presentation%20Guide.pdf
  - 使った箇所: 文字の大きさ、コントラスト、色だけで示さない、動きの抑制
- wcag
  - 出典: WCAG 2.2 2.3.1 Three Flashes or Below Threshold https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html
  - 使った箇所: 1秒に3回を超えて点滅させない
- marp
  - 出典: Marp CLI（v4.5.1）README と bespoke transitions https://github.com/marp-team/marp-cli 、Marp Core のテーマ作成 https://github.com/marp-team/marp-core/blob/main/docs/theme-authoring.md
  - 使った箇所: PDF の出力、`--pdf-notes`・`--pdf-outlines`、`@size`・`@auto-scaling`、遷移と View Transition の対応ブラウザ、設定ファイルの `engine`
- reveal
  - 出典: reveal.js（v6.0.2） https://revealjs.com/ 、PDF export https://revealjs.com/pdf-export
  - 使った箇所: auto-animate、fragment、`?print-pdf`、`pdfSeparateFragments`・`pdfMaxPagesPerSlide`・`showNotes`

テンプレートとスクリプトの挙動（Chrome の PDF が CFF 形式・可変フォント・疑似太字を Type3 にすること、Marp CLI が一時ディレクトリから変換すること、reveal.js の印刷用のページが `ready` の後に組まれること）は、出典ではなく実機で確認した結果で、`references/marp.md` と `references/html.md` の既知の罠に書いた。

## 食い違う点の採否

- **全ページに図を置くか**: alley は見出しの文と視覚的な根拠の組を全ページに求め、farkas はその必要を否定する。見出しを主張の文にする点は両者が対立していないので既定にし、図は根拠を最もよく示せるときだけ置く（`references/message-design.md` §3）
- **投影の文字の大きさ**: a11y の出典で下限が 16〜24pt に割れる。遠い席を想定して 24pt を既定にし、18pt を下限にする（`references/visual.md` §1）
- **文字量の目安**: duarte の数値は英語の語数で、実測の研究ではない。日本語の字数に換算した出典は見つからなかったので、数値ではなく「投影は語句と図、読む資料は文」という作り分けを規則にした（`references/deck-types.md` §1）
- **コントラスト**: a11y の出典に 7:1 を求めるものがあるが、WCAG の AA（4.5:1、大きい文字は 3:1）を既定にした。投影機で暗い色が浮くことは、薄い灰色の本文を避ける規則で扱う
