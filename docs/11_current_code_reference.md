# Coffee Run 現行程式碼與函式說明

版本基準：本機 mobile-first 工作版本  
最後更新：2026-05-23  
程式語言：Python / Streamlit

## 1. 目前版本狀態

### 1.1 GitHub 上的已推送版本

目前遠端 repository：

```text
https://github.com/allytsay33/coffee-run.git
```

遠端 `main` 目前可追溯的初始 commit：

```text
49e21b7 chore: initial coffee run streamlit project
```

### 1.2 本機最新工作版本

本機已在初始 commit 後增加以下工作，但尚未 commit / push：

- 將大型 `app.py` 拆成頁面模組與共用元件。
- 改成 mobile-first 介面。
- 新增底部導航。
- 新增手機版 CSS。
- 探索頁依 wireframe 調整搜尋、篩選、地圖和列表布局。
- 補充協作、wireframe 與 schema 文件。

因此目前若組員直接 clone GitHub，取得的不是你電腦上最新手機版。確認新版畫面後，需要再 commit 並 push。

## 2. 目前 Python 檔案樹

```text
app.py
api_keys.py
components.py
config.py
database.py
file_storage.py
filters.py
formatters.py
google_maps.py
seed_data.py
state.py
styles.py
pages/
  __init__.py
  auth.py
  explore.py
  profile.py
  ranking.py
  social.py
```

## 3. 程式架構總覽

```text
app.py
 ├── state.py                  session state
 ├── styles.py                 mobile-first CSS
 ├── pages/auth.py             登入與底部導航
 ├── pages/explore.py          探索功能
 │    ├── filters.py           篩選邏輯
 │    ├── google_maps.py       Google Places / map
 │    ├── api_keys.py          API key 取得
 │    ├── components.py        地圖 / 店家 / 貼文元件
 │    └── database.py          持久化資料
 ├── pages/social.py           發文與 feed
 │    ├── file_storage.py      圖片存檔
 │    ├── components.py        貼文元件
 │    └── database.py
 ├── pages/profile.py          我的頁
 │    ├── components.py
 │    ├── file_storage.py
 │    └── database.py
 └── pages/ranking.py          推薦排行
```

設計原則：

- `app.py` 只負責入口和路由。
- `pages/` 只負責各畫面的組成和使用者操作。
- `components.py` 負責重複使用的 UI 區塊。
- `database.py` 是唯一 SQL 資料存取層。
- `google_maps.py` 隔離外部 API 串接。

## 4. `app.py`

用途：Streamlit 程式入口與頁面路由。

依賴：

- `database`
- `pages.auth`
- `pages.explore`
- `pages.profile`
- `pages.ranking`
- `pages.social`
- `state`
- `styles`

### `main()`

流程：

```text
設定 Streamlit 頁面
→ 注入手機版 CSS
→ 初始化資料庫
→ 初始化 session state
→ 未登入時顯示登入頁
→ 已登入時顯示底部導航
→ 根據選中頁面 render 功能頁
```

目前路由：

| 導航頁面 | 呼叫函式 |
| --- | --- |
| 探索地圖 | `render_explore_page()` |
| 社群 | `render_social_page()` |
| 個人頁 | `render_profile_page()` |
| 推薦排行 | `render_ranking_page()` |

## 5. `config.py`

用途：共用常數設定，無函式。

| 常數 | 內容 | 使用位置 |
| --- | --- | --- |
| `UPLOAD_DIR` | `data/uploads/` | `file_storage.py` |
| `DEFAULT_TAGS` | 預設發文標籤列表 | `pages/social.py` |
| `PAGE_OPTIONS` | 原本頁面選單文字 | 目前已不再由底部 nav 使用，可後續整理 |

`DEFAULT_TAGS` 現行內容：

```text
安靜、插座、不限時、適合讀書、適合聊天、甜點、平價、晚上營業、學生友善
```

## 6. `state.py`

用途：集中初始化 Streamlit 在 rerun 間要保留的狀態。

### `initialize_state()`

建立：

| session key | 初值 | 用途 |
| --- | --- | --- |
| `user` | `None` | 當前登入使用者 |
| `selected_cafe_id` | `None` | 探索頁選中的咖啡廳 |
| `api_key_override` | `""` | 個人頁手動填入的 Google API key |

補充：`pages/auth.py` 目前也動態建立 `current_page` 作底部導航狀態。

## 7. `styles.py`

用途：注入 Streamlit 的手機優先視覺樣式。

### `inject_mobile_styles()`

目前處理：

- 將 app 內容限制為約 `430px`，在電腦上呈現手機畫布。
- 隱藏 sidebar。
- 設定咖啡色主題字體與區塊樣式。
- 設定輸入框與按鈕圓角。
- 設定卡片邊框與陰影。
- 設定固定底部導航樣式。
- 小螢幕時取消手機畫布陰影並填滿寬度。

注意：

- 這是 Streamlit 上的 CSS 客製化，若 Streamlit DOM 結構改變，部分 selector 可能需要調整。

## 8. `api_keys.py`

用途：讓頁面統一取得 Google API key，不需了解來源細節。

### `current_api_key()`

呼叫：

```python
google_maps.get_api_key(st.session_state.get("api_key_override"))
```

使用場景：

- 探索頁匯入 Google Places。
- 地圖元件生成 Google Static Maps。
- 詳情頁同步 Google 店家詳情。

## 9. `google_maps.py`

用途：Google Maps Platform API 串接。

常數：

| 常數 | 用途 |
| --- | --- |
| `TAIPEI_CENTER` | 文字搜尋預設中心座標 |
| `IOS_GOOGLE_SERVICE_PLIST` | 你的本機 iOS 專案 key fallback 路徑 |

### `get_api_key(override=None)`

API key 解析順序：

```text
1. 畫面手動輸入的 override
2. 環境變數 GOOGLE_MAPS_API_KEY
3. 本機 iOS 專案 GoogleService-Info.plist
```

其他組員電腦通常沒有第 3 項，因此應用手動輸入或環境變數。

### `get_api_key_from_ios_project()`

讀取：

```text
~/Desktop/Coffee_Run!!/Coffee_Run!!/GoogleService-Info.plist
```

取出 plist 的 `API_KEY` 欄位。檔案不存在或格式失敗時回傳空字串。

### `search_cafes(keyword, api_key, location=TAIPEI_CENTER, radius=3500)`

功能：呼叫 Google Places Text Search 查詢台北咖啡廳。

輸入：

- `keyword`：搜尋字串。
- `api_key`：Google API key。
- `location`：搜尋中心。
- `radius`：搜尋半徑。

回傳：可直接傳給 `database.upsert_cafe()` 的 cafe dict list。

資料欄位：

```text
cafe_id, google_place_id, name, area, address,
lat, lng, rating, tags, description, opening_hours,
website, maps_url, source
```

### `fetch_place_details(place_id, api_key)`

功能：取得指定 Google Place 的詳細資訊。

回傳欄位：

```text
name, address, lat, lng, rating, opening_hours, website, maps_url
```

使用位置：探索頁店家詳情的「同步 Google 詳情」按鈕。

### `static_map_url(cafes, api_key, width=430, height=430)`

功能：根據有座標的咖啡廳生成手機比例的 Google Static Maps URL。

限制：

- 目前最多取前 10 個 markers。
- 地圖是圖片，不是可點擊的互動式 marker 地圖。

### `google_maps_url(place_id)`

功能：生成在瀏覽器開啟指定 Google Place 的 URL。

### `infer_area(address)`

功能：從地址文字簡單推定區域標籤。

支援比對：

```text
大安、信義、中山、中正、萬華、松山、士林、公館、師大
```

未匹配則回傳 `Google 搜尋`。

## 10. `database.py`

用途：SQLite 的唯一持久化層。頁面不可直接寫 SQL。

資料庫 schema 詳細欄位請讀：

- `docs/10_current_database_schema.md`

### 初始化與資料轉換

| 函式 | 功能 | 呼叫時機 |
| --- | --- | --- |
| `connect()` | 開資料庫 connection，Row 可轉 dict | 所有 DB 操作 |
| `initialize_database()` | 建 table、migration、seed | app 每次啟動 |
| `migrate_existing_tables(connection)` | 舊 DB 補新增欄位 | 初始化 |
| `seed_cafes(connection)` | 放入範例咖啡廳 | 初始化 |
| `split_tags(tags)` | 逗號字串轉 list | cafe 輸出 / tag 更新 |
| `row_to_cafe(row)` | SQLite row 轉 UI cafe dict | 咖啡廳查詢後 |

### 使用者資料

| 函式 | 輸入 | 回傳 / 行為 |
| --- | --- | --- |
| `get_or_create_user(username)` | 帳號名 | 建立或回傳 user dict；空字串回傳 `None` |
| `update_user_profile(user_id, display_name, avatar_path=None)` | 使用者資料 | 更新暱稱，若有新頭貼一併更新 |
| `get_user(user_id)` | ID | user dict 或 `None` |
| `get_user_stats(user_id)` | ID | `favorite_count`, `post_count`, `footprint_count`, `review_count` |

### 咖啡廳資料

| 函式 | 輸入 | 回傳 / 行為 |
| --- | --- | --- |
| `upsert_cafe(cafe)` | cafe dict | 新增或更新；回傳 `cafe_id` |
| `list_cafes()` | 無 | 所有咖啡廳，使用者評分優先排序 |
| `get_cafe(cafe_id)` | cafe ID | 單一 cafe dict |
| `list_areas()` | 無 | 地區名稱列表 |
| `list_all_tags()` | 無 | cafes 與 post_tags 的全部標籤 |
| `refresh_cafe_user_rating(cafe_id)` | cafe ID | 由 reviews + posts 重算 `user_rating` |
| `refresh_cafe_tags(cafe_id)` | cafe ID | 合併貼文標籤到 `cafes.tags` |

### 收藏

| 函式 | 功能 |
| --- | --- |
| `get_favorite_ids(user_id)` | 回傳使用者收藏 cafe ID set |
| `add_favorite(user_id, cafe_id)` | 新增收藏；重複不新增 |
| `remove_favorite(user_id, cafe_id)` | 取消收藏 |
| `list_favorite_cafes(user_id)` | 取得收藏店家列表 |

### 舊版 Reviews

| 函式 | 功能 |
| --- | --- |
| `add_review(user_id, cafe_id, rating, note)` | 寫入舊版心得並更新店家平均 |
| `list_reviews(user_id)` | 取得使用者舊版心得 |

目前新社群頁不主動呼叫此區功能。

### 貼文、留言、愛心

| 函式 | 功能 |
| --- | --- |
| `create_post(user_id, cafe_id, content, rating, image_path, tags)` | 寫入貼文與標籤，再更新咖啡廳平均和標籤 |
| `list_posts(cafe_id=None)` | 回傳全部或指定店家的貼文，並包含作者、店名、愛心數、留言數、標籤 |
| `user_liked_post(user_id, post_id)` | 查目前使用者是否已按讚 |
| `toggle_like(user_id, post_id)` | 已按讚則刪除，未按讚則新增 |
| `add_comment(user_id, post_id, content)` | 新增留言 |
| `list_comments(post_id)` | 查指定貼文留言，時間由舊到新 |

### 足跡

| 函式 | 功能 |
| --- | --- |
| `list_footprint_cafes(user_id)` | 取得使用者曾發文過的不重複咖啡廳，供足跡地圖顯示 |

## 11. `filters.py`

用途：探索頁的目前本機篩選邏輯。

### `filtered_cafes(cafes, keyword, area, minimum_rating, selected_tags)`

輸入：

- `cafes`：從 DB 取得的 cafe dict list。
- `keyword`：站內文字搜尋。
- `area`：地區或 `全部`。
- `minimum_rating`：最低評分。
- `selected_tags`：必須全部具備的標籤列表。

比對規則：

- keyword 搜尋店名、地區、地址、描述、標籤。
- 評分使用 `user_rating`，若無則使用 Google `rating`。
- 多選標籤採 AND 規則：店家必須包含所有已選標籤。

目前限制：

- `營業中`、距離上限、結構化 traits 尚未真正實作。

## 12. `components.py`

用途：跨頁重複使用的畫面區塊。

### `render_map(cafes)`

功能：

- 過濾沒有座標的店家。
- 有 API key 時顯示 Google Static Map。
- 無 API key 時回退使用 Streamlit `st.map()`。

### `render_cafe_card(cafe)`

功能：

- 顯示手機版咖啡廳卡片。
- 顯示店名、距離、綜合評分、地區、地址、描述、標籤。
- 「查看詳情」寫入 `selected_cafe_id`。
- 「收藏 / 取消收藏」操作 `favorites`。

### `render_post_card(post, compact=False)`

功能：

- 顯示貼文的咖啡廳名稱、作者、圖片、內文、標籤、評分、愛心數與留言數。
- 提供愛心切換。
- 展開留言與新增留言。

`compact` 目前用於產生不同 Streamlit widget key，避免同一篇貼文同時出現在不同區塊時 key 衝突。

## 13. `file_storage.py`

用途：上傳圖片寫入本機資料夾。

### `save_uploaded_file(uploaded_file, folder)`

流程：

```text
若沒有檔案 → 回傳 None
→ 建立 data/uploads/
→ 使用 UUID 生成不重複檔名
→ 寫入本機
→ 回傳路徑字串
```

使用場景：

- 貼文圖片：folder 為 `post`。
- 個人頭貼：folder 為 `avatar`。

限制：

- 換電腦後圖片不會自動同步。
- `data/uploads/` 目前應被 `.gitignore` 排除。

## 14. `formatters.py`

### `format_distance(distance_meters)`

| 情況 | 顯示 |
| --- | --- |
| 空值或 0 | `距離待補` |
| 小於 1000 m | `350 m` |
| 大於等於 1000 m | `1.2 km` |

### `format_tags(tags)`

將 list 轉為 Streamlit markdown inline code 標籤，例如：

```text
`安靜` `插座`
```

## 15. `pages/auth.py`

用途：登入頁和底部導航。

### `render_login_page()`

功能：

- 顯示 Coffee Run 標題。
- 輸入帳號名。
- 呼叫 `get_or_create_user()`。
- 登入後寫入 session state 並 rerun。

### `render_mobile_nav()`

功能：

- 將目前 user 重新由 DB 讀取到 session。
- 管理 `current_page` 狀態。
- 顯示底部導航 radio。
- 將顯示文字映射到實際頁面 route。

目前含四頁：

```text
探索、社群、我的、排行
```

wireframe 主要只有三頁，是否保留「排行」由產品決策確認。

## 16. `pages/explore.py`

用途：探索、地圖、Google 匯入、詳情與相關貼文。

### `render_google_search_import(api_key)`

功能：

- 顯示搜尋欄與搜尋按鈕。
- 有 API key 時呼叫 `google_maps.search_cafes()`。
- 將每筆結果用 `database.upsert_cafe()` 存入 DB。
- 完成後 rerun 顯示最新店家。

### `render_explore_page()`

功能：

- 顯示「探索咖啡廳」手機版主頁。
- 讀取所有 cafes、areas、tags。
- 顯示快速 chips 與更多篩選展開區。
- 呼叫 `filtered_cafes()`。
- 用同一批 results 顯示地圖與列表。
- 最後顯示目前選中店家的詳情。

目前注意事項：

- 快速 chip `營業中` 目前只是視覺選項，尚未有開店狀態查詢。
- 地圖使用圖片呈現，不支援點 marker 開詳情。

### `render_cafe_detail()`

功能：

- 取得 `selected_cafe_id` 對應的店家。
- 顯示描述、地址、營業時間、外部連結、評分與標籤。
- Google 匯入店家可按鈕同步 Place Details。
- 取得並顯示與此咖啡廳相關的所有貼文。

## 17. `pages/social.py`

用途：社群 feed 與發文。

### `render_post_form(cafes)`

功能：

- 要求選擇特定咖啡廳。
- 輸入評分、標籤、內文。
- 上傳單張圖片。
- 驗證內文不為空。
- 呼叫 `database.create_post()`。

### `render_social_page()`

功能：

- 顯示社群頁標題。
- 將發文表單放在可展開區塊。
- 讀取最新貼文並以 `render_post_card()` 呈現。

與 wireframe 尚有差距：

- 現為一欄 feed，未做縮圖瀑布流 / grid。
- 未做獨立貼文詳情頁。
- 未做多張照片。

## 18. `pages/profile.py`

用途：我的頁、帳號設定、收藏與足跡。

### `render_profile_header(user, stats)`

功能：

- 顯示頭貼或未上傳提示。
- 顯示暱稱和帳號名。
- 顯示貼文數、探店數、收藏數。

### `render_profile_editor(user)`

功能：

- 編輯暱稱。
- 上傳新頭貼。
- 更新後 rerun。

### `render_profile_page()`

功能：

- 讀使用者與統計資料。
- 顯示個人卡片與編輯區。
- 提供 Google API key 輸入與登出。
- 顯示發過文店家的足跡地圖。
- 顯示收藏清單。
- 顯示自己的貼文。

與 wireframe 尚有差距：

- 未做探店 / 足跡 / 已收藏三個 icon tabs。
- 未做個人簡介。
- 未做 Top 3 探店。
- 未做分享個人檔案。

## 19. `pages/ranking.py`

用途：目前額外存在的推薦排行頁。

### `render_ranking_page()`

功能：

- 讀取所有咖啡廳。
- 依 `user_rating`，若無則 `rating`，由高到低排序。
- 顯示排行卡片。

產品決策待確認：

- 此頁不在最新三頁 wireframe 的底部導航主需求中。
- 可保留作 Demo 加分頁，或併回探索頁後移除主導航入口。

## 20. `seed_data.py`

用途：首次啟動用的示範咖啡廳資料，無函式。

常數：

- `SEED_CAFES`：目前含 6 間示範咖啡廳，包含座標、評分、標籤、描述、營業時間與 Google Maps URL。

注意：

- 這些店名多為 demo 資料，不等同正式 Google Places 結果。
- Google 搜尋後取得的真實店家會另外寫入同一張 `cafes` 表。

## 21. 目前完成度對照

| 功能 | 現況 |
| --- | --- |
| 手機版畫布與底部導覽 | 本機已實作 |
| Google Places 搜尋 | 已實作且 key 測試成功 |
| 地圖顯示 | 已實作，Static Map / `st.map` fallback |
| 關鍵字 / 地區 / 評分 / tags 篩選 | 已實作 |
| 營業中與結構化精細篩選 | 未實作 |
| 咖啡廳詳情與相關貼文 | 已實作 |
| 收藏咖啡廳 | 已實作 |
| 社群發文 / 單圖 / 評分 / tags | 已實作 |
| 愛心 / 留言 | 已實作 |
| 社群圖片 grid / 詳情獨立頁 | 未實作 |
| 個人資料 / 頭貼 / 統計 | 已實作 |
| 足跡地圖 / 收藏清單 / 我的貼文 | 已實作 |
| 個人 tabs / bio / Top 3 | 未實作 |

## 22. 啟動與檢查

啟動：

```bash
cd /Users/weishan33/Desktop/coffee_run_streamlit
python3 -m streamlit run app.py
```

編譯檢查：

```bash
python3 -m py_compile app.py database.py google_maps.py seed_data.py config.py state.py formatters.py file_storage.py filters.py api_keys.py components.py styles.py pages/*.py
```

在確認本機 mobile-first 版本符合設計後，需另行 commit / push，GitHub 組員才會取得同一版本。

