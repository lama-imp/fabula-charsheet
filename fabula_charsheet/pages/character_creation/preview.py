from copy import deepcopy

import streamlit as st

import config
from .classes import add_new_class
from .utils import show_martial, SkillTableWriter, if_show_spells, SpellTableWriter, show_skill
from pages.controller import CharacterController, ClassController
from data.models import Dexterity, Might, Insight, Willpower, Item, CharacterTheme, CharClass, LocNamespace
from data import compendium as c
from data import saved_characters as s


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


def avatar_uploader(loc: LocNamespace):
    uploaded_avatar = st.file_uploader(
        loc.page_avatar_uploader_label,
        accept_multiple_files=False,
        type=["jpg", "jpeg", "png", "gif"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button("Use this avatar", disabled=not uploaded_avatar):
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
    if st.button(loc.page_attributes_update_button, disabled=attributes_error):
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
        SkillTableWriter().write_in_columns(class_controller.char_class.skills)

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
            SpellTableWriter().write_in_columns(class_spells)
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


def build(controller: CharacterController):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)

    @st.dialog(loc.page_class_add_dialog_title, width="large")
    @st.fragment
    def add_new_class_dialog(
            character_controller: CharacterController,
            class_controller: ClassController,
            loc: LocNamespace
    ):
        add_new_class(character_controller, class_controller, loc)

    @st.dialog(title=loc.page_avatar_uploader_title)
    def avatar_uploader_dialog():
        avatar_uploader(loc)

    @st.dialog(title=loc.page_identity_dialog_title)
    def edit_identity_dialog():
        edit_identity(controller, loc)

    @st.dialog(title=loc.page_attributes_dialog_title)
    def edit_attributes_dialog():
        edit_attributes(controller, loc)

    @st.dialog(title=loc.page_class_edit_dialog_title, width="large")
    def edit_class_dialog(char_class: CharClass):
        edit_class(controller, char_class, loc)

    st.set_page_config(layout="wide")
    st.title(loc.page_character_preview_title)

    if "avatar" not in st.session_state.keys():
        st.session_state.avatar = None

    message_col, img_col, _ = st.columns(3, gap="medium")
    if st.session_state.avatar is not None:
        controller.dump_avatar(st.session_state.avatar)
    with message_col:
        st.markdown(
            loc.page_character_preview_message.format(
                save_button=loc.page_save_character_button
            )
        )
        if st.button(loc.page_save_character_button, disabled= not controller.has_enough_skills()):
            controller.dump_character()
            controller.dump_avatar(st.session_state.avatar)
            s.SAVED_CHARS.char_list.append(controller.character)
            st.toast(loc.page_save_character_toast, icon="🧙")
        if not controller.has_enough_skills():
            st.warning(
                loc.page_character_preview_skill_points_warning.format(level=controller.character.level)
            )

    with img_col:
        if st.session_state.avatar is not None:
            st.image(st.session_state.avatar, width=150)
        else:
            st.image(config.default_avatar_path, width=150)
        if st.button(loc.page_upload_avatar_button):
            avatar_uploader_dialog(loc)


    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        i_col1, i_col2 = st.columns([0.8, 0.2])
        with i_col1:
            st.markdown(f"#### Name: {controller.character.name}")
        with i_col2:
            if st.button("Edit"):
                edit_identity_dialog(controller)
        st.write(f"{controller.character.identity} from {controller.character.origin}")
        st.markdown(f"**Theme**: {controller.character.theme}")
        st.markdown(f"**Level**: {controller.character.level}")

        a_col1, a_col2 = st.columns(2)
        with a_col1:
            st.markdown("##### Attributes")
        with a_col2:
            if st.button("Edit attributes"):
                edit_attributes_dialog(controller)
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
                    edit_class_dialog(controller, char_class)
            with c_col3:
                if st.button("Remove", key=f"{char_class.name}-remove"):
                    controller.character.classes.remove(char_class)
                    st.rerun()
            st.write("**Skills**:")
            added_skills = [skill for skill in char_class.skills if skill.current_level > 0]
            for skill in added_skills:
                st.write(f"{skill.name.title()} - level {skill.current_level}")
            if controller.character.spells.get(char_class.name, None):
                st.write("**Spells**:")
                st.write(", ".join(spell.name.title() for spell in controller.character.spells[char_class.name]))
            st.divider()
        if st.button("Add new class", disabled=controller.has_enough_skills()):
            st.session_state.class_spells = []
            add_new_class_dialog(controller, ClassController(), loc)

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
            for i, item in enumerate(getattr(controller.character.inventory.backpack, category)):
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
                                 key=f'{item.name}-{i}-equip',
                                 disabled=(item in controller.equipped_items())):
                        equip_item(controller, item)
                        st.rerun()
