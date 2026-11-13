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
通信はすべて Discord.app 本体の関数か、本体の認証つき HTTP クライアント（MessageQueue が
/interactions を叩くのと同じもの）から出すので、送り元とヘッダは通常の操作と同じになる。
self-bot（ユーザートークンで外から API を叩く）ではない。

しくみ:
- 普段使いの Discord とは別に、MCP 専用のインスタンスを起動する（`launch`）。Discord 本体の
  `--multi-instance` と環境変数 `DISCORD_USER_DATA_DIR` で、別のデータ置き場・別ウィンドウとして
  同時に動く。CDP のポート（`--remote-debugging-port`）はこちらにだけ開く。初回だけログインが要る。
- CDP で renderer に入り、`webpackChunkdiscord_app` に chunk を 1 つ push して webpack require を
  受け取る。ページにはランタイムが複数あるので、モジュールキャッシュが最大のもの（アプリ本体）を使う。
- その require から Flux ストア（GuildStore / ChannelStore / MessageStore / …）と、本体の認証つき
  HTTP クライアントを取り出す。メッセージの読み書きは HTTP クライアントで REST を直接呼ぶ（ストアは
  読み込み済みの古い範囲だけを持っていることがあり、送信の反映も遅れるため）。チャンネルを開かないので、
  専用ウィンドウの表示も変えない。interaction の応答（ephemeral を含む）は gateway 経由で MessageStore
  にだけ届くので、そこから読む。

安全:
- 書き込み（送信・編集・削除・スレッド作成・コマンド実行・ボタン・モーダル・汎用 REST の GET 以外）は、
  ~/.claude/local/discord-app-mcp.json の write_allow に明示したチャンネルか、write_allow_guilds に明示した
  サーバー内のチャンネル（スレッドを含む）だけ通る（既定は空）。1 件ずつの確認は呼び出し側（Claude Code）が行う前提。
- 汎用 REST（discord_api）の書き込みはチャンネル配下のメッセージまわりとスレッドの変更に限り、サーバーの管理操作は通さない。
- トークンは renderer の外へ出さない。この MCP はトークンを読まない。

使い方:
  discord-app-mcp.py doctor                 # CDP への接続・モジュール解決を確認
  discord-app-mcp.py launch [--dry-run]     # 専用インスタンスを起動する（普段使いには触れない）
  discord-app-mcp.py launch --at-login      # ログイン時用。普段使いの起動を待ってから起動する
  discord-app-mcp.py server                 # stdio の MCP サーバとして動く
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
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
  const V = "__AGENT_VERSION__";  // AGENT_JS のハッシュ。中身を変えると古いエージェントを張り直す
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
  for(const n of ["GuildStore","MessageStore","UserStore","ChannelStore","AuthenticationStore"]) S[n]=byName(n);
  const MA=exps.find(e=>fn(e,"fetchMessages")&&fn(e,"sendMessage")&&fn(e,"editMessage")&&fn(e,"deleteMessage"));
  // アプリ本体の認証つき HTTP クライアント（MessageQueue.handleCommand もこれで /interactions を叩く）。
  // 同じモジュールが export する fT（rejectWithError の既定）で、汎用の superagent と見分ける
  let HTTP;
  for(const m of Object.values(w.c)){ const e=get(m,"exports"); const b=e&&get(e,"Bo");
    if(b&&get(e,"fT")&&["get","post","put","patch","del"].every(k=>fn(b,k))){ HTTP=b; break; } }
  const D=exps.find(e=>fn(e,"subscribe")&&fn(e,"unsubscribe")&&fn(e,"dispatch")&&get(e,"_actionHandlers"));
  const missing=[];
  for(const [k,v] of Object.entries({...S, MessageActions:MA, HTTP, Dispatcher:D})) if(!v) missing.push(k);
  if(missing.length) return { ok:false, missing };
  // 起動直後はモジュールが揃っても gateway の READY 前でストアが空
  if(!S.UserStore.getCurrentUser()) return { ok:false, missing:["READY（ログイン前か接続中）"] };

  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const store=cid=>S.MessageStore.getMessages(cid);
  const arr=cid=>{ try{ return store(cid).toArray(); }catch{ return []; } };
  // ストアのレコード（camelCase）と REST の JSON（snake_case）の両方を整形する
  const fmtUser=u=>u?{id:u.id, name:(u.globalName||u.global_name||u.username), bot:!!u.bot}:null;
  const fmtMsg=m=>({ id:m.id, author:fmtUser(m.author), content:m.content||"",
     ts:(()=>{try{return new Date(m.timestamp).toISOString()}catch{return String(m.timestamp)}})(),
     edited:!!(m.editedTimestamp||m.edited_timestamp), ephemeral:!!((m.flags||0)&64),
     reply_to:((m.messageReference||m.message_reference||{}).message_id)||null,
     attachments:(m.attachments||[]).map(a=>({name:a.filename,url:a.url})),
     embeds:(m.embeds||[]).length, reactions:(m.reactions||[]).map(r=>({emoji:(r.emoji&&(r.emoji.name||r.emoji.id)),count:r.count})) });
  const channelOf=cid=>{ const ch=S.ChannelStore.getChannel(cid); if(!ch) throw new Error("channel_not_found: "+cid+"（未参加か id 誤り）"); return ch; };
  // fetchMessages は REST の完了で解決する Promise を返す（キャッシュで足りたときは undefined）
  const fetch_=async (cid, before, limit)=>{
    const p=MA.fetchMessages({channelId:cid, before:before||undefined, limit});
    await Promise.race([Promise.resolve(p), sleep(10000)]); await sleep(150);
  };
  const ensureLoaded=async cid=>{ channelOf(cid); if(!store(cid).ready) await fetch_(cid, null, 50); };

  // Bo は rejectWithError:false でも 4xx/5xx で reject する（値は応答オブジェクト）ので、どちらも {status, body} にそろえる
  const rest=async (method, url, body)=>{
    let r; try{ r=await HTTP[method]({url, body, rejectWithError:false}); }catch(e){ r=e; }
    if(r==null||r.status==null) throw new Error("http_failed: "+String(r&&r.message||r));
    return { status:r.status, body:r.body??null };
  };
  const channelInfo=async cid=>{ const ch=S.ChannelStore.getChannel(cid); if(ch) return {name:ch.name, type:ch.type, guild_id:ch.guild_id||null};
    const r=await rest("get",`/channels/${cid}`); if(r.status>=300) throw new Error("channel_not_found: "+cid+"（未参加か id 誤り）");
    return {name:r.body.name||null, type:r.body.type, guild_id:r.body.guild_id||null}; };
  // ephemeral のメッセージはストアにしか無く、それ以外はストアに無ければ REST で取る（user アカウントは単体 GET を使えないので around）
  const messageOf=async (cid, mid)=>{ const m=S.MessageStore.getMessage(cid,mid); if(m) return m;
    const r=await rest("get", `/channels/${cid}/messages?around=${mid}&limit=1`);
    return (r.status<300&&(r.body||[]).find(x=>x.id===mid))||null; };
  const restError=(what, r)=>({ ok:false, status:r.status, error:r.body, what });
  const snowflake=()=>((BigInt(Date.now())-1420070400000n)<<22n).toString();

  // interaction の結果は gateway でしか届かない（POST は 204 だけ返す）。nonce ごとに集める。
  // 応答メッセージは interaction と同じ nonce を持つ（ephemeral も MessageStore に入る）
  const inter={};
  const onEv=t=>a=>{ const n=a.nonce||(a.message&&a.message.nonce); const r=n&&inter[n]; if(!r) return;
    if(t==="INTERACTION_MODAL_CREATE") r.modal={ id:a.id, custom_id:a.customId, title:a.title, channel_id:a.channelId,
       application_id:a.application&&a.application.id, components:a.components };
    else if(t==="INTERACTION_FAILURE") r.failure={ code:a.errorCode??null, message:a.errorMessage??null };
    else if(t==="INTERACTION_SUCCESS") r.success=true; };
  const EV=["INTERACTION_SUCCESS","INTERACTION_FAILURE","INTERACTION_MODAL_CREATE"];
  if(window.__DMCP&&window.__DMCP.unsubscribe) window.__DMCP.unsubscribe();
  const subs=EV.map(t=>[t,onEv(t)]); subs.forEach(([t,f])=>D.subscribe(t,f));
  const unsubscribe=()=>subs.forEach(([t,f])=>D.unsubscribe(t,f));
  const modals={};  // 開いたモーダルを interaction id で保持し、submitModal で使う
  const LOADING=128;  // 応答が deferred（「考え中」）の間のメッセージ flags
  const fmtModal=m=>({ id:m.id, title:m.title, fields:(function walk(cs){ return (cs||[]).flatMap(c=>
     c.type===1? walk(c.components) : c.type===18? walk([c.component]) :
     c.type===4? [{custom_id:c.customId, label:c.label||null, required:!!c.required, placeholder:c.placeholder||null}] : []); })(m.components) });
  // body を /interactions に送り、成功・失敗・モーダル・応答メッセージを待って返す
  const interact=async (cid, body, waitSec)=>{
    await ensureLoaded(cid);
    const nonce=snowflake(); const rec=inter[nonce]={};
    const r=await rest("post","/interactions",{...body, nonce, session_id:S.AuthenticationStore.getSessionId()});
    if(r.status>=300){ delete inter[nonce]; return { ok:false, status:r.status, error:r.body }; }
    const replies=()=>arr(cid).filter(m=>m.nonce===nonce);
    const until=Date.now()+Math.max(2,Math.min(60,waitSec||15))*1000;
    let settledAt=null;
    while(Date.now()<until){
      if(rec.failure||rec.modal) break;
      const ms=replies();
      if(ms.length&&ms.every(m=>!((m.flags||0)&LOADING))) break;
      // 応答メッセージなしで終わる操作（元のメッセージの書き換えなど）は、成功から少し待って打ち切る
      if(rec.success&&!ms.length){ settledAt=settledAt||Date.now(); if(Date.now()-settledAt>2500) break; }
      await sleep(300);
    }
    delete inter[nonce];
    if(rec.modal) modals[rec.modal.id]=rec.modal;
    const ms=replies();
    return { ok:!rec.failure, nonce,
      state: rec.failure?"failed": rec.modal?"modal": ms.some(m=>(m.flags||0)&LOADING)?"pending": rec.success||ms.length?"done":"no_ack",
      failure:rec.failure||null, modal:rec.modal?fmtModal(rec.modal):null,
      replies: ms.map(m=>({...fmtMsg(m), components:fmtComponents(m.components)})) };
  };
  const fmtComponents=cs=>(function walk(cs){ return (cs||[]).flatMap(c=>
     Array.isArray(c.components)? walk(c.components) :
     (c.customId||c.custom_id)? [{custom_id:c.customId||c.custom_id, type:c.type, label:c.label||c.placeholder||null, disabled:!!c.disabled,
       options:(c.options||[]).map(o=>({value:o.value,label:o.label}))}] : []); })(cs);

  // コマンド定義。サーバーのチャンネルはサーバーの index、DM は チャンネルの index に、ユーザーにインストールしたアプリの index を足す
  const indexCache={};  // 実行のたびに取り直すとすぐ 429 になる
  const commandIndex=async cid=>{
    const ch=channelOf(cid);
    const urls=[ch.guild_id?`/guilds/${ch.guild_id}/application-command-index`:`/channels/${cid}/application-command-index`,
                "/users/@me/application-command-index"];
    const cmds=[], apps={};
    for(const u of urls){ const c=indexCache[u]; let r;
      if(c&&Date.now()-c.at<60000) r=c.r;
      else { r=await rest("get",u); if(r.status>=300) throw new Error("command_index_failed: "+u+" "+r.status+" "+JSON.stringify(r.body));
             indexCache[u]={at:Date.now(), r}; }
      for(const a of r.body.applications||[]) apps[a.id]=a.name;
      for(const c of r.body.application_commands||[]) if(!cmds.some(x=>x.id===c.id)) cmds.push(c); }
    return { cmds, apps };
  };
  // name は表示用に訳されていることがあり、/interactions には訳す前の name_default を送る（訳した名前は 10005 Unknown Integration）
  const realName=c=>c.name_default||c.name;
  const OPT={SUB:1,GROUP:2,STRING:3,INTEGER:4,BOOLEAN:5,NUMBER:10,ATTACHMENT:11};
  const coerce=(o,v)=>{
    if(o.type===OPT.INTEGER){ const n=Number(v); if(!Number.isInteger(n)) throw new Error("option "+o.name+": 整数を渡す"); return n; }
    if(o.type===OPT.NUMBER){ const n=Number(v); if(Number.isNaN(n)) throw new Error("option "+o.name+": 数値を渡す"); return n; }
    if(o.type===OPT.BOOLEAN) return v===true||v==="true";
    if(o.type===OPT.ATTACHMENT) throw new Error("option "+o.name+": 添付ファイルの引数には対応していない");
    return String(v);  // STRING と、user / channel / role / mentionable の id
  };
  const buildOptions=(decl, given)=>{
    const out=[];
    for(const o of decl||[]){ if(!(o.name in given)){ if(o.required) throw new Error("option "+o.name+" は必須"); continue; }
      out.push({type:o.type, name:o.name, value:coerce(o, given[o.name])}); }
    const unknown=Object.keys(given).filter(k=>!(decl||[]).some(o=>o.name===k));
    if(unknown.length) throw new Error("未知の option: "+unknown.join(", ")+"（list_commands で引数名を確かめる）");
    return out;
  };

  const api = {
    whoami(){ return fmtUser(S.UserStore.getCurrentUser()); },
    listGuilds(){ return Object.values(S.GuildStore.getGuilds()).map(x=>({id:x.id,name:x.name})); },
    // ゲートの判定用。アーカイブ済みのスレッドはストアに無いことがあるので REST で引く
    async guildOf(cid){ return (await channelInfo(cid)).guild_id||null; },
    listChannels(gid){ const c=S.ChannelStore.getMutableGuildChannelsForGuild(gid)||{};
      return Object.values(c).filter(ch=>ch&&ch.guild_id===gid)
        .map(ch=>({id:ch.id,name:ch.name,type:ch.type,parent:ch.parent_id,topic:ch.topic||null,nsfw:!!ch.nsfw}))
        .sort((a,b)=>(a.type-b.type)||String(a.name).localeCompare(String(b.name))); },
    // before を省くと最新、指定するとその id より古い側を limit 件（古い順）で返す。
    // ストア（MessageStore）は読み込み済みの古い範囲だけを持っていることがあるので、毎回 REST で読む
    async readMessages(cid, limit, before){
      limit=Math.max(1,Math.min(100,limit||30));
      const ch=await channelInfo(cid);
      const r=await rest("get", `/channels/${cid}/messages?limit=${limit}`+(before?`&before=${before}`:""));
      if(r.status>=300) throw new Error("read_failed: "+r.status+" "+JSON.stringify(r.body));
      const page=(r.body||[]).slice().reverse();  // REST は新しい順
      return { channel:{id:cid,name:ch.name,guild:ch.guild_id}, count:page.length,
        next_before: page.length? page[0].id : null,
        has_more_before: page.length===limit,
        messages: page.map(fmtMsg) };
    },
    // POST の応答で確定する（ストアの反映は待たない）。enforce_nonce で、同じ nonce の再送は二重投稿にならない。
    // files（[{name, data: base64}]）は本体と同じ経路で上げる: アップロード先を受け取って PUT し、投稿で参照する
    async sendMessage(cid, content, files){
      const nonce=snowflake();
      const body={content:content||"", nonce, enforce_nonce:true, tts:false};
      if(files&&files.length){
        const bytes=files.map(f=>Uint8Array.from(atob(f.data), c=>c.charCodeAt(0)));
        const u=await rest("post", `/channels/${cid}/attachments`,
          {files:files.map((f,i)=>({id:String(i), filename:f.name, file_size:bytes[i].length}))});
        if(u.status>=300) return restError("upload_url", u);
        for(const a of u.body.attachments){
          const p=await fetch(a.upload_url, {method:"PUT", body:bytes[Number(a.id)]});
          if(!p.ok) return { ok:false, what:"upload", status:p.status, error:(await p.text()).slice(0,300) };
        }
        body.attachments=u.body.attachments.map(a=>({id:a.id, filename:files[Number(a.id)].name, uploaded_filename:a.upload_filename}));
      }
      let r;
      try{ r=await rest("post", `/channels/${cid}/messages`, body); }
      catch(e){ return { ok:false, error:"unknown: 届いたか分からない（"+String(e&&e.message||e)+"）。再送する前に read_messages で確かめる" }; }
      if(r.status>=300) return restError("send", r);
      return { ok:true, id:r.body.id };
    },
    async editMessage(cid, mid, content){
      const r=await rest("patch", `/channels/${cid}/messages/${mid}`, {content});
      if(r.status>=300) return restError("edit", r);
      return { ok:true, content:r.body.content };
    },
    async deleteMessage(cid, mid){
      const r=await rest("del", `/channels/${cid}/messages/${mid}`);
      if(r.status>=300) return restError("delete", r);
      return { ok:true };
    },
    async channelType(cid){ return (await channelInfo(cid)).type; },
    // message_id があればそのメッセージから、無ければチャンネルに直接作る。フォーラム（15）とメディア（16）は最初の投稿 content が要る
    async createThread(cid, name, messageId, content, autoArchive, isPrivate){
      const ch=channelOf(cid); const forum=ch.type===15||ch.type===16;
      const body={name, auto_archive_duration:autoArchive||1440};
      let url;
      if(messageId) url=`/channels/${cid}/messages/${messageId}/threads`;
      else { url=`/channels/${cid}/threads`;
        if(forum){ if(!content) throw new Error("フォーラムのチャンネルには最初の投稿 content が要る"); body.message={content}; }
        else body.type= ch.type===5? 10 : isPrivate? 12 : 11; }
      const r=await rest("post", url, body);
      if(r.status>=300) return { ok:false, status:r.status, error:r.body };
      // gateway の THREAD_CREATE でストアに入るまで、send_message などがこのスレッドを見つけられない
      for(let i=0;i<25&&!S.ChannelStore.getChannel(r.body.id);i++) await sleep(200);
      return { ok:true, id:r.body.id, name:r.body.name, parent_id:r.body.parent_id, type:r.body.type };
    },
    async listCommands(cid){
      const {cmds, apps}=await commandIndex(cid);
      const T={1:"slash",2:"user",3:"message",4:"primary_entry_point"};
      const opt=o=>({name:o.name, type:o.type, required:!!o.required, description:o.description||null,
         choices:(o.choices||[]).map(c=>({name:c.name,value:c.value})), autocomplete:!!o.autocomplete,
         options:(o.options||[]).length? o.options.map(opt) : undefined});
      return cmds.map(c=>({ id:c.id, application:apps[c.application_id]||c.application_id, application_id:c.application_id,
         kind:T[c.type]||c.type, name:c.name, name_default:c.name_default||null, description:c.description||null,
         options:(c.options||[]).map(opt) }));
    },
    // command はコマンド名（表示名・訳す前の名前・id のどれでもよい）。サブコマンドは "group sub" のように空白で続ける
    async runCommand(cid, command, options, targetId, applicationId, waitSec){
      const ch=channelOf(cid);
      const [head, ...path]=String(command).trim().split(/\s+/);
      const {cmds}=await commandIndex(cid);
      const hits=cmds.filter(c=>(c.id===head||c.name===command||c.name===head||realName(c)===head||realName(c)===command)
         &&(!applicationId||c.application_id===applicationId));
      if(!hits.length) throw new Error("command_not_found: "+command+"（list_commands で確かめる）");
      if(hits.length>1) throw new Error("同名のコマンドが複数ある: "+hits.map(c=>c.application_id).join(", ")+"（application_id を指定する）");
      const c=hits[0]; const whole=c.name===command||realName(c)===command;
      let decl=c.options||[], wrap=x=>x;
      for(const p of (whole? [] : path)){
        const o=decl.find(o=>(o.type===OPT.SUB||o.type===OPT.GROUP)&&o.name===p);
        if(!o) throw new Error("サブコマンドが無い: "+p);
        const outer=wrap; wrap=x=>outer([{type:o.type, name:o.name, options:x}]); decl=o.options||[];
      }
      if(decl.some(o=>o.type===OPT.SUB||o.type===OPT.GROUP)) throw new Error("サブコマンドを指定する: "+decl.map(o=>o.name).join(", "));
      const data={version:c.version, id:c.id, name:realName(c), type:c.type, application_command:c,
         options: wrap(buildOptions(decl, options||{}))};
      if(c.type===2||c.type===3){ if(!targetId) throw new Error("コンテキストメニューのコマンドには target_id（"+(c.type===3?"メッセージ":"ユーザー")+" id）が要る"); data.target_id=targetId; }
      return interact(cid, {type:2, application_id:c.application_id, guild_id:ch.guild_id||undefined, channel_id:cid, data}, waitSec);
    },
    // ボタンかセレクトメニューを操作する。values はセレクトの選択値
    async clickComponent(cid, mid, customId, values, waitSec){
      const ch=await channelInfo(cid);
      const m=await messageOf(cid, mid);
      if(!m) throw new Error("message_not_found: "+mid);
      const comp=fmtComponents(m.components).find(c=>c.custom_id===customId);
      if(!comp) throw new Error("component_not_found: "+customId+"（このメッセージの components: "+fmtComponents(m.components).map(c=>c.custom_id).join(", ")+"）");
      const appId=m.applicationId||m.application_id||(m.application&&m.application.id)||(m.author&&m.author.id);
      const data={component_type:comp.type, custom_id:customId};
      if(comp.type!==2){ if(!Array.isArray(values)||!values.length) throw new Error("セレクトメニューには values が要る"); data.values=values.map(String); }
      const r=await interact(cid, {type:3, guild_id:ch.guild_id||undefined, channel_id:cid, message_flags:m.flags||0, message_id:mid, application_id:appId, data}, waitSec);
      const after=await messageOf(cid, mid);
      return {...r, message_after: after? {...fmtMsg(after), components:fmtComponents(after.components)} : null};
    },
    // values は入力欄の custom_id かラベルを鍵にした値
    async submitModal(cid, modalId, values, waitSec){
      const m=modals[modalId];
      if(!m) throw new Error("modal_not_found: "+modalId+"（モーダルは run_command・click_component の返り値の modal.id。張り直しで消える）");
      if(m.channel_id!==cid) throw new Error("このモーダルはチャンネル "+m.channel_id+" のもの");
      const used=new Set();
      const fill=cs=>cs.map(c=>{
        if(c.type===1) return {type:1, components:fill(c.components)};
        if(c.type===18) return {type:18, component:fill([c.component])[0]};
        if(c.type===4){ const k=[c.customId, c.label].find(k=>k!=null&&k in values);
          if(k==null&&c.required) throw new Error("入力欄 "+(c.label||c.customId)+" は必須");
          if(k!=null) used.add(k); return {type:4, custom_id:c.customId, value:k!=null?String(values[k]):""}; }
        throw new Error("このモーダルの部品（type "+c.type+"）には対応していない（入力欄だけ扱える）");
      });
      const components=fill(m.components);
      const unknown=Object.keys(values).filter(k=>!used.has(k));
      if(unknown.length) throw new Error("モーダルに無い入力欄: "+unknown.join(", "));
      const ch=channelOf(cid);
      const r=await interact(cid, {type:5, application_id:m.application_id, channel_id:cid, guild_id:ch.guild_id||undefined,
         data:{id:m.id, custom_id:m.custom_id, components}}, waitSec);
      if(r.ok) delete modals[modalId];
      return r;
    },
    async request(method, path, body){ return rest(method, path, body); },
  };
  window.__DMCP={ v:V, api, unsubscribe };
  return { ok:true };
})()
"""
AGENT_JS = AGENT_JS.replace("__AGENT_VERSION__", hashlib.sha1(AGENT_JS.encode()).hexdigest()[:12])


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
            self._page_ws_url(), max_size=2 ** 27, timeout=120, suppress_origin=True
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


def _write_allowed(cdp: CDP, channel_id: str) -> bool:
    config = _config()
    allow = config.get("write_allow")
    if allow == "*" or (isinstance(allow, list) and channel_id in allow):
        return True
    guilds = config.get("write_allow_guilds")
    return isinstance(guilds, list) and bool(guilds) and cdp.call_api("guildOf", channel_id) in guilds


def _require_write_allowed(cdp: CDP, channel_id: str) -> None:
    if not _write_allowed(cdp, channel_id):
        raise DiscordAppError(
            f"チャンネル {channel_id} への書き込みは許可されていない。"
            f"{CONFIG} の write_allow に channel id か、write_allow_guilds に guild id を足すと通る"
        )


# 汎用 REST で書き込みを通すのは、チャンネル配下のメッセージまわりと、スレッド自体の変更（アーカイブ・ロック・改名・削除）だけ。
# サーバーの管理（ロール・BAN・チャンネルの作成や権限）は、書き込みを許可したサーバーでも通さない
_CHANNEL_WRITE_PATH = re.compile(
    r"^/channels/(\d+)(?:/(messages|pins|typing|threads|thread-members|polls)(?:/.*)?)?$"
)
_THREAD_TYPES = (10, 11, 12)


def _check_request(cdp: CDP, method: str, path: str) -> None:
    bare = path.split("?", 1)[0]
    if not bare.startswith("/") or ".." in bare:
        raise DiscordAppError("path は /channels/... のような API のパスで渡す")
    if bare.startswith("/auth"):
        raise DiscordAppError("/auth 配下は扱わない")
    if method == "get":
        return
    m = _CHANNEL_WRITE_PATH.match(bare)
    if not m:
        raise DiscordAppError(
            "GET 以外で通すのは /channels/{id}/(messages|pins|typing|threads|thread-members|polls)/... と、"
            "スレッド自体の PATCH・DELETE だけ"
        )
    channel_id, sub = m.group(1), m.group(2)
    if sub is None and (method not in ("patch", "del") or cdp.call_api("channelType", channel_id) not in _THREAD_TYPES):
        raise DiscordAppError("チャンネル自体の変更はスレッドの PATCH・DELETE だけ通す")
    _require_write_allowed(cdp, channel_id)


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
    def discord_send_message(channel_id: str, content: str = "", files: list[str] | None = None) -> dict:
        """チャンネルにメッセージを送る。files にローカルファイルの絶対パスを渡すと添付する（画像など。最大10件）。
        content と files のどちらかは要る。write_allow か write_allow_guilds で許可したチャンネルだけ通る。
        送信は外に出る操作なので、呼ぶ前に送り先・本文・添付を利用者に確認すること。"""
        if not content and not files:
            raise DiscordAppError("content か files のどちらかを渡す")
        if files and len(files) > 10:
            raise DiscordAppError("添付は1回に10件まで")
        payload = []
        for path in files or []:
            if not os.path.isfile(path):
                raise DiscordAppError(f"ファイルが無い: {path}")
            with open(path, "rb") as f:
                payload.append({"name": os.path.basename(path), "data": base64.b64encode(f.read()).decode()})
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("sendMessage", channel_id, content, payload)

    @mcp.tool()
    def discord_edit_message(channel_id: str, message_id: str, content: str) -> dict:
        """自分のメッセージの本文を書き換える。write_allow か write_allow_guilds で許可したチャンネルだけ通る。"""
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("editMessage", channel_id, message_id, content)

    @mcp.tool()
    def discord_delete_message(channel_id: str, message_id: str) -> dict:
        """メッセージを削除する。write_allow か write_allow_guilds で許可したチャンネルだけ通る。"""
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("deleteMessage", channel_id, message_id)

    @mcp.tool()
    def discord_create_thread(
        channel_id: str,
        name: str,
        message_id: str | None = None,
        content: str | None = None,
        auto_archive_minutes: int = 1440,
        private: bool = False,
    ) -> dict:
        """スレッドを作る。message_id を渡すとそのメッセージから、省くとチャンネルに直接作る（private=True で非公開スレッド）。
        フォーラムのチャンネルでは content（最初の投稿）が要る。auto_archive_minutes は 60・1440・4320・10080。
        write_allow か write_allow_guilds で許可したチャンネルだけ通る。作る前にスレッド名を利用者に確認すること。
        返り値の id はスレッドのチャンネル id で、send_message・read_messages にそのまま渡せる。"""
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("createThread", channel_id, name, message_id, content, auto_archive_minutes, private)

    @mcp.tool()
    def discord_list_commands(channel_id: str) -> list:
        """そのチャンネルで使えるアプリのコマンド（スラッシュ・メッセージのコンテキストメニュー・ユーザーのコンテキストメニュー）を返す。
        kind: slash / message / user。options は引数（type 3=文字列, 4=整数, 5=真偽, 6=ユーザー, 7=チャンネル, 8=ロール, 10=数値, 1=サブコマンド, 2=サブコマンドグループ）。"""
        return cdp.call_api("listCommands", channel_id)

    @mcp.tool()
    def discord_run_command(
        channel_id: str,
        command: str,
        options: dict | None = None,
        target_id: str | None = None,
        application_id: str | None = None,
        wait_seconds: int = 15,
    ) -> dict:
        """アプリのコマンドを自分の名義で実行し、Bot の応答を待って返す。
        command はコマンド名か id。サブコマンドは "group sub" のように空白で続ける。options は {引数名: 値}（ユーザー・チャンネル・ロールは id）。
        コンテキストメニューのコマンド（kind が message / user）は target_id にメッセージ id かユーザー id を渡す。
        返り値 state: done（応答あり）/ modal（フォームが開いた。submit_modal で送る）/ pending（応答待ちのまま時間切れ）/ failed / no_ack。
        replies は応答メッセージ（ephemeral=自分にだけ見えるものを含む。components はボタン・セレクト）。
        Bot 側で何が起きるか分からないので、呼ぶ前にコマンドと引数を利用者に確認すること。write_allow か write_allow_guilds で許可したチャンネルだけ通る。"""
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("runCommand", channel_id, command, options or {}, target_id, application_id, wait_seconds)

    @mcp.tool()
    def discord_click_component(
        channel_id: str,
        message_id: str,
        custom_id: str,
        values: list[str] | None = None,
        wait_seconds: int = 15,
    ) -> dict:
        """Bot のメッセージのボタンを押す、またはセレクトメニューで values を選ぶ。custom_id は run_command の replies[].components か、
        このツールのエラーに出る一覧から取る。返り値は run_command と同じ形に、操作後のメッセージ（message_after）を足したもの。
        呼ぶ前に、押すボタンを利用者に確認すること。write_allow か write_allow_guilds で許可したチャンネルだけ通る。"""
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("clickComponent", channel_id, message_id, custom_id, values, wait_seconds)

    @mcp.tool()
    def discord_submit_modal(channel_id: str, modal_id: str, values: dict, wait_seconds: int = 15) -> dict:
        """run_command・click_component が返したモーダル（state=modal）を送信する。modal_id は modal.id、
        values は {入力欄の custom_id かラベル: 値}（modal.fields に一覧がある）。扱えるのはテキストの入力欄だけ。
        呼ぶ前に入力内容を利用者に確認すること。write_allow か write_allow_guilds で許可したチャンネルだけ通る。"""
        _require_write_allowed(cdp, channel_id)
        return cdp.call_api("submitModal", channel_id, modal_id, values, wait_seconds)

    @mcp.tool()
    def discord_api(method: str, path: str, body: dict | None = None) -> dict:
        """Discord.app の認証で REST API（https://discord.com/api/v9 からの相対パス）を呼び、{status, body} を返す。専用ツールに無い操作に使う。
        GET はどのパスでも通る（/auth 配下を除く）。例: GET /users/@me/channels（DM 一覧）、GET /guilds/{id}/messages/search?content=語、
        GET /channels/{id}/pins、GET /channels/{id}/threads/archived/public、GET /guilds/{id}/members/{user_id}。
        GET 以外は、許可したチャンネルの /channels/{id}/(messages|pins|typing|threads|thread-members|polls)/... と、
        スレッド自体の PATCH・DELETE だけ通る。例: PUT /channels/{id}/messages/{mid}/reactions/{絵文字（URL エンコード）}/@me（リアクション）、
        PUT /channels/{id}/pins/{mid}、PATCH /channels/{thread_id} {"archived": true, "locked": true}、PUT /channels/{thread_id}/thread-members/@me（参加）。
        GET 以外は外に出る操作なので、呼ぶ前に内容を利用者に確認すること。"""
        m = method.strip().lower()
        m = {"delete": "del"}.get(m, m)
        if m not in ("get", "post", "put", "patch", "del"):
            raise DiscordAppError("method は GET・POST・PUT・PATCH・DELETE のどれか")
        _check_request(cdp, m, path)
        return cdp.call_api("request", m, path, body)

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
