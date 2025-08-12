import logging
from functools import partial
from typing import Callable

import streamlit as st
from . import error
from .character_creation import character_creation
from .character_view import character_view


PAGE_MODULES = (
    character_view,
    character_creation,
)

def build_pages():
    loc = st.session_state.localizator.get(st.session_state.language)
    pages = []

    for page in PAGE_MODULES:
        build_error = lambda: None

        if not hasattr(page, "build") or not isinstance(page.build, Callable):
            message = f"Page {page.__name__} does not specify 'build' function."
            logging.warning(message)
            st.error(message, icon="🚨")
            build_error = partial(error.build, message)

        # Determine title
        if hasattr(page, "title_key"):
            title = getattr(loc, page.title_key, page.__name__)
        elif hasattr(page, "title"):
            title = page.title
        else:
            message = (
                f"Page {page.__name__} does not specify 'title' or 'title_key'. "
                f"Defaulting title to '{page.__name__}'"
            )
            st.warning(message, icon="⚠️")
            logging.warning(message)
            title = page.__name__

        # Build config
        page_config = {
            "page": getattr(page, "build", build_error),
            "title": title,
            "icon": getattr(page, "icon", None),
            "url_path": getattr(page, "url_path", page.__name__),
        }
        pages.append(page_config)

    return pages
