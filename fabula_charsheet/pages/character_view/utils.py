import uuid
from pathlib import Path

import streamlit as st

import config
from pages.character_view.view_state import ViewState
from pages.controller import CharacterController
from data.models import AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, SpellTarget, Spell, SpellDuration, DamageType, Armor, Shield, Accessory, Item, \
    Skill, LocNamespace
from pages.character_creation.utils import SkillTableWriter


def set_view_state(state: ViewState):
    st.session_state.view_step = state
    st.rerun()


def get_avatar_path(char_id: uuid.UUID) -> Path | None:
    for ext in ("jpg", "jpeg", "png", "gif"):
        matches = list(config.SAVED_CHARS_IMG_DIRECTORY.glob(f"*{char_id}.{ext}"))
        if matches:
            return matches[0]

    return None


def avatar_update(controller: CharacterController, loc: LocNamespace):
    uploaded_avatar = st.file_uploader(
        "avatar uploader", accept_multiple_files=False,
        type=["jpg", "jpeg", "png", "gif"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button(loc.page_avatar_use_button, disabled=not uploaded_avatar):
        controller.dump_avatar(uploaded_avatar)
        st.rerun()


def level_up(controller: CharacterController, loc: LocNamespace):
    selected = set()
    def add_point(skill: Skill, idx=None):
        if st.checkbox(" ", key=f"{skill.name}-point", label_visibility="hidden"):
            selected.add(skill.name)
        else:
            selected.discard(skill.name)

    sorted_classes = sorted(
        [c for c in controller.character.classes if c.class_level() < 10],
        key=lambda x: x.class_level(),
        reverse=True
    )
    writer = SkillTableWriter(loc)
    writer.columns = writer.level_up_columns(add_point)
    for char_class in sorted_classes:
        st.markdown(f"#### {char_class.name.localized_name(loc)}")
        writer.write_in_columns([skill for skill in char_class.skills if skill.current_level < skill.max_level])

    if st.button(loc.confirm_button, disabled=(len(selected) != 1)):
        controller.character.level += 1
        selected_skill_name = list(selected)[0]
        for char_class in controller.character.classes:
            if char_class.get_skill(selected_skill_name):
                char_class.levelup_skill(selected_skill_name)
        st.rerun()


def add_chimerist_spell(controller: CharacterController, loc: LocNamespace):

    input_dict = {
        "name": st.text_input(loc.page_view_spell_name),
        "description": st.text_input(loc.page_view_spell_description),
        "is_offensive": st.checkbox(label=loc.page_view_spell_offensive),
        "mp_cost": st.number_input(loc.page_view_spell_mp_cost, value=0, step=5),
        "target": st.pills(loc.page_view_spell_target, [t for t in SpellTarget], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "duration": st.pills(loc.page_view_spell_duration, [t for t in SpellDuration], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "damage_type": st.pills(loc.page_view_spell_damage_type, [t for t in DamageType], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "char_class": ClassName.chimerist,
    }

    if st.button(loc.add_spell_button):
        try:
            new_spell = Spell(
                **input_dict
            )
            controller.add_spell(new_spell, ClassName.chimerist)
            st.toast(loc.page_view_spell_added.format(spell_name=input_dict['name']))
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning(loc.page_view_spell_error, icon="🪬")


def remove_chimerist_spell(controller: CharacterController, loc: LocNamespace):
    chimerist_spells = controller.character.spells[ClassName.chimerist]
    for spell in chimerist_spells:
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(spell.localized_name(loc))
        with c2:
            if st.button(loc.remove_button, key=f"{spell.name}-remove"):
                controller.remove_spell(spell, ClassName.chimerist)
                st.rerun()


def add_item(controller: CharacterController, loc: LocNamespace):
    item_type = st.segmented_control(
        loc.page_view_item_type,
        [Weapon, Armor, Shield, Accessory, Item],
        format_func=lambda x: loc[f"item_{x.__name__.lower()}"],
        selection_mode="single"
    )

    if item_type:
        name = st.text_input(loc.page_view_item_name)
        item_dict = {
            "name": name.lower() if name else name,
            "cost": st.number_input(loc.page_view_item_cost, value=0, step=50),
            "quality": st.text_input(loc.page_view_item_quality, value=loc.item_no_quality),
         }
        input_dict = {}
        if item_type.__name__ == "Weapon":
            def accuracy_input():
                st.write(loc.page_view_item_accuracy_check)
                c1, c2 = st.columns(2)
                with c1:
                    accuracy1 = st.selectbox("accuracy_selector_1",
                                             [a for a in AttributeName],
                                             key="acc-1",
                                             label_visibility="hidden",
                                             format_func=lambda x: AttributeName.to_alias(x, loc))
                with c2:
                    accuracy2 = st.selectbox("accuracy_selector_2",
                                             [a for a in AttributeName],
                                             key="acc-2",
                                             label_visibility="hidden",
                                             format_func=lambda x: AttributeName.to_alias(x, loc))

                return [accuracy1, accuracy2]

            input_dict = {
                "martial": st.checkbox(label=loc.page_view_item_martial),
                "grip_type": st.pills(loc.page_view_item_grip, [t for t in GripType], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
                "range": st.pills(loc.page_view_item_range, [t for t in WeaponRange], format_func=lambda s: s.localized_name(loc),
                                      selection_mode="single"),
                "weapon_category": st.pills(loc.page_view_item_category, [t for t in WeaponCategory], format_func=lambda s: s.localized_name(loc),
                                      selection_mode="single"),
                "damage_type": st.pills(loc.page_view_item_damage_type, [t for t in DamageType],
                                        format_func=lambda s: s.localized_name(loc), selection_mode="single"),
                "accuracy": accuracy_input(),
                "bonus_accuracy": st.number_input(loc.page_view_item_bonus_accuracy, value=0, step=1),
                "bonus_damage": st.number_input(loc.page_view_item_bonus_damage, value=0, step=1),
                # "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                # "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
            }

        if item_type.__name__ == "Armor":
            def defense_input():
                def_type = st.pills(
                    loc.page_view_item_select_defense_type,
                    [loc.page_view_item_defense_type_dexterity_dice, loc.page_view_item_defense_type_flat]
                )
                if def_type == loc.page_view_item_defense_type_dexterity_dice:
                    return AttributeName.dexterity
                elif def_type == loc.page_view_item_defense_type_flat:
                    defense = st.number_input(loc.page_view_item_provide_defense_value, value=0, step=1)
                    return defense

            input_dict = {
                "martial": st.checkbox(label=loc.page_view_item_martial),
                "defense": defense_input(),
                "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
                "bonus_initiative": st.number_input(loc.page_view_item_bonus_initiative, value=0, step=1),
            }

        if item_type.__name__ == "Shield":
            input_dict = {
                "martial": st.checkbox(label=loc.page_view_item_martial),
                "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
                "bonus_initiative": st.number_input(loc.page_view_item_bonus_initiative, value=0, step=1),
            }

    if st.button(loc.page_view_add_item_button, disabled=(not item_type)):
        try:
            combined_dict = item_dict | input_dict
            new_item = item_type(
                **combined_dict
            )
            controller.add_item(new_item)
            st.toast(loc.page_view_added_item_to_equipment.format(name=combined_dict['name']))
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning(loc.page_view_error_adding_item, icon="🪨")


def remove_item(controller: CharacterController, loc: LocNamespace):
    all_items = controller.character.inventory.backpack.all_items()
    for i, item in enumerate(all_items):
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(f"{item.__class__.__name__} - {item.name.title()}")
        with c2:
            if st.button(loc.remove_button, key=f"{item.name}-{i}-remove"):
                controller.remove_item(item)
                st.rerun()


def unequip_item(controller, category: str):
    try:
        controller.unequip_item(category)
    except Exception as e:
        st.warning(e, icon="💢")
