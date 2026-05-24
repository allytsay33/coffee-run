# Coffee Run Supabase 啟用步驟

更新日期：2026-05-24

## 1. 現在的程式行為

程式已支援兩種儲存模式：

| 狀態 | 寫入位置 | 用途 |
| --- | --- | --- |
| 未設定 `SUPABASE_DB_URL` | 本機 `data/coffee_run.db` | UI 開發與離線預覽 |
| 已設定 `SUPABASE_DB_URL` | Supabase PostgreSQL | 組員與 Demo 使用者共用資料 |

啟動網站時，`database.initialize_database()` 會在選定的資料庫自動建立資料表與 demo 初始資料。因此不需要另外在 Supabase SQL Editor 手動貼 schema。

## 2. 建立 Supabase 專案

1. 前往 <https://supabase.com/dashboard> 並登入。
2. 點選 `New project`。
3. 填寫專案名稱，例如 `coffee-run`。
4. 設定並保存 Database Password。這個密碼不要放到 GitHub 或群組公開訊息。
5. Region 選離展示所在地較近的區域。
6. 等待專案建立完成。

## 3. 取得資料庫連線字串

1. 進入新建立的 Supabase project。
2. 點頁面上方 `Connect`。
3. 選擇 `Session pooler`。
4. 複製 PostgreSQL connection string。
5. 將字串內的密碼 placeholder 換成建立專案時設定的 Database Password。
6. 確認字串最後包含 `sslmode=require`；若沒有，可加上 `?sslmode=require`。

使用 `Session pooler` 的原因：本專案的 Streamlit app 是後端程式，且本機 / 多數部署環境需要 IPv4 相容連線。資料庫密碼只放在後端私密設定中，不應出現在網頁程式碼或 GitHub。

## 4. 在自己的電腦啟用 Supabase

在 Terminal 執行：

```bash
cd /Users/weishan33/Desktop/coffee_run_streamlit
python3 -m pip install -r requirements.txt
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

打開 `.streamlit/secrets.toml`，將範例網址換成你的真實 connection string：

```toml
SUPABASE_DB_URL = "postgresql://postgres.PROJECT_REF:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres?sslmode=require"
```

注意：

- `.streamlit/secrets.toml` 已加入 `.gitignore`，不可 commit。
- `.streamlit/secrets.toml.example` 只有範例格式，可以 commit 給組員。
- 若密碼含有 `@`、`#`、`/` 等特殊符號，需要在 URL 中做 percent encoding；最簡單的做法是將資料庫密碼設定為英數組合。

重新啟動網站：

```bash
python3 -m streamlit run app.py
```

登入後打開「我的」頁面的「設定」，顯示 `資料庫：Supabase PostgreSQL（多人共用）` 即代表程式已切換到雲端資料庫。

## 5. 組員如何共用

每位組員：

1. 從 GitHub pull 最新程式碼。
2. 執行 `python3 -m pip install -r requirements.txt`。
3. 自己建立 `.streamlit/secrets.toml`。
4. 由專案負責人私下提供相同的 Supabase connection string。
5. 執行網站。

只要六人的 `SUPABASE_DB_URL` 相同，收藏、貼文、留言、愛心、個人資料與咖啡廳補充篩選資料都會出現在同一個資料庫。

## 6. 既有本機資料是否會自動搬過去

不會。切換至 Supabase 後，雲端會有新的初始店家與 demo 社群資料；原本 `data/coffee_run.db` 仍留在你的電腦，不會被刪除。

如果需要保留你本機已搜尋到的 Google 店家、既有貼文或收藏，請先不要刪除 `data/coffee_run.db`。確認 Supabase 可連線後，再執行一次性的資料搬移；搬移必須處理使用者與貼文 ID 對應，不能直接把 `.db` 上傳到 GitHub。

## 7. 圖片限制與下一步

目前貼文照片與頭貼仍保存在執行網站那台電腦的 `data/uploads/`。資料庫共享後，文字資料、評分與收藏可多人看到，但由另一台電腦上傳的圖片檔案不會自動出現在你的電腦。

若 Demo 需要多台電腦都能看到相同圖片，下一步應將 `file_storage.py` 改接 Supabase Storage，並在 `posts.image_path`、`post_photos.image_path`、`users.avatar_path` 儲存公開圖片 URL。

## 8. 參考文件

- Supabase Database Connections: <https://supabase.com/docs/reference/postgres/connection-strings>
- Streamlit Connect to Supabase: <https://docs.streamlit.io/develop/tutorials/databases/supabase>
