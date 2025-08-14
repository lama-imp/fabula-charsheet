from collections.abc import Iterable, Callable
from copy import deepcopy
from typing import Optional

import streamlit as st
from pydantic import BaseModel

from data.models import (
    Skill,
    Spell,
    Weapon,
    Armor,
    AttributeName,
    Shield,
    Accessory,
    Therioform,
    Item,
    LocNamespace,
    HeroicSkill,
)
from .common import add_item_as, join_with_or


class ColumnConfig(BaseModel):
    name: str
    width: float
    process: Optional[Callable]

class TableWriter:
    columns = None

    def __init__(self, loc: LocNamespace):
        self.loc = loc
        if self.columns is None:
            if hasattr(self, "base_columns"):
                self.columns = self.base_columns
            else:
                raise AssertionError("TableWriter requires 'columns' or 'base_columns' to be defined")

    def write_in_columns(
            self,
            data: Iterable,
            header: bool = True
    ):
        if header:
            self._write_header()

        for item_idx, item in enumerate(data):
            for cell, column_config in zip(
                st.columns(spec=[col.width for col in self.columns]),
                self.columns
            ):
                with cell:
                    column_config.process(item, item_idx)

            self._add_description(item, item_idx)

    def _write_header(self):
        for cell, column_name in zip(
            st.columns(spec=[col.width for col in self.columns]),
            (col.name for col in self.columns)
        ):
            with cell:
                key = f"column_{column_name}"
                try:
                    localized_value = getattr(self.loc, key)
                except AttributeError:
                    localized_value = column_name.capitalize()
                st.markdown(f"##### {localized_value}")

    def _add_description(self, item, idx=None):
        raise NotImplementedError

    def _add_item_as(self, item: Item):
        @st.dialog(self.loc.page_equipment_create_new_name)
        def add_item_as_dialog(item: Item):
            add_item_as(item)

        add_item_as_dialog(item)


class SkillTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="skill",
                width=0.2,
                process=lambda s, idx=None: st.write(s.localized_name(self.loc)),
            ),
            ColumnConfig(
                name="description",
                width=0.7,
                process=lambda s, idx=None: st.write(s.localized_description(self.loc)),
            ),
            ColumnConfig(
                name="level",
                width=0.2,
                process=self._level_input,
            ),
        )

    @property
    def level_readonly_columns(self):
        return (
            self.base_columns[0],
            self.base_columns[1],
            ColumnConfig(
                name="level",
                width=0.2,
                process=lambda s, idx=None: st.write(str(s.current_level))
            ),
        )

    @property
    def heroic_skills_columns(self):
        return (
            self.base_columns[0],
            self.base_columns[1],
        )

    @property
    def level_up_columns(self):
        return (
            self.base_columns[0],
            self.base_columns[1],
            ColumnConfig(
                name="level",
                width=0.2,
                process=add_point
            ),
        )

    @property
    def level_up_new_class_columns(self):
        return (
            self.base_columns[0],
            self.base_columns[1],
            ColumnConfig(
                name="level",
                width=0.2,
                process=self._level_input_for_levelup
            ),
        )

    @staticmethod
    def _level_input(skill: Skill, idx=None):
        if skill.max_level > 1:
            level = st.slider(
                "level",
                min_value=0,
                max_value=skill.max_level,
                value=skill.current_level,
                key=f"{skill.name}-slider",
                label_visibility="hidden",
            )
        else:
            level = int(
                st.toggle(
                    "level2",
                    value=bool(skill.current_level),
                    key=f"{skill.name}-toggle",
                    label_visibility="hidden",
                )
            )
        skill.current_level = level

    @staticmethod
    def _level_input_for_levelup(skill: Skill, idx=None):
        st.session_state.selected_hero_skills = st.session_state.get("selected_hero_skills", [])
        level = st.checkbox(" ", key=f"{skill.name}-point", label_visibility="hidden")
        if level and skill not in st.session_state.selected_hero_skills:
                st.session_state.selected_hero_skills.append(skill)
                skill.current_level += 1
        else:
            if skill in st.session_state.selected_hero_skills:
                st.session_state.selected_hero_skills.remove(skill)
                skill.current_level -= 1
        skill.current_level = int(level)

    def _add_description(self, item, idx=None):
        pass


class HeroicSkillTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="heroic_skill",
                width=0.3,
                process=lambda s, idx=None: st.write(s.localized_name(self.loc)),
            ),
            ColumnConfig(
                name="requirements",
                width=0.55,
                process=self._process_requirements,
            ),
            ColumnConfig(
                name="select",
                width=0.15,
                process=self._skill_selector,
            ),
        )

    def _process_requirements(self, skill: HeroicSkill, idx=None):
        requirements_string = ""
        if skill.required_class:
            if len(skill.required_class) == 1:
                required_class_name = skill.required_class[0].localized_name(self.loc)
                requirements_string = self.loc.heroic_skill_one_mastery_requirement.format(class_name=required_class_name)
                if skill.required_skill:
                    required_skill_name = skill.required_skill.localized_name(self.loc)
                    requirements_string = requirements_string[:-1]
                    requirements_string += self.loc.heroic_skill_skill_requirement.format(skill_name=required_skill_name)
            else:
                required_classes_names = [c.localized_name(self.loc) for c in skill.required_class]
                requirements_string = self.loc.heroic_skill_several_mastery_requirement.format(
                    classes=join_with_or(required_classes_names, self.loc)
                )
        st.write(requirements_string)


    def _skill_selector(self, skill: HeroicSkill, idx=None):
        st.session_state.selected_hero_skills = st.session_state.get("selected_hero_skills", [])
        if st.checkbox("add skill",
                       value=(skill in st.session_state.selected_hero_skills),
                       label_visibility="hidden",
                       key=f"{skill.name}-toggle"
                       ):
            if skill not in st.session_state.selected_hero_skills:
                st.session_state.selected_hero_skills.append(skill)
        else:
            if skill in st.session_state.selected_hero_skills:
                st.session_state.selected_hero_skills.remove(skill)

    def _add_description(self, skill: HeroicSkill, idx=None):
        st.markdown(skill.localized_description(self.loc))
        st.divider()


class SpellTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="spell",
                width=0.25,
                process=self.write_spell_name,
            ),
            ColumnConfig(
                name="mp",
                width=0.15,
                process=self.write_mp_cost,
            ),
            ColumnConfig(
                name="target",
                width=0.25,
                process=self.write_target,
            ),
            ColumnConfig(
                name="duration",
                width=0.2,
                process=self.write_duration,
            ),
            ColumnConfig(
                name="select",
                width=0.15,
                process=self.spell_selector,
            ),
        )

    def add_one_spell_columns(self, single_spell_selector: Callable):
        columns = list(self.base_columns)
        last_col = columns[-1]
        columns[-1] = ColumnConfig(
            name=last_col.name,
            width=last_col.width,
            process=single_spell_selector,
        )
        return tuple(columns)

    def _add_description(self, spell: Spell, idx=None):
        st.markdown(spell.localized_description(self.loc))
        st.divider()

    def write_spell_name(self, spell: Spell, idx=None):
        st.write(f"{spell.localized_name(self.loc)}{'⚡' if spell.is_offensive else ''}")

    def write_mp_cost(self, spell: Spell, idx=None):
        st.write(f"{spell.mp_cost}{f' x {self.loc.spell_target_marker}' if spell.target == 'up_to_three' else ''}")

    def write_target(self, spell: Spell, idx=None):
        st.write(spell.target.localized_name(self.loc))

    def write_duration(self, spell: Spell, idx=None):
        st.write(spell.duration.localized_name(self.loc))

    def spell_selector(self, spell: Spell, idx=None):
        st.session_state.class_spells = st.session_state.get("class_spells", [])
        if st.checkbox("add spell",
                       value=(spell in st.session_state.class_spells),
                       label_visibility="hidden",
                       key=f"{spell.name}-toggle"
                       ):
            if spell not in st.session_state.class_spells:
                st.session_state.class_spells.append(spell)
        else:
            if spell in st.session_state.class_spells:
                st.session_state.class_spells.remove(spell)


class WeaponTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="weapon",
                width=0.2,
                process=self._process_weapon,
            ),
            ColumnConfig(
                name="cost",
                width=0.15,
                process=self._process_cost,
            ),
            ColumnConfig(
                name="accuracy",
                width=0.2,
                process=self._process_accuracy,
            ),
            ColumnConfig(
                name="damage",
                width=0.2,
                process=self._process_damage,
            ),
            ColumnConfig(
                name="add",
                width=0.15,
                process=self._add_weapon,
            ),
        )

    @property
    def equip_columns(self):
        return (
            *self.base_columns[:-1],
            ColumnConfig(
                name="equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _process_weapon(self, s, idx=None):
        key = f"item_{s.name}"
        weapon_name = getattr(self.loc, key, s.name.title())
        st.write(f"{weapon_name} {'♦️' if s.martial else ''}")

    def _process_cost(self, s, idx=None):
        currency = getattr(self.loc, "zenit_short", "z")
        st.write(f"{s.cost} {currency}")

    def _process_accuracy(self, s, idx=None):
        st.write(s.format_accuracy(self.loc))

    def _process_damage(self, s, idx=None):
        hr_label = getattr(self.loc, "hr", "HR")
        damage_key = f"damage_{s.damage_type}"
        damage_type = getattr(self.loc, damage_key, s.damage_type)
        st.write(f"【{hr_label} + {s.bonus_damage}】 {damage_type}")

    def _add_description(self, item: Weapon, idx=None):
        st.write(
            " ◆ ".join((
                item.grip_type.localized_name(self.loc),
                item.range.localized_name(self.loc),
                item.localized_quality(self.loc),
            ))
        )
        st.divider()

    def _add_weapon(self, weapon: Weapon, idx=None):
        cannot_equip = False
        if weapon.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.can_equip_weapon(weapon.range):
                    cannot_equip = False

        if st.button(
                self.loc.add_button,
                key=f"{weapon.name}-add",
                disabled=(cannot_equip or (st.session_state.start_equipment.zenit < weapon.cost))
        ):
            st.session_state.start_equipment.backpack.weapons.append(deepcopy(weapon))
            st.session_state.start_equipment.zenit -= weapon.cost
        if st.button(self.loc.add_as_button, key=f"{weapon.name}-add-as"):
            self._add_item_as(weapon)

    def equip(self, item: Weapon, idx: int | None = None):
        cannot_equip = False
        if item.martial:
            cannot_equip = True
            for char_class in st.session_state.char_controller.character.classes:
                if char_class.martial_weapon:
                    cannot_equip = False
        if item in st.session_state.char_controller.equipped_items():
            cannot_equip = True
        key_suffix = f"{item.name}-{idx}" if idx is not None else item.name
        if st.button(self.loc.equip_button,
                     key=f'{key_suffix}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(self.loc.equipped_message.format(item_name=item.localized_name(self.loc)))
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class ArmorTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="armor",
                width=0.2,
                process=self._process_armor,
            ),
            ColumnConfig(
                name="cost",
                width=0.15,
                process=self._process_cost,
            ),
            ColumnConfig(
                name="defense",
                width=0.155,
                process=self._write_defense,
            ),
            ColumnConfig(
                name="magic_defense",
                width=0.155,
                process=self._write_magic_defense,
            ),
            ColumnConfig(
                name="initiative",
                width=0.15,
                process=lambda s, idx=None: st.write(str(s.bonus_initiative)),
            ),
            ColumnConfig(
                name="add",
                width=0.15,
                process=self._add_armor,
            ),
        )

    @property
    def equip_columns(self):
        return (
            *self.base_columns[:-1],  # all except last (Add)
            ColumnConfig(
                name="equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _process_armor(self, s, idx=None):
        key = f"item_{s.name}"
        armor_name = getattr(self.loc, key, s.name.title())
        st.write(f"{armor_name} {'♦️' if s.martial else ''}")

    def _process_cost(self, s, idx=None):
        currency = getattr(self.loc, "zenit_short", "z")
        st.write(f"{s.cost} {currency}")

    def _add_description(self, item: Armor, idx=None):
        st.write(item.localized_quality(self.loc))
        st.divider()

    def _add_armor(self, armor: Armor, idx=None):
        cannot_equip = False
        if armor.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False

        disabled = cannot_equip or (st.session_state.start_equipment.zenit < armor.cost)
        if st.button(self.loc.add_button, key=f"{armor.name}-add", disabled=disabled):
            st.session_state.start_equipment.backpack.armors.append(deepcopy(armor))
            st.session_state.start_equipment.zenit -= armor.cost

        if st.button(self.loc.add_as_button, key=f"{armor.name}-add-as"):
            self._add_item_as(armor)

    def _write_defense(self, item: Armor, idx=None):
        def_bonus = f" + {item.bonus_defense}" if item.bonus_defense > 0 else ""
        if isinstance(item.defense, AttributeName):
            st.write(f"{AttributeName.to_alias(item.defense, self.loc)}{def_bonus}")
        else:
            st.write(f"{str(item.defense)}{def_bonus}")

    def _write_magic_defense(self, item: Armor, idx=None):
        def_bonus = f" + {item.bonus_magic_defense}" if item.bonus_magic_defense > 0 else ""
        if isinstance(item.magic_defense, AttributeName):
            st.write(f"{AttributeName.to_alias(item.magic_defense, self.loc)}{def_bonus}")
        else:
            st.write(f"{str(item.magic_defense)}{def_bonus}")

    def equip(self, item: Armor, idx: int | None = None):
        cannot_equip = False
        if item.martial:
            cannot_equip = True
            for char_class in st.session_state.char_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False

        if item in st.session_state.char_controller.equipped_items():
            cannot_equip = True

        key_suffix = f"{item.name}-{idx}" if idx is not None else item.name

        if st.button(self.loc.equip_button,
                     key=f'{key_suffix}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(self.loc.equipped_message.format(item_name=item.localized_name(self.loc)))
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class ShieldTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="shield",
                width=0.2,
                process=self._process_shield,
            ),
            ColumnConfig(
                name="cost",
                width=0.15,
                process=self._process_cost,
            ),
            ColumnConfig(
                name="defense",
                width=0.155,
                process=self._write_defense,
            ),
            ColumnConfig(
                name="magic_defense",
                width=0.155,
                process=self._write_magic_defense,
            ),
            ColumnConfig(
                name="initiative",
                width=0.15,
                process=lambda s, idx=None: st.write(str(s.bonus_initiative)),
            ),
            ColumnConfig(
                name="add",
                width=0.15,
                process=self._add_shield,
            ),
        )

    @property
    def equip_columns(self):
        return (
            *self.base_columns[:-1],  # all except last (Add)
            ColumnConfig(
                name="equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _process_shield(self, s, idx=None):
        key = f"item_{s.name}"
        shield_name = getattr(self.loc, key, s.name.title())
        st.write(f"{shield_name} {'♦️' if s.martial else ''}")

    def _process_cost(self, s, idx=None):
        currency = getattr(self.loc, "zenit_short", "z")
        st.write(f"{s.cost} {currency}")

    def _add_description(self, item: Shield, idx=None):
        st.write(item.localized_quality(self.loc))
        st.divider()

    def _add_shield(self, shield: Shield, idx=None):
        cannot_equip = False
        if shield.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_shields:
                    cannot_equip = False

        disabled = cannot_equip or (st.session_state.start_equipment.zenit < shield.cost)
        if st.button(self.loc.add_button, key=f"{shield.name}-add", disabled=disabled):
            st.session_state.start_equipment.backpack.shields.append(deepcopy(shield))
            st.session_state.start_equipment.zenit -= shield.cost

        if st.button(self.loc.add_as_button, key=f"{shield.name}-add-as"):
            self._add_item_as(shield)

    def _write_defense(self, item: Shield, idx=None):
        st.write(f"+{item.bonus_defense}")

    def _write_magic_defense(self, item: Shield, idx=None):
        st.write(f"+{item.bonus_magic_defense}")

    def equip(self, item: Shield, idx=None):
        cannot_equip = False
        if item.martial:
            cannot_equip = True
            for char_class in st.session_state.char_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False

        if item in st.session_state.char_controller.equipped_items():
            cannot_equip = True

        key_suffix = f"{item.name}-{idx}" if idx is not None else item.name

        if st.button(self.loc.equip_button,
                     key=f'{key_suffix}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(self.loc.equipped_message.format(item_name=item.localized_name(self.loc)))
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class AccessoryTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="accessory",
                width=0.2,
                process=self._process_name,
            ),
            ColumnConfig(
                name="cost",
                width=0.15,
                process=self._process_cost,
            ),
            ColumnConfig(
                name="quality",
                width=0.155,
                process=lambda s, idx=None: st.write(s.localized_quality(self.loc)),
            ),
            ColumnConfig(
                name="equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _process_name(self, s, idx=None):
        key = f"item_{s.name}"
        item_name = getattr(self.loc, key, s.name.title())
        st.write(item_name)

    def _process_cost(self, s, idx=None):
        currency = getattr(self.loc, "zenit_short", "z")
        st.write(f"{s.cost} {currency}")

    def _add_description(self, item: Accessory, idx=None):
        st.divider()

    def equip(self, item: Accessory, idx: int | None = None):
        key_suffix = f"{item.name}-{idx}" if idx is not None else item.name
        disabled = item in st.session_state.char_controller.equipped_items()
        if st.button(self.loc.equip_button, key=f'{key_suffix}-equip', disabled=disabled):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(self.loc.equipped_message.format(item_name=item.localized_name(self.loc)))
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class ItemTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="items",
                width=0.2,
                process=lambda s, idx=None: st.write(s.name.title()),
            ),
            ColumnConfig(
                name="cost",
                width=0.15,
                process=lambda s, idx=None: st.write(f"{s.cost} z"),
            ),
            ColumnConfig(
                name="quality",
                width=0.155,
                process=lambda s, idx=None: st.write(f"{s.quality}"),
            ),
        )

    def _add_description(self, item: Accessory, idx=None):
        st.divider()


class TherioformTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="therioform",
                width=0.3,
                process=lambda t, idx=None: st.write(f"_{t.localized_name(self.loc)}_"),
            ),
            ColumnConfig(
                name="genoclepsis",
                width=0.7,
                process=lambda t, idx=None: st.write(t.localized_creatures(self.loc)),
            ),
        )

    def _add_description(self, therioform: Therioform, idx=None):
        st.write(therioform.localized_description(self.loc))


def add_point(skill: Skill, idx=None):
    st.session_state.selected_hero_skills = st.session_state.get("selected_hero_skills", [])
    if st.checkbox(" ", key=f"{skill.name}-point", label_visibility="hidden"):
        if skill not in st.session_state.selected_hero_skills:
            st.session_state.selected_hero_skills.append(skill)
    else:
        if skill in st.session_state.selected_hero_skills:
            st.session_state.selected_hero_skills.remove(skill)
