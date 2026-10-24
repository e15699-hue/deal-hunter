#!/usr/bin/env python3
"""國家資訊地圖：幾何框架管線（未來性框架）。

跑在 refresh_map_data.sh 的抓取之後、推送之前，每次資料更新都重跑，
所以新公告、新路段會自動進入框架，不用人工重做。

做兩件事：
1. 路段名萃取：從停電公告 samples 文字解析路段名（路／街／大道／巷／弄＋段），
   寫回各區 districts 的 `roads` 欄位（依出現次數排序、每區最多 6 條）。
   注意：台電公告偶有私用區字元（造字），萃取時會被截斷，屬已知限制，
   查不到幾何時地圖頁會自動退回只顯示區域框＋文字，不會壞掉。
2. 路段幾何快取（可選）：`--precompute N` 時，對前 N 條路段查 Overpass（開放街圖路網），
   把幾何線段寫入 map/roads_cache.json（key：縣市｜鄉鎮｜路段）。
   地圖頁優先讀快取，查無才即時查 Overpass；快取可隨排程逐批補齊，不必一次全做完。

區域框資料（map/boundaries/）為靜態圖資，由 tools/build_boundaries.py 一次性建置，
本腳本不動它；地圖頁點標記時依縣市分檔即時載入（手機輕量：不一次全載）。
"""
import json, os, re, sys, glob, time, urllib.request, urllib.parse
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROAD_RE = re.compile(r"[\u4e00-\u9fff]{1,8}?(?:大道|路|街|巷|弄)(?:[一二三四五六七八九十\d]+段)?")
SKIP = set("停電短暫復電施工維護改善更換遷移新增設線路開關變壓器設備故障搶修".split())


PREFIX_RE = re.compile(r"^(?:[\u4e00-\u9fff]{1,3}[縣市])?(?:[\u4e00-\u9fff]{1,5}[鄉鎮市區])?(?:[\u4e00-\u9fff]{1,5}[村里])?")


def clean_road(tok):
    # 公告地址常帶完整前綴（南投縣仁愛鄉中華巷、台中市北區力行路），OSM 路名只有最後一段，
    # 須把縣市／鄉鎮／村里前綴剝掉，否則即時查詢一定查不到。
    return PREFIX_RE.sub("", tok)


def extract_roads(samples):
    cnt = Counter()
    for s in samples or []:
        text = re.sub(r"[\uE000-\uF8FF]", "", s)  # 私用區造字先移除，避免截斷整段
        for m in ROAD_RE.finditer(text):
            tok = clean_road(m.group(0)).lstrip("與及和、之")
            if len(tok) < 2 or tok in SKIP:
                continue
            if len(tok) == 2 and tok[0] in "一二三四五六七八九十" and tok[1] in "巷弄":
                continue  # 通用編號巷（每鄉鎮都有），無法對到唯一路段
            if tok.endswith("弄路"):
                continue
            if re.search(r"(停電|復電|施工|維護|改善|更換|遷移|線路)", tok):
                continue
            cnt[tok] += 1
    return [r for r, _ in cnt.most_common(6)]


def overpass_road(name, lat, lng, timeout=40):
    q = (f'[out:json][timeout:25];'
         f'way["name"="{name}"]["highway"](around:10000,{lat},{lng});'
         f'out geom;')
    req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                                 data=urllib.parse.urlencode({"data": q}).encode(),
                                 headers={"User-Agent": "HowkangLife/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        d = json.load(resp)
    best = None
    for el in d.get("elements", []):
        geom = el.get("geometry") or []
        if len(geom) >= 2:
            line = [[g["lat"], g["lon"]] for g in geom]
            if best is None or len(line) > len(best):
                best = line
    return best


def main():
    precompute = 0
    if "--precompute" in sys.argv:
        try:
            precompute = int(sys.argv[sys.argv.index("--precompute") + 1])
        except Exception:
            precompute = 0
    cache_path = os.path.join(ROOT, "map", "roads_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        try:
            cache = json.load(open(cache_path, encoding="utf-8")).get("roads", {})
        except Exception:
            cache = {}
    files = sorted(glob.glob(os.path.join(ROOT, "map", "outages_*.json")))
    districts = []
    for fp in files:
        d = json.load(open(fp, encoding="utf-8"))
        changed = False
        for dist in d.get("districts", []):
            roads = extract_roads(dist.get("samples"))
            if roads != dist.get("roads"):
                dist["roads"] = roads
                changed = True
            districts.append(dist)
        if changed:
            json.dump(d, open(fp, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"outage districts: {len(districts)}, with roads: {sum(1 for x in districts if x.get('roads'))}")
    if precompute > 0:
        # 優先順序：台中市（使用者所在地）＋公告筆數多者先補
        ordered = sorted(districts, key=lambda x: (0 if (x.get("county") or "").strip() == "台中市" else 1, -(x.get("count") or 0)))
        done = 0
        for dist in ordered:
            if done >= precompute:
                break
            county = (dist.get("county") or "").strip()
            town = (dist.get("district") or "").strip()
            for road in (dist.get("roads") or [])[:2]:
                key = f"{county}|{town}|{road}"
                if key in cache or done >= precompute:
                    continue
                try:
                    line = overpass_road(road, dist["lat"], dist["lng"])
                    if line:
                        cache[key] = line
                        print(f"cached {key} ({len(line)} pts)")
                    else:
                        print(f"no geom {key}")
                except Exception as e:
                    print(f"overpass err {key}: {e}")
                done += 1
                time.sleep(1.2)
        json.dump({"version": 1, "roads": cache}, open(cache_path, "w", encoding="utf-8"),
                  ensure_ascii=False, separators=(",", ":"))
        print(f"roads_cache entries: {len(cache)}")
    else:
        if not os.path.exists(cache_path):
            json.dump({"version": 1, "roads": {}}, open(cache_path, "w", encoding="utf-8"),
                      ensure_ascii=False, separators=(",", ":"))
            print("roads_cache created (empty)")


if __name__ == "__main__":
    main()
