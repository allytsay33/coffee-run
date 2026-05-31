"""Reusable mobile UI blocks for maps, cafes, and community posts."""

import base64
from html import escape
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from formatters import format_distance

_LOGO_PATH = Path(__file__).parent / "data" / "logo.png"


def _header_logo_src() -> str:
    if _LOGO_PATH.exists():
        b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode()
        return f"data:image/png;base64,{b64}"
    return ""


POST_PREVIEW_IMAGES = (
    "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=720&q=80",
    "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=720&q=80",
    "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=720&q=80",
)


def render_brand_header():
    """Render the compact Coffee Run identity bar and publish shortcut."""
    user = st.session_state.user
    display_name = escape(user.get("display_name") or user["username"])
    logo_src = _header_logo_src()
    logo_html = (
        f'<img src="{logo_src}" class="brand-logo-img" alt="Coffee Run">'
        if logo_src
        else '<span class="brand-mark">C</span>'
    )
    with st.container(key="brewbound_header"):
        brand, spacer, publish, avatar = st.columns([4, 5, 2, 2])
        with brand:
            st.markdown(
                f"""
                <div class="brand-lockup">
                    {logo_html}
                    <span class="brand-copy">
                        <strong>Coffee Run</strong>
                        <small>咖啡地圖社群</small>
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("　", key="header_brand_logo"):
                st.session_state.current_page = "探索地圖"
                st.rerun()
        spacer.empty()
        if publish.button("＋　新探店貼文", key="header_new_post", help="建立探店筆記", width="stretch"):
            st.session_state.current_page = "社群"
            st.session_state.social_view = "create"
            st.rerun()
        if avatar.button(f"{display_name} 的咖啡日常", key="header_profile_link", width="stretch"):
            st.session_state.current_page = "個人頁"
            st.rerun()


def render_map(cafes, key="brewbound_map", interactive=False):
    """Render the exact cafe result set on a map.

    When interactive=True the map always uses pydeck with a hover tooltip
    showing the cafe name, rating, area, and opening hours.
    """
    map_cafes = [cafe for cafe in cafes if cafe.get("lat") is not None and cafe.get("lng") is not None]
    if not map_cafes:
        st.info("目前沒有符合條件的地圖點位。")
        return

    _FALLBACK_PHOTOS = (
        "https://images.unsplash.com/photo-1541167760496-1628856ab772?w=400&q=80",
        "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80",
        "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400&q=80",
    )

    def _cafe_photo(cafe, index):
        """Return first HTTP photo for a cafe, or a fallback Unsplash image."""
        try:
            for photo in database.get_cafe_photos(cafe["cafe_id"]):
                if isinstance(photo, str) and photo.startswith("http"):
                    return photo
        except Exception:
            pass
        return _FALLBACK_PHOTOS[index % len(_FALLBACK_PHOTOS)]

    with st.container(key=key):
        if interactive:
            map_data = pd.DataFrame([{
                "lat": cafe["lat"],
                "lon": cafe["lng"],
                "name": cafe.get("name", ""),
                "rating": f'{(cafe.get("user_rating") or cafe.get("rating") or 0):.1f}',
                "area": cafe.get("area", ""),
                "hours": cafe.get("opening_hours") or "營業時間待補",
                "image_url": _cafe_photo(cafe, i),
            } for i, cafe in enumerate(map_cafes)])
            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state=pdk.ViewState(
                        latitude=map_data["lat"].mean(),
                        longitude=map_data["lon"].mean(),
                        zoom=13,
                        pitch=0,
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_data,
                            get_position="[lon, lat]",
                            get_fill_color=[214, 83, 66, 220],
                            get_radius=80,
                            radius_min_pixels=7,
                            radius_max_pixels=18,
                            pickable=True,
                            auto_highlight=True,
                            get_highlight_color=[124, 94, 67, 255],
                        )
                    ],
                    tooltip={
                        "html": (
                            "<div style='font-family:sans-serif;width:200px;border-radius:12px;overflow:hidden;'>"
                            "<img src='{image_url}' style='width:100%;height:120px;object-fit:cover;display:block;'/>"
                            "<div style='padding:8px 12px 10px;'>"
                            "<div style='font-size:14px;font-weight:700;color:#2d241e;margin-bottom:4px;'>{name}</div>"
                            "<div style='font-size:12px;margin-bottom:3px;'>"
                            "<span style='color:#c78b35;'>★ {rating}</span>"
                            "&ensp;<span style='color:#7c5e43;'>{area}</span>"
                            "</div>"
                            "<div style='font-size:11px;color:#a8a18c;'>{hours}</div>"
                            "</div></div>"
                        ),
                        "style": {
                            "backgroundColor": "white",
                            "border": "1px solid #e6e2d3",
                            "borderRadius": "12px",
                            "boxShadow": "0 4px 16px rgba(55,37,26,0.12)",
                            "padding": "0",
                            "overflow": "hidden",
                        },
                    },
                ),
                height=480,
                use_container_width=True,
            )
            return

        static_url = google_maps.static_map_url(map_cafes, current_api_key(), width=640, height=420)
        if static_url:
            st.image(static_url, width="stretch")
        else:
            map_data = pd.DataFrame([{"lat": cafe["lat"], "lon": cafe["lng"]} for cafe in map_cafes])
            st.pydeck_chart(
                pdk.Deck(
                    map_style=None,
                    initial_view_state=pdk.ViewState(
                        latitude=map_data["lat"].mean(),
                        longitude=map_data["lon"].mean(),
                        zoom=13,
                        pitch=0,
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=map_data,
                            get_position="[lon, lat]",
                            get_fill_color=[214, 83, 66, 180],
                            get_radius=45,
                            radius_min_pixels=3,
                            radius_max_pixels=8,
                            pickable=True,
                        )
                    ],
                ),
                height=360,
                use_container_width=True,
            )


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
    photos = [path for path in database.get_cafe_photos(cafe_id) if path.startswith("http") or Path(path).exists()]
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


def render_post_images(post, small=False):
    """Render all stored photos for one post in upload order."""
    photos = [path for path in post.get("photos", []) if path.startswith("http") or Path(path).exists()]
    if not photos:
        preview_html = (
            f'<div class="post-preview post-preview-small"><img src="{POST_PREVIEW_IMAGES[post["post_id"] % len(POST_PREVIEW_IMAGES)]}" '
            f'alt="{escape(post["cafe_name"])}"><span>PIN &nbsp;{escape(post["cafe_name"])}</span></div>'
            if small else
            f'<div class="post-preview"><img src="{POST_PREVIEW_IMAGES[post["post_id"] % len(POST_PREVIEW_IMAGES)]}" '
            f'alt="{escape(post["cafe_name"])}"><span>PIN &nbsp;{escape(post["cafe_name"])}</span></div>'
        )
        st.markdown(preview_html, unsafe_allow_html=True)
        return
    if small:
        if len(photos) == 1:
            st.image(photos[0], width="stretch")
            if st.button("放大瀏覽", key=f'zoom_{post["post_id"]}_0', width="stretch"):
                st.session_state.lightbox_photo = photos[0]
                st.rerun()
        else:
            sub = st.columns(min(len(photos), 2))
            for index, path in enumerate(photos[:2]):
                sub[index].image(path, width="stretch")
            if st.button("放大瀏覽", key=f'zoom_{post["post_id"]}_multi', width="stretch"):
                st.session_state.lightbox_photo = photos[0]
                st.rerun()
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
    container = st.container(border=True, key="post_detail_card") if not open_detail else st.container(border=True)
    with container:
        st.markdown(
            f'<div class="post-location">PIN &nbsp;{escape(post["cafe_name"])}</div>'
            f'<div class="post-author">@{escape(post["username"])}'
            f'<span class="rating-pill">★ {post["rating"]}.0</span></div>',
            unsafe_allow_html=True,
        )
        render_post_images(post, small=not open_detail)
        st.markdown(f'<p class="post-copy">{escape(post["content"])}</p>', unsafe_allow_html=True)
        if post.get("tags"):
            st.markdown(
                '<div class="tag-row">' + "".join(
                    f'<span>#{escape(tag)}</span>' for tag in post["tags"]
                ) + "</div>",
                unsafe_allow_html=True,
            )
        st.caption(f'♥ {post["like_count"]}　💬 {post["comment_count"]}')

        actions = st.columns(3)
        if actions[0].button("♥" if liked else "♡", key=f'like_{post["post_id"]}_{compact}', width="stretch"):
            database.toggle_like(user_id, post["post_id"])
            st.rerun()
        if open_detail and actions[1].button("查看", key=f'post_detail_{post["post_id"]}_{compact}', width="stretch"):
            st.session_state.selected_post_id = post["post_id"]
            st.session_state.social_view = "detail"
            st.session_state.current_page = "社群"
            st.session_state.pending_nav_label = "社群"
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
