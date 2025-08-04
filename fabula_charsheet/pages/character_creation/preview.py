from copy import deepcopy
from pathlib import Path

import streamlit as st
import yaml

import config
from .classes import add_new_class
from .utils import show_martial, SkillTableWriter, if_show_spells, SpellTableWriter, show_skill
from pages.controller import CharacterController, ClassController
from data.models import Dexterity, Might, Insight, Willpower, Character, Item, character_themes, CharClass
from data import compendium as c
from data import saved_characters as s
from ..character_view.utils import set_view_state
from ..character_view.view_state import ViewState

preview_message = """Take a look at your character.

If everything is OK, click on `Save character`.
"""


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


@st.dialog(title="Upload your avatar")
def avatar_uploader():
    uploaded_avatar = st.file_uploader(
        "avatar uploader", accept_multiple_files=False,
        type=["jpg", "jpeg", "png"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button("Use this avatar", disabled=not uploaded_avatar):
        st.session_state.avatar = uploaded_avatar
        st.rerun()


@st.dialog(title="Edit your name, identity, origin or theme.")
def edit_identity(controller: CharacterController):
    character_name = st.text_input("Name", value=controller.character.name)
    identity = st.text_input("Identity", value=controller.character.identity)
    origin = st.text_input("Origin", value=controller.character.origin)
    theme = st.selectbox(
        "Theme",
        [theme.title() for theme in character_themes],
        index=character_themes.index(controller.character.theme.lower()),
        placeholder="Select a theme or enter a new one",
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


@st.dialog(title="Edit attributes.")
def edit_attributes(controller: CharacterController):
    dexterity = st.select_slider(
        "Dexterity",
        options=[6, 8, 10, 12],
        value=controller.character.dexterity.base,
    )
    might = st.select_slider(
        "Might",
        options=[6, 8, 10, 12],
        value=controller.character.might.base,
    )
    insight = st.select_slider(
        "Insight",
        options=[6, 8, 10, 12],
        value=controller.character.insight.base,
    )
    willpower = st.select_slider(
        "Willpower",
        options=[6, 8, 10, 12],
        value=controller.character.willpower.base,
    )
    attributes_error = (sum([dexterity, might, insight, willpower]) != 32)
    if attributes_error:
        st.warning("Sum of your attributes should be equal to 32.", icon="🎲")
    if st.button("Update", disabled=attributes_error):
        try:
            controller.character.dexterity = Dexterity(base=dexterity, current=dexterity)
            controller.character.might = Might(base=might, current=might)
            controller.character.insight = Insight(base=insight, current=insight)
            controller.character.willpower = Willpower(base=willpower, current=willpower)
            st.rerun()
        except Exception as e:
            st.error(e, icon="🚨")


@st.dialog(title="Edit this class", width="large")
def edit_class(character_controller: CharacterController, char_class: CharClass):
    class_controller = ClassController()
    class_controller.char_class = deepcopy(char_class)
    casting_skill = class_controller.char_class.get_spell_skill()
    st.session_state.class_spells = character_controller.character.spells[char_class.name]

    with st.expander("Choose skills"):
        SkillTableWriter().write_in_columns(class_controller.char_class.skills)

    can_add_skill_number = character_controller.can_add_skill_number()

    if class_controller.char_class.class_level() < 1:
        class_not_ready = True
        st.error("You need to select at least one skill to keep this class.")
    elif can_add_skill_number < 0:
        st.error(
            f"Remove {abs(can_add_skill_number)} level(s) from your skills.")
        class_not_ready = True
    else:
        st.write("You have selected following skills:")
        for skill in class_controller.char_class.skills:
            if skill.current_level > 0:
                show_skill(skill)
        class_not_ready = False

    if if_show_spells(casting_skill):
        class_spells = c.COMPENDIUM.spells.get_spells(class_controller.char_class.name)
        with st.expander("Select spells"):
            SpellTableWriter().write_in_columns(class_spells)
        total_class_spells = len(st.session_state["class_spells"])
        max_n_spells = casting_skill.current_level

        if total_class_spells != max_n_spells:
            class_not_ready = True
            st.error(f"You need to select exactly {max_n_spells} spells (one for each level in {casting_skill.name.title()}).")
        else:
            class_not_ready = False

    if st.button("Update class", disabled=class_not_ready):
        try:
            character_controller.update_class(class_controller.char_class)
            character_controller.character.spells[char_class.name] = st.session_state.class_spells
            st.session_state.class_spells = []
            st.info(f"Updated {char_class.name.title()}.")
            st.rerun()
        except Exception as e:
            st.error(e, icon="🚨")


def build(controller: CharacterController):
    st.set_page_config(layout="wide")
    st.title("Character preview")
    if "avatar" not in st.session_state.keys():
        st.session_state.avatar = None

    message_col, img_col, _ = st.columns(3, gap="medium")
    if st.session_state.avatar is not None:
        controller.dump_avatar(st.session_state.avatar)
    with message_col:
        st.markdown(preview_message)
        if st.button("Save character", disabled= not controller.has_enough_skills()):
            controller.dump_character()
            controller.dump_avatar(st.session_state.avatar)
            s.SAVED_CHARS.char_list.append(controller.character)
            st.toast("Now you can load your character.", icon="🧙")
        if not controller.has_enough_skills():
            st.warning(f"You need to put exactly {controller.character.level} points to your skills.")

    with img_col:
        if st.session_state.avatar is not None:
            st.image(st.session_state.avatar, width=150)
        else:
            st.image(config.default_avatar_path, width=150)
        if st.button("Upload avatar"):
            avatar_uploader()


    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        i_col1, i_col2 = st.columns([0.8, 0.2])
        with i_col1:
            st.markdown(f"#### Name: {controller.character.name}")
        with i_col2:
            if st.button("Edit"):
                edit_identity(controller)
        st.write(f"{controller.character.identity} from {controller.character.origin}")
        st.markdown(f"**Theme**: {controller.character.theme}")
        st.markdown(f"**Level**: {controller.character.level}")

        a_col1, a_col2 = st.columns(2)
        with a_col1:
            st.markdown("##### Attributes")
        with a_col2:
            if st.button("Edit attributes"):
                edit_attributes(controller)
        st.write(f"Dexterity: d{controller.character.dexterity.base}")
        st.write(f"Might: d{controller.character.might.base}")
        st.write(f"Insight: d{controller.character.insight.base}")
        st.write(f"Willpower: d{controller.character.willpower.base}")
        st.write("")
        st.markdown(f"**HP**: {controller.max_hp()} | **MP**: {controller.max_mp()} | **IP**: {controller.max_ip()}")
        st.markdown(f"**Defense**: {controller.defense()} | **Magic Defense**: {controller.magic_defense()}")

    with col2:
        st.markdown("#### Classes")
        if not controller.has_enough_skills():
            pass
        sorted_classes = sorted(controller.character.classes, key=lambda x: x.class_level(), reverse=True)
        for char_class in sorted_classes:
            c_col1, c_col2, c_col3 = st.columns(3)
            with c_col1:
                st.markdown(f"##### {char_class.name.title()}")
            with c_col2:
                if st.button("Edit", key=f"{char_class.name}-edit"):
                    edit_class(controller, char_class)
            with c_col3:
                if st.button("Remove", key=f"{char_class.name}-remove"):
                    controller.character.classes.remove(char_class)
                    st.rerun()
            st.write("**Skills**:")
            added_skills = [s for s in char_class.skills if s.current_level > 0]
            for skill in added_skills:
                st.write(f"{skill.name.title()} - level {skill.current_level}")
            if controller.character.spells.get(char_class.name, None):
                st.write("**Spells**:")
                st.write(", ".join(spell.name.title() for spell in controller.character.spells[char_class.name]))
            st.divider()
        if st.button("Add new class", disabled=controller.has_enough_skills()):
            add_new_class(controller, ClassController())

    with col3:
        st.markdown("#### Equipment")
        st.write(f"You have {controller.character.inventory.zenit} zenit")
        st.markdown("**EQUIPPED**")
        equipped_categories = ["weapon", "armor", "shield"]
        for category in equipped_categories:
            eq_col1, eq_col_2 = st.columns([0.7, 0.3])
            with eq_col1:
                equipped_item = getattr(controller.character.inventory.equipped, category)
                if isinstance(equipped_item, list):
                    equipped_item_str = ' | '.join([w.name.title() for w in equipped_item if w])
                else:
                    equipped_item_str = equipped_item.name.title() if equipped_item else ''
                st.markdown(f"**{category.title()}**: {equipped_item_str}")
            with eq_col_2:
                if st.button("Unequip",
                          key=f"{category}-unequip",
                          disabled=(not equipped_item)):
                    unequip_item(controller, category)
                    st.rerun()
        show_martial(controller.character)
        categories = [k for k, v in controller.character.inventory.backpack.model_dump().items() if v]
        st.markdown("**INVENTORY**")
        for category in categories:
            for item in getattr(controller.character.inventory.backpack, category):
                if category == "armors":
                    formatter = f"{'Martial ' if item.martial else ''}Armor - "
                elif category == "weapons":
                    formatter = f"{'Martial ' if item.martial else ''}{item.range.title()} {item.grip_type.replace('_', '-').title()} Weapon - "
                elif category == "shields":
                    formatter = f"{'Martial ' if item.martial else ''}Shield - "
                else:
                    formatter = ""
                item_name_col, item_button_col = st.columns([0.7, 0.3])
                with item_name_col:
                    st.write(f"{formatter}**{item.name.title()}**")
                with item_button_col:
                    if st.button('Equip',
                                 key=f'{item.name}-equip',
                                 disabled=(item in controller.equipped_items())):
                        equip_item(controller, item)
                        st.rerun()
