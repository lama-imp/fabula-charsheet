from __future__ import annotations

import streamlit as st

from data.models import LocNamespace
from pages.character_creation.creation_state import CreationState
from pages.utils import set_creation_state, add_new_class, remove_class
from pages.controller import CharacterController, ClassController


def build(character_controller: CharacterController):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    st.session_state.class_controller = ClassController()
    st.session_state.class_spells = st.session_state.get("class_spells", [])
    not_ready_for_the_next_step = not character_controller.has_enough_skills()
    st.title(loc.page_class_title)
    current_classes = character_controller.get_character().classes

    @st.dialog(loc.page_class_add_dialog_title, width="large")
    @st.fragment
    def add_new_class_dialog(
            character_controller: CharacterController,
            class_controller: ClassController,
            loc: LocNamespace
    ):
        add_new_class(character_controller, class_controller, loc)


    @st.dialog(loc.page_class_remove_dialog_title, width="large")
    @st.fragment
    def remove_class_dialog(character_controller: CharacterController, loc: LocNamespace):
        remove_class(character_controller, loc)


    st.write(loc.page_class_current_classes_info.format(
        count=len(current_classes),
        classes=', '.join([c.name.title() for c in current_classes])
    ))
    st.write(loc.page_class_skills_added_info.format(
        added=character_controller.get_character().get_n_skill(),
        available=character_controller.get_character().level
    ))

    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button(loc.page_class_add_class_button, disabled=character_controller.has_enough_skills()):
            add_new_class_dialog(character_controller, st.session_state.class_controller, loc)
    with col_2:
        if st.button(loc.page_class_remove_class_button, disabled=not character_controller.character.classes):
            remove_class_dialog(character_controller, loc)

    if not_ready_for_the_next_step:
        st.warning(loc.warn_more_skill_points_needed.format(
            points=character_controller.can_add_skill_number()
        ), icon="🎯")
    if st.button(loc.page_next_button, disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.attributes)
