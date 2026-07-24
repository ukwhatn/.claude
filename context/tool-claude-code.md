# Claude Code 固有指示

AGENTS.md から @import され、Claude Code では毎セッション常駐する。Codex 等の他エージェントはこのファイルを読む必要はない（対応表は context/tool-codex.md 参照）。

## Opus 4.7 ベストプラクティス（自律実行）

Opus 4.7 は自己完結型の実行を前提に設計されている。以下を徹底すること:
- 初回プロンプトに Goal / Constraints / Acceptance criteria を整理して渡されたら、途中介入を最小化して自律的に進める
- ペアプログラミング型の細かい指示・「こまめに」「逐一」等の過度な強制は避ける
- 検証機構（テスト・スクリーンショット・期待出力）の供給は最も効果が高い。PJ側で整備すること（@context/workflow-rules.md「検証機構」参照）
- Agent Teamsは限定発動（後述「委譲判断」参照）。単発Subagentへの実装委譲は「小規模タスク」を除きデフォルト（同上）

## 委譲判断（Agent Teams / 単発Subagent / lead直接実装の使い分け、2026-07更新）

leadは常にオーケストレーション（計画・タスク分解・レビュー）を担う。以下の優先順位で機械的に判定する。

| 判定 | 条件 | 選択 |
|---|---|---|
| 1 | 5+ファイルの並列変更 or 独立タスク3つ以上 or ユーザーが「チームで」等と明示 | **Agent Teams** |
| 2 | 上記に該当しないが「小規模タスク」（@context/workflow-rules.mdのPhase0-5 skip基準と同一: 1ファイルの軽微な修正・既知の単純なバグ修正・文書のtypo修正等）を超える非自明な実装 | **単発Subagent**（Agent tool、`model: sonnet`を既定とする。2026-07時点の既定値であり、モデル世代交代時は見直す） |
| 3 | 「小規模タスク」 | lead直接実装 |

**判定1（Agent Teams）**: 真に並列で進められる独立作業がある時のみ。チーム編成・TaskCreate/TaskUpdateでの依存関係管理のオーバーヘッドがペイする規模でのみ使う。

**判定2（単発Subagent、実装委譲のデフォルト化）**: 並列性のためではなく、lead（会話・計画・レビューに強い/軽量なモデル。セッションごとにユーザーが選択）と実装（実装力の高いモデルに固定）のモデル階層分離が目的。leadは直接Edit/Writeせず、Agent toolで1体のimpl subagentに実装を委譲し、結果をレビューする（Writer/Reviewer分離、@context/claude-customization-guide.md §8）。長時間タスクでcontext compactionが懸念される場合も、判定1に該当しない限りはこの単発Subagent委譲で対応する（Agent Teams化しない）。

**単発Subagentは実装以外にも使う**: 大量のファイル読み・コードベース調査・ログ解析も同様にコンテキスト保護のため単発subagent（Explore等）へ委譲し、本体には結論のみ持ち帰る（実測: subagent委譲セッションはトークン消費約半分・compaction 1/6）。

## Claude Code 固有の Read when

- Agent Teams発動時（spawn前）: `context/agent-teams-guide.md`
- TaskCreate/TaskUpdate使用時（複雑タスクの初回）: `context/task-tool-guide.md`
- CLAUDE.md（AGENTS.md）・skills・hooks の設計・監査時: `context/claude-customization-guide.md`

## Claude Code 固有ツールの注意

- **Workflow ツール**: スクリプトは plain JavaScript のみ（TypeScript構文はパースエラーで空回り）
- **EnterWorktree / ExitWorktree**: 手順詳細は `context/worktree-guide.md`（sanitize・改名フロー・削除時のコミット保全）
- **Compact Instructions**: AGENTS.md 末尾のセクションを compaction 時に参照する
