#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp>=1.2,<2",
#   "pycryptodome>=3.20",
#   "ccl_chromium_reader @ git+https://github.com/cclgroupltd/ccl_chromium_reader@ad37443541dd91dac3ac1fb2eecaeb8693f36815",
# ]
# ///
"""ログイン中の Slack デスクトップアプリのセッションを使い、MCP・アプリ連携を繋げない
ワークスペース（guest 権限など）を読み書きする MCP サーバ。

セッションはアプリのディスク上の保存領域から都度読む（静的トークンを持たない）ので、
アプリがログインし続けている限り、手でトークンを入れ直す必要がない。

- xoxc token と ワークスペース一覧: Local Storage(leveldb) の localConfig_v2 の teams
  （暗号化されていないので keychain 不要。ccl_chromium_reader で読む）
- d cookie: Cookies（Chromium v10 暗号。鍵は macOS の keychain "Slack Safe Storage"）。
  初回は keychain のアクセス許可ダイアログが出る（GUI セッションでのみ読める）

投稿は既定で無効。~/.claude/local/slack-app-mcp.json の post_allow に許可するチャンネルを
明示したときだけ通す。

使い方:
  slack-app-mcp.py doctor            # セッションの取り出しと疎通（auth.test）をワークスペースごとに確認
  slack-app-mcp.py server            # stdio の MCP サーバとして動く（MCP クライアントから起動）
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

SLACK_SUPPORT = os.path.expanduser("~/Library/Application Support/Slack")
COOKIES_DB = os.path.join(SLACK_SUPPORT, "Cookies")
LOCAL_STORAGE = os.path.join(SLACK_SUPPORT, "Local Storage", "leveldb")
KEYCHAIN_SERVICE = "Slack Safe Storage"
CONFIG = os.path.expanduser(
    os.environ.get("SLACK_APP_MCP_CONFIG", "~/.claude/local/slack-app-mcp.json")
)
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Slack/4.51.191 Chrome/150.0.7871.224 Electron/43.4.0 "
    "Safari/537.36 Slack_SSB/4.51.191"
)


class SlackAuthError(Exception):
    """セッションの取り出しに失敗したときに投げる。利用者に次の操作を示すメッセージを持つ。"""


def _keychain_password() -> str:
    """keychain から Slack Safe Storage の鍵を取る。許可が無ければ次の操作を添えて投げる。"""
    r = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    pw = r.stdout.strip()
    if r.returncode != 0 or not pw:
        raise SlackAuthError(
            "keychain の 'Slack Safe Storage' を読めなかった"
            f"（security 終了コード {r.returncode}）。"
            "初回は許可ダイアログで『常に許可』を押す必要がある。"
            "手元で `security find-generic-password -s 'Slack Safe Storage' -w` を一度実行して許可する"
        )
    return pw


def _decrypt_cookie(encrypted: bytes, key: bytes) -> str | None:
    """Chromium v10/v11（macOS）の暗号化 cookie を復号する。xoxd- で始まる値だけ返す。"""
    from Crypto.Cipher import AES

    if encrypted[:3] not in (b"v10", b"v11"):
        return None
    cipher = AES.new(key, AES.MODE_CBC, b" " * 16)
    plain = cipher.decrypt(encrypted[3:])
    pad = plain[-1]
    if 1 <= pad <= 16:
        plain = plain[:-pad]
    # Chrome 130+ は値の前に 32byte の domain hash を付ける。両方を試す
    for candidate in (plain, plain[32:]):
        try:
            text = candidate.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if text.startswith("xoxd-"):
            return text
    return None


def _read_d_cookie() -> str:
    """Slack アプリの Cookies から d cookie（xoxd）を復号して返す。"""
    if not os.path.exists(COOKIES_DB):
        raise SlackAuthError(f"{COOKIES_DB} が無い。Slack アプリにログインしているか確認する")
    key = hashlib.pbkdf2_hmac("sha1", _keychain_password().encode(), b"saltysalt", 1003, 16)
    # アプリが開いている間はロックされるので、コピーを読む
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "Cookies")
        shutil.copy2(COOKIES_DB, copy)
        con = sqlite3.connect(copy)
        try:
            rows = con.execute(
                "select encrypted_value from cookies "
                "where name='d' and host_key like '%slack.com%'"
            ).fetchall()
        finally:
            con.close()
    for (enc,) in rows:
        value = _decrypt_cookie(enc, key)
        if value:
            return value
    raise SlackAuthError(
        "d cookie を復号できなかった。keychain の許可が別のアプリ更新で外れた可能性がある。"
        "Slack アプリに入り直すか、許可をやり直す"
    )


def read_local_config() -> dict:
    """Local Storage(leveldb) の localConfig_v2 を読んで返す。teams に token を含む。

    アプリがロックを持つので leveldb をコピーしてから読む。
    """
    from ccl_chromium_reader import ccl_chromium_localstorage as ls

    if not os.path.isdir(LOCAL_STORAGE):
        raise SlackAuthError(f"{LOCAL_STORAGE} が無い。Slack アプリにログインしているか確認する")
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "leveldb")
        shutil.copytree(LOCAL_STORAGE, copy)
        db = ls.LocalStoreDb(pathlib.Path(copy))
        try:
            value = None
            for rec in db.iter_all_records():
                if rec.script_key == "localConfig_v2" and "app.slack.com" in str(rec.storage_key):
                    value = rec.value
        finally:
            db.close()
    if not value:
        raise SlackAuthError("localConfig_v2 を Local Storage から読めなかった")
    return json.loads(value)


def _teams_to_workspaces(config: dict) -> list[dict]:
    out = []
    for team_id, t in (config.get("teams") or {}).items():
        out.append(
            {
                "team_id": team_id,
                "domain": t.get("domain"),
                "name": t.get("name"),
                "url": t.get("url"),
            }
        )
    return out


def _resolve_domain(workspace: str, spaces: list[dict]) -> dict:
    """domain か team ID か名前で 1 件に決める。"""
    for ws in spaces:
        if workspace in (ws["domain"], ws["team_id"]):
            return ws
    matches = [ws for ws in spaces if ws["name"] and workspace.lower() in ws["name"].lower()]
    if len(matches) == 1:
        return matches[0]
    raise SlackAuthError(
        f"ワークスペース '{workspace}' を 1 件に決められない。"
        f"候補: {', '.join(w['domain'] or w['team_id'] for w in spaces)}"
    )


class Session:
    """localConfig_v2 のトークンと d cookie を持ち、Slack Web API を呼ぶ。

    どちらもアプリの保存領域から読んでキャッシュする。auth 失敗時は読み直して 1 度だけ再試行する。
    """

    def __init__(self) -> None:
        self._d_cookie: str | None = None
        self._config: dict | None = None

    @property
    def config(self) -> dict:
        if self._config is None:
            self._config = read_local_config()
        return self._config

    @property
    def d_cookie(self) -> str:
        if self._d_cookie is None:
            self._d_cookie = _read_d_cookie()
        return self._d_cookie

    @property
    def workspaces(self) -> list[dict]:
        return _teams_to_workspaces(self.config)

    def refresh(self) -> None:
        self._config = None
        self._d_cookie = None

    def resolve(self, workspace: str) -> dict:
        return _resolve_domain(workspace, self.workspaces)

    def token(self, domain: str) -> str:
        for team_id, t in (self.config.get("teams") or {}).items():
            if t.get("domain") == domain and t.get("token"):
                return t["token"]
        raise SlackAuthError(f"localConfig_v2 に {domain} の token が無い")

    def call(self, domain: str, method: str, _retried: bool = False, **params) -> dict:
        """Slack Web API を呼ぶ。token は本文に、d cookie はヘッダに載せる。"""
        data = {k: v for k, v in params.items() if v is not None}
        data["token"] = self.token(domain)
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(
            f"https://{domain}.slack.com/api/{method}",
            data=body,
            headers={
                "User-Agent": USER_AGENT,
                "Cookie": f"d={self.d_cookie}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if not result.get("ok"):
            # トークンの失効はアプリが更新しているので、読み直して 1 度だけ再試行する
            if result.get("error") in ("invalid_auth", "not_authed", "token_expired") and not _retried:
                self.refresh()
                return self.call(domain, method, _retried=True, **params)
            raise SlackAuthError(f"Slack API {method} が失敗: {result.get('error')}")
        return result


# --- メッセージの整形（slack_browser.py と同じ ts/author/text/replies/link の形） ---


def _user_names(session: Session, domain: str, ids: set[str]) -> dict[str, str]:
    names: dict[str, str] = {}
    for uid in ids:
        if not uid:
            continue
        try:
            info = session.call(domain, "users.info", user=uid)
            u = info["user"]
            names[uid] = u.get("real_name") or u.get("name") or uid
        except SlackAuthError:
            names[uid] = uid
    return names


def _format_messages(session: Session, domain: str, team_id: str, channel: str, msgs: list) -> list[dict]:
    ids = {m.get("user") or m.get("bot_id") for m in msgs}
    names = _user_names(session, domain, {i for i in ids if i and i.startswith("U")})
    out = []
    for m in msgs:
        ts = m.get("ts", "")
        uid = m.get("user") or ""
        link = (
            f"https://{domain}.slack.com/archives/{channel}/p{ts.replace('.', '')}"
            if ts
            else None
        )
        out.append(
            {
                "ts": ts,
                "author": names.get(uid, uid or m.get("username") or m.get("bot_id") or ""),
                "text": m.get("text", ""),
                "replies": m.get("reply_count", 0),
                "link": link,
            }
        )
    return out


# --- 投稿ゲート ---


def _post_allowed(domain: str, channel: str) -> bool:
    try:
        with open(CONFIG) as f:
            allow = (json.load(f) or {}).get("post_allow") or {}
    except FileNotFoundError:
        return False
    if allow == "*":
        return True
    chans = allow.get(domain)
    return chans == "*" or (isinstance(chans, list) and channel in chans)


# --- MCP サーバ ---


def build_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("slack-app")
    session = Session()

    @mcp.tool()
    def slack_list_workspaces() -> list[dict]:
        """ログイン中の Slack ワークスペース一覧（team ID・domain・name）を返す。"""
        return session.workspaces

    @mcp.tool()
    def slack_list_channels(workspace: str, types: str = "public_channel,private_channel") -> list[dict]:
        """自分が入っているチャンネル・DM の一覧（id・name・is_member）を返す。workspace は domain か team ID。"""
        ws = session.resolve(workspace)
        r = session.call(
            ws["domain"], "users.conversations", types=types, limit=1000, exclude_archived="true"
        )
        return [
            {"id": c["id"], "name": c.get("name") or c.get("user"), "is_member": c.get("is_member", True)}
            for c in r.get("channels", [])
        ]

    @mcp.tool()
    def slack_history(workspace: str, channel: str, limit: int = 30) -> list[dict]:
        """チャンネルの最新メッセージを ts/author/text/replies/link の形で返す。"""
        ws = session.resolve(workspace)
        r = session.call(ws["domain"], "conversations.history", channel=channel, limit=limit)
        return _format_messages(session, ws["domain"], ws["team_id"], channel, r.get("messages", []))

    @mcp.tool()
    def slack_thread(permalink: str) -> list[dict]:
        """スレッドのパーマリンクを渡すと、親＋返信を全件返す。"""
        m = re.match(
            r"https://([\w-]+)\.slack\.com/archives/(\w+)/p(\d{10})(\d{6})", permalink
        )
        if not m:
            raise SlackAuthError(f"パーマリンクとして読めない: {permalink}")
        domain, channel, ts = m.group(1), m.group(2), f"{m.group(3)}.{m.group(4)}"
        q = re.search(r"thread_ts=([\d.]+)", permalink)
        thread_ts = q.group(1) if q else ts
        ws = session.resolve(domain)
        r = session.call(ws["domain"], "conversations.replies", channel=channel, ts=thread_ts, limit=1000)
        return _format_messages(session, ws["domain"], ws["team_id"], channel, r.get("messages", []))

    @mcp.tool()
    def slack_search(workspace: str, query: str, limit: int = 20) -> list[dict]:
        """Slack の検索構文（in:#ch from:@user after:YYYY-MM-DD など）で検索する。"""
        ws = session.resolve(workspace)
        r = session.call(ws["domain"], "search.messages", query=query, count=limit)
        matches = (r.get("messages") or {}).get("matches", [])
        return [
            {
                "ts": m.get("ts", ""),
                "author": m.get("username") or (m.get("user") or ""),
                "text": m.get("text", ""),
                "channel": (m.get("channel") or {}).get("name"),
                "link": m.get("permalink"),
            }
            for m in matches
        ]

    @mcp.tool()
    def slack_post(workspace: str, channel: str, text: str, thread_ts: str | None = None) -> dict:
        """チャンネルかスレッドに投稿する。post_allow で明示許可したチャンネルだけ通る。"""
        ws = session.resolve(workspace)
        if not _post_allowed(ws["domain"], channel):
            raise SlackAuthError(
                f"{ws['domain']} の {channel} への投稿は許可されていない。"
                f"{CONFIG} の post_allow に channel を足すと通る"
            )
        r = session.call(
            ws["domain"], "chat.postMessage", channel=channel, text=text, thread_ts=thread_ts
        )
        return {"ok": True, "ts": r.get("ts"), "channel": r.get("channel")}

    return mcp


def cmd_diag() -> int:
    """d cookie 取得のどの段で落ちるかを、実値を出さずに表示する。"""
    r = subprocess.run(
        ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    pw = r.stdout.strip()
    print(f"keychain: rc={r.returncode} pw_len={len(pw)} err={r.stderr.strip()[:60]!r}")
    if not pw:
        return 1
    key = hashlib.pbkdf2_hmac("sha1", pw.encode(), b"saltysalt", 1003, 16)
    if not os.path.exists(COOKIES_DB):
        print(f"cookies db: 無い ({COOKIES_DB})")
        return 1
    from Crypto.Cipher import AES

    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "Cookies")
        shutil.copy2(COOKIES_DB, copy)
        con = sqlite3.connect(copy)
        try:
            rows = con.execute(
                "select host_key, length(encrypted_value) el, encrypted_value "
                "from cookies where name='d' and host_key like '%slack.com%'"
            ).fetchall()
        finally:
            con.close()
    print(f"d rows: {len(rows)}")
    for host, el, enc in rows:
        prefix = bytes(enc[:3])
        note = "prefix 不一致"
        if prefix in (b"v10", b"v11"):
            cipher = AES.new(key, AES.MODE_CBC, b" " * 16)
            plain = cipher.decrypt(enc[3:])
            pad = plain[-1]
            stripped = plain[:-pad] if 1 <= pad <= 16 else plain
            cands = []
            for off, cand in (("0", stripped), ("32", stripped[32:])):
                try:
                    s = cand.decode("utf-8")
                    cands.append(f"off{off}:len{len(s)}:head{s[:5]!r}")
                except UnicodeDecodeError:
                    cands.append(f"off{off}:decode不可")
            note = f"pad={pad} " + " ".join(cands)
        print(f"  host={host} enc_len={el} prefix={prefix!r} {note}")
    return 0


def cmd_doctor() -> int:
    """セッションの取り出しと疎通をワークスペースごとに確認する（トークンの実値は出さない）。"""
    session = Session()
    try:
        d = session.d_cookie
    except SlackAuthError as e:
        print(f"d cookie: NG -- {e}")
        return 1
    print(f"d cookie: OK ({d[:8]}…[{len(d)} chars])")
    rc = 0
    for ws in session.workspaces:
        domain = ws["domain"]
        try:
            token = session.token(domain)
            who = session.call(domain, "auth.test")
            print(
                f"{domain}: OK  token={token[:10]}…  user={who.get('user')}  "
                f"team={who.get('team')}"
            )
        except SlackAuthError as e:
            print(f"{domain}: NG -- {e}")
            rc = 1
    return rc


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "server"
    if cmd == "doctor":
        return cmd_doctor()
    if cmd == "diag":
        return cmd_diag()
    if cmd == "server":
        build_server().run()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
