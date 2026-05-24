"""Reusable mobile UI blocks for maps, cafes, and community posts."""

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from formatters import format_distance


POST_PREVIEW_IMAGES = (
    "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=720&q=80",
    "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=720&q=80",
    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=720&q=80",
)


def render_brand_header():
    """Render the compact BrewBound identity bar and publish shortcut."""
    user = st.session_state.user
    initial = escape((user.get("display_name") or user["username"] or "C")[0].upper())
    with st.container(key="brewbound_header"):
        brand, spacer, publish, avatar = st.columns([3, 4, 2, 2])
        brand.markdown(
            """
            <div class="brand-lockup">
                <span class="brand-mark">B</span>
                <span class="brand-copy">
                    <strong>BrewBound <em>Social</em></strong>
                    <small>咖啡地圖社群</small>
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        spacer.markdown(
            '<div class="header-search-display">⌕　搜尋內湖、深夜、不限時、甜點</div>',
            unsafe_allow_html=True,
        )
        if publish.button("＋　新探店貼文", key="header_new_post", help="建立探店筆記", width="stretch"):
            st.session_state.current_page = "社群"
            st.session_state.social_view = "create"
            st.rerun()
        avatar.markdown(
            f'<div class="header-user"><div class="header-avatar">{initial}</div>'
            f'<span>{escape(user.get("display_name") or user["username"])} 的咖啡日常</span></div>',
            unsafe_allow_html=True,
        )


def render_map(cafes):
    """Render the exact cafe result set on a map."""
    map_cafes = [cafe for cafe in cafes if cafe.get("lat") is not None and cafe.get("lng") is not None]
    if not map_cafes:
        st.info("目前沒有符合條件的地圖點位。")
        return
    static_url = google_maps.static_map_url(map_cafes, current_api_key(), width=640, height=420)
    with st.container(key="brewbound_map"):
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
    """Render a warm editorial result card for the explore list."""
    rating = cafe["user_rating"] or cafe["rating"]
    with st.container(border=True):
        status = "營業中" if cafe.get("open_now") == 1 else "營業時間待確認"
        st.markdown(
            f'<div class="cafe-result-head"><div class="coffee-card-title">{escape(cafe["name"])}</div>'
            f'<span class="rating-pill">★ {rating:.1f}</span></div>'
            f'<div class="cafe-meta">{escape(cafe.get("area") or "Taipei Cafe")} &nbsp;|&nbsp; '
            f'{format_distance(cafe["distance_meters"])} &nbsp;|&nbsp; {status}</div>',
            unsafe_allow_html=True,
        )
        if not compact:
            render_cafe_photos(cafe["cafe_id"])
            if cafe.get("tags"):
                st.markdown(
                    '<div class="tag-row">' + "".join(
                        f'<span>#{escape(tag)}</span>' for tag in cafe["tags"][:4]
                    ) + "</div>",
                    unsafe_allow_html=True,
                )
        actions = st.columns([1, 1])
        if actions[0].button("查看詳情", key=f'cafe_detail_{cafe["cafe_id"]}_{compact}', width="stretch"):
            st.session_state.selected_cafe_id = cafe["cafe_id"]
            st.rerun()
        with actions[1]:
            toggle_favorite_button(cafe["cafe_id"], f'favorite_{cafe["cafe_id"]}_{compact}', True)


def render_post_images(post):
    """Render all stored photos for one post in upload order."""
    photos = [path for path in post.get("photos", []) if Path(path).exists()]
    if not photos:
        st.markdown(
            f'<div class="post-preview"><img src="{POST_PREVIEW_IMAGES[post["post_id"] % len(POST_PREVIEW_IMAGES)]}" '
            f'alt="{escape(post["cafe_name"])}"><span>PIN &nbsp;{escape(post["cafe_name"])}</span></div>',
            unsafe_allow_html=True,
        )
        return
    if len(photos) == 1:
        st.image(photos[0], width="stretch")
        return
    columns = st.columns(min(len(photos), 3))
    for index, path in enumerate(photos):
        columns[index % len(columns)].image(path, width="stretch")


def render_post_card(post, compact=False, open_detail=True):
    """Render one BrewBound-style social note with engagement actions."""
    user_id = st.session_state.user["user_id"]
    liked = database.user_liked_post(user_id, post["post_id"])
    with st.container(border=True):
        st.markdown(
            f'<div class="post-location">PIN &nbsp;{escape(post["cafe_name"])}</div>'
            f'<div class="post-author">@{escape(post["username"])}'
            f'<span class="rating-pill">★ {post["rating"]}.0</span></div>',
            unsafe_allow_html=True,
        )
        render_post_images(post)
        st.markdown(f'<p class="post-copy">{escape(post["content"])}</p>', unsafe_allow_html=True)
        if post.get("tags"):
            st.markdown(
                '<div class="tag-row">' + "".join(
                    f'<span>#{escape(tag)}</span>' for tag in post["tags"]
                ) + "</div>",
                unsafe_allow_html=True,
            )
        st.caption(f'愛心 {post["like_count"]}　留言 {post["comment_count"]}')

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
