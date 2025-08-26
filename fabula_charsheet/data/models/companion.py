from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Annotated
from annotated_types import Len

from pydantic import BaseModel, Field, ConfigDict, conint

from .bonds import Bond
from .char_class import CharClass, ClassName
from .attributes import Dexterity, Might, Willpower, Insight, AttributeName
from .inventory import Equipped
from .skill import HeroicSkill, HeroicSkillName
from .spell import Spell, ChimeristSpell
from .therioform import Therioform
from .dance import Dance
from .arcana import Arcanum
from .species import Species
from .skill import Skill
from .damage import DamageType

if TYPE_CHECKING:
    from data.models import LocNamespace


class NPCAttack(BaseModel):
    name: str = ""
    accuracy: Annotated[
        list[AttributeName],
        Len(min_length=2, max_length=2)
    ] = Field(default_factory=lambda: [AttributeName.dexterity, AttributeName.might])
    damage_type: DamageType = DamageType.physical
    bonus_damage: int = 0


class NPCSkill(BaseModel):
    name: str = ""
    description: str = ""

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"npc_skill_{self.name}"
        return getattr(loc, key, self.name.capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"npc_skill_{self.name}_description"
        return getattr(loc, key, self.description)

class Companion(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str = ""
    level: conint(ge=1, le=60) = 5
    dexterity: Dexterity = Field(default_factory=Dexterity)
    might: Might = Field(default_factory=Might)
    insight: Insight = Field(default_factory=Insight)
    willpower: Willpower = Field(default_factory=Willpower)
    base_attacks: Annotated[
        list[NPCAttack],
        Len(min_length=0, max_length=2)
    ]
    bonus_accuracy: int = 0
    bonus_magic: int = 0
    skills: list[NPCSkill] = list()
    equipped: Equipped = Field(default_factory=Equipped)
    species: Species
