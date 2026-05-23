"""Coffee Run Streamlit app entry point.

This file intentionally stays small. Page-specific UI lives in the `pages`
package, reusable widgets live in `components.py`, and persistence stays in
`database.py`. Keeping the entry point thin makes team collaboration easier.
"""

import streamlit as st

import database
from pages.auth import render_login_page, render_mobile_nav
from pages.explore import render_explore_page
from pages.profile import render_profile_page
from pages.ranking import render_ranking_page
from pages.social import render_social_page
from state import initialize_state
from styles import inject_mobile_styles


def main():
    """Initialize app-wide services, then route to the selected page."""
    st.set_page_config(page_title="Coffee Run", page_icon="Coffee", layout="centered")
    inject_mobile_styles()

    # Database initialization is idempotent: it creates missing tables and seeds
    # demo cafes, but it does not erase existing user data.
    database.initialize_database()
    initialize_state()

    # The app uses a classroom-friendly fake login. Without a logged-in user,
    # no feature pages are shown because most actions need a user_id.
    if st.session_state.user is None:
        render_login_page()
        return

    page = render_mobile_nav()
    if page == "探索地圖":
        render_explore_page()
    elif page == "社群":
        render_social_page()
    elif page == "個人頁":
        render_profile_page()
    else:
        render_ranking_page()


if __name__ == "__main__":
    main()
