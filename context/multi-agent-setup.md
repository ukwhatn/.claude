# `.claude` / `.codex` の管理構成

Read when: `~/.claude` の構成を変更するとき、新しいPCをセットアップするとき、Codexへの配布経路を触るとき。通常の作業では読まなくてよい。

## 前提

`~/.claude` は **3台のPCで共有する設定リポジトリ**（`git@github.com:ukwhatn/.claude.git`）。Claude CodeとCodexの両方がここを唯一の実体として読む。

## リポジトリの管理範囲

`.gitignore` は **allowlist方式**（`*` で全除外してから `!` で個別に戻す）。新しいディレクトリを追加しても、allowlistに足さない限り追跡されない。

| 追跡する | 追跡しない |
|---|---|
| `AGENTS.md`（実体）/ `CLAUDE.md`（symlink）/ `settings.json` | `CLAUDE.local.md`（マシン固有の実値） |
| `context/` `skills/` `hooks/` `agents/` `templates/` `output-styles/` `bin/` | `.local/`（メモリ・issue） |
| `statusline-command.sh` `subagent-statusline.py` `codex-usage.py` `README.md` `NOTICE.md` | `plugins/`（marketplaceキャッシュ） |

statusline系スクリプトは**ルート直下**に置く（`bin/` を切らない）。`settings.json` が `statusLine` / `subagentStatusLine` から参照しており、settingsだけ同期されてスクリプトが無いと毎tickで実行失敗するため、allowlistへの追加は必須。

`settings.json` にマシン依存の値はほぼ無く、そのまま3台で共有できている（`extraKnownMarketplaces` / `enabledPlugins` もここに載るため、pluginの導入はsettings.jsonの同期だけで全台に伝播する）。

## Codexへの配布経路

Codexの走査パスは `~/.codex/skills/` + `~/.agents/skills/` + `<repo>/.agents/skills`。**symlinkを辿る**（公式明記）。

| 対象 | 配布方法 |
|---|---|
| グローバル指示 | `~/.codex/AGENTS.md` → `~/.claude/AGENTS.md`（symlink） |
| skills | `~/.agents/skills` → `~/.claude/skills`（**ディレクトリごと1本**） |
| PJ CLAUDE.md | `~/.codex/config.toml` の `project_doc_fallback_filenames = ["CLAUDE.md"]` で自動読込 |
| context7（公式仕様の確認） | `~/.codex/config.toml` の `[mcp_servers.context7]`（**git管理外なのでマシンごとに設定が必要**） |

`~/.codex/config.toml` は `~/.claude` リポジトリの外にあるため **3PC同期の対象外**。symlinkで済む2項目と違い、マシンごとに手で入れる必要がある（下記セットアップ手順に含めた）。

### CRITICAL: `~/.codex/skills/` に個別symlinkを張らない

skillごとに `~/.codex/skills/<name>` → `~/.claude/skills/<name>` を張る方式は**ドリフトする**。`.claude/skills` 側でスキルを削除・追加してもCodex側が追従しないため。

個別symlink方式を放置すると、**削除済みskillへの壊れリンク**と**後から追加したskillの未リンク**が混在し、一部のskillだけが使える状態になる。`~/.agents/skills` へのディレクトリsymlink 1本にすれば追従する。

`~/.codex/skills/.system` はCodex同梱スキル（`imagegen` / `openai-docs` / `plugin-creator` / `review-agent` / `skill-creator` / `skill-installer`）。**触らない**。ディレクトリ丸ごとsymlinkにできないのはこれが理由。

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

### セットアップの検証

symlinkの存在確認では**注入されているかどうかが分からない**（AGENTS.mdがbyte上限でtruncateされる可能性がある）。実機で確認する:

```bash
codex mcp list   # context7 が enabled で出るか
codex exec --sandbox read-only --skip-git-repo-check < /dev/null \
  'ツールを使わず即答。1) グローバル指示の最後のセクション見出しを原文で 2) skill `worktree-audit` は見えるか'
```

`## マシンローカル設定（git管理外）`（AGENTS.md末尾）が返れば全文注入、`worktree-audit`（`~/.codex/skills` に無いskill）が見えれば `~/.agents/skills` 経由が機能している。

`bin/herdr-delegate.sh` も3台へ配布されるが、**herdr本体のバージョンが古いと依存コマンドが欠けている可能性がある**。symlinkの存在確認と同じく、コマンドの実在は別途確認が要る。スクリプトが依存しているのは次のサブコマンド・オプション:

- `herdr tab create` の `--workspace` / `--cwd` / `--label` / `--no-focus`
- `herdr agent start` の `--kind` / `--pane` / `--timeout` と `--` 以降のargv渡し
- `herdr agent prompt` の `--wait` / `--until`（複数指定）/ `--timeout`
- `herdr pane read` / `herdr pane send-keys` / `herdr pane get` / `herdr tab close`

確認方法は、各コマンドグループを引数なしで実行してusageを出す形（`herdr tab` / `herdr agent` / `herdr pane`）。**bareの `herdr` はTUIを起動するので実行しない**。

## 同期の運用

- **user-level設定を変更したら、変更したスキル自身が `/commit --push` でコミット・pushまで行う**（AGENTS.md「コミット・ブランチ・PR」）。手元に残さない
- pushがrejectされたら `git pull --rebase --autostash && git push`（3台運用では実際に起きる）
- `~/.claude` は直コミット可（実装開始前ゲートの判定結果をAGENTS.mdに永続化済み）

## plugin化しない判断（複数回検討、いずれも見送り）

- pluginは **`CLAUDE.md` / `settings.json` を配布できない**。同期の主な対象は `AGENTS.md` と `context/` なので、plugin化すると経路が「plugin自動更新」と「git」の2本に分かれた上で、最も頻繁に編集するファイルはgit側に残る
- plugin skillは**名前空間付き**（`/commit` → `/ns:commit`）。指示ファイル内のskill名参照は **116箇所**あり、全書き換えが必要
- marketplace方式は実体が `plugins/cache/<mp>/<plugin>/<version>/` に入るため、**更新のたびにsymlink先が変わる**
- 結論: 個人運用ではsymlinkが優位。**他人に配布する必要が出たら再検討する**
- 外部由来で自分が編集しないskill（Cloudflare系等）は公式marketplaceのpluginで導入する、という区分は有効

## 実機検証で確定している事実（推測しない）

- **`codex exec` にはグローバル指示がフル注入される**（Codex自身にコンテキストを列挙させて確認できる）。このためCodexをレビュアーとして呼ぶとlead用の外部レビュー規約を読んで**別CLIへ再委託する**。役割分岐を `AGENTS.md` と `context/agent-cli-guide.md` に規定して解消済み
- **`~/.agents/skills` 経由でskillが読める**（`~/.codex/skills` に存在しないskillがCodexから見えることで確認できる）
- **AGENTS.mdにはbyte上限がある。** `project_doc_max_bytes` というキーが実在し、超過分は「project doc exceeds remaining budget; truncating」で**警告なく切られる**（公式docsはdefault値を書いていない）。26KBでは全文が注入されたが、**48KBでは末尾が切られることを実測で確認している**（`codex 0.145.0`。検証コマンドが返す「最後のセクション見出し」がAGENTS.mdの実際の末尾より手前になる）。切られた分をCodexは読まないまま動作するので、**AGENTS.mdを伸ばしたら必ず上記「セットアップの検証」で末尾セクションが返るかを確認する**。切れていたら、`~/.codex/config.toml` に `project_doc_max_bytes` を明示して上限を上げるか、内容を `context/` へ移してAGENTS.mdを縮める
- **配布経路が未設定でもCodexは正常に起動する**（`~/.codex/AGENTS.md` 不在・`~/.agents/` 不在・`config.toml` にfallbackなし、のいずれでもエラーにならない）ため、1台だけ設定が抜けていても気付けない。**セットアップ手順を変えたら全PCで上記の検証コマンドを流す**
- `--ignore-rules` はexecpolicy `.rules` 用で、AGENTS.mdの読込抑制ではない
- Codexにもplugin marketplace機構はあるがClaude Codeとは**別形式**（`~/.codex/config.toml` の `[marketplaces.*]`）
