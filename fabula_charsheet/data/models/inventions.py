from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, Literal
from pydantic import BaseModel

if TYPE_CHECKING:
    from data.models import LocNamespace

class Invention(BaseModel):
    name: str = ""

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"invention_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"invention_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")
