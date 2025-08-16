from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from data.models import LocNamespace


class Therioform(BaseModel):
    name: str = ""

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"therioform_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"therioform_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")

    def localized_creatures(self, loc: LocNamespace) -> str:
        key = f"therioform_{self.name}_creatures"
        return getattr(loc, key, f"[Missing creatures for {self.name}]")
