---
name: writing-code
description: コードを書く時の実装原則（deep module設計・seam・テスタビリティ・シーム限定TDD・リーダブルコード）。非自明なプロダクションコードの新規実装・機能追加・リファクタの開始時に使用。TypeScript/Python/Goの言語別ガイドをreferencesに同梱。境界: バグ・エラーの原因調査はsystematic-debuggingが先（原因特定後の修正実装は本スキル）、提出前のdiff確認はself-review、要件定義はdesign-feature。UIの意匠はui-ux-design、DBスキーマ変更はdatabase-migrationと併用する。
---

# Writing Code

人間に読みやすいコードは、生成AIにとっても読み・変更しやすい。本スキルは、コードを書く時の設計判断を毎回同じプロセスに固定する。

バグ・エラーの修正では、先に `/systematic-debugging` スキルで根本原因を特定し、修正の実装段階で本スキルの原則に従う。

## 実装前ゲート: 既存パターンの確認と踏襲

コードを書き始める前に実行する:

1. **同類の既存実装を特定して読む** — 類似画面・類似Usecase・類似moduleを探し、そのパターン（構成・命名・エラーハンドリング・セキュリティ処理・依存の受け渡し方）を確認する
2. **適切な理由がない限り踏襲する** — 「シンプルだから」「今回は例外」は理由にならない。本スキルの設計原則と既存パターンが食い違う場合も、既存パターンが勝つ
3. **逸脱はユーザー確認を経てのみ** — 既存パターンが明らかな技術的負債になると判断した場合に限り、負債と考える根拠を添えてユーザーに確認を取った上で（Claude Code: AskUserQuestion）逸脱してよい。無断の逸脱は禁止

完了基準: 参照した既存実装のパスを挙げられる（新規PJ等で同類実装が存在しない場合はその旨を記録）。逸脱する場合はユーザー確認済みである。

## 設計語彙（Glossary）

設計判断の記述・議論では以下の用語を正確に使う。**コード上の既存命名・フレームワーク公式用語（React component 等）はそのまま尊重する**（既存パターン踏襲と両立させる）。

- **Module** — interfaceとimplementationを持つすべて。スケール非依存: 関数・クラス・パッケージのどれでもよい。設計議論で unit / component / service と言い換えない
- **Interface** — 呼び出し側がmoduleを正しく使うために知るべき**全て**。型シグネチャに加え、不変条件・呼び出し順序の制約・エラーモード・必要な設定・性能特性を含む
- **Seam**（Feathers） — その場所を編集せずに振る舞いを差し替えられる場所。interfaceが住む位置。boundaryと言わない（DDDのbounded contextと衝突するため）
- **Depth** — interfaceにおけるleverage。呼び出し側が学ぶinterface量あたりに引き出せる振る舞いの量。実装行数とinterface行数の比ではない（水増しを誘発するため）
- **Adapter** — seamでinterfaceを満たす具体物。役割の名前であり、中身の大小は問わない

## 設計原則

1. **Deep moduleを設計する** — 小さいinterfaceの背後に多くの振る舞いを置く。interfaceを設計する時に自問する: メソッド数を減らせるか / パラメータを単純化できるか / より多くの複雑さを内側に隠せるか
2. **The deletion test** — そのmoduleを削除したと想像する。複雑さが消えるなら通過型（pass-through）であり不要。複雑さがN箇所の呼び出し側に再出現するなら、moduleは価値を生んでいる
3. **The interface is the test surface** — 呼び出し側とテストは同じseamを通る。interfaceの内側をテストしたくなったら、moduleの形が間違っているサイン
4. **One adapter = hypothetical seam. Two adapters = real seam.** — 実際に差し替わらないものにseam（port・抽象層）を作らない。adapterが1つしかないseamはただの間接参照であり、Speculative Generality（投機的一般化）
5. **依存は生成せず受け取る（DI）** — module内部で依存をnew・生成せず、引数で受け取る。時刻・乱数も依存として扱う
6. **副作用より戻り値** — 引数を変異させたり外部状態を書き換えるより、結果を値として返す。テスト容易性と参照透過性が上がる

## リーダブルコード原則

- **命名**: 名前だけで役割が分かること。プロジェクトの用語集（CONTEXT.md等があれば）と一致させ、同じ概念には全体で同じ語を使う
- **docstring**: 既存形式（JSDoc / docstring）を踏襲。本スキルで書き方を重複定義しない

### コメントは **Why のみ**（What / How は書かない）

コードを読めば分かる What / How をコメントに書くのは、二重メンテナンスの負債・コード変更時の陳腐化リスク・レビュー時のノイズを増やすだけ。**削除するとレビュアーが混乱するか**を自問し、混乱しないなら書かない。

**書かない例（Anti-pattern）:**

```typescript
// ❌ 名前と重複（What）
// ユーザーを取得
const user = getUser(id);

// ❌ How をなぞる
// i を 1 増やす
i++;

// ❌ 明白な null チェック
// null チェック
if (user == null) return;

// ❌ 関数名と重複する docstring
/**
 * getUser
 * ユーザーを取得する
 * @returns User
 */
function getUser(id: string): User { ... }

// ❌ タスク/PR 番号や依頼者を書く（履歴は git / PR にある）
// PR #123 で追加
// used by X
```

**書く例（Why）:**

```typescript
// ✅ workaround の理由（外部要因）
// Cloudflare Workers の instanceof が bundler で false を返すことがあるため name 判定を併用
if (err instanceof DomainError || err.name === "DomainError") { ... }

// ✅ 見た目に反する動作の意図（実装ミス誤解の防止）
// 終了日は 23:59:59 まで含める（半開区間ではなく閉区間で扱う仕様）
const toEpoch = dateInputToEpoch(dateInput, 23, 59, 59);

// ✅ 隠れた不変条件
// page_revisions.has_source=1 ⇔ R2 オブジェクト存在（R2 先行書き込みで整合）

// ✅ 意図的な逸脱の理由（biome-ignore 系）
// pageId 変更を検知する目的（setter だけを呼ぶ effect）
// biome-ignore lint/correctness/useExhaustiveDependencies: pageId 変更を検知する目的
useEffect(() => setVotesPage(1), [pageId]);

// ✅ 有効な TODO（条件付き）
// TODO: OAuth 4.0 対応時にこの workaround を削除（issue #456）
```

**判断規則:**

1. コメントを消してもコードだけで意図が分かる → **消す**
2. 「削除された機能を今後も明示的に残したい」→ commit message / PR 説明 / ADR に書く（コード内に書くと腐る）
3. コメントが 3 行以上 → 「関数抽出 + 命名で表現できないか」を先に検討
4. コメントが「なぜ」を説明していない → **書き換える or 消す**

## テスト規律（シーム限定TDD）

テスト基盤が存在するPJでプロダクションコードを書く時に適用する。**適用外**: テスト基盤が存在しないPJ / 設定・ドキュメントのみの変更 / UIの微調整。適用外で進めた場合は完了報告にその旨を明示する。

### ループの規則

1. **Test at pre-agreed seams** — テストを書く前に、テスト対象のseamを列挙する。実装計画（30_plan.md等）にseamが列挙済みならそれを合意とみなし自律実行してよい。計画外の公開interface新設・変更が必要になった時のみユーザーに確認する（Claude Code: AskUserQuestion）
2. **Red before green** — 失敗するテストを先に書き、それを通す最小限のコードだけを書く。将来のテストを先取りした投機的実装をしない
3. **Vertical slices** — 1テスト→1実装→繰り返し。各テストは前のサイクルの学びに応答する**tracer bullet**。全テストの先書き（horizontal slicing）は想像上の振る舞いを固定するため行わない
4. **リファクタはループの外** — red→greenのサイクル内でリファクタしない。green後・レビュー段階の責務として分離する

### テストの質

- テストは**public interfaceを通して振る舞いを検証する**。内部実装が全て変わってもテストは変わらないのが良いテスト。良いテストは仕様書のように読める（「user can checkout with valid cart」）
- **トートロジー禁止** — 期待値をコードと同じ方法で再計算しない（`expect(add(a, b)).toBe(a + b)` は構造的に必ず通る）。期待値は独立した真実源から取る: 既知の正しいリテラル・手計算した例・仕様書
- **Mockは外部境界のみ** — 外部API・DB（テストDBを優先）・時刻/乱数・ファイルシステム。自分のmodule・内部コラボレータ・自分が制御するものはmockしない。内部をmockしたテストは、振る舞いが変わっていないリファクタで壊れる

### Pure関数の回帰テスト固定

Parser / diff / tokenizer / formatter / 日付境界ヘルパー等、**入力から出力が決定論的に定まる pure 関数**を新設・変更する時は、以下を必ず整備する:

1. **境界値の網羅** — `0` / 空文字 / 空配列 / `null` / `undefined` / `MAX_SAFE_INTEGER` / 極端に長い文字列。日付は timezone 境界 / DST / 閏年。数値は integer overflow / floating point 誤差
2. **CJK と ASCII の両方** — Tokenize / diff / word-wrap 等は必ず両方をテスト（片方だけだと日本語圏で落ちるバグを見逃す）
3. **バグ修正時の回帰固定** — 修正したバグの **bug-triggering input を回帰テストとして残す**（後日同じロジック変更で再発した時に検出する）
4. **Property-based testing の判断** — Invariant を明示できるロジック（`mapToDsl(dslToMap(x)) === x` の round-trip、`sort(sort(arr)) === sort(arr)` の idempotency、可換性、逆演算成立）は `fast-check` 等を優先。個別ケース列挙より状態空間の網羅性が上がる

**完了基準に追加**: 新設・変更した pure 関数について境界値網羅と bug-triggering input の回帰テストが揃っている。

### Falsy check（言語横断のよくある罠）

- ID / count / revision 番号は `0` を有効値として持ちうる。`!!id` / `if (id)` は `0` を弾く
- **`!= null`（`null` と `undefined` のみ false）** を default にする
- 「truthy チェックか null チェックか」を意識しない実装が本番バグを生む常連。lint rule 化を検討する

## アンチパターン（実装中の自己検知）

書いている最中に以下の兆候を検知したら手を止めて設計を見直す。いずれも判断材料でありハード違反ではない。**PJの明文規約が常に勝つ**。

| Smell | 兆候 | 対処 |
|---|---|---|
| Duplicated Code | 同じロジックが2箇所以上 | 共通化を検討（3箇所目で必須検討） |
| Feature Envy | 他moduleのデータばかり触るメソッド | ロジックをデータ側へ移す |
| Primitive Obsession | ドメイン概念を裸のstring/intで表現 | 専用型・値オブジェクトへ |
| Data Clumps | 同じ引数群がいつも一緒に移動 | まとめて型にする |
| Shotgun Surgery | 1つの変更が多数ファイルに飛散 | 変更が集まるようmoduleを再配置（localityの欠如） |
| Speculative Generality | 「いつか使うかも」の抽象層・引数 | 削除（two adapters ruleで判定） |
| Message Chains | a.b().c().d() の連鎖 | 深いinterfaceで隠蔽 |

## 言語別ガイド（Read when）

新規module作成・公開interface変更・テスト設計を伴う実装の開始時に、対象言語のガイドをReadする。既存コードの数行修正では読まない。

- TypeScript: [references/typescript.md](references/typescript.md)
- Python: [references/python.md](references/python.md)
- Go: [references/go.md](references/go.md)

## 完了基準

実装を完了とする前に、以下をすべて確認する:

- [ ] 実装前ゲートを通過している（参照した同類実装を特定済み。既存パターンからの逸脱がある場合はユーザー確認済み）
- [ ] 変更した各moduleの振る舞いがinterface経由でテストされている（テスト規律の適用外条件に該当する場合は、完了報告にその旨を明示した）
- [ ] 新規に公開した各module（export）にdeletion testを自問した（削除して複雑さが消えるだけの通過型を公開していない）
- [ ] 新設したseam・抽象層にadapterが2つ以上ある。1つしかないものは削除した
- [ ] 設計判断の記述・コミットメッセージの用語がGlossaryと一致している
- [ ] PJ規定の品質チェック（lint / format / typecheck / test）が通っている
- [ ] 新設・変更した pure 関数について境界値網羅 + CJK/ASCII 両方 + bug-triggering input の回帰テストが揃っている
- [ ] falsy check（`!!id` で `0` を弾いていないか、`!= null` を使っているか）を全 diff で確認した

---

出典: obra/superpowers および mattpocock/skills（いずれもMIT License）を翻案。詳細はリポジトリルートの NOTICE.md を参照。
