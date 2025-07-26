from __future__ import annotations
from enum import StrEnum, auto
from pydantic import BaseModel


class AttributeName(StrEnum):
    dexterity = auto()
    might = auto()
    insight = auto()
    willpower = auto()

    @classmethod
    def to_alias(cls, attribute: AttributeName):
        match attribute:
            case cls.dexterity:
                return "DEX"
            case cls.might:
                return "MIG"
            case cls.insight:
                return "INS"
            case cls.willpower:
                return "WLP"
            case _:
                raise Exception

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
