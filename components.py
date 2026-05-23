"""Reusable Streamlit UI components.

Page modules call these helpers when they need common visual blocks, such as
maps, cafe cards, or post cards. Keeping them here avoids duplicated UI code.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from formatters import format_distance, format_tags


def render_map(cafes):
    """Render cafes on a map, using Google Static Maps when an API key exists."""
    map_cafes = [cafe for cafe in cafes if cafe.get("lat") is not None and cafe.get("lng") is not None]
    if not map_cafes:
        st.info("目前沒有可顯示在地圖上的座標資料。")
        return

    api_key = current_api_key()
    static_url = google_maps.static_map_url(map_cafes, api_key)
    if static_url:
        st.image(static_url, caption="Google Static Maps API")
    else:
        st.map(pd.DataFrame([{"lat": cafe["lat"], "lon": cafe["lng"]} for cafe in map_cafes]))


def render_cafe_card(cafe):
    """Render one cafe in search results or profile favorites."""
    user = st.session_state.user
    favorite_ids = database.get_favorite_ids(user["user_id"])
    is_favorite = cafe["cafe_id"] in favorite_ids
    combined_rating = cafe["user_rating"] or cafe["rating"]

    with st.container(border=True):
        st.markdown(f'<div class="coffee-card-title">{cafe["name"]}</div>', unsafe_allow_html=True)
        st.caption(
            f'{format_distance(cafe["distance_meters"])}｜'
            f'綜合評分 {combined_rating:.1f}｜{cafe["area"]}'
        )
        st.caption(cafe["address"])
        st.write(cafe["description"])
        st.write(format_tags(cafe["tags"]))

        actions = st.columns([1, 1])
        if actions[0].button("查看詳情", key=f'detail_{cafe["cafe_id"]}', use_container_width=True):
            st.session_state.selected_cafe_id = cafe["cafe_id"]

        # Favorite is tied to cafe_id, so the same button works in search
        # results and on the profile page.
        label = "取消收藏" if is_favorite else "收藏"
        if actions[1].button(label, key=f'favorite_{cafe["cafe_id"]}', use_container_width=True):
            if is_favorite:
                database.remove_favorite(user["user_id"], cafe["cafe_id"])
            else:
                database.add_favorite(user["user_id"], cafe["cafe_id"])
            st.rerun()


def render_post_card(post, compact=False):
    """Render a social post with image, tags, like button, and comments."""
    user_id = st.session_state.user["user_id"]
    liked = database.user_liked_post(user_id, post["post_id"])

    with st.container(border=True):
        st.markdown(f'<div class="coffee-card-title">{post["cafe_name"]}</div>', unsafe_allow_html=True)
        st.caption(f'@{post["username"]}｜{post["created_at"]}')

        # Images are optional because old posts or text-only posts may not have
        # an uploaded file.
        if post.get("image_path") and Path(post["image_path"]).exists():
            st.image(post["image_path"], use_container_width=True)

        st.write(post["content"])
        st.write(format_tags(post.get("tags", [])))

        st.caption(f'評分 {post["rating"]}/5｜愛心 {post["like_count"]}｜留言 {post["comment_count"]}')
        if st.button(
            "收回愛心" if liked else "按愛心",
            key=f'like_{post["post_id"]}_{compact}',
            use_container_width=True,
        ):
            database.toggle_like(user_id, post["post_id"])
            st.rerun()

        with st.expander("留言"):
            for comment in database.list_comments(post["post_id"]):
                st.caption(f'@{comment["username"]}：{comment["content"]}')

            with st.form(f'comment_form_{post["post_id"]}_{compact}', clear_on_submit=True):
                content = st.text_input("新增留言")
                submitted = st.form_submit_button("送出")
                if submitted and content.strip():
                    database.add_comment(user_id, post["post_id"], content)
                    st.rerun()
