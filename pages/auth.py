"""Login and mobile navigation UI."""

import base64
from pathlib import Path

import streamlit as st

import database
from file_storage import save_uploaded_file

_LOGO_PATH = Path(__file__).parent.parent / "data" / "logo.png"
_LOGO_PLACEHOLDER = "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&q=80"


def _logo_src() -> str:
    if _LOGO_PATH.exists():
        b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        return f"data:image/png;base64,{b64}"
    return _LOGO_PLACEHOLDER


def _render_logo():
    st.markdown(
        f'<div class="login-logo"><img src="{_logo_src()}" alt="Coffee Run logo"></div>',
        unsafe_allow_html=True,
    )


def _render_welcome():
    _render_logo()
    st.markdown(
        '<div class="login-title">Coffee Run</div>'
        '<div class="login-subtitle">歡迎使用 Coffee Run</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="login-actions">', unsafe_allow_html=True)
    if st.button("登入現有帳號", key="go_login", type="primary", width="stretch"):
        st.session_state.login_view = "login"
        st.rerun()
    if st.button("創建新帳號", key="go_register", width="stretch"):
        st.session_state.login_view = "register"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_login():
    if st.button("← 返回", key="login_back"):
        st.session_state.login_view = "welcome"
        st.rerun()
    st.markdown('<div class="login-title">登入</div>', unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input("帳號名", placeholder="輸入你的帳號名")
        password = st.text_input("密碼", type="password", placeholder="輸入密碼")
        if st.form_submit_button("登入", type="primary", width="stretch"):
            if not username.strip() or not password:
                st.warning("請輸入帳號名和密碼。")
            else:
                user = database.login_user(username, password)
                if user is None:
                    st.error("帳號名或密碼錯誤。")
                else:
                    st.session_state.user = user
                    st.session_state.login_view = "welcome"
                    st.rerun()


def _render_register():
    if st.button("← 返回", key="register_back"):
        st.session_state.login_view = "welcome"
        st.rerun()
    st.markdown('<div class="login-title">創建帳號</div>', unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=False):
        username = st.text_input("帳號名", placeholder="設定你的帳號名")
        password = st.text_input("密碼", type="password", placeholder="設定密碼")
        avatar = st.file_uploader("頭貼（可略過）", type=["png", "jpg", "jpeg"])
        done = st.form_submit_button("完成", type="primary", width="stretch")
        if done:
            if not username.strip() or not password:
                st.warning("請輸入帳號名和密碼。")
            else:
                avatar_path = save_uploaded_file(avatar, "avatar") if avatar else None
                user = database.register_user(username, password, avatar_path)
                if user is None:
                    st.error("此帳號名已被使用，請換一個。")
                else:
                    st.session_state.user = user
                    st.session_state.login_view = "welcome"
                    st.rerun()


def render_login_page():
    """Route to the correct login sub-screen based on session state."""
    view = st.session_state.get("login_view", "welcome")
    if view == "login":
        _render_login()
    elif view == "register":
        _render_register()
    else:
        _render_welcome()


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
    pending_nav_label = st.session_state.pop("pending_nav_label", None)
    if pending_nav_label in label_to_page:
        current_label = pending_nav_label
        st.session_state.mobile_bottom_nav = current_label
    elif "mobile_bottom_nav" not in st.session_state:
        st.session_state.mobile_bottom_nav = current_label
    with st.container(key="liquid_glass_nav"):
        selected_label = st.radio(
            "頁面",
            list(label_to_page),
            horizontal=True,
            label_visibility="collapsed",
            key="mobile_bottom_nav",
        )

    st.session_state.current_page = label_to_page[selected_label]
    return st.session_state.current_page
