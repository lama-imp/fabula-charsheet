from pathlib import Path

import yaml
import streamlit as st

from data.models import LangEnum


class Localizator:
    default_language = LangEnum.en

    def __init__(self, translations: dict[LangEnum, dict[str, str]]):
        self.__translations = translations

    def get(self, lang: LangEnum):
        return self.__translations.get(lang, self.default_language)


def init_localizator(locals_directory: Path):
    if st.session_state.get("localizator"):
        return

    translations = dict()

    for lang in LangEnum:
        yaml_path = Path(locals_directory, f"{lang}.yaml").resolve(strict=True)
        with yaml_path.open(encoding='utf8') as f:
            raw_yaml = yaml.load(f, Loader=yaml.Loader)
        translations[lang] = raw_yaml

    st.session_state.localizator = Localizator(translations)


def select_local():
    with st.sidebar:
        selected_language = st.selectbox(
            "Select Language",
            options=list(LangEnum),
            format_func=lambda lang: lang.value.upper(),
            index=list(LangEnum).index(st.session_state.get("selected_language", LangEnum.en)),
            label_visibility="hidden",
        )

        st.session_state["selected_language"] = selected_language
