from collections.abc import Iterable, Callable
from copy import deepcopy
from itertools import chain
from typing import Optional

import streamlit as st
from pydantic import BaseModel

from data.models import (
    Skill,
    Spell,
    Weapon,
    Armor,
    AttributeName,
    CharClass,
    Character,
    Shield,
    Accessory,
    Therioform,
    Item,
)
from pages.controller import ClassController
from .creation_state import CreationState


class ColumnConfig(BaseModel):
    name: str
    width: float
    process: Optional[Callable]

class TableWriter:
    columns = None

    def __init__(self):
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
                st.markdown(f"##### {column_name}")

    def _add_description(self, item, idx=None):
        raise NotImplementedError


class SkillTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="Skill",
                width=0.2,
                process=lambda s, idx=None: st.write(s.name.title()),
            ),
            ColumnConfig(
                name="Description",
                width=0.7,
                process=lambda s, idx=None: st.write(s.description),
            ),
            ColumnConfig(
                name="Level",
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
                name="Level",
                width=0.2,
                process=lambda s, idx=None: st.write(str(s.current_level))
            ),
        )

    def level_up_columns(self, add_point_handler: Callable):
        return (
            self.base_columns[0],
            self.base_columns[1],
            ColumnConfig(
                name="Level",
                width=0.2,
                process=add_point_handler
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

    def _add_description(self, item, idx=None):
        pass


class SpellTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="Spell",
                width=0.25,
                process=self.write_spell_name,
            ),
            ColumnConfig(
                name="MP",
                width=0.15,
                process=self.write_mp_cost,
            ),
            ColumnConfig(
                name="Target",
                width=0.25,
                process=self.write_target,
            ),
            ColumnConfig(
                name="Duration",
                width=0.2,
                process=self.write_duration,
            ),
            ColumnConfig(
                name="Select",
                width=0.15,
                process=self.spell_selector,
            ),
        )

    def _add_description(self, spell: Spell, idx=None):
        st.markdown(spell.description)
        st.divider()

    def write_spell_name(self, spell: Spell, idx=None):
        st.write(f"{spell.name.title()}{'⚡' if spell.is_offensive else ''}")

    def write_mp_cost(self, spell: Spell, idx=None):
        st.write(f"{spell.mp_cost}{' x T' if spell.target == 'up_to_three' else ''}")

    def write_target(self, spell: Spell, idx=None):
        mapping = {
            "one_creature": "One creature",
            "up_to_three": "Up to three creatures",
            "weapon": "One equipped weapon",
            "self": "Self",
            "special": "Special",
        }
        st.write(mapping[spell.target])

    def write_duration(self, spell: Spell, idx=None):
        st.write(spell.duration.title())

    def spell_selector(self, spell: Spell, idx=None):
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
                name="Weapon",
                width=0.2,
                process=lambda s, idx=None: st.write(f"{s.name.title()} {'♦️' if s.martial else ''}"),
            ),
            ColumnConfig(
                name="Cost",
                width=0.15,
                process=lambda s, idx=None: st.write(f"{s.cost} z"),
            ),
            ColumnConfig(
                name="Accuracy",
                width=0.2,
                process=lambda s, idx=None: st.write(s.format_accuracy()),
            ),
            ColumnConfig(
                name="Damage",
                width=0.2,
                process=lambda s, idx=None: st.write(f"【HR + {s.bonus_damage}】 {s.damage_type}"),
            ),
            ColumnConfig(
                name="Add",
                width=0.15,
                process=self._add_weapon,
            ),
        )

    @property
    def equip_columns(self):
        return (
            *self.base_columns[:-1],
            ColumnConfig(
                name="Equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _add_description(self, item: Weapon, idx=None):
        st.write(
            " ◆ ".join((
                item.grip_type.title().replace('_', '-'),
                item.range.title(),
                item.quality,
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

        if st.button('Add', key=f"{weapon.name}-add", disabled=(cannot_equip or (st.session_state.start_equipment.zenit < weapon.cost))):
            st.session_state.start_equipment.backpack.weapons.append(deepcopy(weapon))
            st.session_state.start_equipment.zenit -= weapon.cost
        if st.button('Add as', key=f"{weapon.name}-add-as"):
            add_item_as(weapon)

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
        if st.button('Equip',
                     key=f'{key_suffix}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(f"Equipped {item.name.title()}")
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class ArmorTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="Armor",
                width=0.2,
                process=lambda s, idx=None: st.write(f"{s.name.title()} {'♦️' if s.martial else ''}"),
            ),
            ColumnConfig(
                name="Cost",
                width=0.15,
                process=lambda s, idx=None: st.write(f"{s.cost} z"),
            ),
            ColumnConfig(
                name="Defense",
                width=0.155,
                process=self._write_defense,
            ),
            ColumnConfig(
                name="M.Defense",
                width=0.155,
                process=self._write_magic_defense,
            ),
            ColumnConfig(
                name="Initiative",
                width=0.15,
                process=lambda s, idx=None: st.write(str(s.bonus_initiative)),
            ),
            ColumnConfig(
                name="Add",
                width=0.15,
                process=self._add_armor,
            ),
        )

    @property
    def equip_columns(self):
        return (
            *self.base_columns[:-1],  # all except last (Add)
            ColumnConfig(
                name="Equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _add_description(self, item: Armor, idx=None):
        st.write(item.quality)
        st.divider()

    def _add_armor(self, armor: Armor, idx=None):
        cannot_equip = False
        if armor.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False

        disabled = cannot_equip or (st.session_state.start_equipment.zenit < armor.cost)
        if st.button('Add', key=f"{armor.name}-add", disabled=disabled):
            st.session_state.start_equipment.backpack.armors.append(deepcopy(armor))
            st.session_state.start_equipment.zenit -= armor.cost

        if st.button('Add as', key=f"{armor.name}-add-as"):
            add_item_as(armor)

    def _write_defense(self, item: Armor, idx=None):
        def_bonus = f" + {item.bonus_defense}" if item.bonus_defense > 0 else ""
        if isinstance(item.defense, AttributeName):
            st.write(f"{AttributeName.to_alias(item.defense)}{def_bonus}")
        else:
            st.write(f"{str(item.defense)}{def_bonus}")

    def _write_magic_defense(self, item: Armor, idx=None):
        def_bonus = f" + {item.bonus_magic_defense}" if item.bonus_magic_defense > 0 else ""
        if isinstance(item.magic_defense, AttributeName):
            st.write(f"{AttributeName.to_alias(item.magic_defense)}{def_bonus}")
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

        if st.button('Equip',
                     key=f'{key_suffix}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(f"Equipped {item.name.title()}")
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class ShieldTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="Shield",
                width=0.2,
                process=lambda s, idx=None: st.write(f"{s.name.title()} {'♦️' if s.martial else ''}"),
            ),
            ColumnConfig(
                name="Cost",
                width=0.15,
                process=lambda s, idx=None: st.write(f"{s.cost} z"),
            ),
            ColumnConfig(
                name="Defense",
                width=0.155,
                process=self._write_defense,
            ),
            ColumnConfig(
                name="M.Defense",
                width=0.155,
                process=self._write_magic_defense,
            ),
            ColumnConfig(
                name="Initiative",
                width=0.15,
                process=lambda s, idx=None: st.write(str(s.bonus_initiative)),
            ),
            ColumnConfig(
                name="Add",
                width=0.15,
                process=self._add_shield,
            ),
        )

    @property
    def equip_columns(self):
        return (
            *self.base_columns[:-1],  # all except last (Add)
            ColumnConfig(
                name="Equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _add_description(self, item: Shield, idx=None):
        st.write(item.quality)
        st.divider()

    def _add_shield(self, shield: Shield, idx=None):
        cannot_equip = False
        if shield.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_shields:
                    cannot_equip = False

        disabled = cannot_equip or (st.session_state.start_equipment.zenit < shield.cost)
        if st.button('Add', key=f"{shield.name}-add", disabled=disabled):
            st.session_state.start_equipment.backpack.shields.append(deepcopy(shield))
            st.session_state.start_equipment.zenit -= shield.cost

        if st.button('Add as', key=f"{shield.name}-add-as"):
            add_item_as(shield)

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

        if st.button('Equip',
                     key=f'{key_suffix}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(f"Equipped {item.name.title()}")
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class AccessoryTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="Accessory",
                width=0.2,
                process=lambda s, idx=None: st.write(s.name.title()),
            ),
            ColumnConfig(
                name="Cost",
                width=0.15,
                process=lambda s, idx=None: st.write(f"{s.cost} z"),
            ),
            ColumnConfig(
                name="Quality",
                width=0.155,
                process=lambda s, idx=None: st.write(s.quality),
            ),
            ColumnConfig(
                name="Equip",
                width=0.15,
                process=self.equip,
            ),
        )

    def _add_description(self, item: Accessory, idx=None):
        st.divider()

    def equip(self, item: Accessory, idx: int | None = None):
        key_suffix = f"{item.name}-{idx}" if idx is not None else item.name
        disabled = item in st.session_state.char_controller.equipped_items()
        if st.button('Equip', key=f'{key_suffix}-equip', disabled=disabled):
            try:
                st.session_state.char_controller.equip_item(item)
                st.toast(f"Equipped {item.name.title()}")
            except Exception as e:
                st.warning(e, icon="🙅‍♂️")
            st.rerun()


class ItemTableWriter(TableWriter):
    @property
    def base_columns(self):
        return (
            ColumnConfig(
                name="Other items",
                width=0.2,
                process=lambda s, idx=None: st.write(s.name.title()),
            ),
            ColumnConfig(
                name="Cost",
                width=0.15,
                process=lambda s, idx=None: st.write(f"{s.cost} z"),
            ),
            ColumnConfig(
                name="Quality",
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
                name="Therioform",
                width=0.3,
                process=lambda t, idx=None: st.write(t.name.title()),
            ),
            ColumnConfig(
                name="Genoclepsis suggestions",
                width=0.7,
                process=lambda t, idx=None: st.write(t.creatures),
            ),
        )

    def _add_description(self, therioform: Therioform, idx=None):
        st.write(therioform.description)


def set_creation_state(state: CreationState):
    st.session_state.creation_step = state
    st.rerun()


def if_show_spells(casting_skill: Skill):
    if casting_skill and casting_skill.current_level > 0:
        return True
    return False

def list_skills(class_controller: ClassController, can_add_skill_number: int):
    with st.container(border=True):
        st.subheader(f"You can put {can_add_skill_number} more points to your skills.")
        st.write("You have selected following skills:")
        for skill in class_controller.char_class.skills:
            if skill.current_level > 0:
                show_skill(skill)

def show_skill(skill: Skill):
    st.markdown(f"**{skill.name.title()}** - level {skill.current_level}")

def show_martial(input: CharClass | Character):
    martial = {
        "martial_melee": "melee weapons",
        "martial_ranged": "ranged weapons",
        "martial_armor": "armor",
        "martial_shields": "shields"
    }
    if isinstance(input, CharClass):
        can_equip = input.can_equip_list()
    else:
        can_equip = set(chain.from_iterable([x.can_equip_list() for x in input.classes]))
    if can_equip:
        st.write(f"Your character can equip martial {', '.join(martial[m] for m in can_equip)}.")
    else:
        st.write(f"Your character can not equip martial items.")

@st.dialog("Create a new name")
def add_item_as(item: Item):
    new_name = st.text_input("Write new name here")
    if st.button(f"Add this item as {new_name}", disabled= not new_name):
        item = deepcopy(item)
        item.name = new_name.lower()
        if isinstance(item, Armor):
            st.session_state.start_equipment.backpack.armors.append(item)
        elif isinstance(item, Weapon):
            st.session_state.start_equipment.backpack.weapons.append(item)
        elif isinstance(item, Shield):
            st.session_state.start_equipment.backpack.shields.append(item)
        else:
            st.error("Unknown item type. Cannot add.")
            return
        st.toast(f"Added {new_name}")
        st.session_state.start_equipment.zenit -= item.cost
        st.rerun()
