from __future__ import annotations
from pydantic import BaseModel

from .status import Status


class CharState(BaseModel):
    minus_hp: int = 0
    minus_mp: int = 0
    minus_ip: int = 0
    statuses: list[Status] = list()

    def use_health_potion(self, controller):
        self.minus_hp = max(0, self.minus_hp - 50)
        has_deep_pockets = any(
            skill.name == "deep_pockets" for skill in controller.character.heroic_skills
        )
        ip_cost = 2 if has_deep_pockets else 3
        self.minus_ip = min(controller.max_ip(), self.minus_ip + ip_cost)

    def use_mana_potion(self, controller):
        self.minus_mp = max(0, self.minus_mp - 50)
        has_deep_pockets = any(
            skill.name == "deep_pockets" for skill in controller.character.heroic_skills
        )
        ip_cost = 2 if has_deep_pockets else 3
        self.minus_ip = min(controller.max_ip(), self.minus_ip + ip_cost)
