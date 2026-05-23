"""Streamlit session-state helpers.

Streamlit reruns the script after most user interactions. Values that must
survive reruns, such as the current user or selected cafe, are stored here.
"""

import streamlit as st


def initialize_state():
    """Create session-state keys used across multiple pages."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "selected_cafe_id" not in st.session_state:
        st.session_state.selected_cafe_id = None
    if "api_key_override" not in st.session_state:
        st.session_state.api_key_override = ""
