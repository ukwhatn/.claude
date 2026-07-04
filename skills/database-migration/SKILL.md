---
name: database-migration
description: DBマイグレーション支援。スキーマ変更・マイグレーション作成依頼時、および「マイグレーションを1つにまとめて」「統合前後が同値か確認して」等の統合・同値性確認依頼時に使用。ORM自動検出、命名規則確認、既存マイグレーションとの整合性を検証。
---

# DBマイグレーション支援

## トリガー条件

- DBスキーマ変更が必要な場合
- マイグレーションファイルの作成を依頼された場合
- 複数マイグレーションの統合（squash）や統合前後の同値性確認を依頼された場合（→「マイグレーション統合」セクション）

## ORM検出

```bash
# Prisma
ls prisma/schema.prisma 2>/dev/null

# SQLAlchemy (Alembic)
ls alembic/ alembic.ini 2>/dev/null

# Drizzle
ls drizzle.config.ts 2>/dev/null

# Django ORM
ls */migrations/ 2>/dev/null
```

## ORM別コマンド

### Prisma

```bash
npx prisma format
npx prisma migrate dev --name <名前>
npx prisma generate
```

### SQLAlchemy (Alembic)

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Drizzle

```bash
npx drizzle-kit generate
npx drizzle-kit migrate
```

## 実行手順

### 1. スキーマ変更の確認

```bash
git diff <schema-file>
```

### 2. 命名規則の検証

CLAUDE.mdに命名規則があれば確認。

### 3. マイグレーション作成

ORM固有のコマンドを実行。

### 4. 検証

```markdown
## マイグレーション検証

- [ ] 命名規則に従っている
- [ ] 必須フィールドにデフォルト値設定
- [ ] 外部キー制約が適切
- [ ] ロールバック可能
```

## マイグレーション統合（squash）

ブランチ内で積み上がった複数のマイグレーションを1つにまとめる手順（Prisma前提。他ORMは同等コマンドに読み替え）。

**CRITICAL: `prisma migrate reset` はDB全削除を伴う破壊的操作。実行前に (1) ユーザー承認 (2) 対象DBがローカル/使い捨てであること（DATABASE_URLがlocalhost等）の確認を必須とする。**

### 手順

1. **統合対象の特定**: `git diff <BASE_BRANCH> --name-only -- prisma/migrations/` でブランチ追加分のマイグレーションを列挙
2. **統合前SQLの保存**: 統合対象の全 `migration.sql` を結合し、比較用に退避（メモリディレクトリ配下または`$CLAUDE_JOB_DIR`。`/tmp`は使わない）
3. **巻き戻し**: 統合対象のマイグレーションディレクトリを削除 → ユーザー承認の上 `npx prisma migrate reset`（ブランチ追加前の状態に戻す）
4. **統合マイグレーション作成**: `npx prisma migrate dev --name <統合名>` で現在のschema.prismaから1本生成
5. **同値性確認（必須）**:
   - 退避した統合前SQLと新規生成SQLをdiffし、意味的な差分がないことを確認（ステートメントの順序差・コメント差は許容、DDL内容の差は要調査）
   - 差分がある場合はなぜ生じたかを調査して報告（schema.prismaとの乖離が原因のことが多い）
   - 補助: `npx prisma migrate diff --from-migrations prisma/migrations --to-schema-datamodel prisma/schema.prisma --script` が空であることを確認
6. **適用確認**: `npx prisma migrate dev` がクリーンに完走し、`npx prisma generate` が成功すること

