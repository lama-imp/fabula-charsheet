from __future__ import annotations
from pydantic import BaseModel

from .status import Status
from pages.controller import CharacterController
from data.models.character import Character



class CharState(BaseModel):
    minus_hp: int = 0
    minus_mp: int = 0
    minus_ip: int = 0
    statuses: list[Status] = list()

    def use_health_potion(self):
        self.minus_hp = max(0, self.minus_hp - 50)
        self.minus_ip = min(CharacterController.max_ip(), self.minus_ip + (2 if "deep_pockets" in Character.heroic_skills else 3) )