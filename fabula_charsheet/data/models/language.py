from enum import StrEnum, auto

from pydantic import RootModel


class LangEnum(StrEnum):
    en = auto()
    ru = auto()

class LocNamespace(RootModel[dict[str, str]]):
    def __getattr__(self, item: str) -> str:
        try:
            return self.root[item]
        except KeyError:
            raise AttributeError(f"Translation key '{item}' not found")

    def __getitem__(self, item: str) -> str:
        return self.root[item]
