from __future__ import annotations

from pydantic import BaseModel
from typing import TYPE_CHECKING

from .class_name import ClassName

if TYPE_CHECKING:
    from data.models import LocNamespace


class Skill(BaseModel):
    name: str = ""
    current_level: int = 0
    max_level: int = 10
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
    required_skill: list[Skill] = list()
    can_add_several_times: bool = False

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"skill_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")
