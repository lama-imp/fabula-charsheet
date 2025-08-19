from __future__ import annotations
from pydantic import BaseModel

from .therioform import Therioform
from .status import Status
from .attributes import Attribute


class CharState(BaseModel):
    minus_hp: int = 0
    minus_mp: int = 0
    minus_ip: int = 0
    statuses: list[Status] = list()
    improved_attributes: list[Attribute] = list()
    active_therioforms: list[Therioform] = list()
