from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from enum import StrEnum, auto

from annotated_types import Len
from pydantic import BaseModel, Field

from .attributes import AttributeName
from .damage import DamageType
from .species import Species
from .status import Status
from .weapon import WeaponRange

if TYPE_CHECKING:
    from data.models import LocNamespace


class CompanionSkillName(StrEnum):
    crisis_effect = auto()
    damage_absorption = auto()
    damage_immunity = auto()
    damage_resistance = auto()
    final_act = auto()
    flying = auto()
    improved_damage = auto()
    improved_defenses = auto()
    improved_hit_points = auto()
    reaction = auto()
    special_attack = auto()
    specialized = auto()
    status_effect_immunity = auto()
    unique_action = auto()


class CompanionSkill(BaseModel):
    name: CompanionSkillName
    damage_types: list[DamageType] = Field(default_factory=list)
    statuses: list[Status] = Field(default_factory=list)
    defense_option: str | None = None
    check_type: str | None = None
    check_context: str | None = None
    attack_index: int | None = None
    description: str = ""

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"npc_skill_{self.name}"
        return getattr(loc, key, self.name.replace("_", " ").capitalize())

    def localized_description(self, loc: LocNamespace) -> str:
        key = f"npc_skill_{self.name}_description"
        return getattr(loc, key, f"[Missing description for {self.name}]")


class CompanionAttack(BaseModel):
    name: str = ""
    accuracy: Annotated[
        list[AttributeName],
        Len(min_length=2, max_length=2)
    ] = Field(default_factory=lambda: [AttributeName.dexterity, AttributeName.might])
    damage_type: DamageType = DamageType.physical
    range: WeaponRange = WeaponRange.melee


SPECIES_STARTING_SKILLS: dict[Species, int] = {
    Species.beast: 4,
    Species.construct: 2,
    Species.elemental: 2,
    Species.plant: 3,
}

PLANT_VULNERABILITY_CHOICES: list[DamageType] = [
    DamageType.air,
    DamageType.lightning,
    DamageType.fire,
    DamageType.ice,
]


class Companion(BaseModel):
    name: str = ""
    species: Species = Species.beast
    dexterity: int = 8
    might: int = 8
    insight: int = 8
    willpower: int = 8
    species_damage_choice: DamageType | None = None
    basic_attacks: Annotated[
        list[CompanionAttack],
        Len(min_length=0, max_length=2)
    ] = Field(default_factory=list)
    skills: Annotated[
        list[CompanionSkill],
        Len(min_length=0, max_length=4)
    ] = Field(default_factory=list)

    def innate_resistances(self) -> list[DamageType]:
        if self.species == Species.construct:
            return [DamageType.earth]
        return []

    def innate_immunities(self) -> list[DamageType]:
        if self.species == Species.construct:
            return [DamageType.poison]
        if self.species == Species.elemental:
            immunities = [DamageType.poison]
            if self.species_damage_choice is not None:
                immunities.append(self.species_damage_choice)
            return immunities
        return []

    def innate_vulnerabilities(self) -> list[DamageType]:
        if self.species == Species.plant and self.species_damage_choice is not None:
            return [self.species_damage_choice]
        return []

    def innate_status_immunities(self) -> list[Status]:
        if self.species == Species.construct:
            return [Status.poisoned]
        if self.species == Species.elemental:
            return [Status.poisoned]
        if self.species == Species.plant:
            return [Status.dazed, Status.shaken, Status.enraged]
        return []
