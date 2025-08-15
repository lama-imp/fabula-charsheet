from __future__ import annotations
from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class Species(StrEnum):
    beast = auto()
    construct = auto()
    demon = auto()
    elemental = auto()
    humanoid = auto()
    monster = auto()
    plant = auto()
    undead = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"species_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()
