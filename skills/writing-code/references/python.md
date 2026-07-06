# Python実装ガイド

本体（SKILL.md）の原則をPythonで具体化する。Pythonの基本文法は扱わない。

## Seamの表現

- Seamは `typing.Protocol`（構造的部分型）で表現し、**消費側の近くで定義する**。実装側はProtocolを知らずに満たせるため、疎結合なseamになる
- ABC（継承ベース）は、所有する型階層に共通実装を持たせたい時のみ。差し替え可能性だけが目的ならProtocolを使う
- two adapters rule は同様に適用: 差し替えの実需（本番+テスト等）がないProtocolは作らない

## 型ヒント

- moduleの公開interface（公開関数・公開メソッド）には型ヒントを必須とする。内部のローカル変数は推論に任せてよい
- `Any` を使わない。外部境界からの未知の値は検証（PJ採用のpydantic等）で具体型に落としてから流す

## 不正な状態を表現不可能にする

- 状態の組合せは `Enum` / `Literal` union で列挙し、boolean flagの組合せで表現しない
- ドメイン概念を裸のdict・tupleで受け渡さない（Primitive Obsession / Data Clumps）。`dataclass`（不変にするなら `frozen=True`）またはpydanticモデルにする。`dict[str, Any]` のバケツリレーはinterfaceを不透明にする

## DIと副作用

- 依存（外部クライアント・時刻・乱数・設定）は引数・コンストラクタで受け取る。モジュールグローバルでのインスタンス生成に直接依存するとseamが消える
- `datetime.now()` / `random` の直呼びも注入対象
- 引数のdict/listをin-placeで変異させず、新しい値を返す（副作用より戻り値）

## テストのPython固有事項

- 本体のテスト規律（シーム限定TDD・トートロジー禁止・mockは外部境界のみ）に従う
- `monkeypatch` / `unittest.mock.patch` で**自分のmoduleの内部を差し替えるのは実装結合**のサイン。境界をProtocolにしてfakeを注入する形に設計を直す
- patchが正当なのは外部境界（時刻・環境変数・外部SDK）のみ
