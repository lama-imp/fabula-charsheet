# Interactive Character Sheet

An unofficial character creation and management app, compatible with Fabula Ultima. Requires the Fabula Ultima Core Rulebook.

## How it works

The app has two pages:
- **Character Creation** – a step-by-step wizard (identity → classes → attributes → equipment → preview) for building a new character from scratch.
- **Character View** – load an existing character to view and manage it: track HP/MP/IP and statuses, equip and swap items, level up, learn spells and heroic skills, and more.

Supported classes, including their special abilities (e.g. Arcanist's Arcana, Tinkerer's Inventions, Wayfarer's Companion):

- All core classes
- Dancer (High Fantasy)
- Mutant (Techno Fantasy)

Partial Russian translation (thanks to [Katayando](https://github.com/Katayando)).

## Download and run (no installation)

Ready-to-run builds for Windows, macOS and Linux are attached to each release on the [Releases page](https://github.com/lama-imp/fabula-charsheet/releases). No Python or uv needed.

- **Windows**: unzip `charsheet-windows-x64.zip` and double-click `charsheet.exe` inside the folder. If SmartScreen warns about an unknown app, click *More info → Run anyway*.
- **macOS**: unzip `charsheet-macos-arm64.zip` (Apple Silicon) or `charsheet-macos-x64.zip` (Intel) and open `charsheet.app`. The first time, right-click the app and choose *Open* (the app isn't signed with an Apple developer certificate). To quit, right-click its Dock icon and choose *Quit*.
- **Linux**: extract `charsheet-linux-x64.tar.gz` and run `charsheet/charsheet`.

The app opens in your default browser. On Windows and Linux a console window stays open while the app runs; close it to quit.

Where characters are saved in the downloaded app:
- **Windows and Linux**: the `characters` folder next to the `charsheet` executable. Keep this folder when you update to a new version.
- **macOS**: `~/Documents/Interactive Character Sheet/characters`.

Set the `FABULA_CHARACTERS_DIR` environment variable to use a different folder.

## Run from source

### Requirements:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) – Python package and project manager

### Run the app
Run the app with `uv` (this also creates the virtual environment and installs dependencies on first run):
```shell
uv run -m streamlit -- run fabula_charsheet/main.py
```

The app window will open in your default browser.

## Saved data

When running from source, characters are saved locally as YAML files under `fabula_charsheet/characters/` (excluded from version control via `.gitignore`).

## Contributing

Issues and pull requests are welcome.

### Adding or improving a translation

UI text and game data descriptions are translated via YAML files under `fabula_charsheet/assets/locals/<lang>/`. English (`en`) is the fallback language — any key missing from another language falls back to the English text automatically.

- **To fill in missing Russian translations**: find the missing key in the corresponding YAML file under `assets/locals/en/` and add it with the same key and file path under `assets/locals/ru/`.
- **To add a new language**:
  1. Add the language code to `LangEnum` in `fabula_charsheet/data/models/language.py`.
  2. Create `fabula_charsheet/assets/locals/<lang>/`, mirroring the file structure of `assets/locals/en/`, and translate the keys.
- Keys are looked up by name, so a translated string must use the exact same key as its English counterpart — copying the English key and translating only the value is the safest approach.

### Building the executables

The [Build executables](.github/workflows/build-executables.yml) workflow builds the app with PyInstaller on Windows, macOS and Linux. Run it manually from the Actions tab, or push a `v*` tag to also attach the builds to that tag's release. To build locally for your own OS:
```shell
uv run --with pyinstaller pyinstaller packaging/fabula_charsheet.spec --noconfirm
```
The result is in `dist/`.

## Releases

See the [Releases page](https://github.com/lama-imp/fabula-charsheet/releases) for version history and changelogs.

## License and legal notice

Interactive Character Sheet is an independent production and is not affiliated with Need Games or Rooster Games. It is published under the [Fabula Ultima Third-Party Tabletop License 1.0](https://need.games/wp-content/uploads/2024/06/Fabula-Ultima-Third-Party-Tabletop-License-1.0.pdf). Fabula Ultima is © Need Games and Rooster Games. Requires the Fabula Ultima Core Rulebook.

The default character portrait (`fabula_charsheet/assets/images/default_avatar.png`) was generated with AI.

The app's source code is released under the [MIT License](LICENSE). The MIT License does not cover Fabula Ultima game content (rules text, names and other material), which remains © Need Games and Rooster Games.
