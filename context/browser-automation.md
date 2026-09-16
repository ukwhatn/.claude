# ブラウザ操作（Claude in Chrome / playwright / chrome-devtools）

Read when: ブラウザ操作ツール（`mcp__claude-in-chrome__*` / `mcp__playwright__*` / `mcp__chrome-devtools__*`）を呼ぶ前、またはブラウザ自動化のセットアップ・接続設定を変更する前。マシン固有の実値（browser 名 → deviceId の対応・ポート・プロファイルの場所）は `~/.claude/local/chrome-browser-mapping.md` と `CLAUDE.local.md`（git 管理外。存在しない環境もある）。

## Claude in Chrome（browser 識別）

Chrome 拡張は複数 profile の同時接続をサポートするが、Connected browser の name を永続変更する UI / API は現時点で存在しない（Anthropic 側 feature request 未実装: [claude-code#14536](https://github.com/anthropics/claude-code/issues/14536) / [#14981](https://github.com/anthropics/claude-code/issues/14981) / [#25551](https://github.com/anthropics/claude-code/issues/25551)）。

- `list_connected_browsers` の `name` は connectedAt 順に「Browser 1/2/3」で動的採番される。`switch_browser` の Connect 時に入力した name が反映されることがあるが、他 browser の再接続で reset されることがあるため信用しない
- **deviceId のみが stable な識別子**（マシンごとに固有。Chrome プロファイルの user data から生成）
- mapping を確定させたい場合: 該当 Chrome を再起動 → `list_connected_browsers` で connectedAt が更新された deviceId がその browser
- 環境変数（`CLAUDE_CHROME_BROWSER` 等）/ `settings.json` での事前指定は未サポート
- **最初のタブを開く前に、どの Chrome を操作するかを確定させる**。接続済みの browser が 1 つに絞れているときはエラーが出ず、既定の browser で黙って操作が進むため、意図と違う Chrome を操作していることに気付けない。`list_connected_browsers` で deviceId を確認し、`select_browser({deviceId})` で明示してから操作を始める。**ユーザーは browser をマシン名・プロファイル名で指す**ので、名前 → deviceId の対応は `local/chrome-browser-mapping.md` を Read する
- `computer` ツール等が「Multiple Chrome browsers are connected」エラーになったら、`list_connected_browsers` → `select_browser({deviceId})` で選ぶか、`switch_browser` で対象 Chrome の Connect ボタンをユーザーが click する

## ブラウザ操作 MCP（複数セッションでの共有）

普段使いのブラウザを複数セッションから同時に操作する場合、**MCP サーバをセッションごとに起こさない**。stdio で起こすと、拡張ブリッジ方式では拡張が同時に 1 接続しか保持しないため後から繋いだセッションが先のセッションを切断し、CDP 直結方式では接続ごとにブラウザ側の承認ダイアログが出る。

**使うブラウザ経路は 3 つに限る**: Claude in Chrome（普段使いの Chrome を拡張経由で操作）、playwright（自動化専用 Chrome を常駐サーバ経由で操作）、chrome-devtools（同じ自動化専用 Chrome に CDP で繋いで計測）。普段使いの Chrome へ chrome-devtools-mcp を直接繋ぐ構成（`--autoConnect` 等）は置かない（下記「ユーザーが起動したブラウザへ繋ぐ方式は使わない」と同じ理由）。

**新規 PC でのセットアップは `bin/playwright-mcp-setup.sh` を実行するだけ**（冪等）。LaunchAgent の生成・配置、CDP ポートを開ける playwright 設定の生成、`~/.claude.json` の `mcpServers.playwright`（HTTP）と `mcpServers.chrome-devtools`（`npx chrome-devtools-mcp --browserUrl http://127.0.0.1:<CDPポート>`）の設定、node バージョンの確認までを行う。残る手動作業は、スクリプトが起動する自動化専用 Chrome へのログインだけ（OAuth フローは自動化できない）。

構成は「サーバ 1 本を常駐させ、各セッションは HTTP クライアントとして接続する」。playwright-mcp の場合:

- 常駐: `~/.claude/bin/playwright-mcp-server.sh`（LaunchAgent。ラベルとログパスはセットアップスクリプトが決める）
- 接続: MCP 設定は `{"type":"http","url":"http://127.0.0.1:8931/mcp"}`
- サーバ自身が `--user-data-dir`（**自動化専用**の user-data-dir）でブラウザを起動し、`--shared-browser-context` で全クライアントに同一コンテキストを共有させる。起動フラグの追加は `--config` の `browser.launchOptions.args` で渡す
- **自動化ドライバに普段使いのブラウザプロファイルを開かせない（CRITICAL）**: ドライバはブラウザ起動時に既定でモックの資格情報ストア（`--use-mock-keychain` / `--password-store=basic`）と `--disable-extensions` を付ける。OS キーチェーン由来の鍵で暗号化された cookie とアカウントトークンは復号できなくなって cookie ストアが作り直され、拡張は無効化されたうえで未参照ディレクトリが削除される。ブックマークと履歴は暗号化されていないため残るので、**被害が部分的にしか見えず、プロファイルが壊れたことに気付きにくい**
- 上記の帰結として、自動化ブラウザでは**拡張機能が動かない**。ログイン状態（cookie）は持てるが、拡張前提の操作は自動化できない
- **ユーザーが起動したブラウザへ `--cdp-endpoint` で繋ぐ方式は使わない**（接続ごとにブラウザ側の承認ダイアログが出るため）。サーバ自身に起動させれば承認経路を通らない
- 接続クライアントが 0 になるとブラウザが閉じられるため、常駐クライアント（`bin/playwright-mcp-pin.py`）が 1 本張り続けて生かしておく
- 永続プロファイルは同時に 1 インスタンスしか掴めない。サーバ起動前にブラウザが起動していると profile lock で失敗する
- **共有コンテキストの弱点**: 応答しないタブが 1 枚あると、タブ一覧の取得が返らず全セッションの操作がブロックされる。タブ操作が固まったら、まず応答しないタブを疑う（未コミットのタブ・プリレンダーされたタブが該当し得る）

**同一コンテキストを共有するため、タブは自分のものだけを触る**:

- 操作の開始時に自分のタブを新規に開き、以後は自分の current tab に対してのみ操作する
- `browser_tabs` の index 指定で select / close しない（index は他セッションのタブ開閉でずれるため、ユーザーの既存タブや他セッションのタブを閉じる事故になる）。自分のタブを閉じるときは index を省く（current tab が閉じる）
- タブ一覧にはユーザーの実タブが全て見える。**読み取った内容を無関係な文脈で持ち出さない**

## playwright と chrome-devtools の使い分け

- 操作・状態いじり・テスト生成は playwright（cookie / localStorage / sessionStorage の CRUD、storage state の保存、リクエストのモックとオフライン化、ロケータ生成）
- 計測は chrome-devtools（performance trace と Core Web Vitals、Lighthouse、heap snapshot によるリーク調査、CPU・ネットワークのスロットリング）
- navigate / click / snapshot / console / network 一覧はどちらでもできる。常用しているサーバ側で済ませる
- chrome-devtools は stdio 専用で HTTP transport を持たないため、サーバ 1 本を複数セッションで共有できない（セッションごとにプロセスが立ち、同一エンドポイントに複数プロセスが群がると CDP セッションが競合する）。計測が必要になったときだけ使い、常用しない
- **両者は同じ自動化ブラウザを共有する**（セットアップスクリプトの既定構成）。ブラウザに `--remote-debugging-port` を開けておき、chrome-devtools は `--browserUrl` でそこへ繋ぐ。自動化用の user-data-dir は既定パス外なので古典的な remote debugging が使え、承認ダイアログも出ない（承認を要求するのはブラウザ内から有効化する新方式のみ）。引き換えに、そのポートは無認証で開くので、ログイン状態を持つ自動化ブラウザをローカルの任意プロセスが操作できる
