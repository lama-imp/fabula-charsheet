from __future__ import annotations
from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class Arcanum(BaseModel):
    name: str = ""
    custom_domains: str | None = None
    custom_merge: str | None = None
    custom_dismiss: str | None = None

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"arcanum_{self.name}"
        return getattr(loc, key, self.name)

    def merge(self, loc: LocNamespace) -> str:
        if self.custom_merge is not None:
            return self.custom_merge
        key = f"arcanum_{self.name}_merge"
        return getattr(loc, key, "No merge desciption found")

    def dismiss(self, loc: LocNamespace) -> str:
        if self.custom_dismiss is not None:
            return self.custom_dismiss
        key = f"arcanum_{self.name}_dismiss"
        return getattr(loc, key, "No dismiss desciption found")

    def domains(self, loc: LocNamespace) -> str:
        if self.custom_domains is not None:
            return self.custom_domains
        key = f"arcanum_{self.name}_domains"
        return getattr(loc, key, "No domains found")
