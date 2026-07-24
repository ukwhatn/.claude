---
name: session-analytics
description: 複数セッションを横断した利用傾向分析。~/.claude/projects/配下の全JSONLログを集計し、skill発火回数・tool使用頻度・ユーザーの軌道修正シグナル(中断・権限拒否・AskUserQuestionでのOther回答率)・compaction頻度・未発火skillを可視化してハーネス改善の示唆を出す。使用タイミング: (1) 「このPCでのセッション傾向を分析して」「skillの発火状況を教えて」「ハーネス改善の示唆が欲しい」等の依頼時、(2) 定期的な.claude設定の棚卸し時、(3) 新しいskill/ルール追加の効果を過去傾向と比較したい時。境界: 単一セッション内の振り返りと指示ファイルへの自律反映→session-retro、過去メモリ/issueのキーワード検索→findmem、CLAUDE.md/skills/context自体の静的品質監査→instructions-audit。
allowed-tools: Bash(uv run:*), Read
---

# Session Analytics

`~/.claude/projects/**/*.jsonl`（Claude Codeの全セッション生ログ）を横断集計し、ハーネス（AGENTS.md/context/skills）の改善点を見つけるためのデータを提供する。

## 既存設定との関係

- **session-retro**: 対象範囲が逆。session-retroは「今回1セッション」を振り返り指示ファイルへ自律反映する。本skillは「複数セッションの集計統計」を出すだけで、指示ファイルへの反映は行わない（示唆をユーザーに提示し、適用は`/update-inst`・`/session-retro`・`/instructions-audit`に委ねる）
- **findmem**: メモリディレクトリ(`.local/memory/`, `.local/issues/`)のテキスト検索。本skillはそれとは別データソース（生セッションログ）を扱う
- **メモリディレクトリ**: 分析結果を保存する場合は@context/memory-file-formats.mdの既存構造（`${MEMORY_DIR}/memory/YYMMDD_<context>/`）に従う

## ワークフロー

### Step 1: 実行

```bash
uv run ~/.claude/skills/session-analytics/scripts/analyze_sessions.py [オプション]
```

主なオプション（すべて任意）:

| オプション | 用途 |
|---|---|
| `--since YYYY-MM-DD` | このmtime以降に更新されたセッションファイルのみ対象 |
| `--project SUBSTR` | プロジェクトディレクトリ名の部分一致フィルタ（大小無視） |
| `--top-n N` | 各ランキングの表示件数（既定15） |
| `--json-out PATH` | 集計結果全体をJSONで書き出す（追加分析・時系列比較用） |
| `--skills-dir DIR`（複数指定可） | 未発火skill棚卸しの比較対象。既定は`~/.claude/skills`。project-levelも見たい場合は`--skills-dir ./.claude/skills`を追加指定 |

依存パッケージはゼロ（stdlibのみ）。全セッション（600MB級）でも数秒で完走する。

**完了基準**: コマンドが正常終了し、標準出力にレポートセクション（プロジェクト別/Skill発火/Tool使用頻度/Agent tool/軌道修正シグナル/AskUserQuestion/Compaction/system event/permission mode/Skill棚卸し）が全て表示されている。

### Step 2: 数値の解釈（このskillの本体価値）

生の集計値をそのまま報告せず、以下の観点で異常値・示唆を抽出する:

1. **Skill発火の偏り**: 上位数件に極端に集中していないか。長期間(数ヶ月)未発火のskillは、`git log --diff-filter=A --format=%ad -- skills/<name>/SKILL.md`で追加日を確認し、「観測期間が短いだけ」か「本当に死蔵している」かを切り分ける
2. **AskUserQuestion中断率・Other率**: `中断件数のうち直前tool=AskUserQuestion` と `Other回答率`が高い（目安: 合算で全体の3割超）場合、選択肢設計が実際の意図をカバーしきれていないシグナル。個別の質問文をサンプリングして具体的な改善提案に落とす
3. **権限拒否(has been denied)**: 対象コマンドのパターンを`grep`でサンプル抽出し、「事前確認してから提案する」フローが徹底されているか、「実行してdenyで弾かれてから気づく」フローが常態化していないかを確認する
4. **tool別エラー率**: 特定tool（EnterWorktree/ExitWorktree等）のエラー率が突出している場合、該当guideのtroubleshooting不足を疑う
5. **Compaction**: 平均preTokensが極端に大きい場合、セッション区切り(/handoff)がより早いタイミングで発動すべきというシグナル
6. **未発火skill棚卸し**: 「観測期間内に一度も呼ばれていない」skillは、description(発火条件)の弱さ・実需の欠如・他の指示ファイル(workflow-rules.md等)が同機能を直書きで代替してしまっている自己矛盾、のいずれかを疑い個別に確認する

**完了基準**: 上記6観点それぞれについて「該当あり(具体的数値付き)」か「該当なし」かが判定済みである。

### Step 3: 報告

過程（集計コマンドと生データ）と結論（示唆）を分けて提示する。示唆は「観測された事実→考えられる原因→改善候補」の順で書き、改善候補の適用自体はユーザー確認を経てから行う（本skill単体でAGENTS.md/context/skillsを書き換えない）。

**完了基準**: 各示唆に、それを裏付ける具体的な集計数値（件数・割合）が紐づいている。

## 使用例

```bash
# 直近2週間・全プロジェクトのサマリ
uv run ~/.claude/skills/session-analytics/scripts/analyze_sessions.py --since 2026-07-10

# recerqaプロジェクトに絞って詳細JSONも保存
uv run ~/.claude/skills/session-analytics/scripts/analyze_sessions.py \
  --project recerqa --json-out /tmp/recerqa_analysis.json
```

出力例（抜粋）:
```
--- ユーザー軌道修正シグナル ---
  中断([Request interrupted by user]): 243件
      直前のtool=Bash: 106件
      直前のtool=AskUserQuestion: 38件
  権限拒否 (has been denied): 35件
      tool=Bash: 35件
```
→ 「AskUserQuestion呼び出し199件中38件(19%)が回答されず中断」「権限拒否35件は全てBashのgit破壊的操作」のように、母数となる他の集計値（Tool使用頻度のAskUserQuestion呼び出し数など）と突き合わせて解釈する。

## Gotchas

- ログの`type`別意味: `assistant`のtool_use内`name`が実際のtool呼び出し（`Skill`は`input.skill`にskill名）。中断は`"[Request interrupted by user]"`または`"...for tool use]"`というテキストで表れる。権限拒否は`tool_result.is_error=true`かつcontentに`has been denied`
- サブエージェント（Agent tool経由）のログは`<project>/<session-id>/subagents/*.jsonl`に別ファイルとして存在する。メインセッションだけ見たい集計と、委譲先も含めた実働量を見る集計は目的に応じて使い分ける（レポートは両方出力する）
- `--project`はディレクトリ名（`-Users-xxx-workspace-yyy`形式、パス区切りが`-`に変換されたもの）に対する部分一致。worktree配下のセッションは別ディレクトリとしてカウントされる点に注意
- JSON出力は生カウンタのダンプであり文章化されていない。示唆抽出はStep 2を必ず自分で行うこと（スクリプトは決定論的集計のみを担当し、解釈はモデルの役割）
