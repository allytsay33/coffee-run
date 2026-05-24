"""Login and mobile navigation UI."""

import streamlit as st

import database


def render_login_page():
    """Render the simple classroom-demo login page."""
    st.markdown('<div class="coffee-screen-title">Coffee Run</div>', unsafe_allow_html=True)
    st.caption("輸入帳號名即可開始探索咖啡廳。")

    with st.form("login_form"):
        username = st.text_input("帳號名", placeholder="例如：ally")
        submitted = st.form_submit_button("進入")

        if submitted:
            user = database.get_or_create_user(username)
            if user is None:
                st.warning("請輸入帳號名。")
            else:
                st.session_state.user = user
                st.rerun()


def render_mobile_nav():
    """Render a fixed bottom navigation bar and return the selected page."""
    user = database.get_user(st.session_state.user["user_id"])
    if user:
        st.session_state.user = user

    label_to_page = {
        "探索": "探索地圖",
        "社群": "社群",
        "我的": "個人頁",
    }
    page_to_label = {page: label for label, page in label_to_page.items()}
    current_label = page_to_label.get(st.session_state.current_page, "探索")
    with st.container(key="liquid_glass_nav"):
        selected_label = st.radio(
            "頁面",
            list(label_to_page),
            index=list(label_to_page).index(current_label),
            horizontal=True,
            label_visibility="collapsed",
            key="mobile_bottom_nav",
        )

    st.session_state.current_page = label_to_page[selected_label]
    return st.session_state.current_page
