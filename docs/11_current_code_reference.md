# Coffee Run 現行程式碼與函式說明

更新日期：2026-05-24  
版本：依手機 wireframe 完成之本機工作版本

## 1. 程式檔案結構

```text
app.py                  App 入口與三頁路由
config.py               標籤、快速篩選與個人頁 tab 常數
state.py                Streamlit 跨 rerun 狀態
styles.py               手機版 CSS
components.py           地圖、店家卡片、貼文卡片、收藏共用元件
formatters.py           距離與標籤格式
file_storage.py         單圖 / 多圖上傳存檔
api_keys.py             畫面使用的 Google API key 入口
google_maps.py          Places 搜尋、Details、Static Map
filters.py              探索頁篩選規則
database.py             Supabase PostgreSQL / SQLite fallback 與所有資料存取
seed_data.py            初始咖啡廳資料
pages/
  auth.py               登入與三頁底部導航
  explore.py            探索、篩選、結果、店家詳情
  social.py             圖牆、貼文詳情、發布貼文
  profile.py            探店、足跡、收藏、編輯個人檔案
  ranking.py            舊排行頁，已不在主導航
```

## 2. 整體流程

```text
app.main()
→ database.initialize_database()
→ state.initialize_state()
→ render_login_page() 或 render_mobile_nav()
→ 探索 / 社群 / 我的
```

底部導航已依 wireframe 收斂為：

```text
探索、社群、我的
```

## 3. 核心檔案與函式

## 3.1 `app.py`

| 函式 | 功能 |
| --- | --- |
| `main()` | 設定 Streamlit、注入 CSS、初始化 DB 與 session、依三頁導航顯示頁面 |

## 3.2 `config.py`

無函式，提供：

| 常數 | 功能 |
| --- | --- |
| `UPLOAD_DIR` | 使用者圖片本機存放資料夾 |
| `DEFAULT_TAGS` | 發文標籤選項 |
| `QUICK_FILTERS` | 探索 chips：營業中、深夜咖啡廳、不限時、插座多 |
| `PROFILE_TABS` | 個人頁：探店紀錄、足跡地圖、已收藏 |

## 3.3 `state.py`

| 函式 | 功能 |
| --- | --- |
| `initialize_state()` | 初始化登入者、頁面、選中咖啡廳、選中貼文、社群子頁、個人 tab、探索 filters 等狀態 |

## 3.4 `styles.py`

| 函式 | 功能 |
| --- | --- |
| `inject_mobile_styles()` | 建立約 430px 手機畫布、底部導航、咖啡色視覺、圖牆 placeholder 與頭貼樣式 |

## 3.5 `formatters.py`

| 函式 | 功能 |
| --- | --- |
| `format_distance(distance_meters)` | 將距離格式化為 m / km 或待補 |
| `format_tags(tags)` | 將標籤列表格式化供 Streamlit 顯示 |

## 3.6 `file_storage.py`

| 函式 | 功能 |
| --- | --- |
| `save_uploaded_file(uploaded_file, folder)` | 用 UUID 名稱保存一張圖片 |
| `save_uploaded_files(uploaded_files, folder)` | 保存多張圖片並保留使用者上傳順序 |

## 3.7 `api_keys.py`

| 函式 | 功能 |
| --- | --- |
| `current_api_key()` | 讀取目前頁面應使用的 Google API key |

## 3.8 `google_maps.py`

| 函式 | 功能 |
| --- | --- |
| `get_api_key(override=None)` | 順序讀取手動輸入、環境變數、本機 iOS plist |
| `get_api_key_from_ios_project()` | 讀原 iOS 專案 `GoogleService-Info.plist` |
| `search_cafes(keyword, api_key, location, radius)` | Google Places 搜尋並正規化成 cafe dict，包含 `open_now` |
| `fetch_place_details(place_id, api_key)` | 同步地址、營業時間、評分、網址與營業狀態 |
| `static_map_url(cafes, api_key, width, height)` | 生成手機比例地圖 URL |
| `google_maps_url(place_id)` | 建立店家 Google Maps 外連 |
| `infer_area(address)` | 從地址推估地區 |

## 3.9 `filters.py`

| 函式 | 功能 |
| --- | --- |
| `filtered_cafes(...)` | 依搜尋字、區域、評分、標籤、距離及快速條件篩選店家 |

快速條件邏輯：

- `營業中`：使用 Google `open_now`；未知狀態仍保留於結果。
- `深夜咖啡廳`：看 tag 或 `open_late_score`。
- `不限時`：看 tag 或 `no_time_limit_score`。
- `插座多`：看 tag 或 `has_outlets_score`。

## 3.10 `components.py`

| 函式 | 功能 |
| --- | --- |
| `render_map(cafes)` | 顯示目前結果的 Google Static Map 或 Streamlit fallback map |
| `toggle_favorite_button(cafe_id, key, stretch)` | 所有頁共用的咖啡廳收藏切換 |
| `render_cafe_photos(cafe_id, columns)` | 用社群照片形成店家圖片列表 |
| `render_cafe_card(cafe, compact=False)` | 搜尋結果 / 收藏中的手機店家卡片 |
| `render_post_images(post)` | 顯示單張或多張貼文圖片 |
| `render_post_card(post, compact=False, open_detail=True)` | 貼文內容、愛心、收藏、留言或跳詳情 |

## 4. 資料存取函式：`database.py`

完整資料表請見 `docs/10_current_database_schema.md`。

### 4.1 初始化與轉換

| 函式 | 功能 |
| --- | --- |
| `configured_postgres_url()` | 從環境或 Streamlit secrets 取得 Supabase 私密連線字串 |
| `using_supabase()` / `database_label()` | 判斷目前是否使用多人共用雲端資料庫 |
| `connect()` | 有 Supabase 設定時連 PostgreSQL；否則連本機 SQLite |
| `initialize_database()` | 在目前選定資料庫建立 tables、執行 migration、填 seed 與 seed traits |
| `migrate_existing_tables(connection)` | 舊 DB 自動補 `bio`, `open_now`, `updated_at` 等欄位 |
| `seed_cafes(connection)` | 初始店家資料 |
| `seed_cafe_traits(connection)` | 初始店家標籤轉可篩選 trait |
| `seed_demo_social_data(connection)` | 建立可重複執行、不會重複新增的示範貼文與互動 |
| `split_tags(tags)` | tag 字串轉 list |
| `row_to_cafe(row)` | DB row 轉 page 所需 cafe dict |

### 4.2 使用者

| 函式 | 功能 |
| --- | --- |
| `get_or_create_user(username)` | 簡易登入 |
| `get_user(user_id)` | 取得個人檔案含 `bio` |
| `update_user_profile(user_id, display_name, bio, avatar_path)` | 更新暱稱、簡介與頭貼 |
| `get_user_stats(user_id)` | 取得探店紀錄數、收藏數與足跡數 |

### 4.3 咖啡廳與收藏

| 函式 | 功能 |
| --- | --- |
| `upsert_cafe(cafe)` | 儲存 / 更新 Google 或 seed 店家並建立 traits 容器 |
| `_cafe_query(...)` | 加入 traits 的共用查詢 |
| `list_cafes()` | 探索店家列表 |
| `get_cafe(cafe_id)` | 店家詳情 |
| `list_areas()` | 地區選項 |
| `list_all_tags()` | tag 選項 |
| `get_cafe_photos(cafe_id, limit)` | 從社群貼文取得店家照片 |
| `get_favorite_ids(user_id)` | 查收藏狀態 |
| `add_favorite(user_id, cafe_id)` | 收藏 |
| `remove_favorite(user_id, cafe_id)` | 取消收藏 |
| `list_favorite_cafes(user_id)` | 個人頁已收藏 |
| `list_footprint_cafes(user_id)` | 個人頁足跡地圖 |

### 4.4 貼文與社群互動

| 函式 | 功能 |
| --- | --- |
| `create_post(...)` | 同步寫入貼文、多圖、tags、結構化 feedback，並更新店家評分 / traits |
| `_post_query(...)` | 社群共用查詢，附愛心留言數、照片與標籤 |
| `list_posts(cafe_id=None, user_id=None, search="", sort_by="latest")` | feed、搜尋、店家貼文與個人貼文 |
| `get_post(post_id)` | 貼文詳情 |
| `user_liked_post(user_id, post_id)` | 是否已按愛心 |
| `toggle_like(user_id, post_id)` | 愛心切換 |
| `add_comment(user_id, post_id, content)` | 留言 |
| `list_comments(post_id)` | 留言列表 |
| `refresh_cafe_user_rating(cafe_id)` | 重算站內店家評分 |
| `refresh_cafe_tags(cafe_id)` | 將貼文標籤加入店家搜尋 |
| `refresh_cafe_traits(cafe_id)` | 將細部 feedback 平均成探索篩選資料 |
| `add_review(...)`, `list_reviews(...)` | 保留舊版 review 相容 |

## 5. 頁面檔案

## 5.1 `pages/auth.py`

| 函式 | 功能 |
| --- | --- |
| `render_login_page()` | 帳號名簡易登入 |
| `render_mobile_nav()` | 底部三頁導航：探索、社群、我的 |

## 5.2 `pages/explore.py`

| 函式 | 功能 |
| --- | --- |
| `render_filter_sheet(areas, tags)` | 完整篩選子頁，套用評分、距離、地區、特色 |
| `render_cafe_detail(cafe_id)` | 展開結果、照片、社群貼文、收藏、Google Maps 連結 |
| `sync_search_results(keyword)` | 唯一搜尋框的背景同步流程：呼叫 Google Places 並保存結果 |
| `render_explore_page()` | 探索初始頁、搜尋、chips、地圖、結果切換 |

探索頁不提供資料庫搜尋與 Google 搜尋兩組控制。資料庫同步發生在單一搜尋按鈕背後，畫面只呈現合併後的結果。

## 5.3 `pages/social.py`

| 函式 | 功能 |
| --- | --- |
| `render_social_gallery(posts)` | 三欄貼文圖片圖牆 |
| `render_post_detail(post_id)` | 貼文完整內容、愛心、留言與收藏店家 |
| `render_create_post_page()` | 獨立發文頁，支援多圖、評分、標籤與細部回饋 |
| `render_social_page()` | 社群子頁路由、搜尋與熱門 / 最新排序 |

## 5.4 `pages/profile.py`

| 函式 | 功能 |
| --- | --- |
| `render_profile_header(user, stats)` | 頭貼、自介、探店與收藏數 |
| `render_profile_editor(user)` | 編輯頭貼、名稱、自介 |
| `render_profile_settings()` | API key 與登出 |
| `render_profile_page()` | 探店紀錄 / 足跡地圖 / 已收藏三 tab |

## 5.5 `pages/ranking.py`

保留舊功能函式 `render_ranking_page()`，目前不在 wireframe 三頁導航中，不影響主流程。

## 6. `seed_data.py`

`SEED_CAFES` 提供首次啟動就可顯示地圖與展示篩選的六間咖啡廳。  
真實店家則由 Google Places 匯入至同一張 `cafes` 表。

## 7. 已完成的 wireframe 功能

| 功能 | 實作狀態 |
| --- | --- |
| 手機版畫布與三頁底部導航 | 完成 |
| 探索地圖與搜尋結果 | 完成 |
| Google Places 匯入 / 詳情同步 | 完成 |
| 快速 chips 與完整篩選頁 | 完成 |
| 店家展開詳情、收藏、相關貼文 | 完成 |
| 社群三欄圖牆 | 完成 |
| 貼文詳情、愛心、留言、收藏咖啡廳 | 完成 |
| 獨立發文頁、多張圖片、評分、標籤 | 完成 |
| 發文資料補充探索篩選 | 完成 |
| 個人頁、自介與編輯檔案 | 完成 |
| 探店紀錄 / 足跡地圖 / 已收藏 tabs | 完成 |

## 8. 技術限制

- 地圖目前採 Google Static Map 圖片，marker 不可直接點擊；店家可由結果列表點入。
- 使用者頭貼與貼文圖片存於本機 `data/uploads/`，尚未使用雲端儲存。
- 登入為課堂 Demo 用帳號名登入，沒有密碼驗證。
- 分享個人檔案按鈕保留於 wireframe 位置但目前停用。
