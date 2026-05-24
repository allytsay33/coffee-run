"""Incremental change records for partial GitHub submissions.

This file is intentionally data-only. It records which Python files belong
to each small UI or feature change so separate contributions are not mixed.
"""


CHANGE_RECORDS = [
    {
        "change_id": "ui-bottom-nav-liquid-glass",
        "scope": "底部頁面切換列改為 liquid glass 風格，保留探索、社群、我的三頁。",
        "files": [
            "pages/auth.py",
            "styles.py",
        ],
        "notes": [
            "pages/auth.py 僅調整底部導覽容器與三頁切換元件。",
            "styles.py 僅調整底部導覽列定位、玻璃效果、可滑動選中 pill、圖示與三格等寬排列。",
            "未修改資料庫、探索、社群或個人頁功能邏輯。",
        ],
    },
    {
        "change_id": "ui-brewbound-reference-redesign",
        "scope": "依照提供的 BrewBound Social 電腦版介面重建 Python 顯示層。",
        "files": [
            "app.py",
            "components.py",
            "styles.py",
            "pages/explore.py",
            "pages/social.py",
            "pages/profile.py",
        ],
        "notes": [
            "加入寬版品牌頂列、發布捷徑與暖米白 / 深棕共用視覺。",
            "探索頁改為桌面大地圖、篩選工具列及寬版精緻結果卡。",
            "社群頁改為三欄含照片預覽、評分、標籤與互動的探店卡片流。",
            "個人頁改為寬版身份卡、Top 3、足跡地圖與紀錄區塊。",
            "既有 Supabase、Google 搜尋、收藏、發文、留言與頁面路由邏輯未更動。",
        ],
    },
    {
        "change_id": "ui-left-nav-split-cafe-detail",
        "scope": "桌面版頁面導覽移至左側，探索頁店家資訊改在右側面板開啟。",
        "files": [
            "pages/explore.py",
            "styles.py",
        ],
        "notes": [
            "styles.py 僅調整桌面寬度下的三頁導覽定位與探索雙欄面板樣式。",
            "pages/explore.py 保留原有搜尋、篩選、收藏與同步資料流程，改為左側列表搭配右側地圖 / 詳情切換。",
            "未修改資料庫 schema、API Key 設定或其他頁面功能。",
        ],
    },
]
