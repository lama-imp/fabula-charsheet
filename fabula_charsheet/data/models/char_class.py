from __future__ import annotations
from enum import StrEnum, auto
from pydantic import BaseModel
from typing import TYPE_CHECKING

from .skill import Skill
from .class_name import ClassName

if TYPE_CHECKING:
    from data.models import LocNamespace, WeaponRange


class ClassBonus(StrEnum):
    mp = auto()
    hp = auto()
    ip = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

    def localized_full_name(self, loc: LocNamespace):
        key = f"{self.name}_full"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

class Ritual(StrEnum):
    ritualism = auto()
    spiritism = auto()
    chimerism = auto()
    elementalism = auto()
    entropism = auto()
    arcanism = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"ritual_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

class CharClass(BaseModel):
    name: ClassName | None = None
    class_bonus: ClassBonus | list[ClassBonus] | None = None
    bonus_value: int = 0
    martial_melee: bool = False
    martial_ranged: bool = False
    martial_armor: bool = False
    martial_shields: bool = False
    rituals: list[Ritual] = list()
    skills: list[Skill] = list()

    def class_level(self):
        return sum([s.current_level for s in self.skills])

    def can_equip_list(self) -> list[str]:
        return [
            key for key in ("martial_melee",
                            "martial_ranged",
                            "martial_armor",
                            "martial_shields")
            if getattr(self, key)
        ]

    def can_equip_weapon(self, weapon_range: WeaponRange) -> bool:
        if weapon_range == "melee" and self.martial_melee:
            return True
        if weapon_range == "ranged" and self.martial_ranged:
            return True
        return False

    def clear_skills(self):
        self.skills.clear()

    def get_skill(self, name: str | None) -> Skill | None:
        if name is None:
            return None
        for skill in self.skills:
            if skill.name == name.lower():
                return skill
        return None

    def get_spell_skill(self) -> Skill | None:
        for skill in self.skills:
            if skill.can_add_spell:
                return skill
        return None

    def levelup_skill(self, new_skill_name: str):
        for skill in self.skills:
            if skill.name == new_skill_name:
                skill.current_level += 1

    def get_skill_level(self, skill_name: str) -> int | None:
        for skill in self.skills:
            if skill.name == skill_name.lower():
                return skill.current_level
