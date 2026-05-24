# Coffee Run 完整資料庫 Schema

更新日期：2026-05-24  
實作來源：`database.py`  
資料庫：設定 `SUPABASE_DB_URL` 時使用 Supabase PostgreSQL；未設定時 fallback 至本機 SQLite。啟動 `app.py` 時自動建立與 migration，不需要手動貼建表 SQL。

探索頁只有一個使用者可見的搜尋框。按下搜尋後，系統在背景呼叫 Google Places 並更新 `cafes`；資料庫用來合併店家資料與社群產生的評分、標籤及篩選特徵，不是另一個搜尋介面。

## 1. 關聯概要

```text
users
 ├── posts ── cafes ── cafe_traits
 │     ├── post_photos
 │     ├── post_tags
 │     ├── post_trait_feedback
 │     ├── comments ── users
 │     └── likes ── users
 ├── favorites ── cafes
 └── reviews ── cafes   (保留舊資料相容性)
```

## 2. 完整 SQL Schema

```sql
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    avatar_path TEXT,
    bio TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
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
    open_now INTEGER,
    website TEXT NOT NULL DEFAULT '',
    maps_url TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'seed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER NOT NULL,
    cafe_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, cafe_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);

CREATE TABLE IF NOT EXISTS posts (
    post_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    cafe_id TEXT NOT NULL,
    content TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    image_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);

CREATE TABLE IF NOT EXISTS post_photos (
    photo_id BIGSERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (post_id)
);

CREATE TABLE IF NOT EXISTS post_tags (
    post_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (post_id, tag),
    FOREIGN KEY (post_id) REFERENCES posts (post_id)
);

CREATE TABLE IF NOT EXISTS post_trait_feedback (
    post_id INTEGER PRIMARY KEY,
    cafe_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    has_outlets INTEGER,
    no_time_limit INTEGER,
    quiet_score INTEGER,
    study_score INTEGER,
    chat_score INTEGER,
    dessert_score INTEGER,
    price_score INTEGER,
    open_late INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

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
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id BIGSERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS likes (
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id),
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    cafe_id TEXT NOT NULL,
    rating INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (cafe_id) REFERENCES cafes (cafe_id)
);
```

## 3. 資料表功能

| 資料表 | 功能 | 寫入時機 |
| --- | --- | --- |
| `users` | 帳號、暱稱、頭貼、個人簡介 | 登入、編輯個人檔案 |
| `cafes` | 地圖與店家主資料 | seed、Google Places 搜尋 / 同步 |
| `favorites` | 收藏咖啡廳 | 探索詳情或貼文詳情按收藏 |
| `posts` | 探店貼文、評分、主圖片相容欄位 | 發布探店紀錄 |
| `post_photos` | 多張貼文圖片與顯示順序 | 發布多張照片 |
| `post_tags` | 顯示及快速搜尋的標籤 | 發文選標籤 |
| `post_trait_feedback` | 每篇貼文的結構化回饋 | 發文補充插座、安靜等資訊 |
| `cafe_traits` | 店家彙整後的精細篩選資料 | seed 與發文後重新彙整 |
| `comments` | 貼文留言 | 貼文詳情留言 |
| `likes` | 貼文愛心 | 愛心切換 |
| `reviews` | 舊版評分相容表 | 舊資料保留 |

## 4. 重要欄位規則

### `cafes`

- `rating`：Google 評分。
- `user_rating`：站內 `posts.rating` 與舊 `reviews.rating` 平均。
- `tags`：文字標籤快取，供目前頁面顯示與簡易搜尋。
- `open_now`：Google 最近查詢回傳的營業狀態，`1` 為營業、`0` 為未營業、`NULL` 為未知。
- `source`：資料來源，通常為 `seed` 或 `google_places`。

### `posts` / `post_photos`

- 每篇貼文必須連結 `cafe_id`。
- `posts.image_path` 保留第一張圖片以相容舊貼文。
- `post_photos` 提供 wireframe 需要的多圖顯示。

### `favorites`

- 收藏對象是咖啡廳而非貼文。
- 同一使用者收藏同一咖啡廳只會有一筆資料。

### `post_trait_feedback` / `cafe_traits`

發文細節寫入後的流程：

```text
post_trait_feedback
→ refresh_cafe_traits(cafe_id)
→ cafe_traits 內保存平均 / 比例
→ 探索快速篩選使用 cafe_traits
```

特徵定義：

| 特徵 | feedback 原始值 | cafe_traits 彙整值 |
| --- | --- | --- |
| 插座多 | `0` / `1` | `has_outlets_score` 平均 |
| 不限時 | `0` / `1` | `no_time_limit_score` 平均 |
| 深夜咖啡廳 | `0` / `1` | `open_late_score` 平均 |
| 安靜 | 1 至 5 | `quiet_score` 平均 |
| 適合讀書 | 1 至 5 | `study_score` 平均 |
| 適合聊天 | 1 至 5 | `chat_score` 平均 |

## 5. 畫面與資料表對應

| 畫面 | 主要讀取 | 主要寫入 |
| --- | --- | --- |
| 探索地圖 | `cafes`, `cafe_traits` | Google 匯入寫入 `cafes` |
| 精細篩選 | `cafes`, `cafe_traits` | 無 |
| 咖啡廳詳情 | `cafes`, `post_photos`, `posts` | `favorites` |
| 社群圖牆 | `posts`, `post_photos` | 無 |
| 貼文詳情 | `posts`, `post_photos`, `comments`, `likes` | `favorites`, `likes`, `comments` |
| 發布貼文 | `cafes` | `posts`, `post_photos`, `post_tags`, `post_trait_feedback`, `cafe_traits` |
| 我的探店 | `users`, `posts` | 無 |
| 足跡地圖 | `posts JOIN cafes` | 無 |
| 已收藏 | `favorites JOIN cafes` | 刪除 `favorites` |
| 編輯個人檔案 | `users` | `users` |

## 6. Migration 說明

既有舊版資料庫啟動後會自動：

- 在 `users` 增加 `bio`。
- 在 `cafes` 增加 `open_now` 與 `updated_at`。
- 建立 `post_photos`。
- 建立 `post_trait_feedback`。
- 建立 `cafe_traits`。
- 為 seed 咖啡廳產生初始特徵，讓篩選器可立即展示。
- 建立少量示範使用者與文字探店貼文，讓全新安裝也能查看社群互動流程。
