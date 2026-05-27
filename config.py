"""Shared configuration constants for Coffee Run."""

from pathlib import Path


# User-uploaded images are saved locally for the Streamlit demo version.
UPLOAD_DIR = Path(__file__).parent / "data" / "uploads"

# Default social tags double as early filter data for the explore page.
DEFAULT_TAGS = [
    "通常有位",
    "安靜",
    "咖啡好喝",
    "東西好吃",
    "價格便宜",
    "裝潢音樂",
    "不限時",
    "有 wifi",
    "插座多",
    "有賣單品",
    "有賣甜點",
    "有賣正餐",
    "可站立工作",
    "深夜營業",
    "筆電友善",
    "適合讀書",
    "適合聊天",
    "近捷運站",
    "平價",
    "甜點推薦",
]

QUICK_FILTERS = ["營業中", "深夜營業", "不限時", "有 wifi"]
PROFILE_TABS = ["探店紀錄", "足跡地圖", "已收藏"]
