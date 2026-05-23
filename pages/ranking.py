"""Cafe ranking page."""

import streamlit as st

import database
from formatters import format_distance, format_tags


def render_ranking_page():
    """Render cafes sorted by user rating, falling back to Google rating."""
    st.markdown('<div class="coffee-screen-title">推薦排行</div>', unsafe_allow_html=True)
    cafes = database.list_cafes()
    ranked = sorted(cafes, key=lambda cafe: cafe["user_rating"] or cafe["rating"], reverse=True)

    for index, cafe in enumerate(ranked, start=1):
        with st.container(border=True):
            st.markdown(f'<div class="coffee-card-title">{index}. {cafe["name"]}</div>', unsafe_allow_html=True)
            st.write(
                f'綜合評分 {(cafe["user_rating"] or cafe["rating"]):.1f}｜'
                f'{cafe["area"]}｜{format_distance(cafe["distance_meters"])}'
            )
            st.write(cafe["description"])
            st.write(format_tags(cafe["tags"]))
