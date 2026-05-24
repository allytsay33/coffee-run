# Coffee Run 交接文件

最後更新：2026-05-24

資料庫已於 2026-05-24 改為支援 Supabase PostgreSQL。Supabase 啟用與最新 schema 請優先閱讀 `docs/10_current_database_schema.md` 與 `docs/12_supabase_setup.md`；本文較後段若仍提及 SQLite，代表先前本機 demo 階段的背景說明。

本文件是 Coffee Run Streamlit 版本的完整交接說明，目標是讓任何組員即使沒有參與前期討論，也能理解產品要做什麼、目前做到哪裡、接下來要怎麼分工、怎麼用 Git 協作，以及 demo 前要如何驗收。

## 1. 專案定位

Coffee Run 是一個以咖啡廳探索與社群分享為核心的應用。使用者可以透過地圖找到附近或指定區域的咖啡廳，依照讀書、聊天、插座、不限時、甜點、價格、營業時間等條件篩選店家，也可以針對去過的咖啡廳發文、上傳圖片、留下評分與細節資訊。

目前這份專案是 Python / Streamlit 版本，主要目標是期末專案展示。它不是原本 iOS 專案本體，而是獨立的網頁展示版。

### 1.1 核心價值

- 幫助學生快速找到適合需求的咖啡廳。
- 將 Google Maps 真實店家資料與使用者社群內容結合。
- 讓篩選資料可以隨著使用者發文逐步變得更完整。
- 讓使用者能保存想去的店、看自己的探店紀錄、回顧足跡地圖。

### 1.2 目前技術選型

- 前端與後端介面：Streamlit
- 語言：Python
- 資料庫：Supabase PostgreSQL；未設定連線字串時以 SQLite 作本機 fallback
- 地圖與店家來源：Google Maps / Google Places API
- 圖片上傳：本機檔案儲存於 `data/uploads/`
- 本機 fallback 資料庫：`data/coffee_run.db`

### 1.3 啟動方式

在終端機執行：

```bash
cd /Users/weishan33/Desktop/coffee_run_streamlit
python3 -m streamlit run app.py
```

啟動後打開：

```text
http://localhost:8501
```

## 2. 目前實作狀態

### 2.1 已完成

- 簡易登入：輸入帳號名即可登入。
- 探索地圖頁：
  - 站內關鍵字搜尋。
  - 地區篩選。
  - 最低評分篩選。
  - 標籤篩選。
  - 顯示地圖。
  - 顯示咖啡廳列表。
  - 收藏 / 取消收藏咖啡廳。
  - 點開咖啡廳詳情。
- Google API 串接：
  - 可讀取 iOS 專案 `GoogleService-Info.plist` 裡的 API key。
  - 可用 Google Places Text Search 搜尋咖啡廳。
  - 可用 Place Details 同步店家細節。
  - 可用 Static Maps 顯示地圖圖片。
- 社群頁：
  - 垂直下滑式貼文頁。
  - 發文需連結特定咖啡廳。
  - 發文可上傳圖片、文字、評分、補充標籤。
  - 貼文會顯示咖啡廳名稱、帳號名、圖片、內文、評分、留言數、愛心數。
  - 可按愛心。
  - 可留言。
- 個人頁：
  - 顯示帳號名、暱稱、頭貼。
  - 可編輯暱稱與頭貼。
  - 顯示貼文數、探店數、收藏數。
  - 顯示足跡地圖。
  - 顯示收藏清單。
  - 顯示我的貼文。
- 推薦排行：
  - 依照使用者評分或 Google 評分排序。
- 資料永久保存：
  - 使用者、咖啡廳、收藏、貼文、留言、愛心、標籤都存在 Supabase PostgreSQL；離線開發時可暫存在 SQLite。

### 2.2 尚未完成或仍可強化

- 真正完整的互動式 Google Map：目前主要是 Static Map 或 Streamlit 內建地圖，不是完整可點 marker 的 Google Map 前端。
- 初始資料爬蟲：目前初版資料來自 `seed_data.py` 與 Google Places 搜尋，不是自動爬蟲批次匯入。
- 更精細的篩選欄位：目前標籤是文字型，尚未拆成插座數量、是否不限時、平均價格、座位數、噪音程度等結構化欄位。
- 貼文本身收藏：目前收藏的是咖啡廳，不是單篇貼文。
- 真實使用者驗證：目前是課堂展示用簡易登入，沒有密碼、OAuth 或 Firebase Auth。
- 權限管理：目前沒有刪文、改文、管理員審核。
- 部署：目前是本機啟動，尚未部署到雲端。

## 3. 產品功能需求

以下需求分成三大模組：探索地圖、社群、個人頁。

## 3.1 探索地圖

探索地圖是 Coffee Run 的主功能。使用者進入後應能搜尋真實咖啡廳，透過多條件篩選找到適合自己的店，並查看店家詳情與相關社群貼文。

### 3.1.1 Google Maps / Google Places API 串接

需求：

- 系統應串接 Google Maps Platform。
- 使用者可以用關鍵字搜尋咖啡廳，例如：
  - `咖啡廳`
  - `台大附近咖啡廳`
  - `不限時咖啡廳`
  - `大安區咖啡廳`
- 系統應從 Google Places 取得真實店家資料：
  - Google Place ID
  - 店名
  - 地址
  - 經緯度
  - Google 評分
  - Google Maps 連結
  - 營業時間
  - 官方網站

目前做法：

- `google_maps.py` 負責 API 串接。
- `search_cafes()` 使用 Places Text Search。
- `fetch_place_details()` 使用 Place Details。
- `static_map_url()` 使用 Static Maps。
- API key 讀取順序：
  - 側邊欄手動輸入。
  - `GOOGLE_MAPS_API_KEY` 環境變數。
  - iOS 專案的 `GoogleService-Info.plist`。

建議下一步：

- 新增搜尋地點欄位，例如 `台北市大安區`、`台大`、`公館`。
- 新增半徑設定，例如 500m、1km、3km、5km。
- 將 Google Places 查到的資料自動寫入共用資料庫，避免每次重複打 API。
- 增加錯誤處理提示：
  - Billing 未啟用。
  - API 未啟用。
  - key 權限限制錯誤。
  - 查無結果。
  - 網路錯誤。

### 3.1.2 初始咖啡廳資料來源

需求：

- 初始版本可以先透過爬蟲或 Google Places 搜尋建立咖啡廳資料。
- 後續使用者每次發文時，都會為特定咖啡廳提供評分、標籤和文字描述。
- 系統應把使用者補充的資料回寫到咖啡廳資料來源，讓篩選越來越準。

目前做法：

- 初始資料在 `seed_data.py`。
- Google Places 搜尋結果可加入 `cafes` 資料表。
- 使用者發文後：
  - `refresh_cafe_user_rating()` 更新咖啡廳使用者平均評分。
  - `refresh_cafe_tags()` 將貼文標籤合併到咖啡廳標籤。

建議做法：

- 短期：繼續用 Google Places 搜尋當初版資料來源。
- 中期：建立批次匯入腳本，例如 `scripts/import_google_places.py`。
- 長期：若真的要爬蟲，必須注意網站服務條款與資料合法性。優先使用 Google Places API，因為它是正式資料來源。

建議資料欄位：

- `has_outlets`: 是否有插座。
- `has_wifi`: 是否有 Wi-Fi。
- `time_limit`: 是否限時。
- `quiet_level`: 安靜程度，1 到 5。
- `study_friendly`: 是否適合讀書。
- `chat_friendly`: 是否適合聊天。
- `price_level`: 價格等級，1 到 5。
- `dessert_quality`: 甜點評分，1 到 5。
- `coffee_quality`: 咖啡評分，1 到 5。
- `seat_count_level`: 座位多寡，1 到 5。
- `open_late`: 是否晚上營業。

### 3.1.3 精細篩選器

需求：

- 使用者應可依照多種條件篩選咖啡廳。
- 篩選結果應即時反映在列表與地圖上。
- 篩選資料來源包含：
  - Google 原始資料。
  - 初始匯入資料。
  - 使用者貼文補充資料。

目前已支援：

- 關鍵字。
- 地區。
- 最低評分。
- 標籤。

建議增加：

- 是否不限時。
- 是否有插座。
- 是否適合讀書。
- 是否適合聊天。
- 是否有甜點。
- 是否平價。
- 是否晚上營業。
- Google 評分篩選。
- 使用者評分篩選。
- 距離篩選。
- 營業中篩選。

實作建議：

- 不要只靠單一 `tags` 字串做所有事情。
- 可以保留 `tags` 作為彈性標籤，但重要篩選條件應拆成資料表欄位或統計表。
- 建議新增 `cafe_traits` 表，專門保存由使用者回饋累積出的結構化特徵。

建議 `cafe_traits` 欄位：

```text
cafe_id
outlet_votes_yes
outlet_votes_no
wifi_votes_yes
wifi_votes_no
time_limit_votes_yes
time_limit_votes_no
quiet_score_total
quiet_score_count
study_score_total
study_score_count
chat_score_total
chat_score_count
price_score_total
price_score_count
updated_at
```

這樣可以讓多位使用者的回饋被平均或投票統計，而不是後發文的人覆蓋前面的人。

### 3.1.4 咖啡廳詳情頁

需求：

點開咖啡廳後，應顯示完整資訊：

- 店名。
- 地址。
- 地圖位置。
- 營業時間。
- Google Maps 連結。
- 官方網站。
- Google 評分。
- 使用者平均評分。
- 標籤。
- 適合情境。
- 該咖啡廳所有社群貼文。

目前已支援：

- 店名。
- 地址。
- 營業時間。
- 官方網站。
- Google Maps 連結。
- Google 評分。
- 使用者評分。
- 標籤。
- 連結此咖啡廳的社群貼文。

建議增加：

- 店家圖片。
- 最多人提到的標籤。
- 使用者評分分布。
- 最近貼文。
- 一鍵發文到此咖啡廳。
- 一鍵收藏。

### 3.1.5 儲存功能

需求：

- 每間咖啡廳列表旁需有儲存按鈕。
- 儲存後應出現在個人頁收藏清單。
- 使用者可以取消收藏。

目前已完成：

- `favorites` 資料表。
- `add_favorite()`。
- `remove_favorite()`。
- `list_favorite_cafes()`。
- 探索列表與個人頁都可收藏 / 取消收藏。

建議強化：

- 收藏按鈕改成更明確的圖示或文案。
- 收藏清單可依收藏時間、評分、地區排序。
- 可以新增收藏備註，例如「想讀書」、「下次約朋友」。

## 3.2 社群

社群模組的重點是讓使用者分享探店經驗，並把社群內容反向補充到探索篩選資料。

### 3.2.1 下滑式貼文頁

需求：

- 社群頁應是可往下滑的貼文 feed。
- 預設顯示最新貼文。
- 每篇貼文是一張清楚的內容卡片。

目前已完成：

- `render_social_page()` 顯示最新貼文。
- Streamlit 頁面可自然往下滑。

建議強化：

- 增加篩選：
  - 最新。
  - 最多人按讚。
  - 最高評分。
  - 我的追蹤或我的地區。
- 增加分頁或載入更多，避免貼文變多後頁面太慢。

### 3.2.2 貼文顯示內容

需求：

每篇貼文應顯示：

- 咖啡廳名稱。
- 帳號名。
- 使用者頭貼。
- 圖片。
- 內文。
- 留言。
- 按愛心。
- 評分。
- 收藏。

目前已完成：

- 咖啡廳名稱。
- 帳號名。
- 圖片。
- 內文。
- 留言。
- 按愛心。
- 評分。
- 愛心數。
- 留言數。

目前未完成：

- 貼文收藏。
- 貼文卡片上顯示使用者頭貼。

建議做法：

- 若需求中的「收藏」是收藏咖啡廳，則目前已完成。
- 若需求中的「收藏」是收藏貼文，建議新增 `post_favorites` 資料表。

建議資料表：

```text
post_favorites
- user_id
- post_id
- created_at
PRIMARY KEY (user_id, post_id)
```

### 3.2.3 發文功能

需求：

- 發文一定要連結特定咖啡廳。
- 可上傳圖片。
- 可輸入文字。
- 可給評分。
- 可補充細節資訊，作為篩選資料來源。

目前已完成：

- `render_post_form()`。
- 發文表單必選咖啡廳。
- 可上傳圖片。
- 可填內文。
- 可評分。
- 可補充標籤。
- 發文後會更新咖啡廳使用者評分與標籤。

建議強化：

- 發文時增加結構化欄位：
  - 有插座。
  - 有 Wi-Fi。
  - 是否不限時。
  - 安靜程度。
  - 適合讀書程度。
  - 適合聊天程度。
  - 價格程度。
  - 甜點評分。
- 發文前檢查：
  - 是否選擇咖啡廳。
  - 是否輸入內文。
  - 圖片格式是否正確。
  - 評分是否在合理範圍。
- 發文後可以跳到該貼文或該咖啡廳詳情。

## 3.3 個人頁

個人頁應呈現使用者身份、統計數據、收藏與足跡。

### 3.3.1 帳號資料

需求：

- 顯示帳號名。
- 顯示頭貼。
- 顯示暱稱。

目前已完成：

- 使用者資料存在 `users`。
- 可顯示 `username`。
- 可顯示與修改 `display_name`。
- 可上傳與顯示 `avatar_path`。

建議強化：

- 預設頭貼。
- 個人簡介。
- 社群帳號連結。
- 編輯成功提示更明確。

### 3.3.2 統計資料

需求：

- 貼文數。
- 探店數。

目前已完成：

- `post_count`。
- `footprint_count`，使用已發文的不重複咖啡廳數計算。
- 額外也顯示收藏數。

建議強化：

- 平均評分。
- 最常去的地區。
- 最常使用的標籤。
- 本月探店數。

### 3.3.3 足跡地圖

需求：

- 顯示使用者已發過文的咖啡廳。
- 每個發文過的咖啡廳都應出現在地圖上。

目前已完成：

- `list_footprint_cafes()` 取得使用者發文過的咖啡廳。
- `render_map()` 顯示地圖。

建議強化：

- 足跡地圖 marker 可點。
- 顯示每間店的發文數。
- 依月份或地區篩選足跡。

## 4. 資料庫設計

目前核心資料表：

- `users`：使用者。
- `cafes`：咖啡廳。
- `favorites`：使用者收藏的咖啡廳。
- `reviews`：舊版咖啡筆記，目前主要功能已轉向 posts。
- `posts`：社群貼文。
- `post_tags`：貼文標籤。
- `comments`：留言。
- `likes`：貼文愛心。

### 4.1 users

用途：保存使用者基本資料。

重要欄位：

- `user_id`
- `username`
- `display_name`
- `avatar_path`
- `created_at`

### 4.2 cafes

用途：保存咖啡廳資料，來源可能是 seed、Google Places 或手動建立。

重要欄位：

- `cafe_id`
- `google_place_id`
- `name`
- `area`
- `address`
- `distance_meters`
- `lat`
- `lng`
- `rating`
- `user_rating`
- `tags`
- `description`
- `opening_hours`
- `website`
- `maps_url`
- `source`

### 4.3 posts

用途：保存社群貼文。

重要欄位：

- `post_id`
- `user_id`
- `cafe_id`
- `content`
- `rating`
- `image_path`
- `created_at`

### 4.4 建議新增資料表

若要完整滿足細緻篩選需求，建議新增：

```text
cafe_traits
post_favorites
post_trait_feedback
```

`post_trait_feedback` 可記錄單篇貼文對該咖啡廳的細節回饋：

```text
post_trait_feedback
- post_id
- cafe_id
- user_id
- has_outlets
- has_wifi
- no_time_limit
- quiet_score
- study_score
- chat_score
- price_score
- dessert_score
- coffee_score
- created_at
```

接著用統計函式把這些資料彙整回 `cafe_traits`，供探索頁篩選。

## 5. 建議實作順序

建議用四個階段完成，不要全部同時做。

### 階段 1：穩定現有功能

目標：確保 demo 可以順利跑。

任務：

- 確認 Streamlit 可啟動。
- 確認 Google Places 搜尋可用。
- 確認發文、上傳圖片、留言、按讚正常。
- 確認收藏會出現在個人頁。
- 確認足跡地圖會更新。

驗收標準：

- 使用新帳號登入後，可以完成一輪完整流程：
  - 搜尋咖啡廳。
  - 收藏咖啡廳。
  - 發文。
  - 留言。
  - 按愛心。
  - 到個人頁看到收藏、貼文、足跡。

### 階段 2：補齊精細篩選

目標：讓探索地圖符合產品需求。

任務：

- 設計 `cafe_traits` 與 `post_trait_feedback`。
- 發文表單增加細節欄位。
- 探索頁增加細節篩選器。
- 使用者發文後更新咖啡廳統計資料。

驗收標準：

- 使用者發文選擇「有插座」後，該咖啡廳可以被「有插座」篩選找到。
- 多位使用者回饋同一間店時，系統不會覆蓋資料，而是做統計。

### 階段 3：強化社群與個人頁

目標：讓社群感更完整。

任務：

- 貼文卡片顯示頭貼。
- 新增貼文收藏。
- 個人頁增加收藏貼文區。
- 個人頁增加更多統計。
- 足跡地圖增加列表與排序。

驗收標準：

- 使用者可以收藏貼文。
- 個人頁可以看到自己收藏的咖啡廳與貼文。
- 貼文列表看起來像完整社群 feed。

### 階段 4：整理展示與文件

目標：期末 demo 能清楚說明價值與技術。

任務：

- 更新 README。
- 更新 demo script。
- 補截圖。
- 整理任務看板。
- 準備講稿。

驗收標準：

- 任一組員照 README 可以啟動。
- 任一組員照 demo script 可以展示完整流程。

## 6. 建議分工模式

建議 6 人分工。每個人有清楚負責範圍，避免互相改同一段程式。

### 6.1 組員 A：專案整合與 PM

負責：

- 管理需求清單。
- 維護 README 與交接文件。
- 安排 demo 流程。
- Review 每個 pull request。
- 確保 main branch 隨時可啟動。

主要檔案：

- `README.md`
- `docs/`
- `app.py` 最外層頁面整合

產出：

- 最新交接文件。
- Demo script。
- 最終簡報功能說明。

### 6.2 組員 B：Google Maps / Places

負責：

- Google Places 搜尋。
- Google Place Details。
- Google Static Maps 或地圖顯示。
- API key 設定與錯誤處理。

主要檔案：

- `google_maps.py`
- `app.py` 的 `render_map()`
- `app.py` 的 `render_explore_page()` Google 搜尋區塊

產出：

- Google 搜尋可穩定匯入咖啡廳。
- 地圖可正常顯示。
- API 失敗時有清楚錯誤訊息。

### 6.3 組員 C：資料庫與資料模型

負責：

- Supabase PostgreSQL schema。
- 資料表 migration。
- 咖啡廳、貼文、收藏、留言、愛心資料函式。
- 新增 `cafe_traits`、`post_trait_feedback` 等表。

主要檔案：

- `database.py`
- `seed_data.py`
- `data/coffee_run.db` 不直接手改，只透過程式建立

產出：

- 穩定的資料庫初始化。
- 舊資料不會因 schema 更新壞掉。
- 清楚的查詢函式。

### 6.4 組員 D：探索地圖與篩選

負責：

- 探索頁 UI。
- 搜尋與篩選邏輯。
- 咖啡廳卡片。
- 咖啡廳詳情頁。

主要檔案：

- `app.py` 的 `filtered_cafes()`
- `app.py` 的 `render_explore_page()`
- `app.py` 的 `render_cafe_card()`
- `app.py` 的 `render_cafe_detail()`

產出：

- 精細篩選器。
- 清楚的搜尋結果列表。
- 完整咖啡廳詳情。

### 6.5 組員 E：社群功能

負責：

- 發文表單。
- 貼文卡片。
- 圖片上傳。
- 留言。
- 愛心。
- 貼文收藏。

主要檔案：

- `app.py` 的 `render_social_page()`
- `app.py` 的 `render_post_form()`
- `app.py` 的 `render_post_card()`
- `database.py` 的 posts、comments、likes 相關函式

產出：

- 可用的社群 feed。
- 發文資料能反向補充探索篩選。
- 貼文互動功能完整。

### 6.6 組員 F：個人頁、測試與 Demo

負責：

- 個人頁。
- 收藏清單。
- 足跡地圖。
- 使用者統計。
- 手動測試。
- Demo 截圖與影片。

主要檔案：

- `app.py` 的 `render_profile_page()`
- `database.py` 的 user stats、favorites、footprints 相關函式
- `docs/04_demo_script.md`
- `docs/05_task_board.md`

產出：

- 個人頁完整。
- 每次 demo 前的測試紀錄。
- 展示腳本。

## 7. Git 版本控制方式

目前資料夾還不是 Git repo。建議先初始化 Git，或把這份專案放到 GitHub repository。

### 7.1 第一次建立 repo

在專案根目錄：

```bash
cd /Users/weishan33/Desktop/coffee_run_streamlit
git init
git add .
git commit -m "chore: initial streamlit project"
```

如果要連到 GitHub：

```bash
git remote add origin <GitHub repo URL>
git branch -M main
git push -u origin main
```

### 7.2 Branch 規則

`main` 只放可以啟動、可以 demo 的版本。

每個功能開自己的 branch：

```text
feature/google-places
feature/explore-filters
feature/social-posts
feature/profile-page
feature/database-traits
docs/handoff-and-demo
fix/google-api-errors
```

### 7.3 開發流程

每個人開始前：

```bash
git checkout main
git pull
git checkout -b feature/your-task
```

完成後：

```bash
git status
git add <changed files>
git commit -m "feat: add detailed cafe filters"
git push -u origin feature/your-task
```

接著開 Pull Request，請至少一位組員看過再合併。

### 7.4 Commit message 規則

建議格式：

```text
feat: add Google Places search
fix: handle missing Google API key
docs: update demo script
data: add seed cafes
refactor: split cafe filtering logic
test: add manual test checklist
```

常用類型：

- `feat`: 新功能。
- `fix`: 修 bug。
- `docs`: 文件。
- `data`: 種子資料或範例資料。
- `refactor`: 不改行為的整理。
- `test`: 測試。
- `chore`: 設定、工具、雜項。

### 7.5 合併前檢查

每個 PR 合併前至少做：

```bash
python3 -m py_compile app.py database.py google_maps.py seed_data.py
python3 -m streamlit run app.py
```

手動測試：

- 可以登入。
- 探索頁可以開。
- 咖啡廳列表有資料。
- Google 搜尋可用或錯誤訊息清楚。
- 收藏可新增與取消。
- 發文可成功。
- 圖片可顯示。
- 留言可新增。
- 愛心可切換。
- 個人頁統計正確。
- 足跡地圖有資料。

### 7.6 避免衝突規則

- 不要多人同時大改 `app.py` 同一段函式。
- 每個人只改自己負責的函式。
- 若要修改資料表，先通知資料庫負責人。
- 不要直接刪除 `data/coffee_run.db`，除非整組同意要重建資料。
- 不要把真實 API key 寫死在文件或公開 GitHub。
- 不要提交大型圖片、影片或不必要的暫存檔。

### 7.7 建議 `.gitignore`

建議加入：

```text
__pycache__/
*.pyc
.DS_Store
data/uploads/
*.db-journal
.env
```

是否忽略 `data/coffee_run.db` 要看課堂需求：

- 如果老師要一開就有 demo 資料，可以保留資料庫。
- 如果希望資料庫由程式自動建立，就忽略 `.db`，只保留 `seed_data.py`。

## 8. Google API 設定交接

### 8.1 目前狀態

目前程式已能從原 iOS 專案讀取 Google API key：

```text
/Users/weishan33/Desktop/Coffee_Run!!/Coffee_Run!!/GoogleService-Info.plist
```

對應 project：

```text
coffeerun-d2646
```

目前測試結果：

- Google Places Text Search 可回傳 `OK`。
- Static Maps 可回傳地圖圖片。

### 8.2 必須啟用的服務

Google Cloud Console 內需確認：

- Billing 已啟用。
- Places API 已啟用。
- Maps Static API 已啟用。
- 若未來使用更多地圖功能，可能還需要 Maps JavaScript API。

### 8.3 常見錯誤

`REQUEST_DENIED` 且訊息提到 Billing：

- 代表 key 存在，但 project 沒有啟用 Billing，或 Billing 尚未生效。

`REQUEST_DENIED` 且訊息提到 API not enabled：

- 代表該 project 沒有啟用對應 API。

`REQUEST_DENIED` 且訊息提到 referer / IP / bundle：

- 代表 API key 有使用限制。
- iOS app key 可能只允許 iOS bundle 使用，Streamlit 後端會被擋。
- 解法是新增一支給本機 / server 使用的 key。

### 8.4 安全提醒

- 不要把 API key 明文寫進公開文件。
- 不要把 `.env` 推到 GitHub。
- 若 repository 會公開，建議改用環境變數：

```bash
export GOOGLE_MAPS_API_KEY="你的 key"
python3 -m streamlit run app.py
```

## 9. Demo 建議流程

### 9.1 展示順序

1. 啟動網站。
2. 用帳號名登入。
3. 到探索地圖。
4. 使用 Google Places 搜尋咖啡廳。
5. 匯入搜尋結果。
6. 使用篩選器找店。
7. 點開咖啡廳詳情。
8. 收藏咖啡廳。
9. 到社群頁發文。
10. 上傳圖片、填文字、給評分、補標籤。
11. 對貼文按愛心與留言。
12. 回到咖啡廳詳情，看該店貼文。
13. 到個人頁，看貼文數、探店數、收藏清單、足跡地圖。

### 9.2 講解重點

- Google Places 提供真實咖啡廳資料。
- 使用者發文會補充店家標籤與評分。
- 探索篩選不是固定死資料，而是會隨社群內容成長。
- 收藏與足跡讓使用者有個人化紀錄。
- Supabase PostgreSQL 讓不同裝置與重新整理後資料仍然保存。

### 9.3 Demo 前檢查

- API key 是否可用。
- 網路是否正常。
- Streamlit 是否可啟動。
- 是否已有可展示的咖啡廳資料。
- 是否有至少一篇含圖片貼文。
- 個人頁是否有收藏與足跡。
- 瀏覽器縮放比例是否適合投影。

## 10. 驗收標準

### 10.1 探索地圖驗收

- 使用者可以搜尋真實咖啡廳。
- 使用者可以看到地圖。
- 使用者可以用關鍵字、地區、評分、標籤篩選。
- 使用者可以打開咖啡廳詳情。
- 詳情頁可看到地址、營業時間、連結與社群貼文。
- 使用者可以收藏咖啡廳。
- 收藏會出現在個人頁。

### 10.2 社群驗收

- 使用者可以看到垂直貼文 feed。
- 貼文顯示咖啡廳、帳號、圖片、內文、留言、愛心、評分。
- 使用者可以發文。
- 發文必須連結咖啡廳。
- 發文可上傳圖片、文字、評分。
- 發文後資料會保存。
- 發文後咖啡廳使用者評分會更新。
- 發文補充的標籤會進入咖啡廳篩選資料。

### 10.3 個人頁驗收

- 顯示帳號名。
- 顯示頭貼。
- 顯示暱稱。
- 顯示貼文數。
- 顯示探店數。
- 顯示收藏數。
- 足跡地圖包含已發文咖啡廳。
- 收藏清單包含已收藏咖啡廳。
- 我的貼文包含自己發過的貼文。

## 11. 風險與注意事項

### 11.1 Streamlit 限制

Streamlit 很適合快速 demo，但不適合做高度客製互動地圖。如果老師要求完整像 App 一樣的互動地圖，可能需要：

- Streamlit component。
- Folium / streamlit-folium。
- 或回到 iOS / Web 前端實作。

但若課堂要求只能使用 Python，Streamlit 是較安全的選擇。

### 11.2 Google API 成本

Google Maps Platform 會計費。Demo 前要：

- 設定預算警示。
- 避免無限重複搜尋。
- 優先使用背景資料層保存與合併搜尋結果。

### 11.3 資料正確性

Google 的營業時間、地址、評分可能會改變。使用者貼文也可能是主觀資訊。應在報告中說明：

- Google 資料是外部來源。
- 社群標籤是使用者回饋統計。
- 篩選結果是輔助參考，不是絕對保證。

### 11.4 圖片檔案

目前圖片存在本機 `data/uploads/`。如果換電腦或部署，圖片不會自動同步。若要正式部署，建議改用：

- Firebase Storage。
- S3。
- Cloudinary。
- 或至少把 uploads 資料夾一起備份。

## 12. 建議下一步任務清單

優先順序由高到低：

1. 更新 README 啟動路徑與 Google API 說明。
2. 補上 `.gitignore`。
3. 建立 Git repo 並推到 GitHub。
4. 新增 `cafe_traits` 與 `post_trait_feedback`。
5. 發文表單加入精細回饋欄位。
6. 探索頁加入精細篩選器。
7. 新增貼文收藏。
8. 貼文卡片顯示頭貼。
9. 整理 demo 資料。
10. 更新 demo script。

## 13. 檔案索引

主要程式：

- `app.py`：Streamlit 介面與頁面流程。
- `database.py`：Supabase PostgreSQL / SQLite fallback 資料表、查詢、寫入、統計。
- `google_maps.py`：Google Maps / Places API 串接。
- `seed_data.py`：初始咖啡廳資料。

資料：

- `data/coffee_run.db`：SQLite 資料庫。
- `data/uploads/`：使用者上傳圖片。

文件：

- `README.md`：專案啟動與簡介。
- `docs/01_python_only_check.md`：Python 使用範圍確認。
- `docs/02_prd.md`：舊版產品需求文件。
- `docs/03_team_collaboration.md`：舊版分工文件。
- `docs/04_demo_script.md`：展示流程。
- `docs/05_task_board.md`：任務看板。
- `docs/06_handoff_spec.md`：本交接文件。
