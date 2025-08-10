from __future__ import annotations

from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace

class Item(BaseModel):
    name: str = ""
    cost: int = 0
    quality: str = "no_quality"

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"item_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

    def localized_quality(self, loc: LocNamespace) -> str:
        if self.quality == "no_quality":
            try:
                return getattr(loc, "item_no_quality")
            except AttributeError:
                return self.quality
        else:
            return self.quality
