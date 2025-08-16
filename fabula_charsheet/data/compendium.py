from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import yaml
from pydantic import BaseModel

from data.models import Weapon, CharClass, Spell, ClassName, WeaponCategory, Armor, Shield, Therioform, Dance
from data.models.skill import HeroicSkill, Skill

COMPENDIUM: Compendium | None = None


@dataclass(frozen=True)
class Equipment:
    weapons: list[Weapon]
    armors: list[Armor]
    shields: list[Shield]

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
class HeroicSkills:
    heroic_skills: list[HeroicSkill] = field(default_factory=list)

    def get_skill(self, name: str | None) -> HeroicSkill | None:
        if name is None:
            return None
        for skill in self.heroic_skills:
            if skill.name == name.lower():
                return deepcopy(skill)
        return None


@dataclass(frozen=True)
class Compendium:
    equipment: Equipment
    classes: Classes
    spells: Spells
    heroic_skills: HeroicSkills
    therioforms: list[Therioform] = field(default_factory=list)
    dances: list[Dance] = field(default_factory=list)

    def get_class_name_from_skill(self, skill: Skill):
        for char_class in self.classes.classes:
            if char_class.get_skill(skill.name):
                return char_class.name
        return None


def get_assets_from_file(file_path: Path, asset_class: type[BaseModel]) -> list[BaseModel]:
    with file_path.open(encoding='utf8') as f:
        raw_assets = yaml.load(f, Loader=yaml.UnsafeLoader)
        if isinstance(raw_assets, list):
            return [asset_class(**item) for item in raw_assets]
        else:
            return [asset_class(**raw_assets)]


def init(assets_directory: Path) -> None:
    global COMPENDIUM
    if COMPENDIUM is not None:
        return

    equipment_directory = Path(assets_directory, 'equipment').resolve(strict=True)
    equipment_dict = {}
    for yaml_file in equipment_directory.glob('*.yaml'):
        item_mapping = {
            "weapons": Weapon,
            "armors": Armor,
            "shields": Shield,
        }
        equipment_dict[yaml_file.stem] = get_assets_from_file(yaml_file, item_mapping[yaml_file.stem])

    classes_directory = Path(assets_directory, 'classes').resolve(strict=True)
    classes_list = []
    for yaml_file in classes_directory.glob('*.yaml'):
        classes_list.extend(get_assets_from_file(yaml_file, CharClass))

    spells_directory = Path(assets_directory, 'spells').resolve(strict=True)
    spells_dict = {}
    for yaml_file in spells_directory.glob('*.yaml'):
        spells_dict[yaml_file.stem] = get_assets_from_file(yaml_file, Spell)

    heroic_skills_directory = Path(assets_directory, 'skills').resolve(strict=True)
    heroic_skills_list = []
    for yaml_file in heroic_skills_directory.glob('*.yaml'):
        heroic_skills_list.extend(get_assets_from_file(yaml_file, HeroicSkill))

    special_directory = Path(assets_directory, 'special').resolve(strict=True)
    special_dict = {}
    for yaml_file in special_directory.glob('*.yaml'):
        item_mapping = {
            "therioforms": Therioform,
            "dances": Dance,
        }
        special_dict[yaml_file.stem] = get_assets_from_file(yaml_file, item_mapping[yaml_file.stem])

    e = Equipment(**equipment_dict)
    c = Compendium(
        equipment=e,
        classes=Classes(classes=classes_list),
        spells=Spells(spells=spells_dict),
        heroic_skills=HeroicSkills(heroic_skills=heroic_skills_list),
        **special_dict,
    )
    COMPENDIUM = c


if __name__ == "__main__":
    init(Path("/Users/macbook/Imp/fabula_charsheet/fabula_charsheet/assets"))
    print(COMPENDIUM)
