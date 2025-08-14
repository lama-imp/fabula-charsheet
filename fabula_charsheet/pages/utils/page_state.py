import streamlit as st

from pages.character_creation.creation_state import CreationState
from pages.character_view.view_state import ViewState


def set_view_state(state: ViewState):
    st.session_state.view_step = state
    st.rerun()


def set_creation_state(state: CreationState):
    st.session_state.creation_step = state
    st.rerun()
