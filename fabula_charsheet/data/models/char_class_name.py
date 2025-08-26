from __future__ import annotations
from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class ClassName(StrEnum):
    arcanist = auto()
    chimerist = auto()
    dark_blade = auto()
    elementalist = auto()
    entropist = auto()
    fury = auto()
    guardian = auto()
    loremaster = auto()
    mutant = auto()
    orator = auto()
    rogue = auto()
    spiritist = auto()
    sharpshooter = auto()
    tinkerer = auto()
    wayfarer = auto()
    weaponmaster = auto()
    dancer = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"class_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()
