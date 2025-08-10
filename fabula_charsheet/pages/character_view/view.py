import streamlit as st

import config
from data.models import Status, AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, SpellTarget, Spell, SpellDuration, DamageType, Armor, Shield, Accessory, Item, \
    Skill
from pages.controller import CharacterController
from pages.character_creation.utils import WeaponTableWriter, ArmorTableWriter, SkillTableWriter, SpellTableWriter, \
    AccessoryTableWriter, ItemTableWriter, TherioformTableWriter, ShieldTableWriter
from pages.character_view.utils import set_view_state, get_avatar_path
from pages.character_view.view_state import ViewState


@st.dialog(title="Update your avatar")
def avatar_update(controller: CharacterController):
    uploaded_avatar = st.file_uploader(
        "avatar uploader", accept_multiple_files=False,
        type=["jpg", "jpeg", "png", "gif"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button("Use this avatar", disabled=not uploaded_avatar):
        controller.dump_avatar(uploaded_avatar)
        st.rerun()


@st.dialog("Select a skill to increase by 1 point.", width="large")
def level_up(controller: CharacterController):
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
    writer = SkillTableWriter()
    writer.columns = writer.level_up_columns(add_point)
    for char_class in sorted_classes:
        st.markdown(f"#### {char_class.name.title()}")
        writer.write_in_columns([skill for skill in char_class.skills if skill.current_level < skill.max_level])

    if st.button("Confirm", disabled=(len(selected) != 1)):
        controller.character.level += 1
        selected_skill_name = list(selected)[0]
        for char_class in controller.character.classes:
            if char_class.get_skill(selected_skill_name):
                char_class.levelup_skill(selected_skill_name)
        st.rerun()


@st.dialog("Add a Chimerist spell")
def add_chimerist_spell(controller: CharacterController):
    def prepare_spell_attributes(attribute_name, attribute_value):
        if attribute_name == "name":
            return attribute_value.lower()
        if attribute_value == "No damage":
            return None
        return attribute_value
    input_dict = {
        "name": st.text_input("Spell name"),
        "description": st.text_input("Spell description"),
        "is_offensive": st.checkbox(label="Offensive"),
        "mp_cost": st.number_input("MP cost", value=0, step=5),
        "target": st.pills("Target", [t for t in SpellTarget], format_func=lambda s: s.replace('_', ' ').title(), selection_mode="single"),
        "duration": st.pills("Duration", [t for t in SpellDuration], format_func=lambda s: s.replace('_', ' ').title(), selection_mode="single"),
        "damage_type": st.pills("Damage type", ["No damage"] + [t for t in DamageType], format_func=lambda s: s.replace('_', ' ').title(), selection_mode="single"),
        "char_class": ClassName.chimerist,
    }

    if st.button("Add this spell"):
        try:
            new_spell = Spell(
                **{k: prepare_spell_attributes(k, v) for k, v in input_dict.items()}
            )
            controller.add_spell(new_spell, ClassName.chimerist)
            st.toast(f"Added spell {input_dict['name']} to your spell list.")
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning("Error adding a spell. Maybe some fields are empty?", icon="🪬")


@st.dialog("Remove a Chimerist spell")
def remove_chimerist_spell(controller: CharacterController):
    chimerist_spells = controller.character.spells[ClassName.chimerist]
    for spell in chimerist_spells:
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(spell.name.title())
        with c2:
            if st.button("Remove", key=f"{spell.name}-remove"):
                controller.remove_spell(spell, ClassName.chimerist)
                st.rerun()


@st.dialog("Add an item")
def add_item(controller: CharacterController):
    item_type = st.segmented_control("Item type", [Weapon, Armor, Shield, Accessory, Item], format_func=lambda x: x.__name__, selection_mode="single")

    if item_type:
        name = st.text_input("Item name")
        item_dict = {
            "name": name.lower() if name else name,
            "cost": st.number_input("Cost in zenit", value=0, step=50),
            "quality": st.text_input("Item quality", value="No Quality"),
         }
        input_dict = {}
        if item_type.__name__ == "Weapon":
            def accuracy_input():
                st.write("Accuracy check")
                c1, c2 = st.columns(2)
                with c1:
                    accuracy1 = st.selectbox("", [a for a in AttributeName], key="acc-1", label_visibility="hidden",
                                             format_func=lambda x: AttributeName.to_alias(x))
                with c2:
                    accuracy2 = st.selectbox("", [a for a in AttributeName], key="acc-2", label_visibility="hidden",
                                             format_func=lambda x: AttributeName.to_alias(x))

                return [accuracy1, accuracy2]

            input_dict = {
                "martial": st.checkbox(label="Martial"),
                "grip_type": st.pills("Grip", [t for t in GripType], format_func=lambda s: s.replace('_', ' ').title(), selection_mode="single"),
                "range": st.pills("Range", [t for t in WeaponRange], format_func=lambda s: s.replace('_', ' ').title(),
                                      selection_mode="single"),
                "weapon_category": st.pills("Category", [t for t in WeaponCategory], format_func=lambda s: s.replace('_', ' ').title(),
                                      selection_mode="single"),
                "damage_type": st.pills("Damage type", [t for t in DamageType],
                                        format_func=lambda s: s.replace('_', ' ').title(), selection_mode="single"),
                "accuracy": accuracy_input(),
                "bonus_accuracy": st.number_input("Bonus to accuracy check", value=0, step=1),
                "bonus_damage": st.number_input("Bonus to damage", value=0, step=1),
                "bonus_defense": st.number_input("Bonus to physical defense", value=0, step=1),
                "bonus_magic_defense": st.number_input("Bonus to magic defense", value=0, step=1),
            }

        if item_type.__name__ == "Armor":
            def defense_input():
                def_type = st.pills("Select defense type", ["Dexterity dice", "Flat"])
                if def_type == "Dexterity dice":
                    return AttributeName.dexterity
                elif def_type == "Flat":
                    defense = st.number_input("Provide the defense value", value=0, step=1)
                    return defense

            input_dict = {
                "martial": st.checkbox(label="Martial"),
                "defense": defense_input(),
                "bonus_defense": st.number_input("Bonus to defense", value=0, step=1),
                "bonus_magic_defense": st.number_input("Bonus to magic defense", value=0, step=1),
                "bonus_initiative": st.number_input("Bonus to initiative", value=0, step=1),
            }

        if item_type.__name__ == "Shield":
            input_dict = {
                "martial": st.checkbox(label="Martial"),
                "bonus_defense": st.number_input("Bonus to defense", value=0, step=1),
                "bonus_magic_defense": st.number_input("Bonus to magic defense", value=0, step=1),
                "bonus_initiative": st.number_input("Bonus to initiative", value=0, step=1),
            }

        if item_type.__name__ == "Accessory":
            input_dict = {
                "effect": st.text_input("Effect")
            }

    if st.button("Add this item", disabled=(not item_type)):
        try:
            combined_dict = item_dict | input_dict
            new_item = item_type(
                **combined_dict
            )
            controller.add_item(new_item)
            st.toast(f"Added {combined_dict['name']} to your equipment.")
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning("Error adding an item. Maybe some fields are empty?", icon="🪨")


@st.dialog("Remove an item")
def remove_item(controller: CharacterController):
    all_items = controller.character.inventory.backpack.all_items()
    for i, item in enumerate(all_items):
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(f"{item.__class__.__name__} - {item.name.title()}")
        with c2:
            if st.button("Remove", key=f"{item.name}-{i}-remove"):
                controller.remove_item(item)
                st.rerun()


def build(controller: CharacterController):
    st.set_page_config(layout="wide")
    st.session_state.state_controller = st.session_state.get("state_controller")
    st.title(f"{controller.character.name}")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Skills", "Spells", "Equipment", "Special"])

    # Overview
    with tab1:
        base_col, points_col, attributes_col = st.columns([0.35, 0.4, 0.25], gap="medium")
        with base_col:
            col1, col2 = st.columns(2)
            with col1:
                avatar_path = get_avatar_path(controller.character.id)
                if avatar_path:
                    st.image(avatar_path, use_container_width=True)
                else:
                    st.image(config.default_avatar_path, width=150)
                if st.button("Update avatar"):
                    avatar_update(controller)
            with col2:
                st.write(f"{controller.character.identity} from {controller.character.origin}")
                st.markdown(f"**Level**: {controller.character.level}")
                st.markdown(f"**Theme**: {controller.character.theme}")
                st.number_input("**Fabula Points**", min_value=0)
                current_hp = (controller.max_hp() - st.session_state.state_controller.state.minus_hp)
                if current_hp <= controller.crisis_value():
                    st.write(":red[CRISIS]")
                else:
                    st.write("")
                if st.button("Level up!"):
                    level_up(controller)
            st.markdown("##### Base Attributes")
            st.write(f"Dexterity: d{controller.character.dexterity.base}")
            st.write(f"Might: d{controller.character.might.base}")
            st.write(f"Insight: d{controller.character.insight.base}")
            st.write(f"Willpower: d{controller.character.willpower.base}")
            st.write("")
            st.markdown(
                f"**Max HP**: {controller.max_hp()} | **Max MP**: {controller.max_mp()} | **Max IP**: {controller.max_ip()}")

        with points_col:
            col1, col2, col3, col4, col5 = st.columns([0.5, 0.2, 0.1, 0.1, 0.1])
            with col1:
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: green;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                current_hp = (controller.max_hp() - st.session_state.state_controller.state.minus_hp)
                st.progress(max((current_hp / controller.max_hp()), 0), text=f"HP {current_hp}")
                st.write("")
                st.write("")

                current_mp = (controller.max_mp() - st.session_state.state_controller.state.minus_mp)
                st.progress(max((current_mp / controller.max_mp()), 0), text=f"MP {current_mp}")
                st.write("")
                st.write("")

                current_ip = (controller.max_ip() - st.session_state.state_controller.state.minus_ip)
                st.progress(max((current_ip / controller.max_ip()), 0), text=f"IP {current_ip}")
            with col2:
                hp_input = st.number_input("hp_input", min_value=0, label_visibility="hidden", value=10)
                mp_input = st.number_input("mp_input", min_value=0, label_visibility="hidden", value=10)
                ip_input = st.number_input("ip_input", min_value=0, label_visibility="hidden", value=3)
            with col3:
                st.write("")
                if st.button("", icon=":material/add:", key="add_hp"):
                    st.session_state.state_controller.state.minus_hp = max(0, st.session_state.state_controller.state.minus_hp - hp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/add:", key="add_mp"):
                    st.session_state.state_controller.state.minus_mp = max(0, st.session_state.state_controller.state.minus_mp - mp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/add:", key="add_ip"):
                    st.session_state.state_controller.state.minus_ip = max(0, st.session_state.state_controller.state.minus_ip - ip_input)
                    st.rerun()
                st.write("")
                st.write("")
            with col4:
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_hp"):
                    st.session_state.state_controller.state.minus_hp = min(controller.max_hp(), st.session_state.state_controller.state.minus_hp + hp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_mp"):
                    st.session_state.state_controller.state.minus_mp = min(controller.max_mp(), st.session_state.state_controller.state.minus_mp + mp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_ip"):
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(), st.session_state.state_controller.state.minus_ip + ip_input)
                    st.rerun()
                st.write("")
                st.write("")
            with col5:
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_hp", help="Reset HP"):
                    st.session_state.state_controller.state.minus_hp = 0
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_mp", help="Reset MP"):
                    st.session_state.state_controller.state.minus_mp = 0
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_ip", help="Reset IP"):
                    st.session_state.state_controller.state.minus_ip = 0
                    st.rerun()
                st.write("")
                st.write("")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Health Potion", disabled=(current_ip < 3)):
                    st.session_state.state_controller.state.minus_hp = max(0, st.session_state.state_controller.state.minus_hp - 50)
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(),
                                                                     st.session_state.state_controller.state.minus_ip + 3)
                    st.rerun()
            with col2:
                if st.button("Mana Potion", disabled=(current_ip < 3)):
                    st.session_state.state_controller.state.minus_mp = max(0, st.session_state.state_controller.state.minus_mp - 50)
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(),
                                                                     st.session_state.state_controller.state.minus_ip + 3)
                    st.rerun()
            with col3:
                if st.button("Magic Tent", disabled=(current_ip < 4)):
                    st.session_state.state_controller.state.minus_hp = 0
                    st.session_state.state_controller.state.minus_mp = 0
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(),
                                                                     st.session_state.state_controller.state.minus_ip + 4)
                    st.rerun()

            st.write("##### Equipped:")
            st.write("**Weapon**")
            equipped_weapon = controller.character.inventory.equipped.weapon
            if not equipped_weapon:
                equipped_weapon = [
                    Weapon(
                        name="unarmed strike",
                        cost=0,
                        quality="Automatically equipped in each empty hand slot",
                        martial=False,
                        grip_type=GripType.one_handed,
                        range=WeaponRange.melee,
                        weapon_category=WeaponCategory.brawling,
                        accuracy=[AttributeName.dexterity, AttributeName.might],
                    )
                ]
            for i, weapon in enumerate(equipped_weapon):
                c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.3, 0.1])
                with c1:
                    st.markdown("⚔️")
                    st.write(weapon.name.title())
                with c2:
                    st.markdown("_Accuracy_")
                    accuracy_str = (" + ".join([f"d{getattr(controller.character, attribute).current }"for attribute in weapon.accuracy]))
                    st.write(accuracy_str)
                with c3:
                    st.markdown("_Damage_")
                    st.write(f"【HR + {weapon.bonus_damage}】 {weapon.damage_type}")
                with c4:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"{weapon.name}-{i}-unequip",
                            help="Unequip this item",
                            disabled=(weapon.name == "unarmed strike")
                        ):
                        unequip_item(controller, "weapon")
                        st.rerun()
                st.write(
                    " ◆ ".join((
                        weapon.grip_type.title().replace('_', '-'),
                        weapon.range.title(),
                        weapon.quality,
                    ))
                )

            armor = controller.character.inventory.equipped.armor
            if armor:
                st.write("**Armor**")
                c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.3, 0.1])
                with c1:
                    st.markdown("🧥")
                    st.write(armor.name.title())
                with c2:
                    st.markdown("_Defense_")
                    if isinstance(armor.defense, AttributeName):
                        def_bonus = f" + {armor.bonus_defense}" if armor.bonus_defense > 0 else ""
                        st.write(f"d{str(getattr(controller.character, armor.defense).current)}{def_bonus}")
                    else:
                        st.write(str(armor.defense))
                with c3:
                    st.markdown("_M.Defense_")
                    if isinstance(armor.magic_defense, AttributeName):
                        def_bonus = f" + {armor.bonus_magic_defense}" if armor.bonus_magic_defense > 0 else ""
                        st.write(f"d{str(getattr(controller.character, armor.magic_defense).current)}{def_bonus}")
                    else:
                        st.write(str(armor.magic_defense))
                with c4:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"armor-unequip",
                            help="Unequip this item",
                        ):
                        unequip_item(controller, "armor")
                        st.rerun()
                st.write(f"{armor.quality} ◆ Initiative: {armor.bonus_initiative}")

            shield = controller.character.inventory.equipped.shield
            if shield:
                st.write("**Shield**")
                c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.3, 0.1])
                with c1:
                    st.markdown("🛡️")
                    st.write(shield.name.title())
                with c2:
                    st.markdown("_Defense_")
                    st.write(str(shield.bonus_defense))
                with c3:
                    st.markdown("_M.Defense_")
                    st.write(str(shield.bonus_magic_defense))
                with c4:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"shield-unequip",
                            help="Unequip this item",
                        ):
                        unequip_item(controller, "shield")
                        st.rerun()
                st.write(f"{shield.quality} ◆ Initiative: {shield.bonus_initiative}")

            accessory = controller.character.inventory.equipped.accessory
            if accessory:
                st.write("**Accessory**")
                c1, c2, c3 = st.columns([0.4, 0.5, 0.1])
                with c1:
                    st.write(accessory.name.title())
                with c2:
                    st.write(accessory.quality)
                with c3:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"accessory-unequip",
                            help="Unequip this item",
                        ):
                        unequip_item(controller, "accessory")
                        st.rerun()


        with attributes_col:
            st.markdown("##### Current Attributes")
            att_col1, att_col2 = st.columns(2)

            st.markdown(f"**Initiative**: {controller.initiative()}")

            st.markdown("##### Statuses")
            col1, col2 = st.columns(2)
            for idx, stat in enumerate(Status):
                if idx < 3:
                    with col1:
                        st.session_state.state_controller.remove_status(stat)

                        if st.checkbox(f"{stat.title()}"):
                            st.session_state.state_controller.add_status(stat)
                else:
                    with col2:
                        st.session_state.state_controller.remove_status(stat)

                        if st.checkbox(f"{stat.title()}"):
                            st.session_state.state_controller.add_status(stat)

            changes = controller.apply_status(st.session_state.state_controller.state.statuses)
            for attribute, value in changes.items():
                if value > 0:
                    st.toast(f"Your {attribute} is lowered by {value}!")
            if st.button("Refresh current attributes"):
                st.rerun()

            with att_col1:
                st.write(f"**Dexterity**: d{controller.character.dexterity.current}")
                st.write(f"**Might**: d{controller.character.might.current}")
                st.markdown(f"**Defense**: {controller.defense()}")
            with att_col2:
                st.write(f"**Insight**: d{controller.character.insight.current}")
                st.write(f"**Willpower**: d{controller.character.willpower.current}")
                st.markdown(f"**Magic Defense**: {controller.magic_defense()}")

        st.divider()

    # Skills
    with tab2:
        sorted_classes = sorted(controller.character.classes, key=lambda x: x.class_level(), reverse=True)
        writer = SkillTableWriter()
        writer.columns = writer.level_readonly_columns
        for char_class in sorted_classes:
            st.markdown(f"#### {char_class.name.title()}")
            writer.write_in_columns([skill for skill in char_class.skills if skill.current_level > 0])

        st.divider()

    # Spells
    with tab3:
        for char_class, spell_list in controller.character.spells.items():
            chimerist_skills = controller.get_skills(ClassName.chimerist)
            chimerist_condition = (char_class == ClassName.chimerist
                                   and "spell mimic" in [s.name for s in chimerist_skills])
            if spell_list or chimerist_condition:
                writer = SpellTableWriter()
                writer.columns = writer.columns[:-1]
                chimerist_message = ""
                if chimerist_condition:
                    max_n_spells = controller.get_skill_level(ClassName.chimerist, "spell mimic")
                    if "chimeric mastery" in [s.name for s in chimerist_skills]:
                        max_n_spells += 2
                    chimerist_message = f" ({len(spell_list)} from {max_n_spells})"
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"#### {char_class.title()} spells{chimerist_message}")
                with c2:
                    if chimerist_condition:
                        if st.button("Learn a Chimerist spell", disabled=(len(spell_list) == max_n_spells)):
                            add_chimerist_spell(controller)
                with c3:
                    if chimerist_condition:
                        if st.button("Forget a Chimerist spell", disabled=(len(spell_list) < 1)):
                            remove_chimerist_spell(controller)
                writer.write_in_columns(spell_list)

    #Equipment
    with tab4:
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("Add item"):
                add_item(controller)
        with col2:
            if st.button("Remove item"):
                remove_item(controller)
        backpack = controller.character.inventory.backpack
        if backpack.weapons:
            weapon_writer = WeaponTableWriter()
            weapon_writer.columns = weapon_writer.equip_columns
            weapon_writer.write_in_columns(backpack.weapons)
        if backpack.armors:
            armor_writer = ArmorTableWriter()
            armor_writer.columns = armor_writer.equip_columns
            armor_writer.write_in_columns(backpack.armors)
        if backpack.shields:
            shield_writer = ShieldTableWriter()
            shield_writer.columns = shield_writer.equip_columns
            shield_writer.write_in_columns(backpack.shields)
        if backpack.accessories:
            AccessoryTableWriter().write_in_columns(backpack.accessories)
        if backpack.other:
            ItemTableWriter().write_in_columns(backpack.other)

    # Special
    with tab5:
        if controller.is_class_added(ClassName.mutant) and controller.has_skill("theriomorphosis"):
            therioforms = controller.character.special.get_special("therioforms")
            added_therioforms = [t for t in therioforms if t.added]
            st.markdown("##### Therioforms")
            TherioformTableWriter().write_in_columns(added_therioforms)
            if len(added_therioforms) < controller.get_skill_level(ClassName.mutant, "theriomorphosis"):
                if st.button("Add a therioform"):
                    pass
        st.divider()

    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if st.button("Save current character"):
            controller.dump_character()
            st.session_state.state_controller.dump_state()
    with col2:
        if st.button("Load another character"):
            set_view_state(ViewState.load)

def unequip_item(controller, category: str):
    try:
        controller.unequip_item(category)
    except Exception as e:
        st.warning(e, icon="💢")
