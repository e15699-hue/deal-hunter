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
- `tools/fetch_outages.py`：抓台電全台 20 個區營業處計畫性停電公告，產出 `daily/outages.json`（完整版）、`daily/outages/` 網站精簡快照（未來 14 天、每片 ≤55KB）與 `map/outages_{north,central,south,east}.json`（地圖用鄉鎮市區彙總，依縣市分 4 片以符合推送單檔上限，地圖頁合併讀取）。
- 🗺️ **國家資訊地圖**（2026-10-24 使用者指示，點子 #37 整併）：母版 `map_template.html`（獨立頁，不依賴整站框架，App WebView 可直接套用 `map.html`；網址參數 `?layers=trails,outages,water` 預選圖層、`?q=` 預帶搜尋），`build.py` 的 page_map() 負責產出。圖層資料統一格式（類別、名稱、地點、狀態、來源、更新時間），未來新政府公告照同格式新增圖層即可。
  - 圖層與腳本：🏔️ 步道 `tools/fetch_trails.py`（山林悠遊網步道頁即時狀態＋Nominatim 座標快取；目錄 `tools/trail_catalog.json`）；💡 停電 `tools/fetch_outages.py`（見上）；💧 停水 `tools/fetch_water.py`（台水停水公告 API，範圍多邊形取中心點＋簡化外框）。
  - 座標一律來自官方範圍或 OSM 回傳，不手寫；狀態抓不到時標「查無最新公告」，不編造。
  - 排程：`tools/refresh_map_data.sh`（三支抓取腳本＋資料推送 `tools/push_map_data.py`），cron 每日 06:00 執行，不走 AI、不花 token。停電 6 小時更新曾評估，因推送批數多、核准卡負擔重，改為每日一次（已在報告註明）。
  - 地圖頁為工具頁、載入輕量優先，push_preview 的缺圖 assert 對 map.html 豁免（其餘內容頁維持）。
- 頻道：home 居家裝修（5 篇文章）、daily 民生查詢（停電查詢工具＋菜價/垃圾車入口頁）、kids 親子學習（2026-10-24 新增，點子 #35 兒童線上英文整理：頻道頁＋4 篇）、pets 寵物照護（2026-10-24 新增，點子 #39：頻道頁＋4 篇，只寫科普＋就醫提醒、不診斷）已上線；senior/health/study/ai/car 為籌備中頁面。寵物圖例外：本輪未找到合適台灣場景寵物實圖，暫用中性寵物實圖並標出處，日後找到台灣圖再換。
- 圖片注意：推送工具（push_files）僅支援 UTF-8 文字檔，`img/*.jpg` 二進位圖檔進不了 repo，正式站舊圖目前為 404；新圖改在 `img/credits.json` 加 `remote` 欄位直連 Wikimedia Commons 原圖（build.py 的 fig/thumb 會自動選用），並保留本機副本於 img/。

## 內容標準
- **所有文章與商品盡量要有圖片**（2026-10-24 使用者指示）：列表卡片與文章／商品內頁都要有圖，不要純文字呈現；新內容上線前先檢查有圖才算完成。
- 圖片來源（2026-10-24 使用者拍板）：文章用免費圖庫實圖（Wikimedia Commons 創用授權，逐張標作者／授權，見 `img/credits.json`、`img/CREDITS.md`）；商品日後一律用官方／賣場實圖。
- 圖片取材順序（2026-10-24 使用者補充）：優先用台灣場景／台灣相關的真實圖片；找不到台灣相關圖時最不得已才自己產出圖片，且絕對不得假冒政府網站畫面。2026-10-24 13:58 起全站改用台灣場景圖（居家裝修 5 篇＋民生＋其他頻道共 13 張換圖；系統櫃因 4 輪搜尋無合適台灣圖，暫留中性櫃體特寫並記於 build.py 例外紀錄）。
- 風格標準（2026-10-24 使用者糾正「風格太老舊，要時尚現代」）：台灣場景還要現代時尚、吸引人——同日第二輪換圖 13 張（信義 Apple 室內、南門市場新大樓、台北夜景 101、COMPUTEX 2024、特斯拉充電站等），淘汰眷舍／老市場／廟宇等老舊感照片；系統櫃與合約因台灣候選皆不合（餐廳廚房／老舊辦公室），暫留現代感的中性特寫，記於 build.py 例外紀錄。
- 執行狀態（2026-10-24）：Phase 1 原 17 頁 0 圖已補齊——build.py 以 fig()/thumb() 注入主圖與縮圖，全站每頁 ≥1 圖；圖片本地化存 `img/`（二進位檔需經 GitHub 網頁上傳，push_preview.py 只推文字檔）。push_preview 已加缺圖 assert 閘門，無圖的頁面推不上線。

## 資料來源
- 停電：台灣電力公司各區營業處計畫性工作停電公告（service.taipower.com.tw，全台 20 區處）
- 停水：台灣自來水公司停水公告查詢系統官方 API（web.water.gov.tw/wateroffapi）
- 步道：林業及自然保育署台灣山林悠遊網步道頁即時狀態（recreation.forest.gov.tw）
- 菜價：農業部農糧署農產品批發市場交易行情（data.moa.gov.tw 建置期間連線不穩，自動串接改每日快照方式開發中）
- 垃圾車：各縣市環保局官方查詢系統（入口整理頁）
- 兒童線上英文（kids 頻道）：各平台官網與公開資料整理（OiKID、TutorABC、Native Camp、51Talk、Etalking、WUWOW），2026-10-24 查閱；未公開的價格/退費一律標「需洽詢」，不引用來路不明數字充當官方資訊
