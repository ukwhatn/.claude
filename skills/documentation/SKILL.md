---
name: documentation
description: ドキュメント更新。コード変更後にnpm script/環境変数/API追加を検出した場合に使用。CLAUDE.md/README.md/API仕様の同期を支援。
---

# ドキュメント更新

## トリガー条件

- コード変更後にドキュメント更新が必要な場合
- 以下の変更を検出した場合:
  - 新規npm script追加
  - 環境変数追加
  - APIエンドポイント追加・変更
  - アーキテクチャ変更

## 実行手順

### 1. 変更内容の確認

```bash
git diff <base-branch> --name-only
git diff <base-branch>
```

### 2. 更新が必要なドキュメントの特定

| カテゴリ | 例 | 更新対象 |
|---------|-----|---------|
| コマンド変更 | npm script追加 | CLAUDE.md, README.md |
| API変更 | エンドポイント追加 | API仕様書 |
| 設定変更 | 環境変数追加 | README.md |
| アーキテクチャ変更 | 新規レイヤー | CLAUDE.md |

### 3. 更新提案の作成

```markdown
## ドキュメント更新提案

### CLAUDE.md
**現在:**
```
npm run lint
```

**提案:**
```
npm run lint
npm run new-command  # 新しいコマンド
```

### README.md
**追加:**
```
## 環境変数
- NEW_VAR: 説明
```
```

### 4. 更新不要の判断

以下は更新不要:
- 内部実装の変更のみ
- テストコードの変更のみ
- リファクタリング（機能変更なし）
