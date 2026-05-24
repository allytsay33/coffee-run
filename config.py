"""Shared configuration constants for Coffee Run."""

from pathlib import Path


# User-uploaded images are saved locally for the Streamlit demo version.
UPLOAD_DIR = Path(__file__).parent / "data" / "uploads"

# Default social tags double as early filter data for the explore page.
DEFAULT_TAGS = [
    "手沖咖啡",
    "單品咖啡",
    "冷萃咖啡",
    "西西里咖啡",
    "拿鐵控",
    "美式咖啡",
    "拉花",
    "自家烘焙",
    "布丁控",
    "肉桂捲控",
    "巴斯克蛋糕",
    "戚風蛋糕",
    "提拉米蘇",
    "咖啡廳鹹食",
    "甜點工作室",
    "下午茶甜點",
    "蛋糕控",
    "有wifi",
    "筆電友善",
    "不限時咖啡廳",
    "工作咖啡廳",
    "讀書咖啡廳",
    "安靜",
    "戶外座位",
    "寵物友善",
    "店貓",
    "店狗",
    "深夜咖啡廳",
    "捷運站旁咖啡廳",
    "狗咖",
]

QUICK_FILTERS = ["營業中", "深夜咖啡廳", "不限時咖啡廳", "有wifi"]
PROFILE_TABS = ["探店紀錄", "足跡地圖", "已收藏"]
