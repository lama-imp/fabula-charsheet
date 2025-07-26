from __future__ import annotations
from pydantic import BaseModel
from enum import StrEnum, auto

from .char_class import ClassName
from .damage import DamageType


class SpellTarget(StrEnum):
    one_creature = auto()
    up_to_three = auto()
    weapon = auto()
    self = auto()
    special = auto()

class SpellDuration(StrEnum):
    instantaneous = auto()
    scene = auto()

class Spell(BaseModel):
    name: str = ""
    description: str = ""
    is_offensive: bool = False
    mp_cost: int
    target: SpellTarget = SpellTarget.one_creature
    duration: SpellDuration = SpellDuration.instantaneous
    damage_type: DamageType | None = None
    char_class: ClassName | None = None
