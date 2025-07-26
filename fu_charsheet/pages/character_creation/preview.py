import json

import streamlit as st
import yaml

from .creation_state import CreationState
from .utils import set_creation_state, WeaponTableWriter, ArmorTableWriter, show_martial
from .controller import CharacterController, ClassController
from data.models.character_config import ClassName, ClassBonus, Ritual, Skill, Dexterity, Might, Insight, Willpower, \
    Inventory, Character, Armor, Weapon, Shield, Item, Accessory
from data import compendium as c

preview_message = """Take a look at your character.

If everything is OK, click on `Save character`.
"""



@st.dialog(title="Upload your avatar")
def avatar_uploader():
    st.session_state.avatar = st.file_uploader(
        "avatar uploader", accept_multiple_files=False,
        type=["jpg", "jpeg", "png"],
        label_visibility="hidden"
    )
    if st.session_state.avatar is not None:
        st.image(st.session_state.avatar, width=100)

def build(controller: CharacterController):
    st.set_page_config(layout="wide")
    st.title("Character preview")
    if "avatar" not in st.session_state.keys():
        st.session_state.avatar = None

    message_col, save_col, img_col = st.columns([0.3, 0.3, 0.4])
    if st.session_state.avatar is not None:
        controller.dump_avatar(st.session_state.avatar)
    with message_col:
        st.markdown(preview_message)

    with save_col:
        if st.button("Save character"):
            controller.dump_character()
        if st.button("Upload avatar"):
            avatar_uploader()
        if st.button("Show avatar"):
            with img_col:
                if st.session_state.avatar is not None:
                    st.image(st.session_state.avatar, width=100)
                else:
                    st.write("No avatar")


    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"#### Name: {controller.character.name}")
        st.write(f"{controller.character.identity} from {controller.character.origin}")
        st.markdown(f"**Level**: {controller.character.level}")
        st.markdown(f"**Theme**: {controller.character.theme}")

        st.markdown("##### Attributes")
        st.write(f"Dexterity: d{controller.character.dexterity.base}")
        st.write(f"Might: d{controller.character.might.base}")
        st.write(f"Insight: d{controller.character.insight.base}")
        st.write(f"Willpower: d{controller.character.willpower.base}")
        st.write("")
        st.markdown(f"**HP**: {controller.max_hp()} | **MP**: {controller.max_mp()} | **IP**: {controller.max_ip()}")
        st.markdown(f"**Defense**: {controller.defense()} | **Magic Defense**: {controller.magic_defense()}")

    with col2:
        st.markdown("#### Classes")
        sorted_classes = sorted(controller.character.classes, key=lambda x: x.class_level(), reverse=True)
        for char_class in sorted_classes:
            st.markdown(f"##### {char_class.name.title()}")
            st.write("Skills:")
            for skill in char_class.skills:
                st.write(f"{skill.name.title()} - level {skill.current_level}")
            st.divider()

    with col3:
        st.markdown("#### Equipment")
        st.write(f"{controller.character.inventory.zenit} zenit")
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
        # st.markdown(f"**Armor**: {equipped.armor.name.title() if equipped.armor else ''}")
        # st.markdown(f"**Weapon**: {")
        # st.markdown(f"**Shield**: {equipped.shield.name.title() if equipped.shield else ''}")
        categories = [k for k, v in controller.character.inventory.backpack.model_dump().items() if v]
        st.markdown("**INVENTORY**")
        for category in categories:
            # st.write(category.title())
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

def equip_item(controller, item: Item):
    try:
        controller.equip_item(item)
    except Exception as e:
        st.warning(e)


def unequip_item(controller, category: str):
    try:
        controller.unequip_item(category)
    except Exception as e:
        st.warning(e)


def disable_equip_button(controller, item: Item) -> bool:
    equipped_items = controller.equipped_items()
    return item in equipped_items
