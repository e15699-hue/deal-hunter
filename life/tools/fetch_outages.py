#!/usr/bin/env python3
"""台電計畫性工作停電公告 → daily/outages.json 快照產生器。
資料來源：台灣電力公司各區營業處「計畫性工作停電公告」官方頁面（service.taipower.com.tw）。
Phase 1 建置時快照；Phase 2 預計改為每日排程自動更新。
隻取今天起的公告，避免快照膨脹。
"""
import json, re, sys, urllib.request, datetime, os

BRANCHES = [
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

FW = str.maketrans("０１２３４５６７８９", "0123456789")

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip().translate(FW)
    return s

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (howkang-life snapshot builder)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")

def parse(branch, html):
    out = []
    # 以日期錨點切段
    parts = re.split(r'<a name="(\d{8})"></a>', html)
    # parts: [pre, date1, seg1, date2, seg2, ...]
    for i in range(1, len(parts) - 1, 2):
        ymd, seg = parts[i], parts[i + 1]
        date = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
        rows = re.findall(r'<td class="time">(.*?)</td>\s*<td class="note">(.*?)</td>', seg, re.S)
        for t, n in rows:
            note = clean(n)
            m = re.match(r"([A-Z]\d+)\s*[（(]([^）)]*)[）)]\s*(.*)", note)
            if m:
                code, reason, area = m.group(1), m.group(2), m.group(3)
            else:
                code, reason, area = "", "", note
            out.append({"branch": branch, "date": date, "time": clean(t),
                        "code": code, "reason": reason, "area": area})
    return out

TZ = datetime.timezone(datetime.timedelta(hours=8))

def main():
    today = datetime.datetime.now(TZ).date().isoformat()
    all_rows, stats = [], {}
    for name, url in BRANCHES:
        try:
            rows = [r for r in parse(name, fetch(url)) if r["date"] >= today]
            stats[name] = len(rows)
            all_rows += rows
            print(name, "OK", len(rows), "筆（今天起）", file=sys.stderr)
        except Exception as e:
            stats[name] = f"ERROR {e}"
            print(name, "ERROR", e, file=sys.stderr)
    seen, uniq = set(), []
    for r in all_rows:
        k = (r["branch"], r["date"], r["time"], r["code"], r["area"])
        if k not in seen:
            seen.add(k); uniq.append(r)
    all_rows = uniq
    all_rows.sort(key=lambda r: (r["date"], r["branch"]))
    payload = {
        "source": "台灣電力公司各區營業處計畫性工作停電公告（service.taipower.com.tw）",
        "generated_at": datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M"),
        "branches": [b[0] for b in BRANCHES],
        "count": len(all_rows),
        "items": all_rows,
    }
    out_path = os.path.join(os.path.dirname(__file__), "..", "daily", "outages.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("TOTAL", len(all_rows), "→", out_path)
    print(json.dumps(stats, ensure_ascii=False))
    write_web_snapshot(payload)
    write_map_snapshot(payload)

CODES = {"基隆區營業處": "kl", "北市區營業處": "tp", "桃園區營業處": "ty",
         "新竹區營業處": "hc", "台中區營業處": "tc", "彰化區營業處": "ch",
         "嘉義區營業處": "cy", "台南區營業處": "tn", "高雄區營業處": "kh",
         "屏東區營業處": "pt", "台東區營業處": "tt", "花蓮區營業處": "hl",
         "宜蘭區營業處": "yl", "澎湖區營業處": "ph", "北南區營業處": "tps",
         "北北區營業處": "tpn", "北西區營業處": "tpx", "南投區營業處": "nt",
         "鳳山區營業處": "fs", "雲林區營業處": "yun"}
# 區處→所在縣市（地區文字解析失敗時的備援定位）
BRANCH_CITY = {"基隆區營業處": "基隆市", "北市區營業處": "台北市", "桃園區營業處": "桃園市",
               "新竹區營業處": "新竹市", "台中區營業處": "台中市", "彰化區營業處": "彰化縣",
               "嘉義區營業處": "嘉義市", "台南區營業處": "台南市", "高雄區營業處": "高雄市",
               "屏東區營業處": "屏東縣", "台東區營業處": "台東縣", "花蓮區營業處": "花蓮縣",
               "宜蘭區營業處": "宜蘭縣", "澎湖區營業處": "澎湖縣", "北南區營業處": "台北市",
               "北北區營業處": "台北市", "北西區營業處": "台北市", "南投區營業處": "南投縣",
               "鳳山區營業處": "高雄市", "雲林區營業處": "雲林縣"}

def write_map_snapshot(payload):
    """國家資訊地圖・停電圖層：以鄉鎮市區彙總（每區一個標記），不把數千筆明細全上圖。
    座標來自 Nominatim 快取（tools/geocode_cache.json），查不到的區保留 lat/lng=null、地圖列表仍顯示。"""
    import datetime as _dt
    from geocode import geocode, _load as load_cache, _save as save_cache
    base = os.path.join(os.path.dirname(__file__), "..", "map")
    os.makedirs(base, exist_ok=True)
    today = _dt.datetime.now(TZ).date()
    horizon = (today + _dt.timedelta(days=14)).isoformat()
    buckets = {}
    for r in payload["items"]:
        if r["date"] >= horizon:
            continue
        area = (r["area"] or "").replace("臺", "台")
        area = re.sub(r"^[^\u4e00-\u9fa5]+", "", area)  # 去掉開頭標點（避免縣市誤含「，」）
        m = re.search(r"(.{2,3}[縣市])(.{1,5}?[區鄉鎮市])", area)
        if m:
            county, district = m.group(1), m.group(2)
        else:
            # 部分公告 area 開頭直接就是區名（無縣市前綴），用區處所屬縣市補縣市
            m2 = re.match(r"(.{1,5}?[區鄉鎮市])", area)
            if m2:
                county, district = BRANCH_CITY.get(r["branch"], ""), m2.group(1)
            else:
                county, district = BRANCH_CITY.get(r["branch"], ""), ""
        key = (county, district, r["branch"])
        b = buckets.setdefault(key, {"county": county, "district": district, "branches": set(),
                                     "count": 0, "earliest": r["date"], "samples": []})
        b["branches"].add(r["branch"])
        b["count"] += 1
        b["earliest"] = min(b["earliest"], r["date"])
        if len(b["samples"]) < 3:
            b["samples"].append(f'{r["date"]}｜{r["time"]}｜{area[:60]}')
    cache = load_cache()
    out = []
    for n, ((county, district, _br), b) in enumerate(sorted(buckets.items())):
        q = (county + district) if district else county
        loc = geocode(q, cache=cache, save=False) if q else None
        if loc is None and district and county:
            loc = geocode(county, cache=cache, save=False)  # 里／工業區等小地名查不到時退回縣市中心
        if n % 25 == 24:
            save_cache(cache)  # 排程中途被中斷也不用全部重查
        out.append({"county": county, "district": district, "count": b["count"],
                    "earliest": b["earliest"], "branches": sorted(b["branches"]),
                    "samples": b["samples"],
                    "lat": loc[0] if loc else None, "lng": loc[1] if loc else None})
    save_cache(cache)
    with open(os.path.join(base, "outages_map.json"), "w", encoding="utf-8") as f:
        json.dump({"source": payload["source"], "generated_at": payload["generated_at"],
                   "total_items": sum(b["count"] for b in out),
                   "districts": out}, f, ensure_ascii=False)
    located = sum(1 for b in out if b["lat"] is not None)
    print(f"map snapshot: {len(out)} 區，{located} 區有座標 → map/outages_map.json", file=sys.stderr)

def write_web_snapshot(payload):
    """網站用精簡快照：未來 14 天、每區處一檔、地區文字截 220 字（全文見台電官方頁）。
    分檔是為了讓每個檔案小於 GitHub push_files 單次上限。"""
    import datetime as _dt
    base = os.path.join(os.path.dirname(__file__), "..", "daily", "outages")
    os.makedirs(base, exist_ok=True)
    today = _dt.datetime.now(TZ).date()
    horizon = (today + _dt.timedelta(days=14)).isoformat()
    idx = {"generated_at": payload["generated_at"], "source": payload["source"], "branches": []}
    for bname in payload["branches"]:
        items = []
        for r in payload["items"]:
            if r["branch"] == bname and r["date"] < horizon:
                area = r["area"]
                if len(area) > 220:
                    area = area[:220] + "…"
                items.append({"date": r["date"], "time": r["time"], "reason": r["reason"], "area": area})
        code = CODES[bname]
        # 每片控制在約 55KB bytes，避免超過 push_files 單次上限
        chunks, cur = [], []
        for it in items:
            cur.append(it)
            size = len(json.dumps({"branch": bname, "items": cur}, ensure_ascii=False).encode("utf-8"))
            if size > 55000:
                chunks.append(cur); cur = []
        if cur or not chunks:
            chunks.append(cur)
        for n, chunk in enumerate(chunks, 1):
            fname = f"{code}.json" if n == 1 else f"{code}{n}.json"
            with open(os.path.join(base, fname), "w", encoding="utf-8") as f:
                json.dump({"branch": bname, "items": chunk}, f, ensure_ascii=False)
            idx["branches"].append({"name": bname, "file": fname, "count": len(chunk)})
        print("web snapshot", bname, len(items), "→", len(chunks), "片", file=sys.stderr)
    with open(os.path.join(base, "index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False)
    print("web snapshot index →", base)

if __name__ == "__main__":
    main()
