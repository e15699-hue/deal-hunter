#!/usr/bin/env python3
"""國家資訊地圖：鄉鎮市區界線分檔（區域框資料，一次性建置）。

來源：g0v twgeojson twTown1982.geo.json（公開圖資，1982 年界線；鄉鎮形狀大致不變，
顯示用已足夠；若日後取得較新界線，換輸入檔重跑即可）。
處理：Douglas-Peucker 簡化（容差約 0.0015 度 ≈ 150 公尺，顯示用）→ 依縣市分檔，
輸出 map/boundaries/<縣市>.json，格式：{county, source, features:[{town, rings:[[[lng,lat],...]]}]}。
注意：縣市名以 1982 年為準；地圖頁比對時先比（縣市＋鄉鎮），比不到改比鄉鎮名＋取離標記最近者，
可容納升格合併後的縣市更名與同名鄉鎮（例如兩地的中正區）。
"""
import json, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/twTown1982.geo.json"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "map", "boundaries")
TOL = 0.0015


def _perp(p, a, b):
    x, y = p
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    px, py = x1 + t * dx, y1 + t * dy
    return ((x - px) ** 2 + (y - py) ** 2) ** 0.5


def simplify(ring, tol):
    if len(ring) <= 2:
        return ring
    closed = ring[0] == ring[-1]
    pts = ring[:-1] if closed else ring
    if len(pts) <= 2:
        return ring
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        dmax, idx = 0, -1
        for i in range(a + 1, b):
            d = _perp(pts[i], pts[a], pts[b])
            if d > dmax:
                dmax, idx = d, i
        if dmax > tol:
            keep[idx] = True
            stack.append((a, idx))
            stack.append((idx, b))
    out = [p for p, k in zip(pts, keep) if k]
    if closed:
        out.append(out[0])
    return out


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    by_county = {}
    n_in = n_out = 0
    for ft in d.get("features", []):
        p = ft.get("properties", {}) or {}
        county = (p.get("COUNTYNAME") or "").strip()
        town = (p.get("TOWNNAME") or "").strip()
        g = ft.get("geometry") or {}
        gt, coords = g.get("type"), g.get("coordinates") or []
        if gt == "Polygon":
            polys = [coords]
        elif gt == "MultiPolygon":
            polys = coords
        else:
            continue
        rings = []
        for poly in polys:
            for ring in poly:
                s = simplify([list(pt) for pt in ring], TOL)
                if len(s) >= 4:
                    rings.append(s)
                n_in += len(ring)
                n_out += len(s)
        if rings:
            by_county.setdefault(county, []).append({"town": town, "rings": rings})
    os.makedirs(OUT, exist_ok=True)
    total = 0
    index = {}
    for county, feats in sorted(by_county.items()):
        path = os.path.join(OUT, county + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"county": county, "source": "g0v twgeojson twTown1982（顯示用簡化）",
                       "features": feats}, f, ensure_ascii=False, separators=(",", ":"))
        total += os.path.getsize(path)
        print(f"{county}: {len(feats)} 鄉鎮, {os.path.getsize(path)//1024} KB")
        for ft in feats:
            index.setdefault(ft["town"], []).append(county)
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    # 區塊點選用：每縣市外接矩形，供地圖頁判斷視野交集後才載入該縣市檔（手機輕量）
    bboxes = {}
    for county, feats in by_county.items():
        xs = [pt[0] for ft in feats for ring in ft["rings"] for pt in ring]
        ys = [pt[1] for ft in feats for ring in ft["rings"] for pt in ring]
        bboxes[county] = {"minLng": round(min(xs), 4), "maxLng": round(max(xs), 4),
                          "minLat": round(min(ys), 4), "maxLat": round(max(ys), 4)}
    with open(os.path.join(OUT, "bboxes.json"), "w", encoding="utf-8") as f:
        json.dump(bboxes, f, ensure_ascii=False, separators=(",", ":"))
    print(f"counties: {len(by_county)}, towns: {len(index)}, total: {total//1024} KB, vertices {n_in} -> {n_out}")


if __name__ == "__main__":
    main()
