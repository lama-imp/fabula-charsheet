from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace

class DamageType(StrEnum):
    physical = auto()
    air = auto()
    earth = auto()
    ice = auto()
    fire = auto()
    lightning = auto()
    dark = auto()
    light = auto()
    poison = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"damage_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()
