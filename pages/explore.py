"""Explore workflow: map, filter sheet, results, and cafe details."""

import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from components import render_cafe_card, render_cafe_photos, render_map, render_post_card, toggle_favorite_button
from config import DEFAULT_TAGS, QUICK_FILTERS
from filters import filtered_cafes
from formatters import format_distance, format_tags


def render_filter_sheet(areas, tags):
    """Render the dedicated filter view shown in the wireframe."""
    header = st.columns([1, 4, 1])
    if header[0].button("返回", width="stretch"):
        st.session_state.explore_filter_open = False
        st.rerun()
    header[1].markdown('<div class="coffee-screen-title">地圖篩選</div>', unsafe_allow_html=True)

    current = st.session_state.explore_filters
    with st.form("explore_filter_form"):
        st.markdown('<div class="coffee-section-title">營業狀態</div>', unsafe_allow_html=True)
        quick_filters = st.pills(
            "特色篩選",
            QUICK_FILTERS,
            default=current["quick_filters"],
            selection_mode="multi",
            label_visibility="collapsed",
        ) or []
        st.markdown('<div class="coffee-section-title">評分與距離</div>', unsafe_allow_html=True)
        minimum_rating = st.slider("最低綜合評分", 0.0, 5.0, current["minimum_rating"], 0.5)
        distance_label = st.select_slider(
            "距離範圍",
            ["不限", "500 m", "1 km", "3 km"],
            value={None: "不限", 500: "500 m", 1000: "1 km", 3000: "3 km"}.get(current["maximum_distance"], "不限"),
        )
        area = st.selectbox("地區", areas, index=areas.index(current["area"]) if current["area"] in areas else 0)
        st.markdown('<div class="coffee-section-title">咖啡廳特色</div>', unsafe_allow_html=True)
        selected_tags = st.multiselect("標籤", sorted(set(tags + DEFAULT_TAGS)), default=current["selected_tags"])
        submitted = st.form_submit_button("套用篩選", width="stretch")
        if submitted:
            st.session_state.explore_filters = {
                **current,
                "area": area,
                "minimum_rating": minimum_rating,
                "selected_tags": selected_tags,
                "quick_filters": quick_filters,
                "maximum_distance": {"不限": None, "500 m": 500, "1 km": 1000, "3 km": 3000}[distance_label],
            }
            st.session_state.explore_filter_open = False
            st.rerun()


def render_cafe_detail(cafe_id):
    """Render cafe information inside the exploration focus panel."""
    cafe = database.get_cafe(cafe_id)
    if not cafe:
        st.session_state.selected_cafe_id = None
        return
    with st.container(key="cafe_detail_panel"):
        top = st.columns([3, 1, 1])
        top[0].markdown('<div class="coffee-screen-title">店家資訊</div>', unsafe_allow_html=True)
        if top[1].button("地圖", key="close_cafe_detail", width="stretch"):
            st.session_state.selected_cafe_id = None
            st.rerun()
        with top[2]:
            toggle_favorite_button(cafe["cafe_id"], "detail_favorite", True)

        rating = cafe["user_rating"] or cafe["rating"]
        st.markdown(f'<div class="coffee-card-title">{cafe["name"]}</div>', unsafe_allow_html=True)
        st.caption(f'{rating:.1f} ★｜{format_distance(cafe["distance_meters"])}｜{cafe["opening_hours"] or "營業時間待補"}')
        render_cafe_photos(cafe["cafe_id"])
        st.write(cafe["description"])
        st.write(format_tags(cafe["tags"]))

        if cafe["google_place_id"] and current_api_key() and st.button("同步最新店家資訊", width="stretch"):
            try:
                updated = dict(cafe)
                updated.update(google_maps.fetch_place_details(cafe["google_place_id"], current_api_key()))
                database.upsert_cafe(updated)
                st.success("已同步 Google 店家資訊")
                st.rerun()
            except Exception as error:
                st.error(f"同步失敗：{error}")
        if cafe["maps_url"]:
            st.link_button("在 Google Maps 中查看", cafe["maps_url"], width="stretch")

        posts = database.list_posts(cafe_id=cafe_id)
        st.markdown('<div class="coffee-section-title">社群探店貼文</div>', unsafe_allow_html=True)
        if not posts:
            st.info("目前還沒有貼文，前往社群成為第一位分享者。")
        for post in posts:
            render_post_card(post, compact=True)


def sync_search_results(keyword):
    """Use the single search action to refresh matching Google cafe data."""
    if not keyword.strip():
        return
    api_key = current_api_key()
    if not api_key:
        st.warning("請先到「我的」設定 Google Maps API Key。")
        return
    try:
        results = google_maps.search_cafes(keyword, api_key)
        for cafe in results:
            database.upsert_cafe(cafe)
        st.success(f"找到 {len(results)} 間咖啡廳")
    except Exception as error:
        st.error(f"Google 搜尋失敗：{error}")


def render_explore_page():
    """Render the desktop exploration workflow."""
    cafes = database.list_cafes()
    areas = ["全部"] + database.list_areas()
    tags = database.list_all_tags()
    if st.session_state.explore_filter_open:
        render_filter_sheet(areas, tags)
        return

    st.markdown('<div class="view-heading explore-title"><h2>探索地圖</h2></div>', unsafe_allow_html=True)
    search_cols = st.columns([4, 1])
    keyword = search_cols[0].text_input(
        "搜尋",
        value=st.session_state.explore_filters["keyword"],
        placeholder="搜尋內湖、深夜、不限時、甜點強...",
        label_visibility="collapsed",
    )
    if search_cols[1].button("搜尋", width="stretch"):
        st.session_state.explore_filters["keyword"] = keyword
        sync_search_results(keyword)
        st.rerun()

    st.markdown('<div class="toolbar-label">快捷篩選指標</div>', unsafe_allow_html=True)
    controls = st.columns([4, 1])
    quick_filters = controls[0].pills(
        "快速篩選",
        QUICK_FILTERS,
        default=st.session_state.explore_filters["quick_filters"],
        selection_mode="multi",
        label_visibility="collapsed",
    ) or []
    if quick_filters != st.session_state.explore_filters["quick_filters"]:
        st.session_state.explore_filters["quick_filters"] = quick_filters
        st.rerun()
    if controls[1].button("篩選", width="stretch"):
        st.session_state.explore_filter_open = True
        st.rerun()

    filters = {**st.session_state.explore_filters, "keyword": keyword, "quick_filters": quick_filters}
    results = filtered_cafes(cafes, **filters)

    results_column, focus_column = st.columns([4, 7], gap="large")
    with results_column:
        with st.container(key="explore_results_panel"):
            st.markdown(
                f'<div class="result-heading">搜尋到 <strong>{len(results)}</strong> 間合適空間</div>',
                unsafe_allow_html=True,
            )
            if not results:
                st.info("找不到符合條件的咖啡廳，請放寬篩選或重新搜尋。")
            for cafe in results:
                render_cafe_card(cafe)

    with focus_column:
        with st.container(key="explore_focus_panel"):
            if st.session_state.selected_cafe_id:
                render_cafe_detail(st.session_state.selected_cafe_id)
            else:
                render_map(results, interactive=True)
