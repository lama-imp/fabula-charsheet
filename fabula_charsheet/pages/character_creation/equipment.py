import random

import streamlit as st

from .creation_state import CreationState
from .utils import set_creation_state, WeaponTableWriter, ArmorTableWriter, show_martial, ShieldTableWriter
from pages.controller import CharacterController
from data.models import Inventory
from data import compendium as c

equipment_message = """You get a total budget of 500 zenit to purchase equipment with. By default, you can only purchase basic weapons and basic armor and shields; these items are listed on the next four pages for easy reference. If you want to purchase rare items (page 266) or transports (page 125), discuss it with the rest of your group.

To purchase a martial (♦️) item, you must first be able to equip it — a benefit granted by specific Classes.

Needless to say, you are free to alter the name of any item that doesn't fit your character's concept — for instance, your bronze sword might become a scimitar or your silk vest might become a kimono.
"""


def build(controller: CharacterController):
    st.session_state.start_equipment = st.session_state.get("start_equipment", Inventory(zenit=500))
    st.session_state.additional_zenit = st.session_state.get(
        "additional_zenit",
        (random.randint(1, 6) + random.randint(1, 6)) * 10
    )
    st.title("Purchase equipment")
    st.markdown(equipment_message)

    show_martial(controller.character)
    st.warning("If you want to add several identical items, use `Add as` button to add the 2nd one and change the name (e.g., add `2` to it).",
               icon="‼️")

    base_equipment = c.COMPENDIUM.equipment
    weapons = base_equipment.weapons_by_categories()
    with st.expander("Weapons"):
        sorted_categories = sorted(weapons.keys())
        for category in sorted_categories:
            with st.expander(f"{category.title()} category"):
                WeaponTableWriter().write_in_columns(weapons[category])
    with st.expander("Armor"):
        ArmorTableWriter().write_in_columns(base_equipment.armors)
    with st.expander("Shields"):
        ShieldTableWriter().write_in_columns(base_equipment.shields)

    col1, col2 = st.columns(2, border=True)
    with col1:
        if st.session_state.start_equipment.backpack.all_items():
            st.write("You added following items:")
            for item in st.session_state.start_equipment.backpack.all_items():
                st.write(f"- {item.name.title()}")
        else:
            st.write("Select your starting equipment from above.")
        if st.button("Clear all added items"):
            st.session_state.start_equipment = Inventory(zenit=500)
            st.rerun()
    with col2:
        st.metric("Your remaining zenit", value=st.session_state.start_equipment.zenit, delta=None, )

    st.info("You will not be able to edit your starting equipment on the next step.", icon="🔱")
    st.info(f"You start with {st.session_state.start_equipment.zenit} + {st.session_state.additional_zenit} zenit ", icon="💰")

    if st.button("Next"):
        controller.character.inventory = st.session_state.start_equipment
        st.session_state.start_equipment = Inventory()
        controller.character.inventory.zenit += st.session_state.additional_zenit
        st.session_state.additional_zenit = None
        set_creation_state(CreationState.preview)
