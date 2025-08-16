from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, Literal
from pydantic import BaseModel

if TYPE_CHECKING:
    from data.models import LocNamespace


class DanceDuration(StrEnum):
    instantaneous = auto()
    next_turn = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"dance_duration_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

class Dance(BaseModel):
    name: str = ""
    duration: DanceDuration = DanceDuration.instantaneous

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"dance_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"dance_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")
