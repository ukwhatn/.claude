# TypeScript実装ガイド

本体（SKILL.md）の原則をTypeScriptで具体化する。TSの基本文法・tsconfig一般論は扱わない。

## 目次

1. 型は仕様である（不正な状態を表現不可能にする）
2. 型の抜け穴を作らない（any / as / satisfies）
3. 公開interfaceの戻り値型は明示する
4. Seamの作り方（SDK-style interfaces / DI）
5. エラー設計
6. テストのTS固有事項

## 1. 型は仕様である

Interface（呼び出し側が知るべき全て）のうち、可能な限り多くを型で表現する。型で表現された不変条件は、コメントと違いコンパイラが常時検証する。

**不正な状態を表現不可能にする。** boolean flagの組合せより discriminated union:

```typescript
// BAD: isLoading && hasError という不正な組合せが表現できてしまう
type State = { isLoading: boolean; hasError: boolean; data?: Data };

// GOOD: 不正な組合せが型レベルで存在しない。data有無の分岐も型が導く
type State =
  | { status: "loading" }
  | { status: "error"; error: AppError }
  | { status: "success"; data: Data };
```

**Primitive Obsessionを型で防ぐ。** 同じstring型のIDが複数種類流れるドメインでは、branded type等の専用型で取り違えを型エラーにする:

```typescript
type UserId = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };
// getOrder(userId) が型エラーになる
```

導入はIDの取り違えが実害になる箇所から。全stringのbrand化はSpeculative Generality。

## 2. 型の抜け穴を作らない

- `any` を使わない。外部境界からの未知の値は `unknown` で受け、型ガード・スキーマ検証（PJ採用のzod等）でnarrowingする
- プロダクションコードで `as` による型アサーションを原則使わない。型の嘘は下流の全推論を汚染し、コンパイラの検証を無効化する。値の構築で型を満たすか、型ガードで絞る。正当な例外（branded typeのfactory・型ガードの内部実装・ライブラリ型の既知の不備）では、assertionをその関数の内側に閉じ込め、公開interfaceに漏らさない
- オブジェクトリテラルが型に適合するかの検証は `satisfies` を使う（型を広げずに検証でき、推論も保たれる）
- テストコードでの部分データ構築は例外的に許容する。その場合も `as` より `satisfies` や部分構築ヘルパ（`@total-typescript/shoehorn` の fromPartial 等、PJ採用のもの）を優先する

## 3. 公開interfaceの戻り値型は明示する

推論任せにすると、実装の変更がそのまま公開interfaceの変更として静かに漏れる（意図しないbreaking change）。moduleの公開関数・公開メソッドには戻り値型を書く。module内部のローカル関数は推論に任せてよい。

## 4. Seamの作り方

**SDK-style interfaces over generic fetchers。** 外部操作ごとに型付きの個別関数を定義する:

```typescript
// GOOD: 各関数が独立にmock可能・endpoint単位で型安全
const api = {
  getUser: (id: UserId): Promise<User> => ...,
  createOrder: (data: OrderInput): Promise<Order> => ...,
};

// BAD: mockに条件分岐が必要になり、テストが何を叩くか見えない
const api = { fetch: (endpoint: string, options?: RequestInit) => ... };
```

**DIは関数引数で。** moduleスコープのsingletonを直接importして使うとseamが消える。外部依存（クライアント・時刻・乱数）は引数・factory・constructorで受け取る:

```typescript
// GOOD: seamがある（テストではfakeを注入）
function processPayment(order: Order, paymentClient: PaymentClient) {}

// BAD: seamがない（Stripeなしでテスト不能）
function processPayment(order: Order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
}
```

`Date.now()` / `Math.random()` の直呼びも同様に注入対象（時刻依存バグの再現テストが書けなくなる）。

## 5. エラー設計

- Result型 / throw / neverthrow等の選択は**PJの既存パターンに従う**。独断で切り替えない
- どちらの方式でも、エラーモードはInterfaceの一部。throwするなら何をthrowするかをJSDocの `@throws` か型で呼び出し側に見えるようにする

## 6. テストのTS固有事項

- 本体のテスト規律（シーム限定TDD・トートロジー禁止・mockは外部境界のみ）に従う
- 公開型そのものがinterfaceの主要部であるmodule（共有型パッケージ・ライブラリ）では、型テスト（`expectTypeOf` 等）も振る舞いテストの一種として扱う。アプリケーションコードでは通常不要
