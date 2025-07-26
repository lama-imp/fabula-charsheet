from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, conint

from .char_class import CharClass, ClassName
from .attributes import Dexterity, Might, Willpower, Insight
from .inventory import Inventory
from .spell import Spell

character_themes = [
    "ambition",
    "anger",
    "belonging",
    "doubt",
    "duty",
    "guilt",
    "hope",
    "justice",
    "mercy",
    "vengeance"
]

class InvalidCharacterField(Exception):
    pass

class Therioform(BaseModel):
    name: str = ""
    description: str = ""
    creatures: str = ""
    added: bool = False

class CharSpecial(BaseModel):
    therioforms: list[Therioform] = list()

    def get_special(self, attribute: str):
        return getattr(self, attribute, None)

class Character(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str = ""
    level: int = conint(ge=1, le=60)
    identity: str = ""
    theme: str = ""
    origin: str = ""
    classes: list[CharClass] = list()
    dexterity: Dexterity = Field(default_factory=Dexterity)
    might: Might = Field(default_factory=Might)
    insight: Insight = Field(default_factory=Insight)
    willpower: Willpower = Field(default_factory=Willpower)
    inventory: Inventory = Field(default_factory=Inventory)
    spells: dict[ClassName, list[Spell]] = dict()
    special: CharSpecial = Field(default_factory=CharSpecial)
    
    def set_level(self, level: int):
        if not 1 <= level <= 60:
            raise InvalidCharacterField(f"Level {level} should be between 1 and 60.")
        self.level = level
    
    def set_identity(self, identity: str):
        if not identity:
            raise InvalidCharacterField(f"Identity should not be empty.")
        self.identity = identity
    
    def set_name(self, name: str):
        if not name:
            raise InvalidCharacterField(f"Name should not be empty.")
        self.name = name
    
    def set_theme(self, theme: str):
        if not theme:
            raise InvalidCharacterField(f"Theme should not be empty.")
        self.theme = theme
    
    def set_origin(self, origin: str):
        if not origin:
            raise InvalidCharacterField(f"Origin should not be empty.")
        self.origin = origin

    def get_n_skill(self) -> int:
        n_classes = 0
        for char_class in self.classes:
            for skill in char_class.skills:
                n_classes += skill.current_level
        return n_classes

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
