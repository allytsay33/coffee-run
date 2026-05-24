"""Reusable mobile UI blocks for maps, cafes, and community posts."""

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from formatters import format_distance, format_tags


def render_map(cafes):
    """Render the exact cafe result set on a map."""
    map_cafes = [cafe for cafe in cafes if cafe.get("lat") is not None and cafe.get("lng") is not None]
    if not map_cafes:
        st.info("目前沒有符合條件的地圖點位。")
        return
    static_url = google_maps.static_map_url(map_cafes, current_api_key())
    if static_url:
        st.image(static_url, width="stretch")
    else:
        st.map(pd.DataFrame([{"lat": cafe["lat"], "lon": cafe["lng"]} for cafe in map_cafes]), height=360)


def toggle_favorite_button(cafe_id, key, stretch=False):
    """Render the shared cafe bookmark action used from every feature."""
    user_id = st.session_state.user["user_id"]
    saved = cafe_id in database.get_favorite_ids(user_id)
    label = "取消收藏" if saved else "收藏"
    if st.button(label, key=key, width="stretch" if stretch else "content"):
        if saved:
            database.remove_favorite(user_id, cafe_id)
        else:
            database.add_favorite(user_id, cafe_id)
        st.rerun()


def render_cafe_photos(cafe_id, columns=3):
    """Show community-uploaded cafe photos as the result gallery."""
    photos = [path for path in database.get_cafe_photos(cafe_id) if Path(path).exists()]
    if not photos:
        return
    photo_columns = st.columns(columns)
    for index, photo in enumerate(photos[:columns]):
        photo_columns[index].image(photo, width="stretch")


def render_cafe_card(cafe, compact=False):
    """Render a result row matching the mobile exploration list."""
    rating = cafe["user_rating"] or cafe["rating"]
    with st.container(border=True):
        st.markdown(f'<div class="coffee-card-title">{escape(cafe["name"])}</div>', unsafe_allow_html=True)
        status = "營業中" if cafe.get("open_now") == 1 else "營業資訊請見詳情"
        st.caption(f'{rating:.1f} ★｜{format_distance(cafe["distance_meters"])}｜{status}')
        if not compact:
            render_cafe_photos(cafe["cafe_id"])
            if cafe.get("tags"):
                st.write(format_tags(cafe["tags"][:4]))
        actions = st.columns([1, 1])
        if actions[0].button("查看", key=f'cafe_detail_{cafe["cafe_id"]}_{compact}', width="stretch"):
            st.session_state.selected_cafe_id = cafe["cafe_id"]
            st.rerun()
        with actions[1]:
            toggle_favorite_button(cafe["cafe_id"], f'favorite_{cafe["cafe_id"]}_{compact}', True)


def render_post_images(post):
    """Render all stored photos for one post in upload order."""
    photos = [path for path in post.get("photos", []) if Path(path).exists()]
    if not photos:
        return
    if len(photos) == 1:
        st.image(photos[0], width="stretch")
        return
    columns = st.columns(min(len(photos), 3))
    for index, path in enumerate(photos):
        columns[index % len(columns)].image(path, width="stretch")


def render_post_card(post, compact=False, open_detail=True):
    """Render a social post card with engagement and cafe bookmark actions."""
    user_id = st.session_state.user["user_id"]
    liked = database.user_liked_post(user_id, post["post_id"])
    with st.container(border=True):
        st.markdown(f'<div class="coffee-card-title">{escape(post["cafe_name"])}</div>', unsafe_allow_html=True)
        st.caption(f'@{post["username"]}｜{post["rating"]}.0 ★')
        render_post_images(post)
        st.write(post["content"])
        st.write(format_tags(post.get("tags", [])))
        st.caption(f'愛心 {post["like_count"]}｜留言 {post["comment_count"]}')

        actions = st.columns(3)
        if actions[0].button("收回愛心" if liked else "愛心", key=f'like_{post["post_id"]}_{compact}', width="stretch"):
            database.toggle_like(user_id, post["post_id"])
            st.rerun()
        if open_detail and actions[1].button("查看", key=f'post_detail_{post["post_id"]}_{compact}', width="stretch"):
            st.session_state.selected_post_id = post["post_id"]
            st.session_state.social_view = "detail"
            st.session_state.current_page = "社群"
            st.rerun()
        with actions[2]:
            toggle_favorite_button(post["cafe_id"], f'post_save_cafe_{post["post_id"]}_{compact}', True)

        if not open_detail:
            with st.expander("留言"):
                for comment in database.list_comments(post["post_id"]):
                    st.caption(f'@{comment["username"]}：{comment["content"]}')
                with st.form(f'comment_form_{post["post_id"]}_{compact}', clear_on_submit=True):
                    content = st.text_input("新增留言")
                    if st.form_submit_button("送出", width="stretch") and content.strip():
                        database.add_comment(user_id, post["post_id"], content)
                        st.rerun()
