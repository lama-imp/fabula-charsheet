import streamlit as st

import config
from data.models import Status, AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, LocNamespace
from pages.controller import CharacterController
from pages.utils import WeaponTableWriter, ArmorTableWriter, SkillTableWriter, SpellTableWriter, \
    AccessoryTableWriter, ItemTableWriter, TherioformTableWriter, ShieldTableWriter, BondTableWriter, \
    show_martial, set_view_state, get_avatar_path, avatar_update, level_up, add_chimerist_spell, \
    remove_chimerist_spell, add_item, remove_item, unequip_item, add_heroic_skill, add_spell, add_bond, remove_bond, \
    increase_attribute
from pages.character_view.view_state import ViewState


def build(controller: CharacterController):
    st.set_page_config(layout="wide")
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    st.session_state.state_controller = st.session_state.get("state_controller")

    @st.dialog(loc.page_view_avatar_update_dialog_title)
    def avatar_update_dialog(controller: CharacterController, loc: LocNamespace):
        avatar_update(controller, loc)

    @st.dialog(loc.page_view_level_up_dialog_title, width="large")
    def level_up_dialog(controller: CharacterController, loc: LocNamespace):
        level_up(controller, loc)

    @st.dialog(loc.page_view_add_heroic_skill_dialog_title, width="large")
    def add_heroic_skill_dialog(controller: CharacterController, loc: LocNamespace):
        add_heroic_skill(controller, loc)

    @st.dialog(loc.page_view_add_chimerist_spell_dialog_title, width="large")
    def add_chimerist_spell_dialog(controller: CharacterController, loc: LocNamespace):
        add_chimerist_spell(controller, loc)

    @st.dialog(loc.page_view_add_spell_dialog_title, width="large")
    def add_spell_dialog(
            controller: CharacterController,
            class_name: ClassName,
            loc: LocNamespace
    ):
        add_spell(controller, class_name, loc)

    @st.dialog(loc.page_view_remove_chimerist_spell_dialog_title, width="large")
    def remove_chimerist_spell_dialog(controller: CharacterController, loc: LocNamespace):
        remove_chimerist_spell(controller, loc)

    @st.dialog(loc.page_view_add_item_dialog_title, width="large")
    def add_item_dialog(controller: CharacterController, loc: LocNamespace):
        add_item(controller, loc)

    @st.dialog(loc.page_view_remove_item_dialog_title, width="large")
    def remove_item_dialog(controller: CharacterController, loc: LocNamespace):
        remove_item(controller, loc)

    @st.dialog(loc.page_view_add_bond_dialog_title, width="large")
    def add_bond_dialog(controller: CharacterController, loc: LocNamespace):
        add_bond(controller, loc)

    @st.dialog(loc.page_view_remove_bond_dialog_title, width="large")
    def remove_bond_dialog(controller: CharacterController, loc: LocNamespace):
        remove_bond(controller, loc)

    @st.dialog(loc.page_view_increase_attribute_dialog_title, width="small")
    def increase_attribute_dialog(controller: CharacterController, loc: LocNamespace):
        increase_attribute(controller, loc)

    st.title(f"{controller.character.name}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        loc.page_view_tab_overview,
        loc.page_view_tab_skills,
        loc.page_view_tab_spells,
        loc.page_view_tab_equipment,
        loc.page_view_tab_special,
    ])

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
                if st.button(loc.update_avatar_button):
                    avatar_update_dialog(controller, loc)
            with col2:
                st.write(loc.page_view_identity_origin.format(
                    identity=controller.character.identity,
                    origin=controller.character.origin
                ))
                st.markdown(f"**{loc.page_view_level}:** {controller.character.level}")
                st.markdown(f"**{loc.page_view_theme}:** {controller.character.theme}")
                st.number_input(loc.page_view_fabula_points, min_value=0)
                current_hp = (controller.max_hp() - st.session_state.state_controller.state.minus_hp)
                if current_hp <= controller.crisis_value():
                    st.write(f":red[{loc.page_view_crisis_text}]")
                else:
                    st.write("")
                if st.button(loc.page_view_level_up_button):
                    level_up_dialog(controller, loc)
                if controller.can_add_heroic_skill():
                    if st.button(loc.heroic_skill_button):
                        add_heroic_skill_dialog(controller, loc)
                if controller.character.level == 20 or controller.character.level == 40:
                    if st.button(loc.increase_attribute_button):
                        increase_attribute_dialog(controller, loc)

            st.markdown(f"##### {loc.page_view_base_attributes}")
            st.write(f"{loc.attr_dexterity}: {loc.dice_prefix}{controller.character.dexterity.base}")
            st.write(f"{loc.attr_might}: {loc.dice_prefix}{controller.character.might.base}")
            st.write(f"{loc.attr_insight}: {loc.dice_prefix}{controller.character.insight.base}")
            st.write(f"{loc.attr_willpower}: {loc.dice_prefix}{controller.character.willpower.base}")
            st.write("")
            st.markdown(
                f"**{loc.hp}**: {controller.max_hp()} | **{loc.mp}**: {controller.max_mp()} | **{loc.ip}**: {controller.max_ip()}")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"##### {loc.bonds}")
            with col2:
                if st.button(loc.add_bond_button):
                    add_bond_dialog(controller, loc)
            with col3:
                if st.button(loc.remove_bond_button):
                    remove_bond_dialog(controller, loc)

            writer = BondTableWriter(loc)
            writer.write_in_columns(controller.character.bonds, header=False)


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
                st.progress(max((current_hp / controller.max_hp()), 0), text=f"{loc.hp} {current_hp} / {controller.max_hp()}")
                st.write("")
                st.write("")

                current_mp = (controller.max_mp() - st.session_state.state_controller.state.minus_mp)
                st.progress(max((current_mp / controller.max_mp()), 0), text=f"{loc.mp} {current_mp} / {controller.max_mp()}")
                st.write("")
                st.write("")

                current_ip = (controller.max_ip() - st.session_state.state_controller.state.minus_ip)
                st.progress(max((current_ip / controller.max_ip()), 0), text=f"{loc.ip} {current_ip} / {controller.max_ip()}")
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
                if st.button(loc.page_view_health_potion, disabled=(current_ip < 3), use_container_width=True):
                    st.session_state.state_controller.state.minus_hp = max(0, st.session_state.state_controller.state.minus_hp - 50)
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(),
                                                                     st.session_state.state_controller.state.minus_ip + 3)
                    st.rerun()
            with col2:
                if st.button(loc.page_view_mana_potion, disabled=(current_ip < 3), use_container_width=True):
                    st.session_state.state_controller.state.minus_mp = max(0, st.session_state.state_controller.state.minus_mp - 50)
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(),
                                                                     st.session_state.state_controller.state.minus_ip + 3)
                    st.rerun()
            with col3:
                if st.button(loc.page_view_magic_tent, disabled=(current_ip < 4), use_container_width=True):
                    st.session_state.state_controller.state.minus_hp = 0
                    st.session_state.state_controller.state.minus_mp = 0
                    st.session_state.state_controller.state.minus_ip = min(controller.max_ip(),
                                                                     st.session_state.state_controller.state.minus_ip + 4)
                    st.rerun()

            st.write(f"##### {loc.page_view_equipped}")
            st.write(f"**{loc.item_weapon}**")
            equipped_weapon = controller.character.inventory.equipped.weapon
            if not equipped_weapon:
                equipped_weapon = [
                    Weapon(
                        name="unarmed_strike",
                        cost=0,
                        quality=loc.unarmed_strike_quality,
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
                    st.write(weapon.localized_name(loc))
                with c2:
                    st.markdown(f"_{loc.column_accuracy}_")
                    accuracy_str = (" + ".join([f"{loc.dice_prefix}{getattr(controller.character, attribute).current }"for attribute in weapon.accuracy]))
                    st.write(accuracy_str)
                with c3:
                    st.markdown(f"_{loc.column_damage}_")
                    st.markdown(f"{loc.hr} + {weapon.bonus_damage}\n\n{weapon.damage_type.localized_name(loc)}")
                with c4:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"{weapon.name}-{i}-unequip",
                            help=loc.page_view_unequip_help,
                            disabled=(weapon.name == "unarmed_strike")
                        ):
                        unequip_item(controller, "weapon")
                        st.rerun()
                st.write(
                    " ◆ ".join((
                        weapon.grip_type.localized_name(loc),
                        weapon.range.localized_name(loc),
                        weapon.localized_quality(loc),
                    ))
                )

            armor = controller.character.inventory.equipped.armor
            if armor:
                st.write(f"**{loc.column_armor}**")
                c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.3, 0.1])
                with c1:
                    st.markdown("🧥")
                    st.write(armor.localized_name(loc))
                with c2:
                    st.markdown(f"_{loc.column_defense}_")
                    if isinstance(armor.defense, AttributeName):
                        def_bonus = f" + {armor.bonus_defense}" if armor.bonus_defense > 0 else ""
                        st.write(f"{loc.dice_prefix}{str(getattr(controller.character, armor.defense).current)}{def_bonus}")
                    else:
                        st.write(str(armor.defense))
                with c3:
                    st.markdown(f"_{loc.column_magic_defense}_")
                    if isinstance(armor.magic_defense, AttributeName):
                        def_bonus = f" + {armor.bonus_magic_defense}" if armor.bonus_magic_defense > 0 else ""
                        st.write(f"{loc.dice_prefix}{str(getattr(controller.character, armor.magic_defense).current)}{def_bonus}")
                    else:
                        st.write(str(armor.magic_defense))
                with c4:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"armor-unequip",
                            help=loc.page_view_unequip_help,
                        ):
                        unequip_item(controller, "armor")
                        st.rerun()
                st.write(f"{armor.localized_quality(loc)} ◆ {loc.column_initiative}: {armor.bonus_initiative}")

            shield = controller.character.inventory.equipped.shield
            if shield:
                st.write(f"**{loc.column_shield}**")
                c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.3, 0.1])
                with c1:
                    st.markdown("🛡️")
                    st.write(shield.localized_name(loc))
                with c2:
                    st.markdown(f"_{loc.column_defense}_")
                    st.write(str(shield.bonus_defense))
                with c3:
                    st.markdown(f"_{loc.column_magic_defense}_")
                    st.write(str(shield.bonus_magic_defense))
                with c4:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"shield-unequip",
                            help=loc.page_view_unequip_help,
                        ):
                        unequip_item(controller, "shield")
                        st.rerun()
                st.write(f"{shield.localized_quality(loc)} ◆ {loc.column_initiative}: {shield.bonus_initiative}")

            accessory = controller.character.inventory.equipped.accessory
            if accessory:
                st.write(f"**{loc.column_accessory}**")
                c1, c2, c3 = st.columns([0.4, 0.5, 0.1])
                with c1:
                    st.write(accessory.localized_name(loc))
                with c2:
                    st.write(accessory.localized_quality(loc))
                with c3:
                    if st.button(
                            "",
                            icon=":material/arrow_downward:",
                            key=f"accessory-unequip",
                            help=loc.page_view_unequip_help,
                        ):
                        unequip_item(controller, "accessory")
                        st.rerun()

            show_martial(controller.character)


        with attributes_col:
            st.markdown(f"##### {loc.page_view_current_attributes}")
            att_col1, att_col2 = st.columns(2)

            st.markdown(f"**{loc.column_initiative}**: {controller.initiative()}")

            st.markdown(f"##### {loc.page_view_statuses}")
            col1, col2 = st.columns(2)
            for idx, stat in enumerate(Status):
                col = col1 if idx < 3 else col2
                with col:
                    checked = st.checkbox(stat.localized_name(loc),
                                          value=(stat in st.session_state.state_controller.state.statuses))
                    if checked:
                        st.session_state.state_controller.add_status(stat)
                    else:
                        st.session_state.state_controller.remove_status(stat)

            changes = controller.apply_status(st.session_state.state_controller.state.statuses)
            for attribute, value in changes.items():
                if value > 0:
                    st.toast(f"{loc.msg_status_change.format(attribute=attribute, value=value)}")
            if st.button(loc.page_view_refresh_attributes):
                st.rerun()

            with att_col1:
                st.write(f"**{loc.attr_dexterity}**: {loc.dice_prefix}{controller.character.dexterity.current}")
                st.write(f"**{loc.attr_might}**: {loc.dice_prefix}{controller.character.might.current}")
                st.markdown(f"**{loc.column_defense}**: {controller.defense()}")
            with att_col2:
                st.write(f"**{loc.attr_insight}**: {loc.dice_prefix}{controller.character.insight.current}")
                st.write(f"**{loc.attr_willpower}**: {loc.dice_prefix}{controller.character.willpower.current}")
                st.markdown(f"**{loc.column_magic_defense}**: {controller.magic_defense()}")

        st.divider()

    # Skills
    with tab2:
        sorted_classes = sorted(controller.character.classes, key=lambda x: x.class_level(), reverse=True)
        writer = SkillTableWriter(loc)
        writer.columns = writer.level_readonly_columns
        for char_class in sorted_classes:
            st.markdown(f"#### {char_class.name.localized_name(loc)}")
            writer.write_in_columns([skill for skill in char_class.skills if skill.current_level > 0])
        if controller.character.heroic_skills:
            st.markdown(f"#### {loc.heroic_skills}")
            writer = SkillTableWriter(loc)
            writer.columns = writer.heroic_skills_columns
            writer.write_in_columns(controller.character.heroic_skills)

        st.divider()

    # Spells
    with tab3:
        for class_name, spell_list in controller.character.spells.items():
            chimerist_skills = controller.get_skills(ClassName.chimerist)
            chimerist_condition = (class_name == ClassName.chimerist
                                   and "spell_mimic" in [s.name for s in chimerist_skills])
            if spell_list or chimerist_condition:
                writer = SpellTableWriter(loc)
                writer.columns = writer.columns[:-1]
                chimerist_message = ""
                if chimerist_condition:
                    max_n_spells = controller.get_skill_level(ClassName.chimerist, "spell_mimic") + 2
                    if "chimeric_mastery" in [s.name for s in controller.character.heroic_skills]:
                        max_n_spells += 2
                    chimerist_message = loc.page_view_chimerist_spell_count.format(
                        current=len(spell_list),
                        max=max_n_spells
                    )
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"#### {loc.page_view_class_spells.format(
                        class_name=class_name.localized_name(loc),
                        chimerist_message=chimerist_message
                    )}")
                with c2:
                    if chimerist_condition:
                        if st.button(loc.learn_chimerist_spell_button, disabled=(len(spell_list) == max_n_spells)):
                            add_chimerist_spell_dialog(controller, loc)
                    else:
                        char_class = controller.character.get_class(class_name)
                        casting_skill = char_class.get_spell_skill()
                        can_add_spell = False
                        if casting_skill:
                            can_add_spell = casting_skill.current_level > len(controller.character.get_spells_by_class(class_name))
                        if st.button(loc.learn_spell_button, disabled=not can_add_spell):
                            add_spell_dialog(controller, class_name, loc)

                with c3:
                    if chimerist_condition:
                        if st.button(loc.forget_chimerist_spell_button, disabled=(len(spell_list) < 1)):
                            remove_chimerist_spell_dialog(controller, loc)
                if class_name == ClassName.chimerist:
                    writer.columns = writer.chimerist_columns
                writer.write_in_columns(spell_list)

    #Equipment
    with tab4:
        col1, col2, col3 = st.columns([0.2, 0.2, 0.6])
        with col1:
            if st.button(loc.add_item_button):
                add_item_dialog(controller, loc)
        with col2:
            if st.button(loc.remove_item_button):
                remove_item_dialog(controller, loc)
        with col3:
            st.metric(
                loc.page_view_remaining_zenit,
                value=loc.page_view_remaining_zenit_value.format(zenits=controller.character.inventory.zenit),
                delta=None,
            )
        backpack = controller.character.inventory.backpack
        if backpack.weapons:
            weapon_writer = WeaponTableWriter(loc)
            weapon_writer.columns = weapon_writer.equip_columns
            weapon_writer.write_in_columns(backpack.weapons)
        if backpack.armors:
            armor_writer = ArmorTableWriter(loc)
            armor_writer.columns = armor_writer.equip_columns
            armor_writer.write_in_columns(backpack.armors)
        if backpack.shields:
            shield_writer = ShieldTableWriter(loc)
            shield_writer.columns = shield_writer.equip_columns
            shield_writer.write_in_columns(backpack.shields)
        if backpack.accessories:
            AccessoryTableWriter(loc).write_in_columns(backpack.accessories)
        if backpack.other:
            ItemTableWriter(loc).write_in_columns(backpack.other)

    # Special
    with tab5:
        if controller.is_class_added(ClassName.mutant) and controller.has_skill("theriomorphosis"):
            therioforms = controller.character.special.get_special("therioforms")
            added_therioforms = [t for t in therioforms if t.added]
            st.markdown(f"##### {loc.page_view_therioforms}")
            TherioformTableWriter(loc).write_in_columns(added_therioforms)
            if len(added_therioforms) < controller.get_skill_level(ClassName.mutant, "theriomorphosis"):
                if st.button(loc.page_view_add_therioform):
                    pass
        st.divider()

    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if st.button(loc.save_current_character_button):
            controller.dump_character()
            st.session_state.state_controller.dump_state()
    with col2:
        if st.button(loc.load_another_character_button):
            set_view_state(ViewState.load)
