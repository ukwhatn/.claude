# レイアウト・トークン・状態・モーション

アプリの外枠、密度、デザイントークン、面の重なり、操作中の状態、動き、壊れにくさを扱う。ナビゲーションの型は ナビゲーションの参照、重ねて出す型は 重ね方の参照、通知と空状態の型は 通知の参照、文言は `/writing-ui-text`。

## 目次

0. 決める前に
1. 外枠
2. 密度
3. トークン
4. 面の重なり
5. 状態とフォーカス
6. モーション
7. 堅牢さ
8. 出典キー
9. 未確認で外した規則

## 0. 決める前に

- **製品・利用者・その画面の主な仕事を先に言葉にしてから、配置と見た目を決める**（何のための画面かで、残す要素と削る要素が決まるから）［ANT-fd］［本環境］
- 既存の同種画面か、参照するデザインシステムの型を先に決めてから要素を置く（型を決めずに要素を足すと、後から文言を直しても読みにくさは消えない）［本環境］
- 設計メモ（トークン・外枠の型・原則）を先に書き、目的に照らして見直してから実装する（実装後に型を変えると全画面に波及するから）［ANT-fd］
- 罫線・枠・番号・区切り線は、内容の構造を表すときだけ使う。番号は内容が実際に順序を持つときだけ付ける（装飾の構造は情報があるように見せて読み手を誤らせるから）［ANT-fd］
- 見出しの上の小さな分類ラベル、字間を広げた大文字のラベル、区切りの色の帯、中黒でつないだメタ情報を、まとまりを示す装飾として使わない。まとまりは余白・揃え・見出しの階層で示し、それで足りないときだけ線や面を足す（配置で分かることを言い直すだけで、読む量が増えるから）［ANT-fd］［plusai］［AST-space］［unslop］
- 生成した画面が次の型に寄っていたら、PJ の指定でそう選んだのかを確かめる。クリーム色の背景にセリフ体と赤茶のアクセント、黒の背景に蛍光色1色、新聞風の罫線、同じ角丸と同じ影のカードの並び、全見出しの上の分類ラベル（どれも題材によらず出る既定の型で、選んだ結果ではないから。PJ の指定があればそれに従う）［ANT-fd］
- 作ったら画面を見て自己批評し、目的に効かない装飾を1つずつ削る。消しても同じくらい分かる装飾は消す［ANT-fd］［plusai］

## 1. 外枠

**外枠はアプリ全体で1回だけ決め、全画面で同じものを使う。** 画面ごとに外枠を選び直さない（ヘッダとナビゲーションの位置が画面ごとに変わると、利用者は毎回位置を探し直すから）［CBN-shell］［LIN-redesign］

### 型

| 型 | 構成 | 使う条件 | 出典 |
|---|---|---|---|
| 逆L字 | 上端のヘッダ＋左端のサイドバーが、右下の主領域を囲む | 行き先が複数あるアプリの殻。下の3つの型は、この主領域の中で使う | ［LIN-redesign］［CBN-shell］ |
| 一覧と詳細 | 一覧のペインと、選んだ項目の詳細のペインを横に並べる | 項目の一覧から1件選んで中身を読む。詳細が一覧なしでも単独で意味を持つ（メッセージ・連絡先・ドキュメント） | ［AND-canon］ |
| 主内容と補助ペイン | 主内容が幅の大半を取り、残りに主内容を支える内容を置く | 補助の内容が主内容と一緒でないと意味を持たない（文書とレビューコメント、編集対象と設定パレット） | ［AND-canon］ |
| フィード | 同等の要素をグリッドに並べる | 同じ種類の要素を大量に眺める（カード・記事の並び） | ［AND-canon］ |

- 一覧と詳細か補助ペインかは、**右側の内容が単独で成り立つか**で決める。単独で成り立つなら一覧と詳細、成り立たないなら補助ペイン（狭い幅での畳み方が逆になるから）［AND-canon］
- 既存の外枠にヘッダが無ければ足さない（外枠は変えない）。以下のヘッダの規則は、ヘッダを持つ外枠にだけ当てる
- ヘッダは画面幅いっぱいに置き、全画面で常に出す。左ほど製品内の項目、右ほど製品をまたぐ機能（検索・通知・アカウント）を置く［CBN-shell］
- 検索・通知・アカウント等のヘッダの機能は、画面によって位置を変えない［CBN-shell］
- 外枠の中のナビゲーションの型（サイドバーかタブか等）は ナビゲーションの参照 で選ぶ

### 決定表

| 主領域に出すもの | 型 |
|---|---|
| 行き先が複数ある（全画面共通） | 逆L字の殻 |
| 一覧から選んだ1件を読む／編集する。詳細だけでも意味がある | 一覧と詳細 |
| 主対象を見ながら、それに付随する情報・設定を参照する | 主内容と補助ペイン |
| 同じ種類の要素を大量に眺める | フィード |

### 狭い幅での畳み方

**区切りの幅の数値はスキルに持たない。PJ・CSSフレームワークで定めた区切りを使う。** 下は区切りを跨いだときの振る舞い。

| 型 | 広い幅 | 狭い幅 | 出典 |
|---|---|---|---|
| 一覧と詳細 | 並べる。選んだ項目を一覧側で選択中として示す | 一覧と詳細を切り替える（一覧で選ぶと詳細に替わり、戻る操作で一覧に戻る） | ［AND-canon］ |
| 主内容と補助ペイン | 並べる。主内容に幅の多くを割く | 補助を主内容の下に回すか、下から出るシートに入れる | ［AND-canon］ |
| フィード | 複数列 | 1列 | ［AND-canon］ |
| 逆L字のヘッダ | ヘッダにリンクを並べる | ヘッダのリンクをサイドバー側のメニューに移す | ［CBN-shell］ |

- 一覧と詳細で幅が狭くなったら、表示中の詳細を残して一覧を隠す。幅が広がったら一覧も出し、詳細に出している項目を一覧で選択中にする。何も選んでいない状態で広がったら、詳細側に空の領域を出す（幅の変化で利用者が見ていた対象を失わせないから）［AND-canon］
- 情報量の多い一覧・比較は、サイドバー付きの多カラムを既定にする。単一カラムに詰めて縦に伸ばさない［本環境］
- 詳細をその場で開く導線（側面のパネル・ダイアログ）を使うときは、開いた先が中身を読める幅と高さを持つことを確かめてから提示する［本環境］
- 狭い幅・ノートPC・超横長の各幅で表示を確かめる［VCL-wig］

## 2. 密度

- **密度（余白・行の高さの詰め具合）は、画面幅とは別の軸として決める**。狭い幅だから密にする、広い幅だから疎にする、と連動させない（密度はテーマとして、レスポンシブとは別の機能として扱われているから）［ATL-tokens］［ATL-space］
- 密度を切り替えられるようにするなら、余白をトークンで指定しておく（値を直書きした箇所は密度の切替に追随しないから）［ATL-space］
- 余白は用途で段階を分ける。小さい段階は部品の内側と小さな要素の間、中くらいは大きめの部品の内側、大きい段階はページのレイアウト［ATL-space］

## 3. トークン

### 3層

| 層 | 中身 | 例 |
|---|---|---|
| 値（base） | 生の値。色の段階・余白の段階 | 緑の5段目、余白の4 |
| 役割（functional） | UI上の意味。値を参照する | 成功のアイコン色、面の背景、境界線 |
| 部品（component） | 特定の部品だけで使う。役割を参照する | ボタンの背景、オーバーレイの背景 |

出典: ［PRM-tokens］

- **コードで使うのは役割のトークンか部品のトークンにする。値の層と生の値（色コード・px）を画面のコードに書かない**（直書きした値はライト／ダークの切替にも密度の切替にも追随しないから）［CBN-color］［ATL-tokens］［ATL-space］
- 部品のトークンは、その部品のスタイルの中だけで使う［PRM-tokens］
- **トークンは名前の意味で選ぶ。色が合うからという理由で選ばない**（別のテーマで値が変わったとき、意味の違うトークンは別の色になって壊れるから）［ATL-tokens］
- 背景の役割と、その上に載る文字・アイコンの役割を対で使う（面の色と上の文字色を別々に選ぶと、テーマによってコントラストが崩れるから）［M3-color］
- 余白・高さ・角丸・色の段階は決めたスケールから選び、スケールの間の値を作らない（スケールの外の値が1つ入ると、そこから揃わなくなるから）［ATL-space］［PRM-tokens］
- 新しい役割（状態色など）が要るときは、値を直書きせず役割のトークンとして追加する［ATL-tokens］［CBN-color］
- **主操作の強調とアクセント色は、操作の集まりごとに1つにする**。全部の操作を同じ強さで目立たせない（強調が並ぶと、どれが主操作か分からなくなるから）［AST-emph］［unslop］［ANT-fd］
- 入れ子の面の角丸は同心にする。内側の角丸は、外側の角丸から間の余白を引いた値にする（内側と外側の角が平行に見えないと、別々の形が重なって見えるから）［AST-shape］［unslop］［VCL-wig］

## 4. 面の重なり

- **面の区別は、面の色の明暗の段階で付ける。影は、他のUIの上に浮く要素（ダイアログ・メニュー・浮いたツールバー・動かせるカード）に限る**［ATL-elev］［M3-color］
- 浮く面には必ず影を対で付ける（ダークでは影が見えにくいが、対で使うことで明暗と影の両方で区別できるから）［ATL-elev］
- 内容のまとまりを示すために面を持ち上げない。余白か境界線で足りるなら、それを使う（持ち上げた面が増えると視覚的なノイズになるから）［ATL-elev］
- カードや境界線を足す前に、余白と揃えでまとめられないかを確かめる［AST-space］
- カードの中にカードを置かない。カードの中を分けるときは、余白・見出し・区切り線を使う［HLM］［ANT-fd］［AST-space］
- 色相をまたぐグラデーション、光彩、色付きの影、内容の後ろのぼかした色の塊を、面・文字・境界線に使わない。グラデーションは1つの色の中の明暗の差までにする［unslop］［HLM］［ANT-fd］
- 1つの面の上に置いた部品は、その面より1段上の面の色を使う（入力欄が面に溶け込まないようにするため）［CBN-color］
- 沈んだ面（カンバンの列のような下地）は、基本の面の上にだけ置く。浮いた面の中に沈んだ面を作らない［ATL-elev］
- **ダークテーマでは、高い面ほど明るくする**（前方から光が当たっている見え方にそろえ、影の代わりに明るさで高さを示すため）［ATL-elev］

## 5. 状態とフォーカス

- **hover・focus・pressed を、要素の上に半透明の層を重ねる方法で、全部品で同じように表す**。層の色は、その要素の上の文字色（前景色）を使う（部品ごとに状態の色を決めると、同じ操作が部品によって違って見えるから）［MW-ripple］
- hover・押下・フォーカスでは、通常時よりコントラストを上げる［VCL-wig］
- **フォーカスリングは `:focus-visible` で出す。キーボードで操作しているときに見え、ポインタで押したときには出ない**［MW-focus］［WCAG-247］
- **`outline: none` だけでフォーカスの表示を消さない**。消すなら同じ場所に代わりのリングを出す［VCL-wig］［WCAG-247］
- 固定ヘッダ等の固定要素でフォーカス中の要素を隠さない［VCL-wig］
- 子要素にフォーカスがある間、まとまり全体に表示を付けるときは `:focus-within` を使う［VCL-wig］
- **選択中・現在地を、色だけで示さない**。形の違い（塗りのアイコン・下線・印）か文字を併せて使う（色の区別がつかない利用者には伝わらないから）［WCAG-141］［VCL-wig］
- 選択中のアイコンには塗りの形を使い、非選択は線の形にする（塗りの面が視覚的な強調になり、色以外で選択を示せるから）［HIG-sfsymbols］
- **部品の境界線・フォーカスの表示・状態の塗りは、隣り合う色と 3:1 以上のコントラストにする**［WCAG-1411］［MWG-color］［UISDK-styles］
- 選択・ハイライトの状態は、塗りの変化・全周の枠・文字の太さの変化のように単独で読める表示にする。薄い色合いだけや、片側の色の帯だけで示さない［UISDK-styles］［WCAG-1411］

## 6. モーション

- **動きは、何が変わったか・何が原因で何が起きたかを伝えるときだけ使う**。利用者の操作に応える動き（開く・展開する・確定する）は使ってよい。利用者が起こしていない動きは控え、使うなら1か所にまとめる（全カードの hover 演出や各セクションの登場アニメーションは、注意を散らすから）［VCL-wig］［ANT-fd］
- **位置・大きさ・形の動きと、色・透明度の動きを分けて扱う**。位置・大きさは行き過ぎて戻る動き（バネの揺れ戻し）を許すが、色・透明度は目標の値を行き過ぎさせない（透明度が100%を超えて揺れることはありえないから）［M3-motion］
- 動きの速さは、動く距離と大きさで決める。小さな部品は速く、画面の一部を覆うものは中くらい、全画面の遷移は遅く［M3-motion］［CBN-motion］
- 作業に集中させる画面では、控えめで速い動き（productive）を既定にする。目立つ動き（expressive）は、ページを開く・主操作を押す等のまれで重要な場面に限る［CBN-motion］
- **`transform` と `opacity` だけを動かす。`top`・`left`・`width`・`height` を動かさない**（レイアウトの再計算が起き、動きが滑らかにならないから）［VCL-wig］
- **`transition: all` にしない**。動かすプロパティを列挙する（意図しないプロパティまで動くから）［VCL-wig］
- **`prefers-reduced-motion` に従い、動きを減らすか止めた版を用意する**（操作で起きる動きでめまい・吐き気を起こす利用者がいるから）［VCL-wig］［WCAG-233］
- 動きを止めても、同じ情報が静的な表示で伝わるようにする［CBN-motion］［WCAG-233］
- 動きは途中で止められるようにし、利用者の入力に追随させる［VCL-wig］
- 動きの起点（`transform-origin`）を、物理的に動き出す位置に合わせる（メニューは開いたボタンの側から広げる）［VCL-wig］
- 自動で始まり、5秒を超えて動き続け、ほかの内容と並んで出る表示（自動で回るカルーセル・流れるバナー）には、止める・隠すボタンを付ける。`prefers-reduced-motion` はこのボタンの代わりにならない（その設定をしていない利用者も動きを止める必要があるから）［WCAG-222］［MWG-motion］

## 7. 堅牢さ

- **flex の子で文字を省略表示するときは、その子に `min-width: 0` を付ける**（付けないと子が内容の幅より縮まず、省略されずにはみ出すから）［VCL-wig］
- 文字の入る箱は、長い内容を省略・行数制限・折り返しのどれかで受ける［VCL-wig］
- 利用者が入力する値は、短い・普通・極端に長いの3通りで表示を確かめる［VCL-wig］
- 文字を含む要素（ボタン・バッジ・タブ・カード）に固定の高さを付けない。最低限の高さが必要なら最小値で指定する（利用者が行間や字間を広げたとき、文字がはみ出すか切れるから）［WCAG-1412］［MWG-type］
- 空の文字列・空の配列で表示が崩れないようにする。空・少ない・多い・エラーの各状態を全部作る（空状態の型は 通知の参照）［VCL-wig］
- 50件を超える一覧は仮想化する［VCL-wig］
- 意図しないスクロールバーを出さない。はみ出しを直す［VCL-wig］
- 画面端の安全領域（`env(safe-area-inset-*)`）を避けて配置する［VCL-wig］
- ダークテーマでは `<html>` に `color-scheme: dark` を付ける（スクロールバー・フォーム部品の既定色をテーマに合わせるため）［VCL-wig］

## 8. 出典キー

| キー | URL | 確認 | 原文の該当文 |
|---|---|---|---|
| ANT-fd | https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md | 確認済み（2026-11-13、commit 2c5958e） | "If the brief does not identify what the product or subject matter is, identify it yourself before designing ... one concrete subject, the design's audience, and the design's primary job" / "Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it." / "Adding unnecessary typographic labels above content." / "the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow ... and gradient washes as decoration" / "template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots" / "All traits are legitimate for some briefs, but they are defaults rather than choices" / "Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet" / "Work in two passes." / "Critique your own work as you build" / "Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed." |
| 本環境 | — | 本環境の既定 | 外部の出典を持たない、本環境の運用で定めた既定（型を先に決める／情報量の多い一覧・比較はサイドバー付きの多カラム／その場で開く導線の幅と高さ） |
| LIN-redesign | https://linear.app/now/how-we-redesigned-the-linear-ui | 確認済み | "I started to focus on this inverted L-shape. It's the global chrome of the application that controls the content in the main view." |
| CBN-shell | https://carbondesignsystem.com/components/UI-shell-header/usage/ | 確認済み | "The header is persistent throughout the product experience. For each UI shell component, left-to-right translates to product-to-global." / "As a header scales down to fit smaller screen sizes, header links and menus should collapse into a left-panel hamburger menu." |
| AND-canon | https://developer.android.com/develop/ui/compose/layouts/adaptive/canonical-layouts | 確認済み | "Secondary pane content is meaningful only in relation to the primary content ... The supplementary content in the detail pane of a list‑detail layout, however, is meaningful even without the primary content" / "If an expanded-width display showing both the list and detail panes narrows to medium or compact, the detail pane remains visible and the list pane is hidden" / "For compact-width displays, place the supporting content below the main content or inside a bottom sheet." |
| ATL-tokens | https://atlassian.design/foundations/tokens/design-tokens | 確認済み | "Choose tokens based on meaning where applicable, not specific values." / "Don't use a token just because the colors appear to match. This can break the experience in other themes." / "Non-color themes are also possible: think cozy/comfortable/compact views, reduced motion" |
| ATL-space | https://atlassian.design/foundations/spacing | 確認済み | "This scale is a limited set of space values that can be used to lay out UI elements in a consistent way." / "Each space token should be used in place of the raw pixel or REM values" / "A spacing system also lays a foundation for responsive design and customisable UI density in the future" |
| ATL-elev | https://atlassian.design/foundations/elevation | 確認済み | "The highest two elevation surfaces, raised and overlay, are paired with shadows" / "the higher the elevation, the lighter the surface looks." / "Raised elevations can create visual noise, so don't use to group content when a border or white space would suffice." / "Don't apply sunken elevations on raised or overlay elevations." |
| PRM-tokens | https://primer.style/foundations/primitives/token-names | 確認済み | "Base tokens are the lowest level tokens and map directly to a raw value." / "Functional tokens represent global UI patterns." / "Component/pattern tokens should only be used in component CSS." |
| CBN-color | https://carbondesignsystem.com/elements/color/usage/ | 確認済み | "Hard coded values will not change when the mode is switched." / "A field is considered a layer on top of the background it is placed on" |
| M3-color | https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Color.md | 確認済み | "additional colors which don't represent your brand, but define your UI and ensure accessible color combinations" / "Material3 components will use the following tonal surface color roles by default (instead of elevation overlays ...)" ／ 色の役割は Primary と On Primary のように面と上の色の対で定義されている |
| M3-motion | https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md | 確認済み | "Spatial springs are used for animations that move something on screen ... Effects springs are used to animate properties such as color or opacity where the property's value should not be overshot" / "a speed should be chosen based on the animation's size or distance covered" |
| CBN-motion | https://carbondesignsystem.com/elements/motion/overview/ | 確認済み | "Productive motion is appropriate for moments when the user needs to focus on completing tasks." / "Reserve expressive motion for occasional, important moments" / "the larger the change in distance (traveled) or size (scaling) of the element, the longer the animation takes." / "Make sure there is always a way to communicate similar messages statically." |
| MW-ripple | https://raw.githubusercontent.com/material-components/material-web/main/docs/components/ripple.md | 確認済み | "A state layer is a semi-transparent covering on an element that indicates its state." ／ 既定値 `--md-ripple-hover-color` = `--md-sys-color-on-surface` |
| MW-focus | https://raw.githubusercontent.com/material-components/material-web/main/docs/components/focus-ring.md | 確認済み | "Focus rings are accessible outlines for components to show keyboard focus. Focus rings follow the same heuristics as :focus-visible to determine when they are visible." |
| HIG-sfsymbols | https://developer.apple.com/tutorials/data/design/human-interface-guidelines/sf-symbols.json | 確認済み | "The solid areas in a fill variant tend to give a symbol more visual emphasis, making it a good choice for iOS tab bars and swipe actions and places where you use an accent color to communicate selection" |
| WCAG-141 | https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | 確認済み | "Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element." |
| WCAG-247 | https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html | 確認済み | "Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible." |
| WCAG-233 | https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html | 確認済み | "Motion animation triggered by interaction can be disabled, unless the animation is essential to the functionality or the information being conveyed." |
| VCL-wig | https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/AGENTS.md | 確認済み | "SHOULD: Nested radii: child ≤ parent; concentric" / "NEVER: `outline: none` without visible focus replacement" / "NEVER: `transition: all`—list properties explicitly" / "MUST: Animate compositor-friendly props (`transform`, `opacity`) only" / "MUST: Flex children need `min-w-0` to allow truncation" / "MUST: Virtualize large lists (>50 items)" / "MUST: Honor `prefers-reduced-motion`" |
| plusai | https://plusai.com/blog/how-to-make-ai-slides-that-dont-look-like-ai-slop/ | 確認済み（2026-11-13） | "It's extraneous decoration doing the job that layout should do." / "Use whitespace to separate sections" / "if you delete the decoration and the slide is just as clear, the decoration was slop." |
| unslop | https://github.com/heydamir/unslop/blob/main/skills/unslop/SKILL.md （本環境では `skills/unslop/`） | 確認済み（2026-11-13、commit 97daa3e） | "In the chrome, one accent, used rarely. It marks the primary action, the selection or the one number that matters." / "Remove hue gradients on surfaces, gradient text, colored glows and colored shadows, radial color washes and blobs behind content, and neon borders." / "A gradient is allowed only as a small tone shift inside one neutral" / "Nested radius. An inner radius equals the outer radius minus the padding between them" ／ 兆候の一覧（references/signs.md）に uppercase tracked labels がある |
| HLM | https://github.com/Nutlope/hallmark/blob/main/skills/hallmark/SKILL.md | 確認済み（2026-11-13、commit 04977e1） | "Never an eyebrow, and never a label in tracked capitals or small caps" / "Never a purple-to-blue gradient, a card inside a card, an emoji as an icon" |
| AST-space | https://github.com/facebook/astryx/blob/main/docs/design/spatial-hierarchy.md | 確認済み（2026-11-13、commit 721dbf1。文書の状態は draft） | "DR3 — Space precedes containment. Authors SHOULD use spacing and alignment to establish groups before adding another card or boundary." |
| AST-shape | https://github.com/facebook/astryx/blob/main/docs/design/shape-relationships.md | 確認済み（同上） | "DR2 — Nested curves remain concentric. Inner and outer corners MUST read as parallel shapes after accounting for the space between them." |
| AST-emph | https://github.com/facebook/astryx/blob/main/docs/design/color-emphasis.md | 確認済み（同上） | "DR3 — Emphasis remains scarce. A local action group SHOULD expose one clear primary emphasis rather than making every action compete equally." |
| UISDK-styles | https://github.com/vercel-labs/ui/blob/main/packages/core/skills/ui-sdk/references/styles.md | 確認済み（2026-11-13、commit c53df2f） | "Style `data-selected`, `data-highlighted`, `data-checked` and the rest so the state reads on its own, at 3:1 against what's around it: a fill change, a full outline or a weight change. A faint tint alone doesn't. Don't default to a stripe down one edge." / "Control edges, focus indicators and state fills need 3:1 (WCAG 1.4.11)." |
| MWG-color | https://github.com/GoogleChrome/modern-web-guidance/blob/main/skills/modern-web-guidance/guides/visual-design/color.md | 確認済み（2026-11-13、commit 4dd9683） | "Maintain a minimum contrast ratio of 3:1 for user interface component boundaries and states (WCAG 1.4.11 Non-text Contrast)." |
| MWG-type | https://github.com/GoogleChrome/modern-web-guidance/blob/main/skills/modern-web-guidance/guides/visual-design/typography.md | 確認済み（同上） | "DON'T set a fixed `height` or `block-size` on elements that contain text, such as buttons, badges, tabs and cards. Let the content set the height, with `min-block-size` if a minimum is needed" |
| MWG-motion | https://github.com/GoogleChrome/modern-web-guidance/blob/main/skills/modern-web-guidance/guides/ui-behaviors/motion.md | 確認済み（同上） | "Any moving, blinking, or scrolling content that starts automatically, lasts more than five seconds, and is shown alongside other content needs a visible control to pause, stop, or hide it" / "`prefers-reduced-motion` doesn't replace the control" |
| WCAG-1411 | https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | 確認済み（2026-11-13） | "The visual presentation of the following have a contrast ratio of at least 3:1 against adjacent color(s): User Interface Components Visual information required to identify user interface components and states" |
| WCAG-1412 | https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html | 確認済み（2026-11-13） | "no loss of content or functionality occurs by setting all of the following and by changing no other style property" |
| WCAG-222 | https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html | 確認済み（2026-11-13） | "For any moving, blinking or scrolling information that (1) starts automatically, (2) lasts more than five seconds, and (3) is presented in parallel with other content, there is a mechanism for the user to pause, stop, or hide it" |

## 9. 未確認で外した規則

| 規則 | 外した理由 |
|---|---|
| 情報量の多い業務画面は高密度を既定にする | 根拠になる原文を見つけられなかった。Atlassian・Carbon は密度の選択肢を持つが、どれを既定にすべきかは書いていない |
| 高密度の画面ではオーバーシュートを減らす（shadcn-m3e 由来） | M3 公式の原文で確認できなかった。代わりに Carbon の productive / expressive の使い分けで同じ趣旨を書いた |
| ダークでは高い面ほど明るい（M3 側の記述） | m3.material.io の本文が取れず、M3 の原文で確認できなかった。Atlassian の原文で確認できたので、出典を Atlassian にして本文に残した |
| state layer の不透明度（hover・focus・pressed の %）、motion の ms、Carbon data table の行の高さ、補助ペインの幅の比率（Android の 70/30・50/50） | 原文で確認できたものも含め、sources.md の採否どおり数値はスキルに持たない。比率は「主内容に幅の多くを割く」とだけ書いた |
| 画面幅の区切り（window size class の dp、Carbon のブレークポイント） | sources.md の採否どおり持たない。PJ・CSSフレームワークの値を使う |
| 押下で形が変わる等の M3 Expressive 固有の演出 | sources.md の採否どおり入れない |
| unslop の数値（4px の余白の段階、サイドバーの幅、文字の太さ 400/500、easing の曲線、ms、色コード）と英語の文言・欧文書体・チャートの規則 | sources.md の採否どおり数値は持たない。文言は `/writing-ui-text`、チャートは dataviz に従う。unslop を使うときは unslop の中で扱う |
| 重ねた影（ambient＋direct）、境界線と影を背景の色相に寄せる（Vercel の Design 節） | 原文は確認したが SHOULD の見た目の好みで、ほかの出典と一致を確かめていないので入れない（入れ子の角丸は Astryx・unslop と一致したので3節に入れた） |
| shadcn の変数と M3 の役割の対応表（card = surface-container-low 等） | フレームワーク固有なので shadcn の対応付けの参照の担当。本ファイルには入れない |
| Linear の LCH・3入力（ベース色・アクセント色・コントラスト）からのテーマ生成 | 原文は確認したが、トークンの生成方法は PJ の実装判断で、型の選択の規則にならないので入れない |
