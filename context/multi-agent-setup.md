# `.claude` / `.codex` の管理構成

Read when: `~/.claude` の構成を変更するとき、新しいPCをセットアップするとき、Codex への配布経路を触るとき。通常の作業では読まなくてよい。

## 前提

`~/.claude` は **3台のPCで共有する設定リポジトリ**（`git@github.com:ukwhatn/.claude.git`）。Claude Code と Codex の両方がここを唯一の実体として読む。

## リポジトリの管理範囲

`.gitignore` は **allowlist 方式**（`*` で全除外してから `!` で個別に戻す）。新しいディレクトリを追加しても、allowlist に足さない限り追跡されない。

| 追跡する | 追跡しない |
|---|---|
| `AGENTS.md`（実体）/ `CLAUDE.md`（symlink）/ `settings.json` | `CLAUDE.local.md`（マシン固有の実値） |
| `context/` `skills/` `hooks/` `agents/` `templates/` `output-styles/` | `.local/`（メモリ・issue） |
| `statusline-command.sh` `README.md` `NOTICE.md` | `plugins/`（marketplace キャッシュ） |

`settings.json` にマシン依存の値はほぼ無く、そのまま3台で共有できている（`extraKnownMarketplaces` / `enabledPlugins` もここに載るため、plugin の導入は settings.json の同期だけで全台に伝播する）。

## Codex への配布経路

Codex の走査パスは `~/.codex/skills/` + `~/.agents/skills/` + `<repo>/.agents/skills`。**symlink を辿る**（公式明記）。

| 対象 | 配布方法 |
|---|---|
| グローバル指示 | `~/.codex/AGENTS.md` → `~/.claude/AGENTS.md`（symlink） |
| skills | `~/.agents/skills` → `~/.claude/skills`（**ディレクトリごと1本**） |
| PJ CLAUDE.md | `~/.codex/config.toml` の `project_doc_fallback_filenames = ["CLAUDE.md"]` で自動読込 |

### CRITICAL: `~/.codex/skills/` に個別 symlink を張らない

skill ごとに `~/.codex/skills/<name>` → `~/.claude/skills/<name>` を張る方式は**ドリフトする**。`.claude/skills` 側でスキルを削除・追加しても Codex 側が追従しないため。

2026-08 の実測では、36本中 **12本が壊れリンク**（`.claude/skills` から削除済みの Cloudflare 系等）、**6本が未リンク**（後から追加した skill）という半壊状態だった。`~/.agents/skills` へのディレクトリ symlink 1本に置き換えて解消済み。

`~/.codex/skills/.system` は Codex 同梱スキル（`imagegen` / `openai-docs` / `plugin-creator` / `review-agent` / `skill-creator` / `skill-installer`）。**触らない**。ディレクトリ丸ごと symlink にできないのはこれが理由。

## 新PCのセットアップ

```bash
git clone git@github.com:ukwhatn/.claude.git ~/.claude
ln -sfn ~/.claude/AGENTS.md ~/.codex/AGENTS.md
mkdir -p ~/.agents && ln -sfn ~/.claude/skills ~/.agents/skills
```

`CLAUDE.local.md`（マシン固有の実値: Chrome deviceId マッピング、PAT の置き場所等）は git 管理外なので手動で用意する。

## 同期の運用

- **user-level 設定を変更したら、変更したスキル自身が `/commit --push` でコミット・push まで行う**（AGENTS.md「コミット・ブランチ・PR」）。手元に残さない
- push が reject されたら `git pull --rebase --autostash && git push`（3台運用では実際に起きる）
- `~/.claude` は直コミット可（実装開始前ゲートの判定結果を AGENTS.md に永続化済み）

## plugin 化しない判断（2026-07 / 2026-08 の2回検討、いずれも見送り）

- plugin は **`CLAUDE.md` / `settings.json` を配布できない**。同期の主戦場は `AGENTS.md` と `context/` なので、plugin 化すると経路が「plugin 自動更新」と「git」の2本に割れた上で、最も頻繁に編集するファイルは git 側に残る
- plugin skill は**名前空間付き**（`/commit` → `/ns:commit`）。指示ファイル内の skill 名参照は **116箇所**あり、全書き換えが必要
- marketplace 方式は実体が `plugins/cache/<mp>/<plugin>/<version>/` に入るため、**更新のたびに symlink 先が変わる**
- 結論: 個人運用では symlink が優位。**他人に配布する必要が出たら再検討する**
- 外部由来で自分が編集しない skill（Cloudflare 系等）は公式 marketplace の plugin に寄せる、という線引きは有効

## 実機検証で確定している事実（推測しない）

- **`codex exec` にはグローバル指示がフル注入される**（2026-08 実測。Codex 自身に列挙させ「作業フロー（Phase 0-5）」「外部レビュー」「緩和しない安全項目」を確認）。このため、Codex をレビュアーとして呼ぶと lead 用の外部レビュー規約を読んで**別 CLI へ再委託する事象が発生した**。役割分岐を `AGENTS.md` と `context/agent-cli-guide.md` に追加して解消済み
- **`~/.agents/skills` 経由で skill が読める**（2026-08 実測。`~/.codex/skills` に存在しない `worktree-audit` / `session-analytics` が Codex から見えることで確認）
- `--ignore-rules` は execpolicy `.rules` 用で、AGENTS.md の読込抑制ではない
- Codex にも plugin marketplace 機構はあるが Claude Code とは**別形式**（`~/.codex/config.toml` の `[marketplaces.*]`）
