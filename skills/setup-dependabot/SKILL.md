---
name: setup-dependabot
description: dependabot設定（.github/dependabot.yml）の新規作成・整備。リポジトリのlockfile・workflows等からecosystemを自動検出し、lockfileコンフリクトを回避するgroup設計とsecurity fast-trackを備えた設定を生成する。使用タイミング: (1) dependabot設定の作成・見直し・追加の依頼時、(2) /setup-dependabot 実行時。境界: Renovate設定は対象外。dependabotが作成したPRのレビュー・マージ対応は pr-review 等の通常フローで行う。
---

# Setup Dependabot

リポジトリを走査して package ecosystem を検出し、コンフリクトしにくい dependabot.yml を生成する。設計の核は「**version-updates は ecosystem ごとに1PRに集約、security-updates は別グループで即時**」。

## ワークフロー

### Step 1: ecosystem 検出

リポジトリ全体を走査し、該当する ecosystem をすべて列挙する。

| 検出ファイル | package-ecosystem | 備考 |
|---|---|---|
| `bun.lock` / `bun.lockb` | `bun` | |
| `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` | `npm` | pnpm/yarn も `npm` で扱う |
| `uv.lock` | `uv` | |
| `poetry.lock` / `requirements*.txt` / `Pipfile.lock` | `pip` | |
| `go.mod` | `gomod` | |
| `Cargo.toml` | `cargo` | |
| `Gemfile` | `bundler` | |
| `composer.json` | `composer` | |
| `Dockerfile*` | `docker` | |
| `docker-compose*.y*ml` | `docker-compose` | |
| `.github/workflows/*.y*ml` | `github-actions` | directory は `"/"` 固定 |
| `*.tf` | `terraform` | |
| `pom.xml` / `build.gradle*` | `maven` / `gradle` | |
| `*.csproj` / `packages.config` | `nuget` | |

workspaces/モノレポ（bun/npm workspaces、uv workspace 等）の場合は、パッケージごとに entry を分けず **1 entry の `directories`（複数形）に glob で列挙**する（例: `"/", "/apps/*", "/packages/*"`）。

**完了基準**: 検出した ecosystem と directory の対応表を提示し、検出漏れがないことをマニフェスト系ファイルの一覧（`git ls-files` ベース）で確認した。

### Step 2: 設定値の確定

1. **target-branch**: PJ CLAUDE.md の `BASE_BRANCH` → なければ default branch
2. **assignees**: 個人リポジトリなら repo owner。組織リポジトリで担当者が自明でない場合は AskUserQuestion で確認する
3. **schedule**: weekly をデフォルトとする。変更希望が示されていない限り確認不要
4. **cooldown**: `default-days: 3` / `semver-patch-days: 1` をデフォルトとする（リリース直後の不具合踏み抜き回避と patch の速い取り込みの両立）

**完了基準**: 全 entry 分の target-branch / assignees / schedule / cooldown が確定し、ユーザー確認が必要な項目は AskUserQuestion 済み。

### Step 3: 生成

各 ecosystem entry に以下のテンプレートを適用する:

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

group 名は `<ecosystem>-all` / `<ecosystem>-security` の形式で ecosystem ごとに一意にする。

**完了基準**: `.github/dependabot.yml` を書き出し、検出した全 ecosystem が entry として含まれている。

### Step 4: 検証

1. YAML として parse が通ることを確認する（`python3 -c "import yaml,sys; yaml.safe_load(open('.github/dependabot.yml'))"` 等、環境にあるパーサで）
2. 各 entry の directory/directories が実在するパスまたは実在にマッチする glob であることを確認する

**完了基準**: parse 成功と directory 実在確認の両方を実施し、結果を報告した。

コミットは `/commit` スキルで行う（作業ブランチ・worktree 規約はグローバル規約に従う）。

## Gotchas

- **`target-branch` に default branch 以外を指定すると、その entry は version-updates のみに適用される**（security-updates は default branch 向けにデフォルト設定で作成される）。default 以外を指定する必要が出た場合は公式 docs で最新挙動を確認してから設定する
- **`reviewers` キーは deprecated**。レビュアー指定は CODEOWNERS で行い、dependabot.yml では `assignees` を使う
- **共有 lockfile の group 分割は事故る**: bun/npm workspaces で group をパッケージ別に分けると、同一 weekly run の複数PRが同じ lockfile を触ってコンフリクトする（20+PR を手動一括解決した実例あり）。version-updates は必ず1グループに集約する。react/react-dom 等のランタイム揃えも同一PR内の同時 bump で自動的に達成される
- **`github-actions` の directory は `"/"`**（`.github/workflows` を指定しない。`"/"` で自動検出される）
- `cooldown` は比較的新しいキー。エディタの schema 警告が出ても有効（サポート状況が疑わしい場合は公式 docs で確認する）

## 既存設定との関係

- コミット・PR 作成はそれぞれ `/commit`・`/create-draft-pr` スキルに委譲する（本スキルは dependabot.yml の生成と検証まで）
- 生成後の運用（dependabot PR のレビュー）は pr-review スキルの領分
