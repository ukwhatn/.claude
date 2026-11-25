# 入力から送信までを確認する

- [ ] ラベルを押して目的の入力欄を操作できるか確認する。説明を placeholder だけに任せると、入力後にその説明を見直せない。[G4-29](../references/g-state-forms.md#g4-29)・[G8-04](../references/g-state-forms.md#g8-04)
- [ ] 同名のラジオボタンが意図するグループに属しているか調べる。複数フォームをまたぐ画面では、各要素の実際の form owner も見る。[G4-24](../references/g-state-forms.md#g4-24)・[G6-19](../references/g-state-forms.md#g6-19)
- [ ] 不正な値で登録し、フォームが送信されず、どの欄を直すか分かるか確かめる。スクリプト経由の送信とボタンクリックの両方を試す。[G5-06](../references/g-state-forms.md#g5-06)・[G7-05](../references/g-state-forms.md#g7-05)
- [ ] 送信用ボタンが複数ある場合は、下書きと登録で検証条件・送信する値を確認する。Enter を押したときに使われる既定ボタンも調べる。[G5-14](../references/g-state-forms.md#g5-14)・[G7-09](../references/g-state-forms.md#g7-09)
- [ ] 送信ボタンがないフォームで Enter が効かない場合は、仕様が列挙する型の入力をフォームごとに数える。[G5-23](../references/g-state-forms.md#g5-23)
- [ ] 未入力の欄と送信に失敗した後の欄を比べる。エラーの強調が現れる時機を確認する。[G5-25](../references/g-state-forms.md#g5-25)・[G10-08](../references/g-state-forms.md#g10-08)
