# Claude Code カスタマイズガイド（CLAUDE.md / Skills / Hooks 設計の真実源）

user-level / project-level 共通の指示ファイル設計原則。CLAUDE.md・skills・context の作成・編集・監査時に読む。

> 本ガイドは Claude Code 固有の機構（@import・hooks・settings.json 等）を扱う。user-level の実体ファイルは `~/.claude/AGENTS.md`（`CLAUDE.md` は互換 symlink）であり、本ガイドの「CLAUDE.md」は user-level ではこの実体を指す（project-level は従来どおり CLAUDE.md 命名）。
仕様の記述は公式ドキュメント（code.claude.com/docs）が根拠。実測・ヒューリスティック由来の数値は目安として扱う。

## 1. 知識の置き場所判定

同じ知識でも置き場所で費用対効果が変わる。追加・改善のたびに仕分ける。

| 置き場所 | 向いているもの | 理由 |
|---|---|---|
| **CLAUDE.md** | ほぼ全タスクに普遍的に効く最小限の文脈（stack / repoマップ / 主要コマンド / 非自明な規約 / 検証方法） | 毎セッション冒頭に全ロード。太ると全部が薄まる |
| **Skill** | 特定タスク限定の手続き知識・大きな参照資料・決定論的スクリプト | メタデータのみ常駐、本体は必要時ロード |
| **context/（@なし参照）** | タスク限定の詳細ガイド（Read-when誘導で必要時に読む） | 常駐コストゼロ。トリガー条件の明記が必須 |
| **Hook / permissions.deny** | 絶対に破ってはいけない決定論的ガード | モデル判断に依存せず100%強制 |
| **Subagent** | 多数ファイル読み・探索・独立レビュー | 別文脈で走り結論だけ持ち帰る |
| **linter / formatter** | フォーマット・import順・インデント | LLMより速く安く100%一貫 |

判断原則: 「この行を消したらClaudeが実際に間違えるか？間違えないなら削る」。Claudeが指示なしでできること・言語/FWの常識は書かない。

## 2. ロード機構の事実（設計の前提。誤解が多い）

- **`@path` importは参照元の読み込み時に即時・再帰的に全ロードされる**（再帰importは最大4 hops）。CLAUDE.mdからの@importは**毎セッション常駐**を意味する。「必要時にのみロードされる」は誤り。バッククォートで囲んだパス（`` `@path` ``）はimportされずリテラル扱い
  - 常駐させたくない参照は`@`を付けず、プレーンパス+「Read when: ○○の時に必ずRead」形式で誘導する
- **Skills**: 常駐するのはname/description（+when_to_use）のみ（約100トークン/skill）
  - skill一覧のdescription予算は**モデル文脈窓の1%**（`skillListingBudgetFraction`で調整可）。溢れると呼び出し頻度の低いskillから順にdescriptionが切り詰められる。`/doctor`で実際のコストと上位の寄与skillを確認できる
  - description+when_to_use合算は1,536字で切断される（`skillListingMaxDescChars`で変更可）
- **SKILL.md本文はinvoke時にロードされる**。auto-compaction時は各skillの最新invoke分を要約の後に再添付するが、**各skill先頭5,000トークンまで・全skill合計25,000トークンの予算**を共有する。予算は最後にinvokeしたskillから充填されるため、1セッションで多数invokeすると古いskillは完全に落ちる
  - skill descriptionの一覧そのものも`/compact`後は再注入されず、invokeしたskillのみが保持される
  - → タスク全体を通して効かせたい指示は、skill本文でなくCLAUDE.md等のstanding instructionに置く
- references/等の同梱ファイルは必要時のみロード。**スクリプトは実行され出力だけが文脈に入る**（コード本体は入らない）
- `.claude/rules/`: 各.mdが自動ロード。`paths`フロントマターでファイルパターン条件付きロード可

| 仕組み | ロードタイミング |
|--------|-----------------|
| `@path` import | 参照元読み込み時（CLAUDE.md起点なら毎セッション） |
| プレーンパス + Read-when | Claudeが条件に該当してReadした時のみ |
| skills本文 | invoke時（compact後は上記の予算内で再添付） |
| `rules/`（pathsあり） | マッチするファイルを扱う時のみ |

### 層の位置関係（公式で確認済み）

指示が実際に注入される順序・層は次の通り:

1. **system prompt**（公式記載: 約4,200トークン。出典 context-window.md）
2. その**末尾に output style が追記される**（`"All output styles have their own custom instructions added to the end of the system prompt."` output-styles.md）
3. **user message として CLAUDE.md が注入される**（`"CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance, especially for vague or conflicting instructions."` memory.md）
4. 会話（ユーザー発話・ツール結果等）

**帰結**: 応答形式の規定は **output style に置くのが最も効く**（system prompt の一部になり、かつ system prompt 前文が応答形式の参照先として output style を名指ししている）。CLAUDE.mdは公式に**遵守保証なし**と明記された層である。

**関連する公式仕様**:
- `keep-coding-instructions`: `true`でClaude Code組み込みのソフトウェアエンジニアリング指示を保持、デフォルトの`false`では**削除**される
- UserPromptSubmit hook: stdoutがClaudeに見える3イベントの1つ（他はSessionStart / UserPromptExpansion）。複数hookは並列実行され同一ハンドラは自動重複排除される。`hookSpecificOutput.additionalContext`で注入、上限10,000文字。ブロックはexit **2**（Unix慣例の1ではない）。出典 hooks.md

## 3. CLAUDE.md 設計原則

### サイズと内容
- 公式は「**1ファイルあたり200行未満を目標**（target under 200 lines per CLAUDE.md file）。長いほどcontextを消費し遵守率が下がる」と明記。コミュニティ実測は60〜300行の範囲に分布。「肥大したCLAUDE.mdは指示自体を無視させる」
- 「ルールがあるのに破られ続ける」のはファイルが長すぎてルールが埋もれているサイン
- 入れるもの / 入れないもの:

| ✅ 入れる | ❌ 入れない |
|---|---|
| 推測不能なコマンド（build/test/lint、コードフェンスで） | Claudeが推測できること |
| 既定と異なるstyle・非自明な規約 | 標準的な言語・FWの慣習 |
| PJ固有のアーキテクチャ判断とその理由 | 詳細なAPIドキュメント |
| 環境のクセ・非自明なgotcha | 頻繁に変わる情報 |
| branch/PR規約、検証方法 | ファイルの逐次説明 |

### 書き方
- **命令形で書く**（「TypeScript strictモードを使用する」）。ポインタ（`file:line`）優先、スニペットは陳腐化する
- **検証可能な具体ルール**にする（「適切に処理する」→「エラーはResult型で返し、throwは使わない」）
- **否定形より肯定形**: 「Xを使うな」はXの概念を活性化する。「Yのみを使う」+代替の提示に書き換える
- **理由を添えて汎化させる**: 裸の禁止より「○○禁止。△△だから」。理由は明示していないエッジケースへの判断基準になる
- **強制ルールと推奨を分離**: MUST-follow（違反=バグ）とSHOULD-follow（ベストエフォート）をセクションで分ける
- **強調（IMPORTANT / YOU MUST）は公式も推奨する手段**。ただし全部を強調すると何も強調されない。乱用しない
- システムプロンプト既定と競合するルールは散文では負けやすい。hookでの強制と併記する（意図はCLAUDE.md、強制はhook）

### 保守
- 1行追加してよいのは「Claudeが実際に犯した間違いをその行が防げた」時だけ。仮想のルールを足さない
- **3回言っても直らないルールはhook / permissions.denyへ格上げする**
- 定期的にClaude自身に見直しを依頼し、矛盾・重複・no-op行（デフォルト挙動を変えない行）を削除する

### スコープ配置

| 内容 | 配置場所 |
|------|---------|
| 全PJ共通の作業フロー | user-level（~/.claude/） |
| メモリディレクトリ・品質チェックコマンド | project-level |
| パス固有ルール | project-level `rules/`（pathsあり） |
| 領域固有の規約（モノレポ） | サブディレクトリCLAUDE.md（そのディレクトリに触れた時だけ読まれる） |

### ドキュメント分離の原則

| 対象 | 配置場所 |
|------|---------|
| 人間向け | README.md, docs/ |
| エージェント向け | CLAUDE.md, context/, rules/ |

## 4. Skills 設計原則

### いつSkillにするか
- タスク限定の手続き知識・社内固有ワークフロー・大量の参照資料・決定論的スクリプト。「毎回は要らないが、あるタスクでは深く要る」もの
- 3アーキタイプ: A=Markdownのみ / B=+scripts / C=+外部連携。**Aから始め、必要な場合にのみ複雑さを追加する**

### frontmatter仕様（Claude Code。全フィールド任意、descriptionのみ推奨）

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

- **`allowed-tools`は事前承認であって制限ではない**（全ツールは引き続き呼び出せる）。ツールを実際に外すには`disallowed-tools`かpermission denyを使う
- read-only系skill（検索・レビュー・監査）には`allowed-tools`でread系を事前承認するとprompt削減になる
- 命名: 小文字英数字とハイフンのみ・64字以内・動名詞（gerund）推奨・予約語`claude`/`anthropic`不可

### description（発火しない原因はほぼ常にここ。instructionsではない）
- 「**何をするか**」+「**いつ使うか**（具体的トリガー語・文脈）」+「**使わない条件**（境界・類似skillとの棲み分け）」を三人称で書く。exclusion clauseが誤発火と発火漏れの両方を防ぐ
- 曖昧語（「〜を支援」等）は選択失敗を招く。skillを象徴する語を先頭に。同義語の言い換え列挙は重複、本当に異なる使用分岐だけ列挙する
- `<` `>` を含めない（インジェクション対策・パース事故防止）

### 本文（SKILL.md）
- **500行未満に保つ**。本文は「オンボーディング資料の目次」。詳細手順・テンプレ・稀にしか使わない内容はreferences/に分割
- 参照は**1階層まで**（references/内からさらに参照しない）。**100行を超えるreferenceファイルには冒頭に目次**を付ける
- 各情報に「Claudeが既に知らないことか？」を問う。知っていることは書かない
- **Gotchas**（既知の落とし穴と対処）と**入出力例2〜3対**は成熟skillの最良の資産
- 時限的な情報（バージョン番号・日付依存）を避け、用語は全体で一貫させる
- **degrees of freedom**: 自由度をタスクの脆さに合わせる。High=テキスト指示（判断が要る）/ Medium=パラメータ付きscript / Low=固定コマンド列（壊れやすい・決定論が要る）
- スクリプトは「実行するのか、読んでコンテキストに入れるのか」を明示する。必要パッケージを列挙し、パスはforward slash
- 他skillへの依存は「`/xxx` スキルを実行する」というプロース形式で書く（ディレクトリ内ファイルの直接パス参照はしない）

### 検証・改善ループ
- **evaluation-driven**: 先にevalを作る（skill無しで実タスクを実行→失敗を記録→3シナリオ→baseline→最小の指示を足して反復）
- 作成後は**実タスク**（作り物でない）で挙動観察: 詰まる箇所・予想外の探索順・読まれないファイル・繰り返し読むファイルを見つけ、本文に反映
- 可能なら複数モデル（Haiku/Sonnet/Opus）で動作確認

## 5. Hooks・検証機構

- 検証のゲート強度: (a) 同一プロンプト内でcheck実行 → (b) `/goal`条件で毎ターン再評価 → (c) Stop hook（scriptで判定、通らない限りターン終了をブロック。8連続ブロックで強制終了） → (d) verification subagent
- **証拠を出させる**: 成功を主張させず、test出力・実行コマンド・スクリーンショットを提示させる
- adversarial reviewer（gapを探せと指示されたレビュアー）は健全な実装でもgapを報告しがち。レビュアー側で観点を絞ると報告自体が減るため、絞り込みは受け取った側（lead）のフィルタで行う（運用: `context/agent-cli-guide.md`「Severity別のlead判断基準」）
- 繰り返し破られるCLAUDE.mdルールはhookに格上げする（CLAUDE.mdに意図、hookで強制の二重化）

## 6. コンテキスト最適化

- コンテキスト除外: `.claudeignore`という**公式機能は存在しない**（コミュニティ記事由来の誤情報）。秘匿・不要パスは`permissions.deny`の`Read()`ルール、モノレポの他チームCLAUDE.md除外は`claudeMdExcludes`を使う
- 無関係なタスク間で`/clear`。探索・大量ファイル読みはsubagentへ（結論のみ持ち帰る。要約は1,000〜2,000トークン目安）
- 未使用MCPサーバーを無効化（ツール定義がサイレントに文脈を消費）
- **minimal ≠ short**: 「right altitude」= 脆いハードコードと曖昧な高レベル指示の中間。必要情報を削るのでなく、常駐から外して必要時に十分供給する再配置が正解
- エッジケースの羅列より、多様で正準的なfew-shot例を少数
- 知見: 長時間タスクの機械可読な状態ファイル（機能リスト・pass/fail）はMarkdownよりJSONの方がmodelに勝手に上書きされにくい（本環境のメモリ形式は現状維持。99_history.md参照）

## 7. 監査rubric（CLAUDE.md / skills / context の定期監査用）

`/instructions-audit` スキルが使用する。指摘は次の4分類で出す:

**(a) 削除すべき行**
- Claudeが指示なしでも守れている / 言語・FWの常識 / no-op行（デフォルト挙動を変えない）
- 出典不明の数値を規範として断定している行
- 他ファイルとの重複（真実源を1つ決めて他は参照に）・矛盾（どちらかを削る）

**(b) hook・linter・denyに移すべき行**
- 決定論的に判定できる禁止事項（コマンドパターン・パス書き込み）
- フォーマット・スタイル規約（linter/formatterの仕事）
- 3回以上破られた散文ルール

**(c) Skill化・Read-when化すべき塊**
- 特定タスクでしか使わない手続き知識が常駐している（CLAUDE.md内の長大セクション、@importされた大型ガイド）
- テンプレート・チェックリスト・コマンド定型がSKILL.md本文に埋まっている（references/へ）

**(d) description・構造が弱いSkill**
- 「何を/いつ/使わない条件」が欠ける、曖昧語、1,536字超過で切れている
- 本文500行超、references未分割、read-onlyなのにallowed-tools未宣言
- 理由なしの強調乱用（CRITICAL/MUST/絶対の数を数え、理由付き形式に）
- 実挙動の観察: 読まれないファイル / 繰り返し読まれる内容（本文へ昇格） / リンク未追従（参照を目立たせる）

**(e) system prompt との衝突・重複**
- 本体system promptと**逆**を言う指示は、原文を引用して名指しで優先を宣言しないと一般論では負ける（引用なしの「〜を優先する」だけでは弱い）
- 本体system promptと**同方向**の指示は重複であり削除候補（system promptが既に強制している内容をCLAUDE.md/skillで繰り返さない）
- 発火条件は、モデルの自己分類（「複雑な」「重要な」「必要に応じて」等）ではなく、**着手前に確認できる事実**（ファイル数・拡張子・キーワードの有無等）で書く

## 8. マルチエージェント品質パターン

- **Writer/Reviewer分離**: 実装バイアス排除のため、生成と評価を別コンテキストに分ける。leadをreviewer/オーケストレーター、実装をwriter（subagent）に分離するのが本環境の既定運用（詳細・使い分け基準は@context/tool-claude-code.md「委譲判断」）
- 旧記述「Subagentの毎回明示呼び出しは性能低下要因」は実運用の知見（lead/impl分業のトークン効率・品質実測、2026-07）と矛盾したため撤回。委譲要否はタスク規模で機械的に判定する（同上「委譲判断」参照）

## 9. 継続的改善

- CLAUDE.mdは生きた文書。望ましくない動作の修正指示を追記し、古い指示を削除
- コードレビューは新ルールの最良の供給源（PRで見つかった未文書化規約をCLAUDE.mdへ）
- モデル更新時はハーネス（ルール・ワークフロー）を再検証し、不要になった制約を除去
- モデル更新時は、ハーネス側に残った旧世代前提の記述（世代名を含む見出し・引き継いだeffort既定値・旧仕様のツール名/パラメータ）を洗い出して更新する

自律実行の指針は `context/tool-claude-code.md`「自律実行の前提」を真実源とする。
