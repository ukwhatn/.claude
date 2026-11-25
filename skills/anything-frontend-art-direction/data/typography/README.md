# 書体事例データ

247作品・292記録の書体に関する調査です。[catalog.sqlite3](catalog.sqlite3) はSQLite、[findings.csv](findings.csv) はExcelで開けるBOM付きUTF-8です。フォントや資料の複製は収録していません。原典URLを開き、版・部位・根拠と限界を確認してください。記録の確認日 2026-11-22 は調査・整理の日で、各原典の個別取得時刻ではありません。

<!-- usage-depth:start -->
## 文字の使い方と理由

[usage-depth.csv](usage-depth.csv) とSQLiteの `usage_depth` は、247作品を1作品1行で、対象・文字の処理・理由を記録しています。実作品または現行Webを対象にした 190 作品のうち、場面を確認したものは 190、字形・大きさ・配置などの具体まで確認したものは 162、同じ処理と制作者・発注者の理由が結び付いたものは 46 です。累積数であり、理由までの数は具体までの数に含まれます。排他的には、場面のみ 28、具体まで 116、理由まで 46 です。

書体開発・試験のみ 4、文字対象外 20、未確認 33 は実使用の集計に含めません。実使用の理由まで確認したものの目的は、表現 29、実用 14、両方 3 です。制作者が明示した対象に限定し、実測された効果を意味しません。

以前の「固有名を確認できた34作品」のうち、実使用の代表例に何らかの文字処理の理由があるのは 14 作品です。そのうち、**同じ書体と処理**に理由が結び付くのは 10 作品です。別部位の書体名と匿名の文字処理の理由を結び付けていません。書体開発・試験のみで同じ書体と理由が結び付く 4 作品は別に数えます。

```sql
-- 実作品・現行Webでの累積数と排他的な深さ
SELECT level, COUNT(*) FROM usage_depth
WHERE scope IN ('production', 'current_web') GROUP BY level ORDER BY level;

-- 同じ書体と処理に理由が結び付いた実使用の作品
SELECT DISTINCT d.work_id, n.font_name
FROM usage_depth d JOIN usage_depth_fonts n USING (work_id)
JOIN findings f ON f.work_id=d.work_id AND f.font_name=n.font_name
WHERE d.scope IN ('production','current_web') AND d.level=3
  AND f.status IN ('named_font','typeface_work','rendered_font');

-- 固有名を確認した作品のうち、代表例に何らかの理由がある作品
SELECT COUNT(DISTINCT d.work_id) FROM usage_depth d JOIN findings f USING(work_id)
WHERE d.scope IN ('production','current_web') AND d.level=3
  AND f.status IN ('named_font','typeface_work','rendered_font') AND f.font_name<>'';
```

深さ0は該当箇所が未確認または対象外、1は文字の場面、2はその部位の具体、3は具体と理由まで確認したものです。`scope` は制作時の実作品・作者説明（`production`）、現行画面の観測（`current_web`）、書体の設計・試験（`typeface_design`）、文字対象外（`out_of_scope`）、未確認（`unresolved`）を分けます。`reason_fonts` は理由と直接結び付く書体だけをJSON配列で記録し、理由のない行や匿名の表現は空配列です。`rationale_kind` の `expression`・`practical`・`both` は同じ処理に示された目的です。各行の出典・限界を参照してください。
<!-- usage-depth:end -->


固有名を確認できた作品は34件で、原典などでの使用確認18件、書体自体の制作・研究4件、実描画の確認12件です。この版では3区分の重複はありません。作品を下記の優先順位で一つずつ分類すると、固有名確認34、名称未確認の専用書体5、描き文字8、分類のみ5、CSS指定のみ4、未特定169、原典未取得1、文字対象外21です。

SQLiteでは `works` が作品、`findings` が版・部位・出典ごとの記録です。1作品に複数行あり、作品数は `COUNT(DISTINCT work_id)` で数えます。`status_definitions` と `access_definitions` に各判定と確認方法の説明があります。

```sql
-- 書体名から、作品と該当箇所を探す
SELECT w.title, f.edition, f.role, f.status, f.source_url, f.limitation
FROM findings AS f JOIN works AS w USING (work_id)
WHERE f.font_name LIKE '%ゴシック%';

-- ゲームの事例を、確認状態と一緒に探す
SELECT w.title, w.region, w.year_label, f.role, f.status, f.font_name, f.source_url
FROM works AS w JOIN findings AS f USING (work_id)
WHERE w.medium LIKE '%ゲーム%' ORDER BY w.seq;

-- 状態ごとの作品数（同じ作品が複数の状態に含まれ得る）
SELECT status, COUNT(DISTINCT work_id) AS works
FROM findings GROUP BY status ORDER BY works DESC;

-- 固有名を一次資料または実描画で確認できた作品数
SELECT COUNT(DISTINCT work_id) AS named_works FROM findings
WHERE status IN ('named_font', 'typeface_work', 'rendered_font') AND font_name <> '';

-- 1作品を1分類に集計する
SELECT classification, COUNT(*) AS works
FROM work_classification GROUP BY classification ORDER BY works DESC;

-- 一作品の根拠をまとめて見る
SELECT edition, role, status, font_name, access, source_url, locator, evidence, limitation
FROM findings WHERE work_id = 'JP-GAME-001';
```

CSVの列は `seq`＝台帳順、`work_id`＝作品ID、`title`＝作品名、`region`＝地域キー、`medium`＝媒体、`year_label`＝年表記、`edition`＝版、`role`＝対象部位・役割、`status`＝判定、`font_name`＝書体名、`category`＝分類、`source_url`＝原典URL、`locator`＝該当箇所、`access`＝確認方法、`evidence`＝根拠、`limitation`＝限界、`checked_date`＝確認日です。地域・媒体・年は台帳の表記をそのまま保持し、全制作者の国籍や確定した制作年を意味するとは限りません。

`named_font` は原典が使用を示す固有名、`typeface_work` は書体自体の制作・研究、`lettering` は描き文字です。`custom_unnamed` と `class_only` は固有名が確認できない記録です。`css_declared` は指定候補であり、`rendered_font` は特定環境で実際に描画された書体です。PDFの内部フォント名を調べた場合は、PDFファイル内の文字に関する情報であり、作品画像の中で使われた書体を自動的に証明するものではありません。

「固有名を確認できた作品」は `named_font`・`typeface_work`・`rendered_font` のいずれかに固有名がある作品を一度だけ数えます。`css_declared` は実描画を示さないため含めません。作品内の別部位に `unidentified` があっても、確認できた部位があればこの集計に含まれます。

`work_classification` は同じ作品を一度だけ数える便宜上の分類です。複数の判定がある場合は、固有名確認、名称未確認の専用書体、描き文字、分類のみ、CSS指定のみ、未特定、原典未取得、文字対象外の順で最初に当てはまる分類を使います。作品全体がその一種類に限られるという意味ではありません。ビューの定義はSQLiteの `sqlite_schema` で確認できます。

`unidentified` は確認した資料では特定できなかったもの、`unavailable` は資料を取得できなかったもの、`no_text_scope` は確認対象が文字を扱わないものです。未特定は書体が使われていないことを意味しません。掲載時点と現行版の違い、資料が対象とする部分、読み取り方法は各行を参照してください。
