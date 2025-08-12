from __future__ import annotations
from enum import StrEnum, auto
from pydantic import BaseModel
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.models import LocNamespace


class AttributeName(StrEnum):
    dexterity = auto()
    might = auto()
    insight = auto()
    willpower = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"attr_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()

    def to_alias(self, loc: LocNamespace) -> str:
        key_map = {
            AttributeName.dexterity: "attr_dexterity_alias",
            AttributeName.might: "attr_might_alias",
            AttributeName.insight: "attr_insight_alias",
            AttributeName.willpower: "attr_willpower_alias",
        }
        key = key_map.get(self)
        if not key:
            raise Exception(f"No localization key for attribute alias {self}")
        return getattr(loc, key)

class Attribute(BaseModel):
    base: int = 8
    current: int = 8

class Dexterity(Attribute):
    pass

class Might(Attribute):
    pass

class Insight(Attribute):
    pass

class Willpower(Attribute):
    pass
