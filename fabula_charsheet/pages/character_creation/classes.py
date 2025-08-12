from __future__ import annotations

import streamlit as st

from data.models import LocNamespace
from pages.character_creation.creation_state import CreationState
from pages.character_creation.utils import (
    set_creation_state,
    SkillTableWriter,
    if_show_spells,
    SpellTableWriter,
    list_skills,
    show_martial,
)
from pages.controller import CharacterController, ClassController
from data import compendium as c


def add_new_class(
    character_controller: CharacterController,
    class_controller: ClassController,
    loc: LocNamespace
):
    class_not_ready = True
    selected_class_name = st.selectbox(
        loc.page_class_new_class_label,
        [char_class.name for char_class in sorted(c.COMPENDIUM.classes.classes, key=lambda x: x.name)],
        index=None,
        placeholder=loc.page_class_new_class_placeholder,
        format_func=lambda x: x.localized_name(loc),
        accept_new_options=False,
    )
    selected_class = c.COMPENDIUM.classes.get_class(selected_class_name)

    if selected_class:
        if character_controller.is_class_added(selected_class):
            st.error(loc.page_class_already_added_error)
        else:
            class_bonus = selected_class.class_bonus
            bonus_message = loc.page_class_bonus_message.format(
                class_bonus=class_bonus.localized_name(loc),
                bonus_value=selected_class.bonus_value
            )
            st.markdown(bonus_message)

            show_martial(selected_class)

            if selected_class.rituals:
                rituals_str = ', '.join(r.localized_name(loc) for r in selected_class.rituals)
                st.write(loc.page_class_rituals_info.format(rituals=rituals_str))

            class_controller.char_class = selected_class
            casting_skill = class_controller.char_class.get_spell_skill()

            with st.expander(loc.page_class_choose_skills_expander):
                SkillTableWriter().write_in_columns(selected_class.skills)

            can_add_skill_number = character_controller.can_add_skill_number()

            if class_controller.char_class.class_level() < 1:
                class_not_ready = True
                st.error(loc.error_class_need_skill)
            elif can_add_skill_number < 0:
                levels_to_remove = abs(can_add_skill_number - class_controller.char_class.class_level())
                st.error(loc.error_class_remove_skill.format(levels=levels_to_remove))
                class_not_ready = True
            else:
                list_skills(class_controller, can_add_skill_number)
                class_not_ready = False

            if if_show_spells(casting_skill):
                class_spells = c.COMPENDIUM.spells.get_spells(class_controller.char_class.name)
                with st.expander(loc.page_class_select_spells_expander):
                    SpellTableWriter().write_in_columns(class_spells)
                total_class_spells = len(st.session_state["class_spells"])
                max_n_spells = casting_skill.current_level

                if total_class_spells != max_n_spells:
                    class_not_ready = True
                    st.error(loc.page_class_select_exact_spells_error.format(
                        max_n_spells=max_n_spells,
                        casting_skill=casting_skill.name.title()
                    ))
                else:
                    class_not_ready = False

    if st.button(loc.page_class_add_button, disabled=class_not_ready):
        character_controller.add_class(class_controller.char_class)
        character_controller.character.spells[selected_class_name] = st.session_state.class_spells
        st.session_state.class_spells = []
        st.info(loc.page_class_added_info.format(selected_class=selected_class.name.localized_name(loc)))
        st.rerun()


def remove_class(character_controller: CharacterController, loc: LocNamespace):
    for char_class in character_controller.character.classes:
        c1, c2 = st.columns(2)
        with c1:
            st.write(char_class.name.title())
        with c2:
            if st.button(loc.page_class_remove_button, key=f"{char_class.name}-remove"):
                character_controller.character.classes.remove(char_class)
                st.rerun()


def build(character_controller: CharacterController):
    from data import compendium as c
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
        st.warning(loc.page_class_more_skill_points_warning.format(
            points=character_controller.can_add_skill_number()
        ), icon="🎯")
    if st.button(loc.page_next_button, disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.attributes)
