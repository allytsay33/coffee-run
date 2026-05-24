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
    avatar, identity, metric_area = st.columns([1, 3, 3], vertical_alignment="center")
    with avatar:
        if user.get("avatar_path") and Path(user["avatar_path"]).exists():
            st.image(user["avatar_path"], width=132)
        else:
            initial = escape((user.get("display_name") or user["username"] or "C")[0].upper())
            st.markdown(f'<div class="profile-avatar">{initial}</div>', unsafe_allow_html=True)
    with identity:
        st.markdown(
            f'<div class="profile-name">{escape(user.get("display_name") or user["username"])}　Coffee</div>'
            f'<div class="profile-handle">@{escape(user["username"])}</div>'
            f'<p class="profile-bio">{escape(user.get("bio") or "在城市街頭尋找完美的咖啡角落，記錄每一次探店日常。")}</p>',
            unsafe_allow_html=True,
        )
    with metric_area:
        metrics = st.columns(3)
        metrics[0].metric("探店紀錄", stats["post_count"])
        metrics[1].metric("收藏清單", stats["favorite_count"])
        metrics[2].metric("造訪足跡", stats["footprint_count"])


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


def render_top3_editor(user):
    """Inline editor for selecting the user's top-3 cafes."""
    cafes = database.list_cafes()
    options = {"（未設定）": None} | {f'{c["name"]}｜{c["area"]}': c["cafe_id"] for c in cafes}
    current = database.get_user_top3(user["user_id"])

    def _default(slot):
        cafe = current[slot]
        if not cafe:
            return "（未設定）"
        key = f'{cafe["name"]}｜{cafe["area"]}'
        return key if key in options else "（未設定）"

    with st.form("top3_form"):
        st.markdown('<div class="profile-section-title">編輯 TOP 3</div>', unsafe_allow_html=True)
        sel1 = st.selectbox("🥇 第 1 名", list(options), index=list(options).index(_default(0)))
        sel2 = st.selectbox("🥈 第 2 名", list(options), index=list(options).index(_default(1)))
        sel3 = st.selectbox("🥉 第 3 名", list(options), index=list(options).index(_default(2)))
        col_save, col_cancel = st.columns(2)
        if col_save.form_submit_button("儲存", type="primary", width="stretch"):
            database.set_user_top3(user["user_id"], [options[sel1], options[sel2], options[sel3]])
            st.session_state.top3_editing = False
            st.rerun()
        if col_cancel.form_submit_button("取消", width="stretch"):
            st.session_state.top3_editing = False
            st.rerun()


def render_visit_records(user, favorites):
    """Render the user's ranked cafe list and published visit posts."""
    if st.session_state.get("top3_editing"):
        render_top3_editor(user)
    else:
        with st.container(border=True, key="profile_top3"):
            head = st.columns([4, 1])
            head[0].markdown('<div class="profile-section-title">我的 TOP 3 咖啡名單</div>', unsafe_allow_html=True)
            if head[1].button("編輯", key="edit_top3", width="stretch"):
                st.session_state.top3_editing = True
                st.rerun()
            top3 = database.get_user_top3(user["user_id"])
            if not any(top3):
                st.caption("點右上角「編輯」設定你的 TOP 3。")
            top_columns = st.columns(3)
            for index, cafe in enumerate(top3):
                if cafe:
                    rating = cafe["user_rating"] or cafe["rating"]
                    top_columns[index].markdown(
                        f'<div class="top-cafe"><b>{index + 1}</b><strong>{escape(cafe["name"])}</strong>'
                        f'<small>★ {rating:.1f}</small></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    top_columns[index].markdown(
                        f'<div class="top-cafe top-cafe-empty"><b>{index + 1}</b><span>未設定</span></div>',
                        unsafe_allow_html=True,
                    )

    posts = database.list_posts(user_id=user["user_id"])
    st.markdown('<div class="coffee-section-title">探店貼文</div>', unsafe_allow_html=True)
    if not posts:
        st.info("你還沒有探店紀錄。")
        return
    post_columns = st.columns(3)
    for index, post in enumerate(posts):
        with post_columns[index % 3]:
            render_post_card(post, compact=True)


def render_footprint_map(user):
    """Render only cafes where the user has published a visit post."""
    footprints = database.list_footprint_cafes(user["user_id"])
    with st.container(border=True, key="profile_map"):
        st.markdown('<div class="profile-section-title">足跡地圖</div>', unsafe_allow_html=True)
        st.caption("顯示你已發佈探店貼文的咖啡廳。")
        render_map(footprints)


def render_saved_map(favorites):
    """Render favorite cafes as map markers and cards in the saved subpage."""
    with st.container(border=True, key="profile_map"):
        st.markdown('<div class="profile-section-title">已收藏</div>', unsafe_allow_html=True)
        render_map(favorites)
    if favorites:
        for cafe in favorites:
            render_cafe_card(cafe, compact=True)
    else:
        st.info("你還沒有收藏咖啡廳。")


def render_profile_page():
    """Render profile tabs defined in the mobile wireframe."""
    user = database.get_user(st.session_state.user["user_id"])
    if st.session_state.profile_editing:
        render_profile_editor(user)
        return
    stats = database.get_user_stats(user["user_id"])
    with st.container(border=True, key="profile_identity"):
        render_profile_header(user, stats)
    actions = st.columns([2, 2, 1])
    if actions[0].button("編輯個人檔案", width="stretch"):
        st.session_state.profile_editing = True
        st.rerun()
    actions[1].button("分享個人檔案", width="stretch", disabled=True)
    with actions[2]:
        render_profile_settings()

    favorites = database.list_favorite_cafes(user["user_id"])
    default_tab = st.session_state.profile_tab if st.session_state.profile_tab in PROFILE_TABS else PROFILE_TABS[0]
    if "profile_tab_selector" not in st.session_state:
        st.session_state.profile_tab_selector = default_tab
    with st.container(key="profile_subnav"):
        selected_tab = st.segmented_control(
            "個人頁分頁",
            PROFILE_TABS,
            label_visibility="collapsed",
            key="profile_tab_selector",
        ) or default_tab
    st.session_state.profile_tab = selected_tab

    with st.container(key="profile_tab_content"):
        if selected_tab == "探店紀錄":
            render_visit_records(user, favorites)
        elif selected_tab == "足跡地圖":
            render_footprint_map(user)
        else:
            render_saved_map(favorites)
