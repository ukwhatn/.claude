# コメントの例

SKILL.md「コメント」節の規則の例。規則そのものは SKILL.md が真実源で、ここは判断に迷ったときの見本だけを置く。

## 書かない例

```typescript
// ❌ 名前の言い換え（What）
// ユーザーを取得
const user = getUser(id);

// ❌ コードをなぞる（How）
// i を 1 増やす
i++;

// ❌ 明白な null チェック
// null チェック
if (user == null) return;

// ❌ 関数名と同じことしか言わない docstring
/**
 * getUser
 * ユーザーを取得する
 * @returns User
 */
function getUser(id: string): User { ... }

// ❌ 経緯・依頼者・番号（履歴は git と PR にある）
// PR #123 で追加
// used by X

// ❌ 行番号での参照（行がずれても誰も気づかない）
// see handler.ts:120

// ❌ 消した理由（消したものはコードに残さない。コミットログに書く）
// 旧ロジックは性能問題のため削除
```

## 書く例

```typescript
// ✅ 外部要因の workaround（自明な書き方を採らない理由）
// bundler をまたぐと instanceof が false になることがあるため name でも判定する
if (err instanceof DomainError || err.name === "DomainError") { ... }

// ✅ 見た目に反する動作の意図（実装ミスと誤読されるのを防ぐ）
// 終了日は 23:59:59 まで含める（半開区間ではなく閉区間で扱う仕様）
const toEpoch = dateInputToEpoch(dateInput, 23, 59, 59);

// ✅ 隠れた不変条件
// has_source=1 のとき、対応するオブジェクトがストレージに必ずある（ストレージへ先に書いてから行を更新する）

// ✅ lint 抑制の理由
// biome-ignore lint/correctness/useExhaustiveDependencies: <id> の変更だけを検知したい
useEffect(() => setPage(1), [id]);

// ✅ 消せる条件つきの TODO
// TODO: <ライブラリ> が <機能> に対応したらこの workaround を消す（issue #<番号>）
```

## 迷ったとき

- コメントを消してもコードだけで意図が分かる → 消す
- 「なぜこの変更をしたか」を残したい → コミットメッセージ・PR 説明・ADR に書く
- コメントが「なぜ**この**自明でない選択をしたか」を説明していない → 書き換えるか消す
- 書こうとしている内容が永続的に正しいか分からない → 書かない（コメントはコードと一緒に更新されない）
