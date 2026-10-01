---
name: setup-dependabot
description: dependabot 設定（.github/dependabot.yml）の新規作成・整備。リポジトリから ecosystem を自動検出し、lockfile コンフリクトを避ける group 設計と security fast-track を備えた設定を生成する。dependabot 設定の作成・見直し・追加の依頼時、/setup-dependabot 実行時に使用。境界: Renovate は対象外。dependabot が作った PR の対応は pr-review 等の通常フロー。
disable-model-invocation: true
---

# Setup Dependabot

リポジトリを走査してpackage ecosystemを検出し、コンフリクトしにくいdependabot.ymlを生成する。設計の基本方針は「**version-updatesはecosystemごとに1PRに集約、security-updatesは別グループで即時**」。

## ワークフロー

### Step 1: ecosystem検出

リポジトリ全体を走査し、該当するecosystemをすべて列挙する。

| 検出ファイル | package-ecosystem | 備考 |
|---|---|---|
| `bun.lock` / `bun.lockb` | `bun` | |
| `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | `npm` | pnpm/yarnも `npm` で扱う |
| `uv.lock` | `uv` | |
| `poetry.lock` / `requirements*.txt` / `Pipfile.lock` | `pip` | |
| `go.mod` | `gomod` | |
| `Cargo.toml` | `cargo` | |
| `Gemfile` | `bundler` | |
| `composer.json` | `composer` | |
| `Dockerfile*` | `docker` | |
| `docker-compose*.y*ml` | `docker-compose` | |
| `.github/workflows/*.y*ml` | `github-actions` | directoryは `"/"` 固定 |
| `*.tf` | `terraform` | |
| `pom.xml` / `build.gradle*` | `maven` / `gradle` | |
| `*.csproj` / `packages.config` | `nuget` | |

workspaces/モノレポ（bun/npm workspaces、uv workspace等）の場合は、パッケージごとにentryを分けず **1 entryの `directories`（複数形）にglobで列挙**する（例: `"/", "/apps/*", "/packages/*"`）。

**完了基準**: 検出したecosystemとdirectoryの対応表を提示し、検出漏れがないことをマニフェスト系ファイルの一覧（`git ls-files` ベース）で確認した。

### Step 2: 設定値の確定

1. **target-branch**: PJ CLAUDE.mdの `BASE_BRANCH` → なければdefault branch
2. **assignees**: 個人リポジトリならrepo owner。組織リポジトリで担当者が自明でない場合はAskUserQuestionで確認する
3. **schedule**: weeklyをデフォルトとする。変更希望が示されていない限り確認不要
4. **cooldown**: `default-days: 3` / `semver-patch-days: 1` をデフォルトとする（リリース直後の不具合の取り込み回避とpatchの速い取り込みの両立）

**完了基準**: 全entry分のtarget-branch / assignees / schedule / cooldownが確定し、ユーザー確認が必要な項目はAskUserQuestion済み。

### Step 3: 生成

各ecosystem entryに以下のテンプレートを適用する:

```yaml
version: 2
updates:
  - package-ecosystem: "<ecosystem>"
    directories:            # 単一なら directory: "<path>"
      - "/"
      - "/apps/*"
    schedule:
      interval: "weekly"
    target-branch: "<BASE_BRANCH>"
    open-pull-requests-limit: 10   # group集約後も上限に余裕を持たせる。副次ecosystemは5
    assignees:
      - "<assignee>"
    cooldown:
      default-days: 3
      semver-patch-days: 1
    groups:
      # 全 version-updates を 1PR に集約。特に共有 lockfile（workspaces）では
      # group を分けると同一 run の複数PRが同じ lockfile を触りコンフリクトする
      <ecosystem>-all:
        applies-to: version-updates
        patterns:
          - "*"
      # security-updates は即応が必要なので version-updates と別PRで fast-track
      <ecosystem>-security:
        applies-to: security-updates
        patterns:
          - "*"
    # メジャーバージョン更新を追従しない依存がある場合のみ:
    # ignore:
    #   - dependency-name: "<name>"
    #     update-types: ["version-update:semver-major"]
```

group名は `<ecosystem>-all` / `<ecosystem>-security` の形式でecosystemごとに一意にする。

**完了基準**: `.github/dependabot.yml` を書き出し、検出した全ecosystemがentryとして含まれている。

### Step 4: 検証

1. YAMLとしてparseが通ることを確認する（`python3 -c "import yaml,sys; yaml.safe_load(open('.github/dependabot.yml'))"` 等、環境にあるパーサで）
2. 各entryのdirectory/directoriesが実在するパスまたは実在にマッチするglobであることを確認する

**完了基準**: parse成功とdirectory実在確認の両方を実施し、結果を報告した。

コミットは `/commit` スキルで行う（作業ブランチ・worktree規約はグローバル規約に従う）。

## Gotchas

- **`target-branch` にdefault branch以外を指定すると、そのentryはversion-updatesのみに適用される**（security-updatesはdefault branch向けにデフォルト設定で作成される）。default以外を指定する必要が出た場合は公式docsで最新挙動を確認してから設定する
- **`reviewers` キーはdeprecated**。レビュアー指定はCODEOWNERSで行い、dependabot.ymlでは `assignees` を使う
- **共有lockfileのgroup分割はコンフリクトを起こす**: bun/npm workspacesでgroupをパッケージ別に分けると、同一weekly runの複数PRが同じlockfileを触ってコンフリクトし、大量のPRを手で解決する羽目になる。version-updatesは必ず1グループに集約する。react/react-dom等のランタイム揃えも同一PR内の同時bumpで自動的に達成される
- **`github-actions` のdirectoryは `"/"`**（`.github/workflows` を指定しない。`"/"` で自動検出される）
- `cooldown` は比較的新しいキー。エディタのschema警告が出ても有効（サポート状況が疑わしい場合は公式docsで確認する）

## 既存設定との関係

- コミット・PR作成はそれぞれ `/commit`・`/create-draft-pr` スキルに委譲する（本スキルはdependabot.ymlの生成と検証まで）
- 生成後の運用（dependabot PRのレビュー）はpr-reviewスキルの領分
