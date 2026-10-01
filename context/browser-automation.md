# ブラウザ操作（Claude in Chrome / playwright / chrome-devtools）

Read when: ブラウザ操作ツール（`mcp__claude-in-chrome__*` / `mcp__playwright__*` / `mcp__chrome-devtools__*`）を呼ぶ前、またはブラウザ自動化のセットアップ・接続設定を変更する前。マシン固有の実値（browser名 → deviceIdの対応・ポート・プロファイルの場所）は `~/.claude/local/chrome-browser-mapping.md` と `CLAUDE.local.md`（git管理外。存在しない環境もある）。

## Claude in Chrome（browser識別）

Chrome拡張は複数profileの同時接続をサポートするが、Connected browserのnameを永続変更するUI / APIは現時点で存在しない（Anthropic側feature request未実装: [claude-code#14536](https://github.com/anthropics/claude-code/issues/14536) / [#14981](https://github.com/anthropics/claude-code/issues/14981) / [#25551](https://github.com/anthropics/claude-code/issues/25551)）。

- `list_connected_browsers` の `name` はconnectedAt順に「Browser 1/2/3」で動的採番される。`switch_browser` のConnect時に入力したnameが反映されることがあるが、他browserの再接続でresetされることがあるため信用しない
- **deviceIdのみがstableな識別子**（マシンごとに固有。Chromeプロファイルのuser dataから生成）
- mappingを確定させたい場合: 該当Chromeを再起動 → `list_connected_browsers` でconnectedAtが更新されたdeviceIdがそのbrowser
- 環境変数（`CLAUDE_CHROME_BROWSER` 等）/ `settings.json` での事前指定は未サポート
- **最初のタブを開く前に、どのChromeを操作するかを確定させる**。接続済みのbrowserが1つに絞れているときはエラーが出ず、既定のbrowserで通知なく操作が進むため、意図と違うChromeを操作していることに気付けない。`list_connected_browsers` でdeviceIdを確認し、`select_browser({deviceId})` で明示してから操作を始める。**ユーザーはbrowserをマシン名・プロファイル名で指す**ので、名前 → deviceIdの対応は `local/chrome-browser-mapping.md` をReadする
- `computer` ツール等が「Multiple Chrome browsers are connected」エラーになったら、`list_connected_browsers` → `select_browser({deviceId})` で選ぶか、`switch_browser` で対象ChromeのConnectボタンをユーザーがclickする

## ブラウザ操作MCP（複数セッションでの共有）

普段使いのブラウザを複数セッションから同時に操作する場合、**MCPサーバをセッションごとに起こさない**。stdioで起こすと、拡張ブリッジ方式では拡張が同時に1接続しか保持しないため後から繋いだセッションが先のセッションを切断し、CDP直結方式では接続ごとにブラウザ側の承認ダイアログが出る。

**使うブラウザ経路は3つに限る**: Claude in Chrome（普段使いのChromeを拡張経由で操作）、playwright（自動化専用Chromeを常駐サーバ経由で操作）、chrome-devtools（同じ自動化専用ChromeにCDPで繋いで計測）。普段使いのChromeへchrome-devtools-mcpを直接繋ぐ構成（`--autoConnect` 等）は置かない（下記「ユーザーが起動したブラウザへ繋ぐ方式は使わない」と同じ理由）。

**新規PCでのセットアップは `bin/playwright-mcp-setup.sh` を実行するだけ**（冪等）。LaunchAgentの生成・配置、CDPポートを開けるplaywright設定の生成、`~/.claude.json` の `mcpServers.playwright`（HTTP）と `mcpServers.chrome-devtools`（`npx chrome-devtools-mcp --browserUrl http://127.0.0.1:<CDPポート>`）の設定、nodeバージョンの確認までを行う。残る手動作業は、スクリプトが起動する自動化専用Chromeへのログインだけ（OAuthフローは自動化できない）。

構成は「サーバ1本を常駐させ、各セッションはHTTPクライアントとして接続する」。playwright-mcpの場合:

- 常駐: `~/.claude/bin/playwright-mcp-server.sh`（LaunchAgent。ラベルとログパスはセットアップスクリプトが決める）
- 接続: MCP設定は `{"type":"http","url":"http://127.0.0.1:8931/mcp"}`
- サーバ自身が `--user-data-dir`（**自動化専用**のuser-data-dir）でブラウザを起動し、`--shared-browser-context` で全クライアントに同一コンテキストを共有させる。起動フラグの追加は `--config` の `browser.launchOptions.args` で渡す
- **自動化ドライバに普段使いのブラウザプロファイルを開かせない（CRITICAL）**: ドライバはブラウザ起動時に既定でモックの資格情報ストア（`--use-mock-keychain` / `--password-store=basic`）と `--disable-extensions` を付ける。OSキーチェーン由来の鍵で暗号化されたcookieとアカウントトークンは復号できなくなってcookieストアが作り直され、拡張は無効化されたうえで未参照ディレクトリが削除される。ブックマークと履歴は暗号化されていないため残るので、**被害が部分的にしか見えず、プロファイルが壊れたことに気付きにくい**
- 上記の帰結として、自動化ブラウザでは**拡張機能が動かない**。ログイン状態（cookie）は持てるが、拡張前提の操作は自動化できない
- **ユーザーが起動したブラウザへ `--cdp-endpoint` で繋ぐ方式は使わない**（接続ごとにブラウザ側の承認ダイアログが出るため）。サーバ自身に起動させれば承認経路を通らない
- 接続クライアントが0になるとブラウザが閉じられるため、常駐クライアント（`bin/playwright-mcp-pin.py`）が接続を1本保持し続けてブラウザを閉じさせない
- 永続プロファイルは同時に1インスタンスからしか開けない。サーバ起動前にブラウザが起動しているとprofile lockで失敗する
- **共有コンテキストの弱点**: 応答しないタブが1枚あると、タブ一覧の取得が返らず全セッションの操作がブロックされる。タブ操作が応答しなくなったら、まず応答しないタブがあるかを確認する（未コミットのタブ・プリレンダーされたタブが該当し得る）

**同一コンテキストを共有するため、タブは自分のものだけを触る**:

- 操作の開始時に自分のタブを新規に開き、以後は自分のcurrent tabに対してのみ操作する
- `browser_tabs` のindex指定でselect / closeしない（indexは他セッションのタブ開閉でずれるため、ユーザーの既存タブや他セッションのタブを誤って閉じてしまう）。自分のタブを閉じるときはindexを省く（current tabが閉じる）
- タブ一覧にはユーザーの実タブが全て見える。**読み取った内容を無関係な文脈で持ち出さない**

## playwrightとchrome-devtoolsの使い分け

- 操作・状態いじり・テスト生成はplaywright（cookie / localStorage / sessionStorageのCRUD、storage stateの保存、リクエストのモックとオフライン化、ロケータ生成）
- 計測はchrome-devtools（performance traceとCore Web Vitals、Lighthouse、heap snapshotによるリーク調査、CPU・ネットワークのスロットリング）
- navigate / click / snapshot / console / network一覧はどちらでもできる。常用しているサーバ側で済ませる
- chrome-devtoolsはstdio専用でHTTP transportを持たないため、サーバ1本を複数セッションで共有できない（セッションごとにプロセスが立ち、同一エンドポイントに複数プロセスが接続するとCDPセッションが競合する）。計測が必要になったときだけ使い、常用しない
- **両者は同じ自動化ブラウザを共有する**（セットアップスクリプトの既定構成）。ブラウザに `--remote-debugging-port` を開けておき、chrome-devtoolsは `--browserUrl` でそこへ繋ぐ。自動化用のuser-data-dirは既定パス外なので古典的なremote debuggingが使え、承認ダイアログも出ない（承認を要求するのはブラウザ内から有効化する新方式のみ）。引き換えに、そのポートは無認証で開くので、ログイン状態を持つ自動化ブラウザをローカルの任意プロセスが操作できる
