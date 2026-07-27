# Claude Code 固有指示

AGENTS.md から @import され、Claude Code では毎セッション常駐する。Codex 等の他エージェントはこのファイルを読む必要はない（対応表は context/tool-codex.md 参照）。

## 自律実行の前提

- 初回プロンプトに Goal / Constraints / Acceptance criteria を整理して渡されたら、途中介入を最小化して自律的に進める
- ペアプログラミング型の細かい指示・「こまめに」「逐一」等の過度な強制は避ける
- 検証機構（テスト・スクリーンショット・期待出力）の供給は最も効果が高い。PJ側で整備すること（@context/workflow-rules.md「検証機構」参照）
- **自己検証を促す指示は書かない**（「最終検証ステップを含める」「応答前に再検証する」「サブエージェントを使って検証する」等）。自己検証と自己修正は指示がなくても行われるため、重複はコストだけを増やす
- effort は既定の `high` から始め、評価に基づいて調整する。品質が保てる範囲では `low`/`medium` をコストとレイテンシの制御手段として使い、要求の厳しいコーディング・エージェント作業では `xhigh` に上げる。旧世代から引き継いだ既定値はそのまま使わず再評価する
- Agent Teamsは限定発動（後述「委譲判断」参照）

## 委譲判断（Agent Teams / 単発Subagent / lead直接実装の使い分け、2026-07更新）

leadは常にオーケストレーション（計画・タスク分解・レビュー）を担う。以下の優先順位で機械的に判定する。

| 判定 | 条件 | 選択 |
|---|---|---|
| 1 | 5+ファイルの並列変更 or 独立タスク3つ以上 or ユーザーが「チームで」等と明示 | **Agent Teams** |
| 2 | 判定1に該当しないが、真に独立していて並列化できる規模の作業（大量のファイル読み・コードベース横断調査・ログ解析、複数ファイルにまたがる実装） | **単発Subagent**（Agent tool、`model: sonnet`を既定とする。モデル世代交代時は見直す） |
| 3 | 自分が数回のツール呼び出しで終えられる作業、および「小規模タスク」（`context/workflow-rules.md`「適用範囲」の skip 基準） | **lead直接実装** |

**委譲しないケース**:
- 自分が数回のツール呼び出しで終えられる作業
- 自分の作業の検証・ダブルチェック
- 1体で足りる作業に複数体を使うこと。spawn 数は低く保つ

**判定1（Agent Teams）**: 真に並列で進められる独立作業がある時のみ。チーム編成・TaskCreate/TaskUpdateでの依存関係管理のオーバーヘッドがペイする規模でのみ使う。

**判定2（単発Subagent）**: 目的は並列性ではなく、lead（会話・計画・統合）と実装のモデル階層分離とコンテキスト保護（実測: 委譲セッションはトークン消費約半分・compaction 1/6）。leadは結論のみを受け取り、**報告は一次情報と突き合わせて検証してから採用する**（Writer/Reviewer分離、@context/claude-customization-guide.md §8）。

## Claude Code 固有の Read when

- Agent Teams発動時（spawn前）: `context/agent-teams-guide.md`
- TaskCreate/TaskUpdate使用時（複雑タスクの初回）: `context/task-tool-guide.md`
- CLAUDE.md（AGENTS.md）・skills・hooks の設計・監査時: `context/claude-customization-guide.md`

## Claude Code 固有ツールの注意

- **Workflow ツール**: スクリプトは plain JavaScript のみ（TypeScript構文はパースエラーで空回り）
- **EnterWorktree / ExitWorktree**: 手順詳細は `context/worktree-guide.md`（sanitize・改名フロー・削除時のコミット保全）
- **Compact Instructions**: AGENTS.md 末尾のセクションを compaction 時に参照する
