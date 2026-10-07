#!/usr/bin/env python3
"""常駐の playwright-mcp（HTTP）経由で、ログイン済みの自動化 Chrome の Slack Web クライアントを操作する。

各コマンドは browser_run_code_unsafe を 1 回呼び、その中で自分専用のタブを開いて閉じる。
共有コンテキストの current tab（他のセッションが使っているタブ）には触れない。

ワークスペースの対応は ~/.claude/local/slack-workspaces.json に置く:
  {"<domain>": {"team": "T0123456789", "home": "D0123456789"}}
<domain> は <domain>.slack.com の部分。home は開いて既読になっても困らない会話（Slackbot か自分の DM）。

使い方:
  slack_browser.py channels  --ws <domain>
  slack_browser.py history   --ws <domain> <channel_id> [--limit 30]
  slack_browser.py thread    <permalink>                 # https://<domain>.slack.com/archives/C.../p...
  slack_browser.py search    --ws <domain> "<query>" [--limit 20]
  slack_browser.py post      <permalink|channel_id> --file body.txt [--ws <domain>] [--send]

history・thread は開いたチャンネル・スレッドを既読にする（search と channels は home だけを開く）。
post は --send が無ければ送信先と本文を表示するだけで、ブラウザに触れない。
"""
import argparse
import json
import os
import re
import sys
import urllib.request

PORT = os.environ.get("PLAYWRIGHT_MCP_PORT", "8931")
URL = f"http://127.0.0.1:{PORT}/mcp"
CONFIG = os.path.expanduser(os.environ.get("SLACK_BROWSER_CONFIG", "~/.claude/local/slack-workspaces.json"))


def post_rpc(body, session_id=None, timeout=180):
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        session_id = response.headers.get("Mcp-Session-Id", session_id)
        result = None
        for line in response.read().decode().splitlines():
            if line.startswith("data:"):
                result = json.loads(line[5:].strip())
        return result, session_id


def run_code(code, timeout=180):
    _, sid = post_rpc({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "slack-browser", "version": "1"}},
    })
    post_rpc({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    result, _ = post_rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                          "params": {"name": "browser_run_code_unsafe", "arguments": {"code": code}}},
                         sid, timeout=timeout)
    if result is None:
        sys.exit("playwright-mcp から応答が無い")
    if "error" in result:
        sys.exit(f"MCP error: {result['error']}")
    text = "".join(c.get("text", "") for c in result["result"].get("content", []))
    if result["result"].get("isError"):
        sys.exit(text)
    # 応答は markdown。"### Result" の直後の 1 行が戻り値の JSON
    match = re.search(r"### Result\n(.*?)(?:\n### |\Z)", text, re.S)
    if not match:
        sys.exit(f"戻り値を読めない:\n{text[:2000]}")
    return json.loads(match.group(1).strip())


# ページ内で使う共通関数。message_container を読み、スクロールしながら集める
JS_LIB = r"""
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const readMessages = (root) => [...root.querySelectorAll('[data-qa="message_container"]')].map(m => {
  const a = m.querySelector('a.c-timestamp');
  const link = a ? a.href : null;
  const tsm = link && link.match(/\/p(\d{10})(\d{6})/);
  const reply = m.querySelector('[data-qa="reply_bar_count"]');
  const files = [...m.querySelectorAll('[data-qa="file_name"], .c-file__title')].map(f => f.innerText.trim()).filter(Boolean);
  return {
    ts: tsm ? `${tsm[1]}.${tsm[2]}` : null,
    author: m.querySelector('[data-qa="message_sender_name"]')?.innerText?.trim() || null,
    text: m.querySelector('[data-qa="message-text"]')?.innerText?.trim() ?? m.innerText.trim(),
    replies: reply ? reply.innerText.trim() : undefined,
    files: files.length ? files : undefined,
    link,
  };
}).filter(x => x.ts);
const collect = async (root, direction, limit) => {
  const sc = [...root.querySelectorAll('.c-scrollbar__hider')].find(e => e.scrollHeight > e.clientHeight) || null;
  const seen = new Map();
  const add = () => { for (const x of readMessages(root)) if (!seen.has(x.ts) || (!seen.get(x.ts).author && x.author)) seen.set(x.ts, x); };
  if (sc && direction === 'up') {
    // Slack はチャンネルごとのスクロール位置を覚えているので、最新まで送ってから遡る
    for (let i = 0, h = -1; i < 10 && sc.scrollHeight !== h; i++) { h = sc.scrollHeight; sc.scrollTop = sc.scrollHeight; await sleep(1000); }
  }
  add();
  if (sc) {
    if (direction === 'down') { sc.scrollTop = 0; await sleep(1200); add(); }
    let stale = 0;
    while (seen.size < limit && stale < 4) {
      const before = seen.size;
      if (direction === 'up') sc.scrollTop = Math.max(0, sc.scrollTop - sc.clientHeight * 0.8);
      else sc.scrollTop = sc.scrollTop + sc.clientHeight * 0.8;
      await sleep(1200);
      add();
      stale = seen.size === before ? stale + 1 : 0;
    }
  }
  let list = [...seen.values()].sort((a, b) => Number(a.ts) - Number(b.ts));
  let last = null;
  for (const x of list) { if (x.author) last = x.author; else x.author = last; }
  if (direction === 'up') list = list.slice(-limit);
  return list;
};
"""


def page_code(body):
    """自分専用のタブを開いて body を実行し、必ず閉じる関数を返す。body は p（新しいタブ）を使う"""
    return ("async (page) => {\n  const p = await page.context().newPage();\n  try {\n"
            + body + "\n  } finally { await p.close(); }\n}")


def load_ws(ws):
    """(team ID, home) を返す。home は、開いて既読になっても困らない起点の会話（自分か Slackbot の DM）"""
    try:
        with open(CONFIG) as f:
            config = json.load(f)
    except FileNotFoundError:
        sys.exit(f"{CONFIG} が無い。{{\"{ws}\": {{\"team\": \"T...\", \"home\": \"D...\"}}}} の形で作る")
    if ws not in config:
        sys.exit(f"{CONFIG} に {ws} が無い。登録済み: {', '.join(config)}")
    entry = config[ws]
    if not entry.get("home"):
        sys.exit(f"{CONFIG} の {ws} に home（Slackbot か自分の DM の ID）が無い")
    return entry["team"], entry["home"]


def parse_permalink(url):
    m = re.match(r"https://([\w-]+)\.slack\.com/archives/(\w+)/p(\d{10})(\d{6})", url)
    if not m:
        sys.exit(f"パーマリンクとして読めない: {url}")
    ws, channel, ts = m.group(1), m.group(2), f"{m.group(3)}.{m.group(4)}"
    q = re.search(r"thread_ts=([\d.]+)", url)
    return ws, channel, ts, (q.group(1) if q else None)


def goto_and_wait(url):
    return (f"    await p.goto({json.dumps(url)});\n"
            "    await p.locator('[role=\"treeitem\"]').first().waitFor({ timeout: 30000 }).catch(() => {});\n"
            "    if (!(await p.locator('[role=\"treeitem\"]').count())) return { error: 'クライアントが開かない（未ログインの可能性）: ' + p.url() };\n")


def cmd_channels(args):
    team, home = load_ws(args.ws)
    body = goto_and_wait(f"https://app.slack.com/client/{team}/{home}") + r"""
    await p.waitForTimeout(2000);
    return await p.evaluate(() => [...document.querySelectorAll('[role="treeitem"][aria-level="2"]')]
      .filter(e => /^[CDG][A-Z0-9]+$/.test(e.id))
      .map(e => ({ id: e.id, name: e.innerText.trim().split('\n').pop(),
                   unread: /unread/.test(e.innerHTML.slice(0, 2000)) || undefined })));
"""
    return run_code(page_code(body))


def cmd_search(args):
    team, home = load_ws(args.ws)
    body = goto_and_wait(f"https://app.slack.com/client/{team}/{home}") + f"""
    await p.waitForTimeout(1500);
    await p.locator('[data-qa="top_nav_search"]').click();
    await p.getByRole('combobox').first().waitFor({{ timeout: 15000 }});
    // 検索欄には前回の検索語が残る。流し込み（fill）は検索語として認識されないので打鍵する
    await p.keyboard.press('Meta+A'); await p.keyboard.press('Backspace');
    await p.keyboard.type({json.dumps(args.query)}, {{ delay: 40 }});
    await p.waitForTimeout(2500);
    // 先頭の候補が「検索結果を表示する」でないとき（チャンネル等）に Enter やクリックをすると、そのチャンネルを開いて既読にする
    const first = p.locator('#c-search_autocomplete__suggestion_0');
    if (!(await first.locator('[data-qa="search-query-entity-text-content"]').count())) {{
      const txt = (await first.count()) ? (await first.innerText()).replace(/\\s+/g, ' ') : null;
      await p.keyboard.press('Escape');
      return {{ error: '先頭の候補が検索ではないので中止した', suggestion: txt }};
    }}
    await first.click();
    await p.locator('[data-qa="search_result"], [data-qa="search_view"]').first().waitFor({{ timeout: 30000 }});
    await p.waitForTimeout(3000);
    return await p.evaluate(async (limit) => {{
      const sleep = (ms) => new Promise(r => setTimeout(r, ms));
      const seen = new Map();
      const add = () => {{
        for (const it of document.querySelectorAll('[data-qa="search_result"]')) {{
          const a = it.querySelector('a.c-timestamp');
          if (!a || seen.has(a.href)) continue;
          seen.set(a.href, {{
            channel: it.querySelector('[data-qa="search_result_channel_name"]')?.innerText?.trim().split('\\n').pop().trim() || null,
            author: it.querySelector('[data-qa="message_sender_name"]')?.innerText?.trim() || null,
            time: a.getAttribute('aria-label'),
            text: it.querySelector('[data-qa="message-text"]')?.innerText?.trim() || null,
            link: a.href,
          }});
        }}
      }};
      add();
      const sc = document.querySelector('[data-qa="search_view"] .c-scrollbar__hider');
      for (let stale = 0; sc && seen.size < limit && stale < 3;) {{
        const before = seen.size;
        sc.scrollTop += sc.clientHeight * 0.8; await sleep(1200); add();
        stale = seen.size === before ? stale + 1 : 0;
      }}
      const header = document.querySelector('[data-qa="search_view"] [role="list"]')?.getAttribute('aria-label');
      return {{ header, results: [...seen.values()].slice(0, limit) }};
    }}, {int(args.limit)});
"""
    return run_code(page_code(body), timeout=300)

def cmd_history(args):
    team, _ = load_ws(args.ws)
    body = (goto_and_wait(f"https://app.slack.com/client/{team}/{args.channel}")
            + "    await p.locator('[data-qa=\"message_pane\"] [data-qa=\"message_container\"]').first().waitFor({ timeout: 30000 });\n"
            + "    await p.waitForTimeout(1500);\n"
            + f"    return await p.locator('[data-qa=\"message_pane\"]').evaluate(async (root) => {{ {JS_LIB}\n return await collect(root, 'up', {int(args.limit)}); }});\n")
    return run_code(page_code(body), timeout=300)


def cmd_thread(args):
    ws, channel, ts, thread_ts = parse_permalink(args.url)
    team, _ = load_ws(ws)
    root_ts = thread_ts or ts
    body = (goto_and_wait(f"https://app.slack.com/client/{team}/{channel}/thread/{channel}-{root_ts}")
            + "    const pane = p.locator('[data-qa=\"threads_flexpane\"]');\n"
            + "    await pane.locator('[data-qa=\"message_container\"]').first().waitFor({ timeout: 30000 });\n"
            + "    await p.waitForTimeout(1500);\n"
            + f"    return await pane.evaluate(async (root) => {{ {JS_LIB}\n return await collect(root, 'down', 1000); }});\n")
    return run_code(page_code(body), timeout=300)


def cmd_post(args):
    text = open(args.file).read().rstrip("\n") if args.file != "-" else sys.stdin.read().rstrip("\n")
    if not text.strip():
        sys.exit("本文が空")
    if args.target.startswith("https://"):
        ws, channel, ts, thread_ts = parse_permalink(args.target)
        root_ts = thread_ts or ts
        in_thread = True
    else:
        if not args.ws:
            sys.exit("チャンネル ID を渡すときは --ws が要る")
        ws, channel, root_ts = args.ws, args.target, None
        in_thread = False
    team, _ = load_ws(ws)
    where = f"{ws} / {channel}" + (f" / thread {root_ts}" if in_thread else "（チャンネル本体）")
    if not args.send:
        return {"dry_run": True, "to": where, "text": text}
    url = (f"https://app.slack.com/client/{team}/{channel}/thread/{channel}-{root_ts}" if in_thread
           else f"https://app.slack.com/client/{team}/{channel}")
    body = goto_and_wait(url) + f"""
    const text = {json.dumps(text)};
    const inThread = {json.dumps(in_thread)};
    const root = inThread ? p.locator('[data-qa="threads_flexpane"]') : p.locator('body');
    const box = inThread
      ? root.locator('[data-qa="texty_input"]').first()
      : p.locator('[data-qa="message_input"]:not([data-qa="threads_flexpane"] *) [data-qa="texty_input"]').first();
    await box.waitFor({{ timeout: 30000 }}).catch(() => {{}});
    if (!(await box.count())) return {{ error: '入力欄が無い（投稿できないチャンネルの可能性）' }};
    await box.fill(text);
    await p.waitForTimeout(500);
    const typed = (await box.evaluate(e => [...e.querySelectorAll('p')].map(x => x.innerText).join('\\n'))).trim();
    if (typed.replace(/\\s+/g, '') !== text.replace(/\\s+/g, '')) {{
      await box.evaluate(e => {{ e.focus(); document.execCommand('selectAll'); document.execCommand('delete'); }});
      return {{ error: '入力欄の内容が本文と一致しないので送らなかった', typed }};
    }}
    const before = await root.locator('[data-qa="message_container"]').count();
    const send = inThread ? root.locator('[data-qa="texty_send_button"]').first()
                          : p.locator('[data-qa="texty_send_button"]:not([data-qa="threads_flexpane"] *)').first();
    await send.click();
    await p.waitForTimeout(3000);
    const links = await root.locator('[data-qa="message_container"] a.c-timestamp').evaluateAll(as => as.map(a => a.href));
    return {{ sent: true, to: {json.dumps(where)}, last_link: links[links.length - 1] || null }};
"""
    return run_code(page_code(body), timeout=300)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("channels"); s.add_argument("--ws", required=True)
    s = sub.add_parser("history"); s.add_argument("--ws", required=True); s.add_argument("channel"); s.add_argument("--limit", default=30)
    s = sub.add_parser("thread"); s.add_argument("url")
    s = sub.add_parser("search"); s.add_argument("--ws", required=True); s.add_argument("query"); s.add_argument("--limit", default=20)
    s = sub.add_parser("post"); s.add_argument("target"); s.add_argument("--file", required=True)
    s.add_argument("--ws"); s.add_argument("--send", action="store_true")
    args = ap.parse_args()
    out = {"channels": cmd_channels, "history": cmd_history, "thread": cmd_thread,
           "search": cmd_search, "post": cmd_post}[args.cmd](args)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if isinstance(out, dict) and out.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
