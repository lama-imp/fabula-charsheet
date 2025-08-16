import streamlit as st

from . import identity, classes, attributes, equipment, preview
from .creation_state import CreationState
from pages.controller import CharacterController


title_key = "page_title_character_creation"
icon = ":material/add_circle:"


def build():
    loc = st.session_state.localizator.get(st.session_state.language)
    st.session_state.creation_step = st.session_state.get("creation_step", CreationState.classes)
    st.session_state.creation_controller = st.session_state.get("creation_controller", CharacterController(loc))

    match st.session_state.creation_step:
        case CreationState.identity:
            identity.build(st.session_state.creation_controller)
        case CreationState.classes:
            classes.build(st.session_state.creation_controller)
        case CreationState.attributes:
            attributes.build(st.session_state.creation_controller)
        case CreationState.equipment:
            equipment.build(st.session_state.creation_controller)
        case CreationState.preview:
            preview.build(st.session_state.creation_controller)
