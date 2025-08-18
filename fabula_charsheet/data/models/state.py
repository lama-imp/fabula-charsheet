from __future__ import annotations
from pydantic import BaseModel

from .status import Status


class CharState(BaseModel):
    minus_hp: int = 0
    minus_mp: int = 0
    minus_ip: int = 0
    statuses: list[Status] = list()
