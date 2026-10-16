# Skills設計原則

skillを作る・直すときの原則。指示ファイル全般の原則（置き場所の判定・ロード機構・書き方・監査rubric）は `context/claude-customization-guide.md` が真実源。

## いつSkillにするか

- タスク限定の手続き知識・社内固有ワークフロー・大量の参照資料・決定論的スクリプト。「毎回は要らないが、あるタスクでは深く要る」もの
- 3アーキタイプ: A=Markdownのみ / B=+scripts / C=+外部連携。Aから始め、必要な場合にのみ複雑さを追加する

## frontmatter仕様（Claude Code。全フィールド任意、descriptionのみ推奨）

```yaml
---
name: skill-name            # 省略時ディレクトリ名。コマンド名はディレクトリ名由来
description: 何をするか。いつ使うか。使わない条件。
# 主な任意フィールド:
# when_to_use: トリガー句（descriptionに合算、計1536字まで）
# allowed-tools: Read, Grep, Glob   # ツールの「事前承認」（permission prompt削減）
# disallowed-tools: Write, Edit     # ツールをプールから除去（制限はこちら）
# disable-model-invocation: true    # 手動起動のみ。descriptionが文脈から外れる
# user-invocable: false             # /メニュー非表示（モデル専用）
# model / effort / context: fork / agent / paths / argument-hint / hooks
---
```

- `allowed-tools`は事前承認であって制限ではない（全ツールは引き続き呼び出せる）。ツールを実際に外すには`disallowed-tools`かpermission denyを使う
- read-only系skill（検索・レビュー・監査）には`allowed-tools`でread系を事前承認するとprompt削減になる
- 命名: 小文字英数字とハイフンのみ・64字以内・動名詞（gerund）推奨・予約語`claude`/`anthropic`不可

## description（発火しない原因はほぼ常にここ。instructionsではない）

- 「何をするか」+「いつ使うか（具体的トリガー語・文脈）」+「使わない条件（境界・類似skillとの棲み分け）」を三人称で書く。exclusion clauseが誤発火と発火漏れの両方を防ぐ
- 曖昧語（「〜を支援」等）は選択失敗を招く。skillを象徴する語を先頭に。同義語の言い換え列挙は重複、本当に異なる使用分岐だけ列挙する
- `<` `>` を含めない（インジェクション対策・パース失敗防止）

## 本文（SKILL.md）

- 500行未満に保つ。本文は「オンボーディング資料の目次」。詳細手順・テンプレ・稀にしか使わない内容はreferences/に分割
- 参照は1階層まで（references/内からさらに参照しない）。100行を超えるreferenceファイルには冒頭に目次を付ける
- 各情報に「Claudeが既に知らないことか？」を問う。知っていることは書かない
- Gotchas（既知の落とし穴と対処）と入出力例2〜3対は成熟skillの最良の資産
- 時限的な情報（バージョン番号・日付依存）を避け、用語は全体で一貫させる
- degrees of freedom: 自由度をタスクの脆さに合わせる。High=テキスト指示（判断が要る）/ Medium=パラメータ付きscript / Low=固定コマンド列（壊れやすい・決定論が要る）。今のモデルは細かい段取りより目的と制約から組んだほうがよく動くので、Lowは決定論が要る箇所に限る
- スクリプトは「実行するのか、読んでコンテキストに入れるのか」を明示する。必要パッケージを列挙し、パスはforward slash
- 他skillへの依存は「`/xxx` スキルを実行する」というプロース形式で書く（ディレクトリ内ファイルの直接パス参照はしない）

## 検証・改善ループ

- evaluation-driven: 先にevalを作る（skill無しで実タスクを実行→失敗を記録→3シナリオ→baseline→最小の指示を足して反復）
- 作成後は実タスク（作り物でない）で挙動観察: 詰まる箇所・予想外の探索順・読まれないファイル・繰り返し読むファイルを見つけ、本文に反映
- 実際に使うモデル（既定のOpusと、委譲先に指定するモデル）で動作確認
