from __future__ import annotations
from annotated_types import Len
from pydantic import Field
from typing import Annotated
from enum import StrEnum, auto

from .item import Item
from .damage import DamageType
from .attributes import AttributeName

class WeaponCategory(StrEnum):
    arcane = auto()
    bow = auto()
    brawling = auto()
    firearm = auto()
    dagger = auto()
    flail = auto()
    heavy = auto()
    spear = auto()
    sword = auto()
    thrown = auto()

class GripType(StrEnum):
    one_handed = auto()
    two_handed = auto()

class WeaponRange(StrEnum):
    melee = auto()
    ranged = auto()

class Weapon(Item):
    martial: bool = False
    grip_type: GripType = GripType.one_handed
    range: WeaponRange = WeaponRange.melee
    weapon_category: WeaponCategory = WeaponCategory.brawling
    damage_type: DamageType = DamageType.physical
    accuracy: Annotated[
        list[AttributeName],
        Len(min_length=2, max_length=2)
    ] = Field(default_factory=lambda : [AttributeName.dexterity, AttributeName.might])
    bonus_accuracy: int = 0
    bonus_damage: int = 0

    def format_accuracy(self):
        return f"{AttributeName.to_alias(self.accuracy[0])} + {AttributeName.to_alias(self.accuracy[1])}"
