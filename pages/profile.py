"""Profile page with user info, footprint map, favorites, and own posts."""

from pathlib import Path

import streamlit as st

import database
from components import render_cafe_card, render_map, render_post_card
from file_storage import save_uploaded_file


def render_profile_header(user, stats):
    """Render avatar, display name, account name, and profile metrics."""
    with st.container(border=True):
        if user.get("avatar_path") and Path(user["avatar_path"]).exists():
            st.image(user["avatar_path"], width=160)
        else:
            st.info("尚未上傳頭貼")

        st.markdown(
            f'<div class="coffee-card-title">{user.get("display_name") or user["username"]}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f'@{user["username"]}')
        metric_cols = st.columns(3)
        metric_cols[0].metric("貼文數", stats["post_count"])
        metric_cols[1].metric("探店數", stats["footprint_count"])
        metric_cols[2].metric("收藏", stats["favorite_count"])


def render_profile_editor(user):
    """Render the profile edit form for display name and avatar."""
    with st.expander("編輯個人資料"):
        with st.form("profile_form"):
            display_name = st.text_input("暱稱", value=user.get("display_name") or user["username"])
            avatar = st.file_uploader("頭貼", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("儲存")

            if submitted:
                avatar_path = save_uploaded_file(avatar, "avatar") if avatar else None
                database.update_user_profile(user["user_id"], display_name, avatar_path)
                st.success("已更新個人資料")
                st.rerun()


def render_profile_page():
    """Render all current-user profile sections."""
    user = database.get_user(st.session_state.user["user_id"])
    stats = database.get_user_stats(user["user_id"])

    st.markdown('<div class="coffee-screen-title">我的</div>', unsafe_allow_html=True)
    render_profile_header(user, stats)
    render_profile_editor(user)

    with st.expander("Google API 與帳號設定", expanded=False):
        st.text_input(
            "Google Maps API Key",
            key="api_key_override",
            type="password",
            help="可留空。留空時會使用環境變數或本機 iOS 專案 plist。",
        )
        if st.button("登出", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    st.markdown('<div class="coffee-section-title">足跡地圖</div>', unsafe_allow_html=True)
    footprints = database.list_footprint_cafes(user["user_id"])
    if footprints:
        render_map(footprints)
        for cafe in footprints:
            st.caption(f'{cafe["name"]}｜{cafe["area"]}')
    else:
        st.info("發文後，該咖啡廳會出現在足跡地圖。")

    st.markdown('<div class="coffee-section-title">收藏清單</div>', unsafe_allow_html=True)
    favorites = database.list_favorite_cafes(user["user_id"])
    if not favorites:
        st.info("目前還沒有收藏咖啡廳。")
    for cafe in favorites:
        render_cafe_card(cafe)

    st.markdown('<div class="coffee-section-title">我的貼文</div>', unsafe_allow_html=True)
    my_posts = [post for post in database.list_posts() if post["user_id"] == user["user_id"]]
    if not my_posts:
        st.info("目前還沒有發文。")
    for post in my_posts:
        render_post_card(post, compact=True)
