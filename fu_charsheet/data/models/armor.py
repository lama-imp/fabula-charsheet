from pydantic import Field

from .item import Item
from .attributes import AttributeName

class Armor(Item):
    martial: bool = False
    defense: AttributeName| int = Field(default_factory=lambda : AttributeName.dexterity)
    magic_defense: AttributeName = Field(default_factory=lambda : AttributeName.insight)
    bonus_defense: int = 0
    bonus_magic_defense: int = 0
    bonus_initiative: int = 0
