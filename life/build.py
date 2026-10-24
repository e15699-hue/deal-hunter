#!/usr/bin/env python3
"""好康生活 howkang-life 建置腳本：由母版產生全站靜態頁面。
用法：python3 build.py → 產出 index.html / style.css / 各頻道頁面 / sitemap.xml / robots.txt
全站採相對路徑，可同時部署在 life.howkang.com.tw 根目錄與 howkang.com.tw/life/ 預覽。
"""
import os, json

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://life.howkang.com.tw"

CHANNELS = [
    ("home",   "🏠", "居家裝修", "報價單、施工流程、材料與合約——裝修前先做功課，不怕被當盤子。", True),
    ("daily",  "💧", "民生查詢", "停水停電、菜價行情、垃圾車時間——官方資訊分散難查，我們幫你整理成一頁。", True),
    ("senior", "👵", "銀髮 3C", "長輩手機教學、防詐騙——字大、步驟清楚，子女也能直接傳給爸媽看。", False),
    ("health", "🏥", "健康查詢", "假日夜間看診、藥局營業時間——急著找醫生時不用再一間一間打電話。", False),
    ("study",  "📚", "學習考照", "技術士考照刷題與考試資訊——公開題庫整理好，照著練就對了。", False),
    ("ai",     "🤖", "AI 工具", "免費 AI 工具實測——文書、圖片、簡報，哪些真的好用，我們試給你看。", False),
    ("car",    "🚗", "愛車生活", "驗車、稅金、保險到期提醒——車子的例行大事，不再靠記憶。", False),
]
CH = {c[0]: c for c in CHANNELS}

CSS = """
:root{--brand:#D81B60;--brand2:#F06292;--ink:#212121;--sub:#616161;--bg:#FFF7F9;--card:#fff;--line:#F3D9E2;--radius:14px}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif;color:var(--ink);background:var(--bg);line-height:1.75;font-size:17px}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
header.site{background:linear-gradient(135deg,#D81B60,#F06292);color:#fff;padding:14px 16px;position:sticky;top:0;z-index:50;box-shadow:0 2px 10px rgba(216,27,96,.25)}
.hwrap{max-width:1080px;margin:0 auto;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.logo{font-size:24px;font-weight:900;color:#fff;letter-spacing:1px}
.logo small{display:block;font-size:12px;font-weight:400;opacity:.9;letter-spacing:0}
nav.main{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
nav.main a{color:#fff;font-size:15px;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.14)}
nav.main a:hover{background:rgba(255,255,255,.3);text-decoration:none}
nav.main a.on{background:#fff;color:var(--brand);font-weight:700}
main{max-width:1080px;margin:0 auto;padding:24px 16px 48px}
.hero{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:28px 24px;margin-bottom:24px}
.hero h1{font-size:30px;line-height:1.4;margin-bottom:8px}
.hero p{color:var(--sub)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px;display:block;color:var(--ink)}
.card:hover{text-decoration:none;border-color:var(--brand2);box-shadow:0 4px 16px rgba(216,27,96,.12)}
.card .ico{font-size:34px}
.card h3{font-size:20px;margin:6px 0}
.card p{color:var(--sub);font-size:15px}
.badge{display:inline-block;font-size:12px;padding:2px 10px;border-radius:999px;background:#FCE4EC;color:var(--brand);font-weight:700;margin-bottom:6px}
.badge.soon{background:#EEEEEE;color:#757575}
h2.sec{font-size:22px;margin:28px 0 12px;padding-left:10px;border-left:5px solid var(--brand)}
article.post{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:28px 26px}
article.post h1{font-size:27px;line-height:1.45;margin-bottom:6px}
.meta{color:var(--sub);font-size:14px;margin-bottom:18px}
article.post h2{font-size:21px;margin:24px 0 8px;color:#AD1457}
article.post h3{font-size:18px;margin:16px 0 6px}
article.post p{margin:8px 0}
article.post ul,article.post ol{margin:8px 0 8px 22px}
article.post li{margin:4px 0}
.tip{background:#FFF5F8;border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:16px 0}
.tip b{color:var(--brand)}
.note{font-size:14px;color:var(--sub)}
table.cmp{width:100%;border-collapse:collapse;margin:12px 0;font-size:15px}
table.cmp th,table.cmp td{border:1px solid var(--line);padding:8px 10px;text-align:left}
table.cmp th{background:#FCE4EC}
.toolbox{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:22px}
.toolbox label{font-weight:700;display:block;margin:12px 0 4px}
.toolbox input,.toolbox select{width:100%;max-width:420px;padding:10px;border:1px solid #E0A8BC;border-radius:8px;font-size:16px}
.btn{display:inline-block;background:var(--brand);color:#fff;border:none;padding:10px 22px;border-radius:999px;font-size:16px;cursor:pointer;margin-top:14px}
.btn:hover{background:#AD1457}
.result{margin-top:18px}
.result .item{border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:8px 0;background:#FFFBFC}
footer.site{border-top:1px solid var(--line);background:#fff;padding:24px 16px;color:var(--sub);font-size:14px}
.fwrap{max-width:1080px;margin:0 auto}
.crumb{font-size:14px;color:var(--sub);margin-bottom:12px}
.searchbar{display:flex;gap:8px;max-width:640px;margin:14px 0 6px}
.searchbar input{flex:1;padding:12px 14px;border:2px solid var(--brand2);border-radius:999px;font-size:17px;min-width:0}
.searchbar button{background:var(--brand);color:#fff;border:none;padding:12px 22px;border-radius:999px;font-size:16px;cursor:pointer;white-space:nowrap}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.chips span{font-size:14px;color:var(--sub);padding-top:4px}
.chips a{background:#FCE4EC;color:#AD1457;padding:5px 12px;border-radius:999px;font-size:14px}
.chips a:hover{text-decoration:none;background:#F8BBD0}
.alertbar{background:#FFF3E0;border:1px solid #FFCC80;border-radius:var(--radius);padding:14px 18px;margin-bottom:20px;font-size:16px}
.feed{display:flex;flex-direction:column;gap:12px}
.feeditem{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;display:block;color:var(--ink)}
.feeditem:hover{text-decoration:none;border-color:var(--brand2);box-shadow:0 4px 14px rgba(216,27,96,.10)}
.feeditem h3{font-size:19px;margin:2px 0 4px}
.feeditem p{color:var(--sub);font-size:15px}
.tag{display:inline-block;font-size:12px;font-weight:700;color:var(--brand);background:#FCE4EC;border-radius:6px;padding:1px 8px;margin-right:6px}
.fmeta{font-size:13px;color:#9E9E9E;margin-top:6px}
.ranklist{counter-reset:rk;list-style:none}
.ranklist li{counter-increment:rk;padding:9px 0;border-bottom:1px dashed var(--line);display:flex;gap:10px;align-items:baseline}
.ranklist li::before{content:counter(rk);background:var(--brand);color:#fff;font-weight:900;border-radius:8px;min-width:26px;height:26px;display:inline-flex;align-items:center;justify-content:center;font-size:14px}
.more{display:inline-block;margin-top:10px;font-weight:700}
@media(max-width:640px){.hero h1{font-size:24px}article.post{padding:20px 16px}nav.main{margin-left:0;flex-wrap:nowrap;overflow-x:auto;-webkit-overflow-scrolling:touch;padding-bottom:4px}nav.main a{white-space:nowrap}.searchbar button{padding:12px 16px}}
"""

def head(title, desc, depth, active=None, extra=""):
    up = "../" * depth
    nav = ""
    for slug, ico, name, _d, live in CHANNELS:
        cls = ' class="on"' if active == slug else ""
        nav += f'<a href="{up}{slug}/"{cls}>{ico} {name}</a>'
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}｜好康生活</title>
<meta name="description" content="{desc}">
<link rel="stylesheet" href="{up}style.css">
{extra}
</head>
<body>
<header class="site"><div class="hwrap">
<a class="logo" href="{up}">好康生活<small>新聞不報、但你天天要查的生活大小事</small></a>
<nav class="main"><a href="{up}search.html">🔍 搜尋</a>{nav}</nav>
</div></header>
<main>
"""

def foot(depth):
    up = "../" * depth
    return f"""</main>
<footer class="site"><div class="fwrap">
<p><b>好康生活</b> 是 <a href="https://howkang.com.tw/" target="_blank" rel="noopener">好康網</a> 的姊妹站：好康網幫你找省錢好康，好康生活幫你查生活大小事。</p>
<p style="margin-top:8px">本站內容為生活資訊整理，實際公告與價格以各官方單位發布為準。</p>
</div></footer>
</body>
</html>
"""

def w(relpath, html):
    p = os.path.join(ROOT, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", relpath, len(html), "bytes")


# ---------------- 站內搜尋索引 ----------------
PAGES = [
    ("home/quote.html", "居家裝修", "裝修報價單怎麼看？先搞懂這 5 件事", "報價單 估價 追加工程 付款比例 一式 單價 裝修", "約 5 分鐘"),
    ("home/designer.html", "居家裝修", "設計師怎麼挑？從丈量到簽約的檢查清單", "設計師 設計費 丈量費 監工費 圖面 裝修", "約 5 分鐘"),
    ("home/cabinet.html", "居家裝修", "系統櫃怎麼計價？一尺多少錢才合理", "系統櫃 一尺 計價 板材 抽屜 五金 衣櫃", "約 4 分鐘"),
    ("home/process.html", "居家裝修", "裝修施工流程順序：為什麼不能跳著做", "施工流程 順序 拆除 水電 泥作 木作 油漆 工期 裝修", "約 5 分鐘"),
    ("home/contract.html", "居家裝修", "裝修合約注意事項：簽下去之前逐條檢查", "合約 保固 驗收 尾款 追加 減帳 裝修", "約 5 分鐘"),
    ("daily/outage.html", "民生查詢", "停水停電查詢", "停電 停水 台電 台水 計畫性停電 1911 跳電", "查詢工具"),
    ("daily/vegprice.html", "民生查詢", "菜價行情查詢", "菜價 批發市場 行情 蔬菜 農業部 買菜", "查詢工具"),
    ("daily/garbage.html", "民生查詢", "垃圾車時間查詢", "垃圾車 清運時間 環保局 倒垃圾 樂圾車", "查詢工具"),
]

def page_search():
    data = json.dumps([{"u": u, "c": c, "t": t, "k": k} for u, c, t, k, _m in PAGES], ensure_ascii=False)
    body = """
<p class="crumb"><a href="./">首頁</a> ／ 搜尋</p>
<div class="hero"><h1>🔍 查生活大小事</h1>
<p>輸入你想查的事情，例如「停電」「報價單」「垃圾車」。</p>
<div class="searchbar"><input id="q" type="text" placeholder="想查什麼？"><button id="go">搜尋</button></div>
</div>
<div class="feed" id="res" style="margin-top:16px"></div>
<script>
const PAGES = __DATA__;
const res = document.getElementById('res');
function run() {
  const q = document.getElementById('q').value.trim();
  const hit = PAGES.filter(p => !q || (p.t + p.k + p.c).includes(q));
  res.innerHTML = hit.length
    ? hit.map(p => '<a class="feeditem" href="' + p.u + '"><span class="tag">' + p.c + '</span><h3>' + p.t + '</h3></a>').join('')
    : '<p>目前站內還沒有這題的整理。先看看<a href="daily/outage.html">停水停電查詢</a>或<a href="home/">居家裝修</a>，或到姊妹站好康網找好康。</p>';
}
const qs = new URLSearchParams(location.search).get('q');
if (qs) { document.getElementById('q').value = qs; }
run();
document.getElementById('go').addEventListener('click', run);
document.getElementById('q').addEventListener('keydown', e => { if (e.key === 'Enter') run(); });
</script>
"""
    body = body.replace("__DATA__", data)
    w("search.html", head("搜尋", "在好康生活站內搜尋：停電、菜價、垃圾車、裝修報價單、系統櫃、合約等生活大小事。", 0) + body + foot(0))

# ---------------- 首頁 ----------------
def page_index():
    cards = ""
    for slug, ico, name, desc, live in CHANNELS:
        if live:
            cards += f'<a class="card" href="{slug}/"><span class="badge">已上線</span><div class="ico">{ico}</div><h3>{name}</h3><p>{desc}</p></a>'
        else:
            cards += f'<div class="card"><span class="badge soon">籌備中</span><div class="ico">{ico}</div><h3>{name}</h3><p>{desc}</p></div>'
    feed = ""
    for u, c, t, _k, m in PAGES:
        feed += f'<a class="feeditem" href="{u}"><span class="tag">{c}</span><h3>{t}</h3><p class="fmeta">閱讀時間 {m}</p></a>'
    body = f"""
<div class="hero">
<h1>新聞不報、但你天天要查的生活大小事</h1>
<p>停水停電、菜價、裝修報價、長輩手機問題……官方都有公布，卻散在十幾個網站、格式又難查。先搜尋看看，你要查的可能已經整理好了。</p>
<form class="searchbar" action="search.html" method="get"><input name="q" type="text" placeholder="想查什麼？例如：停電、菜價、報價單"><button type="submit">搜尋</button></form>
<div class="chips"><span>大家都在查：</span><a href="daily/outage.html">停電查詢</a><a href="daily/vegprice.html">今天菜價</a><a href="daily/garbage.html">垃圾車時間</a><a href="home/quote.html">裝修報價單</a><a href="home/cabinet.html">系統櫃價格</a></div>
</div>
<div class="alertbar">🌧️ <b>天氣與連假提醒：</b>颱風、停班停課與連假期間，垃圾清運與停水停電安排幾乎每次都會變動，出門前先看 <a href="daily/garbage.html">垃圾車時間查詢</a> 與 <a href="daily/outage.html">停水停電查詢</a> 的官方公告整理。</div>
<h2 class="sec">頻道總覽</h2>
<div class="grid">{cards}</div>
<h2 class="sec">最新整理</h2>
<div class="feed">{feed}</div>
<h2 class="sec">這個站怎麼來的</h2>
<div class="hero">
<p>好康生活是 <a href="https://howkang.com.tw/" target="_blank" rel="noopener">好康網</a> 的姊妹站。我們發現：大家每天 Google 的問題，一大半不是「哪裡便宜」，而是「這件事到底怎麼辦」。所以我們把這些題目分門別類做成功課與查詢工具，慢慢補齊每一個頻道——先求正確、好查，再求多。</p>
</div>
"""
    w("index.html", head("好康生活", "新聞不報、但你天天要查的生活大小事：居家裝修、民生查詢、銀髮 3C、健康查詢、學習考照、AI 工具、愛車生活，一站整理。", 0) + body + foot(0))

# ---------------- 頻道頁 ----------------
HOME_ARTICLES = [
    ("quote", "裝修報價單怎麼看？先搞懂這 5 件事", "報價單不是比總價就好：項目拆分、單位、品牌型號、付款比例、追加工程，每一項都藏著日後爭議的種子。"),
    ("designer", "設計師怎麼挑？從丈量到簽約的檢查清單", "設計費怎麼算、圖面要交付哪些、監工費是什麼——挑設計師之前先把遊戲規則弄清楚。"),
    ("cabinet", "系統櫃怎麼計價？一尺多少錢才合理", "系統櫃用「尺」計價，板材、五金、抽屜都分開算。先看懂計價方式，才不會丈量完才發現預算爆掉。"),
    ("process", "裝修施工流程順序：為什麼不能跳著做", "拆除、水電、泥作、木作、油漆、系統櫃——順序錯了，輕則重工，重則漏水。本篇把完整流程與各階段檢查點整理給你。"),
    ("contract", "裝修合約注意事項：簽下去之前逐條檢查", "分階段付款、追加減帳簽認、保固條款、驗收方式——合約是裝修過程中最重要的保險，簽約前花十分鐘看完這篇。"),
]

def page_home_channel():
    items = ""
    meta = {u.split("/")[-1].replace(".html", ""): m for u, _c, _t, _k, m in PAGES}
    for slug, t, d in HOME_ARTICLES:
        items += f'<a class="feeditem" href="{slug}.html"><h3>{t}</h3><p>{d}</p><p class="fmeta">閱讀時間 {meta.get(slug, "約 5 分鐘")}</p></a>'
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ 居家裝修</p>
<div class="hero"><h1>🏠 居家裝修</h1>
<p>裝修是大多數人一生花費前幾名的大事，偏偏資訊最不透明。我們只做一件事：把報價、流程、材料、合約這些「行內常識」寫成白話文，讓你做決定之前心裡有底。本站只提供知識整理，不評論、不推薦任何店家。</p></div>
<h2 class="sec">裝修前必讀</h2>
<div class="feed">{items}</div>
<h2 class="sec">延伸：租屋看房</h2>
<div class="hero"><p>還沒買房、先租屋？看房時該檢查的壁癌、水壓、手機訊號、隔音與合約陷阱，我們整理在之後的「租屋看房防雷」專題中（籌備中）。</p></div>
"""
    w("home/index.html", head("居家裝修", "裝修報價單、設計師挑選、系統櫃計價、施工流程、合約注意事項——裝修前必讀的白話知識整理。", 1, "home") + body + foot(1))

def page_daily_channel():
    body = """
<p class="crumb"><a href="../">首頁</a> ／ 民生查詢</p>
<div class="hero"><h1>💧 民生查詢</h1>
<p>停水、停電、菜價、垃圾車——這些公告官方都有發布，卻分散在不同單位的網站裡，手機上尤其難查。這個頻道把官方公開資料整理成好查的工具頁，資料來源都標得清清楚楚，實際內容以官方公告為準。</p></div>
<h2 class="sec">查詢工具</h2>
<div class="grid">
<a class="card" href="outage.html"><div class="ico">💡</div><h3>停水停電查詢</h3><p>台電計畫性停電公告即時查詢（官方開放資料）；停水公告整理自來水公司查詢入口與看懂公告的方法。</p></a>
<a class="card" href="vegprice.html"><div class="ico">🥬</div><h3>菜價行情查詢</h3><p>農產品批發市場交易行情（農業部開放資料）：查今天各市場的蔬菜批發價，出門買菜前先看一眼。</p></a>
<a class="card" href="garbage.html"><div class="ico">🚛</div><h3>垃圾車時間查詢</h3><p>各縣市垃圾清運時間與即時位置的官方查詢入口總整理，照縣市找，不用再翻里辦公室公告。</p></a>
</div>
"""
    w("daily/index.html", head("民生查詢", "停水停電、菜價行情、垃圾車時間——官方公開資訊整理成好查的一頁。", 1, "daily") + body + foot(1))

def page_soon(slug):
    _s, ico, name, desc, _l = CH[slug]
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ {name}</p>
<div class="hero"><h1>{ico} {name}</h1>
<p>{desc}</p>
<p style="margin-top:12px"><span class="badge soon">籌備中</span></p>
<p>這個頻道正在準備中。我們會先把內容做到正確、好查再上線，不搶快。先去看看已經上線的 <a href="../home/">居家裝修</a> 與 <a href="../daily/">民生查詢</a>，或到姊妹站 <a href="https://howkang.com.tw/" target="_blank" rel="noopener">好康網</a> 找今天的好康。</p></div>
"""
    w(f"{slug}/index.html", head(name, desc, 1, slug) + body + foot(1))


# ---------------- 居家裝修文章 ----------------
def article(slug, title, desc, body_html):
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">居家裝修</a> ／ {title}</p>
<article class="post">
<h1>{title}</h1>
<p class="meta">好康生活・居家裝修頻道｜本篇為知識整理，不評論、不推薦任何店家；價格資訊為市場常見範圍，實際以各地行情與正式報價為準。</p>
{body_html}
<div class="tip"><b>看完接著讀：</b> <a href="./">回居家裝修頻道</a> 看其他篇：報價單、設計師、系統櫃、施工流程、合約，五篇一起看，裝修前功課就做滿了。</div>
</article>
<h2 class="sec">熱門閱讀</h2>
<div class="hero"><ol class="ranklist">__HOT__</ol></div>
"""
    others = [(u.split("/")[-1], t) for u, c, t, _k, _m in PAGES if c == "居家裝修" and not u.endswith(slug + ".html")]
    hot = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in others)
    body = body.replace("__HOT__", hot)
    w(f"home/{slug}.html", head(title, desc, 1, "home") + body + foot(1))

def articles():
    article("quote", "裝修報價單怎麼看？先搞懂這 5 件事",
    "報價單不是比總價就好：項目拆分、單位數量、材料品牌型號、付款比例、追加工程，這 5 件事看懂，裝修爭議先少一半。",
    """
<p>拿到裝修報價單，很多人只看最後一行的總價。總價當然重要，但日後會不會追加、會不會吵架，關鍵在總價「怎麼組成的」。以下 5 件事，簽約前逐項對照檢查。</p>
<h2>1. 項目有沒有拆細</h2>
<p>好的報價單會把工程拆成：拆除、水電、泥作、木作、油漆、系統櫃等類別，每類再列明細。最怕看到「木作工程　一式　350,000」這種寫法——「一式」代表沒人知道裡面包了什麼，日後對方說「這個不在一式裡面」你也無從反駁。要求對方把每一項的內容寫清楚，是屋主最基本的自保。</p>
<h2>2. 單位與數量對不對</h2>
<p>不同工程的計價單位不同，看錯單位就會誤判價格：</p>
<table class="cmp"><tr><th>工程</th><th>常見單位</th><th>意思</th></tr>
<tr><td>油漆、泥作（貼磚）</td><td>坪</td><td>以施工面積計價，先確認坪數怎麼量</td></tr>
<tr><td>木作櫃體、天花板</td><td>尺／坪</td><td>櫃體常用長度（尺），天花板用坪</td></tr>
<tr><td>水電配管、插座</td><td>迴路／組／點</td><td>一組迴路或一個出線點計價</td></tr>
<tr><td>拆除、清運</td><td>車／式</td><td>清運常以車次計，要問一車多大、包幾車</td></tr></table>
<p>數量自己也要粗算一次：例如油漆坪數大約是室內地坪的 2.5～3 倍（牆面＋天花），數量差太多就要問清楚。</p>
<h2>3. 材料品牌與型號有沒有寫明</h2>
<p>「矽酸鈣板」「系統板材」只是材料大類，同類裡等級差很多。報價單上應該寫到品牌、系列或等級（例如板材的耐燃等級、五金的品牌）。寫得越具體，日後驗收越有依據；只寫大類，等於把選料的權力全部交給對方。</p>
<h2>4. 付款比例合不合理</h2>
<p>常見的分期方式是簽約、開工、階段驗收、完工驗收分段付，重點是「付款永遠不要跑在進度前面」。簽約金比例過高（例如一開口就要五成）就要特別小心；每一期付款前，先確認該階段的工程確實完成了再付。</p>
<h2>5. 追加工程怎麼算，先講好</h2>
<p>裝修做到一半發現要追加（例如拆開才發現管線老舊），是常態不是意外。簽約前先問清楚：追加工程的單價怎麼計算、追加前會不會先出書面報價經你同意才施工。原則是「沒簽認、不施工、不同意、不付錢」，口頭講好的一律請對方補上書面。</p>
<div class="tip"><b>一句話總結：</b>報價單的價值不在總價，在明細。拆得越細、寫得越清楚的報價單，日後越少爭議——這和價格高低無關，是做事方式的問題。</div>
""")

    article("designer", "設計師怎麼挑？從丈量到簽約的檢查清單",
    "設計費怎麼算、丈量費是什麼、圖面要交付哪些、監工費怎麼收——挑設計師前先把遊戲規則弄懂，溝通成本省一半。",
    """
<p>第一次裝修的人常有的疑問：設計師到底在收什麼錢？丈量要錢、設計要錢、監工又要錢？先把收費結構弄清楚，再來談挑人，就不會在第一關就糊里糊塗簽約。</p>
<h2>設計相關費用，通常有這幾種</h2>
<ul>
<li><b>丈量費</b>：到府量測與初步諮詢的費用，常見作法是簽約後可折抵設計費。是否折抵、折抵條件，問清楚再付。</li>
<li><b>設計費</b>：多以「每坪」計價，依設計師資歷與案件複雜度差異很大。確認設計費包含哪些圖面（見下一段），只給示意圖和給到完整施工圖，是完全不同的工作量。</li>
<li><b>監工費</b>：設計師代為監工、與工班協調的費用，有的以工程總價的百分比計，有的含在整體報價中。要問清楚監工的頻率（多久到場一次）與回報方式。</li>
<li><b>工程費</b>：實際施工的費用，與設計費分開看待。有些公司設計與工程同包，有些只做設計、工程另找工班，兩種模式沒有絕對好壞，重點是責任歸屬寫清楚。</li>
</ul>
<h2>簽約前要確認交付的圖面</h2>
<p>設計不是只看漂亮的 3D 圖。對施工真正重要的是圖面是否完整，簽約前逐項確認會交付：</p>
<ol>
<li>平面配置圖（傢俱、隔間位置）</li>
<li>天花板圖、燈具配置圖</li>
<li>水電配置圖（插座、開關、給排水位置）</li>
<li>各立面圖與櫃體施工圖</li>
<li>材料表（品牌、型號、色號）</li>
</ol>
<p>3D 模擬圖可以幫助想像，但不能取代施工圖。合約裡把交付圖面列表寫明，日後驗收才有依據。</p>
<h2>挑人時觀察這幾件事</h2>
<ul>
<li><b>作品要看「完工照」不要只看渲染圖</b>，並問清楚哪些是本人實際經手的案件。</li>
<li><b>溝通方式</b>：裝修期長達數月，回訊息的速度、說明是否耐心，比名氣更影響你的實際體驗。</li>
<li><b>報價透明度</b>：願意把報價拆細、把「不包含哪些項目」先講明的人，日後追加爭議通常比較少（報價單怎麼看，可參考本頻道的報價單專篇）。</li>
<li><b>合約與公司登記</b>：以公司或工作室名義簽約、合約條款完整（含工期、付款、保固），是基本門檻。</li>
</ul>
<div class="tip"><b>提醒：</b>設計師的風格合不合，和專業度是兩回事。先確認遊戲規則（費用、圖面、合約）都合理，再從合規的人選裡挑風格喜歡的，順序不要反過來。</div>
""")

    article("cabinet", "系統櫃怎麼計價？一尺多少錢才合理",
    "系統櫃以「尺」計價，板材等級、五金、抽屜都分開算。看懂計價邏輯與常見加價項目，丈量完才不會被總價嚇到。",
    """
<p>系統櫃是裝修預算裡最容易「丈量前一個價、丈量後變另一個價」的項目。原因不是誰黑心，而是它的計價方式和一般人想的不一樣：不是算整座多少錢，而是長度、深度、板材、配件一項一項疊上去的。</p>
<h2>基本計價：以「尺」為單位</h2>
<p>系統櫃最常見的計價單位是「尺」（台尺，1 尺約 30.3 公分），以櫃體的正面寬度計算，深度則有標準深度（常見約 40～60 公分，衣櫃較深）。報價邏輯大致是：寬度幾尺 × 每尺單價 ＝ 櫃體基本價。每尺單價會隨板材等級、門片材質、高度（做到頂會加價）而不同，從每尺數千元到上萬元都有，落差主要來自材料與作法，不要只拿單一數字跨店比價——先確認對方報的單價包含什麼。</p>
<h2>價格差在哪：板材與門片</h2>
<ul>
<li><b>桶身板材</b>：常見為塑合板、美耐皿板等，等級看厚度、耐潮與甲醛等級（認明有標示的低甲醛等級，如 F1／E0 等標示）。廚房、浴室附近等潮濕區，耐潮性更重要。</li>
<li><b>門片</b>：平板門最經濟，造型門、玻璃門、鋁框門都會加價。</li>
<li><b>背板與封邊</b>：看不到的地方最容易有等級差，簽約前問清楚背板厚度與封邊作法。</li>
</ul>
<h2>最容易漏算的加價項目</h2>
<ol>
<li><b>抽屜</b>：幾乎都是另計，一個抽屜依滑軌等級（一般滑軌／緩衝滑軌）計價。</li>
<li><b>五金配件</b>：拉籃、升降衣桿、褲架、格子抽、把手升級，多為選配另計。</li>
<li><b>鉸鏈</b>：一般鉸鏈與緩衝鉸鏈價差不大，但數量一多就是一筆，確認報價含哪一種。</li>
<li><b>特殊尺寸</b>：超高、超深、轉角櫃、斜角處理，通常會有加工費。</li>
<li><b>丈量與設計</b>：有些含在總價內、有些另計，先問。</li>
</ol>
<h2>下單前的檢查動作</h2>
<ul>
<li>要求報價單列出：每座櫃子的寬度（尺）、單價、板材與門片材質、抽屜與配件的數量與單價。</li>
<li>確認總價是否含安裝、運送、收尾清潔，還是另計。</li>
<li>圖面確認後才下單製作，現場尺寸以丈量為準，自己的預估只拿來抓預算。</li>
</ul>
<div class="tip"><b>一句話總結：</b>系統櫃比價要比「同板材、同配件、同含安裝」的總價，只比每尺單價最容易被配件加價追回來。</div>
""")

    article("process", "裝修施工流程順序：為什麼不能跳著做",
    "拆除、水電、泥作、木作、油漆、系統櫃、清潔、驗收——順序錯了輕則重工、重則日後漏水。完整流程與各階段檢查點一次整理。",
    """
<p>裝修是一連串「前面的決定後面的事」的工程：插座位置在牆壁封起來之前就要定案，磁磚貼下去之後想改排水就得打掉重來。了解標準流程順序，不只是長知識，更是你在每個階段知道「現在該確認什麼」的依據。</p>
<h2>標準流程一覽</h2>
<table class="cmp"><tr><th>順序</th><th>階段</th><th>主要工作</th><th>屋主檢查點</th></tr>
<tr><td>1</td><td>保護工程</td><td>公共區域與室內既有部分包覆保護</td><td>電梯、走道保護是否確實，避免鄰里糾紛</td></tr>
<tr><td>2</td><td>拆除</td><td>拆除舊裝潢、隔間、衛浴設備，清運廢棄物</td><td>確認拆除範圍與圖面一致，承重牆不可動</td></tr>
<tr><td>3</td><td>水電</td><td>配管配線、給排水、插座與迴路配置</td><td>插座位置與數量逐一對圖確認，這是最後能改的時機</td></tr>
<tr><td>4</td><td>泥作</td><td>砌牆、防水、貼磚、地面整平</td><td>浴室防水要做試水（蓄水測試）再貼磚</td></tr>
<tr><td>5</td><td>木作</td><td>天花板、木作櫃體、門框等木工</td><td>天花板高度、冷氣與燈具位置配合</td></tr>
<tr><td>6</td><td>油漆</td><td>批土、打磨、上漆</td><td>顏色先試色再全面施作，完工在不同光線下檢查</td></tr>
<tr><td>7</td><td>系統櫃與廚具安裝</td><td>工廠製作的櫃體到場組裝</td><td>門片開啟、抽屜滑順度、收邊是否平整</td></tr>
<tr><td>8</td><td>設備安裝與收尾</td><td>燈具、衛浴設備、開關面板、五金</td><td>逐項試用：水龍頭、馬桶沖水、插座通電</td></tr>
<tr><td>9</td><td>清潔與驗收</td><td>細清後逐項驗收、列缺失清單改善</td><td>缺失改善完成才付尾款（見合約專篇）</td></tr></table>
<h2>為什麼順序不能亂</h2>
<ul>
<li><b>水電在泥作之前</b>：管線要埋進牆地，泥作做完才要改管線，就得打除重作。</li>
<li><b>防水在貼磚之前</b>：防水層在磁磚底下，順序反了等於沒做。</li>
<li><b>油漆在木作之後</b>：木作施工的粉塵與碰撞會弄髒新漆面。</li>
<li><b>系統櫃在地板完成之後丈量安裝</b>：地板高度會影響櫃體尺寸，先裝櫃再鋪地板容易出誤差。</li>
</ul>
<h2>工期怎麼抓</h2>
<p>一般住宅裝修從數週到數月不等，影響最大的是工程範圍與訂製品（如系統櫃、廚具）的製作時間。簽約時要求合約載明預定工期與各階段里程碑，比只寫一個完工日期更能掌握進度；若有延誤，原因與責任也要有約定（合約怎麼寫，見本頻道合約專篇）。</p>
<div class="tip"><b>給第一次裝修的你：</b>每個階段完工時到現場拍照留存（尤其是水電配管、防水這些之後會被蓋住的部分），日後維修或有爭議時，這些照片就是最有力的紀錄。</div>
""")

    article("contract", "裝修合約注意事項：簽下去之前逐條檢查",
    "分階段付款、追加減帳簽認、保固條款、驗收與尾款——裝修合約是整個工程最重要的保險，簽約前花十分鐘逐條看完這篇。",
    """
<p>裝修金額大、工期長、中間變數多，口頭約定在出爭議時幾乎沒有保障。合約不是不信任對方，而是讓雙方對「做什麼、多少錢、多久、壞了誰負責」有同一份文字依據。以下條款，簽約前逐條確認有沒有寫進去。</p>
<h2>1. 工程範圍與圖說附件</h2>
<p>合約應附上設計圖、施工圖與報價明細表，並註明「圖說與報價單為合約附件」。日後對方說「這個沒包含」，翻附件就知道。報價單的明細怎麼看，可先讀本頻道的報價單專篇。</p>
<h2>2. 總價與付款方式</h2>
<ul>
<li>總價是「含稅」還是「未稅」，要寫清楚。</li>
<li>付款分階段綁進度：常見為簽約、開工、各階段驗收、完工驗收分期給付，每期比例白紙黑字。</li>
<li>保留一筆尾款在「驗收完成、缺失改善後」才給付，這是你確保對方把收尾做好的籌碼。</li>
<li>付款方式留紀錄（匯款優於現金），每筆付款請對方簽收或開立收據。</li>
</ul>
<h2>3. 追加與減帳的規則</h2>
<p>中途追加工程在所難免，合約要先約定：追加項目須經雙方書面簽認（寫明項目與金額）後才施作，未經簽認的追加，費用的認定方式也要先講明。減帳（取消項目）同理，白紙黑字才不會各說各話。</p>
<h2>4. 工期與延誤處理</h2>
<p>寫明開工日、預定完工日，以及延誤的處理方式（例如可歸責於施工方時的約定）。也別忘了反過來：若因屋主變更設計導致延誤，工期順延是合理的，重點是雙方規則對等、事先講明。</p>
<h2>5. 保固條款</h2>
<ul>
<li>保固範圍：哪些項目保固（常見如防水、結構性施工、設備各有不同年限與範圍）。</li>
<li>保固起算日：通常以驗收完成日起算，寫清楚。</li>
<li>保固期內的報修方式與回應時間，有寫比沒寫好。</li>
</ul>
<h2>6. 驗收方式</h2>
<p>約定完工後雙方共同驗收，缺失列成清單、改善期限寫明，改善完成再付尾款。驗收時逐項試用設備（水、電、門窗、櫃體五金），不要只用眼睛看外觀。</p>
<h2>7. 解約與爭議處理</h2>
<p>約定任一方解約的條件與已完成工程的結算方式，以及爭議處理途徑（例如先協商、再循調解或法律途徑）。用不到最好，但寫了才有依據。</p>
<div class="tip"><b>最後提醒：</b>簽約前把合約帶回家慢慢看完，有看不懂的條款就問，合理的業者不會催你當場簽。政府也有公布室內裝修相關的契約範本可供對照，簽約前花一點時間比對，是整個裝修最划算的十分鐘。</div>
""")


# ---------------- 民生查詢工具頁 ----------------
TAIPOWER_LINKS = [
    ("台中區營業處", "https://service.taipower.com.tw/branch/d105/xcnotice?xsmsid=0M242581317628413301"),
    ("彰化區營業處", "https://service.taipower.com.tw/branch/d106/xcnotice?xsmsid=0M242581314418510444"),
    ("高雄區營業處", "https://service.taipower.com.tw/branch/d109/xcnotice?xsmsid=0M242581310382588530"),
    ("屏東區營業處", "https://service.taipower.com.tw/branch/d110/xcnotice?xsmsid=0M242581319136855888"),
    ("鳳山區營業處", "https://service.taipower.com.tw/branch/d119/xcnotice?xsmsid=0M242581312415567180"),
]

def page_outage():
    links = "、".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in TAIPOWER_LINKS)
    body = """
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">民生查詢</a> ／ 停水停電查詢</p>
<div class="hero"><h1>💡 停水停電查詢</h1>
<p>「計畫性停電」是台電為了施工、換變壓器、遷移線路排定的停電（不是缺電限電），公告其實都有，只是藏在各區營業處的網頁裡很難查。下面這個工具把台電官方公告整理成可以打字搜尋的列表：輸入你家附近的路名或區名，就能看近期會不會停電。</p></div>

<h2 class="sec">計畫性停電查詢（台電官方公告整理）</h2>
<div class="toolbox">
<label for="q">輸入路名、區名或鄉鎮（例如：西屯、工業區一路、左營）</label>
<input id="q" type="text" placeholder="輸入關鍵字後按查詢">
<label for="b">區營業處</label>
<select id="b"><option value="">全部區處</option></select>
<button class="btn" id="go">查詢</button>
<p class="note" id="stat">資料載入中…</p>
<div class="result" id="res"></div>
<p class="note">資料來源：台灣電力公司各區營業處「計畫性工作停電公告」。本頁為定期整理的快照（整理時間見上方），最新與完整資訊請以台電官方公告為準；目前涵蓋台中、彰化、高雄、屏東、鳳山 5 個區營業處，其他區處陸續加入中。官方原頁：__LINKS__</p>
</div>

<h2 class="sec">突然停電怎麼辦（非計畫性）</h2>
<div class="hero">
<p>不在上方公告裡、卻突然沒電，通常是設備故障或天災造成的突發停電，不會事先公告。可以這樣處理：</p>
<ul style="margin:8px 0 8px 22px">
<li>先看鄰居家有沒有電，確認是自家跳電還是整區停電。</li>
<li>整區停電：撥台電客服 <b>1911</b> 通報或詢問復電進度，並上台電官網「停電查詢」系統看搶修狀態。</li>
<li>看到電線掉落或外露，<b>不要碰觸</b>，立刻打 1911 通知台電。</li>
<li>停電時先拔掉精密電器插頭（電腦、電視），復電瞬間的電壓波動比較傷機器；冰箱門盡量不要開，食物保冷可以撐比較久。</li>
</ul>
</div>

<h2 class="sec">停水查詢：看台水公告</h2>
<div class="hero">
<p>停水公告由台灣自來水公司發布在「台水停水資訊網」（wateroff.water.gov.tw），可以依地址查詢自家是否在停水範圍；台水也有官方 LINE「停水公告查詢系統」，訂閱並輸入住址後，有停水會提前推播通知——這是目前最不會漏掉停水消息的方法，建議長輩也一起訂閱。</p>
<h3 style="margin-top:14px">停水前，台水提醒的 5 件事</h3>
<ol style="margin:8px 0 8px 22px">
<li><b>提前 6 小時完成儲水</b>，避免大家集中在停水前大量取水，管線末端反而提前沒水。</li>
<li><b>關閉抽水機、加壓馬達</b>電源，避免缺水空轉損壞甚至引發火災；電熱水器也要依安全規範處理。</li>
<li>進水口低於地面的建築，停水期間<b>關閉總表前制水閥</b>，降低虹吸污染風險。</li>
<li>用橡皮管接水時，<b>管口不要浸在水裡</b>，避免虹吸造成二次污染。</li>
<li>復水後先開水閥<b>排氣</b>再正常用水；管線末端或地勢較高處，水壓恢復會比較慢。</li>
</ol>
<p class="note">（整理自台灣自來水公司停水宣導資訊。）</p>
</div>
<script>
const FW = s => s.replace(/[０-９]/g, c => String.fromCharCode(c.charCodeAt(0) - 0xFEE0));
const qp = new URLSearchParams(location.search).get('q');
if (qp) document.getElementById('q').value = qp;
let DATA = null;
fetch('outages/index.json').then(r => r.json()).then(async idx => {
  const sel = document.getElementById('b');
  [...new Set(idx.branches.map(b => b.name))].forEach(n => { const o = document.createElement('option'); o.value = n; o.textContent = n; sel.appendChild(o); });
  const parts = await Promise.all(idx.branches.map(b =>
    fetch('outages/' + b.file).then(r => r.json()).then(d => d.items.map(it => ({...it, branch: d.branch}))).catch(() => [])
  ));
  const items = parts.flat().sort((a, b) => a.date < b.date ? -1 : 1);
  DATA = { generated_at: idx.generated_at, count: items.length, items };
  document.getElementById('stat').textContent = '資料整理時間：' + idx.generated_at + '｜未來 14 天共 ' + items.length + ' 筆公告｜輸入關鍵字開始查詢（地區文字為節錄，全文見台電官方頁）';
  if (qp) document.getElementById('go').click();
}).catch(() => { document.getElementById('stat').textContent = '資料載入失敗，請改至台電官方公告頁查詢。'; });
document.getElementById('go').addEventListener('click', () => {
  const res = document.getElementById('res');
  if (!DATA) { res.innerHTML = '<p>資料尚未載入完成，請稍候再試。</p>'; return; }
  const q = FW(document.getElementById('q').value.trim());
  const b = document.getElementById('b').value;
  let items = DATA.items.filter(it => (!b || it.branch === b) && (!q || FW(it.area).includes(q) || it.branch.includes(q)));
  if (!items.length) { res.innerHTML = '<p>查無符合的公告——代表目前公告期間內，你查詢的範圍沒有計畫性停電（突發停電請見下方說明）。</p>'; return; }
  const MAX = 50;
  res.innerHTML = '<p>共 ' + items.length + ' 筆' + (items.length > MAX ? '（只顯示前 ' + MAX + ' 筆，請縮小關鍵字）' : '') + '</p>' +
    items.slice(0, MAX).map(it =>
      '<div class="item"><b>' + it.date + '｜' + it.time + '</b>（' + it.branch + (it.reason ? '・' + it.reason : '') + '）<br>' + it.area + '</div>'
    ).join('');
});
</script>
"""
    body = body.replace("__LINKS__", links)
    w("daily/outage.html", head("停水停電查詢", "台電計畫性停電公告整理成可搜尋工具，輸入路名就知道近期會不會停電；停水查詢與停水前準備一次看懂。", 1, "daily") + body + foot(1))

def page_vegprice():
    body = """
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">民生查詢</a> ／ 菜價行情查詢</p>
<div class="hero"><h1>🥬 菜價行情查詢</h1>
<p>菜價每天都在變，但一般人只看得到市場零售價。其實農業部每天都公布各批發市場的「交易行情」——哪種菜今天量多價跌、哪種菜正在貴，看批發行情就知道。這一頁先教你看懂行情、去哪裡查，自動整理功能正在建置中。</p></div>

<h2 class="sec">批發價和你買的價錢，差在哪？</h2>
<div class="hero">
<ul style="margin:8px 0 8px 22px">
<li><b>批發行情</b>是清晨在批發市場（如果菜市場、台北一市、二市等）的成交價，單位是每公斤，是零售價的「上游指標」。</li>
<li>零售價還會加上運輸、攤商成本與損耗，所以會比批發價高一截，兩者不要直接相比，要看的是<b>趨勢</b>：批發價連跌，代表產量多、這幾天買這種菜相對划算。</li>
<li>颱風、大雨過後葉菜類批發價常先跳漲，一兩週後隨復耕回落——看行情就知道現在是「先買根莖類擋一下」還是「葉菜可以放心買」。</li>
</ul>
</div>

<h2 class="sec">去哪裡查官方行情</h2>
<div class="hero">
<p>資料來源是<b>農業部農糧署「農產品批發市場交易行情」</b>（政府資料開放平台有同一份開放資料），官方查詢管道：</p>
<ul style="margin:8px 0 8px 22px">
<li>農業部網站的「農產品交易行情」查詢系統：可依日期、市場、作物名稱查每日交易量與平均價，還能看走勢圖。</li>
<li>想訂閱特定作物的價格變化，官方系統有「快速訂閱」功能，價格異動會主動通知。</li>
</ul>
<p>好康生活正在把這份開放資料做成手機好讀的查詢工具（輸入菜名就看今天各市場行情），完成後會直接在這一頁上線，不用再自己翻官方系統。</p>
<p class="note">建置說明：官方資料端點（data.moa.gov.tw）於建置期間連線不穩定，我們改採「每日快照整理」方式開發，完成後本頁會標示資料日期與來源，不會用過期或來路不明的數字充數。</p>
</div>
"""
    w("daily/vegprice.html", head("菜價行情查詢", "農業部農產品批發市場交易行情怎麼看：批發價與零售價差別、去哪查官方行情、颱風後菜價怎麼判斷。", 1, "daily") + body + foot(1))

def page_garbage():
    body = """
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">民生查詢</a> ／ 垃圾車時間查詢</p>
<div class="hero"><h1>🚛 垃圾車時間查詢</h1>
<p>垃圾車沒有全國統一的查詢系統——每個縣市（甚至每個鄉鎮）都有自己的清運路線與時間，由各縣市環保局或公所管理。這一頁把主要縣市的官方查詢方式整理在一起，照你住的縣市對號入座。</p></div>

<h2 class="sec">主要縣市官方查詢方式</h2>
<div class="hero">
<table class="cmp"><tr><th>縣市</th><th>官方查詢方式</th><th>可以查到什麼</th></tr>
<tr><td>新北市</td><td>「新北樂圾車」官方網站</td><td>清運路線、垃圾車即時動態、定點收運地點與時間</td></tr>
<tr><td>台北市</td><td>台北市環保局網站清運資訊</td><td>各區收運時間與地點；另有 30 處限時定點收受點，錯過垃圾車可改去定點</td></tr>
<tr><td>基隆市</td><td>「基隆垃圾車來了」查詢系統</td><td>垃圾車即時位置與預估到點時間</td></tr>
<tr><td>桃園市</td><td>「桃園垃圾車」App／桃園市環境管理處公告</td><td>沿線收運時間；週三、週日為清潔隊例休（各區以公告為準）</td></tr>
<tr><td>台中市</td><td>台中市環保局「垃圾清運大車隊」即時查詢</td><td>清運路線即時位置與收運時間</td></tr>
<tr><td>其他縣市</td><td>各縣市環保局或鄉鎮市公所網站</td><td>多數公所會公布每週清運日程表（PDF 或公告頁），搜尋「你的鄉鎮＋垃圾車時間」通常第一筆就是官方頁</td></tr>
</table>
</div>

<h2 class="sec">連假與颱風天，清運最容易變動</h2>
<div class="hero">
<p>平常的收運時間相對固定，但遇到連續假期、颱風停班停課，清運安排幾乎每次都會調整：有的縣市停收、有的改成夜間收運、有的加班收運，各縣市都不同，而且常常當天才公告。出門倒垃圾前，記得先看一次縣市環保局的最新公告，不要用平常的時間表推測。</p>
<p class="note">舉例：2026 年 10 月 24 日颱風停班停課當天，台中市全日停收、台北市晚間恢復正常收運、新北市午後加班收運——同一天三個城市三種安排，這就是為什麼要以官方公告為準。（資料來源：各縣市環保局當日公告）</p>
</div>
"""
    w("daily/garbage.html", head("垃圾車時間查詢", "各縣市垃圾車清運時間與即時位置的官方查詢方式總整理：新北樂圾車、基隆垃圾車來了、台中清運大車隊等。", 1, "daily") + body + foot(1))

# ---------------- 主程式 ----------------
def main():
    with open(os.path.join(ROOT, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS.strip() + "\n")
    print("wrote style.css")
    page_index()
    page_search()
    page_home_channel()
    page_daily_channel()
    for slug, _i, _n, _d, live in CHANNELS:
        if not live:
            page_soon(slug)
    articles()
    page_outage()
    page_vegprice()
    page_garbage()
    urls = ["", "search.html", "home/", "daily/", "daily/outage.html", "daily/vegprice.html", "daily/garbage.html"] \
        + [f"home/{s}.html" for s, _t, _d in HOME_ARTICLES] \
        + [f"{s}/" for s, _i, _n, _d, live in CHANNELS if not live]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' \
        + "".join(f"<url><loc>{BASE}/{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sm)
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    print("wrote sitemap.xml / robots.txt, total urls:", len(urls))

if __name__ == "__main__":
    main()
