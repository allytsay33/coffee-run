"""Profile workflow: records, footprint map, favorites, and editing."""

from html import escape
from pathlib import Path

import streamlit as st

import database
from components import render_cafe_card, render_map, render_post_card
from config import PROFILE_TABS
from file_storage import save_uploaded_file


def render_profile_header(user, stats):
    """Render account identity, profile text, and headline statistics."""
    if user.get("avatar_path") and Path(user["avatar_path"]).exists():
        st.image(user["avatar_path"], width=76)
    else:
        initial = escape((user.get("display_name") or user["username"] or "C")[0].upper())
        st.markdown(f'<div class="profile-avatar">{initial}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="coffee-screen-title">{escape(user.get("display_name") or user["username"])}</div>',
        unsafe_allow_html=True,
    )
    st.caption(f'@{user["username"]}')
    if user.get("bio"):
        st.write(user["bio"])
    metrics = st.columns(2)
    metrics[0].metric("探店紀錄", stats["post_count"])
    metrics[1].metric("已收藏", stats["favorite_count"])


def render_profile_editor(user):
    """Edit avatar, nickname, and biography."""
    top = st.columns([1, 4])
    if top[0].button("返回", width="stretch"):
        st.session_state.profile_editing = False
        st.rerun()
    top[1].markdown('<div class="coffee-screen-title">編輯個人檔案</div>', unsafe_allow_html=True)
    with st.form("profile_form"):
        avatar = st.file_uploader("頭貼", type=["png", "jpg", "jpeg"])
        display_name = st.text_input("用戶名", value=user.get("display_name") or user["username"])
        bio = st.text_area("個人簡介", value=user.get("bio") or "", placeholder="分享你的咖啡偏好...")
        if st.form_submit_button("儲存", width="stretch"):
            avatar_path = save_uploaded_file(avatar, "avatar") if avatar else None
            database.update_user_profile(user["user_id"], display_name, bio, avatar_path)
            st.session_state.profile_editing = False
            st.rerun()


def render_profile_settings():
    """Hold demo account actions without cluttering the primary layout."""
    with st.expander("設定", expanded=False):
        st.caption(f"資料庫：{database.database_label()}")
        st.text_input("Google Maps API Key", key="api_key_override", type="password")
        if st.button("登出", width="stretch"):
            st.session_state.user = None
            st.rerun()


def render_profile_page():
    """Render profile tabs defined in the mobile wireframe."""
    user = database.get_user(st.session_state.user["user_id"])
    if st.session_state.profile_editing:
        render_profile_editor(user)
        return
    stats = database.get_user_stats(user["user_id"])
    render_profile_header(user, stats)
    actions = st.columns([2, 2, 1])
    if actions[0].button("編輯個人檔案", width="stretch"):
        st.session_state.profile_editing = True
        st.rerun()
    actions[1].button("分享個人檔案", width="stretch", disabled=True)
    with actions[2]:
        render_profile_settings()

    selected_tab = st.segmented_control(
        "個人頁分頁",
        PROFILE_TABS,
        default=st.session_state.profile_tab,
        label_visibility="collapsed",
    ) or st.session_state.profile_tab
    st.session_state.profile_tab = selected_tab

    if selected_tab == "探店紀錄":
        posts = database.list_posts(user_id=user["user_id"])
        st.markdown('<div class="coffee-section-title">探店紀錄</div>', unsafe_allow_html=True)
        if not posts:
            st.info("你還沒有探店紀錄。")
        for post in posts:
            render_post_card(post, compact=True)
    elif selected_tab == "足跡地圖":
        footprints = database.list_footprint_cafes(user["user_id"])
        st.markdown('<div class="coffee-section-title">足跡地圖</div>', unsafe_allow_html=True)
        render_map(footprints)
    else:
        favorites = database.list_favorite_cafes(user["user_id"])
        st.markdown('<div class="coffee-section-title">已收藏</div>', unsafe_allow_html=True)
        if favorites:
            render_map(favorites)
            for cafe in favorites:
                render_cafe_card(cafe, compact=True)
        else:
            st.info("你還沒有收藏咖啡廳。")
