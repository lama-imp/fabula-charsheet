from __future__ import annotations

from typing import Literal

import streamlit as st

from data.models import LocNamespace, ClassBonus
from .table_writer import SkillTableWriter, SpellTableWriter
from .common import if_show_spells, list_skills, show_martial
from pages.controller import CharacterController, ClassController
from data import compendium as c


def add_new_class(
    character_controller: CharacterController,
    class_controller: ClassController,
    loc: LocNamespace,
    mode: Literal["creation", "addition"] = "creation"
):
    st.session_state.class_not_ready = True
    if mode == "creation":
        available_classes = [char_class.name for char_class in sorted(c.COMPENDIUM.classes.classes, key=lambda x: x.name)]
    else:

        available_classes = [char_class.name for char_class in
                             sorted(c.COMPENDIUM.classes.classes, key=lambda x: x.name)
                             if char_class.name not in [
                                 added_class.name for added_class in character_controller.character.classes
                             ]
        ]
    selected_class_name = st.selectbox(
        loc.page_class_new_class_label,
        available_classes,
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
            class_controller.char_class = selected_class

            show_bonus(class_controller, loc)

            show_martial(selected_class)

            if selected_class.rituals:
                rituals_str = ', '.join(r.localized_name(loc) for r in selected_class.rituals)
                st.write(loc.page_class_rituals_info.format(rituals=rituals_str))

            casting_skill = class_controller.char_class.get_spell_skill()

            with st.expander(loc.page_class_choose_skills_expander):
                writer = SkillTableWriter(loc)
                if mode == "addition":
                    writer.columns = writer.level_up_new_class_columns
                writer.write_in_columns(selected_class.skills)

            can_add_skill_number = character_controller.can_add_skill_number()

            if class_controller.char_class.class_level() < 1:
                st.session_state.class_not_ready = True
                st.error(loc.error_class_need_skill)
            elif can_add_skill_number < 0:
                levels_to_remove = abs(can_add_skill_number - class_controller.char_class.class_level())
                st.error(loc.error_class_remove_skill.format(levels=levels_to_remove))
                st.session_state.class_not_ready = True
            else:
                list_skills(class_controller, can_add_skill_number)
                st.session_state.class_not_ready = False

            if if_show_spells(casting_skill):
                class_spells = c.COMPENDIUM.spells.get_spells(class_controller.char_class.name)

                if mode == "creation":
                    max_n_spells = casting_skill.current_level
                else:
                    class_spells = [spell for spell in class_spells if
                                    spell not in character_controller.character.get_spells_by_class(selected_class_name)]
                    max_n_spells = 1

                with st.expander(loc.page_class_select_spells_expander):
                    SpellTableWriter(loc).write_in_columns(class_spells)
                total_class_spells = len(st.session_state["class_spells"])

                if total_class_spells != max_n_spells:
                    st.session_state.class_not_ready = True
                    st.error(loc.error_class_select_exact_spells.format(
                        max_n_spells=max_n_spells,
                        casting_skill=casting_skill.localized_name(loc)
                    ))
                else:
                    st.session_state.class_not_ready = False

    if mode == "creation":
        if st.button(loc.page_class_add_button, disabled=st.session_state.class_not_ready):
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


def show_bonus(class_controller: ClassController, loc: LocNamespace):
    if isinstance(class_controller.char_class.class_bonus, list):
        class_bonus = st.pills(
            loc.msg_select_bonus,
            [b for b in class_controller.char_class.class_bonus],
            format_func=lambda b: b.localized_full_name(loc),
        )
        class_controller.char_class.class_bonus = class_bonus
        if class_bonus:
            bonus_message = loc.page_class_bonus_message.format(
                class_bonus=class_bonus.localized_name(loc),
                bonus_value=class_controller.char_class.bonus_value
            )
            st.markdown(bonus_message)
    elif isinstance(class_controller.char_class.class_bonus, ClassBonus):
        class_bonus = class_controller.char_class.class_bonus
        bonus_message = loc.page_class_bonus_message.format(
            class_bonus=class_bonus.localized_name(loc),
            bonus_value=class_controller.char_class.bonus_value
        )
        st.markdown(bonus_message)
