# Fabula Ultima Interactive Character Sheet

Character creation and view.

## How it works

The app has two pages:
- **Character Creation** – a step-by-step wizard (identity → classes → attributes → equipment → preview) for building a new character from scratch.
- **Character View** – load an existing character to view and manage it: track HP/MP/IP and statuses, equip and swap items, level up, learn spells and heroic skills, and more.

Supported classes, including their special abilities (e.g. Arcanist's Arcana, Tinkerer's Inventions, Wayfarer's Companion):

Core classes:
- Arcanist
- Chimerist
- Dark Blade
- Elementalist
- Entropist
- Fury
- Guardian
- Loremaster
- Orator
- Rogue
- Sharpshooter
- Spiritist
- Tinkerer
- Wayfarer
- Weaponmaster

Also supported, from supplement books:
- Dancer (High Fantasy)
- Mutant (Techno Fantasy)

Partial Russian translation (thanks to [Katayando](https://github.com/Katayando)).

## Requirements:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) – Python package and project manager

## Run the app
Run the app with `uv` (this also creates the virtual environment and installs dependencies on first run):
```shell
uv run -m streamlit -- run fabula_charsheet/main.py
```

The app window will open in your default browser.

## Saved data

Characters are saved locally as YAML files under `fabula_charsheet/characters/` (excluded from version control via `.gitignore`).

## Contributing

Issues and pull requests are welcome.

### Adding or improving a translation

UI text and game data descriptions are translated via YAML files under `fabula_charsheet/assets/locals/<lang>/`. English (`en`) is the fallback language — any key missing from another language falls back to the English text automatically.

- **To fill in missing Russian translations**: find the missing key in the corresponding YAML file under `assets/locals/en/` and add it with the same key and file path under `assets/locals/ru/`.
- **To add a new language**:
  1. Add the language code to `LangEnum` in `fabula_charsheet/data/models/language.py`.
  2. Create `fabula_charsheet/assets/locals/<lang>/`, mirroring the file structure of `assets/locals/en/`, and translate the keys.
- Keys are looked up by name, so a translated string must use the exact same key as its English counterpart — copying the English key and translating only the value is the safest approach.

## License

[MIT](LICENSE)

## Releases

See the [Releases page](https://github.com/lama-imp/fabula-charsheet/releases) for version history and changelogs.

