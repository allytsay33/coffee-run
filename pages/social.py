"""Social feed and post creation page."""

import streamlit as st

import database
from components import render_post_card
from config import DEFAULT_TAGS
from file_storage import save_uploaded_file


def render_post_form(cafes):
    """Render the form for creating a cafe-linked social post."""
    st.markdown('<div class="coffee-section-title">發文</div>', unsafe_allow_html=True)

    if not cafes:
        st.info("目前沒有咖啡廳資料，請先到探索地圖新增咖啡廳。")
        return

    cafe_options = {f'{cafe["name"]}｜{cafe["area"]}': cafe["cafe_id"] for cafe in cafes}
    with st.form("post_form", clear_on_submit=True):
        cafe_label = st.selectbox("連結咖啡廳", list(cafe_options))
        rating = st.slider("評分", 1, 5, 4)
        tags = st.multiselect("補充篩選標籤", DEFAULT_TAGS)
        content = st.text_area("內文", placeholder="分享這間咖啡廳的環境、餐點、適合情境。")
        image = st.file_uploader("上傳圖片", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("發布貼文")

        if submitted:
            if not content.strip():
                st.warning("請輸入貼文內容。")
            else:
                image_path = save_uploaded_file(image, "post")
                database.create_post(
                    st.session_state.user["user_id"],
                    cafe_options[cafe_label],
                    content,
                    rating,
                    image_path,
                    tags,
                )
                st.success("已發布貼文")
                st.rerun()


def render_social_page():
    """Render post creation followed by the latest social posts."""
    st.markdown('<div class="coffee-screen-title">社群</div>', unsafe_allow_html=True)
    cafes = database.list_cafes()
    with st.expander("發布新的探店貼文", expanded=False):
        render_post_form(cafes)

    st.markdown('<div class="coffee-section-title">最新貼文</div>', unsafe_allow_html=True)
    posts = database.list_posts()
    if not posts:
        st.info("目前還沒有貼文。")
    for post in posts:
        render_post_card(post)
