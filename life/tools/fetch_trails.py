#!/usr/bin/env python3
"""山區步道開放狀態 → map/trails.json 快照產生器（國家資訊地圖・步道圖層）。
狀態來源：林業及自然保育署「台灣山林悠遊網」各步道頁面的即時狀態欄
（開放／暫停開放等原文照錄）；不在該站目錄內的步道（國家公園系統等），
狀態一律標「查無最新公告」，不編造開放／封鎖。
座標來自 Nominatim（OpenStreetMap）查詢＋快取，不手寫座標。
步道目錄 tools/trail_catalog.json 由山林悠遊網步道頁 tr_id 枚舉產生（見 README）。
"""
import json, os, re, sys, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TZ = datetime.timezone(datetime.timedelta(hours=8))
RECREATION = "https://recreation.forest.gov.tw"

# （步道名，縣市，管理單位／所屬山區）——縣市為公開地理資訊，僅供顯示與篩選
TRAILS = [
    ("玉山主峰步道", "南投縣", "玉山國家公園"),
    ("雪山主峰步道", "苗栗縣", "雪霸國家公園"),
    ("合歡山主峰步道", "南投縣", "太魯閣國家公園"),
    ("嘉明湖國家步道", "台東縣", "林業保育署台東分署"),
    ("北大武山步道", "屏東縣", "林業保育署屏東分署"),
    ("霞喀羅國家步道", "新竹縣", "林業保育署新竹分署"),
    ("見晴懷古步道", "宜蘭縣", "林業保育署宜蘭分署"),
    ("特富野古道", "嘉義縣", "林業保育署嘉義分署"),
    ("奮瑞古道", "嘉義縣", "林業保育署嘉義分署"),
    ("奮起湖大凍山步道", "嘉義縣", "林業保育署嘉義分署"),
    ("能高越嶺道西段", "南投縣", "林業保育署南投分署"),
    ("能高越嶺道東段", "花蓮縣", "林業保育署花蓮分署"),
    ("八仙山主峰步道", "台中市", "林業保育署台中分署"),
    ("鳶嘴山步道", "台中市", "林業保育署台中分署"),
    ("加里山登山步道", "苗栗縣", "林業保育署新竹分署"),
    ("聖母登山步道", "宜蘭縣", "林業保育署宜蘭分署"),
    ("茶壺山步道", "新北市", "瑞芳區公所"),
    ("大屯山步道", "台北市", "陽明山國家公園"),
    ("七星山步道", "台北市", "陽明山國家公園"),
    ("柴山步道", "高雄市", "壽山國家自然公園"),
    ("大坑登山步道", "台中市", "台中市政府"),
    ("軍艦岩步道", "台北市", "陽明山國家公園"),
    ("錐麓古道", "花蓮縣", "太魯閣國家公園"),
    ("浸水營國家步道（東段）", "屏東縣", "林業保育署屏東分署"),
    ("阿朗壹古道", "屏東縣", "屏東縣政府"),
    ("阿里山巨木群步道", "嘉義縣", "林業保育署嘉義分署"),
]

def fetch(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (howkang-life snapshot builder)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")

def norm(s):
    return re.sub(r"[\s\-：:・、（）()]", "", s or "")

def trail_status(tr_id):
    """抓山林悠遊網步道頁狀態欄原文；失敗回傳 None（不猜狀態）。"""
    try:
        html = fetch(f"{RECREATION}/Trail/RT?tr_id={tr_id}")
        flat = re.sub(r"\s+", " ", html)
        m = re.search(r'class="status"[^>]*>(.*?)</div>', flat)
        return m.group(1).strip() if m else None
    except Exception:
        return None

# 顯示名 → 山林悠遊網目錄正式名（子字串比對不到時的明確對照，避免張冠李戴）
ALIASES = {
    "阿里山巨木群步道": "阿里山國家森林遊樂區巨木群步道",
}
# 顯示名 → 優先覆寫查詢（正式名會被 Nominatim 錯配到別處時用，例：玉山主峰步道→台北、柴山步道→木柵；命中者一律標 geo_approx）
GEO_OVERRIDES = {
    "玉山主峰步道": "玉山",
    "柴山步道": "柴山 高雄市",
}
# 顯示名 → Nominatim 查詢備援（正式步道名查不到時用；命中者一律標 geo_approx）
GEO_ALIASES = {
    "合歡山主峰步道": "合歡山主峰",
    "霞喀羅國家步道": "霞喀羅古道",
    "奮起湖大凍山步道": "奮起湖",  # 登山口一帶概略位置
    "能高越嶺道西段": "能高越嶺道",
    "能高越嶺道東段": "能高越嶺道",
    "八仙山主峰步道": "八仙山",
    "浸水營國家步道（東段）": "浸水營古道",
    "阿里山巨木群步道": "阿里山巨木群",
}

def main():
    from geocode import geocode, _load as load_cache, _save as save_cache
    catalog = {}
    cat_path = os.path.join(HERE, "trail_catalog.json")
    if os.path.exists(cat_path):
        with open(cat_path, encoding="utf-8") as f:
            catalog = json.load(f)
    # tr_id → 名稱正規化對照
    by_norm = {norm(v["name"]): k for k, v in catalog.items()}
    now = datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    cache = load_cache()
    items, no_status, no_geo = [], [], []
    for name, county, unit in TRAILS:
        tr_id = None
        if name in ALIASES and norm(ALIASES[name]) in by_norm:
            tr_id = by_norm[norm(ALIASES[name])]
        else:
            for cn, tid in by_norm.items():
                if norm(name) == cn or norm(name) in cn or cn in norm(name):
                    tr_id = tid
                    break
        status_raw = trail_status(tr_id) if tr_id else None
        if status_raw is None:
            no_status.append(name)
        loc = None
        geo_approx = False
        if name in GEO_OVERRIDES:
            loc = geocode(f"{GEO_OVERRIDES[name]} 台灣", cache=cache, save=False)
            geo_approx = bool(loc)
        if not loc:
            loc = geocode(f"{name} 台灣", cache=cache, save=False)
        if not loc:
            loc = geocode(f"{name} {county}", cache=cache, save=False)
        if not loc and name in GEO_ALIASES:
            loc = geocode(f"{GEO_ALIASES[name]} 台灣", cache=cache, save=False)
            geo_approx = bool(loc)
        if not loc:
            no_geo.append(name)
        items.append({
            "name": name, "county": county, "unit": unit,
            "status_raw": status_raw or "查無最新公告",
            "geo_approx": geo_approx,
            "lat": loc[0] if loc else None, "lng": loc[1] if loc else None,
            "source": "林業及自然保育署台灣山林悠遊網" if tr_id else "各管理處公告（本站尚未串接即時狀態）",
            "source_url": f"{RECREATION}/Trail/RT?tr_id={tr_id}" if tr_id else "",
            "updated_at": now,
        })
    save_cache(cache)
    payload = {"source": "林業及自然保育署台灣山林悠遊網（步道頁即時狀態）＋各管理處公告",
               "generated_at": now, "count": len(items), "items": items}
    out = os.path.join(ROOT, "map", "trails.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"trails: {len(items)} 條（有即時狀態 {len(items)-len(no_status)}，無狀態 {len(no_status)}：{no_status}；無座標 {no_geo}）→ {out}")

if __name__ == "__main__":
    main()
