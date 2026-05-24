"""Local and cloud file-storage helpers for uploaded images."""

import os
from pathlib import Path
from uuid import uuid4

import streamlit as st

from config import UPLOAD_DIR

_CONTENT_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}
_STORAGE_BUCKET = "post-photos"


def _supabase_storage_config():
    """Return (url, key) for Supabase Storage, or (None, None) if not configured."""
    def _read(key):
        val = os.environ.get(key, "").strip()
        if val:
            return val
        try:
            return str(st.secrets.get(key, "")).strip()
        except Exception:
            return ""

    url = _read("SUPABASE_URL")
    key = _read("SUPABASE_KEY")
    return (url, key) if (url and key) else (None, None)


def save_uploaded_file(uploaded_file, folder):
    """Persist a Streamlit uploaded file to Supabase Storage or local disk."""
    if uploaded_file is None:
        return None

    suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"
    filename = f"{folder}_{uuid4().hex}{suffix}"
    file_bytes = bytes(uploaded_file.getbuffer())

    supabase_url, supabase_key = _supabase_storage_config()
    if supabase_url and supabase_key:
        import requests
        content_type = _CONTENT_TYPES.get(suffix, "image/jpeg")
        upload_url = f"{supabase_url}/storage/v1/object/{_STORAGE_BUCKET}/{filename}"
        response = requests.post(
            upload_url,
            headers={"Authorization": f"Bearer {supabase_key}", "Content-Type": content_type},
            data=file_bytes,
        )
        if response.status_code in (200, 201):
            return f"{supabase_url}/storage/v1/object/public/{_STORAGE_BUCKET}/{filename}"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    destination = UPLOAD_DIR / filename
    destination.write_bytes(file_bytes)
    return str(destination)


def save_uploaded_files(uploaded_files, folder):
    """Persist multiple uploaded images while retaining their chosen order."""
    return [save_uploaded_file(uploaded_file, folder) for uploaded_file in uploaded_files or []]
