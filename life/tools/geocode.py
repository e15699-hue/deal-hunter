#!/usr/bin/env python3
"""共用地理編碼 helper：Nominatim（OpenStreetMap）查詢＋本機快取。
座標一律來自 OSM 回傳結果（台灣範圍驗證），不手寫座標。
快取檔 tools/geocode_cache.json 會隨專案推送，排程重跑時不再重打 API。
用法：from geocode import geocode; geocode("台中市北屯區") -> (lat, lng) 或 None
"""
import json, os, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, "geocode_cache.json")
# 台灣本島＋離島大致範圍
LAT_MIN, LAT_MAX = 21.8, 26.4
LNG_MIN, LNG_MAX = 118.0, 122.1  # 含澎湖（119.3–119.7）、金門（118.2–118.4）、馬祖

def _load():
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(cache):
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)

def geocode(name, cache=None, save=True):
    """回傳 (lat, lng) 或 None。name 為中文地名（縣市＋區/鄉鎮或步道名＋台灣）。"""
    own = cache is None
    if own:
        cache = _load()
    if name in cache:
        v = cache[name]
        return (v[0], v[1]) if v else None
    url = ("https://nominatim.openstreetmap.org/search?format=json&limit=5&countrycodes=tw&q="
           + urllib.parse.quote(name))
    req = urllib.request.Request(url, headers={"User-Agent": "howkang-life map geocoder (contact: site admin)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            results = json.loads(r.read().decode("utf-8"))
    except Exception:
        results = []
    picked = None
    for res in results:
        try:
            lat, lng = float(res["lat"]), float(res["lon"])
        except Exception:
            continue
        if LAT_MIN <= lat <= LAT_MAX and LNG_MIN <= lng <= LNG_MAX:
            picked = (lat, lng)
            break
    cache[name] = list(picked) if picked else None
    if save and own:
        _save(cache)
    time.sleep(1.1)  # Nominatim 使用政策：每秒最多 1 次查詢
    return picked
