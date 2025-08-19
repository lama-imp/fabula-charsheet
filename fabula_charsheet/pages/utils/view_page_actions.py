from __future__ import annotations

import math

import streamlit as st

from pages.controller import CharacterController, ClassController
from data.models import AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, SpellTarget, Spell, SpellDuration, DamageType, Armor, Shield, Accessory, Item, \
    Skill, LocNamespace, HeroicSkill, Species, ChimeristSpell, Therioform
from .table_writer import SkillTableWriter, HeroicSkillTableWriter, SpellTableWriter, TherioformTableWriter, \
    DanceTableWriter
from .classes_page_actions import add_new_class
from data import compendium as c


def avatar_update(controller: CharacterController, loc: LocNamespace):
    uploaded_avatar = st.file_uploader(
        "avatar uploader", accept_multiple_files=False,
        type=["jpg", "jpeg", "png", "gif"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button(loc.use_avatar_button, disabled=not uploaded_avatar):
        controller.dump_avatar(uploaded_avatar)
        st.rerun()


def level_up(controller: CharacterController, loc: LocNamespace):
    st.session_state.selected_hero_skills = []
    st.session_state.class_spells = []

    sorted_classes = sorted(
        [char_class for char_class in controller.character.classes if char_class.class_level() < 10],
        key=lambda x: x.class_level(),
        reverse=True
    )

    writer = SkillTableWriter(loc)
    writer.columns = writer.level_up_columns

    for char_class in sorted_classes:
        st.markdown(f"#### {char_class.name.localized_name(loc)}")
        writer.write_in_columns([skill for skill in char_class.skills if skill.current_level < skill.max_level])

    class_controller = ClassController()
    if controller.can_add_class():
        add_new_class(controller, class_controller, loc, mode="addition")

    if st.session_state.selected_hero_skills:
        selected_skill: Skill = st.session_state.selected_hero_skills[0]

        if selected_skill.can_add_spell:
            class_name = c.COMPENDIUM.get_class_name_from_skill(selected_skill)
            class_spells = c.COMPENDIUM.spells.get_spells(class_name)

            class_spells = [spell for spell in class_spells if
                            spell not in controller.character.get_spells_by_class(class_name)]
            max_n_spells = 1

            with st.expander(loc.page_class_select_spells_expander):
                SpellTableWriter(loc).write_in_columns(class_spells)
            total_class_spells = len(st.session_state.class_spells)

            if total_class_spells != max_n_spells:
                st.error(loc.error_class_select_exact_spells.format(
                    max_n_spells=max_n_spells,
                    casting_skill=selected_skill.localized_name(loc)
                ))

    if st.button(loc.confirm_button, disabled=(len(st.session_state.selected_hero_skills) != 1)):
        controller.character.level += 1
        selected_class_name = c.COMPENDIUM.get_class_name_from_skill(selected_skill)
        if controller.is_class_added(selected_class_name):
            for char_class in controller.character.classes:
                if char_class.get_skill(selected_skill.name):
                    char_class.levelup_skill(selected_skill.name)
        else:
            controller.add_class(class_controller.char_class)
        if selected_skill.can_add_spell:
            controller.character.spells[selected_class_name] = st.session_state.class_spells
        st.rerun()


def add_spell(controller: CharacterController, class_name: ClassName, loc: LocNamespace):
    selected_spells = set()
    def single_spell_selector(self, spell: Spell, idx=None):
        if st.checkbox("add spell",
                       value=(spell in selected_spells),
                       label_visibility="hidden",
                       key=f"{spell.name}-toggle"
                       ):
            if spell not in selected_spells:
                selected_spells.add(spell)
        else:
            if spell in selected_spells:
                selected_spells.discard(spell)

    class_spells = c.COMPENDIUM.spells.get_spells(class_name)
    available_spells = [spell for spell in class_spells if spell not in controller.character.get_spells_by_class(class_name)]

    writer = SpellTableWriter(loc)
    writer.columns = writer.add_one_spell_columns(single_spell_selector)
    writer.write_in_columns(available_spells)

    if st.button(loc.add_spell_button, disabled=(len(selected_spells) != 1)):
        spell = list(selected_spells)[0]
        controller.character.spells[class_name] = controller.character.spells.get(class_name, [])
        controller.character.spells[class_name].append(spell)
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
        "species": st.pills(loc.page_view_spell_species, [t for t in Species], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "char_class": ClassName.chimerist,
    }

    if st.button(loc.add_spell_button):
        try:
            new_spell = ChimeristSpell(
                **input_dict
            )
            controller.add_spell(new_spell, ClassName.chimerist)
            st.toast(loc.msg_spell_added.format(spell_name=input_dict['name']))
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning(loc.error_adding_spell, icon="🪬")


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
                "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
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


def add_heroic_skill(controller: CharacterController, loc: LocNamespace):
    st.session_state.selected_hero_skills = []
    mastered_classes = [char_class for char_class in controller.character.classes if char_class.class_level() == 10]

    def heroic_skill_availability(skill: HeroicSkill):
        if skill in controller.character.heroic_skills:
            return skill.can_add_several_times
        if not skill.required_class:
            return True
        if set(skill.required_class).intersection(set(char_class.name for char_class in mastered_classes)):
            if skill.required_skill:
                return any(
                    (char_class.get_skill(skill.required_skill.name) or Skill()).current_level > 0
                    for char_class in controller.character.classes
                )
            return True
        return False

    st.write(loc.msg_add_heroic_skill)
    writer = HeroicSkillTableWriter(loc)
    sorted_skills = sorted(c.COMPENDIUM.heroic_skills.heroic_skills, key=lambda x: x.localized_name(loc))
    writer.write_in_columns([skill for skill in sorted_skills if heroic_skill_availability(skill)])

    if st.button(loc.confirm_button, disabled=(len(st.session_state.selected_hero_skills) != 1)):
        controller.character.level += 1
        selected_heroic_skill = st.session_state.selected_hero_skills[0]
        controller.character.heroic_skills.append(selected_heroic_skill)
        st.rerun()


def increase_attribute(controller: CharacterController, loc: LocNamespace):
    st.markdown(loc.msg_increase_attribute)
    attributes = [
        controller.character.dexterity,
        controller.character.might,
        controller.character.insight,
        controller.character.willpower,
    ]

    for attribute in attributes:
        if attribute.base < 12:
            with st.container():
                col1, col2, col3 = st.columns([0.2, 0.5, 0.3])
                with col2:
                    s = f"**{attribute.name.localized_name(loc)}**: {loc.dice_prefix}{attribute.base} :material/keyboard_double_arrow_right: {loc.dice_prefix}{attribute.base + 2}"
                    st.markdown(s)
                with col3:
                    if st.button(
                            ":material/add_task:",
                            key=attribute.name,
                    ):
                        attribute.base += 2
                        st.rerun()


def add_therioform(controller: CharacterController, loc: LocNamespace):
    selected_therioform = list()
    def single_selector(therioform: Therioform, idx=None):
        if st.checkbox("add therioform",
                       value=(therioform in selected_therioform),
                       label_visibility="hidden",
                       key=f"{therioform.name}-toggle"
                       ):
            if therioform not in selected_therioform:
                selected_therioform.append(therioform)
        else:
            if therioform in selected_therioform:
                selected_therioform.remove(therioform)

    sorted_therioforms = sorted(c.COMPENDIUM.therioforms, key=lambda x: x.localized_name(loc))
    available_therioforms = [t for t in sorted_therioforms if t not in controller.character.special.therioforms]

    writer = TherioformTableWriter(loc)
    writer.columns = writer.add_one_therioform_columns(single_selector)
    writer.write_in_columns(available_therioforms, description=False)

    if st.button(loc.add_therioform_button, key="add-new-therioform", disabled=(len(selected_therioform) != 1)):
        therioform = selected_therioform[0]
        controller.character.special.therioforms.append(therioform)
        st.rerun()

def add_dance(controller: CharacterController, loc: LocNamespace):
    selected_dance = list()
    def single_selector(therioform: Therioform, idx=None):
        if st.checkbox("add therioform",
                       value=(therioform in selected_dance),
                       label_visibility="hidden",
                       key=f"{therioform.name}-toggle"
                       ):
            if therioform not in selected_dance:
                selected_dance.append(therioform)
        else:
            if therioform in selected_dance:
                selected_dance.remove(therioform)

    sorted_dances = sorted(c.COMPENDIUM.dances, key=lambda x: x.localized_name(loc))
    available_dances = [t for t in sorted_dances if t not in controller.character.special.dances]

    writer = DanceTableWriter(loc)
    writer.columns = writer.add_one_dance_columns(single_selector)
    writer.write_in_columns(available_dances, description=False)

    if st.button(loc.add_spell_button, disabled=(len(selected_dance) != 1)):
        dance = selected_dance[0]
        controller.character.special.dances.append(dance)
        st.rerun()


def manifest_therioform(controller: CharacterController, loc: LocNamespace):
    selected_therioforms = list()
    can_manifest_number = 0
    def selector(therioform: Therioform, idx=None):
        if st.checkbox("add therioform",
                       value=(therioform in selected_therioforms),
                       label_visibility="hidden",
                       key=f"{therioform.name}-toggle"
                       ):
            if therioform not in selected_therioforms:
                selected_therioforms.append(therioform)
        else:
            if therioform in selected_therioforms:
                selected_therioforms.remove(therioform)

    st.markdown(loc.page_view_manifest_therioform_selection)
    key = "skill_{skill_name}"
    skill = st.pills(
        "therioform selection",
        ["theriomorphosis", "genoclepsis"],
        format_func=lambda x: getattr(loc, key.format(skill_name=x), x),
        label_visibility="hidden"
    )
    if skill == "theriomorphosis":
        available_therioforms = [t for t in controller.character.special.therioforms]
        can_manifest_number = 2
    elif skill == "genoclepsis":
        available_therioforms = sorted(c.COMPENDIUM.therioforms, key=lambda x: x.localized_name(loc))
        can_manifest_number = controller.get_skill_level(ClassName.mutant, "genoclepsis")

    if skill:
        writer = TherioformTableWriter(loc)
        writer.columns = writer.add_one_therioform_columns(selector)
        writer.write_in_columns(available_therioforms, description=False)

        if st.button(loc.confirm_button, key="confirm-therioform", disabled=(len(selected_therioforms) > can_manifest_number)):
            controller.state.minus_hp += math.floor(controller.current_hp() / 3)
            controller.state.active_therioforms.extend(selected_therioforms)
            st.rerun()
