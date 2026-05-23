"""Google API key lookup used by Streamlit pages."""

import streamlit as st

import google_maps


def current_api_key():
    """Prefer sidebar input, then environment/iOS-project fallback."""
    return google_maps.get_api_key(st.session_state.get("api_key_override"))
