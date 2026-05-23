"""Local file-storage helpers for uploaded images."""

from pathlib import Path
from uuid import uuid4

from config import UPLOAD_DIR


def save_uploaded_file(uploaded_file, folder):
    """Persist a Streamlit uploaded file and return its local path."""
    if uploaded_file is None:
        return None

    # Use UUID filenames so two users uploading `image.jpg` do not overwrite
    # each other during a demo.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"
    filename = f"{folder}_{uuid4().hex}{suffix}"
    destination = UPLOAD_DIR / filename
    destination.write_bytes(uploaded_file.getbuffer())
    return str(destination)
