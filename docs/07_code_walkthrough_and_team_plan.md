# 程式碼導覽與分工建議

最後更新：2026-05-22

本文件說明 Coffee Run Streamlit 版本目前每個程式檔案的用途，以及建議的團隊分工方式。若組員剛加入，建議先讀本文件，再讀 `docs/06_handoff_spec.md`。

## 1. 目前程式結構

```text
coffee_run_streamlit/
- app.py
- config.py
- state.py
- api_keys.py
- components.py
- filters.py
- formatters.py
- file_storage.py
- database.py
- google_maps.py
- seed_data.py
- pages/
  - auth.py
  - explore.py
  - social.py
  - profile.py
  - ranking.py
```

## 2. 檔案功能介紹

### 2.1 app.py

用途：整個 Streamlit app 的入口。

負責內容：

- 設定 Streamlit 頁面。
- 初始化 SQLite 資料庫。
- 初始化 session state。
- 判斷使用者是否登入。
- 根據側邊欄選單切換頁面。

不應放在這裡的內容：

- 不要放大量頁面 UI。
- 不要放 SQL。
- 不要放 Google API 細節。

適合負責人：

- 整合測試負責人。
- 專案整合負責人。

### 2.2 config.py

用途：集中放全專案共用設定。

目前內容：

- `UPLOAD_DIR`：上傳圖片儲存位置。
- `DEFAULT_TAGS`：發文時可選的預設標籤。
- `PAGE_OPTIONS`：側邊欄頁面順序。

適合負責人：

- 整合測試負責人。
- UI 負責人。

### 2.3 state.py

用途：管理 Streamlit session state。

目前內容：

- `user`：目前登入使用者。
- `selected_cafe_id`：目前選到的咖啡廳。
- `api_key_override`：側邊欄輸入的 Google API key。

為什麼需要這個檔案：

Streamlit 每次按按鈕都會重新執行程式，所以需要把跨頁狀態存在 `st.session_state`。

適合負責人：

- 功能邏輯負責人。
- 整合測試負責人。

### 2.4 api_keys.py

用途：統一取得目前要使用的 Google API key。

目前邏輯：

- 優先使用側邊欄手動輸入。
- 若沒有輸入，就交給 `google_maps.py` 從環境變數或本機 iOS 專案 plist 讀取。

適合負責人：

- Google API 功能負責人。

### 2.5 components.py

用途：共用 Streamlit UI 元件。

目前內容：

- `render_map()`：顯示地圖。
- `render_cafe_card()`：顯示咖啡廳卡片。
- `render_post_card()`：顯示社群貼文卡片。

這個檔案是 UI 和功能邏輯的交界。它會呼叫 `database.py`，但不應該直接寫 SQL。

適合負責人：

- UI 負責人。
- 社群功能負責人。
- 探索地圖功能負責人。

### 2.6 filters.py

用途：探索頁的篩選邏輯。

目前內容：

- `filtered_cafes()`：依照關鍵字、地區、最低評分、標籤篩選咖啡廳。

未來如果要加入「有插座」、「不限時」、「適合讀書」等精細條件，建議優先改這裡。

適合負責人：

- 探索地圖功能負責人。

### 2.7 formatters.py

用途：顯示格式工具。

目前內容：

- `format_distance()`：把距離轉成 `m` 或 `km`。
- `format_tags()`：把標籤轉成 Streamlit chip 顯示格式。

適合負責人：

- UI 負責人。

### 2.8 file_storage.py

用途：處理使用者上傳圖片。

目前內容：

- `save_uploaded_file()`：把 Streamlit 上傳檔案存到 `data/uploads/`。

注意：

- 目前是本機儲存。
- 若未來部署到雲端，可能要改成 Firebase Storage、S3 或 Cloudinary。

適合負責人：

- 社群功能負責人。
- 整合測試負責人。

### 2.9 database.py

用途：SQLite 資料庫層。

負責內容：

- 建立資料表。
- 舊資料庫 migration。
- 新增 / 查詢 / 更新使用者。
- 新增 / 查詢 / 更新咖啡廳。
- 收藏功能。
- 發文功能。
- 留言功能。
- 愛心功能。
- 個人頁統計。
- 足跡地圖資料。

協作規則：

- 只有資料庫組主要改這個檔案。
- UI 組和功能組需要新資料時，先討論需要什麼函式，再由資料庫組加。
- 頁面檔不要直接寫 SQL。

適合負責人：

- 資料庫負責人 1。
- 資料庫負責人 2。

### 2.10 google_maps.py

用途：Google Maps / Google Places API 串接。

目前內容：

- 取得 API key。
- 從 iOS 專案 plist 讀取 API key。
- 使用 Places Text Search 搜尋咖啡廳。
- 使用 Place Details 取得店家詳細資訊。
- 建立 Google Static Maps 圖片 URL。
- 建立 Google Maps 店家連結。
- 從地址推測地區。

適合負責人：

- Google API 功能負責人。

### 2.11 seed_data.py

用途：提供第一次啟動時的範例咖啡廳資料。

注意：

- 這不是正式資料來源。
- 正式資料應該從 Google Places 或使用者投稿補齊。

適合負責人：

- 資料庫負責人。
- Demo 資料負責人。

## 3. pages 資料夾

### 3.1 pages/auth.py

用途：登入頁與側邊欄。

目前內容：

- `render_login_page()`。
- `render_sidebar()`。

適合負責人：

- UI 負責人。
- 個人頁功能負責人。

### 3.2 pages/explore.py

用途：探索地圖頁。

目前內容：

- Google Places 搜尋匯入。
- 站內搜尋。
- 地區、評分、標籤篩選。
- 地圖。
- 搜尋結果咖啡廳卡片。
- 咖啡廳詳情。
- 詳情頁連結社群貼文。

適合負責人：

- 探索地圖功能負責人。
- Google API 功能負責人協作。

### 3.3 pages/social.py

用途：社群頁。

目前內容：

- 發文表單。
- 上傳圖片。
- 評分。
- 補充標籤。
- 最新貼文 feed。

適合負責人：

- 社群功能負責人。

### 3.4 pages/profile.py

用途：個人頁。

目前內容：

- 顯示頭貼、帳號、暱稱。
- 編輯個人資料。
- 貼文數、探店數、收藏數。
- 足跡地圖。
- 收藏清單。
- 我的貼文。

適合負責人：

- 個人頁功能負責人。

### 3.5 pages/ranking.py

用途：推薦排行頁。

目前內容：

- 依照使用者評分或 Google 評分排序咖啡廳。

適合負責人：

- 探索地圖功能負責人。
- UI 負責人。

## 4. 你提出的分工方式是否可行

你提出：

- 做 UI 介面：1 人。
- 做功能邏輯：3 人。
- 做資料庫：2 人。
- 做整合測試：1 人。

這樣總共 7 人。這個分法可以，但要注意一件事：如果 UI、功能邏輯、資料庫完全分開，容易發生「UI 等功能邏輯、功能邏輯等資料庫」的卡關狀況。

我建議改成：

```text
1 人 UI 系統與整體視覺
3 人功能頁 owner
2 人資料庫與資料模型
1 人整合測試與 Git 管理
```

也就是不要讓 UI 那個人負責所有頁面的每個細節，而是讓每個功能頁 owner 負責該頁能完整跑起來，UI 負責統一風格與共用元件。

## 5. 推薦分工

### 5.1 UI 系統與共用元件 1 人

負責檔案：

- `components.py`
- `formatters.py`
- `config.py`
- 各 `pages/*.py` 的排版 review

工作內容：

- 統一按鈕、卡片、標題、文字風格。
- 優化咖啡廳卡片。
- 優化貼文卡片。
- 優化個人頁排版。
- 確認手機或窄視窗不會太難看。

注意：

- 不要自己改資料庫 SQL。
- 如果需要新資料，請資料庫組新增函式。

### 5.2 功能邏輯 3 人

#### 功能邏輯 A：探索地圖與 Google Places

負責檔案：

- `pages/explore.py`
- `filters.py`
- `google_maps.py`

工作內容：

- Google 搜尋。
- 店家詳情同步。
- 地圖顯示。
- 精細篩選器。

#### 功能邏輯 B：社群

負責檔案：

- `pages/social.py`
- `components.py` 的 `render_post_card()`
- `file_storage.py`

工作內容：

- 發文。
- 圖片上傳。
- 留言。
- 愛心。
- 貼文收藏。
- 發文補充篩選資料。

#### 功能邏輯 C：個人頁與推薦

負責檔案：

- `pages/profile.py`
- `pages/ranking.py`
- `components.py` 的 `render_cafe_card()`

工作內容：

- 個人資料。
- 收藏清單。
- 足跡地圖。
- 我的貼文。
- 推薦排行。

### 5.3 資料庫 2 人

#### 資料庫 A：核心 schema 與 migration

負責檔案：

- `database.py`
- `seed_data.py`

工作內容：

- 維護資料表。
- 新增 migration。
- 確認舊資料庫不會壞。
- 管理 seed data。

#### 資料庫 B：功能查詢與統計

負責檔案：

- `database.py`

工作內容：

- 新增功能頁需要的查詢函式。
- 個人頁統計。
- 咖啡廳評分計算。
- 標籤統計。
- 未來 `cafe_traits` 精細篩選資料表。

### 5.4 整合測試與 Git 管理 1 人

負責檔案：

- `app.py`
- `README.md`
- `docs/`

工作內容：

- 管理 GitHub main branch。
- Review PR 是否能跑。
- 每次合併前啟動 Streamlit 測試。
- 維護 demo script。
- 寫測試清單。
- 確認組員沒有 commit API key 或資料庫暫存檔。

## 6. 更順的協作方式

最順的方式不是「同一個人負責一整頁的 UI + 邏輯 + 資料庫」，也不是「每層完全切開」。推薦用混合制：

```text
功能頁 owner 負責讓該功能完成
資料庫組負責資料表與 SQL
UI 組負責風格與共用元件
整合測試負責合併與驗收
```

例如社群功能：

- 社群 owner 改 `pages/social.py`。
- 如果需要新增貼文收藏資料表，請資料庫組改 `database.py`。
- 如果貼文卡片不好看，請 UI 組改 `components.py`。
- 完成後整合測試負責確認發文、留言、愛心、個人頁都沒壞。

這樣每個人都有主責，但不會互相卡死。

## 7. 修改規則

### 7.1 UI 組

可以改：

- `components.py`
- `formatters.py`
- `config.py`
- `pages/*.py` 的顯示文字與排版

不建議改：

- `database.py`
- SQL schema

### 7.2 功能組

可以改：

- 自己負責的 `pages/*.py`
- `filters.py`
- `google_maps.py`
- 必要時改 `components.py`

不建議直接改：

- unrelated page
- 資料庫 schema

### 7.3 資料庫組

可以改：

- `database.py`
- `seed_data.py`

要先討論再改：

- 刪除欄位。
- 改既有函式回傳格式。
- 清空資料庫。

### 7.4 整合測試

可以改：

- `app.py`
- `README.md`
- `docs/`
- 小型修正

主要職責：

- 合併前跑測試。
- 確認 main branch 可啟動。

## 8. 每次合併前必做

```bash
python3 -m py_compile app.py database.py google_maps.py seed_data.py config.py state.py formatters.py file_storage.py filters.py api_keys.py components.py pages/*.py
python3 -m streamlit run app.py
```

手動測試：

- 登入。
- 探索地圖。
- Google Places 搜尋。
- 收藏咖啡廳。
- 發文。
- 上傳圖片。
- 留言。
- 按愛心。
- 個人頁足跡。
- 收藏清單。
- 推薦排行。

