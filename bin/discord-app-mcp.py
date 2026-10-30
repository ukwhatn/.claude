#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp>=1.2,<2",
#   "websocket-client>=1.7",
# ]
# ///
"""MCP 専用に起動した Discord デスクトップアプリを、クライアント本体の通信経路で読み書きする MCP サーバ。

Bot を入れられない（が自分は参加している）サーバーのチャンネルを読む・書くための道具。
通信はすべて Discord.app 本体の関数から出す（REST を自前で叩かない）ので、送り元とヘッダは
通常の操作と同じになる。self-bot（ユーザートークンで外から API を叩く）ではない。

しくみ:
- 普段使いの Discord とは別に、MCP 専用のインスタンスを起動する（`launch`）。Discord 本体の
  `--multi-instance` と環境変数 `DISCORD_USER_DATA_DIR` で、別のデータ置き場・別ウィンドウとして
  同時に動く。CDP のポート（`--remote-debugging-port`）はこちらにだけ開く。初回だけログインが要る。
- CDP で renderer に入り、`webpackChunkdiscord_app` に chunk を 1 つ push して webpack require を
  受け取る。ページにはランタイムが複数あるので、モジュールキャッシュが最大のもの（アプリ本体）を使う。
- その require から Flux ストア（GuildStore / MessageStore / …）と MessageActions
  （fetchMessages / sendMessage / editMessage / deleteMessage）を取り出して呼ぶ。履歴は
  fetchMessages（UI がスクロールで古い履歴を読むのと同じ関数）でストアへ読み込んでから返すので、
  チャンネルを開かない（専用ウィンドウの表示も変えない）。

安全:
- 送信・編集・削除は、~/.claude/local/discord-app-mcp.json の write_allow に明示した
  チャンネルだけ通る（既定は空）。1 件ずつの確認は呼び出し側（Claude Code）が行う前提。
- トークンは renderer の外へ出さない。この MCP はトークンを読まない。

使い方:
  discord-app-mcp.py doctor                 # CDP への接続・モジュール解決を確認
  discord-app-mcp.py launch [--dry-run]     # 専用インスタンスを起動する（普段使いには触れない）
  discord-app-mcp.py launch --at-login      # ログイン時用。普段使いの起動を待ってから起動する
  discord-app-mcp.py server                 # stdio の MCP サーバとして動く
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
DEFAULT_PORT = 9334
DEFAULT_INSTANCE_DIR = "~/Library/Application Support/discord-mcp-instance"
DISCORD_BIN = "/Applications/Discord.app/Contents/MacOS/Discord"
BOOT_TIMEOUT = 60  # 起動直後にアプリ本体のモジュールが揃うまでの最大待ち秒
MAIN_WAIT_AT_LOGIN = 120  # --at-login で普段使いの起動を待つ最大秒


class DiscordAppError(Exception):
    """接続・解決・操作の失敗。利用者に次の操作を示すメッセージを持つ。"""


def _config() -> dict:
    try:
        with open(CONFIG) as f:
            return json.load(f) or {}
    except FileNotFoundError:
        return {}


def _cdp_port() -> int:
    return int(_config().get("cdp_port", DEFAULT_PORT))


def _instance_dir() -> str:
    return os.path.expanduser(_config().get("instance_dir", DEFAULT_INSTANCE_DIR))


# renderer に置く「エージェント」。アプリ本体の require からモジュールを解決して
# window.__DMCP.api.* を生やす。ページの再読み込みで消えるので、そのときは張り直す。
#
# 書き込み（send/edit/delete）の戻り値 Promise は解決しないことがある（ストアに未読込の
# チャンネルでは内部キューで pending のまま）ので await せず、ストアをポーリングして確定する。
AGENT_JS = r"""
(() => {
  const V = "3";  // api の形を変えたら上げる（古いエージェントを張り直させる）
  if (window.__DMCP && window.__DMCP.v === V) return { ok:true, cached:true };
  const chunks = window.webpackChunkdiscord_app;
  if (!Array.isArray(chunks)) return { ok:false, missing:["webpackChunkdiscord_app"] };
  // push すると、chunk 配列を共有する全ランタイムがコールバックを呼ぶ。キャッシュ最大がアプリ本体
  const reqs = []; chunks.push([[Symbol("dmcp")], {}, r => { reqs.push(r); }]);
  const size = r => { try { return Object.keys(r.c || {}).length; } catch { return 0; } };
  const w = reqs.sort((a, b) => size(b) - size(a))[0];
  if (!w || size(w) < 1000) return { ok:false, missing:["app webpack runtime (loading?)"] };

  const get=(o,k)=>{try{return o[k]}catch{return undefined}};
  // どのキーにも関数を返す Proxy を除外する（ランダムキーが関数なら Proxy）
  const real=e=>{ try{ return e && (typeof e==="object"||typeof e==="function")
     && typeof e["__dmcp_"+Math.random().toString(36).slice(2)]!=="function"; }catch{return false} };
  const exps=[];
  for(const m of Object.values(w.c)){ const e=get(m,"exports"); if(!e) continue;
    if(real(e)) exps.push(e);
    let ks=[]; try{ ks=Object.keys(e); }catch{}
    for(const k of ks){ const v=get(e,k); if(v&&real(v)) exps.push(v); } }
  const fn=(e,k)=>typeof get(e,k)==="function";
  const byName=n=>exps.find(e=>{try{return fn(e,"getName")&&fn(e,"addChangeListener")&&e.getName()===n}catch{return false}});

  const S={};
  for(const n of ["GuildStore","MessageStore","UserStore","ChannelStore"]) S[n]=byName(n);
  const MA=exps.find(e=>fn(e,"fetchMessages")&&fn(e,"sendMessage")&&fn(e,"editMessage")&&fn(e,"deleteMessage"));
  const missing=[];
  for(const [k,v] of Object.entries({...S, MessageActions:MA})) if(!v) missing.push(k);
  if(missing.length) return { ok:false, missing };
  // 起動直後はモジュールが揃っても gateway の READY 前でストアが空
  if(!S.UserStore.getCurrentUser()) return { ok:false, missing:["READY（ログイン前か接続中）"] };

  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const store=cid=>S.MessageStore.getMessages(cid);
  const arr=cid=>{ try{ return store(cid).toArray(); }catch{ return []; } };
  const older=(a,b)=>BigInt(a)<BigInt(b);
  const fmtUser=u=>u?{id:u.id, name:(u.globalName||u.username), bot:!!u.bot}:null;
  const fmtMsg=m=>({ id:m.id, author:fmtUser(m.author), content:m.content||"",
     ts:(()=>{try{return new Date(m.timestamp).toISOString()}catch{return String(m.timestamp)}})(),
     edited:!!m.editedTimestamp, reply_to:(m.messageReference&&m.messageReference.message_id)||null,
     attachments:(m.attachments||[]).map(a=>({name:a.filename,url:a.url})),
     embeds:(m.embeds||[]).length, reactions:(m.reactions||[]).map(r=>({emoji:(r.emoji&&(r.emoji.name||r.emoji.id)),count:r.count})) });
  const channelOf=cid=>{ const ch=S.ChannelStore.getChannel(cid); if(!ch) throw new Error("channel_not_found: "+cid+"（未参加か id 誤り）"); return ch; };
  // fetchMessages は REST の完了で解決する Promise を返す（キャッシュで足りたときは undefined）
  const fetch_=async (cid, before, limit)=>{
    const p=MA.fetchMessages({channelId:cid, before:before||undefined, limit});
    await Promise.race([Promise.resolve(p), sleep(10000)]); await sleep(150);
  };
  const ensureLoaded=async cid=>{ channelOf(cid); if(!store(cid).ready) await fetch_(cid, null, 50); };
  // pred(メッセージ配列) が値を返すまで最大 ~10 秒ポーリング
  const poll=async (cid, pred)=>{ for(let i=0;i<25;i++){ const v=pred(arr(cid)); if(v) return v; await sleep(400); } return null; };

  const api = {
    whoami(){ return fmtUser(S.UserStore.getCurrentUser()); },
    listGuilds(){ return Object.values(S.GuildStore.getGuilds()).map(x=>({id:x.id,name:x.name})); },
    listChannels(gid){ const c=S.ChannelStore.getMutableGuildChannelsForGuild(gid)||{};
      return Object.values(c).filter(ch=>ch&&ch.guild_id===gid)
        .map(ch=>({id:ch.id,name:ch.name,type:ch.type,parent:ch.parent_id,topic:ch.topic||null,nsfw:!!ch.nsfw}))
        .sort((a,b)=>(a.type-b.type)||String(a.name).localeCompare(String(b.name))); },
    // before を省くと最新、指定するとその id より古い側を limit 件（古い順）で返す
    async readMessages(cid, limit, before){
      const ch=channelOf(cid); limit=Math.max(1,Math.min(100,limit||30));
      await ensureLoaded(cid);
      const pick=()=>{ let a=arr(cid); if(before) a=a.filter(m=>older(m.id,before)); return a; };
      let a=pick();
      // 足りなければ、手元の最古より前を読み込む（UI のスクロールと同じ）
      for(let i=0;i<4 && a.length<limit && store(cid).hasMoreBefore!==false;i++){
        const oldest=a.length? a[0].id : before;
        const n0=arr(cid).length;
        await fetch_(cid, oldest, 100);
        a=pick(); if(arr(cid).length===n0) break;
      }
      const page=a.slice(-limit);
      return { channel:{id:cid,name:ch.name,guild:ch.guild_id}, count:page.length,
        next_before: page.length? page[0].id : null,
        has_more_before: a.length>page.length || store(cid).hasMoreBefore!==false,
        messages: page.map(fmtMsg) };
    },
    async sendMessage(cid, content){
      await ensureLoaded(cid);
      const nonce=String(Date.now())+"000";
      try{ MA.sendMessage(cid,{content, tts:false, invalidEmojis:[], validNonShortcutEmojis:[]}, true, {nonce}); }
      catch(e){ return { ok:false, error:String(e&&e.message||e) }; }
      const r=await poll(cid, ms=>{ const m=ms.find(x=>x.nonce===nonce); if(!m) return null;
        if(m.state==="SENT") return {id:m.id}; if(m.state==="SEND_FAILED") return {failed:true}; return null; });
      if(!r) return { ok:false, error:"timeout: 送信の確定（SENT）を確認できなかった" };
      if(r.failed) return { ok:false, error:"send_failed" };
      return { ok:true, id:r.id };
    },
    async editMessage(cid, mid, content){
      await ensureLoaded(cid);
      if(!S.MessageStore.getMessage(cid,mid)) throw new Error("message_not_in_store: "+mid+"（read_messages の before で読み込んでから）");
      try{ MA.editMessage(cid, mid, {content}); }catch(e){ return { ok:false, error:String(e&&e.message||e) }; }
      const r=await poll(cid, ()=>{ const m=S.MessageStore.getMessage(cid,mid); return m&&m.content===content; });
      return { ok:!!r, content:(S.MessageStore.getMessage(cid,mid)||{}).content };
    },
    async deleteMessage(cid, mid){
      await ensureLoaded(cid);
      if(!S.MessageStore.getMessage(cid,mid)) throw new Error("message_not_in_store: "+mid+"（read_messages の before で読み込んでから）");
      try{ MA.deleteMessage(cid, mid); }catch(e){ return { ok:false, error:String(e&&e.message||e) }; }
      const r=await poll(cid, ()=> !S.MessageStore.getMessage(cid,mid));
      return { ok:!!r };
    },
  };
  window.__DMCP={ v:V, api };
  return { ok:true };
})()
"""


# --- CDP クライアント（同期・接続を 1 本保持） ---


class CDP:
    """専用インスタンスの page ターゲットへ websocket を張り、Runtime.evaluate を同期で呼ぶ。"""

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
                f"MCP 専用の Discord を起動する（{e}）"
            )
        pages = [t for t in targets if t.get("type") == "page" and "discord.com" in t.get("url", "")]
        if not pages:
            raise DiscordAppError("discord.com の page ターゲットが無い。専用の Discord が起動中か、ログインしているか確認する")
        return pages[0]["webSocketDebuggerUrl"]

    def _connect(self) -> None:
        import websocket  # websocket-client

        if self._ws is not None:
            return
        # suppress_origin: CDP は Origin ヘッダ付きの WebSocket を 403 で弾く（devtools 自身は付けない）
        self._ws = websocket.create_connection(
            self._page_ws_url(), max_size=2 ** 27, timeout=60, suppress_origin=True
        )

    def _cmd(self, method: str, params: dict | None = None) -> dict:
        import websocket

        self._connect()
        self._id += 1
        mid = self._id
        try:
            self._ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
            while True:
                msg = json.loads(self._ws.recv())
                if msg.get("id") == mid:
                    break
        except (websocket.WebSocketException, OSError):
            # Discord の再起動などで切れた。次の呼び出しで張り直す
            self._ws = None
            raise DiscordAppError("CDP 接続が切れた。専用の Discord が落ちたなら `launch` で起動し直す")
        if "error" in msg:
            raise DiscordAppError(f"CDP {method}: {msg['error']}")
        return msg["result"]

    def evaluate(self, expression: str):
        res = self._cmd(
            "Runtime.evaluate",
            {"expression": expression, "awaitPromise": True, "returnByValue": True},
        )
        if "exceptionDetails" in res:
            exc = res["exceptionDetails"]
            desc = (exc.get("exception") or {}).get("description") or exc.get("text")
            raise DiscordAppError(f"renderer 例外: {str(desc)[:300]}")
        return res["result"].get("value")

    def _ensure_agent(self) -> None:
        # 起動直後はアプリ本体のモジュールが揃っていないので、揃うまで張り直しを繰り返す
        deadline = time.monotonic() + BOOT_TIMEOUT
        while True:
            res = self.evaluate(AGENT_JS) or {}
            if res.get("ok"):
                return
            if time.monotonic() > deadline:
                raise DiscordAppError(f"モジュール解決に失敗した（未解決: {res.get('missing')}）")
            time.sleep(2.0)

    def call_api(self, method: str, *args):
        """window.__DMCP.api.<method>(...args) を呼ぶ。エージェントが無ければ張る。"""
        with self._lock:
            self._ensure_agent()
            expr = (
                "(async()=>{try{const a=" + json.dumps(list(args)) + ";"
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


# --- 専用インスタンスの起動 ---


def _cdp_reachable(port: int) -> bool:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=3).read()
        return True
    except OSError:
        return False


def _discord_processes() -> tuple[list[str], list[str]]:
    """(普段使いの Discord, 専用インスタンス) のメインプロセスのコマンドラインを返す。"""
    out = subprocess.run(["ps", "-axo", "command="], capture_output=True, text=True).stdout
    mains = [l for l in out.splitlines() if l.startswith(DISCORD_BIN)]
    instance = [l for l in mains if "--multi-instance" in l]
    return [l for l in mains if l not in instance], instance


def cmd_launch(dry_run: bool, at_login: bool) -> int:
    port, data_dir = _cdp_port(), _instance_dir()
    if _cdp_reachable(port):
        print(f"CDP ({port}): 既に待ち受けている。何もしない")
        return 0
    main, instance = _discord_processes()
    if instance:
        # ポートなしで専用インスタンスが動いている。勝手に落とさず報告だけする
        print(f"NG: 専用インスタンスが動いているのに CDP ({port}) が開いていない: {instance[0][:160]}")
        return 1
    if at_login and not main:
        # 先に専用を起動すると、普段使いの自動起動が専用の窓をアクティブにするだけで終わる
        for _ in range(MAIN_WAIT_AT_LOGIN // 5):
            if dry_run or _discord_processes()[0]:
                break
            time.sleep(5)
    cmd = ["open", "-n", "-a", "Discord", "--env", f"DISCORD_USER_DATA_DIR={data_dir}",
           "--args", "--multi-instance", f"--remote-debugging-port={port}"]
    if dry_run:
        print("dry-run: 次を実行する: " + " ".join(cmd))
        return 0
    os.makedirs(data_dir, exist_ok=True)
    subprocess.run(cmd, check=True)
    for _ in range(60):
        if _cdp_reachable(port):
            print(f"CDP ({port}): 専用インスタンスを起動した（データ: {data_dir}）")
            return 0
        time.sleep(1)
    print(f"NG: CDP ({port}): 起動を確認できなかった")
    return 1


# --- MCP サーバ ---


def build_server(cdp: CDP):
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("discord-app")

    @mcp.tool()
    def discord_whoami() -> dict:
        """ログイン中の自分（id・表示名）を返す。接続の疎通確認を兼ねる。"""
        return cdp.call_api("whoami")

    @mcp.tool()
    def discord_list_guilds() -> list:
        """参加しているサーバー（id・name）の一覧を返す。"""
        return cdp.call_api("listGuilds")

    @mcp.tool()
    def discord_list_channels(guild_id: str) -> list:
        """サーバー内のチャンネル（id・name・type・parent・topic）の一覧を返す。type: 0=テキスト, 2=ボイス, 4=カテゴリ, 5=アナウンス, 15=フォーラム。"""
        return cdp.call_api("listChannels", guild_id)

    @mcp.tool()
    def discord_read_messages(channel_id: str, limit: int = 30, before: str | None = None) -> dict:
        """チャンネルのメッセージを古い順で返す（最大100件）。before を省くと最新 limit 件。
        過去へさかのぼるときは、返り値の next_before を次の呼び出しの before に渡す（has_more_before が false なら先頭まで来た）。
        返り値: channel・count・next_before・has_more_before・messages（id・author・content・ts・reply_to・attachments・reactions）。"""
        return cdp.call_api("readMessages", channel_id, limit, before)

    @mcp.tool()
    def discord_send_message(channel_id: str, content: str) -> dict:
        """チャンネルにメッセージを送る。write_allow に入れたチャンネルだけ通る。
        送信は外に出る操作なので、呼ぶ前に送り先と本文を利用者に確認すること。"""
        _require_write_allowed(channel_id)
        return cdp.call_api("sendMessage", channel_id, content)

    @mcp.tool()
    def discord_edit_message(channel_id: str, message_id: str, content: str) -> dict:
        """自分のメッセージの本文を書き換える。write_allow に入れたチャンネルだけ通る。"""
        _require_write_allowed(channel_id)
        return cdp.call_api("editMessage", channel_id, message_id, content)

    @mcp.tool()
    def discord_delete_message(channel_id: str, message_id: str) -> dict:
        """メッセージを削除する。write_allow に入れたチャンネルだけ通る。"""
        _require_write_allowed(channel_id)
        return cdp.call_api("deleteMessage", channel_id, message_id)

    return mcp


def cmd_doctor() -> int:
    port = _cdp_port()
    main, instance = _discord_processes()
    print(f"CDP port: {port}  reachable={_cdp_reachable(port)}  "
          f"普段使い={'起動中' if main else 'なし'}  専用={'起動中' if instance else 'なし'}")
    if not _cdp_reachable(port):
        print("NG: `discord-app-mcp.py launch` で MCP 専用の Discord を起動する")
        return 1
    cdp = CDP(port)
    try:
        me = cdp.call_api("whoami")
        guilds = cdp.call_api("listGuilds")
        print(f"OK: user={me.get('name')} ({me.get('id')})  guilds={len(guilds)}")
        return 0
    except DiscordAppError as e:
        print(f"NG: {e}")
        return 1


def main() -> int:
    args = sys.argv[1:]
    cmd = args[0] if args else "server"
    if cmd == "doctor":
        return cmd_doctor()
    if cmd == "launch":
        return cmd_launch(dry_run="--dry-run" in args, at_login="--at-login" in args)
    if cmd == "server":
        build_server(CDP(_cdp_port())).run()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
