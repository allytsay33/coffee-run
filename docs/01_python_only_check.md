# Python 使用範圍確認

## 結論

目前新版 Coffee Run 已改成 Python / Streamlit 專案，和原本 iOS Swift 專案分開。你們自己維護的主要程式碼都是 Python：

- `app.py`
- `database.py`
- `seed_data.py`

資料永久保存使用 Python 內建的 `sqlite3` 模組。Streamlit 是 Python 套件，用來用 Python 程式產生瀏覽器介面。

## 和老師規定的關係

作業說明寫「只能使用 Python」。這個版本沒有自己撰寫 Swift、TypeScript、HTML、CSS 或 JavaScript。

需要注意的是，Streamlit 本質上會在瀏覽器顯示網站，因此底層仍會由套件產生網頁。建議跟老師確認一句：

> 老師您好，我們想使用 Streamlit 製作期末專案。所有功能、畫面與資料處理都由 Python 程式撰寫，不會自行撰寫 HTML、CSS 或 JavaScript。請問這樣是否符合只能使用 Python 的規定？

如果老師說 Streamlit 可以使用，這個方向就合理。如果老師要求完全不能用網站框架，則要改成 Tkinter 桌面程式。

## 不再使用的舊專案

以下舊版本不建議作為期末專案提交：

- iOS / Swift / Xcode 版本
- React / TypeScript / Vite 版本
- HTML / JavaScript 前端版本

