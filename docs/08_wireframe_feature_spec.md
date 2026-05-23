# Coffee Run Wireframe 功能規格

最後更新：2026-05-23

本文件依照目前 Figma / 截圖 wireframe 整理 Coffee Run 手機版功能。內容包含三大主頁：「探索」、「社群」、「我的」，以及篩選、發文、個人檔案、收藏、足跡地圖等子流程。

## 1. 產品主架構

Coffee Run 採手機版 app 體驗設計，底部固定三個主導航：

```text
探索
社群
我的
```

### 1.1 三個主功能

- 探索：搜尋咖啡廳、地圖瀏覽、篩選條件、查看搜尋結果、收藏咖啡廳。
- 社群：瀏覽探店貼文、查看貼文詳情、發佈探店紀錄。
- 我的：查看個人資料、探店紀錄、足跡地圖、已收藏咖啡廳、編輯個人檔案。

### 1.2 核心資料流

```text
Google Map / Places API
→ 取得咖啡廳資料
→ 存入資料庫 cafes
→ 探索頁顯示地圖與搜尋結果
→ 使用者收藏 / 發文
→ favorites / posts / post_tags / cafe_traits 更新
→ 個人頁與社群頁同步顯示
```

## 2. 探索頁功能

探索頁是使用者進 app 後的主要入口，負責咖啡廳搜尋、地圖展示與篩選。

## 2.1 探索初始頁

畫面元素：

- 頁面標題：探索咖啡廳。
- 搜尋列：提示文字「在這裡搜尋...」。
- 快速篩選 chips：
  - 營業中
  - 深夜咖啡廳
  - 不限時
  - 插座多
- 更多篩選按鈕。
- 地圖區塊。
- 地圖 marker。
- 底部導航列。

### 2.1.1 搜尋列

使用者可輸入：

```text
內湖的咖啡廳
台大附近咖啡廳
不限時咖啡廳
插座多咖啡廳
深夜咖啡廳
```

按搜尋後：

1. 先查本機資料庫是否已有符合資料。
2. 若本機資料不足，呼叫 Google Places API。
3. 將 Google 回傳結果寫入資料庫。
4. 更新地圖 marker。
5. 更新搜尋結果列表。

### 2.1.2 地圖顯示

地圖需要顯示：

- 目前搜尋區域。
- 咖啡廳 marker。
- marker 上可顯示簡化資訊，例如：
  - 咖啡 icon
  - 評分
  - 店名摘要

Demo 可先做：

- 使用 Google Static Maps 或 Streamlit map 顯示 marker。
- 點搜尋結果列表查看詳情。

Future work：

- marker 可點擊。
- 點 marker 展開店家 preview。
- 地圖可左右 / 上下滑動。
- 地圖與列表完全連動。

### 2.1.3 快速篩選 chips

篩選條件由負責探索頁的組員與資料庫組共同決定。初版建議：

```text
營業中
深夜咖啡廳
不限時
插座多
安靜
適合讀書
甜點
平價
```

互動規則：

- chip 可多選。
- 已選 chip 顯示高亮。
- 再點一次取消。
- 篩選後地圖與列表同時更新。

資料來源：

- Google Places API：店名、地址、營業時間、Google 評分。
- 資料庫 seed / 匯入資料：初始標籤。
- 使用者發文：補充標籤與評分。
- cafe_traits 統計資料：插座、不限時、安靜程度等。

## 2.2 地圖篩選頁

wireframe 中有「地圖篩選」頁面，負責較完整的精細篩選。

### 2.2.1 頁面元素

- 返回 / 取消按鈕。
- 套用按鈕。
- 篩選分類：
  - 營業狀態
  - 評分篩選
  - 距離篩選
  - 咖啡廳特色
  - 快速篩選

### 2.2.2 建議篩選欄位

營業狀態：

- 只看營業中。
- 只看深夜營業。

評分：

- 最低 3.0。
- 最低 4.0。
- 最低 4.5。

距離：

- 500 公尺內。
- 1 公里內。
- 3 公里內。

咖啡廳特色：

- 不限時。
- 插座多。
- 安靜。
- 適合讀書。
- 適合聊天。
- 有甜點。
- 平價。

### 2.2.3 篩選結果互動

按「套用」後：

```text
篩選條件
→ 查詢資料庫 / Google API 已存結果
→ 更新搜尋結果
→ 更新地圖 marker
→ 回到探索結果頁
```

按「取消」後：

- 不改變原本篩選條件。
- 回到探索頁。

### 2.2.4 資料庫需求

需要能支援：

```text
cafes.opening_hours
cafes.rating
cafes.user_rating
cafes.tags
cafe_traits.has_outlets
cafe_traits.no_time_limit
cafe_traits.quiet_score
cafe_traits.study_score
cafe_traits.chat_score
cafe_traits.price_score
```

Demo 可先做：

- tags-based 篩選。
- 評分篩選。
- 地區篩選。

Future work：

- 真正計算「目前營業中」。
- 用使用者位置算距離。
- cafe_traits 統計表。

## 2.3 探索搜尋結果頁

搜尋後畫面顯示：

- 上方搜尋列保留搜尋關鍵字。
- 地圖顯示搜尋範圍與 marker。
- 下方顯示「搜尋結果」。
- 結果列表可垂直滑動。

### 2.3.1 搜尋結果卡片

每張卡片顯示：

```text
店名
Google / 使用者評分
步行距離
關閉時間 / 營業時間
照片縮圖
收藏按鈕
```

wireframe 參考：

```text
Angelina
4.3 ★｜走路 2 分鐘｜關閉時間：下午11:00
照片 1 / 照片 2 / 照片 3
收藏 icon
```

互動：

- 點卡片：展開搜尋結果詳情。
- 點收藏 icon：加入 / 移除收藏。
- 收藏後資料寫入 `favorites`。

## 2.4 搜尋結果展開頁

wireframe 中有搜尋結果展開頁，可視為咖啡廳詳情頁。

### 2.4.1 頁面元素

- 店名。
- 評分。
- 距離。
- 營業時間。
- 收藏 icon。
- 店家圖片區。
- 使用者貼文 preview。
- 評分與標籤。
- Google Map 查看按鈕。

### 2.4.2 可左右滑動圖片

wireframe 標註圖片區可左右滑動。

Demo 可先做：

- 顯示單張圖片或多張圖片垂直排列。

Future work：

- 橫向圖片 carousel。
- 支援多張店家照片。
- 串 Google Place Photos API。

### 2.4.3 社群貼文連結

此頁應顯示和該咖啡廳相關的社群貼文。

資料來源：

```text
posts WHERE cafe_id = current_cafe_id
```

排序方式：

- 初版：最新貼文優先。
- 可選：按讚數最高優先。

### 2.4.4 Google Maps 連結

按「在 Google Map 中查看」：

- 開啟該店 Google Maps URL。

此功能目前 AI 不一定能自動生成完整體驗，若時間不足可列為 future work。

## 3. 社群頁功能

社群頁負責瀏覽其他使用者探店貼文，也提供發文入口。

## 3.1 社群初始頁

畫面元素：

- 搜尋列。
- 發文按鈕 `+`。
- 多欄瀑布流貼文縮圖。
- 底部導航列。

### 3.1.1 貼文縮圖瀑布流

wireframe 顯示類似 Pinterest / Instagram explore 的貼文縮圖牆。

每個縮圖：

- 顯示貼文首圖。
- 可有不同高度，形成瀑布流。
- 點擊後進入貼文詳情頁。

Demo 可先做：

- 一欄或三欄圖片 grid。
- 使用現有 posts 的 image_path。

Future work：

- Masonry layout。
- 無限下滑載入。
- 熱門貼文排序。

### 3.1.2 社群搜尋

搜尋列可搜尋：

- 咖啡廳名稱。
- 使用者名稱。
- 標籤。
- 貼文內文。

Demo 可先做：

- 搜尋咖啡廳名稱 / 內文。

### 3.1.3 發文按鈕

點 `+`：

- 進入「發佈貼文頁面」。

## 3.2 瀏覽貼文頁

點選社群貼文後進入貼文詳情。

### 3.2.1 頁面元素

- 咖啡廳名稱。
- 標籤 chips。
- 收藏咖啡廳 icon。
- 貼文圖片。
- 愛心數。
- 留言數。
- 使用者名稱。
- 內文。
- 評分。

wireframe 參考：

```text
咖啡廳名稱
深夜咖啡廳 / 不限時 / 插座多
貼文圖片
♡ 201   💬 30
使用者名稱
內文
4.3 ★
```

### 3.2.2 收藏功能

wireframe 標註：

使用者可儲存咖啡廳，此資料需存放至資料庫供個人頁「收藏清單」使用。

功能：

- 點收藏 icon。
- 若未收藏：新增 `favorites`。
- 若已收藏：取消收藏。
- 個人頁收藏清單即時可查。

注意：

- 此處收藏的是「咖啡廳」，不是貼文。
- 如果未來要收藏貼文，需新增 `post_favorites`。

### 3.2.3 按讚與留言

按讚：

- 寫入 `likes`。
- 再點取消。

留言：

- 寫入 `comments`。
- 顯示留言數。

排序：

- 社群初始頁可優先顯示按讚數高的貼文。

## 3.3 發佈貼文頁

發文是社群與探索資料補充的核心。

### 3.3.1 頁面元素

- 返回首頁 / 取消按鈕。
- 標題：探店紀錄。
- 選擇咖啡廳欄位。
- 選擇照片欄位。
- 已選照片 preview。
- 編輯內文。
- 咖啡廳評分。
- 咖啡廳細節標籤。
- 發布按鈕。

### 3.3.2 選擇咖啡廳

流程：

1. 使用者輸入或選擇咖啡廳。
2. 系統先查資料庫 `cafes`。
3. 若找不到，再呼叫 Google Map / Places API。
4. 若仍找不到，顯示：

```text
查無此咖啡廳
```

資料庫需求：

- 發文一定要有 `cafe_id`。
- 不允許沒有咖啡廳的貼文。

### 3.3.3 選擇照片

功能：

- 上傳一張或多張照片。
- 顯示已選照片 preview。
- 可調整照片順序。

Demo 可先做：

- 單張照片上傳。

Future work：

- 多張照片。
- 拖曳排序。
- 相簿管理。

### 3.3.4 內文

使用者可輸入探店心得。

欄位：

```text
content
```

驗證：

- 不能空白。

### 3.3.5 評分

使用者可給咖啡廳評分。

欄位：

```text
rating 1-5
```

送出後：

- 寫入 `posts.rating`。
- 重新計算 `cafes.user_rating`。

### 3.3.6 標籤

標籤選項應由資料庫負責人整理，不建議完全依賴 AI 生成。

建議初始標籤：

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

送出後：

- 寫入 `post_tags`。
- 合併回 `cafes.tags`。
- 未來可更新 `cafe_traits`。

## 4. 我的頁功能

我的頁負責個人資料、探店紀錄、足跡地圖與收藏。

## 4.1 個人首頁

畫面元素：

- 帳號名。
- 頭貼。
- 自介。
- 探店紀錄數。
- 已收藏數。
- 編輯個人檔案按鈕。
- 分享個人檔案按鈕。
- 設定按鈕。
- 分頁 icon：
  - 探店紀錄
  - 足跡地圖
  - 已收藏
- 貼文 grid。
- 底部導航。

### 4.1.1 個人統計

顯示：

```text
探店紀錄：30
已收藏：10
```

資料來源：

- 探店紀錄：`COUNT(posts WHERE user_id = current_user)`
- 已收藏：`COUNT(favorites WHERE user_id = current_user)`

### 4.1.2 探店紀錄

顯示使用者發過的貼文。

可顯示：

- Top 3 咖啡廳。
- 最近貼文 grid。
- 每篇貼文首圖。

Demo 可先做：

- 顯示我的貼文列表。

Future work：

- 圖片 grid。
- Top 3 自動統計。

## 4.2 足跡地圖

畫面元素：

- 個人資料區。
- 分頁 icon 選到足跡地圖。
- 地圖。

功能：

- 將使用者發過文的咖啡廳顯示在地圖上。
- 資料來源：

```text
SELECT DISTINCT cafes.*
FROM posts
JOIN cafes ON posts.cafe_id = cafes.cafe_id
WHERE posts.user_id = current_user
```

Demo 已可做：

- 用現有 `list_footprint_cafes()` 顯示地圖。

## 4.3 已收藏

畫面元素：

- 個人資料區。
- 分頁 icon 選到已收藏。
- 地圖。
- 已收藏咖啡廳列表。

功能：

- 顯示使用者已收藏的咖啡廳。
- 地圖顯示收藏咖啡廳位置。
- 可取消收藏。

資料來源：

```text
favorites
JOIN cafes
```

## 4.4 編輯個人檔案

畫面元素：

- 標題：編輯個人檔案。
- 頭貼。
- 修改頭貼按鈕。
- 用戶名欄位。
- 個人簡介欄位。
- 底部導航。

功能：

- 修改頭貼。
- 修改用戶名 / 暱稱。
- 修改個人簡介。

目前資料庫已有：

```text
users.username
users.display_name
users.avatar_path
```

建議新增：

```text
users.bio
```

Demo 可先做：

- 修改暱稱。
- 修改頭貼。

Future work：

- 修改個人簡介。
- 分享個人檔案。
- 更完整帳號系統。

## 5. 資料庫需求整理

## 5.1 目前已有資料表

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

## 5.2 建議新增資料表 / 欄位

### users 新增欄位

```text
bio TEXT DEFAULT ''
```

### cafe_traits

支援精細篩選。

```text
cafe_id TEXT PRIMARY KEY
has_outlets_score REAL
no_time_limit_score REAL
quiet_score REAL
study_score REAL
chat_score REAL
price_score REAL
dessert_score REAL
open_late_score REAL
updated_at TEXT
```

### post_photos

若支援多張照片。

```text
photo_id INTEGER PRIMARY KEY
post_id INTEGER
image_path TEXT
sort_order INTEGER
created_at TEXT
```

### post_trait_feedback

保留每篇貼文對咖啡廳特徵的回饋。

```text
post_id INTEGER
cafe_id TEXT
user_id INTEGER
has_outlets INTEGER
no_time_limit INTEGER
quiet_score INTEGER
study_score INTEGER
chat_score INTEGER
price_score INTEGER
dessert_score INTEGER
open_late INTEGER
created_at TEXT
```

## 6. Demo 優先順序

## 6.1 必做

- 探索頁手機版。
- Google Places 搜尋咖啡廳。
- 地圖顯示咖啡廳。
- 快速篩選 chips。
- 搜尋結果列表。
- 收藏咖啡廳。
- 社群貼文 feed。
- 發文必須連結咖啡廳。
- 上傳圖片。
- 評分與標籤。
- 個人頁顯示貼文數、收藏數。
- 足跡地圖。
- 收藏清單。

## 6.2 可以簡化

- 圖片左右滑動：先單張或多張垂直顯示。
- 社群瀑布流：先 grid 或一欄 feed。
- 地圖 marker 點擊：先用列表點詳情。
- 追蹤功能：暫不做。
- 分享個人檔案：暫不做。

## 6.3 Future work

- 多張照片排序。
- 貼文收藏。
- 追蹤使用者。
- 真正互動式 Google Map marker。
- Google Place Photos API。
- 根據目前時間判斷營業中。
- 使用者定位與距離計算。
- 原生 app 版本。

## 7. 六人分工建議

### 你：UI / UX / Wireframe Owner

負責：

- 所有手機版頁面 wireframe。
- 視覺風格。
- 共用元件規格。
- 檢查各組做出來是否符合設計。

主要協作檔案：

- `styles.py`
- `components.py`
- Figma 文件

### A：探索 + 地圖 + 篩選

負責：

- 探索初始頁。
- 搜尋結果頁。
- 搜尋結果展開頁。
- 地圖與篩選連動。
- Google API 使用。

主要檔案：

- `pages/explore.py`
- `filters.py`
- `google_maps.py`

### B：社群 + 發文

負責：

- 社群初始頁。
- 貼文詳情頁。
- 發文頁。
- 圖片上傳。
- 愛心 / 留言。

主要檔案：

- `pages/social.py`
- `components.py` 的 post card
- `file_storage.py`

### C：我的頁 + 個人檔案

負責：

- 個人首頁。
- 探店紀錄。
- 足跡地圖。
- 已收藏。
- 編輯個人檔案。

主要檔案：

- `pages/profile.py`
- `pages/ranking.py`

### D：資料庫 + Schema + Demo Data

負責：

- 建資料表。
- 寫 schema 文件。
- seed data。
- demo 測試資料。
- 若做爬蟲 / 匯入，也由此人主責資料格式。

主要檔案：

- `database.py`
- `seed_data.py`
- schema 文件

### E：整合測試 + Git + 簡報錄影

負責：

- GitHub branch / PR 管理。
- 合併前測試。
- README。
- Demo script。
- 簡報。
- 錄影。

主要檔案：

- `app.py`
- `README.md`
- `docs/`

