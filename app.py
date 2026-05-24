"""Coffee Run Streamlit app entry point.

This file intentionally stays small. Page-specific UI lives in the `pages`
package, reusable widgets live in `components.py`, and persistence stays in
`database.py`. Keeping the entry point thin makes team collaboration easier.
"""

import streamlit as st

import database
from components import render_brand_header
from pages.auth import render_login_page, render_mobile_nav
from pages.explore import render_explore_page
from pages.profile import render_profile_page
from pages.social import render_social_page
from state import initialize_state
from styles import inject_mobile_styles


def main():
    """Initialize app-wide services, then route to the selected page."""
    st.set_page_config(page_title="BrewBound Social", page_icon="Coffee", layout="wide")
    inject_mobile_styles()

    # Database initialization creates missing tables and seed content without
    # erasing user data, whether storage is local or hosted by Supabase.
    try:
        database.initialize_database()
    except Exception as error:
        st.error("資料庫連線失敗。請檢查 Supabase 連線字串與套件安裝狀態。")
        st.code(str(error))
        st.stop()
    initialize_state()

    # The app uses a classroom-friendly fake login. Without a logged-in user,
    # no feature pages are shown because most actions need a user_id.
    if st.session_state.user is None:
        render_login_page()
        return

    render_brand_header()
    page = render_mobile_nav()
    if page == "探索地圖":
        render_explore_page()
    elif page == "社群":
        render_social_page()
    elif page == "個人頁":
        render_profile_page()


if __name__ == "__main__":
    main()
