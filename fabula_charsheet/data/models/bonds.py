from __future__ import annotations
from enum import StrEnum, auto
from pydantic import BaseModel
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from data.models import LocNamespace


class Emotion(StrEnum):
    admiration = auto()
    inferiority = auto()
    loyalty = auto()
    mistrust = auto()
    affection = auto()
    hatred = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"emotion_{self.name}"
        try:
            return getattr(loc, key)
        except AttributeError:
            return self.name.capitalize()


class Bond(BaseModel):
    name: str = ""
    respect: Literal[Emotion.admiration, Emotion.inferiority] | None = None
    trust: Literal[Emotion.loyalty, Emotion.mistrust] | None = None
    affinity: Literal[Emotion.affection, Emotion.hatred] | None = None
