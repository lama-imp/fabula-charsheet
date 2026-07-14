import streamlit as st

import config
from data import saved_characters as s
from data.models import Character, LocNamespace
from .common import get_avatar_path


def delete_character(character: Character, loc: LocNamespace):
    st.warning(loc.page_delete_character_warning, icon="❓")
    c1, c2 = st.columns([0.2, 0.8])
    with c1:
        if st.button(loc.no_button):
            st.rerun()
    with c2:
        if st.button(
                    loc.page_delete_character_yes_button.format(name=character.name.title()),
                    icon="💀"
                ):
            s.SAVED_CHARS.char_list.remove(character)
            char_paths = list(config.SAVED_CHARS_DIRECTORY.glob(f"*.{character.id}.character.yaml"))
            if not char_paths:
                st.error(loc.page_delete_character_file_missing, icon="📜")
            for char_path in char_paths:
                try:
                    char_path.unlink()
                except PermissionError:
                    st.error(loc.page_delete_character_file_permission, icon="🔒")
            avatar_path = get_avatar_path(character.id)
            if avatar_path:
                try:
                    avatar_path.unlink()
                    st.rerun()
                except PermissionError:
                    st.error(loc.page_delete_character_avatar_permission, icon="🔒")
            else:
                st.rerun()
