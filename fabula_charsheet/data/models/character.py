from __future__ import annotations

import uuid
from typing import TYPE_CHECKING
from enum import StrEnum, auto

from pydantic import BaseModel, Field, ConfigDict, conint

from .bonds import Bond
from .char_class import CharClass, ClassName
from .attributes import Dexterity, Might, Willpower, Insight
from .inventory import Inventory
from .skill import HeroicSkill, HeroicSkillName
from .spell import Spell, ChimeristSpell
from .therioform import Therioform
from .dance import Dance

if TYPE_CHECKING:
    from data.models import LocNamespace


class CharacterTheme(StrEnum):
    ambition = auto()
    anger = auto()
    belonging = auto()
    doubt = auto()
    duty = auto()
    guilt = auto()
    hope = auto()
    justice = auto()
    mercy = auto()
    vengeance = auto()

    def localized_name(self, loc: LocNamespace) -> str:
        key = f"theme_{self.name}"
        return getattr(loc, key, self.name.capitalize())

class InvalidCharacterField(Exception):
    pass


class CharSpecial(BaseModel):
    therioforms: list[Therioform] = list()
    dances: list[Dance] = list()

    def get_special(self, attribute: str):
        return getattr(self, attribute, None)

class Character(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str = ""
    level: conint(ge=1, le=60) = 5
    identity: str = ""
    theme: str = ""
    origin: str = ""
    classes: list[CharClass] = list()
    dexterity: Dexterity = Field(default_factory=Dexterity)
    might: Might = Field(default_factory=Might)
    insight: Insight = Field(default_factory=Insight)
    willpower: Willpower = Field(default_factory=Willpower)
    inventory: Inventory = Field(default_factory=Inventory)
    spells: dict[ClassName, list[Spell | ChimeristSpell]] = dict()
    special: CharSpecial = Field(default_factory=CharSpecial)
    heroic_skills: list[HeroicSkill] = list()
    bonds: list[Bond] = list()

    def set_level(self, level: int, loc: LocNamespace):
        if not 1 <= level <= 60:
            msg = loc.error_invalid_level.format(level=level) if hasattr(loc,
                                                                         "error_invalid_level") else f"Level {level} should be between 1 and 60."
            raise InvalidCharacterField(msg)
        self.level = level

    def set_identity(self, identity: str, loc: LocNamespace):
        if not identity:
            msg = loc.error_identity_empty if hasattr(loc,
                                                      "error_identity_empty") else "Identity should not be empty."
            raise InvalidCharacterField(msg)
        self.identity = identity

    def set_name(self, name: str, loc: LocNamespace):
        if not name:
            msg = loc.error_name_empty if hasattr(loc, "error_name_empty") else "Name should not be empty."
            raise InvalidCharacterField(msg)
        self.name = name

    def set_theme(self, theme: str, loc: LocNamespace):
        if not theme:
            msg = loc.error_theme_empty if hasattr(loc, "error_theme_empty") else "Theme should not be empty."
            raise InvalidCharacterField(msg)
        self.theme = theme

    def set_origin(self, origin: str, loc: LocNamespace):
        if not origin:
            msg = loc.error_origin_empty if hasattr(loc, "error_origin_empty") else "Origin should not be empty."
            raise InvalidCharacterField(msg)
        self.origin = origin

    def get_n_skill(self) -> int:
        n_skills = 0
        for char_class in self.classes:
            for skill in char_class.skills:
                n_skills += skill.current_level
        return n_skills

    def get_spells_by_class(self, class_name: str | None) -> list[Spell]:
        if class_name is None:
            return []
        for spell_class, spell_list in self.spells.items():
            if spell_class == class_name.lower():
                return spell_list
        return []

    def get_all_spells(self) -> list[Spell]:
        spell_list = []
        for class_spells in self.spells.values():
            spell_list.extend(class_spells)
        return spell_list

    def get_class(self, class_name: str | None) -> CharClass | None:
        if class_name is None:
            return None
        for char_class in self.classes:
            if char_class.name == class_name.lower():
                return char_class
        return None

    def has_heroic_skill(self, heroic_skill_name : HeroicSkillName) -> bool:
        if heroic_skill_name.name in self.heroic_skills:
            return True
        else:
            return False
