import streamlit as st

import config
from data import saved_characters as s
from data.models import Character, LocNamespace
from pages.controller import CharacterController
from pages.utils import set_view_state, get_avatar_path, delete_character
from pages.character_view.view_state import ViewState


def build(controller: CharacterController):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)

    @st.dialog(title=loc.page_delete_character_title)
    def delete_character_dialog(character: Character, loc: LocNamespace):
        delete_character(character, loc)

    st.set_page_config(layout="centered")
    st.title(loc.page_load_character_title)

    if s.SAVED_CHARS.char_list:
        for char in s.SAVED_CHARS.char_list:
            col1, col2, col3 = st.columns(3)
            with col1:
                avatar_path = get_avatar_path(char.id)
                if avatar_path:
                    st.image(avatar_path, width=150)
                else:
                    st.image(config.default_avatar_path, width=150)
            with col2:
                st.write(loc.page_load_character_info.format(name=char.name, level=char.level))
            with col3:
                load_col, delete_col = st.columns(2)
                with load_col:
                    if st.button(loc.page_load_character_load_button, key=f"{char.id}-loader"):
                        controller.character = char
                        try:
                            controller.load_state()
                        except Exception as e:
                            st.toast(e)
                        set_view_state(ViewState.view)
                with delete_col:
                    if st.button(loc.page_load_character_delete_button, key=f"{char.id}-delete"):
                        delete_character_dialog(char, loc)

            st.divider()
    else:
        st.info(loc.page_load_character_no_saved, icon="👻")
