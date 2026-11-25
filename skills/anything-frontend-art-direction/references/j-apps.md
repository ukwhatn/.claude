# 会話型アプリの UI

プロトコルの共通仕様から始め、利用するホストの権限・表示モード・未対応機能を確認する。

[使い方](../SKILL.md) · [出典名と発行元](../sources.md)

## プロトコルと UI の受け渡し

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="j-01"></a>J-01 | MCPツールと描画リソースを結び付ける全体像 | [032](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx) |
| <a name="j-02"></a>J-02 | MCP Appsの隔離された表示領域と通信経路 | [032](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx) |
| <a name="j-03"></a>J-03 | 埋め込み表示で許可する接続先の宣言 | [032](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx) |
| <a name="j-04"></a>J-04 | UIリソースを先に登録する利点 | [032](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx) |
| <a name="j-05"></a>J-05 | A2UIの表示構造とデータを更新するメッセージ | [033](https://raw.githubusercontent.com/a2ui-project/a2ui/main/specification/v0_9/docs/a2ui_protocol.md) |
| <a name="j-06"></a>J-06 | モデル生成後にA2UIメッセージを検証する方針 | [033](https://raw.githubusercontent.com/a2ui-project/a2ui/main/specification/v0_9/docs/a2ui_protocol.md) |
| <a name="j-07"></a>J-07 | 表示の更新順を保ち操作を別経路で返す通信 | [033](https://raw.githubusercontent.com/a2ui-project/a2ui/main/specification/v0_9/docs/a2ui_protocol.md) |
| <a name="j-08"></a>J-08 | IDで表示構造を組み立てクリックを返す仕組み | [033](https://raw.githubusercontent.com/a2ui-project/a2ui/main/specification/v0_9/docs/a2ui_protocol.md) |
| <a name="j-09"></a>J-09 | Vercel AI SDKでツールの結果をReact部品に表示する流れ | [034](https://raw.githubusercontent.com/vercel/ai/main/content/docs/04-ai-sdk-ui/04-generative-user-interfaces.mdx) |
| <a name="j-10"></a>J-10 | 生成UIのサーバーストリームとクライアントの状態 | [034](https://raw.githubusercontent.com/vercel/ai/main/content/docs/04-ai-sdk-ui/04-generative-user-interfaces.mdx) |
| <a name="j-11"></a>J-11 | 会話内UIの相互運用を図る標準化の背景 | [035](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/) |
| <a name="j-12"></a>J-12 | 会話内ウィジェットの隔離と操作承認 | [035](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/) |
| <a name="j-13"></a>J-13 | UIが描画できないホストに返すツール結果 | [035](https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/) |

## ChatGPT の UI 統合

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="j2-01"></a>J2-01 | 会話で独自UIを足す判断とテキスト応答 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-02"></a>J2-02 | 描画リソース登録からホストとの通信までの手順 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-03"></a>J2-03 | 標準MCP AppsとChatGPT固有の互換フィールド | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-04"></a>J2-04 | 標準外の機能を呼び出すChatGPT拡張 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-05"></a>J2-05 | ChatGPT向けの部品ライブラリと使用例 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-06"></a>J2-06 | インライン表示から必要な大きさを決める考え方 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-07"></a>J2-07 | カルーセル・全画面・小窓を選ぶ場面 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-08"></a>J2-08 | データ取得と表示のツールを分離する目的 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-09"></a>J2-09 | 取得したデータが揃ってから一度だけ表示する流れ | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-10"></a>J2-10 | 業務データ・一時的な表示状態・永続設定の分け方 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-11"></a>J2-11 | 操作をサーバーへ送り確定データで画面を更新する流れ | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-12"></a>J2-12 | ウィジェット内の一時状態とモデルへの通知 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-13"></a>J2-13 | セッションをまたぐ状態を保存する際の認可と競合 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-14"></a>J2-14 | ホストが渡すロケールを表示に反映する方法 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-15"></a>J2-15 | ウィジェットが実際に必要とするドメインの申告 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-16"></a>J2-16 | ウィジェットの中に別のページを表示できる条件 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-17"></a>J2-17 | 外部決済を使う場合に販売側が扱う工程 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-18"></a>J2-18 | ホストの決済画面に渡すセッションと表示情報 | [103](https://developers.openai.com/plugins/build/chatgpt-ui.md) |
| <a name="j2-19"></a>J2-19 | ウィジェットやサーバーに与える権限と同意 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-20"></a>J2-20 | ツールが返すデータ・秘密情報・ログの扱い | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-21"></a>J2-21 | 入力スキーマで必要な情報だけを求める設計 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-22"></a>J2-22 | 応答に内部識別子や無関係な情報を含めない判断 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-23"></a>J2-23 | 会話のうちユーザーが共有した部分を扱う境界 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-24"></a>J2-24 | ホストが管理する概略位置情報の取得 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-25"></a>J2-25 | ツールの引数検証と不可逆操作の確認 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-26"></a>J2-26 | 隔離された表示領域で使えないブラウザ機能 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-27"></a>J2-27 | ウィジェットとサーバーで異なるネットワーク制約 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-28"></a>J2-28 | MCPへのOAuth接続とクライアント認証 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |
| <a name="j2-29"></a>J2-29 | 公開前のセキュリティ確認とリリース後の監視 | [104](https://developers.openai.com/plugins/guides/security-privacy.md) |

## MCP Apps と goose の実装例

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="j3-01"></a>J3-01 | 単独サイトと比べた会話内UIの連携 | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-02"></a>J3-02 | MCP Appの描画リソースを呼び出し前に取得する仕組み | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-03"></a>J3-03 | ツールの結果とウィジェットの双方向メッセージ | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-04"></a>J3-04 | 会話だけより表示や操作が適する場面 | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-05"></a>J3-05 | サンドボックスがホストページを隔離する範囲 | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-06"></a>J3-06 | MCP Appの通信とUIフレームワークの選択 | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-07"></a>J3-07 | MCP Appsを表示できるホストを調べる入口 | [105](https://modelcontextprotocol.io/extensions/apps/overview.md) |
| <a name="j3-08"></a>J3-08 | gooseの独立ウィンドウ表示と会話内表示 | [106](https://raw.githubusercontent.com/block/goose/main/documentation/docs/guides/interactive-chat/mcp-ui.md) |
| <a name="j3-09"></a>J3-09 | gooseの独立アプリが使えるツールやリソース | [106](https://raw.githubusercontent.com/block/goose/main/documentation/docs/guides/interactive-chat/mcp-ui.md) |
| <a name="j3-10"></a>J3-10 | 共有されたHTMLをgooseに取り込む方法 | [106](https://raw.githubusercontent.com/block/goose/main/documentation/docs/guides/interactive-chat/mcp-ui.md) |
| <a name="j3-11"></a>J3-11 | gooseの会話内でツールのUIを操作する流れ | [106](https://raw.githubusercontent.com/block/goose/main/documentation/docs/guides/interactive-chat/mcp-ui.md) |
| <a name="j3-12"></a>J3-12 | gooseのチュートリアルが想定する実装範囲 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-13"></a>J3-13 | gooseの例で表示対象のリソースを伝えるメタデータ | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-14"></a>J3-14 | MCP Appをリソース一覧に登録する識別子とメディア型 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-15"></a>J3-15 | UI リソースの CSP と表示枠の希望をどのフィールドに指定するか。ホストへの希望と実際の表示を区別する。 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) · [032](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx) |
| <a name="j3-16"></a>J3-16 | ウィジェットの初期化完了とテーマの受け取り | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-17"></a>J3-17 | gooseの橋渡し例で要求と応答を対応させる方法 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-18"></a>J3-18 | サイズ変更やユーザーの意図をホストに通知する方法 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-19"></a>J3-19 | CSPで接続・素材・フレームの参照先を分ける方法 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-20"></a>J3-20 | 機器やクリップボードへのアクセスを宣言する項目 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-21"></a>J3-21 | 機能の宣言・ホストによる許可・利用者の同意 | [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |
| <a name="j3-22"></a>J3-22 | 仕様とチュートリアルで使われる通信メソッド | [032](https://raw.githubusercontent.com/modelcontextprotocol/ext-apps/main/specification/2026-01-26/apps.mdx) · [105](https://modelcontextprotocol.io/extensions/apps/overview.md) · [107](https://raw.githubusercontent.com/block/goose/main/documentation/docs/tutorials/building-mcp-apps.md) |

## ホストごとの対応範囲

| ID | 確認すること | 出典 |
| --- | --- | --- |
| <a name="j4-01"></a>J4-01 | VS CodeでのMCP機能に影響する実行環境とクライアント | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-02"></a>J4-02 | VS Codeの会話内UIとエディターで異なるリソース参照 | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-03"></a>J4-03 | VS Codeで入力を求められる会話の段階 | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-04"></a>J4-04 | VS Codeの会話でMCP Appを表示する条件 | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-05"></a>J4-05 | VS Codeが提供する表示モードとチャット入力連携 | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-06"></a>J4-06 | VS Codeのサンドボックスと接続先制限 | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-07"></a>J4-07 | VS Codeが仲介するMCPサーバーの認証 | [110](https://code.visualstudio.com/api/extension-guides/ai/mcp.md) |
| <a name="j4-08"></a>J4-08 | Claude向けMCP Apps SDKのサーバー側と表示側 | [111](https://claude.com/docs/connectors/building/mcp-apps/quickstart.md) |
| <a name="j4-09"></a>J4-09 | Claudeホストに描画リソースの場所を伝える方法 | [111](https://claude.com/docs/connectors/building/mcp-apps/quickstart.md) |
| <a name="j4-10"></a>J4-10 | 表示部品とテキスト利用を両立するツールの戻り値 | [111](https://claude.com/docs/connectors/building/mcp-apps/quickstart.md) |
| <a name="j4-11"></a>J4-11 | ClaudeのどのクライアントでUIを表示できるか | [111](https://claude.com/docs/connectors/building/mcp-apps/quickstart.md) |
| <a name="j4-12"></a>J4-12 | Claude向けのUIを会話の一部として設計する原則 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-13"></a>J4-13 | 会話内ウィジェットに収まりやすい作業の特徴 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-14"></a>J4-14 | 結果や簡単な操作をインラインカードに置く用途 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-15"></a>J4-15 | 似た候補をカルーセルで見比べる用途 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-16"></a>J4-16 | 会話と並行する作業や広い画面が必要な作業の表示方法 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-17"></a>J4-17 | ClaudeモバイルのWebViewでレイアウトを検証する観点 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-18"></a>J4-18 | ホストとの一貫性とブランド表示を両立させる方法 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-19"></a>J4-19 | 利用者が会話とウィジェットを行き来する操作設計 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-20"></a>J4-20 | Claudeが渡すスタイル変数を画面へ反映する方法 | [112](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| <a name="j4-21"></a>J4-21 | M365 Copilotで会話内アプリを開発する前提 | [113](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-mcp-apps) |
| <a name="j4-22"></a>J4-22 | M365 Copilotの認証・許可ドメイン・リダイレクト設定 | [113](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-mcp-apps) |
| <a name="j4-23"></a>J4-23 | M365 Copilot向けのUX指針とAPIの環境差 | [113](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-mcp-apps) |
| <a name="j4-24"></a>J4-24 | M365 Copilotの標準ブリッジとChatGPT拡張の対応表 | [113](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-mcp-apps) |
| <a name="j4-25"></a>J4-25 | M365 Copilot内にMCPウィジェットを表示する仕組み | [113](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/plugin-mcp-apps) |
