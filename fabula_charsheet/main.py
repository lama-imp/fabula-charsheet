import streamlit as st

from pages import pages
from data.compendium import init as init_compendium
from data.saved_characters import init as init_saved_characters
from config import ASSETS_DIRECTORY, SAVED_CHARS_DIRECTORY


def main():
    init_compendium(ASSETS_DIRECTORY)
    init_saved_characters(SAVED_CHARS_DIRECTORY)

    st.set_page_config(page_title="Fabula Ultima", page_icon=":material/person_play:")
    pg = st.navigation([st.Page(**p) for p in pages], position="top")

    pg.run()


if __name__ == "__main__":
    main()
