# Coffee Run Streamlit

這是 Coffee Run 的 Python / Streamlit 手機優先版本，和原本 iOS 專案分開。本版本以期末專案展示為目標；設定 Supabase 後，使用 PostgreSQL 保存所有組員與展示使用者共享的資料。

## 功能

- 搜尋咖啡店
- 依地區與評分篩選
- 簡易暱稱登入
- 收藏咖啡店
- 新增咖啡筆記
- 足跡地圖與個人收藏
- Supabase PostgreSQL 多人共用資料庫

## 啟動方式

```bash
cd /Users/weishan33/Desktop/coffee_run_streamlit
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

## Supabase 設定

尚未設定 Supabase 時，程式會暫時使用本機 `data/coffee_run.db` 讓介面可以開啟。要讓大家共用同一份資料：

```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

接著把 `.streamlit/secrets.toml` 內的 `SUPABASE_DB_URL` 改成 Supabase Dashboard 的 `Connect > Session pooler` 連線字串，再重新啟動網站。完整操作步驟見 `docs/12_supabase_setup.md`。

## 專案文件

- `docs/01_python_only_check.md`：Python 使用範圍確認
- `docs/02_prd.md`：產品需求文件
- `docs/03_team_collaboration.md`：六人分工與協作方式
- `docs/04_demo_script.md`：展示流程
- `docs/05_task_board.md`：任務看板
- `docs/06_handoff_spec.md`：完整交接文件，包含產品需求、建議做法、分工、Git 流程與驗收標準
- `docs/07_code_walkthrough_and_team_plan.md`：程式碼導覽與細部分工建議
- `docs/08_wireframe_feature_spec.md`：依照手機版 wireframe 整理的詳細功能規格
- `docs/09_schema_function_contracts_and_ownership.md`：六人分工校正、完整資料庫 schema、功能函式契約與系統邏輯
- `docs/10_current_database_schema.md`：目前程式已實作的資料庫 schema 與資料流程
- `docs/11_current_code_reference.md`：目前程式版本、所有 Python 檔案與函式逐項說明
- `docs/12_supabase_setup.md`：建立 Supabase、設定機密連線字串與資料轉移說明

## 重要提醒

不要把原本的 iOS Swift 專案或 React / TypeScript 專案混進這個版本。這份專案的提交方向是 Python / Streamlit。
