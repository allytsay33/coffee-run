"""Shared configuration constants for Coffee Run."""

from pathlib import Path


# User-uploaded images are saved locally for the Streamlit demo version.
UPLOAD_DIR = Path(__file__).parent / "data" / "uploads"

# Default social tags double as early filter data for the explore page.
DEFAULT_TAGS = [
    "安靜",
    "插座",
    "不限時",
    "適合讀書",
    "適合聊天",
    "甜點",
    "平價",
    "晚上營業",
    "學生友善",
]

# Sidebar page order. Keeping this in one place avoids mismatched labels.
PAGE_OPTIONS = ["探索地圖", "社群", "個人頁", "推薦排行"]
