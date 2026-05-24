# Coffee Run 分工、資料庫 Schema 與功能契約


## 1. 建議六人職責表

| 角色 | 主責 | 可修改範圍 | 不應單獨決定 |
| --- | --- | --- | --- |
| 1. UI / UX / 流程 / 共用元件 / 驗收整合 | Figma、手機版視覺、共用卡片、操作流程、整合驗收、簡報視覺與錄影腳本 | `styles.py`, `components.py`, `docs/`, `README.md` | 資料表 schema、功能資料查詢規則 |
| 2. 探索頁功能 | 探索初始頁、篩選 UI、結果列表、詳情頁、Google Map / Places 呼叫與畫面連動 | `pages/explore.py`, `filters.py`, `google_maps.py`, `api_keys.py` | 整體 schema；需以 issue / 契約向資料庫組提出需求 |
| 3. 探索資料庫與咖啡廳資料匯入，兼任 Schema Owner | **全專案 schema 與 migration 最終 owner**、`cafes`、精細篩選統計、Google 匯入 / 初始咖啡廳資料 | `database.py` schema/migration、`seed_data.py`、未來 `data_import/` | 社群頁與個人頁 UI |
| 4. 社群頁功能 | 社群縮圖牆 / feed、貼文詳情、發文表單、圖片上傳、愛心留言互動 | `pages/social.py`, `file_storage.py`, post 元件 | 自行新增資料表；需求交給 schema owner |
| 5. 社群資料庫與 Demo 使用者資料 | posts、photos、tags、comments、likes、預設使用者、預設貼文與 demo 互動資料 | `database.py` 中社群 repository 函式、社群 seed script | 修改 `cafes` 核心定義或 schema 命名規則 |
| 6. 個人頁功能與資料查詢 | 個人檔案、探店紀錄、足跡地圖、收藏清單、編輯檔案，並協助最終流程測試 | `pages/profile.py`、個人與收藏 repository 函式 | 未經 schema owner review 新增欄位 |



## 2. 所有模組共用規則

### 3.1 Schema Owner 規則

角色 3 是 schema owner，負責：

- 定義 table 與欄位名稱。
- 新增 migration。
- Review 任何資料表變更。
- 確保不同功能不重複建立概念相同的表。

角色 5 與角色 6 可以寫自己功能所需的 repository 函式，但若需新增欄位 / table，流程為：

```text
功能 owner 列出需求
→ schema owner 確認 schema
→ schema owner 或與該功能 DB 負責人共同實作 migration
→ 功能 owner 接 repository function
```

### 3.2 頁面不直接寫 SQL

`pages/*.py` 只能：

- 接收使用者操作。
- 呼叫 service / database 函式。
- 顯示資料與錯誤訊息。

不得在頁面中直接執行 SQL。所有 SQL 統一放資料庫層。

### 3.3 功能契約先於實作

每一組先確認輸入與回傳資料形狀，例如：

```python
cafe = {
    "cafe_id": "google-abc",
    "name": "Angelina",
    "area": "內湖",
    "address": "台北市內湖區...",
    "lat": 25.08,
    "lng": 121.57,
    "rating": 4.3,
    "user_rating": 4.6,
    "tags": ["不限時", "插座多"],
}
```

只要資料契約固定，頁面與資料庫就可平行開發。

## 4. Schema 設計原則

### 4.1 現有實作與目標 Schema 的關係

目前程式已有：

```text
users
cafes
favorites
reviews
posts
post_tags
comments
likes
```

為降低 Demo 前風險，建議：

- 保留現有 table 與欄位。
- 只以 migration 新增必要欄位 / table。
- 不在近期大幅 rename `cafes.rating` 或刪除 `reviews`。

### 4.2 資料分層

資料分為四類：

| 類型 | 例子 | 來源 |
| --- | --- | --- |
| 使用者資料 | 暱稱、頭貼、自介 | 使用者輸入 / demo seed |
| 店家基礎資料 | 店名、地址、座標、Google 評分、營業時間 | Google Places / seed |
| 社群資料 | 貼文、照片、留言、愛心 | 使用者互動 |
| 彙整篩選資料 | 不限時、插座多、安靜、使用者評分 | 社群 feedback 彙整 |

## 5. 完整資料庫 Schema

以下為 Demo 完整 schema 的功能契約。實際 Supabase PostgreSQL SQL 請以 `docs/10_current_database_schema.md` 為準。

## 5.1 users：使用者

用途：登入、個人頁、貼文作者、留言者。

| 欄位 | 型別 | 必填 | 說明 | 狀態 |
| --- | --- | --- | --- | --- |
| `user_id` | BIGSERIAL PK | 是 | 使用者 ID | 目前已有 |
| `username` | TEXT UNIQUE | 是 | 帳號名，登入使用 | 目前已有 |
| `display_name` | TEXT | 否 | 顯示暱稱 | 目前已有 |
| `avatar_path` | TEXT | 否 | 頭貼檔案路徑 | 目前已有 |
| `bio` | TEXT DEFAULT `''` | 否 | 個人簡介 | 新增 |
| `created_at` | TEXT | 是 | 建立時間 | 目前已有 |

建議 SQL：

```sql
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    avatar_path TEXT,
    bio TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## 5.2 cafes：咖啡廳主資料

用途：探索結果、地圖 marker、詳情頁、收藏、足跡。

| 欄位 | 型別 | 必填 | 說明 | 狀態 |
| --- | --- | --- | --- | --- |
| `cafe_id` | TEXT PK | 是 | 本系統 ID，例如 `google-{place_id}` | 目前已有 |
| `google_place_id` | TEXT UNIQUE | 否 | Google Place ID | 目前已有 |
| `name` | TEXT | 是 | 店名 | 目前已有 |
| `area` | TEXT | 是 | 顯示地區，例如內湖、大安 | 目前已有 |
| `address` | TEXT | 是 | 地址 | 目前已有 |
| `lat` | REAL | 否 | 緯度 | 目前已有 |
| `lng` | REAL | 否 | 經度 | 目前已有 |
| `distance_meters` | INTEGER DEFAULT 0 | 是 | 和搜尋中心 / 使用者距離，現階段可為 0 | 目前已有 |
| `rating` | REAL DEFAULT 0 | 是 | Google 評分，保留現有命名 | 目前已有 |
| `user_rating` | REAL DEFAULT 0 | 是 | 站內使用者平均評分 | 目前已有 |
| `opening_hours` | TEXT DEFAULT `''` | 是 | Google 營業時間文字 | 目前已有 |
| `open_now` | INTEGER | 否 | 最近一次 API 查詢時是否營業中：0 / 1 / NULL | 新增 |
| `website` | TEXT DEFAULT `''` | 是 | 官方網站 | 目前已有 |
| `maps_url` | TEXT DEFAULT `''` | 是 | Google Maps 外連 | 目前已有 |
| `description` | TEXT DEFAULT `''` | 是 | 簡介 | 目前已有 |
| `tags` | TEXT DEFAULT `''` | 是 | Demo 用文字標籤快取 | 目前已有 |
| `source` | TEXT DEFAULT `'seed'` | 是 | `seed`, `google_places`, `manual` | 目前已有 |
| `created_at` | TEXT | 是 | 建立時間 | 目前已有 |
| `updated_at` | TEXT | 否 | 最後同步時間 | 新增 |

注意：

- `tags` 可支援目前 Demo；正式精細篩選仍應依 `cafe_traits`。
- `rating` 保留作 Google 評分以避免改壞既有程式；文件中可稱為 `google_rating`。

## 5.3 cafe_photos：咖啡廳照片

用途：探索結果列表三張縮圖、咖啡廳詳情照片區。

| 欄位 | 型別 | 說明 | 狀態 |
| --- | --- | --- | --- |
| `photo_id` | BIGSERIAL PK | 照片 ID | 已有 |
| `cafe_id` | TEXT FK | 對應店家 | 新增 |
| `image_url` | TEXT | Google / 遠端圖片 URL | 新增 |
| `local_path` | TEXT | 本機 demo 圖片路徑 | 新增 |
| `source` | TEXT | `google`, `post`, `seed` | 新增 |
| `sort_order` | INTEGER DEFAULT 0 | 顯示順序 | 新增 |
| `created_at` | TEXT | 建立時間 | 新增 |

Demo 簡化：

- 可暫不建立此表，先從貼文圖片顯示店家照片。
- 若要符合 wireframe 的三張店家縮圖，再新增此表。

## 5.4 cafe_traits：咖啡廳彙整特徵

用途：探索頁精細篩選，資料來自初始資料與使用者貼文回饋。

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `cafe_id` | TEXT PK / FK | 咖啡廳 |
| `has_outlets_score` | REAL DEFAULT 0 | 插座多可信分數 / 平均分 |
| `no_time_limit_score` | REAL DEFAULT 0 | 不限時可信分數 |
| `quiet_score` | REAL DEFAULT 0 | 安靜程度平均 |
| `study_score` | REAL DEFAULT 0 | 適合讀書程度平均 |
| `chat_score` | REAL DEFAULT 0 | 適合聊天程度平均 |
| `dessert_score` | REAL DEFAULT 0 | 甜點推薦程度 |
| `price_score` | REAL DEFAULT 0 | 平價程度 |
| `open_late_score` | REAL DEFAULT 0 | 深夜咖啡廳程度 |
| `feedback_count` | INTEGER DEFAULT 0 | 累積回饋數 |
| `updated_at` | TEXT | 更新時間 |

建議 SQL：

```sql
CREATE TABLE IF NOT EXISTS cafe_traits (
    cafe_id TEXT PRIMARY KEY,
    has_outlets_score REAL NOT NULL DEFAULT 0,
    no_time_limit_score REAL NOT NULL DEFAULT 0,
    quiet_score REAL NOT NULL DEFAULT 0,
    study_score REAL NOT NULL DEFAULT 0,
    chat_score REAL NOT NULL DEFAULT 0,
    dessert_score REAL NOT NULL DEFAULT 0,
    price_score REAL NOT NULL DEFAULT 0,
    open_late_score REAL NOT NULL DEFAULT 0,
    feedback_count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);
```

## 5.5 favorites：收藏的咖啡廳

用途：探索 / 貼文詳情點收藏，個人頁顯示已收藏。

| 欄位 | 型別 | 說明 | 狀態 |
| --- | --- | --- | --- |
| `user_id` | INTEGER FK | 收藏者 | 目前已有 |
| `cafe_id` | TEXT FK | 被收藏店家 | 目前已有 |
| `created_at` | TEXT | 收藏時間 | 目前已有 |

主鍵：

```text
(user_id, cafe_id)
```

重要產品決策：

- wireframe 上的書籤 icon 是**收藏咖啡廳**，不是收藏單篇貼文。
- 因此同一間店不論從探索頁或貼文詳情收藏，都寫入此表。

## 5.6 posts：探店貼文

用途：社群貼文、個人探店紀錄、咖啡廳相關貼文。

| 欄位 | 型別 | 必填 | 說明 | 狀態 |
| --- | --- | --- | --- | --- |
| `post_id` | BIGSERIAL PK | 是 | 貼文 ID | 目前已有 |
| `user_id` | INTEGER FK | 是 | 作者 | 目前已有 |
| `cafe_id` | TEXT FK | 是 | 必須連結的咖啡廳 | 目前已有 |
| `content` | TEXT | 是 | 內文 | 目前已有 |
| `rating` | INTEGER | 是 | 作者給咖啡廳的評分 1 到 5 | 目前已有 |
| `image_path` | TEXT | 否 | Demo 單圖路徑 | 目前已有 |
| `created_at` | TEXT | 是 | 發布時間 | 目前已有 |
| `updated_at` | TEXT | 否 | 編輯時間 | 新增，非 Demo 必要 |

約束：

- 貼文必須指定 `cafe_id`。
- `rating` 應限制在 1 至 5。
- `content` 不可為空。

## 5.7 post_photos：貼文多張照片

用途：發文選多張相片、貼文詳情左右滑動圖片。

| 欄位 | 型別 | 說明 | 狀態 |
| --- | --- | --- | --- |
| `photo_id` | BIGSERIAL PK | 照片 ID | 已有 |
| `post_id` | INTEGER FK | 貼文 ID | 新增 |
| `image_path` | TEXT | 圖片檔案位置 | 新增 |
| `sort_order` | INTEGER DEFAULT 0 | 使用者排定順序 | 新增 |
| `created_at` | TEXT | 建立時間 | 新增 |

Demo 簡化：

- 目前 `posts.image_path` 可支援單圖發文。
- 多張圖片與排序可列第二階段。

## 5.8 post_tags：貼文標籤

用途：貼文顯示 chips，並補充咖啡廳探索篩選資料。

| 欄位 | 型別 | 說明 | 狀態 |
| --- | --- | --- | --- |
| `post_id` | INTEGER FK | 貼文 | 目前已有 |
| `tag` | TEXT | 標籤名稱 | 目前已有 |

主鍵：

```text
(post_id, tag)
```

建議固定可選標籤：

```text
深夜咖啡廳
不限時
插座多
安靜
適合讀書
適合聊天
甜點
平價
交通方便
```

## 5.9 post_trait_feedback：單篇貼文細部評價

用途：不要只把使用者選的標籤混在字串中，而是保留可統計的回饋來源。

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `post_id` | INTEGER PK / FK | 回饋來自哪篇貼文 |
| `cafe_id` | TEXT FK | 評價哪間店 |
| `user_id` | INTEGER FK | 評價者 |
| `has_outlets` | INTEGER | 0 / 1 / NULL |
| `no_time_limit` | INTEGER | 0 / 1 / NULL |
| `quiet_score` | INTEGER | 1 到 5 / NULL |
| `study_score` | INTEGER | 1 到 5 / NULL |
| `chat_score` | INTEGER | 1 到 5 / NULL |
| `dessert_score` | INTEGER | 1 到 5 / NULL |
| `price_score` | INTEGER | 1 到 5 / NULL |
| `open_late` | INTEGER | 0 / 1 / NULL |
| `created_at` | TEXT | 建立時間 |

用途流程：

```text
發文填寫細節
→ 寫入 post_trait_feedback
→ 計算平均 / 比例
→ 更新 cafe_traits
→ 探索篩選使用 cafe_traits
```

Demo 簡化：

- 目前可先以 `post_tags` 更新 `cafes.tags`。
- 若精細篩選是評分重點，應優先新增此表與 `cafe_traits`。

## 5.10 comments：貼文留言

| 欄位 | 型別 | 說明 | 狀態 |
| --- | --- | --- | --- |
| `comment_id` | BIGSERIAL PK | 留言 ID | 目前已有 |
| `post_id` | INTEGER FK | 貼文 | 目前已有 |
| `user_id` | INTEGER FK | 留言者 | 目前已有 |
| `content` | TEXT | 留言內容 | 目前已有 |
| `created_at` | TEXT | 時間 | 目前已有 |

## 5.11 likes：貼文愛心

| 欄位 | 型別 | 說明 | 狀態 |
| --- | --- | --- | --- |
| `post_id` | INTEGER FK | 貼文 | 目前已有 |
| `user_id` | INTEGER FK | 按讚者 | 目前已有 |
| `created_at` | TEXT | 時間 | 目前已有 |

主鍵：

```text
(post_id, user_id)
```

## 5.12 reviews：舊版筆記表

目前程式已有 `reviews`，但 wireframe 已將評分整合進貼文。

決策：

- Demo 前保留，避免 migration 破壞現有資料。
- 新功能不再優先寫入 `reviews`。
- 評分以 `posts.rating` 與 `cafes.user_rating` 為主。

## 6. Table 關聯圖

```text
users
 ├──< posts >── cafes ──1 cafe_traits
 │      ├──< post_photos
 │      ├──< post_tags
 │      ├──1 post_trait_feedback
 │      ├──< comments >── users
 │      └──< likes >──── users
 │
 └──< favorites >── cafes

cafes
 └──< cafe_photos
```

## 7. 主要資料物件契約

## 7.1 Cafe DTO

探索頁與個人頁接收的咖啡廳資料至少要長這樣：

```python
{
    "cafe_id": "google-ChIJxxx",
    "google_place_id": "ChIJxxx",
    "name": "Angelina",
    "area": "內湖",
    "address": "台北市內湖區...",
    "lat": 25.08,
    "lng": 121.57,
    "distance_meters": 120,
    "rating": 4.3,
    "user_rating": 4.6,
    "opening_hours": "週一至週日 09:00-22:00",
    "open_now": True,
    "website": "",
    "maps_url": "...",
    "tags": ["不限時", "插座多"],
    "description": "...",
    "source": "google_places",
}
```

## 7.2 Post DTO

社群頁與咖啡廳詳情接收的貼文資料：

```python
{
    "post_id": 1,
    "user_id": 2,
    "username": "ally",
    "display_name": "Ally",
    "avatar_path": "...",
    "cafe_id": "google-ChIJxxx",
    "cafe_name": "Angelina",
    "content": "這間咖啡廳很適合讀書。",
    "rating": 5,
    "image_path": "...",
    "photos": ["...", "..."],
    "tags": ["安靜", "插座多"],
    "like_count": 201,
    "comment_count": 30,
    "created_at": "2026-05-23 01:00:00",
}
```

## 7.3 Profile DTO

```python
{
    "user_id": 1,
    "username": "ally",
    "display_name": "Ally",
    "avatar_path": "...",
    "bio": "喜歡找適合讀書的咖啡廳",
    "post_count": 30,
    "footprint_count": 18,
    "favorite_count": 10,
}
```

## 8. 功能函式清單

以下清單分為「已有」與「建議新增」。函式命名可調整，但輸入輸出契約應先確定。

## 8.1 App / 狀態 / UI 共用元件

負責人：角色 1，技術驗收由角色 6 協助。

| 函式 | 狀態 | 功能 |
| --- | --- | --- |
| `main()` | 已有 | 初始化 DB、session、路由主頁 |
| `initialize_state()` | 已有 | 建立登入者、選中咖啡廳、API key 等狀態 |
| `inject_mobile_styles()` | 已有 | 套用手機版視覺 |
| `render_mobile_nav()` | 已有 | 顯示探索 / 社群 / 我的等底部導覽 |
| `render_map(cafes)` | 已有 | 顯示咖啡廳地圖 |
| `render_cafe_card(cafe)` | 已有 | 顯示咖啡廳卡片與收藏操作 |
| `render_post_card(post)` | 已有 | 顯示貼文卡片與愛心留言 |
| `format_distance()` | 已有 | 距離顯示格式 |
| `format_tags()` | 已有 | 標籤顯示格式 |

## 8.2 探索頁與 Google API

負責人：角色 2。資料寫入介面由角色 3 提供。

| 函式 | 狀態 | 功能 |
| --- | --- | --- |
| `render_explore_page()` | 已有 | 探索主頁 |
| `sync_search_results(keyword)` | 已有 | 單一搜尋操作在背景呼叫 Google 並同步店家資料 |
| `render_cafe_detail()` | 已有 | 店家詳情與相關貼文 |
| `filtered_cafes()` | 已有 | 現階段 keyword / area / rating / tags 篩選 |
| `search_cafes(keyword, api_key, location, radius)` | 已有 | Google Places 搜尋 |
| `fetch_place_details(place_id, api_key)` | 已有 | Google Place Details |
| `static_map_url(cafes, api_key)` | 已有 | 地圖圖片 URL |
| `apply_explore_filters(filters)` | 建議新增 | 將 UI 篩選整理為查詢條件 |
| `get_cafe_detail_view(cafe_id)` | 建議新增 | 店家資料 + traits + photos + posts |
| `calculate_open_now(opening_hours)` | 未來 | 判斷目前是否營業中 |
| `calculate_distance(origin, cafe)` | 未來 | 真實距離計算 |

建議探索 filters 物件：

```python
{
    "keyword": "",
    "area": "全部",
    "minimum_rating": 4.0,
    "open_now": False,
    "open_late": False,
    "no_time_limit": False,
    "has_outlets": False,
    "quiet": False,
    "study_friendly": False,
    "max_distance_meters": None,
}
```

## 8.3 Schema、咖啡廳 DB 與資料匯入

負責人：角色 3。

| 函式 | 狀態 | 功能 |
| --- | --- | --- |
| `connect()` | 已有 | 依設定連 Supabase PostgreSQL 或本機 SQLite fallback |
| `initialize_database()` | 已有 | 建立 table 與 seed |
| `migrate_existing_tables()` | 已有 | 舊 DB 增欄 |
| `seed_cafes()` | 已有 | 初始咖啡廳資料 |
| `upsert_cafe(cafe)` | 已有 | 寫入 Google / seed 咖啡廳 |
| `list_cafes()` | 已有 | 取得咖啡廳 |
| `get_cafe(cafe_id)` | 已有 | 取得單店 |
| `list_areas()` | 已有 | 篩選地區 |
| `list_all_tags()` | 已有 | 篩選標籤 |
| `create_schema_v2()` | 建議新增 | 建立新增 tables / columns |
| `upsert_cafe_traits(cafe_id, traits)` | 建議新增 | 建立 / 更新特徵 |
| `recalculate_cafe_traits(cafe_id)` | 建議新增 | 從 feedback 彙整 traits |
| `list_cafes_by_filters(filters)` | 建議新增 | DB 層完整篩選查詢 |
| `import_google_cafes(query)` | 建議新增 | 批次取得並匯入可 demo 真實店家 |
| `seed_demo_cafe_traits()` | 建議新增 | 讓 demo 篩選有足夠結果 |

## 8.4 社群頁功能

負責人：角色 4。資料函式由角色 5 實作。

| 函式 | 狀態 | 功能 |
| --- | --- | --- |
| `render_social_page()` | 已有 | 顯示 feed 與發文入口 |
| `render_post_form(cafes)` | 已有 | 發文表單 |
| `save_uploaded_file()` | 已有 | 上傳圖檔儲存 |
| `render_post_detail(post_id)` | 建議新增 | 完整貼文詳情畫面 |
| `render_social_gallery()` | 建議新增 | 縮圖 grid / 瀑布流替代版本 |
| `render_create_post_page()` | 建議新增 | 符合 wireframe 的獨立發文頁 |
| `select_or_import_cafe_for_post()` | 建議新增 | 發文選店，DB 找不到再查 Google |

## 8.5 社群資料庫與 Demo 使用者資料

負責人：角色 5；新增 table 需角色 3 review。

| 函式 | 狀態 | 功能 |
| --- | --- | --- |
| `create_post(...)` | 已有 | 建立單圖貼文、tags、更新店家評分 |
| `list_posts(cafe_id=None)` | 已有 | 顯示 feed / 店家相關貼文 |
| `user_liked_post()` | 已有 | 確認按讚狀態 |
| `toggle_like()` | 已有 | 愛心切換 |
| `add_comment()` | 已有 | 留言 |
| `list_comments()` | 已有 | 留言列表 |
| `refresh_cafe_user_rating()` | 已有 | 站內評分平均 |
| `refresh_cafe_tags()` | 已有 | tag 合併回咖啡廳 |
| `create_post_with_feedback(post, traits, photos)` | 建議新增 | 新增完整貼文、照片、細部評價 |
| `add_post_photo(post_id, path, order)` | 建議新增 | 多張照片 |
| `list_post_photos(post_id)` | 建議新增 | 貼文詳情照片 |
| `list_feed_posts(sort_by)` | 建議新增 | 最新 / 熱門排序 |
| `seed_demo_users_and_posts()` | 建議新增 | Demo 帳號、圖片、按讚、留言 |

## 8.6 個人頁功能與資料庫

負責人：角色 6。

| 函式 | 狀態 | 功能 |
| --- | --- | --- |
| `render_profile_page()` | 已有 | 個人頁 |
| `render_profile_header()` | 已有 | 頭貼、暱稱、統計 |
| `render_profile_editor()` | 已有 | 編輯暱稱、頭貼 |
| `get_or_create_user()` | 已有 | Demo 登入 |
| `get_user()` | 已有 | 個人資料 |
| `update_user_profile()` | 已有 | 更新基本個人檔案 |
| `get_user_stats()` | 已有 | 貼文、探店、收藏統計 |
| `get_favorite_ids()` | 已有 | 收藏狀態 |
| `add_favorite()` | 已有 | 收藏咖啡廳 |
| `remove_favorite()` | 已有 | 取消收藏 |
| `list_favorite_cafes()` | 已有 | 收藏清單 |
| `list_footprint_cafes()` | 已有 | 足跡地圖 |
| `update_user_bio()` | 建議新增 | 編輯個人簡介 |
| `list_user_posts(user_id)` | 建議新增 | 個人貼文 grid，不要由 UI 自行過濾 |
| `list_top_cafes_for_user(user_id)` | 建議新增 | Top 3 探店 |
| `render_profile_tabs()` | 建議新增 | 探店 / 足跡 / 收藏三頁籤 |

## 9. 整體系統邏輯

## 9.1 首次進入與登入

```text
啟動 app
→ initialize_database()
→ 建立 seed 咖啡廳 / demo 資料
→ 使用者輸入帳號名
→ get_or_create_user()
→ 進入探索頁
```

Demo 版本登入原則：

- 不處理密碼。
- 帳號名相同即視為同一個使用者。

## 9.2 探索搜尋流程

```text
使用者輸入搜尋文字
→ 使用者按唯一的搜尋按鈕
→ google_maps.search_cafes()
→ database.upsert_cafe()
→ 合併 cafes、社群評分與標籤後套用篩選
→ 地圖與列表顯示同一批 cafes
```

重要規則：

- 探索頁僅顯示一個搜尋框，不讓使用者選擇「資料庫搜尋」或「Google 搜尋」。
- Supabase PostgreSQL 是共用背景資料層；未設定雲端前才使用 SQLite fallback。
- Google API 結果需先正規化後寫 DB。
- 畫面不直接保存 API raw payload。
- 地圖與結果列表不可各自查不同資料來源，避免畫面不一致。

## 9.3 精細篩選流程

第一階段 Demo：

```text
使用者選 chips / filter
→ filtered_cafes() 依 tags、評分、地區篩選
→ 地圖和列表更新
```

完整版本：

```text
使用者選 chips / filter
→ list_cafes_by_filters(filters)
→ JOIN cafes + cafe_traits
→ 依 traits 分數與 Google 欄位查詢
→ 地圖和列表更新
```

## 9.4 咖啡廳詳情與收藏

```text
使用者點一間咖啡廳
→ get_cafe_detail_view(cafe_id)
→ 顯示店家資訊、照片、標籤、相關貼文

使用者按收藏
→ add_favorite(user_id, cafe_id)
→ 我的頁「已收藏」可看到該店
```

收藏必須一致：

- 從探索頁按書籤。
- 從咖啡廳詳情按書籤。
- 從社群貼文詳情按書籤。

三個入口都寫同一張 `favorites` 表。

## 9.5 社群瀏覽流程

```text
進入社群頁
→ list_feed_posts(sort_by="popular" 或 "latest")
→ 顯示圖片 grid / feed
→ 點縮圖
→ 顯示貼文詳情
→ 可按讚、留言、收藏該咖啡廳
```

wireframe 中收藏 icon 指向店家收藏，所以貼文詳情需要知道 `cafe_id`。

## 9.6 發文流程

```text
使用者按 +
→ 開啟發佈貼文頁
→ 選擇咖啡廳
   → 先查 cafes
   → 找不到則 Google Places 搜尋並匯入
→ 選照片 / 填內文 / 給評分 / 選標籤與 traits
→ create_post_with_feedback()
   → INSERT posts
   → INSERT post_photos 或 posts.image_path
   → INSERT post_tags
   → INSERT post_trait_feedback
   → refresh_cafe_user_rating()
   → recalculate_cafe_traits()
→ 社群頁可看到貼文
→ 個人頁增加探店紀錄與足跡
```

## 9.7 個人頁流程

```text
進入我的頁
→ get_user() + get_user_stats()
→ 顯示頭貼、自介、探店紀錄數、已收藏數
→ 使用者切換：
   探店紀錄：list_user_posts()
   足跡地圖：list_footprint_cafes()
   已收藏：list_favorite_cafes()
→ 編輯個人檔案：update_user_profile() / update_user_bio()
```

## 10. Demo 版本的實作範圍決策

## 10.1 Demo 必須完成

| 功能 | 資料支援 |
| --- | --- |
| 手機版三主頁導覽 | session state |
| 單一搜尋框搜尋並顯示咖啡廳 | `cafes`, Google Places |
| 地圖顯示點位 | `cafes.lat/lng` |
| tags / 評分篩選 | `cafes.tags`, `rating`, `user_rating` |
| 咖啡廳收藏 | `favorites` |
| 發文連結咖啡廳 | `posts.cafe_id` |
| 圖片、內文、評分、標籤 | `posts`, `post_tags` |
| 愛心與留言 | `likes`, `comments` |
| 個人頁貼文數 / 探店數 / 收藏數 | aggregate queries |
| 足跡地圖 | `posts JOIN cafes` |

## 10.2 若時間充足優先新增

| 功能 | 需新增資料 |
| --- | --- |
| 個人簡介 | `users.bio` |
| 使用者回饋轉精細篩選 | `post_trait_feedback`, `cafe_traits` |
| 社群熱門排序 | 現有 `likes` 即可寫新 query |
| 個人頁 tabs | 不需新 schema |
| Demo 帳號與互動資料 | seed scripts |

## 10.3 可明確列為 Future Work

- 追蹤其他使用者。
- 貼文多張照片拖曳排序。
- 真正圖片 carousel。
- 原生地圖 marker 點擊互動。
- 使用者即時定位與步行時間。
- 貼文收藏。

## 11. 各角色第一週交付物

| 角色 | 交付物 |
| --- | --- |
| UI / UX / 驗收 | Figma 最終版、共用元件樣式表、完整 demo click-through 流程 |
| 探索功能 | 探索頁、詳情頁、篩選條件 UI 與 API 搜尋成功 |
| Schema / 探索 DB | schema v2 文件與 migration、真實咖啡廳匯入資料、可篩選 seed |
| 社群功能 | 社群瀏覽、貼文詳情、發文表單流程 |
| 社群 DB / Demo data | demo users、posts、images、likes、comments 與 repository 函式 |
| 個人頁 | 個人資料、三頁籤、足跡與收藏資料呈現 |

## 12. Pull Request 邊界

為避免大家用 AI 修改到彼此檔案，PR 必須遵守：

```text
UI owner：styles.py / components.py / docs UI 部分
探索功能：pages/explore.py / filters.py / google_maps.py
Schema owner：database schema / migration / seed_data / import scripts
社群功能：pages/social.py / 貼文相關 component
社群資料：database 社群函式 / demo seeds
個人頁：pages/profile.py / 個人與收藏 query
```

若修改 `database.py`：

- PR 描述必須寫「新增 / 修改哪些函式」。
- 若動到 table 或 column，必須由 schema owner review。
- 禁止直接刪除使用者本機資料庫作為 migration 方法。
