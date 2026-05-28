"""Community workflow: gallery feed, post detail, and publishing."""

import streamlit as st

import database
import google_maps
from api_keys import current_api_key
from components import render_post_card
from config import DEFAULT_TAGS
from file_storage import save_uploaded_files


def render_create_post_page():
    """Render the dedicated cafe review publishing view."""
    top = st.columns([1, 4])
    if top[0].button("返回", width="stretch"):
        st.session_state.social_view = "feed"
        st.rerun()
    top[1].markdown('<div class="coffee-screen-title">探店紀錄</div>', unsafe_allow_html=True)

    with st.expander("找不到想分享的咖啡廳？"):
        search_keyword = st.text_input("搜尋咖啡廳", placeholder="輸入店名或地區", key="post_cafe_google_search")
        if st.button("從 Google 加入咖啡廳", width="stretch"):
            if not current_api_key():
                st.warning("請先在「我的」設定 Google Maps API Key。")
            elif search_keyword.strip():
                try:
                    results = google_maps.search_cafes(search_keyword, current_api_key())
                    for cafe in results:
                        database.upsert_cafe(cafe)
                    st.success(f"已加入 {len(results)} 間店，可在下方選擇。")
                    st.rerun()
                except Exception as error:
                    st.error(f"搜尋失敗：{error}")

    cafes = database.list_cafes()
    if not cafes:
        st.info("請先到探索頁搜尋並加入一間咖啡廳。")
        return
    options = {f'{cafe["name"]}｜{cafe["area"]}': cafe["cafe_id"] for cafe in cafes}

    if "custom_tags" not in st.session_state:
        st.session_state.custom_tags = []

    with st.form("publish_post_form", clear_on_submit=False):
        cafe_label = st.selectbox("選擇咖啡廳", list(options))
        photos = st.file_uploader("選擇照片", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        content = st.text_area("編輯內文", placeholder="記錄這次探店體驗...")
        rating = st.slider("咖啡廳評分", 1, 5, 4)
        all_tags = DEFAULT_TAGS + st.session_state.custom_tags
        tags = st.multiselect("咖啡廳標籤", all_tags)
        new_tag_input = st.text_input("自訂標籤", placeholder="輸入標籤名稱，點「新增標籤」加入選項")
        add_tag = st.form_submit_button("新增標籤")
        submitted = st.form_submit_button("發布", width="stretch")

    if add_tag:
        tag = new_tag_input.strip()
        if tag and tag not in DEFAULT_TAGS and tag not in st.session_state.custom_tags:
            st.session_state.custom_tags.append(tag)
        st.rerun()

    if submitted:
        if not content.strip():
            st.warning("請輸入貼文內容。")
        else:
            paths = save_uploaded_files(photos, "post")
            database.create_post(
                st.session_state.user["user_id"],
                options[cafe_label],
                content,
                rating,
                paths,
                tags,
            )
            st.session_state.social_view = "feed"
            st.session_state.custom_tags = []
            st.success("已發布探店紀錄")
            st.rerun()


def render_post_detail(post_id):
    """Render one full social post with comments and cafe collection."""
    if st.session_state.get("lightbox_photo"):
        if st.button("← 返回貼文", key="lightbox_back", width="stretch"):
            st.session_state.lightbox_photo = None
            st.rerun()
        st.image(st.session_state.lightbox_photo, use_container_width=True)
        return

    if st.button("返回社群", width="stretch"):
        st.session_state.social_view = "feed"
        st.session_state.selected_post_id = None
        st.rerun()
    post = database.get_post(post_id)
    if not post:
        st.info("找不到此貼文。")
        return
    render_post_card(post, compact=True, open_detail=False)


def render_social_gallery(posts):
    """Display the BrewBound inspiration stream as rich social note cards."""
    if not posts:
        st.info("目前沒有貼文，點右上方新增第一篇探店紀錄。")
        return
    columns = st.columns(3)
    for index, post in enumerate(posts):
        with columns[index % 3]:
            render_post_card(post)


def render_social_page():
    """Route within the social feature according to user interaction."""
    if st.session_state.social_view == "create":
        render_create_post_page()
        return
    if st.session_state.social_view == "detail" and st.session_state.selected_post_id:
        render_post_detail(st.session_state.selected_post_id)
        return

    st.markdown(
        '<div class="view-heading"><h2>探索靈感</h2>'
        '<p>愛咖啡的人都在這裡，尋找與你共鳴的不限時角落。</p></div>',
        unsafe_allow_html=True,
    )
    header = st.columns([4, 1])
    search = header[0].text_input("搜尋貼文", placeholder="搜尋咖啡廳或探店心得...", label_visibility="collapsed")
    if header[1].button("新增", width="stretch"):
        st.session_state.social_view = "create"
        st.rerun()
    sort_by = st.segmented_control("排序", ["最新", "熱門"], default="熱門", label_visibility="collapsed")
    posts = database.list_posts(search=search, sort_by=sort_by or "熱門")
    render_social_gallery(posts)
