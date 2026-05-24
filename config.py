"""Shared configuration constants for Coffee Run."""

from pathlib import Path


# User-uploaded images are saved locally for the Streamlit demo version.
UPLOAD_DIR = Path(__file__).parent / "data" / "uploads"

# Default social tags double as early filter data for the explore page.
DEFAULT_TAGS = [
    "安靜",
    "插座多",
    "不限時",
    "適合讀書",
    "適合聊天",
    "甜點",
    "平價",
    "深夜咖啡廳",
    "學生友善",
]

QUICK_FILTERS = ["營業中", "深夜咖啡廳", "不限時", "插座多"]
PROFILE_TABS = ["探店紀錄", "足跡地圖", "已收藏"]
