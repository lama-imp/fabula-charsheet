from __future__ import annotations

from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class Quality(BaseModel):
    name: str = ""
    cost: int = 100

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"quality_{self.name}"
        return getattr(loc, key, self.name)

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"quality_{self.name}_description"
        return getattr(loc, key, "No description found")
