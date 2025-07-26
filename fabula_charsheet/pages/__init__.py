import logging
from functools import partial
from typing import Callable

import streamlit as st
from . import error
from .character_creation import character_creation
from .character_view import character_view


pages = []


for page in (
        character_view,
        character_creation,
):
    build_error = lambda: None

    if not hasattr(page, "build") or not isinstance(page.build, Callable):
        message = f"Page {page.__name__} does not specify 'build' function."
        logging.warning(message)
        st.error(message, icon="🚨")
        build_error = partial(error.build, message)

    if not hasattr(page, "title"):
        message = f"Page {page.__name__} does not specify 'title' variable. Defaulting title to '{page.__name__}'"
        st.warning(message, icon="⚠️")
        logging.warning(message)

    page_config = {
        'title': page.__name__,
        'icon': None,
        'url_path': page.__name__,
    }

    pages.append(
        {
            'page': getattr(page, 'build', build_error),
            **{key: getattr(page, key, default_value) for key, default_value in page_config.items()}
        }
    )
