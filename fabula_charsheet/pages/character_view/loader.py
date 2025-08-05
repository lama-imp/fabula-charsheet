from pathlib import Path

import streamlit as st

import config
from data import saved_characters as s
from data.models import Character
from pages.controller import CharacterController
from pages.character_view.utils import set_view_state, get_avatar_path
from pages.character_view.view_state import ViewState

st.set_page_config(layout="centered")


@st.dialog(title="Delete a character")
def delete_character(character: Character):
    st.warning("Are you sure you want to completely delete this character?", icon="❓")
    c1, c2 = st.columns([0.2, 0.8])
    with c1:
        if st.button("No"):
            st.rerun()
    with c2:
        if st.button(f"Yes, delete {character.name.title()}", icon="💀"):
            s.SAVED_CHARS.char_list.remove(character)
            char_path = Path(config.SAVED_CHARS_DIRECTORY, f"{character.name.lower().replace(' ', '_')}.yaml")
            try:
                char_path.unlink()
            except FileNotFoundError:
                st.error("Character file does not exist.", icon="📜")
            except PermissionError:
                st.error("You do not have permission to delete this character file.", icon="🔒")
            avatar_path = get_avatar_path(character.name)
            if avatar_path:
                try:
                    avatar_path.unlink()
                    st.rerun()
                except PermissionError:
                    st.error("You do not have permission to delete this character avatar.", icon="🔒")
            else:
                st.rerun()


def build(controller: CharacterController):
    st.title("Load a character")
    if s.SAVED_CHARS.char_list:
        for char in s.SAVED_CHARS.char_list:
            col1, col2, col3 = st.columns(3)
            with col1:
                avatar_path = get_avatar_path(char.name)
                if avatar_path:
                    st.image(avatar_path, width=150)
                else:
                    st.image(config.default_avatar_path, width=150)
            with col2:
                st.write(f"{char.name}, level {char.level}")
            with col3:
                load_col, delete_col = st.columns(2)
                with load_col:
                    if st.button("Load", key=f"{char.name}-loader"):
                        controller.character = char
                        set_view_state(ViewState.view)
                with delete_col:
                    if st.button("Delete", key=f"{char.name}-delete"):
                        delete_character(char)

            st.divider()
    else:
        st.info("No saved characters. Start with creating a character.", icon="👻")

