# 状態・フォーム・ナビゲーション

入力の所有者、送信を始めた要素、検証結果の順に調べる。ブラウザーの送信手順を確認してからアプリの処理を足す。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## React の状態設計

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g-01"></a>G-01 | アプリが大きくなったときの状態の整理 | [022](https://react.dev/learn/managing-state) |
| <a name="g-02"></a>G-02 | Reactの状態管理を学ぶ順序 | [022](https://react.dev/learn/managing-state) |
| <a name="g-03"></a>G-03 | 操作結果を状態から描画する考え方 | [022](https://react.dev/learn/managing-state) |
| <a name="g-04"></a>G-04 | 外部との同期にEffectが必要な場面 | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-05"></a>G-05 | 表示時に計算できる値の扱い | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-06"></a>G-06 | 後から届く古いレスポンスへの対処 | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-07"></a>G-07 | コンポーネントの状態を初期化する方法 | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-08"></a>G-08 | イベントとEffectの使い分け | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-09"></a>G-09 | 共通の親に状態を移す判断 | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-10"></a>G-10 | 依存する入力候補の取得と表示時の計測 | [023](https://react.dev/learn/you-might-not-need-an-effect) |
| <a name="g-11"></a>G-11 | フレームワークのデータ取得機能を選ぶ理由 | [023](https://react.dev/learn/you-might-not-need-an-effect) |

## フォームの入力支援

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g2-01"></a>G2-01 | 入力名をラベルと結び付ける方法 | [045](https://www.w3.org/WAI/tutorials/forms/labels/) |
| <a name="g2-02"></a>G2-02 | 見た目だけラベルを隠す場合の注意 | [045](https://www.w3.org/WAI/tutorials/forms/labels/) |
| <a name="g2-03"></a>G2-03 | 画面に見えない名前を使う条件 | [045](https://www.w3.org/WAI/tutorials/forms/labels/) |
| <a name="g2-04"></a>G2-04 | labelで入力欄を囲む関連付け | [045](https://www.w3.org/WAI/tutorials/forms/labels/) |
| <a name="g2-05"></a>G2-05 | ラベルと入力欄を近くに置く配置 | [045](https://www.w3.org/WAI/tutorials/forms/labels/) |
| <a name="g2-06"></a>G2-06 | 入力型を選んでも可視ラベルを残す理由 | [045](https://www.w3.org/WAI/tutorials/forms/labels/) |
| <a name="g2-07"></a>G2-07 | 関連する選択肢にグループ名を付ける方法 | [046](https://www.w3.org/WAI/tutorials/forms/grouping/) |
| <a name="g2-08"></a>G2-08 | 読み上げの差を考慮した凡例と個別ラベル | [046](https://www.w3.org/WAI/tutorials/forms/grouping/) |
| <a name="g2-09"></a>G2-09 | 入力の早期確認とサーバー側検証の役割 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-10"></a>G2-10 | HTMLを土台に検証を組み立てる方法 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-11"></a>G2-11 | 標準の制約属性と検証結果のCSS | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-12"></a>G2-12 | 必須の入力とラジオ群の確認 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-13"></a>G2-13 | 空値・文字列パターン・入力型の検証 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-14"></a>G2-14 | 妥当性の項目をAPIで調べる方法 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-15"></a>G2-15 | ブラウザ既定のエラー表示を置き換える場合 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-16"></a>G2-16 | エラーメッセージの具体性と入力形式の許容範囲 | [042](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Form_validation) |
| <a name="g2-17"></a>G2-17 | フォームを短く保ち、必要な制限時間を調整できるようにする | [041](https://www.w3.org/WAI/tutorials/forms/) |
| <a name="g2-18"></a>G2-18 | ラベルとグループが入力方法ごとに果たす役割 | [041](https://www.w3.org/WAI/tutorials/forms/) |

## URL と履歴

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g3-01"></a>G3-01 | ウィンドウで利用する履歴操作API | [060](https://developer.mozilla.org/en-US/docs/Web/API/History) |
| <a name="g3-02"></a>G3-02 | 履歴件数・状態・スクロール復元の参照 | [060](https://developer.mozilla.org/en-US/docs/Web/API/History) |
| <a name="g3-03"></a>G3-03 | 履歴移動と再読み込みの使い分け | [060](https://developer.mozilla.org/en-US/docs/Web/API/History) |
| <a name="g3-04"></a>G3-04 | 履歴に持たせられるデータ | [060](https://developer.mozilla.org/en-US/docs/Web/API/History) |
| <a name="g3-05"></a>G3-05 | 追加した履歴に戻ったときの状態通知 | [061](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState) |
| <a name="g3-06"></a>G3-06 | 履歴状態に大きな値を持たせる場合 | [061](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState) |
| <a name="g3-07"></a>G3-07 | pushStateの引数とURLの扱い | [061](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState) |
| <a name="g3-08"></a>G3-08 | 履歴更新で発生する例外 | [061](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState) |
| <a name="g3-09"></a>G3-09 | フラグメント操作と履歴APIの挙動差 | [061](https://developer.mozilla.org/en-US/docs/Web/API/History/pushState) |
| <a name="g3-10"></a>G3-10 | SPAの遷移を扱うNavigation API | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) |
| <a name="g3-11"></a>G3-11 | 遷移開始の検出と傍受の条件 | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) · [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-12"></a>G3-12 | 遷移確定前後に実行できる処理 | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) |
| <a name="g3-13"></a>G3-13 | 傍受した遷移の成否通知 | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) |
| <a name="g3-14"></a>G3-14 | 履歴項目の取得と破棄の検出 | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) |
| <a name="g3-15"></a>G3-15 | 遷移の確定と完了を待つ二つのPromise | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) · [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-16"></a>G3-16 | 各履歴項目の状態を更新する経路 | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) |
| <a name="g3-17"></a>G3-17 | 初回読み込みとフレームごとの制約 | [062](https://developer.mozilla.org/en-US/docs/Web/API/Navigation_API) |
| <a name="g3-18"></a>G3-18 | 履歴を追加・置換する仕様手順 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-19"></a>G3-19 | 履歴状態の追加数に上限がある場合 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-20"></a>G3-20 | URLを書き換えられる範囲の比較 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-21"></a>G3-21 | 復元方式を早期に指定する理由 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-22"></a>G3-22 | Navigation APIが扱う履歴の境界 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-23"></a>G3-23 | 遷移イベントの発火とキャンセルの例外 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-24"></a>G3-24 | 傍受できるURLと中断シグナル | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-25"></a>G3-25 | 確定前の中止と確定後の完了処理 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-26"></a>G3-26 | 傍受時のスクロールを任せるか制御するか | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-27"></a>G3-27 | 傍受が遷移先の同一文書フラグに与える影響 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-28"></a>G3-28 | 新しいウィンドウを開く処理と戻り値 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-29"></a>G3-29 | ポップアップ指定の解釈 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-30"></a>G3-30 | Locationの値の参照を保護する仕組み | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-31"></a>G3-31 | 読み込み中のLocation変更と履歴の置換 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-32"></a>G3-32 | Locationの遷移・置換・再読込のチェック | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-33"></a>G3-33 | 同じフラグメントを設定した場合の扱い | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-34"></a>G3-34 | Historyの主要メソッドの仕様 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-35"></a>G3-35 | 履歴の相対移動を処理する順序 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-36"></a>G3-36 | Windowごとの遷移オブジェクトとイベント | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-37"></a>G3-37 | navigateの状態引き渡しとPromiseの結果 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-38"></a>G3-38 | reloadと既存項目への移動の完了条件 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-39"></a>G3-39 | navigateで早期に返るエラー | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-40"></a>G3-40 | 履歴項目のキー・ID・状態の寿命 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-41"></a>G3-41 | 前後移動の可否と状態だけを更新するAPI | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-42"></a>G3-42 | 傍受後にフォーカスとスクロールを処理する手順 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-43"></a>G3-43 | 文書間遷移の開始側・表示側イベント | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-44"></a>G3-44 | 復元されなかったページの情報を読む方法 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |
| <a name="g3-45"></a>G3-45 | 履歴キャッシュに保存できなかった理由 | [063](https://html.spec.whatwg.org/multipage/nav-history-apis.html) |

## 入力の種類と自動入力

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g4-01"></a>G4-01 | 入力欄と隠し値で異なるautocompleteの意味 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-02"></a>G4-02 | autocompleteで使える値と隠し欄の制約 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-03"></a>G4-03 | 複数の配送先を別々に自動入力する方法 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-04"></a>G4-04 | 請求先・配送先の区別とパスキー候補 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-05"></a>G4-05 | フォームから継承する自動入力の設定 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-06"></a>G4-06 | 氏名などを細分化しすぎない理由 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-07"></a>G4-07 | 国ごとの住所階層に対応した入力欄 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-08"></a>G4-08 | ブラウザが自動入力候補を整理する単位 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-09"></a>G4-09 | autocomplete が off のとき、過去の値を記憶したり候補に出したりしないことはブラウザーへの推奨。 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-10"></a>G4-10 | 氏名や連絡先をグループ内で矛盾なく埋める規則 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-11"></a>G4-11 | 自動入力グループ名をブラウザが解釈しない理由 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-12"></a>G4-12 | 自動入力を実行できる欄と値の条件 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-13"></a>G4-13 | 候補が入力欄の制約を満たすための変換 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-14"></a>G4-14 | 入力欄の種類と情報に応じた候補の選び方 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-15"></a>G4-15 | 未指定・未知のinput型の扱い | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-16"></a>G4-16 | 入力後に既定値を変える場合とリセット | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-17"></a>G4-17 | readonlyが効く入力型の違い | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-18"></a>G4-18 | 隠し入力が検証と入力イベントの対象外となる理由 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-19"></a>G4-19 | 検索欄と通常の一行テキストの違い | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-20"></a>G4-20 | 電話番号の許容書式を決める方法 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-21"></a>G4-21 | URLとメール欄で許容される値 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-22"></a>G4-22 | 厳密な数値と概値を入力する欄の違い | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-23"></a>G4-23 | 見た目が中間状態になるチェック欄と二態のスイッチ | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-24"></a>G4-24 | ラジオボタンが同じ選択群に属する条件 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-25"></a>G4-25 | 選択ファイル名の読み書きと個数の制約 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-26"></a>G4-26 | 送信ボタンの既定ラベルと検証を飛ばす指定 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-27"></a>G4-27 | 文字数・正規表現・刻み幅の入力制約 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-28"></a>G4-28 | datalistの候補表示と検証の違い | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-29"></a>G4-29 | 入力欄の名前と補足を表示する場所 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-30"></a>G4-30 | 変更時と確定時で異なる入力イベント | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-31"></a>G4-31 | 自動入力とスクリプト更新で異なるイベント通知 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-32"></a>G4-32 | inputの型と対応するデータの一覧 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-33"></a>G4-33 | 属性やメソッドを使えるinput型を調べる箇所 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-34"></a>G4-34 | 擬似クリックによる入力コントロールの動作 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-35"></a>G4-35 | チェック操作をキャンセルした際の選択状態 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-36"></a>G4-36 | input型の変更で引き継ぐ値と選択範囲 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-37"></a>G4-37 | checkedとは別に設定される中間表示 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-38"></a>G4-38 | チェックとスイッチのドラッグが発火するイベント | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-39"></a>G4-39 | ラジオ群の選択を排他的にする契機 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-40"></a>G4-40 | 複数メールアドレスを空白除去して保存する手順 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-41"></a>G4-41 | カラーピッカーの色空間を切り替える属性 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-42"></a>G4-42 | 色入力の透過と保存形式を決める規則 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-43"></a>G4-43 | ファイル入力で選択可能な形式を伝える方法 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-44"></a>G4-44 | 送信ボタンの起動時に確認される条件 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-45"></a>G4-45 | 画像ボタンの既定寸法と送信座標 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-46"></a>G4-46 | 画像ボタンのクリック位置を受け取る項目名 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-47"></a>G4-47 | 画像ボタンで選んだ位置を記録する時点 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-48"></a>G4-48 | 画像ボタンのリソース取得と完了通知 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-49"></a>G4-49 | 入力欄の書字方向を変更した場合の通知 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-50"></a>G4-50 | 数値・日時入力を地域に合わせて表示する方針 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-51"></a>G4-51 | 入力型によって変わるvalueの読み書き | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-52"></a>G4-52 | チェック済みの既定値と操作後の状態を分ける印 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-53"></a>G4-53 | checkedと選択ファイル一覧の参照 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-54"></a>G4-54 | 日付・数値に変換して入力値を扱うAPI | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-55"></a>G4-55 | 刻み幅で上下させた値の丸めと境界 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-56"></a>G4-56 | スクリプトからピッカーを開ける条件 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-57"></a>G4-57 | ファイル選択の起動・中断と通知 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-58"></a>G4-58 | 連続入力でinput通知をまとめる余地 | [084](https://html.spec.whatwg.org/multipage/input.html#the-input-element) |
| <a name="g4-59"></a>G4-59 | 自動入力の指定順とフィールド名の選択 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-60"></a>G4-60 | 氏名・住所の自動入力に使うデータ形式 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-61"></a>G4-61 | 支払い情報を自動入力する欄と形式 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-62"></a>G4-62 | 通貨・金額・言語・生年月日の自動入力 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-63"></a>G4-63 | 電話・メール・URLを自動入力する形式 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-64"></a>G4-64 | コントロールと自動入力トークンの組み合わせ | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-65"></a>G4-65 | 自動入力で選択ボックスに使える値の分類 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-66"></a>G4-66 | 生年月日全体を月入力欄に指定できない理由 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-67"></a>G4-67 | ブラウザがautocompleteの指定を解析する順序 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-68"></a>G4-68 | 自動入力トークンを普通の欄・連絡先・認証に分類する規則 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-69"></a>G4-69 | 複数メール・テキスト・選択ボックスの保存単位 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-70"></a>G4-70 | 隠し欄の値を候補選択に利用する規則 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-71"></a>G4-71 | 同一住所や国を参照する複数欄の整合 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-72"></a>G4-72 | 隣接するユーザー名・パスワード欄から入力目的を推測する場合 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-73"></a>G4-73 | DOMから読んだautocomplete値の正規化 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-74"></a>G4-74 | autocompleteを無効に指定する場面 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-75"></a>G4-75 | onと目的付き自動入力指定の違い | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |
| <a name="g4-76"></a>G4-76 | 隠し入力で値の種類を伝える指定 | [083](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#autofill) |

## 制約検証と送信

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g5-01"></a>G5-01 | 制約検証の対象となるコントロール | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-02"></a>G5-02 | 任意の入力エラーを設定する方法 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-03"></a>G5-03 | ブラウザが区別する入力エラーの種類 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-04"></a>G5-04 | 無効化された入力にも状態が残る場合 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-05"></a>G5-05 | 検証結果の収集と利用者への報告の違い | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-06"></a>G5-06 | checkValidityが発火するイベントと成否 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-07"></a>G5-07 | 入力を直したときに独自エラーを消す方法 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-08"></a>G5-08 | 変化を反映するValidityStateオブジェクト | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-09"></a>G5-09 | reportValidityによる通知とフォーカス | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-10"></a>G5-10 | ユーザー向けの検証メッセージの取得 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-11"></a>G5-11 | 入力をサーバー側で再検証する理由 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-12"></a>G5-12 | 検証の用語・手順・APIを引く順序 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-13"></a>G5-13 | 送信方法とフォームのデータ形式 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-14"></a>G5-14 | Enterなどで送信ボタンが起動する条件 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-15"></a>G5-15 | 検証やイベント処理後に送信を見送る条件 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-16"></a>G5-16 | 送信先URLを決めて遷移を予約する手順 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-17"></a>G5-17 | GET・POSTに使われるデータの位置と形式 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-18"></a>G5-18 | フォーム項目の文字列と添付ファイルの表現 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-19"></a>G5-19 | 送信対象のコントロールを集める順序 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-20"></a>G5-20 | 送信に使う文字エンコーディングの選択 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-21"></a>G5-21 | どのボタンがフォームを送信したか調べる方法 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-22"></a>G5-22 | 送信予定のデータをイベントで加工する方法 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-23"></a>G5-23 | 送信ボタンがないフォームの暗黙的送信 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#implicit-submission) |
| <a name="g5-24"></a>G5-24 | 送信を始める前に確認される制約 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-25"></a>G5-25 | 検証の前に入力の利用者操作状態を更新する規則 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-26"></a>G5-26 | 送信イベントでページが変わった場合の再判定 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-27"></a>G5-27 | ダイアログを閉じるフォームの戻り値 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) · [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g5-28"></a>G5-28 | 送信先・遷移先ウィンドウ・openerの選択 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-29"></a>G5-29 | URL方式と送信メソッドの組み合わせ | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-30"></a>G5-30 | 予約済みのフォーム遷移を置き換える条件 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-31"></a>G5-31 | 通常の送信とメール用URLの組み立て | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-32"></a>G5-32 | 集計から除外される入力と送信画像の座標 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-33"></a>G5-33 | 入力型によって変わる送信値 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-34"></a>G5-34 | 未選択のファイルと書字方向を送る場合 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-35"></a>G5-35 | formdataイベントの通知から返却まで | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-36"></a>G5-36 | 文字コード指定の正規化と既定値 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-37"></a>G5-37 | 項目名・値の改行とファイル名の変換 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-38"></a>G5-38 | 添付対応フォームの境界と文字エスケープ | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-39"></a>G5-39 | プレーンテキスト送信を機械で解釈しにくい理由 | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-40"></a>G5-40 | 送信ボタン情報と送信予定データのイベント | [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g5-41"></a>G5-41 | 不正な入力を進行順に集める静的検証 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-42"></a>G5-42 | 対話的検証でどのエラーを表示するか | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-43"></a>G5-43 | 独自メッセージ内の改行の正規化 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-44"></a>G5-44 | 要素の検証に失敗した場合のイベント | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-45"></a>G5-45 | 不正な入力を利用者に報告する条件 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-46"></a>G5-46 | カスタムフォーム要素の検証APIに必要な条件 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |
| <a name="g5-47"></a>G5-47 | エラーメッセージが空文字になる条件 | [087](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#constraints) |

## フォームの所有関係と共通属性

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g6-01"></a>G6-01 | フォーム外のコントロールをフォームに結び付ける方法 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-02"></a>G6-02 | 要素の移動やID変更と所属フォームの再判定 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-03"></a>G6-03 | form属性の参照が優先される条件 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-04"></a>G6-04 | HTMLパーサーと入れ子のフォームの特殊例 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-05"></a>G6-05 | 通常要素とカスタム要素から所属フォームを参照する方法 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-06"></a>G6-06 | 送信フィールド名として使えない値 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-07"></a>G6-07 | 文字エンコーディング名を送信する隠し欄 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) · [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g6-08"></a>G6-08 | 入力名とフォームの組み込みプロパティの衝突 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-09"></a>G6-09 | 入力欄の書字方向を送信に含める方法 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-10"></a>G6-10 | 最大文字数とtextareaの改行の数え方 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-11"></a>G6-11 | 最小文字数と任意入力の組み合わせ | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-12"></a>G6-12 | 無効化がイベントと検証に及ぼす影響 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-13"></a>G6-13 | ボタンごとにフォーム全体の送信設定を上書きする方法 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-14"></a>G6-14 | フォームと送信ボタンから送信先を決める規則 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-15"></a>G6-15 | GET・POST・ダイアログを閉じる指定の扱い | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-16"></a>G6-16 | エンコード形式の既定値と上書き | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-17"></a>G6-17 | 検証を行わずに保存できる送信ボタン | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-18"></a>G6-18 | DOM接続前のフォーム参照をまとめて更新しない条件 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-19"></a>G6-19 | 所属フォームを選び直す仕様手順 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-20"></a>G6-20 | どの要素が送信属性を上書きできるか | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-21"></a>G6-21 | 送信メソッドとして指定できるキーワード | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-22"></a>G6-22 | URLエンコードと添付対応の形式の比較 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-23"></a>G6-23 | 送信先プロパティに空の値を指定した場合 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |
| <a name="g6-24"></a>G6-24 | フォーム要素にdisabledを直接指定できる範囲 | [091](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#association-of-controls-and-forms) |

## フォームとフィールドセット

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g7-01"></a>G7-01 | フォーム要素から使えるDOM API | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-02"></a>G7-02 | フォーム要素が表す文書上の役割 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-03"></a>G7-03 | フォームの文字コード・名前・自動入力・relの指定 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-04"></a>G7-04 | フォームを名前で検索する際の画像ボタンの例外 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-05"></a>G7-05 | submit() は対話的検証と submit イベントを省く。通常の送信操作を再現するなら requestSubmit() を確認する。 | [092](https://html.spec.whatwg.org/multipage/forms.html#dom-form-requestsubmit) · [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g7-06"></a>G7-06 | form.elementsに含まれるコントロール | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-07"></a>G7-07 | フォーム要素が記憶した名前の優先順 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-08"></a>G7-08 | 所属が変わったコントロールの古い名前の削除 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-09"></a>G7-09 | 送信・再送信要求・リセットのAPI手順 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-10"></a>G7-10 | フォーム全体を検証して通知する方法 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-11"></a>G7-11 | GET送信用の検索フォームを組み立てる例 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-12"></a>G7-12 | フィールドセットが公開するDOM API | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-13"></a>G7-13 | fieldsetのグループ名を与えるlegend | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-14"></a>G7-14 | フィールドセットを無効にした場合の凡例の例外 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-15"></a>G7-15 | フィールドセットの所属と配下のコントロールを調べる方法 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-16"></a>G7-16 | フィールドセットにある妥当性検証API | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-17"></a>G7-17 | 凡例の入力で内側のフォーム群を有効化する例 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-18"></a>G7-18 | 凡例の中に見出しを置くマークアップ例 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-19"></a>G7-19 | fieldsetとoptgroupで異なるlegendの役割 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-20"></a>G7-20 | 凡例要素からフォームを参照できる条件 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-21"></a>G7-21 | formの配置条件と内部に置ける要素 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-22"></a>G7-22 | フォーム単位で自動入力の既定を決める値 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-23"></a>G7-23 | フォームに公開される名前一覧の収集・整列 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-24"></a>G7-24 | 名前付きアクセスで一つの要素か一覧を返す規則 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-25"></a>G7-25 | requestSubmitの引数と例外 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-26"></a>G7-26 | フォームのリセットを再入させない手順 | [092](https://html.spec.whatwg.org/multipage/forms.html#the-form-element) |
| <a name="g7-27"></a>G7-27 | fieldsetのコンテンツモデルと属性 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-28"></a>G7-28 | フィールドセット自身と祖先による無効化 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |
| <a name="g7-29"></a>G7-29 | legendを配置できる親と内容の制約 | [093](https://html.spec.whatwg.org/multipage/form-elements.html#the-fieldset-element) |

## ラベル付け

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g8-01"></a>G8-01 | ラベル要素が公開するDOMプロパティ | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-02"></a>G8-02 | labelの中に入れられる要素の制約 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-03"></a>G8-03 | 入力の名前をlabelで付ける二通りの方法 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-04"></a>G8-04 | forで参照するIDを解決する規則 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-05"></a>G8-05 | forがないラベルで対象を選ぶ規則 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-06"></a>G8-06 | ラベル内の別の操作要素を起動した場合 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-07"></a>G8-07 | クリックしたラベルから入力に行われる操作の違い | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-08"></a>G8-08 | ラベルが指す入力と所属フォームの参照 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-09"></a>G8-09 | コントロールに結び付いたラベル一覧 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-10"></a>G8-10 | カスタムフォーム要素からラベルを取得する方法 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |
| <a name="g8-11"></a>G8-11 | 入力型の切替が既存のラベル一覧に与える影響 | [095](https://html.spec.whatwg.org/multipage/forms.html#the-label-element) |

## ボタンの役割と命令

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g9-01"></a>G9-01 | ボタンの中に別の操作要素を入れないための要件 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-02"></a>G9-02 | ボタン要素の命令用DOM API | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-03"></a>G9-03 | ボタンの種類と起動時の役割 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-04"></a>G9-04 | 既定のbuttonがフォーム送信になる条件 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-05"></a>G9-05 | ポップオーバーやダイアログに送れる命令 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-06"></a>G9-06 | 命令と対象要素の適合性を判断する規則 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-07"></a>G9-07 | ボタン起動から送信や命令に分岐する条件 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-08"></a>G9-08 | ボタンの所属と送信動作を制御する属性 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-09"></a>G9-09 | commandのDOM値と送信ボタンの値 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-10"></a>G9-10 | button.typeの実際の戻り値 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-11"></a>G9-11 | ボタン向けの制約検証プロパティ | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |
| <a name="g9-12"></a>G9-12 | ヒントやポップオーバーを開くボタンの例 | [098](https://html.spec.whatwg.org/multipage/form-elements.html#the-button-element) |

## 入力状態を表すセレクター

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="g10-01"></a>G10-01 | :enabledと:disabledの対象 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-02"></a>G10-02 | チェック済み・選択済みを表すCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-03"></a>G10-03 | 三態チェックや未確定の進捗に対応するCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-04"></a>G10-04 | 既定の送信ボタンや選択肢を表すCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-05"></a>G10-05 | プレースホルダーの表示中に当たるCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-06"></a>G10-06 | 入力とフォームを妥当と判定する規則 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-07"></a>G10-07 | 無効な入力があるフォームとフィールドセットのCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-08"></a>G10-08 | 利用者の入力に応じて妥当性を示すCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) · [088](https://html.spec.whatwg.org/multipage/form-control-infrastructure.html#form-submission-2) |
| <a name="g10-09"></a>G10-09 | 数値などの範囲内外を表すCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-10"></a>G10-10 | 必須入力と任意入力のCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-11"></a>G10-11 | ブラウザの自動入力を示すCSSと編集後の扱い | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-12"></a>G10-12 | 編集可能な要素を判定するCSS | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-13"></a>G10-13 | 実際に無効化されている要素の選択 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-14"></a>G10-14 | 進捗値が定まっていないprogressの選択 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-15"></a>G10-15 | ヒントを表示中のtextareaの選択 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-16"></a>G10-16 | fieldsetの妥当性に影響する子孫 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-17"></a>G10-17 | 必須指定のtextareaを選ぶ規則 | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
| <a name="g10-18"></a>G10-18 | 任意入力扱いになるコントロール | [099](https://html.spec.whatwg.org/multipage/semantics-other.html#pseudo-classes) |
