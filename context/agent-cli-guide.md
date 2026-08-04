# agent cli 使用ガイド

> **モデルslugについての注記**: 本ファイルに記載の外部CLIモデルslug（`gpt-5.6-sol` 等）は 2026-07 時点のもの。使用前に `--help` や `--list-models` 等で実在を再確認する。

## 目次

- [概要](#概要)
- [Agent（Claude subagent）使用後の codex 裏取り（CRITICAL）](#agentclaude-subagent使用後の-codex-裏取りcritical)
- [使用するCLIの選択（cursor優先 / codex fallback）](#使用するcliの選択cursor優先--codex-fallback)
- [基本コマンド](#基本コマンド)
- [CRITICAL: diff/ファイル内容の埋め込み禁止](#critical-diffファイル内容の埋め込み禁止)
- [レビュー用コマンド例](#レビュー用コマンド例)
- [出力形式（cursor: `agent`）](#出力形式cursor-agent)
- [レビューループの流れ](#レビューループの流れ)
- [Severity別のlead判断基準](#severity別のlead判断基準)
- [レビュー専任 agent に分ける場合（Claude Code）](#レビュー専任-agent-に分ける場合claude-code)
- [モデル選択ガイド](#モデル選択ガイド)
- [注意事項](#注意事項)

## 概要

外部CLI（既定は cursor の `agent` CLI、無い環境では codex CLI にfallback）のnon-interactive modeを使用して、別モデルによるレビューを実施する。
実行主体とは異なるベンダーのモデルによる分析で、計画・実装の品質を向上させる。

> **実行主体が Codex の場合**: 外部レビューCLIは cursor（`agent`）または claude を用い、codex 自身での再帰レビューは行わない（別ベンダー bias 独立性の確保が目的のため）。claude の non-interactive 例: 初回 `claude -p "<プロンプト>" --output-format json | jq -r '.session_id, .result'`、継続 `claude -p "<プロンプト>" --resume <session_id> --output-format json | jq -r '.result'`（プロンプト本文・Severity分類・ループ規定は本ガイド共通）。以下の cursor/codex の使い分けは「実行主体が Claude Code」の場合の既定。

外部CLIは lead が Bash で直接実行するのが既定。レビュー専任の agent に分ける場合は「レビュー専任 agent に分ける場合」参照。

**重要**: レビューはSeverity分類に基づく収束条件付きループで実施する（詳細は「レビューループの流れ」参照）。

## Agent（Claude subagent）使用後の codex 裏取り（CRITICAL）

Agent ツール（Claude subagent）を review 目的で使用したら、続けて **codex（または cursor）でも同じ対象を必ずレビューする**。credit 切れ・network 遮断で codex が実行不能な場合は、05_log.md に理由付きで skip を記録し、**codex 復旧後に裏取りを実施する**（当該 PR がマージされる前に間に合えばよく、その phase 内で完結させる必要はない。後回し可）。

理由:

- Claude 単独 review の主な弱点は同一モデル系列内の bias（見落としパターンが同型）
- 別ベンダー LLM の指摘は「使えるときに一度回せば十分」ではなく、review の各 phase で bias 独立性の担保が必要
- Agent review Phase 2 / Phase 4、実装レビュー、PR 前レビューのいずれでも適用する

「外部CLIが使えない場合の方針（§3）」に従い外部レビューを省略した場合も、**Claude 単独で review を完結させたとみなさない**。省略した旨は完了報告に明記し、codex/cursor 復旧後に上記手順で裏取りを実施する。

## 使用するCLIの選択（cursor優先 / codex fallback）

環境によって利用可能なCLIが異なる。**実行前に必ず以下の判定でCLIを選択すること。**

```bash
# cursor CLI の実体コマンドを捕捉（cursor-agent / agent のどちらでも動くように）。無ければ codex にfallback
CURSOR_CLI="$(command -v cursor-agent || command -v agent)"
if [ -n "$CURSOR_CLI" ]; then
  REVIEW_CLI=cursor   # 以後 "$CURSOR_CLI" -p ... で呼ぶ
elif command -v codex >/dev/null 2>&1; then
  REVIEW_CLI=codex
else
  echo "レビュー用CLI（cursor-agent / codex）が見つからない" >&2
fi
```

> 以降の例では cursor 側を `agent` と表記するが、これは `"$CURSOR_CLI"`（= `cursor-agent` または `agent`）の短縮表記。`cursor-agent` しか無い環境では `agent` を `cursor-agent` に読み替える（または上記 `$CURSOR_CLI` を使う）。

### 外部CLIが使えない場合の方針（両 CLI 使えない・credit 切れ・network 遮断時）

外部CLIが使えない環境（両方不在・credit切れ・network遮断）では、外部レビューを省略し、その旨を完了報告に明記する。**Claude 自身を reviewer role で spawn する自己検証で代替しない**（同一モデルによる自己検証は指示がなくても行われており、reviewer role での spawn は bias 独立性を持たないままコストを倍増させるだけのため）。

**発火条件（いずれか）:**
- `command -v cursor-agent && command -v codex` が両方失敗
- codex 実行時に `Your workspace is out of credits` エラー
- ネットワーク遮断・API 障害でどちらも実行不能

**省略時の手順**: 05_log.md に理由付きで skip を記録し、外部CLI復旧後に「Agent 使用後の codex 裏取り原則」に従って裏取りを実施する（PR マージ前に間に合えばよく、後回し可）。

**レビュー実施前は必ず Read:**
- `~/.claude/context/code-review-checklist.md`（汎用 anti-pattern チェックリスト）
- PJ 側の CLAUDE.md および context/（PJ 固有規約）
- 該当タスクの `05_log.md`（既知の判断・スコープアウト事項）

| CLI | 実体 | 既定モデル | セッション継続 | 結果取得 |
|-----|------|-----------|--------------|---------|
| cursor（優先） | `agent`（= `cursor-agent`） | `gpt-5.6-sol-medium` | `--resume <session_id>` | `--output-format json` → `jq -r '.result'` |
| codex（fallback） | `codex exec` | `gpt-5.6-sol` + `-c model_reasoning_effort="medium"` | `codex exec resume --last`（CWDの直近セッション） | `--json` → `jq` で `agent_message` を抽出、または `-o <file>` |

**CRITICAL: モデル/effortの指定体系は両CLIで異なる（混同禁止）**
- **cursor**: effort/speedをモデル名に含む合成slug（例: `gpt-5.6-sol-medium`。実在を `agent --list-models` で確認済 2026-07）。effort表記はモデル系列で揺れる（gpt-5.6-sol系・gpt-5.4以前・claude系は `medium`/`xhigh` 表記、gpt-5.5系のxhigh相当のみ `extra-high` 表記で `gpt-5.5-xhigh-fast` は存在しない＝実測）。利用可能なslugは `agent --list-models` で確認（`gpt-5.6-sol-medium` が無ければ一覧の最も近いgpt-5.6-sol系slugにfallback）
- **codex**: モデルslug（`gpt-5.6-sol`）とreasoning effort（`-c model_reasoning_effort="medium"`）を別指定。`gpt-5.6-sol-medium` のような合成名は**存在しない**。速度（Fast）はservice tier側の概念でslugに含めない

- **どちらもプロンプトにdiff/ファイル内容を埋め込まない**（後述「diff/ファイル内容の埋め込み禁止」）。CLIは自分でBash/Readを使って取得できる。
- codex は **既定で read-only sandbox かつ承認プロンプトなしで完走**するため、レビュー（git diff・ファイル読取のみ）にそのまま使える。

## 基本コマンド

以下がcursor/codex共通の呼び出しテンプレート（初回・2回目以降）。**計画レビュー・実装レビュー・PRレビュー・レビュー専任agentを含む全レビュー種別がこれを共用する**。各レビュー種別で変わるのは`<プロンプト>`の中身のみ（「レビュー用コマンド例」参照）。

### cursor（`agent` / `cursor-agent`）— 優先

```bash
# 初回（session_idを取得）
agent -p "<プロンプト>" --trust --model gpt-5.6-sol-medium --output-format json 2>/dev/null | jq -r '.session_id, .result'

# 2回目以降（セッション継続）
agent -p "<プロンプト>" --resume <session_id> --trust --model gpt-5.6-sol-medium --output-format json 2>/dev/null | jq -r '.result'
```

### codex（`codex exec`）— cursorが無い環境のfallback

```bash
# 初回（read-only sandboxで完走。最終メッセージのみ抽出）
codex exec --model gpt-5.6-sol -c model_reasoning_effort="medium" --json "<プロンプト>" 2>/dev/null \
  | jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'

# 2回目以降（CWDの直近セッションを継続。プロンプトは位置引数で渡す）
codex exec resume --last --json "<プロンプト>" 2>/dev/null \
  | jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'
```

- 最終メッセージはJSONLの `item.completed`（`item.type=="agent_message"`）の `.item.text` に入る。`thread.started` の `.thread_id` がセッションID（`resume --last` を使えばID追跡は不要）。
- `--json` の代わりに `-o <file>`（`--output-last-message`）で最終メッセージをファイルへ書き出すことも可能（stdoutにも出力される）。
- 特定セッションを継続する場合は `codex exec resume <SESSION_ID> "<プロンプト>"`。
- 認証は保存済みCLIログインを既定で再利用。CI等では `CODEX_API_KEY` を当該コマンド限定で付与する。

### 主要オプション（cursor: `agent`）

| オプション | 説明 |
|-----------|------|
| `-p, --print` | 非対話モード、結果を出力 |
| `--trust` | **必須**。ワークスペース信頼を自動承認（省略するとインタラクティブ確認が発生しnon-interactiveモードで失敗する） |
| `--model <model>` | 使用モデル（gpt-5.6-sol-medium推奨） |
| `--output-format json` | JSON形式で出力（session_id取得に必須） |
| `--resume <session_id>` | 特定のセッションを再開 |

**CRITICAL: cursorの `--output-format stream-json` は使用禁止。バッファリング問題でハングする可能性がある。必ず `json` を使用すること。**（codexは `--json`（JSONL）を使用する）

### 主要オプション（codex: `codex exec`）

| オプション | 説明 |
|-----------|------|
| `codex exec` | 非対話モード（alias `codex e`）。既定で read-only sandbox・承認なしで完走 |
| `--model, -m <model>` | 使用モデル（レビュー標準: `gpt-5.6-sol`。他に `gpt-5.5`, `gpt-5.4`, `gpt-5.4-mini`） |
| `-c model_reasoning_effort="medium"` | reasoning深度（low/medium/high/xhigh）。レビュー標準はmedium。既定値に依存せず必ず明示する |
| `--json` | JSONL（newline-delimited JSON）で出力 |
| `-o, --output-last-message <file>` | 最終メッセージをファイルへ書き出す（stdoutにも出力） |
| `resume --last` / `resume <SESSION_ID>` | セッション継続（プロンプトは位置引数） |
| `--sandbox <policy>` | `read-only`（既定）/ `workspace-write` / `danger-full-access`。レビューは既定のまま |

## CRITICAL: diff/ファイル内容の埋め込み禁止

**プロンプトに `$(git diff ...)` や `$(cat ...)` でdiff/ファイル内容を埋め込むことを禁止する（cursor/codex共通）。**

外部CLI（cursor/codex）はツール（Bash等）を持っているため、自分でdiffやファイル内容を取得できる。
プロンプトには「何を取得してレビューすべきか」の指示のみ記載する。

### 理由
- 大きなdiffでトークン上限やコマンドライン長超過が発生する
- バイナリファイルが含まれるとプロンプトが壊れる
- agentが自律的に必要な範囲を判断して読める

### NG例
```bash
# 禁止: diffをプロンプトに埋め込み
agent -p "以下のdiffをレビューしてください。$(git diff main)" ...

# 禁止: ファイル内容をプロンプトに埋め込み
agent -p "以下の計画をレビューしてください。$(cat plan.md)" ...
```

### OK例
```bash
# OK: agentに自分でdiffを取得させる
agent -p "git diff main を実行してコード変更をレビューしてください。" ...

# OK: agentに自分でファイルを読ませる
agent -p "/path/to/plan.md を読んで計画をレビューしてください。" ...
```

## レビュー用コマンド例

以降は各レビュー種別の**プロンプト本文のみ**を示す。CLIコマンドへの組み込み方（`--trust --model ... --output-format json` 等）は「基本コマンド」節の共通テンプレートを参照し、`<プロンプト>` の部分に以下の本文を差し込む。cursor/codexどちらを使うかは「使用するCLIの選択」の判定に従う（コマンド形の対応は「基本コマンド」参照）。

**レビュープロンプトには必ず「`~/.claude/context/code-review-checklist.md` を Read して各セクションをチェックせよ」を含める**（cursor/codex どちらも Bash / Read を持つので自ら参照可能）。checklist を明示させることで、抽象観点（「セキュリティを見て」）だけでは検出できない具体的 anti-pattern（BOLA、CSRF 登録漏れ、Drizzle encoder、falsy check 等）の見落としを減らす。

**レビュープロンプトには「既存経路との突き合わせ」を必ず含める**（diff だけを見るレビューの構造的な盲点を塞ぐ）:

```
差分が読み書きするもの（テーブル・レコード・セッションキー・URL空間・外部API）を列挙し、
それぞれについて既存の触っている箇所を grep で洗い出してください。
既存経路が持つガード（認可チェック・ロック・入力検証・履歴記録・冪等性・削除ガード）と
差分側のガードを突き合わせ、差分側に無いものを列挙してください。
```

外部CLIもサブエージェントも、指示しない限り diff の内側しか見ない。一方で人間のレビュアーは既存実装のガードを記憶しており、そことの差分で指摘してくる。**この差が、複数系統の agent review を回しても人間レビューで大量の指摘が出る主因**（実測: agent review 4系統を通した PR に、人間レビュアーが「既存の該当行を引用した」指摘を11件付けた。うち6件が「既存経路にあるガードが新経路に無い」型で、全て既存コードを grep すれば機械的に発見できるものだった。2026-08）。

**レビュープロンプトには費用対効果軸も必ず含める**（機構拡大ラチェットの抑制）: 「各指摘に、発生確率の根拠（ベースレート）・発生時の損失・対策の実装/保守コストを付記せよ。対策コストが期待損失を上回る指摘は出すな。既存機構で代替可能な新機構（新規テーブル・状態・インフラ・運用プロセス）の提案は Action Required にせず Recommended とせよ」。reviewerは指摘を出すことに最適化されており、「対策が見合わない」と言うインセンティブを持たないため、明示的に軸を与える。

**レビュープロンプトには実害シナリオの付記要求も必ず含める**: 「バグ・不整合・堅牢性の指摘には、実際に発生する具体的な入力・状態と、その結果の誤動作を付記せよ。付記できない指摘は Recommended 以下に分類せよ」。これは報告の絞り込みではなくメタデータ要求であり、「絞り込みを書かない」規定（「Severity別のlead判断基準」参照）と両立する。leadは実害シナリオの無い防御的指摘（checklist §16 の類型）を機械的にスキップ候補にできる。

### 1. 計画レビュー（Phase 2）

**初回プロンプト:**
```
このリポジトリの ${MEMORY_DIR}/memory/<task>/30_plan.md を読んで、計画をレビューしてください。
- 抜け漏れがないか
- リスクや懸念点
- より良いアプローチの提案

指摘は以下の形式で分類してください:
- **Action Required**: バグ・セキュリティ・データ損失リスク（マージ不可）
- **Recommended**: 改善推奨だが動作には直接影響しない
- **Minor**: スタイル・命名等の軽微な指摘

指摘がなければ「指摘なし」とだけ回答してください。
```
コマンド組み込みは「基本コマンド」の初回パターン（cursorは`--output-format json`からsession_id取得、codexは`--json`からthread_id取得）。

**2回目以降のプロンプト:**
```
以下の改善を行いました:
- [改善内容1]
- [改善内容2]

再度レビューしてください。同じSeverity分類形式で回答してください。指摘がなければ「指摘なし」とだけ回答してください。
```
コマンド組み込みは「基本コマンド」の2回目以降パターン（`--resume <session_id>` / `resume --last`でセッション継続）。

### 2. 実装レビュー（Phase 4）

**初回プロンプト:**
```
# BASE_BRANCHはPJ CLAUDE.mdで定義された値を使用
このリポジトリで git diff $BASE_BRANCH を実行して、コード変更をレビューしてください。
- バグや論理エラー
- セキュリティ上の問題
- パフォーマンス改善点
- ベストプラクティス違反

指摘は以下の形式で分類してください:
- **Action Required**: バグ・セキュリティ・データ損失リスク（マージ不可）
- **Recommended**: 改善推奨だが動作には直接影響しない
- **Minor**: スタイル・命名等の軽微な指摘

指摘がなければ「指摘なし」とだけ回答してください。
```
コマンド組み込みは「基本コマンド」の初回パターン。

**2回目以降のプロンプト:** 計画レビューと同一（「以下の改善を行いました」形式）。コマンド組み込みも「基本コマンド」の2回目以降パターンを使う。

### 3. PRレビュー

**プロンプト:**
```
gh pr diff <番号> を実行して、PRの変更内容をレビューしてください。
- 変更の妥当性
- テストの十分性
- ドキュメントの更新必要性

指摘がなければ「指摘なし」とだけ回答してください。
```
コマンド組み込みは「基本コマンド」の初回パターン。

## 出力形式（cursor: `agent`）

| 形式 | 説明 | 使用可否 |
|------|------|----------|
| `json` | 構造化JSON | **推奨** |
| `text` | プレーンテキスト | 使用可 |
| `stream-json` | ストリーミングJSON | **使用禁止** |

> codexは `--json`（JSONL）。最終メッセージは `item.completed`（`item.type=="agent_message"`）の `.item.text`、セッションIDは `thread.started` の `.thread_id`。

### JSON出力の構造

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 30000,
  "result": "レビュー結果テキスト",
  "session_id": "uuid-string",
  "request_id": "uuid-string"
}
```

## レビューループの流れ

1. **初回レビュー実行**
   - `agent -p`でレビュープロンプトを送信
   - `--output-format json`でsession_idを取得
   - 結果のSeverity分類を確認

2. **Severity別のlead判断**
   - leadがレビュー結果を受け取り、Severity別に修正/スキップを判断
   - 修正が必要な指摘は実装担当の agent に委譲（委譲しない構成なら lead が修正）
   - スキップした指摘と理由は05_log.mdに記録

3. **再レビュー（セッション継続）**
   - `--resume <session_id>`でセッション継続
   - 改善内容を伝えて再度レビューを依頼

4. **打ち切り条件（いずれかを満たした時点で終了）**
   - Action Requiredがゼロ
   - 同じ指摘が2ラウンド連続で出現（既知制限として05_log.mdに記録）
   - 安全上限: 5ラウンドで強制打ち切り（残存指摘はissueファイルに記録）
   - **設計文書（計画・方針・要件ドキュメント）のレビューは安全上限2〜3ラウンド**。ラウンドごとに新規指摘が湧き続けるのはLLMレビューの非収束特性（同一対象への反復実行で毎回異なる指摘が出る既知の挙動）であり、品質不足の証拠ではない。**成果物の機構数・文書量がラウンドごとに単調増加している場合は膨張シグナルとみなし、修正でなくユーザー確認で打ち切る**
   - **実装レビューでも膨張シグナルを監視する**: 修正ラウンドごとにdiffの行数・分岐・ガードが単調増加している場合、指摘対応を続けず減算パス（下記5）へ移るかユーザー確認で打ち切る

5. **減算パス（実装レビューの収束後に1回・必須）**
   - Action Requiredがゼロに収束したら（または打ち切り時）、加算方向とは独立の簡素化専用パスを1回実行する。バグ検知（加算）と簡素化（減算）を同一レビューに混ぜると加算が常に勝つため、減算を同格の独立パスとして置く
   - 実行手段: ビルトイン `/simplify` スキル、または外部CLIに次のプロンプト:
     「git diff $BASE_BRANCH を実行し、このdiffから削除・簡素化できるもののみを挙げてください。バグ探し・堅牢性向上の提案は不要です。特に: 型・上流・DB制約で保証済みの値への再ガード、利用実績のない抽象化、レビューループ中に追加された防御のうち重複しているもの」
   - leadが残存指摘（Recommended）と減算指摘を突き合わせて裁定する。減算適用後の再レビューは1回のみ（再加算ループの防止。そこで出た新規指摘はAction Requiredのみ対応する）

## Severity別のlead判断基準

| Severity | 判断 |
|----------|------|
| Action Required | 必ず修正（implementerに委譲） |
| Recommended | 必要性で判断（将来のバグ温床/保守性低下→修正、好みの問題/実害なし→スキップ） |
| Minor | 必要性で判断（一貫性/生産性に影響→修正、純粋なスタイル差→スキップ） |

**レビュープロンプトに「重大な問題のみ報告せよ」「保守的に判定せよ」等の絞り込みを書かない**（モデルが文字通り受け取り報告自体を減らす）。レビュアーには気付いた問題を全て報告させ、絞り込みはlead側で行う: Action Requiredとして採用するのはcorrectness / security / data integrity / 明示要件に影響するgapのみとし、それ以外はRecommended/Minorへ再分類する。

**AR定義の境界（機構拡大の抑制）**: 新機構の導入（新規テーブル・状態/enum・インフラ・運用プロセス）を伴う指摘は、テールリスクを「データ損失」と表現していてもARとして自動修正しない。Recommended扱いとし、採否はユーザー確認に回す（AGENTS.md「機構拡大のユーザー確認」）。**事実として正しい指摘と採用すべき指摘は別物** — 採否は費用対効果（発生確率×発生時の損失 vs 実装・保守コスト）で判断し、棄却理由は05_log.mdに記録する。

**レビュー指摘自体も検証対象とする**: Action Requiredを適用する前に、指摘の根拠を実挙動・一次情報で確認する（レビュアーは誤ることがあり、誤指摘をそのまま適用すると正常な設定・コードを壊すため）。反証できた指摘はスキップし、反証根拠とともに05_log.mdに記録する。

**指摘が具体的な機構を名指ししている場合、勝手に別機構へ置き換えない**: 指摘の「意図」だけを汲んで自分の判断で別の実装手段を選ぶと、**その手段は誰にも検証されていない状態で入る**（レビュアーは自分が書いていない機構を後続ラウンドで疑わず、指摘元の検証も効かない）。置き換えるなら、その機構が実機で動くことを自分で確認してから適用する（実例: 2026-07 <PJ>。レビューは`redirect: "manual"`を名指ししたが「リダイレクトを拒否する」という意図を汲んで`redirect: "error"`に置換→ Workersランタイム未実装で全fetchが即例外、以後4ラウンドのレビューでも検出されず本番障害）。

**同一Recommendedが複数ラウンド繰り返されるのはシグナル**: 打ち切り条件（同一指摘2R連続）は「ループを止める」判断であり、「指摘の中身を棄却してよい」という意味ではない。同じRecommendedを2ラウンド連続でスキップするなら、スキップ理由（多くは「既存precedentに合わせる」）を再検証するか、ユーザーに判断を仰ぐ（実例: 2026-07 <PJ> RSSで「watcher/resumeの状態遷移テストを追加せよ」が5ラウンド全てで出続けたが既存precedentを理由に毎回スキップ→ 実際に検出されたバグ・本番障害はすべてその未テストの結合層だった）。

スキップ理由は05_log.mdに記録すること。

**却下の蓄積を規約に還元する**: 同じ類型の指摘を同じ理由でスキップすることが2タスク以上で繰り返されたら、PJ CLAUDE.md「レビュー方針」の却下類型に追記する（/session-retro・/update-inst 経由）。05_log.md限りの記録はタスクとともに死蔵され、同種ノイズが毎回再生成される。規約側に還元するとレビュアーが生成前に読み、ノイズ自体が減る。

## レビュー専任 agent に分ける場合（Claude Code）

外部CLIは lead が直接実行するのが既定。レビューループが長く、指摘と修正の文脈を lead のコンテキストから分離したい場合のみ、reviewer を1体に分ける（`name` を付けて `SendMessage` で連携する構成）。

### spawn 指示テンプレート

```
あなたはこのセッションのreviewerです。

## 役割
外部CLI（cursorの`agent`、無ければcodex）をBash経由で実行し、レビュー結果をleadに報告する。

## 実行手順
0. CLI判定（`command -v cursor-agent || command -v agent` で無ければ `codex`）
1. `~/.claude/context/agent-cli-guide.md`の「基本コマンド」節のテンプレートで、Bashから外部CLIコマンドを実行（初回: session_id/thread_id取得）
2. 結果をleadにSendMessageで報告（Severity分類付き）
3. leadからの修正完了報告を受け、同節の「2回目以降」パターン（`--resume` / `resume --last`）でセッション継続して再レビュー
4. 打ち切り条件を満たすまでループ

## 打ち切り条件
- Action Required = 0
- 同一指摘が2ラウンド連続
- 安全上限: 5ラウンド
```

### 連携フロー

```
lead → reviewer（spawn + レビュー依頼）
  reviewer: agent CLI実行 → leadに指摘報告
  lead: Severity判断 → implementerに修正委譲
  implementer: 修正 → leadに完了報告
  lead → reviewer（再レビュー依頼）
  reviewer: --resume で再レビュー → leadに報告
  （打ち切り条件まで繰り返し）
```

### 長寿命パターン

reviewer を分けた場合、Phase 2（計画レビュー）からPhase 4（実装レビュー）まで存続させてよい。
agent CLIのセッションはPhaseごとに新規作成するが、reviewer 自体は跨いで再利用する。
これにより、コードベースへの理解を保持した状態でレビューの質を維持できる。

## モデル選択ガイド

| CLI | 指定 | 特徴 | 推奨用途 |
|-----|--------|------|----------|
| cursor | `--model gpt-5.6-sol-medium`（合成slug） | medium reasoning | コードレビュー標準 |
| codex | `--model gpt-5.6-sol -c model_reasoning_effort="medium"` | 同等 | コードレビュー標準（fallback時） |
| codex | `--model gpt-5.4` | 軽量・低コスト | 簡易チェック用の代替 |

```bash
# cursor: 利用可能な合成slug一覧を確認（medium variantが無ければ一覧の最も近いgpt-5.6-sol系slugにfallback）
agent --list-models
# codex: モデルとreasoningは別指定（合成slug不可）
codex exec --model gpt-5.6-sol -c model_reasoning_effort="medium" ...
```

## 注意事項

- cursor（`agent`）の `-p`モード（非対話モード）ではスキル（`/commit`等）は使用不可。他のオプション・制約は「主要オプション」「基本コマンド」節を参照

### CRITICAL: `codex exec` は stdin を読む（バックグラウンド実行でハングする）

**`codex exec` はプロンプトを位置引数で渡しても stdin を読もうとする**（起動時に `Reading additional input from stdin...` を出す）。バックグラウンド実行（Claude Code の `run_in_background: true` 等）では stdin が開いたままになるため、そこで待ち続けて**レビューが一度も走らないまま終了し、出力ファイルが空になる**。

`2>/dev/null` でstderrを捨てているとこの待機メッセージも見えないため、「実行したつもりで空振り」に気付けない。

**ルール: バックグラウンドで `codex exec` を実行するときは必ず `< /dev/null` で stdin を閉じる。**

```bash
codex exec --model gpt-5.6-sol -c model_reasoning_effort="medium" --json "<プロンプト>" \
  < /dev/null 2>/dev/null | jq -r 'select(.type=="item.completed" and .item.type=="agent_message") | .item.text'
```

`codex exec resume --last` も同様。

**空振りの見分け方**: 出力ファイルが空 かつ `ps aux | grep [c]odex` に自分が起動したプロセスが無い場合、ハング後に終了している。パイプを外して前景で軽いプロンプト（`"1+1 は？"` 等）を投げ、CLI 自体が生きているかを先に切り分ける（実例: 2026-07 <PJ>。レビューが空振りし、疎通確認で `Reading additional input from stdin...` を見て原因特定）。

### CRITICAL: パイプ実行時のエラーハンドリング

`agent ... | jq` / `codex exec ... | jq` のようにパイプで繋ぐと、CLI側のエラー（stderr）がjqのパースエラーに隠蔽される。

**ルール:**
1. **`2>/dev/null`でstderrを分離する**（基本コマンド例の通り）
2. **jqがパースエラーを返した場合、パイプを外してCLI単体で再実行し、エラーメッセージを確認する**
3. **同じコマンドをjqの書式変更やプロンプト簡素化でリトライすることを禁止する** — jqパースエラーの原因は十中八九CLI側のエラー出力であり、jq側の問題ではない
4. **出力が「空」の場合はパースエラーとは別物**。上の stdin ハングを疑う（jq を外しても何も出ないなら CLI 側が走っていない）
