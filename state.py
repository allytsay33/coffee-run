"""Streamlit session-state helpers.

Streamlit reruns the script after most user interactions. Values that must
survive reruns, such as the current user or selected cafe, are stored here.
"""

import streamlit as st


def initialize_state():
    """Create session-state keys used across multiple pages."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "selected_cafe_id" not in st.session_state:
        st.session_state.selected_cafe_id = None
    if "api_key_override" not in st.session_state:
        st.session_state.api_key_override = ""
    if "current_page" not in st.session_state:
        st.session_state.current_page = "探索地圖"
    if "selected_post_id" not in st.session_state:
        st.session_state.selected_post_id = None
    if "social_view" not in st.session_state:
        st.session_state.social_view = "feed"
    if "profile_tab" not in st.session_state:
        st.session_state.profile_tab = "探店紀錄"
    if "profile_editing" not in st.session_state:
        st.session_state.profile_editing = False
    if "explore_filter_open" not in st.session_state:
        st.session_state.explore_filter_open = False
    if "login_view" not in st.session_state:
        st.session_state.login_view = "welcome"
    if "explore_filters" not in st.session_state:
        st.session_state.explore_filters = {
            "keyword": "",
            "area": "全部",
            "minimum_rating": 0.0,
            "selected_tags": [],
            "quick_filters": [],
            "maximum_distance": None,
        }
