#!/usr/bin/env python3
"""離線路段幾何快取：不靠 Overpass，從 Geofabrik 台灣 PBF 直接萃取路段線。

背景：本機 VM 連不上任何 Overpass 端點，地圖頁即時查詢必然逾時、路段線永遠畫不出來。
本腳本改走離線路線：讀取 tools/taiwan-latest.osm.pbf（Geofabrik 台灣全檔），
對每個停電公告區的前 3 條路段（地圖頁 showRoads 只畫前 3 條），找出 OSM 路網中
同名、且離該區中心 10 公里內的最長一段 way，簡化後寫入 map/roads_cache.json。
地圖頁優先讀快取，快取命中時路段線立即出現，不再等即時查詢。

用法（需先備好 PBF 與 venv，見下方）：
    tools/.venv-osm/bin/python tools/build_roads_offline.py
PBF 取得：curl -L -o tools/taiwan-latest.osm.pbf https://download.geofabrik.de/asia/taiwan-latest.osm.pbf
venv 建置：python3 -m venv tools/.venv-osm && tools/.venv-osm/bin/pip install osmium
快取格式與 Overpass 版相同：{"version": 1, "roads": {"縣市|鄉鎮|路段": [[lat, lon], ...]}}
本腳本只新增缺失的 key，不覆蓋既有快取；日後公告換新路段時重跑即可補齊。
"""
import json, os, sys, math, glob
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PBF = os.path.join(ROOT, "tools", "taiwan-latest.osm.pbf")
CACHE_PATH = os.path.join(ROOT, "map", "roads_cache.json")

try:
    import osmium
except ImportError:
    sys.exit("需要 pyosmium：tools/.venv-osm/bin/pip install osmium")


def approx_km(lat1, lon1, lat2, lon2):
    dlat = (lat1 - lat2) * 111.0
    dlon = (lon1 - lon2) * 111.0 * math.cos(math.radians((lat1 + lat2) / 2.0))
    return math.hypot(dlat, dlon)


def dp_simplify(pts, tol):
    """Douglas-Peucker（經緯度平面近似，顯示用、容差約 30 公尺）。"""
    if len(pts) <= 2:
        return pts

    def perp(p, a, b):
        ax, ay, bx, by, px, py = a[1], a[0], b[1], b[0], p[1], p[0]
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b - a < 2:
            continue
        dmax, idx = 0.0, -1
        for i in range(a + 1, b):
            d = perp(pts[i], pts[a], pts[b])
            if d > dmax:
                dmax, idx = d, i
        if dmax > tol:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    return [p for p, k in zip(pts, keep) if k]


class RoadHandler(osmium.SimpleHandler):
    def __init__(self, wanted_names):
        super().__init__()
        self.wanted = wanted_names
        self.ways = defaultdict(list)  # road name -> [ [(lat, lon), ...], ... ]

    def way(self, w):
        if "highway" not in w.tags:
            return
        name = w.tags.get("name")
        if name not in self.wanted:
            return
        pts = []
        for n in w.nodes:
            try:
                loc = n.location
                if loc.valid():
                    pts.append((loc.lat, loc.lon))
            except Exception:
                pass
        if len(pts) >= 2:
            self.ways[name].append(pts)


def main():
    districts = []
    for fp in sorted(glob.glob(os.path.join(ROOT, "map", "outages_*.json"))):
        d = json.load(open(fp, encoding="utf-8"))
        districts.extend(d.get("districts", []))
    cache = {}
    if os.path.exists(CACHE_PATH):
        try:
            cache = json.load(open(CACHE_PATH, encoding="utf-8")).get("roads", {})
        except Exception:
            cache = {}
    needed = {}  # key -> (county, district, road, lat, lng)
    for dist in districts:
        lat, lng = dist.get("lat"), dist.get("lng")
        if lat is None or lng is None:
            continue
        for road in (dist.get("roads") or [])[:3]:
            key = f"{dist['county']}|{dist['district']}|{road}"
            if key not in cache:
                needed[key] = (dist["county"], dist["district"], road, lat, lng)
    print(f"districts: {len(districts)}, cache existing: {len(cache)}, keys needed: {len(needed)}")
    if not needed:
        print("nothing to do")
        return
    wanted = set(v[2] for v in needed.values())
    print(f"distinct road names to find: {len(wanted)}")
    if not os.path.exists(PBF):
        sys.exit(f"PBF not found: {PBF}")
    handler = RoadHandler(wanted)
    print("scanning PBF (this takes a few minutes)...")
    handler.apply_file(PBF, locations="sparse_file_array")
    print(f"ways collected: {sum(len(v) for v in handler.ways.values())} across {len(handler.ways)} names")

    def way_len(pts):
        return sum(approx_km(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
                   for i in range(len(pts) - 1))

    added, missing, fallback_used = [], [], []
    for key, (county, district, road, lat, lng) in sorted(needed.items()):
        cands = []
        for pts in handler.ways.get(road, []):
            if min(approx_km(lat, lng, p[0], p[1]) for p in pts) <= 10.0:
                cands.append(pts)
        used_fallback = False
        if not cands:
            # 備援：公告路名無段數、OSM 有分段時（如「崇德路」對「崇德路一段」）
            for name, ways in handler.ways.items():
                if name.startswith(road) and len(name) > len(road) and name[len(road)] in "一二三四五六七八九十0123456789":
                    for pts in ways:
                        if min(approx_km(lat, lng, p[0], p[1]) for p in pts) <= 10.0:
                            cands.append(pts)
            used_fallback = bool(cands)
        if not cands:
            missing.append(key)
            continue
        best = max(cands, key=way_len)
        line = dp_simplify(best, 0.0003)
        line = [[round(p[0], 5), round(p[1], 5)] for p in line]
        cache[key] = line
        added.append(key)
        if used_fallback:
            fallback_used.append(key)
    json.dump({"version": 1, "roads": cache},
              open(CACHE_PATH, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"added: {len(added)}, fallback: {len(fallback_used)}, missing: {len(missing)}, cache total: {len(cache)}")
    print(f"cache file size: {os.path.getsize(CACHE_PATH)} bytes")
    if missing:
        print("missing keys (no OSM way within 10km, e.g. renamed roads like 台中港路->台灣大道):")
        for k in missing[:60]:
            print("  ", k)
        if len(missing) > 60:
            print(f"  ... and {len(missing) - 60} more")


if __name__ == "__main__":
    main()
