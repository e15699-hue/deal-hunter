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
    ("kids",   "👨‍👩‍👧", "親子學習", "兒童線上英文怎麼挑——師資、教材、價格、退費，先看懂各家規則再決定，不當冤大頭。", True),
    ("pets",   "🐾", "寵物照護", "狗狗拉肚子、貓咪不吃飯先怎麼判斷——只寫科普＋就醫提醒，不診斷、不取代獸醫。", True),
    ("senior", "👵", "銀髮 3C", "長輩手機教學、防詐騙——字大、步驟清楚，子女也能直接傳給爸媽看。", False),
    ("health", "🏥", "健康查詢", "假日夜間看診、藥局營業時間——急著找醫生時不用再一間一間打電話。", False),
    ("study",  "📚", "學習考照", "技術士考照刷題與考試資訊——公開題庫整理好，照著練就對了。", False),
    ("ai",     "🤖", "AI 工具", "免費 AI 工具實測——文書、圖片、簡報，哪些真的好用，我們試給你看。", False),
    ("car",    "🚗", "愛車生活", "驗車、稅金、保險到期提醒——車子的例行大事，不再靠記憶。", False),
]
CH = {c[0]: c for c in CHANNELS}

# ---------------- 圖片（2026-10-24 使用者標準：文章／商品盡量要有圖片） ----------------
# 文章圖一律用免費圖庫實圖（Wikimedia Commons，授權與作者記錄在 img/credits.json）；
# 商品圖日後一律用官方／賣場實圖，不用圖庫圖或生成圖充數。
# 圖片取材順序（2026-10-24 使用者補充，適用全部網站）：客群是台灣人，優先用台灣場景／台灣相關的真實圖片；
# 找不到台灣相關圖時最不得已才自己產出圖片，且自行產出的圖絕對不得假冒政府網站畫面。
# 風格標準（2026-10-24 使用者糾正）：台灣場景還要現代時尚、吸引人——明亮、新穎、乾淨，淘汰老舊感照片（眷舍老屋、老市場、老廟宇等）。
# 例外紀錄：cabinet（系統櫃）經多輪搜尋無合適台灣場景圖，現用白色櫥櫃特寫本身已是現代簡約風，暫留（不以餐廳廚房圖硬換）；
# contract（合約）台灣辦公室候選皆老舊昏暗，改回乾淨的合約文件特寫（無場景誤認）。
try:
    IMG_META = json.load(open(os.path.join(ROOT, "img", "credits.json"), encoding="utf-8"))
except FileNotFoundError:
    IMG_META = {}
IMG_ALT = {
    "hero_home": "明亮現代的套房室內",
    "quote": "新北市立美術館新建工程夜景",
    "designer": "台北 Apple A13 現代室內設計",
    "cabinet": "安裝完成的白色廚房櫃體",
    "process": "台北車站雙子星新建工程工地",
    "contract": "合約文件與簽名筆特寫",
    "outage": "台北夜景與 101 大樓燈光",
    "vegprice": "改建後的台北南門市場入口",
    "garbage": "台北夜間垃圾清運作業",
    "senior": "長輩用手機在台北街頭錄影",
    "health": "康是美現代藥妝店面",
    "study": "台灣國中電腦教室上課實景",
    "ai": "2024 台北國際電腦展現場",
    "car": "新竹科學園區特斯拉超級充電站",
    "kids": "小女孩戴著耳機用平板上課",
    "engguide": "孩子們在電腦教室裡學習",
    "engvs": "老師在家透過筆電進行遠距教學",
    "engprice": "存錢筒與硬幣",
    "engfaq": "兩個孩子一起看平板學習",
    "pets": "兩隻黃金獵犬躺在草地上",
    "petguide": "獸醫人員照護獲救的小貓",
    "petdiet": "狗狗正在吃飼料",
    "petvaccine": "獸醫為家貓施打狂犬病疫苗",
    "petfaq": "狗狗盯著球準備玩接球遊戲",
}
CHANNEL_IMG = {"home": "hero_home", "daily": "outage", "kids": "kids", "pets": "pets", "senior": "senior", "health": "health", "study": "study", "ai": "ai", "car": "car"}
PAGE_IMG = {"home/quote.html": "quote", "home/designer.html": "designer", "home/cabinet.html": "cabinet",
            "home/process.html": "process", "home/contract.html": "contract", "daily/outage.html": "outage",
            "daily/vegprice.html": "vegprice", "daily/garbage.html": "garbage",
            "kids/guide.html": "engguide", "kids/vs.html": "engvs", "kids/price.html": "engprice", "kids/faq.html": "engfaq",
            "pets/guide.html": "petguide", "pets/diet.html": "petdiet", "pets/vaccine.html": "petvaccine", "pets/faq.html": "petfaq"}
SLUG_IMG = {"quote": "quote", "designer": "designer", "cabinet": "cabinet", "process": "process", "contract": "contract"}
KIDS_SLUG_IMG = {"guide": "engguide", "vs": "engvs", "price": "engprice", "faq": "engfaq"}
PETS_SLUG_IMG = {"guide": "petguide", "diet": "petdiet", "vaccine": "petvaccine", "faq": "petfaq"}

def _credit(key):
    m = IMG_META.get(key, {})
    artist = m.get("artist") or "Wikimedia Commons 貢獻者"
    return f'照片：{artist}／{m.get("license", "")}，來源 <a href="{m.get("page", "")}" target="_blank" rel="noopener">Wikimedia Commons</a>'

def _src(key, prefix):
    """圖片來源：credits.json 有 remote 欄位時用遠端圖庫原圖網址（推送工具僅支援 UTF-8 文字檔，二進位圖檔無法進 repo，故新圖採 Wikimedia Commons 直連並標出處）；否則用本機 img/ 路徑。"""
    m = IMG_META.get(key, {})
    return m.get("remote") or f"{prefix}img/{key}.jpg"

def fig(key, prefix):
    """文章／頁面主圖（含出處標示）。"""
    if key not in IMG_META:
        return ""
    return f'<figure class="fig"><img src="{_src(key, prefix)}" alt="{IMG_ALT.get(key, "")}" loading="lazy"><figcaption>{_credit(key)}</figcaption></figure>'

def thumb(key, prefix, cls="fthumb"):
    if key not in IMG_META:
        return ""
    return f'<img class="{cls}" src="{_src(key, prefix)}" alt="{IMG_ALT.get(key, "")}" loading="lazy">'

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
.fig{margin:14px 0}
.fig img{width:100%;height:auto;max-height:420px;object-fit:cover;object-position:center;border-radius:12px;display:block}
.fig figcaption{font-size:12px;color:var(--sub);margin-top:6px}
.card img.thumb{width:100%;height:160px;object-fit:cover;border-radius:10px;margin-bottom:12px;display:block}
.feeditem{display:flex;gap:14px;align-items:center}
.feeditem .fthumb{width:120px;height:88px;object-fit:cover;border-radius:10px;flex:none}
.feeditem .ftxt{min-width:0}
@media(max-width:640px){.feeditem .fthumb{width:96px;height:74px}}
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
<nav class="main"><a href="{up}map.html">🗺️ 國家資訊地圖</a><a href="{up}search.html">🔍 搜尋</a>{nav}</nav>
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
    ("map.html", "民生查詢", "國家資訊地圖：步道開放、停電、停水一張圖查完", "國家資訊地圖 地圖 停電 停水 步道 開放 封鎖 山區 登山", "查詢工具"),
    ("daily/outage.html", "民生查詢", "停水停電查詢", "停電 停水 台電 台水 計畫性停電 1911 跳電", "查詢工具"),
    ("daily/vegprice.html", "民生查詢", "菜價行情查詢", "菜價 批發市場 行情 蔬菜 農業部 買菜", "查詢工具"),
    ("daily/garbage.html", "民生查詢", "垃圾車時間查詢", "垃圾車 清運時間 環保局 倒垃圾 樂圾車", "查詢工具"),
    ("kids/guide.html", "親子學習", "兒童線上英文怎麼挑？6 家平台對照表一次看懂", "兒童英文 線上英文 OiKID TutorABC 51Talk Native Camp Etalking WUWOW 比較 試聽 挑選", "約 6 分鐘"),
    ("kids/vs.html", "親子學習", "OiKID vs TutorABC Junior：兩家差在哪、適合誰", "OiKID TutorABC Junior tutorJr 比較 差別 師資 價格 退費", "約 5 分鐘"),
    ("kids/price.html", "親子學習", "兒童線上英文價格與退費規則整理", "價格 學費 退費 堂數 月費 點數 分期 兒童英文 簽約", "約 5 分鐘"),
    ("kids/faq.html", "親子學習", "兒童線上英文家長常見問題 FAQ", "FAQ 試聽 幾歲開始 固定老師 退費 設備 旁聽 兒童英文", "約 5 分鐘"),
    ("pets/guide.html", "寵物照護", "狗狗拉肚子、貓咪不吃飯：先判斷這 5 件事，再決定要不要馬上看獸醫", "狗狗拉肚子 貓咪不吃飯 嘔吐 血便 精神不好 獸醫 就醫 急診 毛孩", "約 6 分鐘"),
    ("pets/diet.html", "寵物照護", "狗狗貓咪飲食入門：飼料怎麼挑、哪些人類食物絕對不能給", "飼料 飲食 不能吃 巧克力 洋蔥 葡萄 木糖醇 換飼料 喝水 毛孩", "約 5 分鐘"),
    ("pets/vaccine.html", "寵物照護", "疫苗、結紮、驅蟲、寵物登記：毛孩新手的預防清單", "疫苗 狂犬病 結紮 驅蟲 晶片 寵物登記 健檢 獸醫 毛孩", "約 5 分鐘"),
    ("pets/faq.html", "寵物照護", "毛孩行為與日常照護 FAQ：亂叫、亂抓、亂尿先別急著罵", "亂叫 亂抓 亂尿 咬人 焦慮 換環境 洗澡 刷牙 毛孩 FAQ", "約 5 分鐘"),
]

def page_search():
    data = json.dumps([{"u": u, "c": c, "t": t, "k": k, "i": ((IMG_META.get(PAGE_IMG[u], {}).get("remote") or ("img/" + PAGE_IMG[u] + ".jpg")) if u in PAGE_IMG else "")} for u, c, t, k, _m in PAGES], ensure_ascii=False)
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
    ? hit.map(p => '<a class="feeditem" href="' + p.u + '">' + (p.i ? '<img class="fthumb" src="' + p.i + '" alt="">' : '') + '<div class="ftxt"><span class="tag">' + p.c + '</span><h3>' + p.t + '</h3></div></a>').join('')
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
        timg = thumb(CHANNEL_IMG.get(slug, ""), "", "thumb")
        if live:
            cards += f'<a class="card" href="{slug}/">{timg}<span class="badge">已上線</span><div class="ico">{ico}</div><h3>{name}</h3><p>{desc}</p></a>'
        else:
            cards += f'<div class="card">{timg}<span class="badge soon">籌備中</span><div class="ico">{ico}</div><h3>{name}</h3><p>{desc}</p></div>'
    feed = ""
    for u, c, t, _k, m in PAGES:
        feed += f'<a class="feeditem" href="{u}">{thumb(PAGE_IMG.get(u, ""), "")}<div class="ftxt"><span class="tag">{c}</span><h3>{t}</h3><p class="fmeta">閱讀時間 {m}</p></div></a>'
    body = f"""
<div class="hero">
<h1>新聞不報、但你天天要查的生活大小事</h1>
<p>停水停電、菜價、裝修報價、長輩手機問題……官方都有公布，卻散在十幾個網站、格式又難查。先搜尋看看，你要查的可能已經整理好了。</p>
<form class="searchbar" action="search.html" method="get"><input name="q" type="text" placeholder="想查什麼？例如：停電、菜價、報價單"><button type="submit">搜尋</button></form>
<div class="chips"><span>大家都在查：</span><a href="map.html">國家資訊地圖</a><a href="daily/outage.html">停電查詢</a><a href="daily/vegprice.html">今天菜價</a><a href="daily/garbage.html">垃圾車時間</a><a href="home/quote.html">裝修報價單</a><a href="home/cabinet.html">系統櫃價格</a><a href="kids/guide.html">兒童英文怎麼挑</a><a href="pets/guide.html">毛孩拉肚子怎麼辦</a></div>
{fig("hero_home", "")}
</div>
<div class="alertbar">🌧️ <b>天氣與連假提醒：</b>颱風、停班停課與連假期間，垃圾清運與停水停電安排幾乎每次都會變動，出門前先看 <a href="daily/garbage.html">垃圾車時間查詢</a> 與 <a href="daily/outage.html">停水停電查詢</a> 的官方公告整理。</div>
<h2 class="sec">🗺️ 國家資訊地圖</h2>
<div class="hero">
<p><b>步道開放／封鎖、停電、停水，一張地圖直接查結果</b>——政府公開資訊分門別類標在地圖上，圖層可勾選、可複選，點標記就看得到狀態與摘要，不用再轉到政府網站慢慢翻。手機打開就能用，之後 App 也會用同一張圖。</p>
<p style="margin-top:10px"><a href="map.html"><b>打開國家資訊地圖 →</b></a></p>
</div>
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
        items += f'<a class="feeditem" href="{slug}.html">{thumb(SLUG_IMG.get(slug, ""), "../")}<div class="ftxt"><h3>{t}</h3><p>{d}</p><p class="fmeta">閱讀時間 {meta.get(slug, "約 5 分鐘")}</p></div></a>'
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ 居家裝修</p>
<div class="hero"><h1>🏠 居家裝修</h1>
<p>裝修是大多數人一生花費前幾名的大事，偏偏資訊最不透明。我們只做一件事：把報價、流程、材料、合約這些「行內常識」寫成白話文，讓你做決定之前心裡有底。本站只提供知識整理，不評論、不推薦任何店家。</p>
{fig("hero_home", "../")}</div>
<h2 class="sec">裝修前必讀</h2>
<div class="feed">{items}</div>
<h2 class="sec">延伸：租屋看房</h2>
<div class="hero"><p>還沒買房、先租屋？看房時該檢查的壁癌、水壓、手機訊號、隔音與合約陷阱，我們整理在之後的「租屋看房防雷」專題中（籌備中）。</p></div>
"""
    w("home/index.html", head("居家裝修", "裝修報價單、設計師挑選、系統櫃計價、施工流程、合約注意事項——裝修前必讀的白話知識整理。", 1, "home") + body + foot(1))

def page_daily_channel():
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ 民生查詢</p>
<div class="hero"><h1>💧 民生查詢</h1>
<p>停水、停電、菜價、垃圾車——這些公告官方都有發布，卻分散在不同單位的網站裡，手機上尤其難查。這個頻道把官方公開資料整理成好查的工具頁，資料來源都標得清清楚楚，實際內容以官方公告為準。</p></div>
<h2 class="sec">查詢工具</h2>
<div class="grid">
<a class="card" href="../map.html"><div class="ico">🗺️</div><h3>國家資訊地圖</h3><p>步道開放／封鎖、停電、停水一張圖查完：圖層可勾選複選，點標記看狀態與摘要，結果直接顯示、不用轉到政府網站。</p></a>
<a class="card" href="outage.html">{thumb("outage", "../", "thumb")}<div class="ico">💡</div><h3>停水停電查詢</h3><p>台電計畫性停電公告即時查詢（官方開放資料）；停水公告整理自來水公司查詢入口與看懂公告的方法。</p></a>
<a class="card" href="vegprice.html">{thumb("vegprice", "../", "thumb")}<div class="ico">🥬</div><h3>菜價行情查詢</h3><p>農產品批發市場交易行情（農業部開放資料）：查今天各市場的蔬菜批發價，出門買菜前先看一眼。</p></a>
<a class="card" href="garbage.html">{thumb("garbage", "../", "thumb")}<div class="ico">🚛</div><h3>垃圾車時間查詢</h3><p>各縣市垃圾清運時間與即時位置的官方查詢入口總整理，照縣市找，不用再翻里辦公室公告。</p></a>
</div>
"""
    w("daily/index.html", head("民生查詢", "停水停電、菜價行情、垃圾車時間——官方公開資訊整理成好查的一頁。", 1, "daily") + body + foot(1))

def page_soon(slug):
    _s, ico, name, desc, _l = CH[slug]
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ {name}</p>
<div class="hero"><h1>{ico} {name}</h1>
<p>{desc}</p>
{fig(CHANNEL_IMG.get(slug, ""), "../")}
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
{fig(SLUG_IMG.get(slug, ""), "../")}
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


# ---------------- 親子學習頻道（點子 #35 兒童線上英文整理，2026-10-24 使用者拍板） ----------------
# 誠實紅線：本站尚未實際上過這些平台的課，內容一律為「公開資訊整理」並標查閱日期，
# 不寫假實測心得；「實測心得」欄位等日後真的試聽再補。文內平台連結先連官網（聯盟連結待帳號核准後替換）。
OFFICIAL_LINKS = {
    "OiKID": "https://www.oikid.com/",
    "TutorABC Junior": "https://www.tutorabc.com/",
    "Native Camp": "https://nativecamp.net/zh-tw",
    "51Talk": "https://tw.51talk.com/",
    "Etalking Kids": "https://www.etalking.com.tw/",
    "WUWOW Jr": "https://www.wuwow.tw/",
}

def off(name):
    return f'<a href="{OFFICIAL_LINKS[name]}" target="_blank" rel="noopener">{name} 官網</a>'

KIDS_ARTICLES = [
    ("guide", "兒童線上英文怎麼挑？6 家平台對照表一次看懂", "師資、教材、上課型態、收費方式——先看懂 4 個挑選維度，再用一張對照表把 6 家平台的公開資訊攤開比。"),
    ("vs", "OiKID vs TutorABC Junior：兩家差在哪、適合誰", "一家是台灣本土專做兒童，一家是大品牌兒少線。從師資、選老師、教材、價格公開度到退費，逐項對照，幫你判斷哪家適合你家孩子。"),
    ("price", "兒童線上英文價格與退費規則整理", "為什麼官網都查不到完整價目？三種收費方式怎麼比、各家有公開的價格資訊、退費規則，以及簽約前一定要問清楚的 6 件事。"),
    ("faq", "兒童線上英文家長常見問題 FAQ", "幾歲可以開始、菲師好不好、能不能固定老師、試聽要注意什麼、兄弟姊妹能不能共用——家長最常問的 10 個問題一次整理。"),
]

def page_kids_channel():
    items = ""
    meta = {u.split("/")[-1].replace(".html", ""): m for u, _c, _t, _k, m in PAGES}
    for slug, t, d in KIDS_ARTICLES:
        items += f'<a class="feeditem" href="{slug}.html">{thumb(KIDS_SLUG_IMG.get(slug, ""), "../")}<div class="ftxt"><h3>{t}</h3><p>{d}</p><p class="fmeta">閱讀時間 {meta.get(slug, "約 5 分鐘")}</p></div></a>'
    offcards = ""
    offdesc = {
        "OiKID": "台灣本土兒童專科，3–15 歲，一對一＋團體課。",
        "TutorABC Junior": "TutorABC 兒少品牌（tutorJr），4–18 歲，牛津／國家地理授權教材。",
        "Native Camp": "月費吃到飽、免預約立即上課，有兒童教材，全齡可用。",
        "51Talk": "菲律賓外師為主、一對一短時高頻，3–15 歲。",
        "Etalking Kids": "英美加澳外師、一對一進度班，4–12 歲，美國小學教材。",
        "WUWOW Jr": "一對一＋點數制，4–12 歲，有 7 天鑑賞期。",
    }
    for name, url in OFFICIAL_LINKS.items():
        offcards += f'<a class="card" href="{url}" target="_blank" rel="noopener"><h3>{name}</h3><p>{offdesc[name]}</p></a>'
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ 親子學習</p>
<div class="hero"><h1>👨‍👩‍👧 親子學習</h1>
<p>第一個主題是「兒童線上英文」。家長挑平台最頭痛的不是選擇太少，而是每家的師資講法、收費方式、退費規則都寫在不同地方，官網還常常不標價。這個頻道把各平台的公開資訊整理成對照表與白話說明，讓你先做完功課、再帶孩子去試聽。</p>
{fig("kids", "../")}
<p class="note" style="margin-top:10px">本站的做法：只整理公開資訊並標明查閱日期，不假裝上過課。日後實際試聽各平台後，會再補上標明日期的「實測心得」欄位。</p></div>
<h2 class="sec">先讀這 4 篇</h2>
<div class="feed">{items}</div>
<h2 class="sec">平台官網快速連結</h2>
<div class="grid">{offcards}</div>
"""
    w("kids/index.html", head("親子學習", "兒童線上英文怎麼挑：6 家平台師資、教材、價格、退費對照整理，OiKID、TutorABC Junior、Native Camp、51Talk、Etalking Kids、WUWOW Jr。", 1, "kids") + body + foot(1))

def kids_article(slug, title, desc, body_html):
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">親子學習</a> ／ {title}</p>
<article class="post">
<h1>{title}</h1>
<p class="meta">好康生活・親子學習頻道｜本篇為公開資訊整理（2026-10-24 查閱各平台官網與公開資料），不是實際上課心得；價格與規則以各平台官網與正式合約為準。</p>
{fig(KIDS_SLUG_IMG.get(slug, ""), "../")}
{body_html}
<div class="tip"><b>看完接著讀：</b> <a href="./">回親子學習頻道</a> 看其他篇：總對照表、OiKID vs TutorABC Junior、價格與退費、家長 FAQ，四篇一起看，挑平台的功課就做滿了。</div>
</article>
<h2 class="sec">熱門閱讀</h2>
<div class="hero"><ol class="ranklist">__HOT__</ol></div>
"""
    others = [(u.split("/")[-1], t) for u, c, t, _k, _m in PAGES if c == "親子學習" and not u.endswith(slug + ".html")]
    hot = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in others)
    body = body.replace("__HOT__", hot)
    w(f"kids/{slug}.html", head(title, desc, 1, "kids") + body + foot(1))

def kids_articles():
    kids_article("guide", "兒童線上英文怎麼挑？6 家平台對照表一次看懂",
    "OiKID、TutorABC Junior、Native Camp、51Talk、Etalking Kids、WUWOW Jr 六家兒童線上英文的師資、教材、上課型態、收費與試聽對照，先看懂 4 個挑選維度再對號入座。",
    """
<p>幫孩子挑線上英文，資訊多到眼花：每家都說自家師資好、教材棒，但收費方式和退費規則卻很少直接寫在官網上。與其一家一家慢慢翻，先用這篇把「挑選的維度」和「6 家平台的公開資訊」一次看懂，再帶孩子去試聽驗證。</p>
<h2>先搞懂 4 個挑選維度</h2>
<ol>
<li><b>師資型態</b>：母語外師（英美加澳）、雙語師（中英）、菲律賓外師是三種主流。沒有哪種絕對最好，差別在口音環境、互動方式與價格帶，先想清楚你最在意的是什麼。</li>
<li><b>教材系統</b>：有分級系統（如對應 CEFR、美國 CCSS、劍橋或台灣 108 課綱）的教材，學習路徑比較清楚；用國際出版社授權教材（牛津、國家地理等）的，內容來源明確。</li>
<li><b>上課型態</b>：一對一專注度高；小班有同儕互動；免預約制彈性最大但老師不固定。低年級孩子多半需要一對一的引導。</li>
<li><b>收費方式</b>：堂數套裝制、月費訂閱制、點數制三種，邏輯完全不同（細節見本頻道「價格與退費」專篇）。只比單堂價格，很容易比錯。</li>
</ol>
<h2>6 家平台對照表（公開資訊整理）</h2>
<table class="cmp"><tr><th>平台</th><th>師資</th><th>上課型態</th><th>適合年齡</th><th>收費方式</th><th>免費試聽</th></tr>
<tr><td><b>OiKID</b></td><td>母語外師＋雙語師，可自選老師</td><td>一對一 25 分鐘＋團體主題課</td><td>3–15 歲</td><td>堂數套裝（官網未公開定價）</td><td>有，1 堂一對一</td></tr>
<tr><td><b>TutorABC Junior</b></td><td>母語外師＋雙語師，系統媒合</td><td>一對一／1 對 4 小班，25 或 45 分鐘</td><td>4–18 歲</td><td>套裝制，兒少約 $300/堂起（官網）</td><td>有，免費體驗課</td></tr>
<tr><td><b>Native Camp</b></td><td>140 多國講師（含母語講師認定）</td><td>一對一，免預約立即上課，5–25 分鐘</td><td>全齡（有兒童教材）</td><td>月費吃到飽，年繳平均 $1,999/月（官網）</td><td>有，7 天免費體驗</td></tr>
<tr><td><b>51Talk</b></td><td>菲律賓外師為主＋歐美外師</td><td>一對一 25 分鐘，短時高頻</td><td>3–15 歲</td><td>堂數套裝（官網未公開定價）</td><td>有，1 堂一對一</td></tr>
<tr><td><b>Etalking Kids</b></td><td>英美加澳外師（證照認證）</td><td>一對一進度班 25 分鐘</td><td>4–12 歲</td><td>官網未公開，需洽詢</td><td>有，免費試讀＋分級測驗</td></tr>
<tr><td><b>WUWOW Jr</b></td><td>美、菲、南非外師，部分雙語</td><td>一對一 25 分鐘</td><td>4–12 歲</td><td>點數制（官網未公開完整價目）</td><td>有，體驗課＋程度分析</td></tr></table>
<p class="note">資料來源：各平台官網與公開資料，2026-10-24 查閱。標「官網未公開」者，代表官網沒有放完整價目，需預約試聽後由顧問報價——這是這個行業的常態，不是單一平台的問題。</p>
<h2>依你家的情況對號入座</h2>
<ul>
<li><b>想要母語外師＋有系統的教材路徑</b>：先看 TutorABC Junior（牛津、國家地理授權教材，4 歲一路到 18 歲）、OiKID（自編教材對應美國 CCSS 與台灣課綱，專做 3–15 歲）、Etalking Kids（美國小學課本＋CEFR 分級，進度班制）。</li>
<li><b>預算優先、想讓孩子高頻開口</b>：51Talk（菲師一對一、短時高頻）和 Native Camp（月費吃到飽、上越多越划算）是兩個不同方向的省錢解法。</li>
<li><b>不想綁長約、想隨時停</b>：Native Camp 是月費訂閱制，可隨時退會；WUWOW Jr 有 7 天鑑賞期全額退費（依公開資訊，簽約前以合約為準）。</li>
<li><b>家有兩個孩子</b>：OiKID 有雙寶共用方案（一個方案兩寶分配堂數）；Native Camp 一個帳號只能一人使用，家庭成員要另外辦家庭方案。</li>
<li><b>孩子坐不住、時間很難固定</b>：Native Camp 免預約、5 分鐘也能上；其他平台多為預約制，先確認取消與改期規則（TutorABC 官網載明開課前 4 小時可免費改期）。</li>
</ul>
<h2>最後一關：一定要試聽</h2>
<p>對照表只能幫你縮小範圍，適不適合，孩子坐上去上 25 分鐘就知道。建議至少試聽 2 家，觀察：孩子願不願意開口、老師會不會等孩子回答、教材畫面清不清楚。試聽前先看本頻道的「價格與退費」篇，把簽約前要問的問題列好；常見疑問則收在「家長 FAQ」篇。</p>
<div class="tip"><b>本站聲明：</b>本篇所有資訊皆為公開資料整理，我們還沒有實際上過這些平台的課，所以不寫「實測心得」。日後實際試聽後，會在各篇補上標明日期的實測欄位。平台連結：__OFFICIALS__。</div>
""".replace("__OFFICIALS__", "、".join(off(n) for n in OFFICIAL_LINKS)))

    kids_article("vs", "OiKID vs TutorABC Junior：兩家差在哪、適合誰",
    "OiKID 與 TutorABC Junior（tutorJr）逐項對照：品牌背景、師資與選老師方式、教材、上課型態、價格公開度、退費與試聽，幫你判斷哪家適合你家孩子。",
    """
<p>家長做功課時最常撞在一起比較的，就是這兩家：一家是台灣本土、專做兒童的 OiKID；一家是大型線上教育品牌 TutorABC 旗下的兒少線 TutorABC Junior（就是以前常聽到的 tutorJr）。兩家都主打母語外師與系統教材，但組織方式差很多。這篇不下「誰比較好」的結論，而是把差異攤開，讓你對照自家需求選。</p>
<h2>逐項對照</h2>
<table class="cmp"><tr><th>項目</th><th>OiKID</th><th>TutorABC Junior</th></tr>
<tr><td>品牌背景</td><td>2016 年創立於台北，專做兒童線上英文</td><td>TutorABC 旗下兒少品牌，成人與兒少課程都有</td></tr>
<tr><td>適合年齡</td><td>3–15 歲</td><td>4–18 歲（幼兒 Kids 線主打 4–6 歲）</td></tr>
<tr><td>師資</td><td>英美加澳等母語外師＋中英雙語師，具 TEFL／TESOL 認證</td><td>全球外師＋雙語師，官網載明師資錄取率約 3–5%、具教學證照</td></tr>
<tr><td>選老師方式</td><td>家長可自選老師、可固定（熱門老師要提早約）</td><td>系統依程度與需求媒合（DCGS），課後可以訂選喜歡的老師</td></tr>
<tr><td>教材</td><td>自編教材，對應美國 CCSS 課綱與台灣課綱，8 級分級</td><td>牛津、劍橋、國家地理等出版社授權教材，CEFR 分級</td></tr>
<tr><td>上課型態</td><td>一對一精品課 25 分鐘＋「摩天輪」團體主題課</td><td>一對一（25／45 分鐘）＋1 對 4 小班；24 小時可訂課</td></tr>
<tr><td>家長功能</td><td>課程錄影回放、親子陪讀</td><td>家長遠端旁聽、課後錄影回放、學習紀錄查詢</td></tr>
<tr><td>價格公開度</td><td>官網未公開定價，試聽後由顧問依方案報價</td><td>官網 FAQ 載明兒少約 $300/堂起，實際依專案報價</td></tr>
<tr><td>退費</td><td>官網未公開細則，簽約前需向顧問確認計算方式</td><td>官網載明：依合約啟用時間與已使用堂數計算退款</td></tr>
<tr><td>免費試聽</td><td>1 堂一對一體驗課</td><td>免費體驗課（先註冊做問卷與程度測驗，顧問再安排）</td></tr></table>
<p class="note">資料來源：兩平台官網與公開資料，2026-10-24 查閱；未公開的項目不猜測、不引用來路不明的數字。</p>
<h2>適合誰</h2>
<h3>比較適合 OiKID 的情況</h3>
<ul>
<li>孩子年齡在 3–15 歲，想要「專做兒童」的平台介面與教材節奏。</li>
<li>希望自己挑老師、固定老師，陪孩子慢慢建立熟悉感。</li>
<li>家有兩個孩子，想用雙寶共用方案分配堂數。</li>
<li>喜歡有團體主題課讓孩子換個上課氣氛。</li>
</ul>
<h3>比較適合 TutorABC Junior 的情況</h3>
<ul>
<li>希望教材是國際出版社授權（牛津、國家地理），並且一路從幼兒學到高中（4–18 歲）不用換平台。</li>
<li>作息不固定，需要 24 小時都能訂課。</li>
<li>想讓孩子偶爾上小班課跟同儕互動，或家長想用旁聽功能掌握上課狀況。</li>
<li>之後可能接檢定（全民英檢、多益等）或升學加強課程，同品牌內有對應課程線。</li>
</ul>
<h2>試聽時，觀察這 5 件事</h2>
<ol>
<li>孩子卡住時，老師是直接給答案，還是會等、會換個方式引導？</li>
<li>25 分鐘裡，孩子實際開口的次數多不多？</li>
<li>教材畫面與互動方式，孩子跟不跟得上、會不會分心？</li>
<li>下課後孩子願不願意「再上一次」？這是最誠實的指標。</li>
<li>顧問報價時，把總價、堂數、使用期限、退費算法一次問清楚（清單見「價格與退費」篇）。</li>
</ol>
<div class="tip"><b>本站聲明：</b>本篇為公開資訊整理，我們尚未實際上過這兩家的課，不寫假心得。日後實際試聽後，會補上標明日期的實測欄位。先去官網看看：__OFFICIALS__。</div>
""".replace("__OFFICIALS__", off("OiKID") + "、" + off("TutorABC Junior")))

    kids_article("price", "兒童線上英文價格與退費規則整理",
    "兒童線上英文三種收費方式（堂數套裝、月費訂閱、點數制）怎麼比、各平台有公開的價格資訊、退費規則整理，以及簽約前必問的 6 件事。",
    """
<p>兒童線上英文最讓家長困惑的就是價格：打開官網，多半只看到「預約免費試聽」，看不到完整價目。這不是單一平台的問題，而是這個行業普遍採「試聽後由顧問依方案報價」的模式。所以這篇做兩件事：把有公開的資訊整理出來；沒公開的，教你簽約前問到答案再簽。</p>
<h2>三種收費方式，先看懂再比價</h2>
<h3>1. 堂數套裝制（OiKID、TutorABC Junior、51Talk、Etalking Kids）</h3>
<p>一次買一個堂數包（如 100 堂），在期限內上完。比價重點不是總價，而是：期限多長（上不完會不會過期）、單堂換算時「贈送堂數」算不算進去、請假與停課規則。買越多單價越低，但前提是孩子真的會持續上。</p>
<h3>2. 月費訂閱制（Native Camp）</h3>
<p>每月固定費用、堂數吃到飽，不綁長約。比價重點是：你家一個月實際能上幾堂？上得少，單堂成本反而高；預約指定老師的金幣是另外付費的，要一起算。</p>
<h3>3. 點數制（WUWOW Jr）</h3>
<p>買點數、依課程類型扣點。比價重點是：想上的課型一堂扣幾點、點數有沒有期限、最低要買多少點。</p>
<h2>各平台價格公開資訊對照</h2>
<table class="cmp"><tr><th>平台</th><th>公開的價格資訊</th><th>備註</th></tr>
<tr><td>TutorABC Junior</td><td>官網 FAQ：兒少課程約 $300/堂起</td><td>實際費用依專案報價，簽約前請顧問出完整試算</td></tr>
<tr><td>Native Camp</td><td>官網：月費制吃到飽，年繳折扣平均每月 $1,999</td><td>月繳金額以官網公告為準；預約金幣另購</td></tr>
<tr><td>OiKID</td><td>官網未公開定價</td><td>家長公開彙整：套裝總價約 $62,400 起、精品課換算約 $380–450/堂（非官方數字，僅供抓預算，實際以顧問報價為準）</td></tr>
<tr><td>51Talk</td><td>官網未公開定價</td><td>家長公開彙整：套裝平均約 $250/堂，買越多越便宜（非官方數字，僅供參考）</td></tr>
<tr><td>Etalking Kids</td><td>官網未公開定價</td><td>需預約試讀後洽詢顧問</td></tr>
<tr><td>WUWOW Jr</td><td>官網未公開完整價目</td><td>家長公開彙整：單堂約 $300–650（非官方數字，僅供參考）</td></tr></table>
<h2>退費規則整理</h2>
<table class="cmp"><tr><th>平台</th><th>退費規則（公開資訊）</th></tr>
<tr><td>TutorABC Junior</td><td>官網載明：依合約啟用時間、已使用堂數計算退款</td></tr>
<tr><td>Native Camp</td><td>月費制，可隨時線上退會、不綁長約；注意退會即終止使用，且 7 天體驗期滿未取消會自動轉付費</td></tr>
<tr><td>WUWOW Jr</td><td>公開資訊：7 天鑑賞期內可全額退費；提供停課（最長半年）與課程轉讓，細節以合約為準</td></tr>
<tr><td>OiKID</td><td>官網未公開細則，簽約前務必向顧問索取退費計算方式並留存合約</td></tr>
<tr><td>51Talk</td><td>官網未公開細則，同上</td></tr>
<tr><td>Etalking Kids</td><td>官網 FAQ 未載明，同上</td></tr></table>
<p>提醒：線上課程的退費多半依合約約定與補習服務相關規定計算，「已上堂數」常以定價（而非折扣後單價）計算，這是簽約前最值得問清楚的一條。</p>
<h2>簽約前必問的 6 件事</h2>
<ol>
<li>總價多少？含幾堂？其中幾堂是贈送的？贈課在退費時怎麼算？</li>
<li>使用期限多長？到期沒上完怎麼辦？能不能申請展延或停課？</li>
<li>退費公式是什麼？請顧問直接試算一個例子（例如上 20 堂後退費能拿回多少）。</li>
<li>分期是跟平台分，還是向銀行／融資公司貸款？提前清償或退費時，分期怎麼處理？</li>
<li>請假、改期、取消的規則（最晚幾小時前、扣不扣堂數）？</li>
<li>合約能不能帶回家看完再簽？合理的業者不會要求當場簽約付款。</li>
</ol>
<div class="tip"><b>一句話總結：</b>不要用「最低單堂價」做決定。用「總價 ÷ 你家真的會上完的堂數」估成本，再把退費規則問到有數字，才是完整的比價。本站連結皆連向各平台官網，無合作關係揭露需求；日後若有合作連結，會在連結旁清楚標示。</div>
""")

    kids_article("faq", "兒童線上英文家長常見問題 FAQ",
    "兒童線上英文 FAQ：幾歲可以開始、母語外師與菲師怎麼選、能不能固定老師、試聽注意事項、設備需求、兄弟姊妹共用與退費，10 個家長最常問的問題。",
    """
<p>挑兒童線上英文時，家長問的問題其實高度重複。這篇把 10 個最常見的問題一次整理，答案都來自各平台的公開資訊；需要細節的，會指到本頻道的專篇。</p>
<h3>Q1：幾歲可以開始上線上英文？</h3>
<p>各平台的招生下限多在 3–4 歲（OiKID 3 歲、TutorABC Junior 與 Etalking Kids、WUWOW Jr 約 4 歲）。但能不能「坐得住 25 分鐘、願意跟螢幕裡的老師互動」比年齡更關鍵，建議先用免費試聽測試孩子的反應，再決定要不要開始。</p>
<h3>Q2：一定要選母語外師嗎？菲律賓老師好嗎？</h3>
<p>兩種都有人選，差別在學習目標與預算：母語外師的口音環境最接近英語母語國家；菲律賓外師的課程價格帶較低、一對一堂數可以排得更密，對「先敢開口、多練習」的目標很實用。與其糾結國籍，不如試聽時實際聽老師的發音與引導方式，並確認平台的師資認證（如 TESOL／TEFL）與篩選機制。</p>
<h3>Q3：可以固定同一位老師嗎？</h3>
<p>各家機制不同：OiKID 可自選老師、可固定（熱門老師要提早預約）；TutorABC Junior 以系統媒合為主、課後可訂選喜歡的老師；Etalking Kids 是進度班制，由平台依進度安排；Native Camp 是免預約制，老師不固定，想指定老師要用金幣預約。孩子比較慢熟的，優先考慮能固定老師的平台。</p>
<h3>Q4：試聽真的免費嗎？要注意什麼？</h3>
<p>本篇整理的 6 家都有免費試聽或試讀（多為 1 堂一對一；Native Camp 是 7 天體驗期）。兩個提醒：①Native Camp 的 7 天體驗需綁定付款方式做驗證，期滿前沒取消會自動轉付費，記得設提醒；②試聽後顧問來電說明方案是正常流程，不用有壓力，先把問題清單準備好再談價格。</p>
<h3>Q5：上課需要什麼設備？</h3>
<p>電腦或平板＋穩定網路＋耳機麥克風就能上。低年級孩子建議用螢幕較大的設備（筆電或平板），教材看得清楚、操作也簡單；Etalking 官網建議使用有線網路確保連線品質。上課前先做一次設備與環境測試，多數平台試聽前都會協助確認。</p>
<h3>Q6：一週上幾堂比較好？</h3>
<p>常見的安排是每週 2–3 堂、每次 25 分鐘的「短時高頻」，比一週一次長時間更容易維持語感與習慣。實際頻率還是要配合孩子的作息與其他才藝，先求穩定持續，再求堂數。</p>
<h3>Q7：家長可以旁聽或看上課回放嗎？</h3>
<p>多數平台提供課程錄影回放（OiKID、51Talk、Etalking Kids 都有）；TutorABC Junior 有家長遠端旁聽功能；WUWOW Jr 提供家長匿名旁觀。選平台時可以把「看不看得到上課狀況」列入比較，低年級尤其重要。</p>
<h3>Q8：兄弟姊妹可以共用一個帳號或方案嗎？</h3>
<p>OiKID 有雙寶共用方案，一個方案的堂數可由兩個孩子分配使用；Native Camp 明確規定一個帳號只能一人使用，家人要用需另辦家庭方案；其他平台多為一人一帳號，購買前先向顧問確認。</p>
<h3>Q9：買了之後不適合，退費怎麼算？</h3>
<p>各家規則差異大：TutorABC 官網載明依合約啟用時間與已使用堂數計算；WUWOW Jr 有 7 天鑑賞期；Native Camp 月費制可隨時退會。其他平台官網未公開細則，簽約前務必問清楚（完整整理與必問清單見「價格與退費」篇）。</p>
<h3>Q10：線上英文跟實體補習班怎麼選？</h3>
<p>沒有標準答案，看家庭條件：線上省下接送時間、排課彈性大、一對一開口機會多；實體有同儕氛圍與老師現場管理。也有家庭採混合制（平日線上維持頻率、假日實體或活動課）。先想清楚你家最缺的是「時間彈性」還是「同儕環境」，再對照本頻道的總對照表挑平台。</p>
<div class="tip"><b>還沒決定？</b>先看 <a href="guide.html">總對照表</a> 縮小到 2 家，各帶孩子試聽一次——孩子的反應會幫你做最後的決定。本站各篇皆為公開資訊整理，實際試聽心得日後補上。</div>
""")

# ---------------- 寵物照護頻道（點子 #39，2026-10-24 使用者拍板） ----------------
# 誠實紅線：本站不是獸醫院，本頻道只寫一般科普與「何時該就醫」的判斷方向，
# 不做個別診斷、不開藥、不給劑量、不取代獸醫師面診；出現紅旗症狀一律寫「儘速就醫」。
# 圖片例外紀錄：本輪在 Wikimedia Commons 未找到合適的台灣場景寵物實圖，
# 暫用中性寵物實圖並標作者／授權／來源，日後找到台灣場景圖再換（比照系統櫃例外作法）。
PETS_ARTICLES = [
    ("guide", "狗狗拉肚子、貓咪不吃飯：先判斷這 5 件事，再決定要不要馬上看獸醫", "半夜毛孩拉肚子或不吃飯，飼主最慌。先看精神、食慾、排泄、嘔吐與年齡／病史這 5 件事，對照紅旗清單，決定是先觀察還是馬上就醫。"),
    ("diet", "狗狗貓咪飲食入門：飼料怎麼挑、哪些人類食物絕對不能給", "飼料標示怎麼看、換飼料為什麼要漸進、哪些人類食物對犬貓有毒、喝水與體重怎麼觀察——飲食篇只講原則，不推特定品牌。"),
    ("vaccine", "疫苗、結紮、驅蟲、寵物登記：毛孩新手的預防清單", "第一次養毛孩最容易漏掉的 4 件事：疫苗、結紮、驅蟲與寵物登記。時程與項目由獸醫師依年齡與生活環境評估，本文只給清單與提問方向。"),
    ("faq", "毛孩行為與日常照護 FAQ：亂叫、亂抓、亂尿先別急著罵", "亂叫、亂抓家具、亂尿、咬手、怕打雷——先排除身體不舒服，再看環境與習慣。突然改變的行為，先看獸醫再談訓練。"),
]

def page_pets_channel():
    items = ""
    meta = {u.split("/")[-1].replace(".html", ""): m for u, _c, _t, _k, m in PAGES}
    for slug, t, d in PETS_ARTICLES:
        items += f'<a class="feeditem" href="{slug}.html">{thumb(PETS_SLUG_IMG.get(slug, ""), "../")}<div class="ftxt"><h3>{t}</h3><p>{d}</p><p class="fmeta">閱讀時間 {meta.get(slug, "約 5 分鐘")}</p></div></a>'
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ 寵物照護</p>
<div class="hero"><h1>🐾 寵物照護</h1>
<p>台灣養貓養狗的人越來越多，半夜狗狗拉肚子、貓咪不吃飯，飼主第一反應就是 Google。這個頻道把毛孩爸媽天天問的問題寫成白話科普：症狀先怎麼判斷、飲食要注意什麼、疫苗與登記有哪些、行為問題先別急著罵。</p>
{fig("pets", "../")}
<div class="tip"><b>重要提醒：</b>本站不是獸醫院。本頻道內容只提供一般知識整理，<b>不做個別診斷、不取代獸醫師面診</b>。毛孩出現本頻道列出的紅旗症狀，或狀況持續惡化，請儘速帶去獸醫院，不要只看文章等它自己好。</div></div>
<h2 class="sec">先讀這 4 篇</h2>
<div class="feed">{items}</div>
<h2 class="sec">台灣官方資源怎麼找</h2>
<div class="hero"><p>狂犬病疫苗、寵物登記、動物收容與認養等規定與服務，各縣市由動物保護處（或防疫所）公告與辦理；有疑問時，直接洽詢所在地動保處或你的獸醫師，比看網路傳言可靠。疫苗與登記的實際時程、費用與補助，以官方公告為準。</p></div>
"""
    w("pets/index.html", head("寵物照護", "狗狗拉肚子、貓咪不吃飯先怎麼判斷，飼料怎麼挑，疫苗、結紮、驅蟲與寵物登記清單，毛孩行為 FAQ——只寫科普＋就醫提醒，不診斷。", 1, "pets") + body + foot(1))

def pets_article(slug, title, desc, body_html):
    body = f"""
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">寵物照護</a> ／ {title}</p>
<article class="post">
<h1>{title}</h1>
<p class="meta">好康生活・寵物照護頻道｜本篇為一般知識整理（2026-10-24 整理），不是醫療建議、不做個別診斷；毛孩個別狀況請洽獸醫師，嚴重症狀請儘速就醫。</p>
{fig(PETS_SLUG_IMG.get(slug, ""), "../")}
{body_html}
<div class="tip"><b>看完接著讀：</b> <a href="./">回寵物照護頻道</a> 看其他篇：症狀判斷、飲食入門、預防清單、行為 FAQ，四篇一起看，新手功課就做滿了。</div>
</article>
<h2 class="sec">熱門閱讀</h2>
<div class="hero"><ol class="ranklist">__HOT__</ol></div>
"""
    others = [(u.split("/")[-1], t) for u, c, t, _k, _m in PAGES if c == "寵物照護" and not u.endswith(slug + ".html")]
    hot = "".join(f'<li><a href="{u}">{t}</a></li>' for u, t in others)
    body = body.replace("__HOT__", hot)
    w(f"pets/{slug}.html", head(title, desc, 1, "pets") + body + foot(1))

def pets_articles():
    pets_article("guide", "狗狗拉肚子、貓咪不吃飯：先判斷這 5 件事，再決定要不要馬上看獸醫",
    "狗狗拉肚子、貓咪不吃飯時，先看精神、食慾、排泄、嘔吐與年齡／病史，對照紅旗清單決定觀察還是馬上就醫。本篇不診斷，只給判斷方向。",
    """
<p>半夜毛孩突然拉肚子、吐了，或平常愛吃的貓突然不吃飯，飼主第一反應通常是慌。先深呼吸，用下面 5 件事快速盤點，再決定是先觀察、還是馬上出門看獸醫。這篇不幫你的毛孩診斷，只教你「什麼情況不能等」。</p>
<h2>先看這 5 件事</h2>
<ol>
<li><b>精神狀態</b>：還願意走動、回應你、搖尾巴或呼嚕嗎？還是整隻癱著、叫不動、躲起來不出來？精神明顯變差，比單一次拉肚子更值得警覺。</li>
<li><b>食慾與喝水</b>：完全不吃不喝，還是挑食但還願意吃一點？水喝得比平常多很多或幾乎不喝，都要記下來告訴獸醫。</li>
<li><b>排泄狀況</b>：拉肚子是水狀還是成形？有沒有血、黏液、異味特別重？尿量有沒有突然變少、排尿會不會痛、一直蹲卻尿不出來？</li>
<li><b>嘔吐頻率</b>：吐一次後就恢復，還是短時間內反覆吐、吐出膽汁或異物？反覆嘔吐加上不吃不喝，就不要再等。</li>
<li><b>年齡與病史</b>：幼犬貓、老犬貓、有慢性病、正在吃藥、剛換環境或剛換飼料的毛孩，耐受力比較低，同樣症狀要更早看醫生。</li>
</ol>
<h2>出現這些紅旗，不要等，儘速就醫</h2>
<ul>
<li>便便或嘔吐物帶血、呈現黑色柏油狀</li>
<li>反覆嘔吐或腹瀉，合併精神萎靡、完全不吃不喝</li>
<li>呼吸困難、牙齦發白或發紫、抽搐、倒地不起</li>
<li>誤食異物、藥物、巧克力、洋蔥、葡萄、木糖醇等已知有毒物品</li>
<li>排尿困難、一直蹲廁所卻尿不出來（尤其公貓要特別注意）</li>
<li>肚子明顯脹大疼痛、觸摸會哀叫或抗拒</li>
</ul>
<p>去看醫生前，先做 3 件有幫助的事：①用手機拍下便便／嘔吐物的樣子（獸醫判斷很有用）②記下症狀開始時間、吃了什麼、有沒有接觸新東西 ③把正在吃的藥、飼料品牌帶著或拍照。不要自行給毛孩吃人類的止瀉藥、止痛藥或催吐——有些人類藥物對犬貓有毒，催吐也可能讓狀況更糟。</p>
<h2>如果沒有紅旗，可以先這樣觀察</h2>
<p>精神還不錯、只拉一次或吐一次、之後願意喝水休息，獸醫常會建議先觀察並注意飲食：先給少量、好消化的食物（依獸醫平常的建議），不要一次餵太多，也不要馬上換新飼料刺激腸胃。觀察期間如果症狀超過一天沒有改善、反覆出現，或出現上面任何一項紅旗，就不要再拖，直接就醫。幼犬貓脫水速度快，觀察時間要比成犬貓更短。</p>
<div class="tip"><b>一句話總結：</b>判斷的重點不是「拉幾次」，而是「精神＋食慾＋有沒有紅旗」。有紅旗就馬上看獸醫，沒紅旗也不要觀察超過一天還不改善。</div>
""")

    pets_article("diet", "狗狗貓咪飲食入門：飼料怎麼挑、哪些人類食物絕對不能給",
    "狗狗貓咪飼料標示怎麼看、換飼料為什麼要漸進、哪些人類食物對犬貓有毒、喝水與體重怎麼觀察。只講原則，不推特定品牌。",
    """
<p>毛孩飲食最常見的兩個誤區：一是覺得「人吃的、毛孩也能吃一點沒關係」，二是換飼料一次換到底，結果腸胃抗議。飲食篇不推特定品牌，只講挑選與餵食的原則，實際熱量與營養需求，還是要請獸醫師依體重、年齡與健康狀況評估。</p>
<h2>飼料標示先看這 4 項</h2>
<ul>
<li><b>適用年齡與體型</b>：幼犬貓、成犬貓、老犬貓與小型／大型犬的營養需求不同，先對號入座，不要拿成犬飼料長期餵幼犬貓。</li>
<li><b>主要成分順序</b>：成分表依含量由多到少排列，第一項通常是主要蛋白質來源；不要只看包裝正面的行銷字，翻到背面看成分表。</li>
<li><b>營養完整性標示</b>：是否標示符合完整均衡營養標準（例如 AAFCO 等標示），以及適用生命階段。</li>
<li><b>每日建議餵食量只是起點</b>：包裝上的建議量是參考值，實際要依體重變化、活動量與獸醫建議微調，定期量體重比憑感覺餵更可靠。</li>
</ul>
<h2>換飼料要漸進，不要一次換到底</h2>
<p>換新飼料時，用一週左右慢慢混著換：先新舊混餵、再逐步提高新飼料比例，同時觀察便便成形度與食慾。一次換到底、或短時間內頻繁換品牌，都容易拉肚子。如果換飼料後持續拉肚子、嘔吐或精神變差，先停下來並諮詢獸醫，不要硬換下去。</p>
<h2>這些人類食物，犬貓絕對不能吃</h2>
<table class="cmp"><tr><th>食物</th><th>為什麼危險（一般常識整理）</th></tr>
<tr><td>巧克力、咖啡因飲品</td><td>含可可鹼等成分，犬貓代謝慢，少量也可能中毒</td></tr>
<tr><td>洋蔥、大蒜、蔥、韭菜</td><td>可能破壞紅血球，煮熟或粉末狀同樣有風險</td></tr>
<tr><td>葡萄、葡萄乾</td><td>可能造成急性腎損傷，連少量都要警覺</td></tr>
<tr><td>木糖醇（無糖口香糖、部分無糖食品）</td><td>對狗特別危險，可能造成低血糖與肝損傷</td></tr>
<tr><td>酒精、發酵麵糰</td><td>酒精與發酵產生的氣體都可能造成中毒或脹氣</td></tr>
<tr><td>骨頭（尤其煮熟的禽骨）</td><td>容易碎裂，可能刺傷口腔、食道或腸胃</td></tr></table>
<p>誤食上面任何一項，不要自行催吐或餵牛奶「解毒」，先記下吃了什麼、大約多少、什麼時候吃的，馬上聯絡獸醫或動物醫院，依指示處理。貓狗的耐受性不同：貓對某些藥物與食物更敏感，不要把狗的經驗直接套用在貓身上。</p>
<h2>喝水與體重，兩個最容易忽略的指標</h2>
<ul>
<li><b>喝水</b>：每天保持乾淨飲水隨時可喝；貓咪普遍喝水量偏少，可以多放幾個水碗、或依獸醫建議搭配濕食，但不要強迫灌水。</li>
<li><b>體重</b>：每月量一次體重並記錄，突然變瘦或變胖都值得注意；摸得到肋骨但看不到明顯骨頭輪廓，通常是比較健康的體態參考，實際以獸醫評估為準。</li>
<li><b>零食比例</b>：零食與人類食物加起來不要佔每日熱量太高，否則正餐吃不下、營養反而失衡。</li>
</ul>
<div class="tip"><b>一句話總結：</b>飲食的原則很簡單——吃適合年齡的完整飼料、換食漸進、危險食物一口都不要給、體重與喝水定期觀察，有疑問問獸醫，不要問網友偏方。</div>
""")

    pets_article("vaccine", "疫苗、結紮、驅蟲、寵物登記：毛孩新手的預防清單",
    "第一次養毛孩最容易漏掉的 4 件事：疫苗、結紮、驅蟲與寵物登記。時程與項目由獸醫師依年齡與生活環境評估，本文只給清單與提問方向。",
    """
<p>第一次養毛孩，很多人以為「先養著、有問題再看醫生」就好。其實有 4 件預防的事，越早排進去越省事：疫苗、結紮、驅蟲與寵物登記。這篇不給你一張「幾週打哪一針」的固定時間表——因為實際項目與間隔，要由獸醫師看年齡、健康狀況與生活環境決定——而是給你一張到獸醫院時可以直接對照的清單。</p>
<h2>1. 疫苗：先問獸醫這 3 件事</h2>
<ul>
<li><b>核心疫苗有哪些？</b>犬貓各有常見的核心疫苗項目（例如犬的犬瘟熱、犬小病毒等，貓的貓瘟等），以及依生活環境才需要的非核心項目，請獸醫依毛孩狀況說明。</li>
<li><b>基礎免疫要幾劑、間隔多久？</b>幼犬貓通常需要多劑基礎免疫，成犬貓則定期補強，實際劑次與間隔以獸醫師安排為準，不要自行延後或跳過。</li>
<li><b>狂犬病疫苗與登記</b>：台灣規定犬貓應施打狂犬病疫苗並辦理寵物登記，實際規定、時程與費用以所在地動物保護處（防疫所）公告為準；打完疫苗記得留存疫苗證明與手冊。</li>
</ul>
<h2>2. 結紮：不是只有「不要生」的好處</h2>
<p>結紮除了避免意外繁殖，一般也與減少某些生殖系統疾病風險、降低發情期行為困擾有關，但手術時機與風險要個別評估：幼齡、成齡、有慢性病的毛孩適合的時間點不同，術前檢查與術後照護（傷口、活動限制、飲食）都要先問清楚。不要因為「怕毛孩痛」就無限期拖延，也不要在不了解風險的情況下急著決定——把問題列好，一次問獸醫。</p>
<h2>3. 驅蟲：體內、體外都要顧</h2>
<ul>
<li><b>體內驅蟲</b>：腸道寄生蟲不一定有明顯症狀，幼犬貓與剛領養的毛孩尤其要先檢查，驅蟲藥種類與頻率由獸醫師決定。</li>
<li><b>體外驅蟲</b>：跳蚤、壁蝨在台灣一年四季都可能出現，常外出的毛孩更要留意；驅蟲產品有滴劑、口服等多種形式，不要拿狗用的產品直接給貓用（有些成分對貓有毒）。</li>
<li><b>環境也要一起清</b>：毛孩的床墊、毯子、地毯定期清洗，家裡有跳蚤時，只處理毛孩、不處理環境很容易復發。</li>
</ul>
<h2>4. 寵物登記：晶片＋登記，缺一不可</h2>
<p>寵物登記通常是在獸醫院植入晶片並完成登記，之後搬家、換電話、換飼主都要記得更新資料。晶片不是 GPS，不能即時定位，但毛孩走失被拾獲送到收容所或獸醫院時，掃到晶片就能聯絡到飼主。領養或購買毛孩時，先確認晶片與登記是否已完成、資料是否正確。</p>
<h2>到獸醫院的提問清單（直接照著問）</h2>
<ol>
<li>我家毛孩這個年齡，現在該做哪些疫苗與檢查？</li>
<li>結紮建議什麼時候做？術前要檢查什麼、術後要注意什麼？</li>
<li>體內外驅蟲用哪種產品、多久一次？貓狗產品可以共用嗎？</li>
<li>狂犬病疫苗與寵物登記辦好了嗎？手冊與證明要怎麼保存？</li>
<li>下一次回診或補強是什麼時候？可以幫我寫在手冊上嗎？</li>
</ol>
<div class="tip"><b>一句話總結：</b>預防清單的重點不是背時間表，而是「第一次看診就把 4 件事一次問完、寫進手冊」，之後照著手冊回診，就不會漏。</div>
""")

    pets_article("faq", "毛孩行為與日常照護 FAQ：亂叫、亂抓、亂尿先別急著罵",
    "毛孩亂叫、亂抓家具、亂尿、咬手、怕打雷——先排除身體不舒服，再看環境與習慣。突然改變的行為，先看獸醫再談訓練。",
    """
<p>毛孩的「壞習慣」，很多時候是牠在表達需求或不舒服。罵、打、關起來通常只會讓問題更糟。先用這篇的順序檢查：身體 → 環境 → 習慣，突然改變的行為，先看獸醫再談訓練。</p>
<h3>Q1：狗狗一直亂叫，怎麼辦？</h3>
<p>先分辨叫的原因：門外有人經過、無聊想玩、焦慮、分離焦慮，處理方式完全不同。短時間、特定刺激才叫，和整天不停叫，是不同等級的問題。先增加散步與玩耍時間、給予嗅聞與益智玩具消耗精力；如果叫聲突然變多、合併食慾或精神改變，先排除疼痛或生病，再談行為訓練。不要用打罵或戴止吠器硬壓，焦慮型的亂叫壓下去，焦慮本身還在。</p>
<h3>Q2：貓咪亂抓家具、抓沙發怎麼辦？</h3>
<p>抓東西是貓的天性：磨爪、伸展、標記氣味，不是故意搗蛋。解法不是禁止抓，而是「給對的東西抓」：在貓常抓的位置旁邊放穩固的抓板或貓抓柱，材質（麻繩、紙板、地毯）多試幾種；家具暫時用布蓋住或貼防抓貼，貓轉移到抓板上就獎勵。指甲定期修剪（或請獸醫、美容師協助），不要自行去爪——去爪手術在台灣與多國都有爭議，絕對不要當成第一選擇。</p>
<h3>Q3：明明會上廁所，突然亂尿怎麼辦？</h3>
<p>突然亂尿的第一步是看獸醫，不是先罵。泌尿道感染、結石、腎臟問題、疼痛都可能讓毛孩改變如廁習慣；公貓排尿困難更是急症（見症狀判斷篇的紅旗）。排除健康問題後，再檢查：貓砂盆夠不夠乾淨、數量夠不夠（一般建議貓砂盆數＝貓數＋1）、位置是不是太吵或太遠、最近有沒有換貓砂、搬家或新成員加入。</p>
<h3>Q4：幼犬幼貓愛咬手、咬東西，怎麼教？</h3>
<p>幼犬貓用嘴探索世界是正常的，重點是教牠「咬玩具可以、咬手不可以」：玩的時候被咬到就立刻停下來、把手收回、給玩具替代，咬玩具就稱讚；不要用手跟牠玩打架遊戲，那等於在教牠手就是玩具。家裡的電線、藥物、小物件收好，幼犬貓啃咬時誤食異物是很常見的急診原因。</p>
<h3>Q5：毛孩怕打雷、怕鞭炮，怎麼辦？</h3>
<p>打雷、鞭炮、施工噪音期間，先給毛孩一個可以躲的安全角落（籠子開著門、蓋布的窩），不要硬把牠拖出來「習慣噪音」。平常可以播放低音量雷聲錄音、搭配零食做漸進減敏，但嚴重焦慮（發抖、喘、流口水、想逃跑撞門）要請獸醫評估，不要自行給鎮靜藥物。連假與節慶前，先確認毛孩的晶片登記資料正確，萬一受驚走失才找得回來。</p>
<h3>Q6：日常照護有哪些基本功？</h3>
<ul>
<li><b>刷牙</b>：牙齒保健常被忽略，獸醫多建議從小習慣刷牙或使用潔牙產品，牙結石嚴重時需要獸醫處理，不要自行刮牙結石。</li>
<li><b>洗澡與梳毛</b>：頻率依毛種與生活環境而定，洗太頻繁反而傷皮膚；長毛貓狗每天梳毛可以減少毛球與打結。</li>
<li><b>耳朵與指甲</b>：定期檢查耳朵有沒有異味或分泌物、指甲有沒有過長；不確定怎麼清、怎麼剪，先請獸醫或美容師示範一次。</li>
<li><b>體重與活動</b>：每月量體重、每天有固定散步與遊戲時間，體重突然變化先看獸醫，不要自己節食。</li>
</ul>
<div class="tip"><b>還沒決定？</b>先看 <a href="guide.html">症狀判斷篇</a> 學會分辨紅旗，再看 <a href="diet.html">飲食篇</a> 與 <a href="vaccine.html">預防清單篇</a>，新手功課就完整了。本頻道內容皆為一般知識整理，個別狀況請洽獸醫師。</div>
""")

# ---------------- 民生查詢工具頁 ----------------
TAIPOWER_LINKS = [
    ("基隆區營業處", "https://service.taipower.com.tw/branch/d101/xcnotice?xsmsid=0M242581316312033070"),
    ("北市區營業處", "https://service.taipower.com.tw/branch/d102/xcnotice?xsmsid=0M242581312773778160"),
    ("桃園區營業處", "https://service.taipower.com.tw/branch/d103/xcnotice?xsmsid=0M242581312675626779"),
    ("新竹區營業處", "https://service.taipower.com.tw/branch/d104/xcnotice?xsmsid=0M242581313964252236"),
    ("台中區營業處", "https://service.taipower.com.tw/branch/d105/xcnotice?xsmsid=0M242581317628413301"),
    ("彰化區營業處", "https://service.taipower.com.tw/branch/d106/xcnotice?xsmsid=0M242581314418510444"),
    ("嘉義區營業處", "https://service.taipower.com.tw/branch/d107/xcnotice?xsmsid=0M242581317006659586"),
    ("台南區營業處", "https://service.taipower.com.tw/branch/d108/xcnotice?xsmsid=0M242581311248677644"),
    ("高雄區營業處", "https://service.taipower.com.tw/branch/d109/xcnotice?xsmsid=0M242581310382588530"),
    ("屏東區營業處", "https://service.taipower.com.tw/branch/d110/xcnotice?xsmsid=0M242581319136855888"),
    ("台東區營業處", "https://service.taipower.com.tw/branch/d111/xcnotice?xsmsid=0M242581313752905496"),
    ("花蓮區營業處", "https://service.taipower.com.tw/branch/d112/xcnotice?xsmsid=0M242581312305799678"),
    ("宜蘭區營業處", "https://service.taipower.com.tw/branch/d113/xcnotice?xsmsid=0M242581316816175510"),
    ("澎湖區營業處", "https://service.taipower.com.tw/branch/d114/xcnotice?xsmsid=0M242581315569736204"),
    ("北南區營業處", "https://service.taipower.com.tw/branch/d115/xcnotice?xsmsid=0M242581317718023029"),
    ("北北區營業處", "https://service.taipower.com.tw/branch/d116/xcnotice?xsmsid=0M242581312941137933"),
    ("北西區營業處", "https://service.taipower.com.tw/branch/d117/xcnotice?xsmsid=0M242581310300276906"),
    ("南投區營業處", "https://service.taipower.com.tw/branch/d118/xcnotice?xsmsid=0M242581317452513865"),
    ("鳳山區營業處", "https://service.taipower.com.tw/branch/d119/xcnotice?xsmsid=0M242581312415567180"),
    ("雲林區營業處", "https://service.taipower.com.tw/branch/d120/xcnotice?xsmsid=0M242581310910082112"),
]

def page_outage():
    links = "、".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in TAIPOWER_LINKS)
    body = """
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">民生查詢</a> ／ 停水停電查詢</p>
<div class="hero"><h1>💡 停水停電查詢</h1>
<p>「計畫性停電」是台電為了施工、換變壓器、遷移線路排定的停電（不是缺電限電），公告其實都有，只是藏在各區營業處的網頁裡很難查。下面這個工具把台電官方公告整理成可以打字搜尋的列表：輸入你家附近的路名或區名，就能看近期會不會停電。</p>__FIG_OUTAGE__</div>

<h2 class="sec">計畫性停電查詢（台電官方公告整理）</h2>
<div class="toolbox">
<label for="q">輸入路名、區名或鄉鎮（例如：西屯、工業區一路、左營）</label>
<input id="q" type="text" placeholder="輸入關鍵字後按查詢">
<label for="b">區營業處</label>
<select id="b"><option value="">全部區處</option></select>
<button class="btn" id="go">查詢</button>
<p class="note" id="stat">資料載入中…</p>
<div class="result" id="res"></div>
<p class="note">資料來源：台灣電力公司各區營業處「計畫性工作停電公告」。本頁為定期整理的快照（整理時間見上方），最新與完整資訊請以台電官方公告為準；目前涵蓋全台 20 個區營業處。官方原頁：__LINKS__</p>
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
<p>停水公告由台灣自來水公司發布在「停水公告查詢系統」（web.water.gov.tw/wateroff），可以依地址查詢自家是否在停水範圍；進行中的停水公告，本站已直接整理在 <a href="../map.html?layers=water">國家資訊地圖・停水圖層</a>，不用再自己翻官方系統。台水也有官方 LINE「停水公告查詢系統」，訂閱並輸入住址後，有停水會提前推播通知——這是目前最不會漏掉停水消息的方法，建議長輩也一起訂閱。</p>
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
    body = body.replace("__LINKS__", links).replace("__FIG_OUTAGE__", fig("outage", "../"))
    w("daily/outage.html", head("停水停電查詢", "台電計畫性停電公告整理成可搜尋工具，輸入路名就知道近期會不會停電；停水查詢與停水前準備一次看懂。", 1, "daily") + body + foot(1))

def page_vegprice():
    body = """
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">民生查詢</a> ／ 菜價行情查詢</p>
<div class="hero"><h1>🥬 菜價行情查詢</h1>
<p>菜價每天都在變，但一般人只看得到市場零售價。其實農業部每天都公布各批發市場的「交易行情」——哪種菜今天量多價跌、哪種菜正在貴，看批發行情就知道。這一頁先教你看懂行情、去哪裡查，自動整理功能正在建置中。</p>__FIG_VEG__</div>

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
    body = body.replace("__FIG_VEG__", fig("vegprice", "../"))
    w("daily/vegprice.html", head("菜價行情查詢", "農業部農產品批發市場交易行情怎麼看：批發價與零售價差別、去哪查官方行情、颱風後菜價怎麼判斷。", 1, "daily") + body + foot(1))

def page_garbage():
    body = """
<p class="crumb"><a href="../">首頁</a> ／ <a href="./">民生查詢</a> ／ 垃圾車時間查詢</p>
<div class="hero"><h1>🚛 垃圾車時間查詢</h1>
<p>垃圾車沒有全國統一的查詢系統——每個縣市（甚至每個鄉鎮）都有自己的清運路線與時間，由各縣市環保局或公所管理。這一頁把主要縣市的官方查詢方式整理在一起，照你住的縣市對號入座。</p>__FIG_GARBAGE__</div>

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
    body = body.replace("__FIG_GARBAGE__", fig("garbage", "../"))
    w("daily/garbage.html", head("垃圾車時間查詢", "各縣市垃圾車清運時間與即時位置的官方查詢方式總整理：新北樂圾車、基隆垃圾車來了、台中清運大車隊等。", 1, "daily") + body + foot(1))

# ---------------- 國家資訊地圖（獨立嵌入頁） ----------------
def page_map():
    """地圖頁母版為 map_template.html（自給自足：內聯樣式＋Leaflet CDN，不依賴整站框架，
    App WebView 可直接套用 map.html；網址參數 ?layers=trails,outages,water 可預選圖層）。"""
    src = os.path.join(ROOT, "map_template.html")
    with open(src, encoding="utf-8") as f:
        html = f.read()
    w("map.html", html)

# ---------------- 主程式 ----------------
def main():
    with open(os.path.join(ROOT, "style.css"), "w", encoding="utf-8") as f:
        f.write(CSS.strip() + "\n")
    print("wrote style.css")
    page_index()
    page_search()
    page_home_channel()
    page_daily_channel()
    page_kids_channel()
    page_pets_channel()
    for slug, _i, _n, _d, live in CHANNELS:
        if not live:
            page_soon(slug)
    articles()
    kids_articles()
    pets_articles()
    page_outage()
    page_vegprice()
    page_garbage()
    page_map()
    urls = ["", "search.html", "map.html", "home/", "daily/", "daily/outage.html", "daily/vegprice.html", "daily/garbage.html", "kids/", "pets/"] \
        + [f"home/{s}.html" for s, _t, _d in HOME_ARTICLES] \
        + [f"kids/{s}.html" for s, _t, _d in KIDS_ARTICLES] \
        + [f"pets/{s}.html" for s, _t, _d in PETS_ARTICLES] \
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
