#!/usr/bin/env python3
"""好康生活 Phase 1 預覽推送：推到 deal-hunter repo 的 life/ 資料夾。
比照好康網推送鐵律：原始 UTF-8、推送前 assert 佔位字串、小批次、raw md5 驗證。冪等可重跑。
"""
import json, subprocess, sys, os, hashlib, urllib.request, time

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_PREFIX = "life"
BANNED = ("PLACEHOLDER", "__INDEX__")
import glob as _glob
BASE_FILES = [
    "index.html", "search.html", "style.css", "sitemap.xml", "robots.txt", "README.md", "build.py", "push_preview.py",
    "map.html", "map_template.html",
    "home/index.html", "home/quote.html", "home/designer.html",
    "home/cabinet.html", "home/process.html", "home/contract.html",
    "daily/index.html", "daily/outage.html", "daily/vegprice.html", "daily/garbage.html",
    "kids/index.html", "kids/guide.html", "kids/vs.html", "kids/price.html", "kids/faq.html",
    "senior/index.html", "health/index.html", "study/index.html", "ai/index.html", "car/index.html",
    "tools/fetch_outages.py", "tools/fetch_water.py", "tools/fetch_trails.py",
    "tools/geocode.py", "tools/geocode_cache.json", "tools/trail_catalog.json",
    "img/credits.json", "img/CREDITS.md",
]
# 停電分片（20 區處，檔名隨資料量動態增減）與地圖快照一律動態納入，不再手寫清單
FILES = BASE_FILES + sorted(os.path.relpath(p, ROOT) for p in _glob.glob(os.path.join(ROOT, "daily", "outages", "*.json"))) \
    + sorted(os.path.relpath(p, ROOT) for p in _glob.glob(os.path.join(ROOT, "map", "*.json")))
BATCH_MAX = 58000  # bytes（content 合計上限，保守低於單次參數上限）

def load():
    contents = {}
    for rel in FILES:
        c = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        if rel != "push_preview.py":  # 本腳本自身含 BANNED 定義字串，豁免
            for s in BANNED:
                assert s not in c, f"{rel} 含佔位字串 {s}，中止推送"
        contents[rel] = c
    assert "好康生活" in contents["index.html"]
    assert "outages/index.json" in contents["daily/outage.html"]
    assert "報價單" in contents["home/quote.html"]
    assert "OiKID" in contents["kids/guide.html"] and "親子學習" in contents["kids/index.html"], "親子學習頻道內容檢查"
    assert '<img' in contents["index.html"] and '<img' in contents["home/quote.html"], "圖片標準：首頁與文章頁必須有圖"
    for rel, c in contents.items():
        if rel.endswith(".html") and rel not in ("map.html", "map_template.html"):
            # map.html 與其母版 map_template.html 為國家資訊地圖獨立工具頁（App WebView 嵌入用、載入輕量優先；地圖本身即為視覺主體），豁免圖片標準
            assert '<img' in c, f"{rel} 缺圖，不符合圖片標準"
    print("assert 全過，共", len(contents), "檔")
    return contents

def batches(contents):
    out, cur, size = [], [], 0
    for rel in FILES:
        b = len(contents[rel].encode("utf-8"))
        if cur and size + b > BATCH_MAX:
            out.append(cur); cur, size = [], 0
        cur.append(rel); size += b
    if cur: out.append(cur)
    return out

def push(batch, contents):
    args = {
        "owner": "e15699-hue", "repo": "deal-hunter", "branch": "main",
        "message": "好康生活：新增國家資訊地圖（步道／停電／停水圖層）＋停電擴至全台 20 區處",
        "files": [{"path": f"{REPO_PREFIX}/{p}", "content": contents[p]} for p in batch],
    }
    r = subprocess.run(
        ["/opt/hatch/bin/github", "call-tool", "--name", "push_files",
         "--arguments-json", json.dumps(args, ensure_ascii=False)],
        capture_output=True, text=True, timeout=1500)
    out = (r.stdout or "") + (r.stderr or "")
    print("batch", batch, "RC:", r.returncode, flush=True)
    if '"isError":true' in out:
        print(out[-800:]); return 1
    if "equivalent connector write is already running" in out:
        print("遇到寫入鎖"); return 2
    return 0

def md5_remote(rel):
    url = f"https://raw.githubusercontent.com/e15699-hue/deal-hunter/main/{REPO_PREFIX}/{rel}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return hashlib.md5(r.read()).hexdigest()

def main():
    contents = load()
    for i, b in enumerate(batches(contents), 1):
        rc = push(b, contents)
        if rc == 2:
            print("等 60 秒後重試本批"); time.sleep(60); rc = push(b, contents)
        if rc != 0:
            print("推送失敗於批次", i, b); sys.exit(1)
        time.sleep(3)
    print("推送完成，開始 raw md5 驗證")
    ok = 0
    for rel in FILES:
        local = hashlib.md5(contents[rel].encode("utf-8")).hexdigest()
        for attempt in range(3):
            try:
                if md5_remote(rel) == local:
                    ok += 1; break
            except Exception as e:
                print(rel, "raw 讀取失敗", e)
            time.sleep(20)
        else:
            print("MISMATCH", rel)
    print(f"md5 驗證 {ok}/{len(FILES)}")
    sys.exit(0 if ok == len(FILES) else 2)

if __name__ == "__main__":
    main()
