from pathlib import Path

import streamlit as st

import config
from pages.character_view.view_state import ViewState


def set_view_state(state: ViewState):
    st.session_state.view_step = state
    st.rerun()


def get_avatar_path(char_name: str) -> Path | None:
    char_name = char_name.lower().replace(' ', '_')
    for ext in ("jpg", "jpeg", "png"):
        matches = list(config.SAVED_CHARS_IMG_DIRECTORY.glob(f"{char_name}.{ext}"))
        if matches:
            return matches[0]

    return None
