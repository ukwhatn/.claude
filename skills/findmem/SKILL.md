---
name: findmem
description: メモリディレクトリ内の過去タスク・issueをキーワード検索し、関連する作業履歴を表示。使用タイミング: (1) /findmem <keyword>で呼び出された時、(2) Phase 1.0「過去タスク・issue参照」で過去の知見を探す時、(3) 過去の作業を振り返りたい時。
---

# findmem - メモリディレクトリ探索

過去の作業メモリとissueファイルをキーワードで横断検索し、関連する知見を素早く見つける。

## 既存設定との関係

- **Phase 0-5（@context/workflow-rules.md）**: Phase 1.0「過去タスク・issueの参照」を支援
- **メモリディレクトリ（@context/memory-file-formats.md）**: `${MEMORY_DIR}/memory/` と `${MEMORY_DIR}/issues/` を検索対象とする

## 引数

```
/findmem <keyword>           # キーワードで検索
/findmem <keyword1> <keyword2>  # 複数キーワード（AND検索）
```

## ワークフロー

### Step 1: MEMORY_DIRの特定

PJ CLAUDE.mdから`MEMORY_DIR`を読み取る。未定義の場合は`.local/`をデフォルトとする。

### Step 2: ディレクトリ名検索

`${MEMORY_DIR}/memory/` 配下のディレクトリ名をキーワードでフィルタリング:

```bash
ls ${MEMORY_DIR}/memory/ | grep -i "<keyword>"
```

### Step 3: issueファイル検索

`${MEMORY_DIR}/issues/` 配下のファイル名をキーワードでフィルタリング:

```bash
ls ${MEMORY_DIR}/issues/ | grep -i "<keyword>"
```

### Step 4: ファイル内容検索（ディレクトリ名にマッチしなかった場合）

ディレクトリ名でマッチしなかった場合、各メモリディレクトリ内の`05_log.md`と`00_spec.md`の内容をGrepでキーワード検索:

```bash
# 05_log.mdの内容検索
grep -ril "<keyword>" ${MEMORY_DIR}/memory/*/05_log.md

# 00_spec.mdの内容検索
grep -ril "<keyword>" ${MEMORY_DIR}/memory/*/00_spec.md
```

### Step 5: 結果表示

マッチした各ディレクトリについて以下を表示:

```
## 関連する過去タスク

### YYMMDD_<task_name>/
**ファイル構成:**
- 05_log.md (XX KB) - 最終更新: YYYY-MM-DD
- 00_spec.md (XX KB)
- 30_plan.md (XX KB)
- ...

**05_log.mdサマリー（冒頭のユーザー指示）:**
> [05_log.mdの最初のユーザー指示を抽出して表示]

---

## 関連するissue

### <issue-filename>.md
> [issueファイルの冒頭3行を表示]
```

### Step 6: 参照提案

「このディレクトリの詳細を確認しますか？」と提案し、ユーザーが選んだファイルを読み込む。

## 出力例

```
## 関連する過去タスク（2件）

### 260122_temp-account-spec/
ファイル: 00_spec.md, 05_log.md, 10_confluence_prd.md, ... (14ファイル)
最終更新: 2026-02-25

> **ユーザー指示:** かんたんアカウントの要件定義をConfluenceから取得してまとめてほしい

### 260204_mobile-idp-integration/
ファイル: 05_log.md, 20_survey.md (2ファイル)
最終更新: 2026-02-04

> **ユーザー指示:** モバイルアプリからのIdP連携について調査してほしい

---

## 関連するissue（0件）

該当なし
```

## 注意事項

- MEMORY_DIRが存在しない場合はエラーメッセージを表示
- キーワードは大文字小文字を区別しない（case-insensitive）
- 05_log.mdのサマリーは最初の「ユーザー指示:」ブロックのみ抽出（全文は読まない）
