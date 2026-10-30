# `.claude` / `.codex` の管理構成

`~/.claude` リポジトリの管理範囲、Codexへの配布経路、新しいPCのセットアップと検証、CodexへのMCPの追加。

## 前提

`~/.claude` は **3台のPCで共有する設定リポジトリ**（`git@github.com:ukwhatn/.claude.git`）。Claude CodeとCodexの両方がここを唯一の実体として読む。

## リポジトリの管理範囲

`.gitignore` は **allowlist方式**（`*` で全除外してから `!` で個別に戻す）。新しいディレクトリを追加しても、allowlistに足さない限り追跡されない。

| 追跡する | 追跡しない |
|---|---|
| `AGENTS.md`（実体）/ `CLAUDE.md`（symlink）/ `settings.json` | `CLAUDE.local.md`（マシン固有の実値） |
| `context/` `skills/` `hooks/` `agents/` `templates/` `output-styles/` `bin/` `vendor/` `.github/` | `.local/`（メモリ・issue） |
| `statusline-command.sh` `subagent-statusline.py` `codex-usage.py` `README.md` `NOTICE.md` | `plugins/`（marketplaceキャッシュ） |

statusline系スクリプトはルート直下に置く（`bin/` を切らない）。`settings.json` が `statusLine` / `subagentStatusLine` から参照しており、settingsだけ同期されてスクリプトが無いと毎tickで実行失敗するため、allowlistへの追加が要る。

`settings.json` にマシン依存の値はほぼ無く、そのまま3台で共有できている（`extraKnownMarketplaces` / `enabledPlugins` もここに載るため、pluginの導入はsettings.jsonの同期だけで全台に伝播する）。

## Codexへの配布経路

Codexの走査パスは `~/.codex/skills/` + `~/.agents/skills/` + `<repo>/.agents/skills`。symlinkを辿る（公式明記）。

| 対象 | 配布方法 |
|---|---|
| グローバル指示 | `~/.codex/AGENTS.md` → `~/.claude/AGENTS.md`（symlink） |
| skills | `~/.agents/skills` → `~/.claude/skills`（**ディレクトリごと1本**） |
| PJ CLAUDE.md | `~/.codex/config.toml` の `project_doc_fallback_filenames = ["CLAUDE.md"]` で自動読込 |
| context7（公式仕様の確認） | `~/.codex/config.toml` の `[mcp_servers.context7]`（git管理外なのでマシンごとに設定が要る） |

`~/.codex/config.toml` は `~/.claude` リポジトリの外にあるため3PC同期の対象外。symlinkで済む2項目と違い、マシンごとに手で入れる（下記セットアップ手順に含めた）。

### `~/.codex/skills/` に個別symlinkを張らない

skillごとに `~/.codex/skills/<name>` → `~/.claude/skills/<name>` を張る方式はドリフトする。`.claude/skills` 側でスキルを削除・追加してもCodex側が追従しないため。

個別symlink方式を放置すると、削除済みskillへの壊れリンクと後から追加したskillの未リンクが混在し、一部のskillだけが使える状態になる。`~/.agents/skills` へのディレクトリsymlink 1本にすれば追従する。

`~/.codex/skills/.system` はCodex同梱スキル（`imagegen` / `openai-docs` / `plugin-creator` / `review-agent` / `skill-creator` / `skill-installer`）。触らない。ディレクトリ丸ごとsymlinkにできないのはこれが理由。

## 新PCのセットアップ

```bash
git clone git@github.com:ukwhatn/.claude.git ~/.claude
ln -sfn ~/.claude/AGENTS.md ~/.codex/AGENTS.md
mkdir -p ~/.agents && ln -sfn ~/.claude/skills ~/.agents/skills
```

`~/.codex/config.toml` に以下を追記する（top-levelキーは最初の `[table]` より前に置く。`http_headers` のkeyは `~/.claude.json` の `mcpServers.context7.headers` と同一値）:

```toml
project_doc_fallback_filenames = ["CLAUDE.md"]

[mcp_servers.context7]
url = "https://mcp.context7.com/mcp"
http_headers = { CONTEXT7_API_KEY = "ctx7sk-..." }
```

`CLAUDE.local.md`（マシン固有の実値: Chrome deviceIdマッピング、PATの置き場所等）はgit管理外なので手動で用意する。

ディスクの自動棚卸しを使うPCでは `bin/disk-inventory-setup.sh` でLaunchAgentを登録する。対象のリポジトリ・ビルド成果物の起点は `~/.config/disk-inventory/config.sh`（git管理外。無ければ雛形が置かれる）に書き、登録前に `bin/disk-inventory.sh`（dry-run）の報告で消える対象を確認する。

### セットアップの検証

symlinkの存在確認では注入されているかどうかが分からない（AGENTS.mdがbyte上限でtruncateされる可能性がある）。実機で確認する:

```bash
codex mcp list   # context7 が enabled で出るか
codex exec --sandbox read-only --skip-git-repo-check < /dev/null \
  'ツールを使わず即答。1) グローバル指示の最後のセクション見出しを原文で 2) skill `worktree-audit` は見えるか'
```

AGENTS.md末尾の見出し（`## マシンローカル設定`）が返れば全文注入、`worktree-audit`（`~/.codex/skills` に無いskill）が見えれば `~/.agents/skills` 経由が機能している。

`bin/herdr-delegate.sh` も3台へ配布されるが、herdr本体のバージョンが古いと依存コマンドが欠けている可能性がある。symlinkの存在確認と同じく、コマンドの実在は別途確認が要る。スクリプトが依存しているのは次のサブコマンド・オプション:

- `herdr tab create` の `--workspace` / `--cwd` / `--label` / `--no-focus`
- `herdr agent start` の `--kind` / `--pane` / `--timeout` と `--` 以降のargv渡し
- `herdr agent prompt` の `--wait` / `--until`（複数指定）/ `--timeout`
- `herdr pane read` / `herdr pane send-keys` / `herdr pane get` / `herdr tab close`

確認方法は、各コマンドグループを引数なしで実行してusageを出す形（`herdr tab` / `herdr agent` / `herdr pane`）。bareの `herdr` はTUIを起動するので実行しない。

`bin/taskboard-delegate.sh` は taskboard の CLI の `conversation start --parent-from-env` に依存する。入っていない版では自分で `taskboard_outdated` を返すので、PCごとの確認は要らない。

## slack-app-mcp のセットアップ（Mac・Slack.app ログイン済みのPCだけ）

`bin/slack-app-mcp.py` は Slack.app のディスク上のログイン情報（leveldb の xoxc トークン + keychain の d cookie）で、MCP・アプリ連携を繋げないワークスペースも Web API で読む user スコープの MCP。Slack.app にログイン済みの Mac でのみ動く。登録は `~/.claude.json`・keychain・LaunchAgent に載るのでマシンごとに手で行う（同期対象外）。

1. **MCP を user スコープで登録**（`~/.claude.json` の top-level に入る）:

```bash
claude mcp add --scope user slack-app-mcp -- ~/.claude/bin/slack-app-mcp.py server
```

2. **cookie ブローカーを gui ドメインに登録**。keychain の UI 保護項目は Aqua(gui) セッションでしか読めず、taskboard の agent host 経由の Claude Code は Background セッションで動く。Background から keychain を読むため、gui ドメインのワンショット LaunchAgent（ブローカー）を `launchctl kickstart` で起こして FIFO 経由で d cookie を受け取る:

```bash
cp ~/.claude/bin/slack-cookie-broker.plist ~/Library/LaunchAgents/uk.whatn.slack-cookie-broker.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/uk.whatn.slack-cookie-broker.plist
```

plist 内の絶対パスと `PATH`（shebang の `uv` を最小 PATH で解決するための候補列挙）はこの Mac のユーザー用。別ユーザーの PC ではパスを直す。

3. **keychain の初回許可**。初めて d cookie を読むとき keychain のダイアログが出る。GUI セッションで「常に許可」する（この許可は Aqua セッションでしか通らない）。

4. **疎通を検証**。GUI セッションで `~/.claude/bin/slack-app-mcp.py doctor` を実行し、全ワークスペースで auth.test が OK になるか確認する。Background セッション（taskboard の子など）では、同じ doctor がブローカー経由で d cookie を読めるかも確認する。

投稿は既定で無効（`~/.claude/local/slack-app-mcp.json` が無ければ全拒否＝読み取り専用）。投稿を許可するワークスペースは `{"post_allow": {"<domain>": "*"}}` をこのファイルに書く（同期対象外）。読み取り経路を優先し slack-browser(playwright) を fallback にする使い分けは `skills/slack-browser/SKILL.md`。

## discord-app-mcp のセットアップ（Mac・Discord.app を入れたPCだけ）

`bin/discord-app-mcp.py` は、普段使いとは別に起動した MCP 専用の Discord.app に CDP で入り、アプリ本体の関数で読み書きする user スコープの MCP。外から token で API を叩く形にしないのは、Discord ではそれが self-bot として規約で禁じられ、送り元もクライアントと変わるため。専用インスタンスは Discord.app の `--multi-instance` と `DISCORD_USER_DATA_DIR` で別データ・別ウィンドウとして動き、デバッグポートはこちらにだけ開く（普段使いを再起動しない・画面を動かさないため）。登録は `~/.claude.json`・LaunchAgent・専用データ置き場に載るのでマシンごとに手で行う（同期対象外）。

1. **MCP を user スコープで登録**: `claude mcp add --scope user discord-app -- ~/.claude/bin/discord-app-mcp.py server`
2. **専用インスタンスを起動してログインする**: `~/.claude/bin/discord-app-mcp.py launch`（`--dry-run` で実行内容だけ出す）。2つ目の Discord の窓が開くので一度だけログインし、その窓の通知を切る（普段使いと2重に届くため）
3. **ログイン時の起動を登録**: `bash ~/.claude/bin/discord-app-cdp-setup.sh`。ログイン時に1回だけ `launch --at-login` を走らせる（普段使いの起動を待ってから専用を起動する）。定期実行にしないのは、使用中の Discord を再起動させないため。専用が落ちたら `launch` を手で実行する
4. **疎通を検証**: `~/.claude/bin/discord-app-mcp.py doctor`

書き込み（送信・編集・削除）は既定で無効（`~/.claude/local/discord-app-mcp.json` の `write_allow` が空なら全拒否）。許可するチャンネルの id を `write_allow` に並べる（`"*"` で全許可。同期対象外）。

## CodexにMCPサーバーを足す

`~/.codex/config.toml` はマシンごとなので、Codexに使わせたいMCPはPCごとに足す。URL・OAuthのclient id・ポート番号の実値はここに書かない（PJの `CLAUDE.local.md` かメモリに置く）。

Claude Code のディレクトリ別 MCP 登録を Codex に写すときは `python3 ~/.claude/bin/sync-codex-mcp.py` を実行する。`~/.claude.json` の project ごとの登録と、workspace 内の `.mcp.json` / `.claude/settings.json` の登録を対応する `.codex/config.toml` へ生成する。生成ファイルはローカルの `git/info/exclude` に登録し、秘密値を含む場合も git に載せない。既存の手書き `.codex/config.toml` は上書きせず停止する。Codex は信頼済み project の設定だけを読むため、新しい project は `~/.codex/config.toml` の `[projects."<絶対パス>"]` で信頼設定を確認する。OAuth の認証は Claude Code と共有されないため、登録後に各 Codex 接続で確認する。

- **`codex mcp add <name> --url <url>` はOAuthを検出すると、その場でブラウザでのログインを始めて待つ。** 承認を別の端末で行うと、待ち受けが時間切れ（`timed out waiting for OAuth callback`）になる。追加だけ済ませ、ログインは次の手順でやり直す
- **ログインは `codex mcp login <name> --no-browser` で行う。** 承認URLを出し、承認後にブラウザが開こうとしたcallbackのURLを標準入力で受け取る。ハーネスのBashは対話入力できないので、FIFOを介して渡す。FIFOとログはscratchpadに置く（`/tmp` は並列のセッションと共有される）:

```bash
mkfifo "<scratchpad>/codex-login.fifo"
cat "<scratchpad>/codex-login.fifo" | codex mcp login <name> --no-browser > "<scratchpad>/codex-login.log" 2>&1 &
# ログに出た承認URLをユーザーに渡し、承認後のcallback URL（ブラウザのアドレス欄）を貼ってもらう
printf '%s\n' '<貼られたcallback URL>' > "<scratchpad>/codex-login.fifo"
```

- **OAuthの提供元がredirect URIの事前登録を求めるときは、トップレベルの `mcp_oauth_callback_port` / `mcp_oauth_callback_url` でcallbackのポートを固定する**（`[mcp_servers.*]` より前に置く）。同じポートを使うログインは1つずつ行う
- **ログインできたかは `codex mcp list` のAuth欄で判断しない。** 表示とツール呼び出しの結果が食い違うことがある。`codex exec --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check < /dev/null '<サーバー名> のツールを1回呼んで結果を答える'` で実際に呼んで確かめる（read-only sandboxではMCPツールを呼べないので、確認にも使えない）

## 同期の運用

- commit・pushのタイミングと直コミットの可否はAGENTS.md「コミット・ブランチ・PR」
- pushがrejectされたら `git pull --rebase --autostash && git push`（3台運用では実際に起きる）

## plugin化しない判断（複数回検討、いずれも見送り）

- pluginは `CLAUDE.md` / `settings.json` を配布できない。同期の主な対象は `AGENTS.md` と `context/` なので、plugin化すると経路が「plugin自動更新」と「git」の2本に分かれた上で、最も頻繁に編集するファイルはgit側に残る
- plugin skillは名前空間付き（`/commit` → `/ns:commit`）。指示ファイル内のskill名参照は多数あり、全書き換えが要る
- marketplace方式は実体が `plugins/cache/<mp>/<plugin>/<version>/` に入るため、更新のたびにsymlink先が変わる
- 結論: 個人運用ではsymlinkが優位。他人に配布する必要が出たら再検討する
- 外部由来で自分が編集しないskill（Cloudflare系等）は公式marketplaceのpluginで導入する、という区分は有効

## 実機検証で確定している事実（推測しない）

- **`codex exec` にはグローバル指示がフル注入される**（Codex自身にコンテキストを列挙させて確認できる）。このためCodexをレビュアーとして呼ぶとlead用の外部レビュー規約を読んで別CLIへ再委託する。役割分岐を `AGENTS.md` と `context/agent-cli-guide.md` に規定して解消済み
- **`~/.agents/skills` 経由でskillが読める**（`~/.codex/skills` に存在しないskillがCodexから見えることで確認できる）
- **AGENTS.mdにはbyte上限がある。** `project_doc_max_bytes` というキーが実在し、超過分は「project doc exceeds remaining budget; truncating」で警告なく切られる（公式docsはdefault値を書いていない）。26KBでは全文が注入されたが、48KBでは末尾が切られることを実測で確認している（`codex 0.145.0`。検証コマンドが返す「最後のセクション見出し」がAGENTS.mdの実際の末尾より手前になる）。切られた分をCodexは読まないまま動作するので、AGENTS.mdを伸ばしたら上記「セットアップの検証」で末尾セクションが返るかを確認する。切れていたら、`~/.codex/config.toml` に `project_doc_max_bytes` を明示して上限を上げるか、内容を `context/` へ移してAGENTS.mdを縮める
- **配布経路が未設定でもCodexは正常に起動する**（`~/.codex/AGENTS.md` 不在・`~/.agents/` 不在・`config.toml` にfallbackなし、のいずれでもエラーにならない）ため、1台だけ設定が抜けていても気付けない。セットアップ手順を変えたら全PCで上記の検証コマンドを流す
- `--ignore-rules` はexecpolicy `.rules` 用で、AGENTS.mdの読込抑制ではない
- Codexにもplugin marketplace機構はあるがClaude Codeとは別形式（`~/.codex/config.toml` の `[marketplaces.*]`）
