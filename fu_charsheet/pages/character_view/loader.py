import streamlit as st

from data import compendium as c
from data import saved_characters as s
from pages.character_creation.controller import CharacterController
from pages.character_view.utils import set_view_state, get_avatar_path
from pages.character_view.view_state import ViewState

st.set_page_config(layout="centered")

def build(controller: CharacterController):
    st.title("Load a character")
    if s.SAVED_CHARS:
        for char in s.SAVED_CHARS.char_list:
            col1, col2, col3 = st.columns(3)
            with col1:
                avatar_path = get_avatar_path(char.name)
                if avatar_path:
                    st.image(avatar_path, width=150)
                else:
                    st.write("No avatar")
            with col2:
                st.write(f"{char.name}, level {char.level}")
            with col3:
                if st.button("Load", key=f"{char.name}-loader"):
                    controller.character = char
                    set_view_state(ViewState.view)
            st.divider()
    else:
        st.write("No saved characters. Start with creating a character.")

