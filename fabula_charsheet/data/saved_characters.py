from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from data.models import Character


SAVED_CHARS: SavedChars | None = None


@dataclass(frozen=True)
class SavedChars:
    char_list: list[Character]


def init(saved_chars_directory: Path) -> None:
    global SAVED_CHARS
    if SAVED_CHARS is not None:
        return

    char_list = []
    for yaml_file in saved_chars_directory.glob('*.yaml'):
        with yaml_file.open(encoding='utf8') as f:
            raw_char = yaml.load(f, Loader=yaml.Loader)
            char_list.append(Character(**dict(raw_char)))

    s = SavedChars(
        char_list=char_list,
    )
    SAVED_CHARS = s


if __name__ == "__main__":
    init(Path("fabula_charsheet/characters"))
    print(SAVED_CHARS)
