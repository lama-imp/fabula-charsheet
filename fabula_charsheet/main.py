import streamlit as st

from data.localizator import init_localizator, select_local

from data.compendium import init as init_compendium
from data.saved_characters import init as init_saved_characters
from config import ASSETS_DIRECTORY, SAVED_CHARS_DIRECTORY, LOCALS_DIRECTORY
from pages import build_pages


LICENSE_URL = "https://need.games/wp-content/uploads/2024/06/Fabula-Ultima-Third-Party-Tabletop-License-1.0.pdf"

# Notice required by the Fabula Ultima Third-Party Tabletop License 1.0 (section 6).
# Kept in English and not translated, so the wording always matches the license.
LEGAL_NOTICE = (
    "Interactive Character Sheet is an independent production by lama-imp "
    "and is not affiliated with Need Games or Rooster Games. "
    "It is published under the "
    f"[Fabula Ultima Third-Party Tabletop License 1.0]({LICENSE_URL}). "
    "Fabula Ultima is © Need Games and Rooster Games. "
    "Requires the Fabula Ultima Core Rulebook. "
    "The default character portraits were generated with AI."
)


def main():
    init_compendium(ASSETS_DIRECTORY)
    init_saved_characters(SAVED_CHARS_DIRECTORY)
    init_localizator(LOCALS_DIRECTORY)

    st.set_page_config(page_title="Interactive Character Sheet", page_icon=":material/person_play:")

    select_local()

    pages = build_pages()

    pg = st.navigation([st.Page(**p) for p in pages], position="top")

    pg.run()

    st.divider()
    st.caption(LEGAL_NOTICE)


if __name__ == "__main__":
    main()
