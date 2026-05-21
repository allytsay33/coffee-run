# Coffee Run Streamlit

這是 Coffee Run 的 Python / Streamlit 版本，和原本 iOS 專案分開。本版本以期末專案展示為目標，使用 SQLite 保存使用者、收藏與咖啡筆記。

## 功能

- 搜尋咖啡店
- 依地區與評分篩選
- 簡易暱稱登入
- 收藏咖啡店
- 新增咖啡筆記
- 推薦排行
- SQLite 永久保存資料

## 啟動方式

```bash
cd /Users/weishan33/Desktop/Coffee_Run!!/coffee_run_streamlit
python3 -m pip install -r requirements.txt
streamlit run app.py
```

如果 `streamlit` 指令找不到，可以改用：

```bash
python3 -m streamlit run app.py
```

## 專案文件

- `docs/01_python_only_check.md`：Python 使用範圍確認
- `docs/02_prd.md`：產品需求文件
- `docs/03_team_collaboration.md`：六人分工與協作方式
- `docs/04_demo_script.md`：展示流程
- `docs/05_task_board.md`：任務看板
- `docs/06_handoff_spec.md`：完整交接文件，包含產品需求、建議做法、分工、Git 流程與驗收標準

## 重要提醒

不要把原本的 iOS Swift 專案或 React / TypeScript 專案混進這個版本。這份專案的提交方向是 Python / Streamlit。
