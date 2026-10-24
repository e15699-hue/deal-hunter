#!/usr/bin/env python3
"""台水停水公告 → map/water.json 快照產生器（國家資訊地圖・停水圖層）。
資料來源：台灣自來水公司「停水公告查詢系統」官方 API
（https://web.water.gov.tw/wateroffapi/disaster/listWater_Off_Active_All）。
只收最新版（isLatest）公告；座標來自官方公告附的多邊形範圍（EPSG:3857 轉 WGS84）
取中心點＋簡化外框，不手寫座標；時間以台灣時間（UTC+8）顯示。
"""
import json, math, os, re, sys, urllib.request, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
API = "https://web.water.gov.tw/wateroffapi/disaster/listWater_Off_Active_All"
SOURCE_URL = "https://web.water.gov.tw/wateroff/"
TZ = datetime.timezone(datetime.timedelta(hours=8))

COUNTY_CODE = {
    "63000": "台北市", "65000": "新北市", "66000": "台中市", "67000": "台南市",
    "68000": "桃園市", "64000": "高雄市", "10002": "宜蘭縣", "10004": "新竹縣",
    "10005": "苗栗縣", "10007": "彰化縣", "10008": "南投縣", "10009": "雲林縣",
    "10010": "嘉義縣", "10013": "屏東縣", "10014": "台東縣", "10015": "花蓮縣",
    "10016": "澎湖縣", "10017": "基隆市", "10018": "新竹市", "10019": "嘉義市",
    "09020": "金門縣", "09007": "連江縣",
}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (howkang-life snapshot builder)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")

def to_wgs84(x, y):
    """EPSG:3857 公尺 → WGS84 經緯度。"""
    lng = x / 6378137.0 * 180.0 / math.pi
    lat = math.degrees(math.atan(math.sinh(y / 6378137.0)))
    return lng, lat

def simplify(ring, max_pts=40):
    if len(ring) <= max_pts:
        return ring
    step = len(ring) / max_pts
    return [ring[int(i * step)] for i in range(max_pts)]

def parse_area(area_str):
    """官方範圍多邊形字串 → (中心點 (lat, lng), 簡化外框 [[lng, lat], ...]) 或 (None, None)。"""
    if not area_str or area_str == "None":
        return None, None
    try:
        geo = json.loads(area_str.replace("'", '"')) if isinstance(area_str, str) else area_str
    except Exception:
        return None, None
    try:
        coords = geo["coordinates"]
        # MultiPolygon: 取第一個 polygon 的外框
        ring = coords[0][0]
        pts = [to_wgs84(x, y) for x, y in ring]
        pts = [(lng, lat) for lng, lat in pts if 119.0 <= lng <= 123.0 and 21.0 <= lat <= 26.0]
        if not pts:
            return None, None
        clng = sum(p[0] for p in pts) / len(pts)
        clat = sum(p[1] for p in pts) / len(pts)
        return (round(clat, 5), round(clng, 5)), [[round(lng, 5), round(lat, 5)] for lng, lat in simplify(pts)]
    except Exception:
        return None, None

def local_date(utc_str):
    """'2026-10-23T16:00:00.000+0000' → 台灣日期 '2026-10-24'。"""
    try:
        dt = datetime.datetime.strptime(utc_str[:19], "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=datetime.timezone.utc).astimezone(TZ)
        return dt.date().isoformat()
    except Exception:
        return ""

COUNTY_LIST = ["台北市", "新北市", "桃園市", "台中市", "台南市", "臺南市", "高雄市",
               "基隆市", "新竹市", "嘉義市", "宜蘭縣", "新竹縣", "苗栗縣", "彰化縣",
               "南投縣", "雲林縣", "嘉義縣", "屏東縣", "台東縣", "花蓮縣",
               "澎湖縣", "金門縣", "連江縣"]

def split_county_district(region, counties):
    """從範圍文字取縣市＋鄉鎮市區；取不到縣市時用 affectedCounties 代碼補。
    縣市以明確清單比對（避免「宜蘭市」被誤認成縣市）；臺→台統一寫法。"""
    rest = (region or "").replace("臺", "台")
    county = ""
    for c in COUNTY_LIST:
        if c.replace("臺", "台") in rest:
            county = c.replace("臺", "台")
            break
    if not county and counties:
        county = COUNTY_CODE.get(str(counties[0]), "")
    dm = re.search(r"[縣市]/([^/]{1,5}[區鄉鎮市])", rest)
    district = dm.group(1) if dm else ""
    if not district:
        dm2 = re.search(r"(.{1,5}[區鄉鎮市])", rest)
        district = dm2.group(1) if dm2 else ""
    return county, district

def parse_counties(raw):
    """affectedCounties 可能是字串 "['67000']" 或真正的 list，兩種都處理。"""
    if isinstance(raw, list):
        return [str(x) for x in raw]
    try:
        v = json.loads((raw or "[]").replace("'", '"'))
        return [str(x) for x in v] if isinstance(v, list) else []
    except Exception:
        return []

def main():
    data = json.loads(fetch(API))
    now = datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    items = []
    for rec in data:
        if str(rec.get("isLatest")) not in ("True", "true", "1"):
            continue
        water_region = rec.get("waterOffRegion") or ""
        down_region = rec.get("pressureDownRegion") or ""
        if water_region and water_region != "None":
            kind, region, area_str = "停水", water_region, rec.get("waterOffArea")
        elif down_region and down_region != "None":
            kind, region, area_str = "降壓", down_region, rec.get("pressureDownArea")
        else:
            continue
        reason = rec.get("waterOffReason") or rec.get("pressureDownReason") or ""
        counties = parse_counties(rec.get("affectedCounties"))
        county, district = split_county_district(region, counties)
        center, poly = parse_area(area_str)
        if not center:
            continue  # 沒有官方範圍座標就不上圖（不亂編位置）
        sd, ed = local_date(rec.get("startDate", "")), local_date(rec.get("endDate", ""))
        st, et = (rec.get("startTime") or ""), (rec.get("endTime") or "")
        items.append({
            "id": str(rec.get("id", "")), "kind": kind,
            "plan": "計畫性" if str(rec.get("isSchedule")) in ("True", "true", "1") else "突發／搶修",
            "region": region.strip(), "county": county, "district": district,
            "reason": reason.strip(), "start": f"{sd} {st}".strip(), "end": f"{ed} {et}".strip(),
            "households": rec.get("waterOffNumber") or rec.get("pressureDownNumber") or "",
            "lat": center[0], "lng": center[1], "polygon": poly,
            "source": "台灣自來水公司停水公告查詢系統", "source_url": SOURCE_URL,
        })
    items.sort(key=lambda r: (r["start"], r["county"], r["district"]))
    payload = {
        "source": "台灣自來水公司停水公告查詢系統（web.water.gov.tw/wateroffapi）",
        "source_url": SOURCE_URL,
        "generated_at": now, "count": len(items), "items": items,
    }
    out = os.path.join(ROOT, "map", "water.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print("water:", len(items), "筆 →", out)

if __name__ == "__main__":
    main()
