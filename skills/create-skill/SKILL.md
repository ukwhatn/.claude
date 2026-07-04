---
name: create-skill
description: 既存設定と完全に整合したスキルを自動作成。~/.claude/CLAUDE.md、context/*.md、既存スキルを自動参照し、重複・競合を避けたスキルを生成。
---

# Create Skill

既存のuser-level/project-level設定と整合性が取れたスキルを自動作成する。

## 使い方

```
/create-skill <内容>                 # user scope（デフォルト）
/create-skill --user <内容>          # user scope（明示）
/create-skill --project <内容>       # project scope
```

## ワークフロー

### Step 1: 引数パース

```
入力: /create-skill --project 大規模タスク分割ワークフロー
→ scope: project
→ 内容: 大規模タスク分割ワークフロー
```

### Step 2: 既存設定の読み込み（必須）

**常に読み込む:**
- `~/.claude/CLAUDE.md` - user-level設定
- `~/.claude/context/*.md` - 特に以下が重要:
  - `claude-customization-guide.md` - 設計原則、Skills/Commands/CLAUDE.mdの使い分け
  - `workflow-rules.md` - Phase 0-5ワークフロー
  - `memory-file-formats.md` - メモリディレクトリ構造

**--project時に追加で読み込む:**
- `./CLAUDE.md` - project-level設定
- `./.claude/context/*.md` - project-level参照ファイル
- `./.claude/rules/*.md` - project-levelルール

**既存スキルの確認:**
- `~/.claude/skills/*/SKILL.md` のfrontmatter（name, description）を取得
- 重複・競合がないか確認

### Step 3: Skill vs Command vs CLAUDE.md 判定

@context/claude-customization-guide.md に従い判定:

| 選択 | 条件 |
|------|------|
| **Skill**（推奨） | 自動トリガー、ドメイン知識、スクリプト同梱 |
| **CLAUDE.md追記** | 常時適用ルール、200行以下に収まる |

**NOTE**: Commands（`.claude/commands/`）はレガシー形式。新規作成時はSkills形式を使用する。

### Step 4: 整合性チェック

1. **ワークフローとの整合**: Phase 0-5、4ステップ構造との関係
2. **ディレクトリ構造**: MEMORY_DIR、memory/、tasks/等との整合
3. **既存スキルとの重複**: 同じ機能を持つスキルがないか
4. **スコープ判定**: user vs project（@context/claude-customization-guide.md参照）

問題があればAskUserQuestionで確認。

### Step 5: スキル設計

**設計原則（@context/claude-customization-guide.md）:**
- SKILL.mdは**500行以下**
- descriptionに「**何をするか**」+「**いつ使うか**」
- 詳細は別ファイルに分割（参照は**1階層のみ**）
- 既存設定を`@context/xxx.md`形式で参照（重複記載しない）
- 後述「スキル設計原則（予測可能性）」に従う

**description例:**
```yaml
# Good
description: PRレビュー。PR番号・ブランチ名指定時またはレビュー依頼時に使用。

# Bad
description: PRレビュー。
```

### Step 6: スキル作成

**配置先:**
- `--user`: `~/.claude/skills/<skill-name>/`
- `--project`: `./.claude/skills/<skill-name>/`

**構造（Progressive Disclosure）:**
```
<skill-name>/
├── SKILL.md              # Level 2: トリガー時ロード（500行以下）
└── references/           # Level 3: 必要時のみロード
    └── detail.md
```

### Step 7: 確認

作成後、以下を報告:
- 作成したファイル一覧
- 既存設定との関係
- 使い方の例

## SKILL.md テンプレート

```yaml
---
name: <skill-name>
description: <何をするか>。<いつ使うか>。使用タイミング: (1) xxx、(2) yyy。
# オプション:
# allowed-tools: Read, Grep, Glob          # 使用可能ツールの制限
# disable-model-invocation: true           # 手動起動のみ（副作用のある操作向け）
---

# <Skill Name>

[1-2文で概要]

## 既存設定との関係

- **Phase 0-5（@context/workflow-rules.md）**: [補完/拡張/独立]
- **メモリディレクトリ（@context/memory-file-formats.md）**: [既存構造を使用/拡張]

## ワークフロー

[具体的な手順]

## 既存設定への参照

- @context/workflow-rules.md
- @context/memory-file-formats.md
```

## スキル設計原則（予測可能性）

スキルの存在意義は、確率的なシステムから決定性を引き出すこと。根本の価値は**予測可能性**——毎回同じ出力ではなく、毎回同じ**プロセス**を踏ませること。以下はすべてその手段（出典: mattpocock/skills の writing-great-skills を本環境向けに要約）。

### invocationの選択

- **model-invoked**（デフォルト）: モデルが自律発火でき、他スキルからも到達できる。代償としてdescriptionが常時コンテキストに載る（約100トークン/スキル）
- **user-invoked**（`disable-model-invocation: true`）: コンテキスト負荷ゼロだが、存在を覚えておく認知負荷をユーザーが払う。descriptionはモデルの発火に使われないため、人間向けの一行要約でよい（トリガー列挙は不要）
- 判断基準: 「副作用があるか」だけでなく「**誰が到達すべきか**」で選ぶ。モデル自身や他スキルが到達すべきならmodel-invoked、手動でしか呼ばないならuser-invoked

### descriptionの刈り込み（model-invoked）

- **1トリガー=1分岐**: 同義語の言い換え列挙は重複。本当に異なる使用分岐だけを列挙する
- スキルを象徴する語を先頭に置く

### 完了基準（completion criterion）

- 各ステップの終わりに、**チェック可能**（done/not-doneが判定できる）で、必要なら**網羅的**（「変更した全ファイルを確認」等）な完了基準を置く
- 曖昧な完了基準は早期完了（終わった気になって次へ進む）を招く

### リーディングワード

- モデルの事前学習に既にある強い一語（relentless、tight等）は、少ないトークンで行動全体を固定する。冗長な言い回し（「速く・決定的で・低オーバーヘッドな」→ tight）は一語に折り畳む
- デフォルト挙動と変わらない弱い語（「丁寧に」等）はno-op。より強い語に置き換えるか削除する

### 他スキルへの依存

- 「`/xxx` スキルを実行する」というプロース形式で書く。他スキルのディレクトリ内ファイルを直接パス参照しない

### 失敗モード診断（スキルが期待どおり動かない時）

- **早期完了**: まず完了基準を先鋭化する。それでも直らない場合のみ後続ステップを別スキル/別ファイルに分割して視界から隠す
- **重複**: 同じ意味が複数箇所にある → 単一の真実源に集約
- **堆積**: 「追記は安全・削除は怖い」で溜まった古い層 → 定期的に刈り込む
- **肥大**: 全行が生きていても長すぎる → references/への開示か分割
- **no-op**: 「この行はデフォルト挙動を変えるか？」でテストし、変えないなら文ごと削除する

## 禁止事項

- 既存設定との整合性確認なしでスキル作成
- 既存スキルと重複する機能の作成
- SKILL.mdに500行以上記載
- references/内で更にファイル参照（1階層まで）
- model-invokedスキルのdescriptionに「いつ使うか」がない（user-invokedは人間向け一行要約でよい）
- 他スキルのディレクトリ内ファイルへの直接パス参照（依存は`/xxx`プロース形式で書く）
- Commands形式（`.claude/commands/`）での新規作成

## チェックリスト

- [ ] ~/.claude/CLAUDE.md を読んだか
- [ ] ~/.claude/context/claude-customization-guide.md を確認したか
- [ ] 既存スキル一覧を確認したか
- [ ] Skill/CLAUDE.md追記の判定をしたか
- [ ] descriptionに「何を」「いつ」が含まれるか（model-invokedの場合）
- [ ] descriptionの同義語トリガー重複を排したか
- [ ] 各ステップにチェック可能な完了基準があるか
- [ ] no-op行（デフォルト挙動を変えない行）がないか
- [ ] SKILL.mdは500行以下か
- [ ] @context/xxx.md 形式で参照を記載したか
- [ ] 新フロントマター（allowed-tools, disable-model-invocation）を検討したか
