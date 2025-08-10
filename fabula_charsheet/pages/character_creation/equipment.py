import random

import streamlit as st

from .creation_state import CreationState
from .utils import set_creation_state, WeaponTableWriter, ArmorTableWriter, show_martial, ShieldTableWriter
from pages.controller import CharacterController
from data.models import Inventory, LocNamespace
from data import compendium as c




def build(controller: CharacterController):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    st.session_state.start_equipment = st.session_state.get("start_equipment", Inventory(zenit=500))
    st.session_state.additional_zenit = st.session_state.get(
        "additional_zenit",
        (random.randint(1, 6) + random.randint(1, 6)) * 10
    )
    st.title("Purchase equipment")
    st.markdown(loc.equipment_message)

    show_martial(controller.character)

    base_equipment = c.COMPENDIUM.equipment
    weapons = base_equipment.weapons_by_categories()
    with st.expander(loc.page_equipment_weapons):
        sorted_categories = sorted(weapons.keys(), key=lambda cat: cat.localized_name(loc))
        for category in sorted_categories:
            localized_cat_name = category.localized_name(loc)
            with st.expander(loc.page_equipment_category.format(name=localized_cat_name)):
                WeaponTableWriter().write_in_columns(weapons[category])
    with st.expander(loc.page_equipment_armor):
        ArmorTableWriter().write_in_columns(base_equipment.armors)
    with st.expander(loc.page_equipment_shields):
        ShieldTableWriter().write_in_columns(base_equipment.shields)

    col1, col2 = st.columns(2, border=True)
    with col1:
        if st.session_state.start_equipment.backpack.all_items():
            st.write(loc.page_equipment_added_items)
            for item in st.session_state.start_equipment.backpack.all_items():
                st.write(f"- {item.localized_name(loc)}")
        else:
            st.write(loc.page_equipment_select_items)

        if st.button(loc.page_equipment_clear_all):
            st.session_state.start_equipment = Inventory(zenit=500)
            st.rerun()
    with col2:
        st.metric(loc.page_equipment_remaining_zenit, value=st.session_state.start_equipment.zenit, delta=None, )

    st.info(loc.page_equipment_edit_warning, icon="🔱")
    st.info(loc.page_equipment_starting_zenit.format(
        zenit=st.session_state.start_equipment.zenit,
        additional_zenit=st.session_state.additional_zenit
    ), icon="💰")

    if st.button(loc.page_next_button):
        controller.character.inventory = st.session_state.start_equipment
        st.session_state.start_equipment = Inventory()
        controller.character.inventory.zenit += st.session_state.additional_zenit
        st.session_state.additional_zenit = None
        set_creation_state(CreationState.preview)
