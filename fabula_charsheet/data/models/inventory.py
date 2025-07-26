from __future__ import annotations
from annotated_types import Len
from pydantic import BaseModel, Field
from typing import Annotated

from .item import Item
from .weapon import Weapon
from .armor import Armor
from .shield import Shield
from .accessory import Accessory


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
