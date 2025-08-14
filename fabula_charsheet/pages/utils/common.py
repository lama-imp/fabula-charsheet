import uuid
from pathlib import Path
from copy import deepcopy
from itertools import chain

import streamlit as st

import config
from data.models import (
    Skill,
    Weapon,
    Armor,
    CharClass,
    Character,
    Shield,
    Item,
    LocNamespace, Bond, Emotion,
)
from pages.controller import ClassController, CharacterController


def get_avatar_path(char_id: uuid.UUID) -> Path | None:
    for ext in ("jpg", "jpeg", "png", "gif"):
        matches = list(config.SAVED_CHARS_IMG_DIRECTORY.glob(f"*{char_id}.{ext}"))
        if matches:
            return matches[0]

    return None


def if_show_spells(casting_skill: Skill):
    if casting_skill and casting_skill.current_level > 0:
        return True
    return False


def list_skills(class_controller: ClassController, can_add_skill_number: int):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    with st.container(border=True):
        st.subheader(loc.msg_skills_points_remaining.format(count=can_add_skill_number))
        st.write(loc.msg_skills_selected)
        for skill in class_controller.char_class.skills:
            if skill.current_level > 0:
                show_skill(skill)


def show_skill(skill: Skill):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    st.markdown(f"**{skill.localized_name(loc)}** - level {skill.current_level}")


def show_martial(input_: CharClass | Character):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    martial_keys = [
        "melee",
        "ranged",
        "armor",
        "shields",
    ]

    martial = {key: getattr(loc, key) for key in martial_keys}

    if isinstance(input_, CharClass):
        can_equip = input_.can_equip_list()
    else:
        can_equip = set(chain.from_iterable([x.can_equip_list() for x in input_.classes]))

    can_equip = [m[8:] for m in can_equip]

    if can_equip:
        can_equip_items = join_with_and([martial[m] for m in can_equip if m in martial], loc)
        st.write(loc.msg_can_equip_martial.format(items=can_equip_items))
    else:
        st.write(loc.msg_cannot_equip_martial)


def add_item_as(item: Item):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    new_name = st.text_input(loc.page_equipment_write_new_name)
    button_label = loc.page_equipment_add_item_as_button.format(name=new_name)

    if st.button(button_label, disabled= not new_name):
        item = deepcopy(item)
        item.name = new_name
        if isinstance(item, Armor):
            st.session_state.start_equipment.backpack.armors.append(item)
        elif isinstance(item, Weapon):
            st.session_state.start_equipment.backpack.weapons.append(item)
        elif isinstance(item, Shield):
            st.session_state.start_equipment.backpack.shields.append(item)
        else:
            st.error(loc.page_equipment_unknown_item_type)
            return
        st.toast(loc.page_equipment_added.format(name=new_name))
        st.session_state.start_equipment.zenit -= item.cost
        st.rerun()


def join_with_or(items, loc: LocNamespace):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + loc.or_separator + items[-1]

def join_with_and(items, loc: LocNamespace):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + loc.and_separator + items[-1]

def add_bond(controller: CharacterController, loc: LocNamespace):
    with st.expander(loc.bond_explanation):
        st.write(loc.msg_bond_explanation)
    name = st.text_input(loc.bond_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        respect = st.pills(loc.bond_respect_description, [Emotion.admiration, Emotion.inferiority],
                           format_func=lambda s: s.localized_name(loc), selection_mode="single")
    with col2:
        trust = st.pills(loc.bond_trust_description, [Emotion.loyalty, Emotion.mistrust],
                           format_func=lambda s: s.localized_name(loc), selection_mode="single")
    with col3:
        affinity = st.pills(loc.bond_affinity_description, [Emotion.affection, Emotion.hatred],
                           format_func=lambda s: s.localized_name(loc), selection_mode="single")
    input_dict = {
        "name": name,
        "respect": respect,
        "trust": trust,
        "affinity": affinity,
    }

    can_add = any(input_dict.get(k) is not None for k in ["respect", "trust", "affinity"]) and (name != "")
    if not can_add:
        st.warning(loc.adding_bond_error)

    if st.button(loc.add_bond_button,
                 key="add-bond-button",
                 disabled=not can_add
    ):
        new_bond = Bond(
            **input_dict
        )
        controller.character.bonds.append(new_bond)
        st.rerun()

def remove_bond(controller: CharacterController, loc: LocNamespace):
    for bond in controller.character.bonds:
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(f"**{bond.name}**")
            st.write(" | ".join(e for e in [bond.respect, bond.trust, bond.affinity] if e is not None))
        with c2:
            if st.button(loc.remove_button, key=f"{bond.name}-remove"):
                controller.character.bonds.remove(bond)
                st.rerun()
