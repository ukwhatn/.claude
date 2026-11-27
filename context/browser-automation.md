# ブラウザ操作（Claude in Chrome / playwright / chrome-devtools）

ブラウザ操作ツール（`mcp__claude-in-chrome__*` / `mcp__playwright__*` / `mcp__chrome-devtools__*`）の使い方と、ブラウザ自動化の構成。マシン固有の実値（browser名 → deviceIdの対応・ポート・プロファイルの場所）は `~/.claude/local/chrome-browser-mapping.md` と `CLAUDE.local.md`（git管理外。存在しない環境もある）。

## Claude in Chrome（browser識別）

Chrome拡張は複数profileの同時接続をサポートするが、Connected browserのnameを永続的に変えるUI / APIは無い（Anthropic側のfeature requestが未実装）。

- `list_connected_browsers` の `name` はconnectedAt順に「Browser 1/2/3」で動的採番される。`switch_browser` のConnect時に入力したnameが反映されることがあるが、他browserの再接続でresetされることがあるため信用しない
- stableな識別子はdeviceIdだけ（マシンごとに固有。Chromeプロファイルのuser dataから生成）
- mappingを確定させたい場合: 該当Chromeを再起動 → `list_connected_browsers` でconnectedAtが更新されたdeviceIdがそのbrowser
- 環境変数（`CLAUDE_CHROME_BROWSER` 等）/ `settings.json` での事前指定は未サポート
- **最初のタブを開く前に、どのChromeを操作するかを確定させる**。接続済みのbrowserが1つに絞れているときはエラーが出ず、既定のbrowserで通知なく操作が進むため、意図と違うChromeを操作していることに気付けない。`list_connected_browsers` でdeviceIdを確認し、`select_browser({deviceId})` で明示してから操作を始める。ユーザーはbrowserをマシン名・プロファイル名で指すので、名前 → deviceIdの対応は `local/chrome-browser-mapping.md` をReadする
- `computer` ツール等が「Multiple Chrome browsers are connected」エラーになったら、`list_connected_browsers` → `select_browser({deviceId})` で選ぶか、`switch_browser` で対象ChromeのConnectボタンをユーザーにclickしてもらう

## ブラウザ操作MCP（複数セッションでの共有）

普段使いのブラウザを複数セッションから同時に操作する場合、MCPサーバをセッションごとに起こさない。stdioで起こすと、拡張ブリッジ方式では拡張が同時に1接続しか保持しないため後から繋いだセッションが先のセッションを切断し、CDP直結方式では接続ごとにブラウザ側の承認ダイアログが出る。

使うブラウザ経路は3つに限る: Claude in Chrome（普段使いのChromeを拡張経由で操作）、playwright（自動化専用Chromeを常駐サーバ経由で操作）、chrome-devtools（同じ自動化専用ChromeにCDPで繋いで計測）。ユーザーが起動したブラウザへCDPで繋ぐ構成（chrome-devtools-mcpの `--autoConnect`、playwrightの `--cdp-endpoint` 等）は置かない。接続ごとにブラウザ側の承認ダイアログが出るため。サーバ自身にブラウザを起動させれば承認経路を通らない。

新規PCでのセットアップは `bin/playwright-mcp-setup.sh` を実行するだけ（冪等）。LaunchAgentの生成・配置、CDPポートを開けるplaywright設定の生成、`~/.claude.json` の `mcpServers.playwright`（HTTP）と `mcpServers.chrome-devtools`（`npx chrome-devtools-mcp --browserUrl http://127.0.0.1:<CDPポート>`）の設定、nodeバージョンの確認、`bin/playwright-mcp-extensions.txt` に並べた拡張の導入までを行う。サイトへのログインは、下の「自動化Chromeでのログイン」の `browser-login` で行う。

構成は「サーバ1本を常駐させ、各セッションはHTTPクライアントとして接続する」。playwright-mcpの場合:

- 常駐: `~/.claude/bin/playwright-mcp-server.sh`（LaunchAgent。ラベルとログパスはセットアップスクリプトが決める）
- 自動化専用Chromeは Chrome Beta で動かす（セットアップスクリプトが brew で入れる。無いマシンでは普段使いと同じChromeで動く）。macOSはアプリをbundle IDで1つに扱うので、普段使いと同じ `Google Chrome.app` で起動すると、Dockやリンクから開いたChromeが自動化側に吸われる
  - playwrightはタブを作るときに背景の指定を付けないので、Chromeはタブのたびに前面に出て、仮想デスクトップも移る。`bin/playwright-mcp-background-tabs.cjs` を `NODE_OPTIONS` の `--require` で読み込ませ、タブの作成に `background: true` を付けている。playwrightの更新で書き換える箇所が無くなると、サーバのログに `[background-tabs] pattern not found` が出て、前面に出る動作に戻る。タブの選択（`browser_tabs` の select）は playwright-mcp が明示的に前面に出すので、今も前面に出る
  - 安定版で使っていたプロファイルをBetaで開くと、Betaはcookieを読めずに空にする。切り替えるときは、プロファイルの写しを安定版で開いてcookieをCDPで読み出し、Betaに書き込む。Googleアカウントのcookieは、移したあとの再起動で消えるマシン（手元のMac）と残るマシン（studio）があった。移したあとにアカウント選択画面と `myaccount.google.com/u/<n>/` の遷移先でログイン状態を確認し、切れていれば `browser-login` で入り直す
- 接続: MCP設定は `{"type":"http","url":"http://127.0.0.1:8931/mcp"}`
- サーバ自身が `--user-data-dir`（自動化専用のuser-data-dir）でブラウザを起動し、`--shared-browser-context` で全クライアントに同一コンテキストを共有させる。起動フラグの追加は `--config` の `browser.launchOptions.args` で渡す
- **自動化ドライバに普段使いのブラウザプロファイルを開かせない**。ドライバはブラウザ起動時に既定でモックの資格情報ストア（`--use-mock-keychain` / `--password-store=basic`）と `--disable-extensions` を付ける。OSキーチェーン由来の鍵で暗号化されたcookieとアカウントトークンは復号できなくなってcookieストアが再作成され、拡張は無効化されたうえで未参照ディレクトリが削除される。ブックマークと履歴は暗号化されていないため残るので、被害が部分的にしか見えず、プロファイルが壊れたことに気付きにくい
- 自動化専用Chromeでは拡張が動く。playwright-mcpは `--disable-extensions` を既定の起動引数から外している
  - 拡張は `bin/playwright-mcp-extensions.txt` にChromeウェブストアのIDを書き、セットアップスクリプトで入れる。外部拡張の設定を置き、起動後に `chrome.management.setEnabled` で有効にするので、人の操作もVNCも使わない
  - playwright設定の `ignoreDefaultArgs` で `--disable-default-apps` と `--disable-background-networking` を外している。この2つが付いていると、Chromeは外部拡張の設定を読まず、拡張のダウンロードと更新もしない
  - ストアに無い拡張（手元で開発している拡張など）は、そのマシンだけの一覧 `~/.claude/local/playwright-mcp-unpacked-extensions.txt`（git管理外）にディレクトリのパスを書く。ブランド版のChromeは `--load-extension` を受け付けないので、`--enable-unsafe-extension-debugging` を付けて起動し、CDPの `Extensions.loadUnpacked` で読み込む。読み込んだ拡張は再起動で消えるので、`bin/playwright-mcp-pin.py` がブラウザの起動を検知するたびに読み込む（最大で約1分遅れる）
  - 1Password拡張は入れない。解除した拡張は個人アカウント全体を読めるので、無認証のCDPポートに繋がるすべてのクライアントから読める状態になる。ページの `navigator.credentials` も置き換えるので、`browser-login` の仮想認証器より先にパスキーの要求を受け取る
- 接続クライアントが0になるとブラウザが閉じられるため、常駐クライアント（`bin/playwright-mcp-pin.py`）が接続を1本保持し続けてブラウザを閉じさせない
- 永続プロファイルは同時に1インスタンスからしか開けない。サーバ起動前にブラウザが起動しているとprofile lockで失敗する
- 共有コンテキストの弱点: 応答しないタブが1枚あると、タブ一覧の取得が返らず全セッションの操作がブロックされる。タブ操作が応答しなくなったら、まず応答しないタブがあるかを確認する（未コミットのタブ・プリレンダーされたタブが該当し得る）

同一コンテキストを共有するため、タブは自分のものだけを触る:

- 操作の開始時に自分のタブを新規に開き、以後は自分のcurrent tabに対してのみ操作する
- `browser_tabs` のindex指定でselect / closeしない（indexは他セッションのタブ開閉でずれるため、ユーザーの既存タブや他セッションのタブを誤って閉じてしまう）。自分のタブを閉じるときはindexを省く（current tabが閉じる）
- タブ一覧にはユーザーの実タブが全て見える。読み取った内容を無関係な文脈で持ち出さない

## 自動化Chromeでのログイン（browser-login）

ログイン画面が出たら、ユーザーにVNCでのログインを頼む前に `bin/browser-login` を使う。ヘルパーが1Passwordのvault（`0_Primary`）の値を入力欄に入れ、エージェントには状態だけを返す。エージェントはID・パスワード・TOTP・秘密鍵を受け取らないので、`browser_type` や `browser_fill_form` に値を書かない。

サービスアカウントは組み込みのPersonal vaultを読めないので、自動化に使うLogin項目はサービスアカウントが読める `0_Primary` に置く（2026-11-25 に専用vault `Z_Automation` から移設した）。ログインが失敗し続けるときは、ユーザーに項目の値が古くないかを確認してもらう。

1. 自分のタブで、titleの末尾に目印を付ける（目印は英数字・`-`・`_` の4〜64文字。ほかのセッションと重ならない値にする）

   ```js
   // browser_evaluate
   () => { document.title += ' [browser-login:<目印>]' }
   ```

2. ヘルパーを背景で起動する（Bashの `run_in_background`）。項目IDは `browser-login items`（vaultのLogin項目のID・題・URLだけを出す）で調べる。サービスアカウントのトークンが無いマシンでは使えない

   ```sh
   ~/.claude/bin/browser-login login --tab-mark <目印> --item <項目ID> [--timeout 120]
   ```

3. 画面の操作（次へ・ログイン・パスキーでログイン のクリック）は自分で行う。ヘルパーは、ID・パスワード・TOTPの欄が出るたびに1回ずつ値を入れ、パスキーの要求には仮想認証器で応答する。状態は標準出力に1行1つのJSONで出る
   - **ヘルパーを起動してから止めるまでは、スナップショットを作るツール（`browser_click`・`browser_navigate`・`browser_snapshot`・`browser_find` など）を使わない。** playwrightのスナップショットは、パスワード欄に入った値を伏せずに書き出し、`.playwright-mcp/` のファイルにも残す。クリックと遷移は `browser_evaluate`（ボタンを文言で探して `click()`、遷移は `location.href`）で行い、画面は `browser_take_screenshot` で確認する（パスワードは伏せ字で写る）
     - ヘルパーが動いている間は、PreToolUse hook（`hooks/browser-login-guard.py`）が、playwrightとchrome-devtoolsのツールのうちスナップショットを返さないもの以外を拒否する。動いているかは、実行記録（`~/.local/state/browser-login/run-*.json`）のpidが生きているかで判定する
     - ヘルパーは終了するとき（stop・パスキーの認証・時間切れ・例外・SIGINTのどれでも。SIGKILLを除く）、パスワードとTOTPの欄に残った値を空にする。ログインが進まないまま止めたあとにスナップショットを取っても、値は写らない
   - このマシン用のパスキーが無いときも、ヘルパーは空の仮想認証器を入れる。サイトのパスキーの要求はすぐ失敗するので、サイトの「別の方法を試す」からパスワードに進む（仮想認証器が無いと、Chrome自体のパスキーのダイアログが出て、要求が保留のまま残る）
4. 画面でログインの完了を確認したら、`browser-login stop --tab-mark <目印>` で終了させる。パスキーで認証したときと時間切れのときは、ヘルパーが自分で終了する

状態と、そのときにすること:

- `filled`（`field` が `username` / `password` / `totp`）: 値を入れた。次のボタンを押す
- `passkey-ready` / `passkey-asserted`: このマシン用のパスキーを入れた / 認証した
- `origin-mismatch`: 入力欄のオリジンが、項目のURLのホストともそのサブドメインとも一致しないので入れなかった。正しいサイトなら、ユーザーに項目のURLの追加を頼む
- `fill-skipped`: 欄を見つけたが入力の直前に確認できなかった
- `already-running` / `busy`: 同じタブで別のヘルパーが動いている / このマシンで同じパスキーを使うログインが動いている。終わるのを待つ
- `tab-not-found` / `tab-ambiguous`: 目印の付いたタブが無い / 2つ以上ある
- `token-missing` / `token-permissions` / `item-not-found` / `rate-limited`: ユーザーに伝えて止まる。再試行しない
- `timeout`: 入れた欄は `filled` に出る。メールやSMSの確認コード、CAPTCHA、端末の管理状態を確認するSSOで止まっているなら、ユーザーに頼む

パスキーはマシンごとに自動化専用のものを登録する（1Passwordに保存したパスキーは秘密鍵を書き出せないため）。登録は手元のMacで、ユーザー本人の `op` を使って行う（1Passwordの承認が出る）。

```sh
~/.claude/bin/browser-login enroll-passkey --tab-mark <目印> --item <項目ID> --for-host <マシンのLocalHostName>
```

起動したらサイトのパスキー追加の操作をする。トークンを置いたマシンの台数分、`--for-host` を変えて繰り返す。マシン名は各マシンの `scutil --get LocalHostName` の値。

## playwrightとchrome-devtoolsの使い分け

- 操作・状態いじり・テスト生成はplaywright（cookie / localStorage / sessionStorageのCRUD、storage stateの保存、リクエストのモックとオフライン化、ロケータ生成）
- 計測はchrome-devtools（performance traceとCore Web Vitals、Lighthouse、heap snapshotによるリーク調査、CPU・ネットワークのスロットリング）
- navigate / click / snapshot / console / network一覧はどちらでもできる。常用しているサーバ側で済ませる
- playwrightの `browser_run_code_unsafe` は、実行したコードをツールの出力に表示する（`filename` で渡しても表示する）。秘密の値を含むコードは渡さず、Cookieはアプリ側の手順など値が出力に出ない経路で入れる。`filename` はワークスペースの下（allowed roots）しか読まない
- chrome-devtoolsはstdio専用でHTTP transportを持たないため、サーバ1本を複数セッションで共有できない（セッションごとにプロセスが立ち、同一エンドポイントに複数プロセスが接続するとCDPセッションが競合する）。計測が必要になったときだけ使い、常用しない
- 両者は同じ自動化ブラウザを共有する（セットアップスクリプトの既定構成）。ブラウザに `--remote-debugging-port` を開けておき、chrome-devtoolsは `--browserUrl` でそこへ繋ぐ。自動化用のuser-data-dirは既定パス外なので古典的なremote debuggingが使え、承認ダイアログも出ない（承認を要求するのはブラウザ内から有効化する新方式のみ）。引き換えに、そのポートは無認証で開くので、ログイン状態を持つ自動化ブラウザをローカルの任意プロセスが操作できる
