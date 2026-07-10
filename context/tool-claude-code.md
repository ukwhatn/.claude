# Claude Code 固有指示

AGENTS.md から @import され、Claude Code では毎セッション常駐する。Codex 等の他エージェントはこのファイルを読む必要はない（対応表は context/tool-codex.md 参照）。

## Opus 4.7 ベストプラクティス（自律実行）

Opus 4.7 は自己完結型の実行を前提に設計されている。以下を徹底すること:
- 初回プロンプトに Goal / Constraints / Acceptance criteria を整理して渡されたら、途中介入を最小化して自律的に進める
- ペアプログラミング型の細かい指示・「こまめに」「逐一」等の過度な強制は避ける
- 検証機構（テスト・スクリーンショット・期待出力）の供給は最も効果が高い。PJ側で整備すること（@context/workflow-rules.md「検証機構」参照）
- Subagent / Agent Teams は限定発動（後述「Agent Teams 発動条件」参照）。日常タスクはモデル自身の判断に委ねる

## Agent Teams 発動条件

以下のいずれかを満たす場合のみ発動。それ以外はモデル自身の判断（直接実装または単発Subagent）に委ねる。

- (a) **複数ファイル並列**: 5+ファイルの変更が見込まれ、独立に編集できる
- (b) **独立タスク3つ以上**: 互いに依存しないタスクが3つ以上ある
- (c) **ユーザー明示指示**: ユーザーが「チームで」「Agent Teamsで」等と明示

長時間タスクで context compaction が懸念される場合は、(a)(b)(c) のいずれかに該当することが多いはず。該当しないなら通常通りモデル判断で進めて構わない。

**単発Subagentの活用（Agent Teams非発動時）**: 大量のファイル読み・コードベース調査・ログ解析は、コンテキスト保護のため単発subagent（Explore等）への委譲を優先し、本体には結論のみ持ち帰る（実測: subagent委譲セッションはトークン消費約半分・compaction 1/6）。

## Claude Code 固有の Read when

- Agent Teams発動時（spawn前）: `context/agent-teams-guide.md`
- TaskCreate/TaskUpdate使用時（複雑タスクの初回）: `context/task-tool-guide.md`
- CLAUDE.md（AGENTS.md）・skills・hooks の設計・監査時: `context/claude-customization-guide.md`

## Claude Code 固有ツールの注意

- **Workflow ツール**: スクリプトは plain JavaScript のみ（TypeScript構文はパースエラーで空回り）
- **EnterWorktree / ExitWorktree**: 手順詳細は `context/worktree-guide.md`（sanitize・改名フロー・削除時のコミット保全）
- **Compact Instructions**: AGENTS.md 末尾のセクションを compaction 時に参照する
