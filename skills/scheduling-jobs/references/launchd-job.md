# launchd でスクリプトを定期実行する

目次: 作るもの / 本体スクリプト / setup スクリプト / plist / 確認と停止 / Gotchas

## 作るもの

| ファイル | 置き場所 |
|---|---|
| 本体 `<name>.sh` | 他のマシンでも成り立つなら `~/.claude/bin/`、このマシンだけなら git 管理外のツールのディレクトリ |
| setup `<name>-setup.sh` | 本体と同じ場所 |
| マシン固有の設定 `config.sh` | `~/.config/<name>/`（git 管理外。実値はここに書く） |
| ログ | `~/Library/Logs/<name>/` |
| plist | `~/Library/LaunchAgents/<label>.plist`（setup が生成する。手で書かない） |

label は `<逆ドメイン>.<name>`。既存の自作の plist（`ls ~/Library/LaunchAgents`）と同じ接頭辞にそろえる。

## 本体スクリプト

- 引数なしは dry-run（何をするかの報告だけ）、`--apply` で実行する。登録前に dry-run の報告をユーザーに見せる
- 「N日おき」のように launchd の規則で書けない頻度は、毎時起動して `--scheduled` のときに本体が実行要否を判定する（前回実行時刻をファイルに残し、経過時間で決める）。スリープ中に予定時刻を過ぎても、次の起動で拾える
- 独立した処理は1つ失敗しても次へ進め、最後に失敗の有無で終了コードを決める（`set -e` に頼らない）
- 消す処理はゴミ箱（`/usr/bin/trash`）に入れる。`rm -rf` は、消えても困らないとユーザーが確認した場所だけにする

## setup スクリプト

何度実行しても同じ状態に収束させる。やること:

1. 本体に実行権限を付け、ログと設定のディレクトリを作る
2. 設定ファイルが無ければ雛形を置く（あれば触らない）
3. 依存コマンド（`gh`・`docker`・`npm` 等）を `command -v` で引き、そのディレクトリを PATH に並べる。launchd の PATH は `/usr/bin:/bin:/usr/sbin:/sbin` だけで、Homebrew やランタイムの管理ツールが入れたコマンドは見つからない
4. plist を生成する
5. `launchctl bootout gui/$(id -u)/<label>`（失敗は無視）→ `launchctl bootstrap gui/$(id -u) <plist>`

## plist

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>SCRIPT_PATH</string>
        <string>--scheduled</string>
        <string>--apply</string>
    </array>
    <!-- どちらか一方。決まった時刻なら StartCalendarInterval（例: Hour 3 / Minute 0） -->
    <key>StartInterval</key><integer>3600</integer>
    <key>LowPriorityIO</key><true/>
    <key>Nice</key><integer>10</integer>
    <key>StandardOutPath</key><string>LOG_PATH</string>
    <key>StandardErrorPath</key><string>LOG_PATH</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key><string>LAUNCH_PATH</string>
    </dict>
</dict>
</plist>
```

- スリープ中の扱い: `StartInterval` はスリープ中の回を起こさない。`StartCalendarInterval` は復帰したときに、過ぎた回をまとめて1回だけ起こす
- ロード時にも1回動かしたいなら `RunAtLoad`。常駐させるもの（サーバー）は `KeepAlive` で、定期実行とは別物

## 確認と停止

| 目的 | コマンド |
|---|---|
| 1回だけ今すぐ起こす | `launchctl kickstart -k gui/$(id -u)/<label>` |
| 状態と直近の終了コード | `launchctl print gui/$(id -u)/<label>`（`last exit code` と `runs`） |
| 自作のジョブの一覧 | `launchctl list \| grep <接頭辞>`（2列目が直近の終了コード） |
| 止めて外す | `launchctl bootout gui/$(id -u)/<label>` → plist を `/usr/bin/trash` |

## Gotchas

- **Desktop・Documents・Downloads を触る処理は、権限を付けるまで動かない**。ターミナルから試すと通るので、試運転は必ず `kickstart` で launchd から起こす。付けるなら、そのジョブ専用の実行ファイルを作ってシステム設定の「フルディスクアクセス」に足す。`/bin/bash` や `/bin/zsh` に付けると、launchd から起こすすべてのスクリプトがディスク全体を読み書きできるようになる。会社の管理下の Mac では、この許可を付けられないことがある
- `launchctl load` / `unload` は古い形式。新しく書くなら `bootstrap` / `bootout` を使う
- plist を書き換えただけでは反映されない。`bootout` → `bootstrap` し直す
