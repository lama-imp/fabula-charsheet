from __future__ import annotations

from pydantic import BaseModel
from typing import TYPE_CHECKING
from enum import StrEnum, auto

from .class_name import ClassName

if TYPE_CHECKING:
    from data.models import LocNamespace

class HeroicSkillName(StrEnum):
    deep_pockets = auto()
    monkey_grip = auto()
    chimeric_mastery = auto()
    comet = auto()
    greater_theriomorphosis = auto()
    hope = auto()
    volcano = auto()
    extra_hp = auto()
    extra_mp = auto()
    extra_ip = auto()
    extra_spells = auto()
    upgrade = auto()


class Skill(BaseModel):
    name: str = ""
    current_level: int = 0
    max_level: int = 1
    can_add_spell: bool = False

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")

class HeroicSkill(BaseModel):
    name: str = ""
    required_class: list[ClassName] = list()
    required_skill: Skill | None = None
    can_add_several_times: bool = False

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")
