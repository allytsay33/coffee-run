# Coffee Run 現行資料庫 Schema

版本基準：本機 mobile-first 工作版本  
最後更新：2026-05-23  
資料庫引擎：SQLite  
Schema 實作來源：`database.py`

## 1. 文件範圍

本文件描述**目前程式已實作、啟動時會建立或維護的資料表**，供六人小組協作與 Demo 測試使用。

目前資料庫已支援：

- 簡易帳號登入與個人基本資料。
- 咖啡廳 seed data 與 Google Places 匯入資料。
- 咖啡廳收藏。
- 社群貼文、單張圖片、評分、標籤。
- 愛心與留言。
- 個人頁貼文數、探店數、收藏數。
- 足跡地圖資料查詢。

目前尚未實作到資料庫的 wireframe 延伸需求：

- 個人簡介 `bio`。
- 多張貼文圖片與圖片排序。
- 店家照片相簿。
- 結構化精細篩選統計，例如插座票數、不限時可信度、安靜分數。
- 貼文收藏。

## 2. 資料庫生命週期

資料庫檔案位置：

```text
data/coffee_run.db
```

啟動順序：

```text
app.py main()
→ database.initialize_database()
→ CREATE TABLE IF NOT EXISTS
→ migrate_existing_tables()
→ seed_cafes()
```

重要行為：

- `initialize_database()` 不會刪除既有使用者資料。
- `migrate_existing_tables()` 用於舊版資料庫補欄位。
- `seed_cafes()` 使用 `ON CONFLICT DO NOTHING`，不會覆蓋同 `cafe_id` 的既有店家。
- 本機現有 `.db` 可能是較早版本建立後逐步 migration，因此欄位順序或部分 default metadata 可能和全新建立資料庫略不同，但目前程式使用的欄位集合一致。

## 3. ER 關聯摘要

```text
users
 ├──< favorites >── cafes
 ├──< reviews   >── cafes
 ├──< posts     >── cafes
 │      └──< post_tags
 │      ├──< comments >── users
 │      └──< likes    >── users
```

關聯說明：

- 一位使用者可以收藏多間咖啡廳；一間咖啡廳也可被多人收藏。
- 一篇貼文一定屬於一位使用者和一間咖啡廳。
- 貼文可以有多個標籤、多則留言、多個愛心。
- `reviews` 是早期筆記 / 評分資料表，目前社群主流程以 `posts.rating` 為主，但計算使用者平均評分時兩者都會被納入。

## 4. 現行完整 SQL Schema

以下 SQL 對應 `database.initialize_database()` 的新建資料庫定義。

```sql
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    avatar_path TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cafes (
    cafe_id TEXT PRIMARY KEY,
    google_place_id TEXT UNIQUE,
    name TEXT NOT NULL,
    area TEXT NOT NULL,
    address TEXT NOT NULL,
    distance_meters INTEGER NOT NULL DEFAULT 0,
    lat REAL,
    lng REAL,
    rating REAL NOT NULL DEFAULT 0,
    user_rating REAL NOT NULL DEFAULT 0,
    tags TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    opening_hours TEXT NOT NULL DEFAULT '',
    website TEXT NOT NULL DEFAULT '',
    maps_url TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'seed',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL,
    cafe_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, cafe_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    cafe_id TEXT NOT NULL,
    rating INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);

CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    cafe_id TEXT NOT NULL,
    content TEXT NOT NULL,
    rating INTEGER NOT NULL,
    image_path TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);

CREATE TABLE IF NOT EXISTS post_tags (
    post_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (post_id, tag),
    FOREIGN KEY (post_id) REFERENCES posts (post_id)
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS likes (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
```

## 5. 資料表逐表說明

## 5.1 `users`

用途：儲存登入使用者與個人頁資料。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `user_id` | INTEGER | PK, auto increment | 其他資料表引用的使用者識別碼 |
| `username` | TEXT | NOT NULL, UNIQUE | 簡易登入時輸入的帳號名 |
| `display_name` | TEXT | 可空 | 個人頁顯示暱稱 |
| `avatar_path` | TEXT | 可空 | 頭貼本機檔案路徑 |
| `created_at` | TEXT | NOT NULL, default now | 建立帳號時間 |

目前使用情境：

- 使用者輸入帳號名後，若不存在即新增。
- 個人頁可更新 `display_name` 和 `avatar_path`。

尚缺 wireframe 需求：

- 個人簡介欄位 `bio`。

## 5.2 `cafes`

用途：咖啡廳主檔；探索頁、地圖、收藏、貼文與足跡都依賴此表。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `cafe_id` | TEXT | PK | 系統店家 ID；Google 資料使用 `google-{place_id}` |
| `google_place_id` | TEXT | UNIQUE, 可空 | Google Places 店家 ID |
| `name` | TEXT | NOT NULL | 店名 |
| `area` | TEXT | NOT NULL | 篩選使用的地區名稱 |
| `address` | TEXT | NOT NULL | 地址 |
| `distance_meters` | INTEGER | default 0 | 距離顯示；目前 Google 匯入預設為 0 |
| `lat` | REAL | 可空 | 地圖緯度 |
| `lng` | REAL | 可空 | 地圖經度 |
| `rating` | REAL | default 0 | Google 評分 |
| `user_rating` | REAL | default 0 | 站內 reviews 與 posts 評分平均 |
| `tags` | TEXT | default empty | 逗號分隔標籤，供目前篩選使用 |
| `description` | TEXT | default empty | 列表 / 詳情簡介 |
| `opening_hours` | TEXT | default empty | 營業時間文字 |
| `website` | TEXT | default empty | 官方網站 |
| `maps_url` | TEXT | default empty | Google Maps 外連 |
| `source` | TEXT | default `seed` | `seed`、`google_places` 或 `manual` |
| `created_at` | TEXT | default now | 資料建立時間 |

資料來源：

- `seed_data.py`：首次啟動的範例咖啡廳。
- `google_maps.search_cafes()`：Google Places 搜尋結果。
- `google_maps.fetch_place_details()`：同步詳細欄位。
- `refresh_cafe_tags()` / `refresh_cafe_user_rating()`：發文後補充站內資料。

限制：

- `tags` 目前為簡化字串資料，適合 Demo，但還不能可靠代表多人投票後的精細篩選結果。

## 5.3 `favorites`

用途：記錄使用者收藏的**咖啡廳**。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `user_id` | INTEGER | PK part, FK | 收藏者 |
| `cafe_id` | TEXT | PK part, FK | 收藏的咖啡廳 |
| `created_at` | TEXT | default now | 收藏時間 |

複合主鍵 `(user_id, cafe_id)` 可防止同一使用者重複收藏同一間店。

寫入入口：

- 探索頁咖啡廳卡片。
- 個人頁收藏列表中的取消收藏。

預計 wireframe 入口：

- 社群貼文詳情的書籤按鈕，也應寫入此表，因為設計中收藏對象是咖啡廳。

## 5.4 `reviews`

用途：舊版咖啡筆記與評分資料。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `review_id` | INTEGER | PK, auto increment | 評分紀錄 ID |
| `user_id` | INTEGER | FK | 評分者 |
| `cafe_id` | TEXT | FK | 評分店家 |
| `rating` | INTEGER | NOT NULL | 評分 |
| `note` | TEXT | NOT NULL | 心得 |
| `created_at` | TEXT | default now | 建立時間 |

現況決策：

- 表仍保留，避免舊資料遺失。
- 手機 wireframe 的新發文流程主要寫入 `posts`。
- `refresh_cafe_user_rating()` 仍把 `reviews.rating` 與 `posts.rating` 一起平均。

## 5.5 `posts`

用途：社群探店貼文，也是個人探店紀錄和足跡來源。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `post_id` | INTEGER | PK, auto increment | 貼文 ID |
| `user_id` | INTEGER | FK, NOT NULL | 貼文作者 |
| `cafe_id` | TEXT | FK, NOT NULL | 貼文指定的咖啡廳 |
| `content` | TEXT | NOT NULL | 內文 |
| `rating` | INTEGER | NOT NULL | 使用者給店家的 1 至 5 評分 |
| `image_path` | TEXT | 可空 | 單張上傳圖片本機路徑 |
| `created_at` | TEXT | default now | 發文時間 |

核心規則：

- 一篇貼文一定要連結一間咖啡廳。
- 目前支援單張圖片；多圖需新增資料表。
- 新增貼文後會更新該店 `user_rating` 和 `tags`。

## 5.6 `post_tags`

用途：記錄貼文補充的篩選標籤。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `post_id` | INTEGER | PK part, FK | 對應貼文 |
| `tag` | TEXT | PK part | 標籤文字 |

現行標籤來源：

```text
安靜、插座、不限時、適合讀書、適合聊天、甜點、平價、晚上營業、學生友善
```

資料回寫流程：

```text
create_post()
→ INSERT post_tags
→ refresh_cafe_tags()
→ 合併至 cafes.tags
→ 探索頁可用此標籤篩選
```

## 5.7 `comments`

用途：貼文留言。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `comment_id` | INTEGER | PK, auto increment | 留言 ID |
| `post_id` | INTEGER | FK | 對應貼文 |
| `user_id` | INTEGER | FK | 留言者 |
| `content` | TEXT | NOT NULL | 留言內容 |
| `created_at` | TEXT | default now | 留言時間 |

## 5.8 `likes`

用途：貼文愛心。

| 欄位 | 型別 | 條件 | 用途 |
| --- | --- | --- | --- |
| `post_id` | INTEGER | PK part, FK | 被按讚貼文 |
| `user_id` | INTEGER | PK part, FK | 按讚使用者 |
| `created_at` | TEXT | default now | 按讚時間 |

複合主鍵 `(post_id, user_id)` 可保證一人對同一貼文最多一個愛心。

## 6. 現行查詢與更新流程

## 6.1 Google 店家匯入

```text
探索頁輸入搜尋
→ google_maps.search_cafes()
→ 回傳標準 cafe dict
→ database.upsert_cafe()
→ cafes 新增或更新
→ 探索列表 / 地圖顯示
```

## 6.2 發文補充篩選資料

```text
使用者選店、輸入文字、評分、標籤與圖片
→ database.create_post()
→ INSERT posts
→ INSERT post_tags
→ refresh_cafe_user_rating()
→ refresh_cafe_tags()
→ 探索頁列表可使用新評分與標籤
```

## 6.3 收藏與個人頁

```text
按收藏
→ INSERT favorites
→ 個人頁 list_favorite_cafes()

發文
→ posts 有 cafe_id
→ 個人頁 list_footprint_cafes()
→ 足跡地圖出現該店
```

## 7. 目前 DB 函式清單

| 函式 | 作用 |
| --- | --- |
| `connect()` | 開啟 SQLite connection |
| `initialize_database()` | 建立 tables、migration、seed |
| `migrate_existing_tables(connection)` | 舊資料庫補欄位 |
| `seed_cafes(connection)` | 建立示範咖啡廳 |
| `split_tags(tags)` | 標籤字串轉 list |
| `row_to_cafe(row)` | DB row 轉頁面使用 dict |
| `get_or_create_user(username)` | 簡易登入 / 建使用者 |
| `update_user_profile(user_id, display_name, avatar_path)` | 更新暱稱與頭貼 |
| `get_user(user_id)` | 取使用者資料 |
| `upsert_cafe(cafe)` | 建立或同步咖啡廳 |
| `list_cafes()` | 咖啡廳列表排序 |
| `get_cafe(cafe_id)` | 單一咖啡廳詳情 |
| `list_areas()` | 地區篩選選項 |
| `list_all_tags()` | 標籤篩選選項 |
| `get_favorite_ids(user_id)` | 使用者收藏狀態集合 |
| `add_favorite(user_id, cafe_id)` | 新增收藏 |
| `remove_favorite(user_id, cafe_id)` | 取消收藏 |
| `list_favorite_cafes(user_id)` | 個人收藏清單 |
| `add_review(...)` | 新增舊版 review |
| `list_reviews(user_id)` | 查舊版 reviews |
| `create_post(...)` | 新增貼文並更新店家衍生資訊 |
| `list_posts(cafe_id=None)` | 取得全部或指定店家貼文 |
| `user_liked_post(user_id, post_id)` | 讀愛心狀態 |
| `toggle_like(user_id, post_id)` | 切換愛心 |
| `add_comment(user_id, post_id, content)` | 新增留言 |
| `list_comments(post_id)` | 取得留言 |
| `refresh_cafe_user_rating(cafe_id)` | 重算站內平均評分 |
| `refresh_cafe_tags(cafe_id)` | 將貼文標籤彙整至咖啡廳 |
| `get_user_stats(user_id)` | 個人頁統計 |
| `list_footprint_cafes(user_id)` | 個人足跡地圖資料 |

## 8. 尚未實作但已確認需要的 Schema 擴充

以下不是目前程式既有資料表，不可誤認為已完成。

| 延伸需求 | 建議資料表 / 欄位 | 優先級 |
| --- | --- | --- |
| 個人簡介 | `users.bio` | 中 |
| 精細篩選統計 | `cafe_traits` | 高，若要完整呈現篩選產品價值 |
| 每篇貼文結構化回饋 | `post_trait_feedback` | 高，與 `cafe_traits` 搭配 |
| 多張貼文圖片 | `post_photos` | 中 |
| 店家縮圖相簿 | `cafe_photos` | 中 |

詳細目標 schema 與分工提案見：

- `docs/09_schema_function_contracts_and_ownership.md`

