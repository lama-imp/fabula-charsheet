from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class Status(StrEnum):
    dazed = auto()
    enraged = auto()
    poisoned = auto()
    shaken = auto()
    slow = auto()
    weak = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"status_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()
