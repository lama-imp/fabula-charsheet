import streamlit as st

import config
from data.models import Status, AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, LocNamespace
from pages.controller import CharacterController
from pages.utils import WeaponTableWriter, ArmorTableWriter, SkillTableWriter, SpellTableWriter, DanceTableWriter, \
    AccessoryTableWriter, ItemTableWriter, TherioformTableWriter, ShieldTableWriter, BondTableWriter, \
    show_martial, set_view_state, get_avatar_path, avatar_update, level_up, add_chimerist_spell, \
    remove_chimerist_spell, add_item, remove_item, unequip_item, add_heroic_skill, add_spell, add_bond, remove_bond, \
    increase_attribute, add_therioform, add_dance, manifest_therioform, display_equipped_item
from pages.character_view.view_state import ViewState


def build(controller: CharacterController):
    st.set_page_config(layout="wide")
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)

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

    @st.dialog(loc.page_view_add_therioform_dialog_title, width="large")
    def add_therioform_dialog(controller: CharacterController, loc: LocNamespace):
        add_therioform(controller, loc)

    @st.dialog(loc.page_view_add_dance_dialog_title, width="large")
    def add_dance_dialog(controller: CharacterController, loc: LocNamespace):
        add_dance(controller, loc)

    @st.dialog(loc.page_view_manifest_therioform_dialog_title, width="large")
    def manifest_therioform_dialog(controller: CharacterController, loc: LocNamespace):
        manifest_therioform(controller, loc)

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
                if controller.current_hp() <= controller.crisis_value():
                    st.write(f":red[{loc.page_view_crisis_text}]")
                else:
                    st.write("")
                if st.button(loc.page_view_level_up_button):
                    level_up_dialog(controller, loc)
                if controller.can_add_heroic_skill():
                    if st.button(loc.heroic_skill_button):
                        add_heroic_skill_dialog(controller, loc)
                if controller.can_increase_attribute():
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
                st.progress(
                    max((controller.current_hp() / controller.max_hp()), 0),
                    text=f"{loc.hp} {controller.current_hp()} / {controller.max_hp()}"
                )
                st.write("")
                st.write("")

                st.progress(
                    max((controller.current_mp() / controller.max_mp()), 0),
                    text=f"{loc.mp} {controller.current_mp()} / {controller.max_mp()}"
                )
                st.write("")
                st.write("")

                st.progress(
                    max((controller.current_ip() / controller.max_ip()), 0),
                    text=f"{loc.ip} {controller.current_ip()} / {controller.max_ip()}"
                )
            with col2:
                hp_input = st.number_input("hp_input", min_value=0, label_visibility="hidden", value=10)
                mp_input = st.number_input("mp_input", min_value=0, label_visibility="hidden", value=10)
                ip_input = st.number_input("ip_input", min_value=0, label_visibility="hidden", value=3)
            with col3:
                st.write("")
                if st.button("", icon=":material/add:", key="add_hp"):
                    controller.state.minus_hp = max(0, controller.state.minus_hp - hp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/add:", key="add_mp"):
                    controller.state.minus_mp = max(0, controller.state.minus_mp - mp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/add:", key="add_ip"):
                    controller.state.minus_ip = max(0, controller.state.minus_ip - ip_input)
                    st.rerun()
                st.write("")
                st.write("")
            with col4:
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_hp"):
                    controller.state.minus_hp = min(controller.max_hp(), controller.state.minus_hp + hp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_mp"):
                    controller.state.minus_mp = min(controller.max_mp(), controller.state.minus_mp + mp_input)
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/remove:", key="subtract_ip"):
                    controller.state.minus_ip = min(controller.max_ip(), controller.state.minus_ip + ip_input)
                    st.rerun()
                st.write("")
                st.write("")
            with col5:
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_hp", help="Reset HP"):
                    controller.state.minus_hp = 0
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_mp", help="Reset MP"):
                    controller.state.minus_mp = 0
                    st.rerun()
                st.write("")
                st.write("")
                if st.button("", icon=":material/laps:", key="reset_ip", help="Reset IP"):
                    controller.state.minus_ip = 0
                    st.rerun()
                st.write("")
                st.write("")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(loc.page_view_health_potion,
                    disabled=not controller.can_use_potion(),
                    use_container_width=True,
                ):
                    controller.use_health_potion()
                    st.rerun()
            with col2:
                if st.button(loc.page_view_mana_potion,
                    disabled=not controller.can_use_potion(),
                    use_container_width=True
                ):
                    controller.use_mana_potion()
                    st.rerun()
            with col3:
                if st.button(loc.page_view_magic_tent,
                    disabled=not controller.can_use_magic_tent(),
                    use_container_width=True
                ):
                    controller.use_magic_tent()
                    st.rerun()

            st.write(f"##### {loc.page_view_equipped}")
            main_hand = controller.character.inventory.equipped.main_hand or Weapon(
                name="unarmed_strike",
                cost=0,
                quality=loc.unarmed_strike_quality,
                martial=False,
                grip_type=GripType.one_handed,
                range=WeaponRange.melee,
                weapon_category=WeaponCategory.brawling,
                accuracy=[AttributeName.dexterity, AttributeName.might],
            )
            display_equipped_item(controller, main_hand, "main_hand", loc)

            # Off-hand
            off_hand = controller.character.inventory.equipped.off_hand
            if off_hand:
                display_equipped_item(controller, off_hand, "off_hand", loc)

            # Armor
            armor = controller.character.inventory.equipped.armor
            if armor:
                display_equipped_item(controller, armor, "armor", loc)

            # Accessory
            accessory = controller.character.inventory.equipped.accessory
            if accessory:
                display_equipped_item(controller, accessory, "accessory", loc)

            show_martial(controller.character)


        with attributes_col:
            st.markdown(f"##### {loc.page_view_current_attributes}")
            att_col1, att_col2 = st.columns(2)
            initiative_column, _ = st.columns([0.9, 0.1])

            st.markdown(f"##### {loc.page_view_statuses}")
            col1, col2 = st.columns(2)
            for idx, stat in enumerate(Status):
                col = col1 if idx < 3 else col2
                with col:
                    checked = st.checkbox(stat.localized_name(loc),
                                          value=(stat in controller.state.statuses))
                    if checked:
                        controller.add_status(stat)
                    else:
                        controller.remove_status(stat)

            minus_changes = controller.apply_status()
            for attribute, value in minus_changes.items():
                if value > 0:
                    st.toast(f"{loc.msg_negative_status_change.format(
                        attribute=attribute.localized_name(loc),
                        value=value,
                    )}")

            st.markdown(f"##### {loc.page_view_bonus_to_attributes}")
            col1, col2 = st.columns(2)
            for idx, attribute in enumerate(AttributeName):
                col = col1 if idx < 2 else col2
                with col:
                    checked = st.checkbox(attribute.localized_name(loc),
                                          value=(stat in controller.state.improved_attributes))
                    if checked and attribute not in controller.state.improved_attributes:
                        controller.state.improved_attributes.append(attribute)
                    if not checked and attribute in controller.state.improved_attributes:
                        controller.state.improved_attributes.remove(attribute)

            plus_changes = controller.apply_attribute_bonus()
            for attribute, value in plus_changes.items():
                if value > 0:
                    st.toast(f"{loc.msg_positive_status_change.format(
                        attribute=attribute.localized_name(loc),
                        value=value,
                    )}")
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

            with initiative_column:
                st.markdown(f"**{loc.column_initiative}**: {controller.initiative()}")

            if ClassName.mutant in [char_class.name for char_class in controller.character.classes]:
                st.markdown(f"##### {loc.page_view_manifested_terioforms}")
                st.markdown(" • ".join(t.localized_name(loc) for t in controller.state.active_therioforms))
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(loc.manifest_therioform_button):
                        manifest_therioform_dialog(controller, loc)
                with col2:
                    if st.button(loc.page_view_end_therioform_effect):
                        controller.state.active_therioforms = list()
                        st.rerun()

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
        st.divider()
        if controller.is_class_added(ClassName.mutant) and controller.has_skill("theriomorphosis"):
            added_therioforms = [t for t in controller.character.special.therioforms]
            col1, col2 = st.columns([0.25, 0.75])
            with col1:
                st.markdown(f"##### {loc.page_view_therioforms}")
            with col2:
                if len(added_therioforms) < controller.get_skill_level(ClassName.mutant, "theriomorphosis"):
                    if st.button(loc.add_therioform_button):
                        add_therioform_dialog(controller, loc)
            TherioformTableWriter(loc).write_in_columns(added_therioforms)
            st.divider()

        if controller.is_class_added(ClassName.dancer) and controller.has_skill("dance"):
            added_dances = [t for t in controller.character.special.dances]
            col1, col2 = st.columns([0.25, 0.75])
            with col1:
                st.markdown(f"##### {loc.page_view_dances}")
            with col2:
                if len(added_dances) < controller.get_skill_level(ClassName.dancer, "dance"):
                    if st.button(loc.add_dance_button):
                        add_dance_dialog(controller, loc)
            DanceTableWriter(loc).write_in_columns(added_dances)
            st.divider()

    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        if st.button(loc.save_current_character_button):
            controller.dump_character()
            controller.dump_state()
    with col2:
        if st.button(loc.load_another_character_button):
            set_view_state(ViewState.load)
