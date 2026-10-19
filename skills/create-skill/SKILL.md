---
name: create-skill
description: スキルを新規作成する。「スキルを作って」「この手順をスキル化して」等の依頼時、/create-skill 実行時に使用。AGENTS.md・context・既存スキルと整合させ、重複・競合を避ける。境界: 既存スキル・指示ファイルの修正は update-inst、指示ファイル全体の監査は instructions-audit。
---

# Create Skill

既存の user-level / project-level 設定と整合したスキルを作る。

## 使い方

```
/create-skill <内容>                 # user scope（デフォルト）
/create-skill --user <内容>          # user scope（明示）
/create-skill --project <内容>       # project scope
```

## 手順

### Step 1: 既存設定を読む

- `~/.claude/AGENTS.md`（user-level の実体。`CLAUDE.md` は互換 symlink）
- [references/skill-design.md](references/skill-design.md)（スキルの設計原則。作る前に末尾まで読む）
- `~/.claude/context/claude-customization-guide.md`（置き場所の判定・公開リポジトリに書く内容・書き方・§7 監査 rubric）
- `~/.claude/skills/*/SKILL.md` の frontmatter（name・description）。同じ機能のスキルが無いか、description の境界が衝突しないかを見る
- `--project` のときは追加で `./CLAUDE.md`・`./.claude/context/*.md`・`./.claude/rules/*.md`

### Step 2: 置き場所を決める

claude-customization-guide.md「1. 知識の置き場所判定」で、Skill にするか CLAUDE.md に足すかを決める。常時適用するルールで CLAUDE.md が200行以下に収まるなら CLAUDE.md に足す。Commands（`.claude/commands/`）はレガシー形式なので新規には使わない。

スコープ（user / project）も同ガイド「スコープ配置」で決める。既存スキルとの重複・スコープの判断が割れるときは、ユーザーに確かめる（Claude Code: AskUserQuestion）。

### Step 3: 設計する

設計原則（frontmatter・description・本文の長さ・references の分け方・degrees of freedom）は references/skill-design.md に従う。加えて次を決める。

- **invocation**: 誰が到達すべきかで選ぶ。モデル自身や他スキルが到達すべきなら model-invoked（既定。description が常時コンテキストに載る）。手動でしか呼ばないなら `disable-model-invocation: true`（description は人間向けの一行要約でよい）
- **依存する他スキル・context**: 独立の節にせず、読むタイミングと一緒に本文の該当手順に書く（例: 「手順3の前に `context/x.md` を Read する」）。他スキルへの依存は「`/xxx` を実行する」の形にし、他スキルのディレクトリ内のファイルを直接参照しない
- **委譲**: Agent tool を呼ぶ手順には `model` の値を書く（用途と値の対応は `context/delegation.md`「モデルの選択」）

description の例:

```yaml
# Good
description: PRレビュー。PR番号・ブランチ名指定時またはレビュー依頼時に使用。境界: ローカル未コミット変更→code-review、自ブランチの提出前確認→self-review。

# Bad
description: PRレビュー。
```

### Step 4: 作る

配置先:

- `--user`: `~/.claude/skills/<skill-name>/`
- `--project`: `./.claude/skills/<skill-name>/`

```
<skill-name>/
├── SKILL.md              # invoke 時にロード（500行未満）
└── references/           # 必要時のみロード
    └── detail.md
```

テンプレート:

```yaml
---
name: <skill-name>
description: <何をするか>。<いつ使うか>。境界: <使わない条件・棲み分け>。
# オプション:
# allowed-tools: Read, Grep, Glob          # ツールの事前承認（制限ではない。制限は disallowed-tools）
# disallowed-tools: Write, Edit            # ツールをプールから除去
# disable-model-invocation: true           # 手動起動のみ
---

# <Skill Name>

[1〜2文で概要]

## 手順

[具体的な手順。依存する context・他スキルは、使う手順の中で書く]
```

### Step 5: 試して報告する

代表的な実タスク（作り物でないもの）でスキルを発火させ、挙動を見る。詰まる箇所・読まれないファイル・予想外の探索順があれば本文に反映する。期待どおり動かないときは次で診断する。

- **早期完了**: 手順の終わりの状態を具体的に書く。それでも直らなければ後続の手順を別ファイルに分ける
- **重複**: 同じ意味が複数箇所にある → 1か所に集める
- **堆積**: 追記で溜まった古い層 → 削る
- **肥大**: 長すぎる → references/ に出すか分割する
- **no-op**: デフォルト挙動を変えない行 → 削る

作ったファイルの一覧と使い方の例を報告する。

### Step 6: コミット

- user-level（`~/.claude/skills/`）に作ったら、そのターンで `/commit --push` を実行する（AGENTS.md「コミット・ブランチ・PR」）
- project-level に作ったら、`/commit` の直コミット可否の判定に従う
