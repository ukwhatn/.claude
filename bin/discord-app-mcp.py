#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp>=1.2,<2",
#   "websocket-client>=1.7",
# ]
# ///
"""起動中の Discord デスクトップアプリを、クライアント本体の通信経路で読み書きする MCP サーバ。

Bot を入れられない（が自分は参加している）サーバーのチャンネルを読む・書くための道具。
通信はすべて Discord.app 本体から出す（REST を自前で叩かない）ので、送り元とヘッダは
通常の操作と同じになる。self-bot（ユーザートークンで外から API を叩く）ではない。

しくみ:
- Discord.app を `--remote-debugging-port=<port>` 付きで起動しておく（この MCP が面倒を見る）。
- CDP の `Page.addScriptToEvaluateOnNewDocument` で、起動前に `webpackChunkdiscord_app` の
  push を乗っ取り、アプリ本体の webpack require を `window.__DMCP_WREQ` に確保する。
  ファイルは一切書き換えない。フックは CDP 接続が生きている間だけ有効なので、この MCP は
  接続を 1 本張り続ける。
- その require から Flux ストア（GuildStore / MessageStore / …）とアクション
  （MessageActions.sendMessage / editMessage / deleteMessage / …）を取り出して呼ぶ。

安全:
- 送信・編集・削除は、~/.claude/local/discord-app-mcp.json の write_allow に明示した
  チャンネルだけ通る（既定は空）。1 件ずつの確認は呼び出し側（Claude Code）が行う前提。
- トークンは renderer の外へ出さない。この MCP はトークンを読まない。

使い方:
  discord-app-mcp.py doctor   # CDP への接続・フック・モジュール解決を確認
  discord-app-mcp.py launch   # Discord.app を CDP 付きで起動し直す
  discord-app-mcp.py server   # stdio の MCP サーバとして動く
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import urllib.request

CONFIG = os.path.expanduser(
    os.environ.get("DISCORD_APP_MCP_CONFIG", "~/.claude/local/discord-app-mcp.json")
)
DEFAULT_PORT = 9333
BOOT_TIMEOUT = 40  # wreq 捕捉・ナビゲート完了までの最大待ち秒


class DiscordAppError(Exception):
    """接続・フック・解決の失敗。利用者に次の操作を示すメッセージを持つ。"""


def _config() -> dict:
    try:
        with open(CONFIG) as f:
            return json.load(f) or {}
    except FileNotFoundError:
        return {}


def _cdp_port() -> int:
    return int(_config().get("cdp_port", DEFAULT_PORT))


# --- 起動前フック（アプリ本体の require を確保する） ---

HOOK_JS = r"""
window.__DMCP_HOOK_RAN = (window.__DMCP_HOOK_RAN||0)+1;
try {(()=>{
  if (window.__DMCP_HOOKED) return; window.__DMCP_HOOKED = true;
  let store;
  const inject = (arr)=>{ try{ arr.push([[Symbol("dmcp")],{},(r)=>{window.__DMCP_WREQ=r;}]); }catch(e){ window.__DMCP_INJ_ERR=String(e);} };
  Object.defineProperty(window, "webpackChunkdiscord_app", {
    configurable:true,
    get(){ return store; },
    set(v){ store=v;
      const t=setInterval(()=>{ if(window.__DMCP_WREQ){clearInterval(t);return;}
        try{ if(v.push!==Array.prototype.push) inject(v); }catch(e){} }, 30);
      setTimeout(()=>clearInterval(t), 25000);
    },
  });
})();}catch(e){ window.__DMCP_HOOK_ERR=String(e); }
"""

# renderer に常駐させる「エージェント」。アプリ本体の require からモジュールを解決して
# window.__DMCP.api.* を生やす。再読み込み（Page.navigate）のたびに消えるので、
# ナビゲート後は Python 側が張り直す。
#
# 書き込み（send/edit/delete）は MessageActions を発火するが、その戻り値 Promise は
# 解決しないことがある（チャンネルが開いていないと内部キューで pending のまま。
# 20_survey.md 参照）ので await せず、nonce / id で MessageStore をポーリングして確定する。
# チャンネルを開く（Page.navigate）のは Python 側の open_channel が担う。
AGENT_JS = r"""
(() => {
  const V = "2";  // api の形を変えたら上げる（キャッシュを無効化して張り直す）
  const w = window.__DMCP_WREQ;
  if (!w) return { ok:false, reason:"no_wreq" };
  if (window.__DMCP && window.__DMCP.api && window.__DMCP.wreq === w && window.__DMCP.v === V) return { ok:true, cached:true };

  const get=(o,k)=>{try{return o[k]}catch{return undefined}};
  // どのキーにも関数を返す Proxy を除外する（ランダムキーが関数なら Proxy）
  const real=e=>{ try{ return e && (typeof e==="object"||typeof e==="function")
     && typeof e["__dmcp_"+Math.random().toString(36).slice(2)]!=="function"; }catch{return false} };
  const cached=Object.values(w.c).map(m=>get(m,"exports")).filter(Boolean);
  const exps=[]; for(const m of cached){ if(real(m))exps.push(m);
    for(const k of ["Z","ZP","default","A"]){const v=get(m,k); if(v&&real(v))exps.push(v);} }
  const fn=(e,k)=>typeof get(e,k)==="function";
  const byName=n=>exps.find(e=>{try{return fn(e,"getName")&&fn(e,"addChangeListener")&&e.getName()===n}catch{return false}});

  const S={};
  for(const n of ["GuildStore","MessageStore","UserStore","ChannelStore"]) S[n]=byName(n);
  const MessageActions=exps.find(e=>fn(e,"sendMessage")&&fn(e,"editMessage")&&fn(e,"deleteMessage"));

  const missing=[];
  for(const [k,v] of Object.entries({...S, MessageActions})) if(!v) missing.push(k);

  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const arr=cid=>{ try{ return S.MessageStore.getMessages(cid).toArray(); }catch{ return []; } };
  const fmtUser=u=>u?{id:u.id, name:(u.globalName||u.username), bot:!!u.bot}:null;
  const fmtMsg=m=>({ id:m.id, author:fmtUser(m.author), content:m.content||"",
     ts:(()=>{try{return new Date(m.timestamp).toISOString()}catch{return String(m.timestamp)}})(),
     edited:!!m.editedTimestamp, attachments:(m.attachments||[]).map(a=>({name:a.filename,url:a.url})),
     embeds:(m.embeds||[]).length, reactions:(m.reactions||[]).map(r=>({emoji:(r.emoji&&(r.emoji.name||r.emoji.id)),count:r.count})) });

  // 書き込みの確定待ち: pred(メッセージ配列) が真を返すまで最大 ~10 秒ポーリング
  const poll=async (cid, pred)=>{ for(let i=0;i<25;i++){ const v=pred(arr(cid)); if(v!==undefined&&v!==null&&v!==false) return v; await sleep(400); } return null; };

  const api = {
    whoami(){ const u=S.UserStore.getCurrentUser(); return fmtUser(u); },
    listGuilds(){ const g=S.GuildStore.getGuilds(); return Object.values(g).map(x=>({id:x.id,name:x.name})); },
    listChannels(gid){ const c=S.ChannelStore.getMutableGuildChannelsForGuild(gid)||{};
      return Object.values(c).filter(ch=>ch&&ch.guild_id===gid)
        .map(ch=>({id:ch.id,name:ch.name,type:ch.type,parent:ch.parent_id,topic:ch.topic||null,nsfw:!!ch.nsfw}))
        .sort((a,b)=>(a.type-b.type)||String(a.name).localeCompare(String(b.name))); },
    channelInfo(cid){ const ch=S.ChannelStore.getChannel(cid); return ch?{id:cid,name:ch.name,guild:ch.guild_id}:null; },
    // チャンネルは Python 側が開いた前提。開いた直後はロード中なので少し待つ
    async readMessages(cid, limit){
      const ch=S.ChannelStore.getChannel(cid); if(!ch) throw new Error("channel_not_found:"+cid);
      let a=arr(cid);
      for(let i=0;i<15 && a.length===0;i++){ await sleep(400); a=arr(cid); }
      return { channel:{id:cid,name:ch.name,guild:ch.guild_id}, count:a.length,
        messages:a.slice(-Math.max(1,Math.min(100,limit||30))).map(fmtMsg) };
    },
    async sendMessage(cid, content){
      const nonce=String(Date.now())+"000";
      try{ MessageActions.sendMessage(cid,{content, tts:false, invalidEmojis:[], validNonShortcutEmojis:[]}, true, {nonce}); }
      catch(e){ return { ok:false, error:String(e&&e.message||e) }; }
      const r=await poll(cid, ms=>{ const mm=ms.find(x=>x.nonce===nonce);
        if(!mm) return false;
        if(mm.state==="SENT") return {id:mm.id};
        if(mm.state==="SEND_FAILED") return {failed:true}; return false; });
      if(!r) return { ok:false, error:"timeout: SENT を確認できなかった" };
      if(r.failed) return { ok:false, error:"send_failed" };
      return { ok:true, id:r.id };
    },
    async editMessage(cid, mid, content){
      const before=(()=>{const m=S.MessageStore.getMessage(cid,mid); return m&&m.content;})();
      if(before===undefined) throw new Error("message_not_in_store:"+mid);
      try{ MessageActions.editMessage(cid, mid, {content}); }catch(e){ return { ok:false, error:String(e&&e.message||e) }; }
      const r=await poll(cid, ()=>{ const m=S.MessageStore.getMessage(cid,mid); return m&&m.content===content?{ok:true}:false; });
      const m=S.MessageStore.getMessage(cid,mid);
      return { ok:!!r, content:m&&m.content };
    },
    async deleteMessage(cid, mid){
      if(!S.MessageStore.getMessage(cid,mid)) throw new Error("message_not_in_store:"+mid);
      try{ MessageActions.deleteMessage(cid, mid); }catch(e){ return { ok:false, error:String(e&&e.message||e) }; }
      const r=await poll(cid, ()=> !S.MessageStore.getMessage(cid,mid) ? {ok:true} : false);
      return { ok:!!r };
    },
  };
  window.__DMCP={ v:V, wreq:w, S, MessageActions, api, missing };
  return { ok: missing.length===0, missing };
})()
"""


# --- CDP クライアント（同期・接続を 1 本保持） ---


class CDP:
    """Discord.app の page ターゲットへ 1 本の websocket を張り、Runtime.evaluate を同期で呼ぶ。

    フック（addScriptToEvaluateOnNewDocument）は接続が生きている間だけ有効なので、
    この接続は server が動く間ずっと保つ。
    """

    def __init__(self, port: int):
        self.port = port
        self._ws = None
        self._id = 0
        self._lock = threading.Lock()

    def _page_ws_url(self) -> str:
        try:
            targets = json.load(
                urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=5)
            )
        except OSError as e:
            raise DiscordAppError(
                f"CDP ({self.port}) に繋がらない。`discord-app-mcp.py launch` で "
                f"Discord.app を --remote-debugging-port={self.port} 付きで起動する（{e}）"
            )
        pages = [t for t in targets if t.get("type") == "page" and "discord.com" in t.get("url", "")]
        if not pages:
            raise DiscordAppError("discord.com の page ターゲットが無い。Discord.app にログインしているか確認する")
        # /channels を開いているものを優先
        pages.sort(key=lambda t: ("/channels" not in t.get("url", ""), t.get("url", "")))
        return pages[0]["webSocketDebuggerUrl"]

    def connect(self) -> None:
        import websocket  # websocket-client

        if self._ws is not None:
            return
        # suppress_origin: CDP は Origin ヘッダ付きの WebSocket を 403 で弾く（devtools 自身は付けない）
        ws = websocket.create_connection(
            self._page_ws_url(), max_size=2 ** 27, timeout=60, suppress_origin=True
        )
        self._ws = ws
        self._cmd("Page.enable")
        self._cmd("Runtime.enable")
        # 起動前フックを登録（次の読み込みから効く）。接続はこのまま保つ
        self._cmd("Page.addScriptToEvaluateOnNewDocument", {"source": HOOK_JS})

    def _cmd(self, method: str, params: dict | None = None) -> dict:
        import websocket

        if self._ws is None:
            raise DiscordAppError("CDP 未接続")
        self._id += 1
        mid = self._id
        self._ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            try:
                msg = json.loads(self._ws.recv())
            except websocket.WebSocketConnectionClosedException:
                self._ws = None
                raise DiscordAppError("CDP 接続が切れた。Discord.app が落ちた可能性がある")
            if msg.get("id") == mid:
                if "error" in msg:
                    raise DiscordAppError(f"CDP {method}: {msg['error']}")
                return msg["result"]

    def evaluate(self, expression: str, await_promise: bool = True):
        res = self._cmd(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": await_promise, "returnByValue": True},
        )
        if "exceptionDetails" in res:
            exc = res["exceptionDetails"]
            desc = (exc.get("exception") or {}).get("description") or exc.get("text")
            raise DiscordAppError(f"renderer 例外: {str(desc)[:300]}")
        return res["result"].get("value")

    def wreq_present(self) -> bool:
        return bool(self.evaluate("!!window.__DMCP_WREQ", await_promise=False))

    def _wait_wreq(self, timeout: float) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            time.sleep(1.0)
            try:
                if self.wreq_present():
                    return
            except DiscordAppError:
                pass  # ナビゲート直後は一時的に評価できないことがある
        raise DiscordAppError("webpack require を確保できなかった（Discord.app が読み込み中か未ログイン）")

    def _build_agent(self) -> None:
        res = self.evaluate(AGENT_JS)
        if not res or not res.get("ok"):
            raise DiscordAppError(f"モジュール解決に失敗した（未解決: {(res or {}).get('missing')}）")

    def ensure_ready(self) -> None:
        """接続を張り、wreq を確保し、エージェントを張る。未確保なら 1 度だけ再読み込みする。"""
        with self._lock:
            self.connect()
            if not self.wreq_present():
                self._cmd("Page.reload", {})
                self._wait_wreq(BOOT_TIMEOUT)
            self._build_agent()

    def open_channel(self, channel_id: str) -> dict:
        """対象チャンネルを Page.navigate で開く（起動前フックが新ドキュメントで再発火し wreq を取り直す）。

        チャンネルを開かないと MessageStore は空で、書き込みも反映されない（20_survey.md）。
        既にそのチャンネルを開いていればナビゲートしない。戻り値は channelInfo。
        """
        self.ensure_ready()
        info = self.call_api("channelInfo", channel_id)
        if not info:
            raise DiscordAppError(f"チャンネル {channel_id} が見つからない（未参加か id 誤り）")
        gid = info.get("guild") or "@me"
        path = f"/channels/{gid}/{channel_id}"
        with self._lock:
            if self.evaluate("location.pathname", await_promise=False) == path:
                return info
            # ナビゲート前の window に目印を置く。新ドキュメントでは消える
            self.evaluate("window.__DMCP_NAV=1", await_promise=False)
            self._cmd("Page.navigate", {"url": f"https://discord.com{path}"})
            deadline = time.monotonic() + BOOT_TIMEOUT
            while time.monotonic() < deadline:
                time.sleep(1.0)
                try:
                    gone = not self.evaluate("!!window.__DMCP_NAV", await_promise=False)
                    if gone and self.wreq_present():
                        break
                except DiscordAppError:
                    pass
            else:
                raise DiscordAppError(f"チャンネル {channel_id} を開けなかった")
            self._build_agent()
        # ナビゲート直後はストアが水和中。チャンネルが出るまで待つ
        for _ in range(20):
            if self._invoke("channelInfo", channel_id):
                return info
            time.sleep(0.5)
        raise DiscordAppError(f"チャンネル {channel_id} のストアが水和しなかった")

    def call_api(self, method: str, *args):
        """window.__DMCP.api.<method>(...args) を呼ぶ。未準備なら張り直す。"""
        self.ensure_ready()
        return self._invoke(method, *args)

    def call_on_channel(self, channel_id: str, method: str, *args):
        """チャンネルを開いてから api.<method>(channel_id, ...args) を呼ぶ。"""
        self.open_channel(channel_id)
        return self._invoke(method, channel_id, *args)

    def _invoke(self, method: str, *args):
        payload = json.dumps(list(args))
        expr = (
            "(async()=>{try{const a=" + payload + ";"
            "return {ok:true, value: await window.__DMCP.api['" + method + "'](...a)};}"
            "catch(e){return {ok:false, error:String(e&&e.message||e)};}})()"
        )
        res = self.evaluate(expr)
        if not res:
            raise DiscordAppError(f"api.{method}: 応答なし")
        if not res.get("ok"):
            raise DiscordAppError(f"api.{method}: {res.get('error')}")
        return res.get("value")


# --- 書き込みゲート ---


def _write_allowed(channel_id: str) -> bool:
    allow = _config().get("write_allow")
    if allow == "*":
        return True
    return isinstance(allow, list) and channel_id in allow


def _require_write_allowed(channel_id: str) -> None:
    if not _write_allowed(channel_id):
        raise DiscordAppError(
            f"チャンネル {channel_id} への書き込みは許可されていない。"
            f"{CONFIG} の write_allow に channel id を足すと通る"
        )


# --- Discord.app の起動 ---


def _cdp_reachable(port: int) -> bool:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3).read()
        return True
    except OSError:
        return False


def cmd_launch() -> int:
    port = _cdp_port()
    if _cdp_reachable(port):
        print(f"CDP ({port}): 既に待ち受けている")
        return 0
    subprocess.run(["osascript", "-e", 'quit app "Discord"'], capture_output=True)
    for _ in range(15):
        r = subprocess.run(["pgrep", "-f", "Discord.app/Contents/MacOS/Discord"], capture_output=True)
        if r.returncode != 0:
            break
        time.sleep(1)
    # Origin は接続側（suppress_origin）で落とすので --remote-allow-origins は不要
    subprocess.run(["open", "-a", "Discord", "--args", f"--remote-debugging-port={port}"])
    for _ in range(40):
        if _cdp_reachable(port):
            print(f"CDP ({port}): 起動した")
            return 0
        time.sleep(1)
    print(f"CDP ({port}): 起動を確認できなかった")
    return 1


# --- MCP サーバ ---


def build_server(cdp: "CDP"):
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("discord-app")

    @mcp.tool()
    def discord_whoami() -> dict:
        """ログイン中の自分（id・表示名）を返す。接続とフックの疎通確認を兼ねる。"""
        return cdp.call_api("whoami")

    @mcp.tool()
    def discord_list_guilds() -> list:
        """参加しているサーバー（id・name）の一覧を返す。"""
        return cdp.call_api("listGuilds")

    @mcp.tool()
    def discord_list_channels(guild_id: str) -> list:
        """サーバー内のチャンネル（id・name・type・parent・topic）の一覧を返す。type: 0=テキスト, 2=ボイス, 4=カテゴリ, 5=アナウンス。"""
        return cdp.call_api("listChannels", guild_id)

    @mcp.tool()
    def discord_read_messages(channel_id: str, limit: int = 30) -> dict:
        """チャンネルの最新メッセージを返す（最大100件）。対象チャンネルを開いて（アプリがそのチャンネルに切り替わる）履歴を読み込む。
        返り値: channel と messages（id・author・content・ts・attachments・reactions）。"""
        return cdp.call_on_channel(channel_id, "readMessages", limit)

    @mcp.tool()
    def discord_send_message(channel_id: str, content: str) -> dict:
        """チャンネルにメッセージを送る。write_allow に入れたチャンネルだけ通る。
        送信は外に出る操作なので、呼ぶ前に送り先と本文を利用者に確認すること。"""
        _require_write_allowed(channel_id)
        return cdp.call_on_channel(channel_id, "sendMessage", content)

    @mcp.tool()
    def discord_edit_message(channel_id: str, message_id: str, content: str) -> dict:
        """自分のメッセージの本文を書き換える。write_allow に入れたチャンネルだけ通る。"""
        _require_write_allowed(channel_id)
        return cdp.call_on_channel(channel_id, "editMessage", message_id, content)

    @mcp.tool()
    def discord_delete_message(channel_id: str, message_id: str) -> dict:
        """メッセージを削除する。write_allow に入れたチャンネルだけ通る。"""
        _require_write_allowed(channel_id)
        return cdp.call_on_channel(channel_id, "deleteMessage", message_id)

    return mcp


def cmd_doctor() -> int:
    port = _cdp_port()
    print(f"CDP port: {port}  reachable={_cdp_reachable(port)}")
    if not _cdp_reachable(port):
        print("NG: `discord-app-mcp.py launch` で Discord.app を CDP 付きで起動する")
        return 1
    cdp = CDP(port)
    try:
        cdp.ensure_ready()
        me = cdp.call_api("whoami")
        guilds = cdp.call_api("listGuilds")
        print(f"OK: user={me.get('name')} ({me.get('id')})  guilds={len(guilds)}")
        return 0
    except DiscordAppError as e:
        print(f"NG: {e}")
        return 1


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "server"
    if cmd == "doctor":
        return cmd_doctor()
    if cmd == "launch":
        return cmd_launch()
    if cmd == "server":
        cdp = CDP(_cdp_port())
        build_server(cdp).run()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
