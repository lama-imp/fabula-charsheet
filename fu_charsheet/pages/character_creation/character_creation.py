import json

import streamlit as st

from data.models import Character
from . import identity, classes, attributes, equipment, preview
from .creation_state import CreationState
from .controller import CharacterController


title = "Create a character"
icon = ":material/add_circle:"


def build():
    st.session_state.creation_step = st.session_state.get("creation_step", CreationState.identity)
    st.session_state.creation_controller = st.session_state.get("creation_controller", CharacterController())

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
