from __future__ import annotations
from annotated_types import Len
from pydantic import Field
from typing import Annotated
from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace

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

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"weapon_category_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

class GripType(StrEnum):
    one_handed = auto()
    two_handed = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"grip_type_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.replace("_", " ").capitalize()

class WeaponRange(StrEnum):
    melee = auto()
    ranged = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"weapon_range_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

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
    bonus_defense: int = 0
    bonus_magic_defense: int = 0


    def format_accuracy(self, loc: LocNamespace):
        return f"{AttributeName.to_alias(self.accuracy[0], loc)} + {AttributeName.to_alias(self.accuracy[1], loc)}"
