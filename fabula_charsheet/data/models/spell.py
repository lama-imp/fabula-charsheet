from __future__ import annotations
from pydantic import BaseModel
from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace

from .char_class_name import ClassName
from .damage import DamageType
from .species import Species


class SpellTarget(StrEnum):
    one_creature = auto()
    up_to_three = auto()
    weapon = auto()
    self = auto()
    special = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"spell_target_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.replace("_", " ").capitalize()

class SpellDuration(StrEnum):
    instantaneous = auto()
    scene = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"spell_duration_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

class Spell(BaseModel):
    name: str = ""
    is_offensive: bool = False
    mp_cost: int
    target: SpellTarget = SpellTarget.one_creature
    duration: SpellDuration = SpellDuration.instantaneous
    damage_type: DamageType = DamageType.no_damage
    char_class: ClassName | None = None

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"spell_{self.name}"
        return getattr(loc, key, self.name)

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"spell_{self.name}_description"
        return getattr(loc, key, "No description found")

    def localized_damage(self, loc: LocNamespace) -> str:
        key = f"damage_{self.damage_type}"
        return getattr(loc, key, "Unknown damage")

class ChimeristSpell(Spell):
    species: Species
    description: str

    def localized_description(self, loc: LocNamespace) -> str:
        return self.description
