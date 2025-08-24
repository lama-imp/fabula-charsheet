from __future__ import annotations
from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class Arcanum(BaseModel):
    name: str = ""

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"arcanum_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def merge(self, loc: LocNamespace) -> str:
        key = f"arcanum_{self.name}_merge"
        return getattr(loc, key, "No merge desciption found")

    def dismiss(self, loc: LocNamespace) -> str:
        key = f"arcanum_{self.name}_dismiss"
        return getattr(loc, key, "No dismiss desciption found")

    def domains(self, loc: LocNamespace) -> str:
        key = f"arcanum_{self.name}_domains"
        return getattr(loc, key, "No domains found")
