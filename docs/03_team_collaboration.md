# 六人分工與協作方式

## 推薦分工

### 1. 專案整合與文件負責人

負責範圍：

- 維護 README 與交接文件
- 管理 GitHub main branch
- Review pull request
- 確認 demo 版本可以啟動
- 整理期末報告與展示流程

主要檔案：

- `README.md`
- `docs/`

### 2. 資料庫與資料模型負責人

負責範圍：

- SQLite schema
- 使用者、咖啡店、收藏、筆記資料表
- 新增或修改資料庫查詢函式
- 確認資料能永久保存

主要檔案：

- `database.py`
- `seed_data.py`

### 3. 探索與搜尋功能負責人

負責範圍：

- 咖啡店搜尋
- 地區篩選
- 評分篩選
- 店家卡片資訊呈現

主要檔案：

- `app.py` 的 `render_explore_page`
- `app.py` 的 `filtered_cafes`
- `app.py` 的 `render_cafe_card`

### 4. 收藏與個人頁負責人

負責範圍：

- 收藏 / 取消收藏
- 我的收藏頁
- sidebar 使用者統計
- 使用者體驗優化

主要檔案：

- `app.py` 的 `render_favorites_page`
- `app.py` 的 `render_sidebar`
- `database.py` 的 favorite 相關函式

### 5. 咖啡筆記與評分負責人

負責範圍：

- 新增心得表單
- 顯示歷史心得
- 評分紀錄
- 筆記頁排版

主要檔案：

- `app.py` 的 `render_reviews_page`
- `database.py` 的 review 相關函式

### 6. 測試、Demo 與報告負責人

負責範圍：

- 測試每個功能
- 寫 demo script
- 截圖與錄影
- 統整書面報告內容

主要檔案：

- `docs/04_demo_script.md`
- `docs/05_task_board.md`

## Git 協作規則

- `main` 只放可以啟動的版本
- 每個人用自己的 branch
- 每次只改自己負責的檔案區域
- 合併前至少一位同學看過
- 每天開始前先同步最新版

建議 branch：

```bash
feature/database
feature/search
feature/favorites
feature/reviews
feature/docs
feature/demo
```

## Commit 格式

建議格式：

```text
feat: add review form
fix: correct favorite toggle
docs: update demo script
data: add more cafe seed data
```

