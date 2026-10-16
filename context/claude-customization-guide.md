# Claude Codeカスタマイズガイド（CLAUDE.md / Skills / Hooks設計の真実源）

user-level / project-level共通の指示ファイル（CLAUDE.md・skills・context・hooks）の設計原則と監査rubric。

> 本ガイドはClaude Code固有の機構（@import・hooks・settings.json等）を扱う。user-levelの実体ファイルは `~/.claude/AGENTS.md`（`CLAUDE.md` は互換symlink）であり、本ガイドの「CLAUDE.md」はuser-levelではこの実体を指す（project-levelは従来どおりCLAUDE.md命名）。
仕様の記述は公式ドキュメント（code.claude.com/docs）が根拠。

## 1. 知識の置き場所判定

同じ知識でも置き場所で費用対効果が変わる。追加・改善のたびに仕分ける。

| 置き場所 | 向いているもの | 理由 |
|---|---|---|
| **CLAUDE.md** | ほぼ全タスクで普遍的に必要な最小限の文脈（stack / repoマップ / 主要コマンド / 非自明な規約 / 検証方法） | 毎セッション冒頭に全ロード。長くなると全指示の影響が弱まる |
| **Skill** | 特定タスク限定の手続き知識・大きな参照資料・決定論的スクリプト | メタデータのみ常駐、本体は必要時ロード |
| **context/（@なし参照）** | タスク限定の詳細ガイド（Read-when誘導で必要時に読む） | 常駐コストゼロ。トリガー条件の明記が要る |
| **Hook / permissions.deny** | 破られると困る決定論的ガード | モデル判断に依存せず強制できる |
| **Subagent** | 多数ファイル読み・探索・独立レビュー | 別文脈で実行し結論だけを返す |
| **linter / formatter** | フォーマット・import順・インデント | LLMより速く安く一貫する |

判断原則: 「この行を消したらClaudeが実際に間違えるか？間違えないなら削る」。Claudeが指示なしでできること・言語/FWの常識は書かない。

## 2. ロード機構の事実（設計の前提。誤解が多い）

- **`@path` importは参照元の読み込み時に即時・再帰的に全ロードされる**（再帰importは最大4 hops）。CLAUDE.mdからの@importは毎セッション常駐を意味する。「必要時にのみロードされる」は誤り。バッククォートで囲んだパス（`` `@path` ``）はimportされずリテラル扱い
  - 常駐させたくない参照は`@`を付けず、プレーンパス+「Read when: ○○の前にRead」の形で誘導する
- **Skills**: 常駐するのはname/description（+when_to_use）のみ（約100トークン/skill）
  - skill一覧のdescription予算はモデル文脈窓の1%（`skillListingBudgetFraction`で調整可。Claude Code 2.1.x時点）。溢れると呼び出し頻度の低いskillから順にdescriptionが切り詰められる。`/doctor`で実際のコストと上位の寄与skillを確認できる
  - description+when_to_use合算は1,536字で切断される（`skillListingMaxDescChars`で変更可。Claude Code 2.1.x時点）
- **SKILL.md本文はinvoke時にロードされる**。auto-compaction時は各skillの最新invoke分を要約の後に再添付するが、各skill先頭5,000トークンまで・全skill合計25,000トークンの予算を共有する（Claude Code 2.1.x時点）。予算は最後にinvokeしたskillから充填されるため、1セッションで多数invokeすると古いskillは一切再添付されない
  - skill descriptionの一覧そのものも`/compact`後は再注入されず、invokeしたskillのみが保持される
  - → タスク全体を通して適用したい指示は、skill本文でなくCLAUDE.md等のstanding instructionに置く
- references/等の同梱ファイルは必要時のみロード。スクリプトは実行され出力だけが文脈に入る（コード本体は入らない）
- `.claude/rules/`: 各.mdが自動ロード。`paths`フロントマターでファイルパターン条件付きロード可
- ブロックレベルのHTMLコメント `<!-- -->` は注入前に除去される。保守メモはここに書ける

| 仕組み | ロードタイミング |
|--------|-----------------|
| `@path` import | 参照元読み込み時（CLAUDE.md起点なら毎セッション） |
| プレーンパス + Read-when | Claudeが条件に該当してReadした時のみ |
| skills本文 | invoke時（compact後は上記の予算内で再添付） |
| `rules/`（pathsあり） | マッチするファイルを扱う時のみ |

### 層の位置関係（公式で確認済み）

指示が実際に注入される順序・層は次の通り:

1. **system prompt**（公式記載: 約4,200トークン。出典context-window.md。Claude Code 2.1.x時点）
2. その**末尾にoutput styleが追記される**（`"All output styles have their own custom instructions added to the end of the system prompt."` output-styles.md）
3. **user messageとしてCLAUDE.mdが注入される**（`"CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance, especially for vague or conflicting instructions."` memory.md）
4. 会話（ユーザー発話・ツール結果等）

**帰結**: 応答形式の規定は output styleに置くのが最も効果が高い（system promptの一部になり、かつsystem prompt前文が応答形式の参照先としてoutput styleを名指ししている）。CLAUDE.mdは公式に遵守保証なしと明記された層である。

**関連する公式仕様**:
- `keep-coding-instructions`: `true`でClaude Code組み込みのソフトウェアエンジニアリング指示を保持、デフォルトの`false`では削除される
- UserPromptSubmit hook: stdoutがClaudeに見える3イベントの1つ（他はSessionStart / UserPromptExpansion）。複数hookは並列実行され同一ハンドラは自動重複排除される。`hookSpecificOutput.additionalContext`で注入、上限10,000文字。ブロックはexit **2**（Unix慣例の1ではない）。出典hooks.md

## 3. CLAUDE.md設計原則

### サイズと内容
- 公式は「1ファイルあたり200行未満を目標（target under 200 lines per CLAUDE.md file）。長いほどcontextを消費し遵守率が下がる」と明記
- 「ルールがあるのに破られ続ける」のはファイルが長すぎてルールが埋もれているサイン
- 入れるもの / 入れないもの:

| ✅ 入れる | ❌ 入れない |
|---|---|
| 推測不能なコマンド（build/test/lint、コードフェンスで） | Claudeが推測できること |
| 既定と異なるstyle・非自明な規約 | 標準的な言語・FWの慣習 |
| PJ固有のアーキテクチャ判断とその理由 | 詳細なAPIドキュメント |
| 環境のクセ・非自明なgotcha | 頻繁に変わる情報 |
| branch/PR規約、検証方法 | ファイルの逐次説明 |

### 公開リポジトリに書く内容

`~/.claude` は公開リポジトリ。AGENTS.md・`context/`・`skills/` に書く内容は、汎用化した規則そのものだけにする。

- **実例・出来事・日付・固有名詞を書かない**: 「実例: ◯◯で〜が起きた」「〜という指摘があった」「YYYY-MM実測」、勤務先・プロダクト・取引先・人物・社内ツール・業務コードの関数名 / ファイル名は書かない。規則が成り立つ理由は一般的な事実として規則の文面に織り込む。例示が必要なら `<機能名>` のプレースホルダにする。日付の例外は、外部仕様のas-of表明と、陳腐化管理が規則本体に組み込まれた判定結果のみ。個別の出来事・実値はgit管理外のメモリディレクトリ（`05_log.md` / `99_history.md`）に書く
- **規則は防ぎたい結果で書き、手段（パラメータ名・コマンド・ツール名）は添え物にする**。手段だけを名指しした規則は、別の手段で同じ結果を起こしても字面上は守られたことになる（「◯◯を `false` にする」ではなく「本文に◯◯を含めない（`false` にするのはそのため）」）
- **記録するルールは一次情報と突き合わせてから書く**。ルール本文は指示ファイルに1箇所だけ置き、記録・追跡ファイルからは参照する（複写すると変更時に片方だけ更新されて食い違う）
- **毎ターン・毎作業に宣言文・記録・確認の往復を挟ませる規則は、防いでいる失敗がそのコストを上回ることを確かめてから書く**。宣言・記録・確認の手順は規則の数だけ積み重なり、システムプロンプトの既定動作（そのまま実行する・簡潔に書く）を打ち消す

### 書き方
- **命令形で書く**（「TypeScript strictモードを使用する」）。ポインタ（`file:line`）優先、スニペットは陳腐化する
- **検証可能な具体ルール**にする（「適切に処理する」→「エラーはResult型で返し、throwは使わない」）
- **否定形より肯定形**: 「Xを使うな」はXの概念を活性化する。「Yのみを使う」+代替の提示に書き換える
- **理由を添えて汎化させる**: 裸の禁止より「○○しない。△△だから」。理由は明示していないエッジケースへの判断基準になる
- **強調（IMPORTANT / YOU MUST / CRITICAL / 絶対）は既定では付けない**。今のモデルは平叙文の指示にも従い、強調は適用しすぎを招く。付けるのは、軽視されると実際に確かめた指示1つに限り、理由を並べて書く
- **細かい手順より一般的な指示で書く**。今のモデルは手書きの段取りより目的と制約から組んだほうがよく動く。手順を固定するのは、順序を外すと壊れる操作（決定論が要るもの）だけにする
- システムプロンプト既定と競合するルールは散文だけでは既定の方が優先されやすい。hookでの強制と併記する（意図はCLAUDE.md、強制はhook）

### 保守
- 1行追加してよいのは「Claudeが実際に犯した間違いをその行が防げた」時だけ。仮想のルールを足さない
- 3回言っても直らないルールはhook / permissions.denyへ格上げする
- 見直しには `/doctor prompt-audit` を使う（旧世代のモデル向けの記述・存在しないファイルやコマンドへの参照・ファイル間の矛盾を検出する。Claude Code 2.1.283以降）。そのうえで矛盾・重複・no-op行（デフォルト挙動を変えない行）を削除する
- 望ましくない動作の修正指示を追記し、古い指示を削除する。コードレビューは新ルールの最良の供給源（PRで見つかった未文書化規約をCLAUDE.mdへ）
- モデル更新時は、ハーネス（ルール・ワークフロー）を再検証し、旧世代前提の記述（世代名を含む見出し・引き継いだeffort既定値・旧仕様のツール名/パラメータ）と不要になった制約を除去する

### スコープ配置

| 内容 | 配置場所 |
|------|---------|
| 全PJ共通の作業フロー | user-level（~/.claude/） |
| PJの品質チェックコマンド・MEMORY_DIRの上書き | project-level |
| パス固有ルール | project-level `rules/`（pathsあり） |
| 領域固有の規約（モノレポ） | サブディレクトリCLAUDE.md（そのディレクトリに触れた時だけ読まれる） |

## 4. Skills設計原則

skillを作る・直すときの原則（いつSkillにするか・frontmatter・description・本文・検証ループ）は `skills/create-skill/references/skill-design.md` が真実源。

## 5. Hooks・検証機構

- 検証のゲート強度: (a) 同一プロンプト内でcheck実行 → (b) `/goal`条件で毎ターン再評価 → (c) Stop hook（scriptで判定、通らない限りターン終了をブロック。8連続ブロックで強制終了） → (d) 第三者による検証（別ベンダーのLLM、またはfresh contextの検証役）。(d) は自分の作業の自己検証を二重化することではない（同一モデルの自己検証は指示なしでも行われている）
- **証拠を出させる**: 成功を主張させず、test出力・実行コマンド・スクリーンショットを提示させる
- adversarial reviewer（gapを探せと指示されたレビュアー）は健全な実装でもgapを報告しがち。レビュアー側で観点を絞ると報告自体が減るため、絞り込みは受け取った側（lead）のフィルタで行う（運用: `context/agent-cli-guide.md`「Severity別のlead判断」）
- 繰り返し破られるCLAUDE.mdルールはhookに格上げする（CLAUDE.mdに意図、hookで強制の二重化）

## 6. コンテキスト最適化

- コンテキスト除外: `.claudeignore`という公式機能は存在しない（コミュニティ記事由来の誤情報）。秘匿・不要パスは`permissions.deny`の`Read()`ルール、モノレポの他チームCLAUDE.md除外は`claudeMdExcludes`を使う
- 無関係なタスク間で`/clear`。探索・大量ファイル読みはsubagentへ（結論のみ返させる）
- 未使用MCPサーバーを無効化（ツール定義が通知なく文脈を消費）
- **minimal ≠ short**: 「right altitude」= 脆いハードコードと曖昧な高レベル指示の中間。必要情報を削るのでなく、常駐から外して必要時に十分供給する再配置が正解
- エッジケースの羅列より、多様で正準的なfew-shot例を少数
- 長時間タスクの機械可読な状態ファイル（機能リスト・pass/fail）は、MarkdownよりJSONの方がmodelに勝手に上書きされにくい

## 7. 監査rubric（CLAUDE.md / skills / contextの定期監査用）

`/instructions-audit` スキルが使用する。指摘は次の4分類で出す:

**(a) 削除すべき行**
- Claudeが指示なしでも守れている / 言語・FWの常識 / no-op行（デフォルト挙動を変えない）
- 出典不明の数値を規範として断定している行
- 他ファイルとの重複（真実源を1つ決めて他は参照に）・矛盾（どちらかを削る）
- 明示の検証・再確認ステップ（「最後に検証ステップを入れる」「回答前に再確認する」「検証用subagentを使う」）。今のモデルは指示なしで自分の作業を検証し、重ねると過剰検証になる。ユーザーが求めた動作確認（変更を実際に動かす・スクリーンショットを撮る）はこの対象外
- 思考・推論を応答に書き出させる指示（逐語・固定書式で考えを書かせるもの）。`reasoning_extraction` の拒否カテゴリで断られる原因になる。結論の短い説明や実施内容の要約を求めるのはよい
- 旧モデル名・旧effort既定・旧仕様のツール名を前提にした記述
- 旧モデル向けの細かすぎる手順（目的と制約を書けば足りる段取りの列挙）

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

**(e) system promptとの衝突・重複**
- 本体system promptと逆を言う指示は、原文を引用して名指しで優先を宣言しないと一般論では原文の方が優先される（引用なしの「〜を優先する」だけでは弱い）
- 本体system promptと同方向の指示は重複であり削除候補（system promptが既に強制している内容をCLAUDE.md/skillで繰り返さない）
- 発火条件は、モデルの自己分類（「複雑な」「重要な」「必要に応じて」等）ではなく、着手前に確認できる事実（ファイル数・拡張子・キーワードの有無等）で書く
