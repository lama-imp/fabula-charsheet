import os
import sys
from pathlib import Path


PROJECT_ROOT_DIRECTORY = Path(__file__).parent

# True when running from the packaged executable (PyInstaller build).
IS_FROZEN = getattr(sys, "frozen", False)


def _saved_chars_directory() -> Path:
    """Where characters are saved.

    - FABULA_CHARACTERS_DIR environment variable, if set.
    - Running from source: fabula_charsheet/characters (unchanged).
    - Packaged app on Windows/Linux: a "characters" folder next to the
      executable, so the whole app folder stays portable.
    - Packaged app on macOS: ~/Documents/Interactive Character Sheet/characters, because
      the .app bundle itself must not be written to.
    """
    override = os.environ.get("FABULA_CHARACTERS_DIR")
    if override:
        return Path(override)
    if not IS_FROZEN:
        return Path(PROJECT_ROOT_DIRECTORY, "characters")
    if sys.platform == "darwin":
        return Path.home() / "Documents" / "Interactive Character Sheet" / "characters"
    return Path(sys.executable).parent / "characters"


ASSETS_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, "assets").resolve()
assert ASSETS_DIRECTORY.is_dir(), "Assets directory does not exist"

SAVED_CHARS_DIRECTORY = _saved_chars_directory().resolve()
SAVED_CHARS_DIRECTORY.mkdir(parents=True, exist_ok=True)

SAVED_CHARS_IMG_DIRECTORY = Path(SAVED_CHARS_DIRECTORY, "character_images").resolve()
SAVED_CHARS_IMG_DIRECTORY.mkdir(parents=True, exist_ok=True)

SAVED_STATES_DIRECTORY = Path(SAVED_CHARS_DIRECTORY, "states").resolve()
SAVED_STATES_DIRECTORY.mkdir(parents=True, exist_ok=True)

LOCALS_DIRECTORY = Path(ASSETS_DIRECTORY, "locals").resolve()
LOCALS_DIRECTORY.mkdir(parents=True, exist_ok=True)

default_avatar_path = Path(ASSETS_DIRECTORY, "images/default_avatar_2.png")

MIN_ATTRIBUTE_VALUE = 6
MAX_ATTRIBUTE_VALUE = 12

BASE_ATTRIBUTE_SUM = 32
ATTRIBUTE_SUM_AT_LEVEL_20 = BASE_ATTRIBUTE_SUM + 2
ATTRIBUTE_SUM_AT_LEVEL_40 = BASE_ATTRIBUTE_SUM + 4
