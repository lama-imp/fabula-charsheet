from pathlib import Path

import streamlit as st

from pages import pages
from data.compendium import init as init_compendium
from data.saved_characters import init as init_saved_characters


SAVED_CHARS_DIRECTORY = Path(Path(__file__).parent, "characters").resolve(strict=True)

def main():
    init_compendium(Path(Path(__file__).parent, "assets").resolve(strict=True))
    init_saved_characters(SAVED_CHARS_DIRECTORY)
    st.set_page_config(page_title="Fabula Ultima", page_icon=":material/person_play:")
    pg = st.navigation([st.Page(**p) for p in pages], position="top")
    pg.run()


if __name__ == "__main__":
    main()
