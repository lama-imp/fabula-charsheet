# Fabula Ultima Interactive Character Sheet

## Requirements:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) – Python package and project manager


## Setup Environment

Create and activate a virtual environment using `uv`:
```shell
uv venv
```

## Run the app
Run the app with `uv`:
```shell
 uv run -m streamlit -- run fabula_charsheet/main.py
```

The app window will open in your default browser.

## Development

To add a new class:

1. Create a file named `<new_class_name>.yaml` in the [`classes`](fabula_charsheet/assets/classes) directory.  
   Use the structure defined in the [`CharClass`](fabula_charsheet/data/models/char_class.py) model. (See [example](fabula_charsheet/characters/test_char.yaml) for reference.)

2. Add the new class name to the `ClassName` enumeration in [`char_class.py`](fabula_charsheet/data/models/char_class.py).


