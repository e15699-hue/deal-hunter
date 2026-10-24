# 好康生活 howkang-life

好康網（howkang.com.tw）姊妹站。定位：「新聞不報、但你天天要查的生活大小事」。
目標網域：life.howkang.com.tw（子網域，零成本）。

## 現況（Phase 1，2026-10-24）
- 預覽：暫放好康網 repo（deal-hunter）的 `life/` 資料夾 → https://howkang.com.tw/life/
- 正式上線只差兩步（需使用者手動）：
  1. 在 GitHub 手動建立 repo `howkang-life`（Muse 的 GitHub App 無建 repo 權限，已實測 403），把本專案檔案搬過去、開啟 GitHub Pages。
  2. DNS（howkang.com.tw 在 Gandi 代管）加一筆：`CNAME  life  →  e15699-hue.github.io.`，並在新 repo 放 CNAME 檔（內容 `life.howkang.com.tw`）。

## 架構
- `build.py`：母版產生器，改頁面改這裡，執行 `python3 build.py` 產出全站靜態檔（相對路徑，根目錄與 /life/ 子路徑都能跑）。
- `tools/fetch_outages.py`：抓台電 5 個區營業處（台中/彰化/高雄/屏東/鳳山）計畫性停電公告，產出 `daily/outages.json`（完整版）與 `daily/outages/` 網站精簡快照（未來 14 天、每片 ≤55KB）。Phase 2 預計排程每日自動更新。
- 頻道：home 居家裝修（5 篇文章）、daily 民生查詢（停電查詢工具＋菜價/垃圾車入口頁）已上線；senior/health/study/ai/car 為籌備中頁面。

## 內容標準
- **所有文章與商品盡量要有圖片**（2026-10-24 使用者指示）：列表卡片與文章／商品內頁都要有圖，不要純文字呈現；新內容上線前先檢查有圖才算完成。
- 現況盤點（2026-10-24）：Phase 1 共 17 頁 HTML、`<img>` 0 張，5 篇居家裝修文章皆無圖，待補圖。

## 資料來源
- 停電：台灣電力公司各區營業處計畫性工作停電公告（service.taipower.com.tw）
- 菜價：農業部農糧署農產品批發市場交易行情（data.moa.gov.tw 建置期間連線不穩，自動串接改每日快照方式開發中）
- 垃圾車：各縣市環保局官方查詢系統（入口整理頁）
