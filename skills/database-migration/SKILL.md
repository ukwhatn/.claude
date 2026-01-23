---
name: database-migration
description: DBマイグレーション支援。スキーマ変更やマイグレーション作成依頼時に使用。ORM自動検出、命名規則確認、既存マイグレーションとの整合性を検証。
---

# DBマイグレーション支援

## トリガー条件

- DBスキーマ変更が必要な場合
- マイグレーションファイルの作成を依頼された場合

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

