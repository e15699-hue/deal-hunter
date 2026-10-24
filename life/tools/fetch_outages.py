#!/usr/bin/env python3
"""台電計畫性工作停電公告 → daily/outages.json 快照產生器。
資料來源：台灣電力公司各區營業處「計畫性工作停電公告」官方頁面（service.taipower.com.tw）。
Phase 1 建置時快照；Phase 2 預計改為每日排程自動更新。
隻取今天起的公告，避免快照膨脹。
"""
import json, re, sys, urllib.request, datetime, os

BRANCHES = [
    ("台中區營業處", "https://service.taipower.com.tw/branch/d105/xcnotice?xsmsid=0M242581317628413301"),
    ("彰化區營業處", "https://service.taipower.com.tw/branch/d106/xcnotice?xsmsid=0M242581314418510444"),
    ("高雄區營業處", "https://service.taipower.com.tw/branch/d109/xcnotice?xsmsid=0M242581310382588530"),
    ("屏東區營業處", "https://service.taipower.com.tw/branch/d110/xcnotice?xsmsid=0M242581319136855888"),
    ("鳳山區營業處", "https://service.taipower.com.tw/branch/d119/xcnotice?xsmsid=0M242581312415567180"),
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

CODES = {"台中區營業處": "tc", "彰化區營業處": "ch", "高雄區營業處": "kh", "屏東區營業處": "pt", "鳳山區營業處": "fs"}

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
