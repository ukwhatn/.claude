---
name: findmem
description: メモリディレクトリ内の過去タスク・issueをキーワード検索し、関連する作業履歴を表示。使用タイミング: (1) /findmem [keyword]で呼び出された時、(2) Phase 1.0「過去タスク・issue参照」で過去の知見を探す時、(3) 過去の作業を振り返りたい時。
allowed-tools: Read, Grep, Glob, Bash(ls:*), Bash(grep:*)
---

# findmem - メモリディレクトリ探索

過去の作業メモリとissueファイルをキーワードで横断検索し、関連する知見を素早く見つける。

## 既存設定との関係

- **Phase 0-5（@context/workflow-rules.md）**: Phase 1.0「過去タスク・issueの参照」を支援
- **メモリディレクトリ（@context/memory-file-formats.md）**: `${MEMORY_DIR}/memory/` と `${MEMORY_DIR}/issues/` を検索対象とする

## 引数

```
/findmem <keyword>              # キーワードで検索（複数指定でAND検索）
```

## 検索範囲

MEMORY_DIRはPJ CLAUDE.md参照（未定義時`.local/`）。キーワードは大文字小文字を区別しない。

1. `${MEMORY_DIR}/memory/` のディレクトリ名
2. `${MEMORY_DIR}/issues/` のファイル名
3. 1・2でマッチしなかった場合、各メモリディレクトリの `05_log.md` / `00_spec.md` を内容検索

## 出力

マッチした各タスク/issueについて、ディレクトリ名（またはファイル名）・ファイル構成・最終更新日・要約（05_log.mdの冒頭ユーザー指示、issueの冒頭数行）を一覧表示し、詳細を読むか確認する。

```
## 関連する過去タスク（2件）

### 260122_<context-name>/
ファイル: 00_spec.md, 05_log.md, ... (14ファイル) / 最終更新: 2026-02-25
> **ユーザー指示:** <feature>の要件定義をConfluenceから取得してまとめてほしい

---

## 関連するissue（0件）
該当なし
```

## 注意事項

MEMORY_DIRが存在しない場合はその旨を報告する。
