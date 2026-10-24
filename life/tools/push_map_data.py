#!/usr/bin/env python3
"""國家資訊地圖資料推送（排程用）：只推 map/*.json＋daily/outages*（資料快照），不動頁面。
比照推送鐵律：原始 UTF-8、小批次、遇寫入鎖等 60 秒重試一次、raw md5 驗證。
排程若因核准卡導致推送失敗，快照仍留在本機，下一次全站推送會一併帶上。
"""
import json, subprocess, sys, os, glob, hashlib, urllib.request, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_MAX = 58000

def main():
    files = sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "map", "**", "*.json"), recursive=True))
    files += sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, "daily", "outages", "*.json")))
    files.append("daily/outages.json")
    contents = {}
    for rel in files:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            contents[rel] = open(p, encoding="utf-8").read()
    files = list(contents)
    print("data files:", len(files))
    batches, cur, size = [], [], 0
    for rel in files:
        b = len(contents[rel].encode("utf-8"))
        if cur and size + b > BATCH_MAX:
            batches.append(cur); cur, size = [], 0
        cur.append(rel); size += b
    if cur:
        batches.append(cur)
    for b in batches:
        args = {"owner": "e15699-hue", "repo": "deal-hunter", "branch": "main",
                "message": "好康生活：國家資訊地圖資料快照更新（排程）",
                "files": [{"path": f"life/{p}", "content": contents[p]} for p in b]}
        for attempt in (1, 2):
            r = subprocess.run(["/opt/hatch/bin/github", "call-tool", "--name", "push_files",
                                "--arguments-json", json.dumps(args, ensure_ascii=False)],
                               capture_output=True, text=True, timeout=1500)
            out = (r.stdout or "") + (r.stderr or "")
            if '"isError":true' in out:
                print("batch FAILED", b, out[-400:]); return 1
            if "equivalent connector write is already running" in out and attempt == 1:
                print("寫入鎖，等 60 秒重試"); time.sleep(60); continue
            break
        time.sleep(3)
    ok = 0
    for rel in files:
        local = hashlib.md5(contents[rel].encode("utf-8")).hexdigest()
        for _ in range(3):
            try:
                req = urllib.request.Request(
                    f"https://raw.githubusercontent.com/e15699-hue/deal-hunter/main/life/{rel}",
                    headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    if hashlib.md5(resp.read()).hexdigest() == local:
                        ok += 1; break
            except Exception:
                pass
            time.sleep(20)
        else:
            print("MISMATCH", rel)
    print(f"md5 驗證 {ok}/{len(files)}")
    return 0 if ok == len(files) else 2

if __name__ == "__main__":
    sys.exit(main())
