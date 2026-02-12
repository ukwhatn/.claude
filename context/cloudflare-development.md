# Cloudflare (wrangler) 開発ガイド

## wrangler セットアップ
- wranglerはbunでインストールする（`bun add -d wrangler`）

## アカウント管理
- **CRITICAL: 複数のCloudflareアカウントが存在する。デプロイ先アカウントは必ずAskUserQuestionで確認すること（推測・仮定は禁止）**
- `bunx wrangler whoami` で利用可能なアカウント一覧を確認してからユーザーに提示・質問する
- PJ CLAUDE.mdまたはpackage.jsonに`CLOUDFLARE_ACCOUNT_ID`が明記されている場合はそれを使用する
- アカウントが明記されていない場合、デフォルトは `ukwhatn`（`40903f86185f39b5108a3dc845090406`）
