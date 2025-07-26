import streamlit as st

from . import loader, view
from .view_state import ViewState
from pages.character_creation.controller import CharacterController


title = "Load a character"
icon = ":material/file_open:"


def build():
    st.session_state.view_step = st.session_state.get("view_step", ViewState.load)
    st.session_state.char_controller = st.session_state.get("char_controller", CharacterController())

    match st.session_state.view_step:
        case ViewState.load:
            loader.build(st.session_state.char_controller)
        case ViewState.view:
            view.build(st.session_state.char_controller)
