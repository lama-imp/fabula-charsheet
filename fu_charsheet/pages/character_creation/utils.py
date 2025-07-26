from collections.abc import Iterable, Callable
from copy import deepcopy
from itertools import chain
from typing import Optional

import streamlit as st
from pydantic import BaseModel

from data.models.character_config import Skill, Spell, Weapon, Armor, AttributeName, CharClass, Character, Shield, \
    Accessory, Therioform
from .controller import ClassController
from .creation_state import CreationState


class ColumnConfig(BaseModel):
    key: str
    name: str
    width: float
    process: Optional[Callable]

class TableWriter:
    columns = None

    def __init__(self):
        assert self.columns

    def write_in_columns(
            self,
            data: Iterable,
            header: bool = True
    ):
        if header:
            self._write_header()

        for item in data:
            for cell, column_config in zip(st.columns(spec=[col['width'] for col in self.columns]),
                                           self.columns):
                with cell:
                    column_config.get('process')(item)

            self._add_description(item)

    def _write_header(self):
        for cell, column_name in zip(st.columns(spec=[col['width'] for col in self.columns]),
                                     (col['name'] for col in self.columns)):
            with cell:
                st.markdown(f"##### {column_name}")

    def _add_description(self, item):
        raise NotImplementedError


class SkillTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Skill",
                "width": 0.2,
                "process": lambda s: st.write(s.name.title()),
            },
            {
                "name": "Description",
                "width": 0.7,
                "process": lambda s: st.write(s.description),
            },
            {
                "name": "Level",
                "width": 0.2,
                "process": self._level_input
            },
        )
        super().__init__()

    @staticmethod
    def _level_input(skill: Skill):
        if skill.max_level > 1:
            level = st.slider("level", min_value=0, max_value=skill.max_level,
                              key=f"{skill.name}-slider",
                              label_visibility="hidden", )
        else:
            level = int(st.toggle("level2", label_visibility="hidden", key=f"{skill.name}-toggle"))
        skill.current_level = level

    def _add_description(self, item):
        pass


class SpellTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Spell",
                "width": 0.25,
                "process": self.write_spell_name,
            },
            {
                "name": "MP",
                "width": 0.15,
                "process": self.write_mp_cost,
            },
            {
                "name": "Target",
                "width": 0.25,
                "process": self.write_target
            },
            {
                "name": "Duration",
                "width": 0.2,
                "process": self.write_duration
            },
            {
                "name": "Select",
                "width": 0.15,
                "process": self.spell_selector
            },
        )
        super().__init__()


    def _add_description(self, item):
        st.markdown(item.description)
        st.divider()

    def write_spell_name(self, spell: Spell):
        st.write(f"{spell.name.title()}{'⚡' if spell.is_offensive else ''}")

    def write_mp_cost(self, spell: Spell):
        st.write(f"{spell.mp_cost}{' x T' if spell.target == 'up_to_three' else ''}")

    def write_target(self, spell: Spell):
        mapping = {
            "one_creature": "One creature",
            "up_to_three": "Up to three creatures",
            "weapon": "One equipped weapon",
            "self": "Self",
            "special": "Special",
        }
        st.write(mapping[spell.target])

    def write_duration(self, spell: Spell):
        st.write(spell.duration.title())

    def spell_selector(self, spell: Spell):
        if st.checkbox("add spell", label_visibility="hidden", key=f"{spell.name}-toggle"):
            if spell not in st.session_state.class_spells:
                st.session_state.class_spells.append(spell)
        else:
            if spell in st.session_state.class_spells:
                st.session_state.class_spells.remove(spell)


class WeaponTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Weapon",
                "width": 0.2,
                "process": lambda s: st.write(f"{s.name.title()} {'♦️' if s.martial else ''}"),
            },
            {
                "name": "Cost",
                "width": 0.15,
                "process": lambda s: st.write(f"{s.cost} z"),
            },
            {
                "name": "Accuracy",
                "width": 0.2,
                "process": lambda s: st.write(s.format_accuracy())
            },
            {
                "name": "Damage",
                "width": 0.2,
                "process": lambda s: st.write(f"【HR + {s.bonus_damage}】 {s.damage_type}")
            },
            {
                "name": "Add",
                "width": 0.15,
                "process": self._add_weapon
            },
        )
        super().__init__()

    def _add_description(self, item: Weapon):
        st.write(
            " ◆ ".join((
                item.grip_type.title().replace('_', '-'),
                item.range.title(),
                item.quality,
            ))
        )
        st.divider()

    def _add_weapon(self, weapon: Weapon):
        cannot_equip = False
        if weapon.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.can_equip_weapon(weapon.range):
                    cannot_equip = False

        if st.button('Add', key=f"{weapon.name}-add", disabled=cannot_equip):
            st.session_state.start_equipment.backpack.weapons.append(deepcopy(weapon))
            st.session_state.start_equipment.zenit -= weapon.cost
        if st.button('Remove', key=f"{weapon.name}-remove"):
            if weapon in st.session_state.start_equipment.backpack.weapons:
                st.session_state.start_equipment.backpack.weapons.remove(weapon)
                st.session_state.start_equipment.zenit += weapon.cost

    def _equip(self, item: Weapon):
        cannot_equip = False
        if item.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False
        if item in st.session_state.char_controller.equipped_items():
            cannot_equip = True
        if st.button('Equip',
                     key=f'{item.name}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
            except Exception as e:
                st.warning(e)
            st.rerun()


class ArmorTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Armor",
                "width": 0.2,
                "process": lambda s: st.write(f"{s.name.title()} {'♦️' if s.martial else ''}"),
            },
            {
                "name": "Cost",
                "width": 0.15,
                "process": lambda s: st.write(f"{s.cost} z"),
            },
            {
                "name": "Defense",
                "width": 0.155,
                "process": self._write_defense
            },
            {
                "name": "M.Defense",
                "width": 0.155,
                "process": self._write_magic_defense
            },
            {
                "name": "Initiative",
                "width": 0.15,
                "process": lambda s: st.write(str(s.bonus_initiative))
            },
            {
                "name": "Add",
                "width": 0.15,
                "process": self._add_armor
            },
        )
        super().__init__()

    def _add_description(self, item: Armor):
        st.write(item.quality)
        st.divider()

    def _add_armor(self, armor: Armor):
        cannot_equip = False
        if armor.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False

        if st.button('Add', key=f"{armor.name}-add", disabled=cannot_equip):
            st.session_state.start_equipment.backpack.armors.append(deepcopy(armor))
            st.session_state.start_equipment.zenit -= armor.cost
        if st.button('Remove', key=f"{armor.name}-remove"):
            if armor in st.session_state.start_equipment.backpack.armors:
                st.session_state.start_equipment.backpack.armors.remove(armor)
                st.session_state.start_equipment.zenit += armor.cost

    def _write_defense(self, item: Armor):
        def_bonus = f" + {item.bonus_defense}" if item.bonus_defense > 0 else ""
        if isinstance(item.defense, AttributeName):
            st.write(f"{AttributeName.to_alias(item.defense)}{def_bonus}")
        else:
            st.write(f"{str(item.defense)}{def_bonus}")

    def _write_magic_defense(self, item: Armor):
        def_bonus = f" + {item.bonus_magic_defense}" if item.bonus_magic_defense > 0 else ""
        if isinstance(item.magic_defense, AttributeName):
            st.write(f"{AttributeName.to_alias(item.magic_defense)}{def_bonus}")
        else:
            st.write(f"{str(item.magic_defense)}{def_bonus}")

    def _equip(self, item: Armor):
        cannot_equip = False
        if item.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False
        if item in st.session_state.char_controller.equipped_items():
            cannot_equip = True
        if st.button('Equip',
                     key=f'{item.name}-equip',
                     disabled=cannot_equip
        ):
            try:
                st.session_state.char_controller.equip_item(item)
            except Exception as e:
                st.warning(e)
            st.rerun()

class ShieldTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Shield",
                "width": 0.2,
                "process": lambda s: st.write(f"{s.name.title()} {'♦️' if s.martial else ''}"),
            },
            {
                "name": "Cost",
                "width": 0.15,
                "process": lambda s: st.write(f"{s.cost} z"),
            },
            {
                "name": "Defense",
                "width": 0.155,
                "process": self._write_defense
            },
            {
                "name": "M.Defense",
                "width": 0.155,
                "process": self._write_magic_defense
            },
            {
                "name": "Initiative",
                "width": 0.15,
                "process": lambda s: st.write(str(s.bonus_initiative))
            },
            {
                "name": "Add",
                "width": 0.15,
                "process": self._add_shield
            },
        )
        super().__init__()

    def _add_description(self, item: Shield):
        st.write(item.quality)
        st.divider()

    def _add_shield(self, shield: Shield):
        cannot_equip = False
        if shield.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False

        if st.button('Add', key=f"{shield.name}-add", disabled=cannot_equip):
            st.session_state.start_equipment.backpack.armors.append(deepcopy(shield))
            st.session_state.start_equipment.zenit -= shield.cost
        if st.button('Remove', key=f"{shield.name}-remove"):
            if shield in st.session_state.start_equipment.backpack.armors:
                st.session_state.start_equipment.backpack.armors.remove(shield)
                st.session_state.start_equipment.zenit += shield.cost

    def _write_defense(self, item: Shield):
        st.write(f"+{str(item.bonus_defense)}")

    def _write_magic_defense(self, item: Shield):
        st.write(f"+{str(item.bonus_magic_defense)}")

    def _equip(self, item: Shield):
        cannot_equip = False
        if item.martial:
            cannot_equip = True
            for char_class in st.session_state.creation_controller.character.classes:
                if char_class.martial_armor:
                    cannot_equip = False
        if item in st.session_state.char_controller.equipped_items():
            cannot_equip = True
        if st.button('Equip',
                     key=f'{item.name}-equip',
                     disabled=cannot_equip):
            try:
                st.session_state.char_controller.equip_item(item)
            except Exception as e:
                st.warning(e)
            st.rerun()


class AccessoryTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Accessory",
                "width": 0.2,
                "process": lambda s: st.write(s.name.title()),
            },
            {
                "name": "Cost",
                "width": 0.15,
                "process": lambda s: st.write(f"{s.cost} z"),
            },
            {
                "name": "Quality",
                "width": 0.155,
                "process": lambda s: st.write(s.quality),
            },
            {
                "name": "Equip",
                "width": 0.15,
                "process": self._equip
            },
        )
        super().__init__()

    def _add_description(self, item: Accessory):
        st.divider()

    def _equip(self, item: Accessory):
        if st.button('Equip',
                     key=f'{item.name}-equip',
                     disabled=(item in st.session_state.char_controller.equipped_items())):
            try:
                st.session_state.char_controller.equip_item(item)
            except Exception as e:
                st.warning(e)
            st.rerun()



class ItemTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Other items",
                "width": 0.2,
                "process": lambda s: st.write(s.name.title()),
            },
            {
                "name": "Cost",
                "width": 0.15,
                "process": lambda s: st.write(f"{s.cost} z"),
            },
            {
                "name": "Quality",
                "width": 0.155,
                "process": lambda s: st.write(f"{s.quality} z"),
            },
        )
        super().__init__()

    def _add_description(self, item: Accessory):
        st.divider()


class TherioformTableWriter(TableWriter):
    def __init__(self):
        self.columns = (
            {
                "name": "Therioform",
                "width": 0.3,
                "process": lambda t: st.write(t.name.title()),
            },
            {
                "name": "Genoclepsis suggestions",
                "width": 0.7,
                "process": lambda t: st.write(t.creatures),
            },
        )
        super().__init__()

    def _add_description(self, therioform: Therioform):
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
