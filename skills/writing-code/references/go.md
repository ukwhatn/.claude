# Go実装ガイド

本体（SKILL.md）の原則をGoで具体化する。Goの基本文法は扱わない。

## Seamの表現

- **Accept interfaces, return structs。** interfaceは**消費側パッケージで**、必要な最小メソッドだけで定義する。小さいinterfaceはdeep moduleの条件そのもの（`io.Reader` が模範）
- Goの暗黙的interface充足がseamを作る: 実装側は消費側のinterfaceを知らずに満たす。提供側パッケージで大きなinterfaceを事前定義するのはSpeculative Generality
- two adapters rule は同様に適用: 本番実装しか存在しないinterfaceは定義しない（テストfakeが2つ目のadapterになる時に初めて切る）

## エラー設計

- ラップして根本原因を保全する: `fmt.Errorf("fetching user %s: %w", id, err)`。判定は `errors.Is` / `errors.As`。エラーメッセージの文字列マッチは禁止
- エラーモードはInterfaceの一部: 呼び出し側が分岐すべきエラーはsentinel error（`var ErrNotFound = errors.New(...)`）か専用型として公開する

## 不正な状態を表現不可能にする

- zero valueがそのまま有効な状態になる設計を優先する（`sync.Mutex` / `bytes.Buffer` が模範）
- 列挙は typed const（`type Status int` + `const (...)` ）で表現し、裸のstring/intを流さない（Primitive Obsession）

## DIと副作用

- 依存は構造体フィールドまたは引数で注入する。パッケージレベル変数（グローバルclient・グローバルclock）への直接依存はseamを消しテスト不能にする
- `time.Now` も依存: `func() time.Time` フィールドかclock interfaceで注入する
- 副作用より戻り値: レシーバの変異は最小限にし、可能なら値を返す

## テストのGo固有事項

- 本体のテスト規律（シーム限定TDD・トートロジー禁止・mockは外部境界のみ）に従う
- **table-driven tests** を基本形にする（ケース追加が1行で済み、仕様の列挙として読める）
- mockライブラリより**手書きfake**（interfaceを満たす小さな構造体）を優先するのがGoの慣習。呼び出し回数の検証より観測可能な結果の検証
