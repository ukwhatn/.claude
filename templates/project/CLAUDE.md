# <プロジェクト名>

## 変数
MEMORY_DIR=.local/
BASE_BRANCH=develop

## 品質チェック
```bash
# TODO: PJに合わせて設定
npm run lint
npm run format
npm run typecheck
npm test
```

## 検証方針

AIエージェントには検証機構の供給が最も効果が高い。PJで以下を整備:

- **テストコード**: 主要ロジックのユニット/統合テスト（コマンド: `<test command>`）
- **E2Eテスト**: <PJに応じてPlaywright/Cypress等。コマンド: `<e2e command>`>
- **スクリーンショット**: UI変更時は `docs/screenshots/` に変更前後を保存
- **期待出力**: 主要コマンド/APIの fixture を `tests/fixtures/` 等に配置
- **Stop Hook**: 必要に応じて `.claude/settings.json` の `Stop` でテスト自動実行

## PJ固有ルール
- [PJ固有のルールをここに記載]

<!--
注意: PJ独自のサブエージェント呼び出し慣習（quality-checker / pr-reviewer 等を明示的に呼ぶ等）は記述しない。
サブエージェント / Agent Teams の発動はuser-level設定（~/.claude/context/tool-claude-code.md「Agent Teams 発動条件」）に従う。
-->
