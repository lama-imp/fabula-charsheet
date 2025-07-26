from pathlib import Path


PROJECT_ROOT_DIRECTORY = Path(__file__).parent

ASSETS_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, "assets").resolve()
assert ASSETS_DIRECTORY.is_dir(), "Assets directory does not exist"

SAVED_CHARS_DIRECTORY = Path(PROJECT_ROOT_DIRECTORY, "characters").resolve()
SAVED_CHARS_DIRECTORY.mkdir(parents=True, exist_ok=True)

Path(SAVED_CHARS_DIRECTORY, "character_images").mkdir(parents=True, exist_ok=True)
