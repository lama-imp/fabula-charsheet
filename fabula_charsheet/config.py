from pathlib import Path


PROJECT_ROOT_DIRECTORY = Path(__file__).parent

ASSETS_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, "assets").resolve()
assert ASSETS_DIRECTORY.is_dir(), "Assets directory does not exist"

SAVED_CHARS_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, "characters").resolve()
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
