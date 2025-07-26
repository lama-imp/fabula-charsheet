from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from pydantic import BaseModel

from data.models import Character
from data.models.character_config import Weapon, CharClass, Spell, ClassName, WeaponCategory, Armor, Shield

SAVED_CHARS: SavedChars | None = None


@dataclass(frozen=True)
class Equipment:
    weapons: list[Weapon]
    armors: list[Armor]

    def weapons_by_categories(self) -> dict[WeaponCategory, list[Weapon]]:
        categories = defaultdict(list)
        for weapon in self.weapons:
            categories[weapon.weapon_category].append(weapon)
        return categories


@dataclass(frozen=True)
class Classes:
    classes: list[CharClass] = field(default_factory=list)

    def get_class(self, name: str | None) -> CharClass | None:
        if name is None:
            return None
        for char_class in self.classes:
            if char_class.name == name.lower():
                return deepcopy(char_class)
        return None


@dataclass(frozen=True)
class Spells:
    spells: dict[ClassName, list[Spell]] = field(default_factory=dict)

    def get_spells(self, class_name: str | None) -> list[Spell]:
        if class_name is None:
            return []
        for char_class_name in self.spells.keys():
            if char_class_name == class_name.lower():
                return deepcopy(self.spells[char_class_name])
        return []


@dataclass(frozen=True)
class SavedChars:
    char_list: list[Character]


def init(saved_chars_directory: Path) -> None:
    global SAVED_CHARS
    if SAVED_CHARS is not None:
        return

    char_list = []
    for yaml_file in saved_chars_directory.glob('*.yaml'):
        with yaml_file.open(encoding='utf8') as f:
            raw_char = yaml.load(f, Loader=yaml.Loader)
            char_list.append(Character(**dict(raw_char)))

    s = SavedChars(
        char_list=char_list,
    )
    SAVED_CHARS = s


if __name__ == "__main__":
    init(Path("/Users/macbook/Imp/fu_charsheet/fu_charsheet/characters"))
    print(SAVED_CHARS)
