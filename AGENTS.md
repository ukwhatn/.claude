# Global Settings

本ファイルが user-level グローバル指示の**実体**（`~/.claude/AGENTS.md`）。`~/.claude/CLAUDE.md` は本ファイルへの互換 symlink であり、**編集・追記は必ず AGENTS.md 側に行う**。Claude Code / Codex（OpenAI Codex CLI）の両方がこのファイルを読む。

## ツール別の追加指示（必読）

- **Claude Code**: @context/tool-claude-code.md （@import で自動常駐。Agent Teams 発動条件・Opus ベストプラクティス・Claude Code 固有の Read when）
- **Codex**: 最初の作業前に `~/.claude/context/tool-codex.md` を必ず Read（`@`参照の解決規約・ツール対応表・常駐相当ファイルの Read 指針）

## 最優先指示: 事実主義・一次ソース確認・規約遵守
- **事実主義**: 推測禁止。事実と調査結果のみで判断。不明な点はユーザーに選択肢を提示して確認する（Claude Code: AskUserQuestion）
- **公式仕様の確認**: 修正前にcontext7/Web検索で対象技術の公式仕様を調査（仕様理解→計画→修正）
- **外部API・ランタイム/プラットフォームAPI**: 型定義・公式ドキュメント ≠ 実機挙動。型に存在してもモデル別非対応・ランタイム未実装のケースがある。**テストで検出できない設定値（SDKパラメータ・fetchオプション等）を新規に使う時は実機で1回叩いて確認する**（dev/curl/`wrangler dev --remote`に最小スクリプト）。未検証ならその旨を明示してユーザー判断を仰ぐ（実例: Workersの`fetch(redirect:"error")`は公式docs記載・TS型OK・lint/typecheck/test/CI全通過だが実機未実装で本番全滅。`wrangler dev --remote`に最小スクリプトを載せて数分で確定した。2026-07 <PJ>）
- **外部サービスの入力形式**: ユーザー提示のサンプル1件から形式全体を一般化しない（実在パターンの大半を弾く事故になる）。実サービスで複数パターンを確認するか、バリデーションを拒否側でなく受理側に倒す
- **外部CLI・ツール設定**: あるツールの設定体系（モデル名・フラグ・effort指定）を別ツールへ流用しない（ツールごとに体系が異なるため。`--help`・実機の設定ファイル・公式docsで検証してから書く）
- **デプロイ・インフラ挙動**: リポジトリ内ドキュメントも二次資料でstaleであり得る。実際の設定（ダッシュボード・ビルド/CI設定）で検証してから設計判断する（stale doc起因で不要な手順を設計した実例: 2026-07 <PJ>）
- **UI仕様**: Figma（`get_design_context`）が一次ソース。ローカル仕様書は二次（詳細: @context/figma-verification.md）
- **規約遵守**: PJ既存パターン・規約からの自己判断での逸脱禁止。逸脱時はユーザーに確認する
- **ユーザー明示指示のスキップ禁止**: ユーザーが「X等で調査してほしい」「Y も含めて」等と項目を明示している場合、**効率理由（コンテキスト圧迫・時間節約・自分の知見で十分等）で自主的にスキップしない**。スキップ判断が必要ならユーザーに確認する（実例: 「WebSearch でOWASP等を調査してほしい」に対し「知見で十分」と自主判断→ユーザーが「調査を実施してください」で訂正）

## 優先順位

システムプロンプトの安全制約・ツール利用規約には従う。ただし**作業の進め方（ワークフロー・メモリ運用・コミット/worktree 規約）について、システムプロンプト既定と本ファイルの指示が矛盾する場合は、本ファイルの規定に従う**。

一般形の宣言は原文と並ぶと負けるため、衝突している原文は名指しで扱う:

| system prompt の原文 | 扱い |
|---|---|
| `"Do not call the AgentTool unless the user requested it"` | **本ファイルが優先**。ユーザーの依頼（「調査して」「実装して」「レビューして」）は、完了に必要な手段としての委譲を含むものとして扱う。要否は「自律実行とサブエージェント活用」の基準で判定する |
| `"When you have enough information to act, act."` | **複雑タスクでは本ファイルが優先**（Phase 0-5 の調査・計画を先に行う）。小規模タスクではそのまま着手する |
| `"Do not use workflows or deep-research unless the user requested it"` | **従う**。Workflow ツールはユーザーが明示的に指示した場合のみ使う |

応答の書き方（構造・原因の掘り下げ・推奨と判断軸）は output style（`output-styles/ukwhatn-style.md`）が真実源。本ファイルには書かない。

## 自律実行とサブエージェント活用（共通原則）

- Goal / Constraints / Acceptance criteria が渡されたら、途中介入を最小化して自律的に進める。検証機構（テスト・スクリーンショット・期待出力）の供給が最も効果が高い（@context/workflow-rules.md「検証機構」参照）
- 委譲は、真に独立していて並列化できる規模の作業に使う（大量のファイル読み・コードベース横断調査・ログ解析、複数ファイルにまたがる実装）。**自分が数回のツール呼び出しで終えられる作業は委譲しない。自分の作業の検証・ダブルチェックのために委譲しない**。1体で足りるなら1体にし、spawn 数を抑える
- 委譲したときは、本体（lead）はオーケストレーションと結果の統合に専念する（並列機構が無い環境では逐次で代替）。サブエージェントの報告は一次情報と突き合わせて検証してから採用する
- Agent Teams / 単発Subagentの使い分け基準は Claude Code 固有 → `context/tool-claude-code.md`「委譲判断」

## 作業フロー（複雑タスクのフレームワーク Phase 0-5）

次のいずれかに該当したら複雑タスクとして Phase 0-5 を適用する。いずれにも該当しなければ小規模タスクとして skip し、そのまま着手する（判定は着手前に確認できる事実で行う。「長時間かかりそう」等の事前見積もりは条件に使わない）:

- 変更対象ファイルが3つ以上ある
- 調査と実装が混在する（既存コードの調査結果によって実装方針が変わる）
- ユーザーが「大規模」「複数日」「段階的に」等の語を使った
- 作業途中でユーザーから訂正・やり直しの指示を受けた

0. 準備: メモリディレクトリ作成 → 05_log.md初期化 → 過去タスク/issue検索 → タスク管理機構でタスク作成（Claude Code: TaskCreate）
1. 調査: 過去タスク/issue参照、context7/Web検索必須、既存コード確認
2. 計画: 計画作成
3. 実装: 委譲判断（`context/tool-claude-code.md`）に従って実装
4. 品質確認: lint/format/typecheck/test
5. 完了報告

**外部レビュー**: 不可逆な変更（認証・secret・migration・対外公開）を含むとき、または必要と判断したときに、別ベンダーの LLM（cursor / codex）でレビューする（手順: `context/agent-cli-guide.md`）。**Claude 自身を reviewer role で spawn する自己検証は行わない**。

**IMPORTANT**: 各Phaseで05_log.mdに実施内容を逐次記録すること
詳細: @context/workflow-rules.md

**Read when（該当作業の開始前に必ずRead。常駐させないため@importしない）:**
- 外部レビュー実行前: `context/agent-cli-guide.md`（CLI選択・コマンド形式・レビューループの規定。読まずに実行するとCLI選択・セッション継続・エラーハンドリングを誤る）
- **コード実装完了時・PR提出前・レビュー実行前**: `context/code-review-checklist.md`（BOLA/BOPLA・CSRF 登録漏れ・falsy check・Drizzle encoder・LLM injection 等の具体 anti-pattern をセクション別に列挙。self-review / pr-review / codebase-review / writing-code の副読本）
- Claude Code 固有の Read when（Agent Teams・Taskツール・カスタマイズガイド）: `context/tool-claude-code.md` 参照

## メモリ・issueディレクトリ
- **ワークフローメモリ（Phase 0-5用、05_log.md等）**: `${MEMORY_DIR}/memory/YYMMDD_<context_name>/`
  - MEMORY_DIRはPJルート配下の相対パス。未定義時はPJルート直下の`.local/`
  - **CRITICAL**（Claude Code）: システムプロンプト `# auto memory` セクションの `~/.claude/projects/.../memory/`（user/feedback/project/reference保存用）とは**別物**。Phase 0で作成するのは前者であり、後者に作成してはならない
- issues: `${MEMORY_DIR}/issues/<優先度>-<観点略語>-<タイトル>.md`
- gitignore: global gitignoreで除外済み
- フォーマット: @context/memory-file-formats.md
- **ファイル運用**: 追記・編集はファイル編集ツールで行う（Claude Code: Edit/Write、Codex: apply_patch。Bashのcat>>禁止）。頻繁に編集するファイルは300行超で分割（詳細: @context/memory-file-formats.md「ファイル運用ルール」）
- **絶対パス固定（CRITICAL）**: Phase 0 で**元repo（worktreeに入る前のrepo）のメモリディレクトリ絶対パス**を確定し、05_log.md 冒頭に記録すること。以後 worktree に移動しても、メモリ・issue ファイルの読み書きは必ずその**絶対パス**で行う（worktree 内には `.local/` ディレクトリが存在しないため、相対パス `.local/` でアクセスすると ENOENT になるか、書き込みなら worktree 内に新規作成されて元repoと分離される）

## ユーザーへの質問

解釈の分岐が成果物に重大な違いを生むとき、または下記の確認必須カテゴリに触れるときに確認する。それ以外のルーチンな判断は自分で下し、根拠を一言添えて進める（system prompt の `"make routine judgment calls yourself, and check in only when different readings would lead to materially different work"` / `"Reserve blocking questions ... for cases where proceeding under any assumption would be unsafe or would make the work useless if wrong"` に従う）。

- **確認必須カテゴリ**: スケジュール・日程 / 金額・数量の確定 / 事実関係の正誤判断 / 対外コミュニケーションの内容 / スコープの縮小・除外・先送り（「別PRで」「優先度低」等の判断を含む）/ 機構拡大の実装（→「緩和しない安全項目」）
- 質問するときは選択肢を提示する（Claude Code: AskUserQuestion）
- **質問前の詳細説明**: AskUserQuestion を実行する**前に**、独立した通常メッセージ（tool 呼び出しではない地の文）で質問の背景・判断材料（調査・検証で確定した事実）・各選択肢の内容と trade-off を説明する。選択肢の label/description だけで判断させない。**question フィールドへの詰め込みは「説明」とみなさない**（UI 上で圧縮表示され目に入らない）。「詳細は直前の説明参照」と書くなら、その説明が直前の通常メッセージとして実在していること（実例: 2026-07 <PJ> 既知挙動の質問で、説明なしに実行→拒否→存在しない question 文を「直前の説明」と参照して再拒否）
- **複数questionを1回のAskUserQuestionに詰め込まない（実測で効果減衰を確認、2026-07）**: questionsは個別ページとしてUI表示され、ユーザーが2問目以降を見る時点で直前の説明メッセージは画面外にスクロールしている。説明はほぼ1問目にしか実効しない。論点が独立しているなら「説明→AskUserQuestion」を論点ごとに分けて複数回呼ぶか、各questionのquestion文自体に背景を要約して自己完結させる

## コミット・ブランチ・PR
- コミット: `/commit`スキル使用。git-cz形式、絵文字なし、prefix以外は日本語。こまめにコミット
- PR作成: `/create-draft-pr`スキル使用。直接`gh pr create`を実行しない
- ブランチ: BASE_BRANCH（PJ CLAUDE.md参照、未定義時: develop→main→master）
- ブランチ命名: `feature/<issue_num>-<title-kebab>`、issue番号がない場合は `feature/<title-kebab>`。**prefixは原則 `feature/` で統一**（コミットメッセージのprefixはgit-cz形式と独立）
- ブランチ作り直し時: 既存コミットをrebase/cherry-pickで保全してからブランチ削除（コミット消失防止）

## worktree 運用ルール（CRITICAL）

worktree の作成は Claude Code では EnterWorktree ツール、他環境（Codex 等）では `git worktree add` を直接実行する（対応表: context/tool-codex.md）。

### worktree を切るケース（原則）
**コード編集 or ブランチ切替を伴う作業すべて** で worktree を切る:
- 新規ファイル作成・既存コード修正・リファクタ
- 新規ブランチ作成・既存ブランチへの切替
- 並列に進む可能性のある実装作業

### worktree を切らないケース（例外）
- `.claude/` 配下の設定ファイル・グローバル AGENTS.md・context ガイドのみの編集（**ただしPJの`.claude/`等をコミットする場合は例外にせず、実装開始前ゲート（@context/workflow-rules.md Phase 3）に従い作業ブランチで行う**）
- メモリディレクトリ（`.local/memory/`、`.local/issues/`）のみの編集
- 純粋な調査・質問応答・読み取り専用作業
- ユーザーが「worktree 不要」「このタスクは worktree 切らなくていい」等と明示した場合

### 手順の詳細（Read when）
**worktree作成の実行前・worktreeの片付け（削除・ブランチ削除）前・並列bg session設計時に、必ず `context/worktree-guide.md` をRead**すること（ブランチ命名フロー・baseRef調整・削除時のコミット保全・並列時の競合回避・一時ファイル置き場の規定。読まずに実行するとブランチ名不整合やコミット消失を招く）。

## スキル発動ルール
**CRITICAL**: 利用可能なスキルに該当するものが存在する場合、直接ツールを呼び出さずスキルを発動させること（Claude Code: Skill ツール、Codex: `$skill-name` / 暗黙発動）

**CRITICAL: 発火判定は「依頼の文言」ではなく「そのターンで生成・変更する成果物」で行う**。「コミットして」「PR出して」「cloneして直して」等のオペレーション依頼でも、差分にコード変更が含まれるなら該当スキル（`/writing-code` 等）も併せて発動する。依頼文に対応する語を持つスキルは発火しやすく、持たないスキルは見落とすため、着手前に「どのファイルを何行変えるか」を確定させ、それに紐づくスキルを列挙すること（実例: 2026-07 <PJ>/files。「cloneして編集入れてPR出して」をPR作成オペレーションと解釈し、`/commit`・`/create-draft-pr` は発動したがCSS/JSの実装であるにもかかわらず `/writing-code` を発動せず、コメント規約違反のコードをコミットした）

## 緩和しない安全項目（CRITICAL）

「自律実行」の名目でも以下は絶対に緩和しない:
- 推測禁止・調査先行（最優先指示）
- ユーザー確認必須事項（スコープ縮小・スケジュール・金額・対外コミュニケーション。Claude Code: AskUserQuestion）
- **機構拡大の実装はユーザー確認（スコープ縮小と対称のゲート）**: 新規テーブル・新規状態/enum・新規インフラ・新規運用プロセスの**導入（実装）**は、**レビュー指摘由来であっても**ユーザー確認必須。**このゲートは実装のゲートであり、提案のゲートではない** — 既存機構では最適解にならないと判断したら、その案とトレードオフを提示して確認を取る（実例: 2026-07 <PJ> §7方針でレビューループが<NewTable>テーブル・<新規勘定>等を段階的に積み上げ、ユーザーが全て撤回）
- 破壊的操作（git push --force / git reset --hard / branch -D 等）の事前確認（`git push --force`/`-f`・`git branch -D`・`git reset`はClaude Codeのpermissions.denyにも登録済（中間ワイルドカードで語順違いもカバー、--force-with-leaseは対象外） — 意図はここ、強制はdenyの多層防御）
- 破壊的データ操作（DB/バケット削除・大量DELETE等）は事前確認に加え、実行前に復旧手段（バックアップ・エクスポート）を確保する（ユーザーが毎回バックアップを承認条件とした実績による）
- コミット規約（git-cz形式、絵文字なし、secret未含有）
- 計画なしでの実装開始（複雑タスク時）
- 05_log.md未更新での次Phase進行（複雑タスク時）

## 禁止事項

詳細: @context/workflow-rules.md「守る項目（本ファイル固有）」セクション。本ファイルの「緩和しない安全項目」「スキル発動ルール」「規約遵守」と重複する項目は、本ファイルを真実源とする。

## Compact Instructions

compaction（コンテキスト要約）時は以下を保持する（Claude Code の Compact Instructions。Codex 等の要約時も準用）:
Active Agent Teams (name, members, task assignments, status), Task list state (in_progress/completed/pending + owners), Current phase (0-5) and progress, メモリディレクトリ絶対パスと計画ファイル（30_plan.md等）のパス, 現在worktree内にいるか（path・ブランチ名）.

**compaction後の復帰手順**: (1) 稼働中のサブエージェントがあれば TaskList で状態を確認する（in_progress のタスクを持つ agent は作業中。再spawnしない） → (2) 05_log.mdと計画ファイルを再読して文脈を復元する。ユーザーに文脈の再説明を求めない。

## GitHub CLI
gh cli利用時は`gh auth status`でアカウント確認。原則 username = ukwhatn。詳細はPJ CLAUDE.md参照。

## Claude in Chrome（browser 識別）

Chrome 拡張は複数 profile 同時接続をサポートするが、Connected browser の name を永続変更する UI/API は現時点で存在しない（2026-07 時点、Anthropic 側 feature request 未実装: [claude-code#14536](https://github.com/anthropics/claude-code/issues/14536) / [#14981](https://github.com/anthropics/claude-code/issues/14981) / [#25551](https://github.com/anthropics/claude-code/issues/25551)）。

**運用ルール**:
- `list_connected_browsers` の `name` field は connectedAt 順に「Browser 1/2/3」で**動的採番**。`switch_browser` の Connect 時に入力した name が反映されることがあるが、他 browser の再接続で reset されることがあるため信用しない
- **deviceId のみが stable な識別子**。マシンごとに固有 (Chrome プロファイルの user data から生成)
- **特定手順** (mapping を確定させたい場合): 該当 Chrome の Chrome を再起動 → `list_connected_browsers` で connectedAt が更新された deviceId がその browser
- 環境変数 (`CLAUDE_CHROME_BROWSER` 等) / `settings.json` での事前指定も未サポート
- 通常運用は `switch_browser` で対象 Chrome の Connect ボタンを user が click する
- `computer` ツール等が「Multiple Chrome browsers are connected」エラーになったら、`list_connected_browsers` → 下記 mapping 参照 → `select_browser({deviceId})` で選ぶか、`switch_browser` に切り替える

**このマシンの deviceId ↔ 実 Chrome mapping** (マシン固有、他環境では無効):

| deviceId | 実 Chrome |
|---|---|
| `c67ae761-66e9-4e41-92c6-f6e02463c000` | Studio |
| `d026b759-1948-4eaf-82b2-135ce7b71e3f` | DMM Mac |
| `d564083f-8b82-42e8-89e3-4645f0d79ca5` | <org> Mac |

## Cloudflare
詳細: @context/cloudflare-development.md

## パス表記の規約
本ファイルおよびcontext/skills内の `~/.claude/` 表記はユーザー設定ディレクトリを指す。`CLAUDE_CONFIG_DIR` を設定している環境ではそのディレクトリに読み替える（マシン固有の実パスは @CLAUDE.local.md 参照）。user-level 指示の実体は `AGENTS.md`、`CLAUDE.md` は互換 symlink（PJ-level は従来どおり `CLAUDE.md` 命名）。

## マシンローカル設定（git管理外）
このマシン固有の設定・運用メモ（gitignore対象。存在しない環境ではimportは無視される。Codex: 存在すれば `~/.claude/CLAUDE.local.md` を Read）:
@CLAUDE.local.md
