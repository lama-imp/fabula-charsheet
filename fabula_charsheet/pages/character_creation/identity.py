import streamlit as st

from .creation_state import CreationState
from .utils import set_creation_state
from pages.controller import CharacterController
from data.models import CharacterTheme, LocNamespace


def build(controller: CharacterController):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    not_ready_for_the_next_step = True

    st.title(loc.page_identity_character_info_title)

    character_name = st.text_input(loc.page_identity_character_name_label)
    character_level = st.number_input(loc.page_identity_character_level_label, value=5, min_value=1, max_value=60)
    identity = st.text_input(loc.page_identity_identity_label)
    origin = st.text_input(loc.page_identity_origin_label)
    theme = st.selectbox(
        loc.page_identity_theme_label,
        [theme.localized_name(loc) for theme in CharacterTheme],
        index=None,
        placeholder=loc.page_identity_theme_placeholder,
        accept_new_options=True,
    )

    try:
        controller.character.set_name(character_name, loc)
        controller.character.set_level(character_level, loc)
        controller.character.set_identity(identity, loc)
        controller.character.set_origin(origin, loc)
        controller.character.set_theme(theme, loc)
        not_ready_for_the_next_step = False
    except Exception as e:
        st.warning(e, icon="🤌")

    if st.button(loc.page_next_button, disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.classes)
