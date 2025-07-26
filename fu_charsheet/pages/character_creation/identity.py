import streamlit as st

from .creation_state import CreationState
from .utils import set_creation_state
from .controller import CharacterController
from data.models import character_themes


def build(view_model: CharacterController):
    not_ready_for_the_next_step = True
    st.title("Character's name, level, identity, origin and theme")
    character_name = st.text_input("Character name")
    character_level = st.number_input("Character level", value=5, min_value=1, max_value=60)
    identity = st.text_input("Identity")
    origin = st.text_input("Origin")
    theme = st.selectbox(
        "Character's theme",
        [theme.title() for theme in character_themes],
        index=None,
        placeholder="Select a theme or enter a new one",
        accept_new_options=True,
    )
    try:
        view_model.set_name(character_name)
        view_model.set_level(character_level)
        view_model.set_identity(identity)
        view_model.set_origin(origin)
        view_model.set_theme(theme)
        not_ready_for_the_next_step = False
    except Exception as e:
        st.error(e, icon="🚨")

    if st.button("Next", disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.classes)
