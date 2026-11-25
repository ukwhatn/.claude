# 遅さの原因を切り分ける

- [ ] 測定したページ、端末、操作を記録する。入力応答、主要コンテンツの表示、予期しないレイアウト変化のどれを改善したいかを決める。[Web Vitals](../references/f-performance.md)
- [ ] 初期表示で最も大きな要素を確認する。重要画像に遅延読み込みを付けていないか、表示幅に合う画像候補をブラウザーに渡しているかを調べる。[B4-04](../references/b-visual.md#b4-04)・[B4-07](../references/b-visual.md#b4-07)
- [ ] 画像や非同期応答が届く前後を見比べる。後から表示する領域の寸法を先に確保し、操作中のボタンがずれないか試す。[F2-19](../references/f-performance.md#f2-19)・[F2-20](../references/f-performance.md#f2-20)
- [ ] 長いリストの先頭と末尾へ移動する。実際の行高、画面内の行、余分に描く行の関係を確認し、文字サイズを変えても行が重ならないかを見る。[F3-13](../references/f-performance.md#f3-13)・[仮想リストの例](../templates/virtual-list.html)
- [ ] ストリーミングでは最初に送る骨格を決め、遅い部分を境界内に置く。境界内の失敗と骨格の描画失敗を別々に試す。[F4-09](../references/f-performance.md#f4-09)・[F4-12](../references/f-performance.md#f4-12)
- [ ] サーバー側に時間制限を設ける場合、描画処理へ渡した signal と、実際に中断操作を呼ぶコントローラーの対応を確認する。[F4-16](../references/f-performance.md#f4-16)
