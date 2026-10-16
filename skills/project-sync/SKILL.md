---
name: project-sync
description: PJ ドキュメントの同期。PJ CLAUDE.md の更新依頼、ドキュメント整理依頼、コード変更後の CLAUDE.md・README・API 仕様への反映依頼（npm script・環境変数・API 追加等）の時に使用。user-level 設定との整合性確認も行う。境界: CLAUDE.md が未整備の新規 PJ は組み込みの /init。
---

# PJドキュメント同期

PJ の CLAUDE.md・`.claude/`・人間向けドキュメントを、コードと user-level 設定に合わせる。CLAUDE.md のサイズ・強調・命令形・理由の添え方は `~/.claude/context/claude-customization-guide.md`「3. CLAUDE.md設計原則」に従う（公式の目標は1ファイル200行未満）。

## コード変更起点の差分同期

コード変更後の依頼では、フル同期でなく変更起点の差分同期を行う。

1. `git diff <base-branch> --name-only` と `git diff <base-branch>` で変更を読む
2. 更新対象を決める

| カテゴリ | 例 | 更新対象 |
|---------|-----|---------|
| コマンド変更 | npm script追加 | CLAUDE.md, README.md |
| API変更 | エンドポイント追加 | API仕様書 |
| 設定変更 | 環境変数追加 | README.md |
| アーキテクチャ変更 | 新規レイヤー | CLAUDE.md |

3. 内部実装だけの変更・テストコードだけの変更・機能の変わらないリファクタは更新しない
4. 更新提案を示し、承認後に反映する

## フル同期

### 1. 現状把握

PJ の CLAUDE.md（と行数）、`.claude/`・`.claude/rules/`・`docs/` の構成、`.claude/settings.json`（`permissions.deny` の Read ルール・`claudeMdExcludes`）、`~/.claude/AGENTS.md` と `~/.claude/context/` の一覧を読む。

### 2. 差分分析

| 項目 | 確認内容 |
|------|---------|
| CLAUDE.md のサイズ | 肥大せず簡潔か |
| 変数定義 | MEMORY_DIR, BASE_BRANCH があるか |
| 品質チェック | lint/format/typecheck/test コマンドがあるか |
| 検証方針 | ローカル起動・テスト・E2E・スクショ・期待出力の指針があるか |
| レビュー方針 | critical 不変条件・検証境界・エラーハンドリング方式・却下類型があるか（無ければ追加を提案） |
| 詳細の置き場 | タスク限定の詳細を `.claude/context/` に出し、Read-when で誘導しているか（`@` import は毎セッション常駐する） |
| 分離原則 | 人間向け（README.md・docs/）とエージェント向け（CLAUDE.md・.claude/context/・.claude/rules/）が分かれているか |
| コンテキスト除外 | 秘匿・不要パスが permissions.deny の Read ルールで除外されているか。`.claudeignore` は公式機能に存在しないので、残っていれば削除を提案する |
| .claude/rules/ | パス固有ルールが活用されているか |
| user-level との重複 | user-level の AGENTS.md・context に既にある内容（委譲の強制など）を繰り返していないか |
| 強制表現 | 「こまめに」「必ず」「逐次」等の強制表現を多用していないか |

### 3. 更新提案の作成

[references/claude-md-template.md](references/claude-md-template.md) の雛形・書かない内容・提案の書式に沿って書く。

### 4. ユーザー確認

選択肢を示して確かめる（Claude Code: AskUserQuestion）。

1. 更新提案の承認
2. 削除対象の確認（誤削除を防ぐため）
3. PJ 固有の追加要件

### 5. 実行

承認後に、CLAUDE.md の更新・コンテキスト除外の設定・`.claude/rules/` と `.claude/context/` の作成（必要な場合）・不要ファイルの削除・移動とリネームを行う。

## 不要ファイルの判断基準

| 判断 | 条件 |
|------|------|
| 削除 | 古い agent 定義、重複ドキュメント、空ファイル、user-level と重複する指示 |
| 移動 | エージェント向けの内容が docs/ にある → .claude/context/ |
| 統合 | 類似内容の複数ファイル → 1ファイルに |
| 保持 | 人間向けドキュメント（README, docs/）、PJ 固有設定 |
