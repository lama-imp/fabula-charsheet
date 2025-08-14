from copy import deepcopy

import streamlit as st

from pages.utils import SkillTableWriter, if_show_spells, SpellTableWriter, show_skill
from pages.controller import CharacterController, ClassController
from data.models import Dexterity, Might, Insight, Willpower, Item, CharacterTheme, CharClass, LocNamespace
from data import compendium as c


def equip_item(controller, item: Item):
    try:
        controller.equip_item(item)
    except Exception as e:
        st.warning(e, icon="🙅‍♂️")


def unequip_item(controller, category: str):
    try:
        controller.unequip_item(category)
    except Exception as e:
        st.warning(e)


def disable_equip_button(controller, item: Item) -> bool:
    equipped_items = controller.equipped_items()
    return item in equipped_items


def avatar_uploader(loc: LocNamespace):
    uploaded_avatar = st.file_uploader(
        loc.msg_upload_avatar,
        accept_multiple_files=False,
        type=["jpg", "jpeg", "png", "gif"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button(loc.use_avatar_button, disabled=not uploaded_avatar):
        st.session_state.avatar = uploaded_avatar
        st.rerun()


def edit_identity(controller: CharacterController, loc: LocNamespace):
    character_name = st.text_input(loc.page_identity_character_name_label, value=controller.character.name)
    identity = st.text_input(loc.page_identity_identity_label, value=controller.character.identity)
    origin = st.text_input(loc.page_identity_origin_label, value=controller.character.origin)
    if controller.character.theme:
        if controller.character.theme in CharacterTheme:
            default_theme_idx = list(CharacterTheme).index(controller.character.theme)
            options = [theme.localized_name(loc) for theme in CharacterTheme]
        else:
            options = [controller.character.theme] + [theme.localized_name(loc) for theme in CharacterTheme]
            default_theme_idx = None
    else:
        options = [theme.localized_name(loc) for theme in CharacterTheme]
        default_theme_idx = None
    theme = st.selectbox(
        loc.page_identity_theme_label,
        options,
        index=default_theme_idx,
        placeholder=loc.page_identity_theme_placeholder,
        accept_new_options=True,
    )
    if st.button("Update"):
        try:
            controller.character.set_name(character_name)
            controller.character.set_identity(identity)
            controller.character.set_origin(origin)
            controller.character.set_theme(theme)
            st.rerun()
        except Exception as e:
            st.warning(e, icon="🤌")


def edit_attributes(controller: CharacterController, loc: LocNamespace):
    dexterity = st.select_slider(
        loc.attr_dexterity,
        options=[6, 8, 10, 12],
        value=controller.character.dexterity.base,
    )
    might = st.select_slider(
        loc.attr_might,
        options=[6, 8, 10, 12],
        value=controller.character.might.base,
    )
    insight = st.select_slider(
        loc.attr_insight,
        options=[6, 8, 10, 12],
        value=controller.character.insight.base,
    )
    willpower = st.select_slider(
        loc.attr_willpower,
        options=[6, 8, 10, 12],
        value=controller.character.willpower.base,
    )
    attributes_error = (sum([dexterity, might, insight, willpower]) != 32)
    if attributes_error:
        st.warning(loc.page_attributes_sum_error, icon="🎲")
    if st.button(loc.attributes_update_button, disabled=attributes_error):
        try:
            controller.character.dexterity = Dexterity(base=dexterity, current=dexterity)
            controller.character.might = Might(base=might, current=might)
            controller.character.insight = Insight(base=insight, current=insight)
            controller.character.willpower = Willpower(base=willpower, current=willpower)
            st.rerun()
        except Exception as e:
            st.error(e, icon="🚨")


def edit_class(character_controller: CharacterController, char_class: CharClass, loc: LocNamespace):
    class_controller = ClassController()
    class_controller.char_class = deepcopy(char_class)
    casting_skill = class_controller.char_class.get_spell_skill()
    st.session_state.class_spells = character_controller.character.spells[char_class.name]

    with st.expander(loc.page_class_choose_skills):
        SkillTableWriter(loc).write_in_columns(class_controller.char_class.skills)

    can_add_skill_number = character_controller.can_add_skill_number()

    if class_controller.char_class.class_level() < 1:
        class_not_ready = True
        st.error(loc.page_class_error_min_skill)
    elif can_add_skill_number < 0:
        st.error(loc.page_class_error_remove_skills.format(n=abs(can_add_skill_number)))
        class_not_ready = True
    else:
        st.write(loc.page_class_selected_skills)
        for skill in class_controller.char_class.skills:
            if skill.current_level > 0:
                show_skill(skill)
        class_not_ready = False

    if if_show_spells(casting_skill):
        class_spells = c.COMPENDIUM.spells.get_spells(class_controller.char_class.name)
        with st.expander(loc.page_class_select_spells):
            SpellTableWriter(loc).write_in_columns(class_spells)
        total_class_spells = len(st.session_state["class_spells"])
        max_n_spells = casting_skill.current_level

        if total_class_spells != max_n_spells:
            class_not_ready = True
            st.error(loc.page_class_error_spell_count.format(n=max_n_spells, skill=casting_skill.name.title()))
        else:
            class_not_ready = False

    if st.button(loc.page_class_update_button, disabled=class_not_ready):
        try:
            character_controller.update_class(class_controller.char_class)
            character_controller.character.spells[char_class.name] = st.session_state.class_spells
            st.session_state.class_spells = []
            st.info(loc.page_class_updated.format(class_name=char_class.name.title()))
            st.rerun()
        except Exception as e:
            st.error(e, icon="🚨")
