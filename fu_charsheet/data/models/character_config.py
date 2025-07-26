from __future__ import annotations
from annotated_types import Len
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Annotated, List
from enum import StrEnum, auto


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

class ClassName(StrEnum):
    chimerist = auto()
    spiritist =  auto()
    rogue = auto()
    mutant = auto()

class ClassBonus(StrEnum):
    mp = auto()
    hp = auto()
    ip = auto()

class Ritual(StrEnum):
    ritualism = auto()
    spiritism = auto()
    chimerism = auto()
    elementalism = auto()
    entropism = auto()

class Skill(BaseModel):
    name: str = ""
    description: str = ""
    current_level: int = 0
    max_level: int = 10
    can_add_spell: bool = False

class CharClass(BaseModel):
    name: ClassName | None = None
    class_bonus: ClassBonus | None = None
    bonus_value: int = 0
    martial_melee: bool = False
    martial_ranged: bool = False
    martial_armor: bool = False
    martial_shields: bool = False
    rituals: list[Ritual] = list()
    skills: list[Skill] = list()

    def class_level(self):
        return sum([s.current_level for s in self.skills])

    def can_equip_list(self) -> list[str]:
        return [
            key for key in ("martial_melee",
                            "martial_ranged",
                            "martial_armor",
                            "martial_shields")
            if getattr(self, key)
        ]

    def can_equip_weapon(self, weapon_range: WeaponRange) -> bool:
        if weapon_range == "meledd" and self.martial_melee:
            return True
        if weapon_range == "ranged" and self.martial_ranged:
            return True
        return False

    def clear_skills(self):
        self.skills.clear()

    def get_skill(self, name: str | None) -> Skill | None:
        if name is None:
            return None
        for skill in self.skills:
            if skill.name == name.lower():
                return skill
        return None

    def get_spell_skill(self) -> Skill | None:
        for skill in self.skills:
            if skill.can_add_spell:
                return skill
        return None

    def levelup_skill(self, new_skill_name: str):
        for skill in self.skills:
            if skill.name == new_skill_name:
                skill.current_level +=1

    def get_skill_level(self, skill_name: str) -> int | None:
        for skill in self.skills:
            if skill.name == skill_name.lower():
                return skill.current_level


class MutantClass(CharClass):
    therioforms: list[Therioform] = list()

class WeaponCategory(StrEnum):
    arcane = auto()
    bow = auto()
    brawling = auto()
    firearm = auto()
    dagger = auto()
    flail = auto()
    heavy = auto()
    spear = auto()
    sword = auto()
    thrown = auto()

class GripType(StrEnum):
    one_handed = auto()
    two_handed = auto()

class WeaponRange(StrEnum):
    melee = auto()
    ranged = auto()

class DamageType(StrEnum):
    physical = auto()
    air = auto()
    earth = auto()
    ice = auto()
    fire = auto()
    lightning = auto()
    dark = auto()
    light = auto()
    poison = auto()

class Item(BaseModel):
    name: str = ""
    cost: int = 0
    quality: str = "No Quality"


class Weapon(Item):
    martial: bool = False
    grip_type: GripType = GripType.one_handed
    range: WeaponRange = WeaponRange.melee
    weapon_category: WeaponCategory = WeaponCategory.brawling
    damage_type: DamageType = DamageType.physical
    accuracy: Annotated[
        list[AttributeName],
        Len(min_length=2, max_length=2)
    ] = Field(default_factory=lambda : [AttributeName.dexterity, AttributeName.might])
    bonus_accuracy: int = 0
    bonus_damage: int = 0

    def format_accuracy(self):
        return f"{AttributeName.to_alias(self.accuracy[0])} + {AttributeName.to_alias(self.accuracy[1])}"

class Armor(Item):
    martial: bool = False
    defense: AttributeName| int = Field(default_factory=lambda : AttributeName.dexterity)
    magic_defense: AttributeName = Field(default_factory=lambda : AttributeName.insight)
    bonus_defense: int = 0
    bonus_magic_defense: int = 0
    bonus_initiative: int = 0

class Shield(Item):
    martial: bool = False
    bonus_defense: int = 0
    bonus_magic_defense: int = 0
    bonus_initiative: int = 0

class Accessory(Item):
    effect: str = ""


class Equipped(BaseModel):
    armor: Armor | None = None
    weapon: Annotated[list[Weapon], Len(max_length=2)] = list()
    accessory: Accessory | None = None
    shield: Shield | None = None

class Backpack(BaseModel):
    armors: list[Armor] = list()
    weapons: list[Weapon] = list()
    shields: list[Shield] = list()
    accessories: list[Accessory] = list()
    other: list[Item] = list()

    def all_items(self):
        items = []
        items.extend(self.armors)
        items.extend(self.weapons)
        items.extend(self.shields)
        items.extend(self.accessories)
        items.extend(self.other)

        return items

    def add_item(self, item: Item):
        if isinstance(item, Weapon):
            self.weapons.append(item)
        elif isinstance(item, Armor):
            self.armors.append(item)
        elif isinstance(item, Shield):
            self.shields.append(item)
        elif isinstance(item, Accessory):
            self.accessories.append(item)
        else:
            self.other.append(item)

    def remove_item(self, item: Item):
        if isinstance(item, Weapon):
            self.weapons.remove(item)
        elif isinstance(item, Armor):
            self.armors.remove(item)
        elif isinstance(item, Shield):
            self.shields.remove(item)
        elif isinstance(item, Accessory):
            self.accessories.remove(item)
        else:
            self.other.remove(item)

class Inventory(BaseModel):
    zenit: int = 0
    equipped: Equipped = Field(default_factory=Equipped)
    backpack: Backpack = Field(default_factory=Backpack)

class SpellTarget(StrEnum):
    one_creature = auto()
    up_to_three = auto()
    weapon = auto()
    self = auto()
    special = auto()

class SpellDuration(StrEnum):
    instantaneous = auto()
    scene = auto()

class Spell(BaseModel):
    name: str = ""
    description: str = ""
    is_offensive: bool = False
    mp_cost: int
    target: SpellTarget = SpellTarget.one_creature
    duration: SpellDuration = SpellDuration.instantaneous
    damage_type: DamageType | None = None
    char_class: ClassName | None = None


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


class CharSpecial(BaseModel):
    therioforms: list[Therioform] = list()

    def get_special(self, attribute: str):
        return getattr(self, attribute, None)

class Character(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str = ""
    level: int = 5
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

class Status(StrEnum):
    dazed = auto()
    enraged = auto()
    poisoned = auto()
    shaken = auto()
    slow = auto()
    weak = auto()

class CharState(BaseModel):
    minus_hp: int = 0
    minus_mp: int = 0
    minus_ip: int = 0
    statuses: list[Status] = list()

class Therioform(BaseModel):
    name: str = ""
    description: str = ""
    creatures: str = ""
    added: bool = False

if __name__ == "__main__":
    d = Dexterity()
    weapon = Weapon()

    for a in weapon.accuracy:
        print(a, isinstance(d, a))
    print()
