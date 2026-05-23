"""Explore-map page for cafe search, filtering, and cafe details."""

import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from components import render_cafe_card, render_map, render_post_card
from filters import filtered_cafes
from formatters import format_tags


def render_cafe_detail():
    """Render the selected cafe's detail section and linked social posts."""
    cafe_id = st.session_state.selected_cafe_id
    if not cafe_id:
        return

    cafe = database.get_cafe(cafe_id)
    if not cafe:
        return

    st.divider()
    st.markdown(f'<div class="coffee-section-title">{cafe["name"]}</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.write(cafe["description"])
        st.write(f'地址：{cafe["address"]}')
        if cafe["opening_hours"]:
            st.text(cafe["opening_hours"])
        if cafe["website"]:
            st.link_button("官方網站", cafe["website"])
        if cafe["maps_url"]:
            st.link_button("Google Maps", cafe["maps_url"])
        st.write(format_tags(cafe["tags"]))
        st.caption(
            f'Google 評分 {cafe["rating"]:.1f}｜'
            f'使用者評分 {cafe["user_rating"]:.1f}' if cafe["user_rating"] else f'Google 評分 {cafe["rating"]:.1f}｜使用者評分 尚無'
        )

        # Place Details is requested only when the user asks for it, so we avoid
        # unnecessary Google API cost during normal browsing.
        if cafe["google_place_id"] and current_api_key():
            if st.button("同步 Google 詳情", use_container_width=True):
                try:
                    details = google_maps.fetch_place_details(cafe["google_place_id"], current_api_key())
                    updated = dict(cafe)
                    updated.update({key: value for key, value in details.items() if value is not None})
                    database.upsert_cafe(updated)
                    st.success("已同步 Google 詳情")
                    st.rerun()
                except Exception as error:
                    st.error(f"Google 詳情同步失敗：{error}")

    posts = database.list_posts(cafe_id=cafe_id)
    st.markdown('<div class="coffee-section-title">相關貼文</div>', unsafe_allow_html=True)
    if not posts:
        st.info("目前還沒有貼文。")
    for post in posts:
        render_post_card(post, compact=True)


def render_google_search_import(api_key):
    """Render the Google Places import box at the top of explore page."""
    google_keyword = st.text_input(
        "搜尋",
        value="",
        placeholder="在這裡搜尋...",
        label_visibility="collapsed",
    )
    if st.button("搜尋並加入探索清單", use_container_width=True):
        if not api_key:
            st.warning("請先在個人頁設定 Google Maps API Key。沒有 key 時可以先使用本機範例資料。")
            return google_keyword

        try:
            cafes = google_maps.search_cafes(google_keyword, api_key)
            for cafe in cafes:
                database.upsert_cafe(cafe)
            st.success(f"已加入 {len(cafes)} 筆 Google Places 搜尋結果")
            st.rerun()
        except Exception as error:
            st.error(f"Google Places 搜尋失敗：{error}")
    return google_keyword


def render_explore_page():
    """Render map search, filters, result cards, and selected-cafe details."""
    st.markdown('<div class="coffee-screen-title">探索咖啡廳</div>', unsafe_allow_html=True)
    google_keyword = render_google_search_import(current_api_key())

    cafes = database.list_cafes()
    areas = ["全部"] + database.list_areas()
    tags = database.list_all_tags()

    quick_tags = [tag for tag in ["營業中", "深夜咖啡廳", "不限時", "插座多"] if tag in tags or tag == "營業中"]
    selected_quick_tags = st.pills("快速篩選", quick_tags, selection_mode="multi", label_visibility="collapsed") or []

    with st.expander("更多篩選", expanded=False):
        keyword = st.text_input("站內搜尋", value="", placeholder="店名、地區、特色、地址")
        area = st.selectbox("地區", areas)
        minimum_rating = st.slider("最低評分", 0.0, 5.0, 0.0, 0.5)
        selected_tags = st.multiselect("精細篩選", tags, default=[tag for tag in selected_quick_tags if tag in tags])

    results = filtered_cafes(cafes, keyword, area, minimum_rating, selected_tags)
    render_map(results)

    st.markdown('<div class="coffee-section-title">搜尋結果</div>', unsafe_allow_html=True)
    st.caption(f"找到 {len(results)} 間咖啡廳")
    for cafe in results:
        render_cafe_card(cafe)

    render_cafe_detail()
