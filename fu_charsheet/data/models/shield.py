from .item import Item


class Shield(Item):
    martial: bool = False
    bonus_defense: int = 0
    bonus_magic_defense: int = 0
    bonus_initiative: int = 0
