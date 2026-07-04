---
name: instructions-audit
description: CLAUDE.md・skills・context・rules等の指示ファイル監査。指示ファイルの「レビューして」「監査して」「整理・スリム化して」等の依頼時、/instructions-audit実行時に使用。ベストプラクティスrubricで4分類（削除候補/hook・deny移管/skill化・Read-when化/description・構造強化）の指摘を修正案付きで出す。user-level（~/.claude）とproject-level両対応。境界: 指摘の適用・個別知見の追記→update-inst、セッション内容からの知見反映→session-retro、新規スキル作成→create-skill、コード自体の監査→codebase-review。
allowed-tools: Read, Grep, Glob, Bash(ls:*), Bash(wc:*), Bash(find:*), Bash(grep:*)
---

# Instructions Audit

指示ファイル（CLAUDE.md / skills / context / rules / settings.jsonのガード設定）を @context/claude-customization-guide.md のrubric（§7）で監査し、4分類の指摘を修正案付きで報告する。**このスキルは指摘のみを行い、修正はユーザー承認後に別途実施する**（read-only）。

## 使い方

```
/instructions-audit               # 自動判定（./CLAUDE.md or ./.claude があればproject、なければuser）
/instructions-audit --user        # user-level（~/.claude/）を監査
/instructions-audit --project     # project-level（./CLAUDE.md, ./.claude/）を監査
/instructions-audit <path>        # 指定ディレクトリを監査
```

## 既存設定との関係

- **rubricの真実源**: @context/claude-customization-guide.md §7（本スキルはrubricを重複記載しない）
- **Phase 0-5（@context/workflow-rules.md）**: 独立（監査は単発タスク。指摘の適用が複雑タスク化する場合のみPhase 0-5に乗せる）

## ワークフロー

### Step 1: 対象決定

引数から監査スコープを確定する。
- 完了基準: 監査対象のルートパスと、監査対象ファイル群（CLAUDE.md / context/ / skills/ / rules/ / settings.json）のリストが確定している

### Step 2: インベントリ作成

対象の全指示ファイルを列挙し、規模を把握する:
1. CLAUDE.mdと、そこから`@`importされるファイルを**再帰的に**辿る（@importは毎セッション常駐のため、常駐行数はimport先を全て合算して計算する）
2. `skills/*/SKILL.md` の一覧・各行数・frontmatter（description長、allowed-tools有無）・references/の有無
3. `context/`・`rules/` の一覧と行数、どこから参照されているか（@import / プレーンパス / 未参照）
4. `settings.json` の hooks / permissions.deny・allow

- 完了基準: 「常駐合計行数」「skill数とdescription合計」「未参照ファイル一覧」が数値で出ている

### Step 3: rubric適用（監査本体）

@context/claude-customization-guide.md の§7 rubric（4分類）と§1-5の原則を対象に適用する。

**対象が大きい場合（合計500行超）はサブエージェントに委譲する**（コンテキスト保護。分割例: CLAUDE.md+context系 / skills系）。サブエージェントへの指示に含めること:
- 監査rubricとして claude-customization-guide.md を読むこと
- 指摘ごとに「対象ファイル:行」「4分類のどれか」「根拠となる原則（§番号）」「具体的な修正案」を返すこと
- 下記Gotchasを遵守すること

- 完了基準: 全対象ファイルが監査済みで、各指摘に分類・根拠・修正案が揃っている

### Step 4: 報告

以下の構成で報告する（ファイル生成はユーザーが求めた場合のみ）:
1. **サマリ**: 常駐行数・skill数・指摘件数（分類別）
2. **指摘一覧**: 4分類ごとに、影響の大きい順。各指摘は「対象 / 内容 / 根拠原則 / 修正案（diffまたは書き換え文）」
3. **適用の提案**: どの指摘から適用すべきかの推奨順。適用はユーザー承認後（個別の適用は `/update-inst` スキルを実行する）

- 完了基準: ユーザーが各指摘にyes/noで判断できる粒度になっている

## Gotchas（監査時の誤指摘防止）

- **@importは毎セッション常駐**（必要時ロードではない）。常駐行数の計算はimport再帰を含める
- **allowed-toolsは事前承認であって制限ではない**。「セキュリティのため制限せよ」という指摘は誤り。read-only skillへの指摘は「事前承認の欠如（permission prompt増）」として出し、実際の制限が必要な場合のみdisallowed-tools/denyを提案する
- **コミュニティ由来の数値（行数上限等）を規範として指摘しない**。目安として提示し、公式原則（「消したら間違えるか」）を判断基準にする
- 重複に見える記述が意図的な場合がある（冒頭・末尾への重要ルール再掲等）。削除提案時は意図の可能性を添える
- 監査対象に本スキルや claude-customization-guide.md 自身が含まれる場合も除外しない
