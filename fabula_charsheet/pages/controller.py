from __future__ import annotations
import math
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from streamlit.runtime.uploaded_file_manager import UploadedFile

from config import SAVED_CHARS_DIRECTORY, SAVED_CHARS_IMG_DIRECTORY, SAVED_STATES_DIRECTORY
from data.models import (
    Character,
    CharClass,
    Ritual,
    Skill,
    ClassName,
    Spell,
    Accessory,
    Shield,
    Weapon,
    Armor,
    Item,
    CharState,
    Status,
    AttributeName,
    Therioform,
)

if TYPE_CHECKING:
    from data.models import LocNamespace


class CharacterController:
    def __init__(self, loc: LocNamespace):
        self.character = Character()
        self.loc = loc
        self.state = CharState()

    def get_character(self):
        return self.character

    def has_enough_skills(self):
        if not self.character.classes:
            return False
        if self.character.get_n_skill() != self.character.level:
            return False
        return True

    def add_class(self, new_class: CharClass):
        self.character.classes.append(new_class)

    def update_class(self, updated_class: CharClass):
        for i, existing in enumerate(self.character.classes):
            if existing.name == updated_class.name:
                self.character.classes[i] = updated_class
                return
        msg = self.loc.error_class_not_found.format(class_name=updated_class.name)
        raise ValueError(msg)

    def can_add_skill_number(self):
        return self.character.level - self.character.get_n_skill()

    def is_class_added(self, new_class: CharClass | str | None):
        if new_class is None:
            return False
        elif isinstance(new_class, CharClass):
            class_name = new_class.name
        elif isinstance(new_class, str):
            class_name = new_class.lower()
        else:
            msg = self.loc.error_unexpected_class_type.format(class_type=type(new_class))
            raise ValueError(msg)

        return any(c.name == class_name for c in self.character.classes)

    def has_skill(self, skill_name: str) -> bool:
        for char_class in self.character.classes:
            if char_class.get_skill(skill_name) and char_class.get_skill(skill_name).current_level > 0:
                return True
        return False

    def get_skills(self, class_name: ClassName) -> list[Skill]:
        if class_name in [c.name for c in self.character.classes]:
            idx = [c.name for c in self.character.classes].index(class_name)
            return self.character.classes[idx].skills
        return []

    def get_skill_level(self, char_class_name: ClassName, skill_name: str) -> int | None:
        for char_class in self.character.classes:
            if char_class.name == char_class_name:
                return char_class.get_skill_level(skill_name)

    def add_spell(self, spell: Spell, class_name: ClassName):
        if spell not in self.character.spells.get(class_name, []):
            self.character.spells[class_name] = self.character.spells.get(class_name, [])
            self.character.spells[class_name].append(spell)

    def remove_spell(self, spell: Spell, class_name: ClassName):
        if spell in self.character.spells.get(class_name, []):
            self.character.spells[class_name].remove(spell)

    def max_hp(self) -> int:
        return (
                self.character.level
                + self.character.might.base * 5
                + sum([c.bonus_value for c in self.character.classes if c.class_bonus == "hp"])
        )

    def max_mp(self) -> int:
        return (
                self.character.level
                + self.character.willpower.base * 5
                + sum([c.bonus_value for c in self.character.classes if c.class_bonus == "mp"])
        )

    def max_ip(self) -> int:
        return (
                6
                + sum([c.bonus_value for c in self.character.classes if c.class_bonus == "ip"])
        )

    def current_hp(self) -> int:
        return self.max_hp() - self.state.minus_hp

    def current_mp(self) -> int:
        return self.max_mp() - self.state.minus_mp

    def current_ip(self) -> int:
        return self.max_ip() - self.state.minus_ip

    def defense(self):
        armor = self.character.inventory.equipped.armor
        shield = self.character.inventory.equipped.shield
        weapon = self.character.inventory.equipped.weapon

        combined_weapon_bonus = 0
        if weapon:
            for weapon_item in weapon:
                combined_weapon_bonus += weapon_item.bonus_defense

        other_bonuses = 0
        for char_class in self.character.classes:
            if char_class.name == ClassName.rogue:
                for skill in char_class.skills:
                    if skill.name == "dodge":
                        other_bonuses += skill.current_level
        if armor:
            if isinstance(armor.defense, int):
                return (armor.defense 
                        + armor.bonus_defense 
                        + (shield.bonus_defense if shield else 0) 
                        + combined_weapon_bonus 
                        + other_bonuses)
            else:
                return self.character.dexterity.current + armor.bonus_defense + combined_weapon_bonus + other_bonuses
        return (self.character.dexterity.current 
            + (shield.bonus_defense if shield else 0) 
            + combined_weapon_bonus 
            + other_bonuses)

    def magic_defense(self):
        armor = self.character.inventory.equipped.armor
        shield = self.character.inventory.equipped.shield
        weapon = self.character.inventory.equipped.weapon

        combined_weapon_bonus = 0
        if weapon:
            for weapon_item in weapon:
                combined_weapon_bonus += weapon_item.bonus_magic_defense

        return (self.character.insight.current
                + (shield.bonus_magic_defense if shield else 0)
                + (armor.bonus_magic_defense if armor else 0)
                + combined_weapon_bonus
        )

    def initiative(self) -> str:
        armor = self.character.inventory.equipped.armor
        shield = self.character.inventory.equipped.shield
        initiative = f"{self.loc.dice_prefix}{self.character.insight.current} + {self.loc.dice_prefix}{self.character.dexterity.current}"
        bonus = 0
        if shield:
            bonus += shield.bonus_initiative
        if armor:
            bonus += armor.bonus_initiative

        if bonus:
            return f"{initiative} {bonus}"
        return initiative

    def equip_item(self, item: Item):
        if isinstance(item, Armor):
            self.character.inventory.equipped.armor = item
        elif isinstance(item, Weapon):
            equipped_weapon = self.character.inventory.equipped.weapon
            if len(equipped_weapon) == 1 and equipped_weapon[0].grip_type == "one_handed" and item.grip_type == "one_handed":
                self.character.inventory.equipped.weapon.append(item)
            else:
                self.character.inventory.equipped.weapon = [item]
        elif isinstance(item, Shield):
            self.character.inventory.equipped.shield = item
        elif isinstance(item, Accessory):
            self.character.inventory.equipped.accessory = item
        else:
            raise Exception(self.loc.error_equipping_item)

    def unequip_item(self, category: str):
        equipped = getattr(self.character.inventory.equipped, category)
        if equipped:
            if category == "weapon":
                self.character.inventory.equipped.weapon = []
            elif category == "armor":
                self.character.inventory.equipped.armor = None
            elif category == "shield":
                self.character.inventory.equipped.shield = None
            elif category == "accessory":
                self.character.inventory.equipped.accessory = None

    def equipped_items(self) -> list[Item]:
        equipped_items = []
        if self.character.inventory.equipped.shield:
            equipped_items.append(self.character.inventory.equipped.shield)
        if self.character.inventory.equipped.armor:
            equipped_items.append(self.character.inventory.equipped.armor)
        if self.character.inventory.equipped.accessory:
            equipped_items.append(self.character.inventory.equipped.accessory)
        if self.character.inventory.equipped.weapon:
            equipped_items.extend(self.character.inventory.equipped.weapon)
        return equipped_items

    def add_item(self, item: Item):
        self.character.inventory.backpack.add_item(item)

    def remove_item(self, item: Item):
        if item in self.equipped_items():
            if isinstance(item, Weapon):
                self.unequip_item("weapon")
            elif isinstance(item, Armor):
                self.unequip_item("armor")
            elif isinstance(item, Shield):
                self.unequip_item("shield")
            elif isinstance(item, Accessory):
                self.unequip_item("accessory")
        self.character.inventory.backpack.remove_item(item)


    def dump_character(self):
        with Path(
                SAVED_CHARS_DIRECTORY,
                f"{self.character.name}.{self.character.id}.character.yaml"
        ).open("w") as yaml_file:
            yaml.dump(
                self.character.model_dump(),
                yaml_file,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False
            )

    def dump_avatar(self, image: UploadedFile | None ):
        if image is not None:
            image_file_path = Path(
                    SAVED_CHARS_IMG_DIRECTORY,
                    f"{self.character.name}.{self.character.id}{Path(image.name).suffix}"
            )
            image_file_path.write_bytes(image.getbuffer())

    def apply_status(self):
        dex_malus = 0
        mig_malus = 0
        ins_malus = 0
        wlp_malus = 0
        if Status.dazed in self.state.statuses:
            ins_malus -= 2
        if Status.enraged in self.state.statuses:
            ins_malus -= 2
            dex_malus -= 2
        if Status.poisoned in self.state.statuses:
            mig_malus -= 2
            wlp_malus -= 2
        if Status.shaken in self.state.statuses:
            wlp_malus -= 2
        if Status.slow in self.state.statuses:
            dex_malus -= 2
        if Status.weak in self.state.statuses:
            mig_malus -= 2

        self.character.insight.current = max(6, self.character.insight.base + ins_malus)
        self.character.dexterity.current = max(6, self.character.dexterity.base + dex_malus)
        self.character.willpower.current = max(6, self.character.willpower.base + wlp_malus)
        self.character.might.current = max(6, self.character.might.base + mig_malus)

        return {
            AttributeName.dexterity: self.character.dexterity.base - self.character.dexterity.current,
            AttributeName.might: self.character.might.base - self.character.might.current,
            AttributeName.insight: self.character.insight.base - self.character.insight.current,
            AttributeName.willpower: self.character.willpower.base - self.character.willpower.current,
        }

    def crisis_value(self) -> int:
        return math.floor(self.max_hp() / 2)

    def can_add_heroic_skill(self) -> bool:
        mastered_classes = [char_class for char_class in self.character.classes if char_class.class_level() == 10]
        if len(mastered_classes) > len(self.character.heroic_skills):
            return True
        return False

    def can_add_class(self) -> bool:
        non_mastered_classes = [char_class for char_class in self.character.classes if char_class.class_level() < 10]
        return len(non_mastered_classes) < 3

    def can_increase_attribute(self) -> bool:
        sum_of_attributes = sum(
            [
                self.character.dexterity.base,
                self.character.might.base,
                self.character.insight.base,
                self.character.willpower.base,
            ]
        )
        if (
                self.character.level == 20 and sum_of_attributes < 34
        ) or (
                self.character.level == 40 and sum_of_attributes < 36
        ):
            return True

        return False

    def add_status(self, status: Status):
        if status not in self.state.statuses:
            self.state.statuses.append(status)

    def remove_status(self, status: Status):
        if status in self.state.statuses:
            self.state.statuses.remove(status)

    def dump_state(self):
        with Path(SAVED_STATES_DIRECTORY, f"{self.character.id}.yaml").open("w", encoding="utf-8") as yaml_file:
            yaml.dump(
                self.state.model_dump(),
                yaml_file,
                sort_keys=False,
                allow_unicode=True,
                default_flow_style=False
            )

    def load_state(self):
        try:
            with Path(SAVED_STATES_DIRECTORY, f"{self.character.id}.yaml").open('r', encoding="utf-8") as yaml_file:
                raw_state = yaml.load(yaml_file, Loader=yaml.Loader)
                self.state = CharState(**dict(raw_state))
        except:
            self.state = CharState()
            raise Exception("Unable to load state. Switching to default.")


class ClassController:
    def __init__(self):
        self.char_class = CharClass()

    def add_ritual(self, ritual: Ritual):
        self.char_class.rituals.append(ritual)

    def add_skill(self, skill: Skill):
        self.char_class.skills.append(skill)
