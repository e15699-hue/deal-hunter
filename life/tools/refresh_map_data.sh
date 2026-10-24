#!/bin/bash
# 國家資訊地圖資料排程：抓取官方快照（不走 AI、不花 token）→ 推送資料檔到預覽站。
# 由 cron 每日呼叫；單次執行約需 5-10 分鐘（含 Nominatim 地理編碼節流）。
set -e
cd "$(dirname "$0")/.."
python3 tools/fetch_outages.py
python3 tools/fetch_water.py
python3 tools/fetch_trails.py
# 幾何框架：從新公告萃取路段名寫回 districts.roads（快取幾何另以 --precompute 分批補，不在每日排程內全量跑）
python3 tools/build_map_geo.py
python3 tools/push_map_data.py
echo "refresh done: $(date '+%Y-%m-%d %H:%M')"
