from enum import StrEnum, auto


class CreationState(StrEnum):
    identity = auto()
    classes = auto()
    attributes = auto()
    equipment = auto()
    preview = auto()
