from pathlib import Path

import yaml
import streamlit as st

from data.models import LangEnum, LocNamespace


class Localizator:
    default_language = LangEnum.en

    def __init__(self, translations: dict[LangEnum, dict[str, str]]):
        self.__translations = translations

    def get(self, lang: LangEnum):
        return LocNamespace(root=self.__translations.get(lang, {}))


def init_localizator(locals_directory: Path):
    if st.session_state.get("localizator"):
        return

    translations = dict()

    for lang in LangEnum:
        lang_dir = Path(locals_directory, lang).resolve(strict=True)

        if not lang_dir.is_dir():
            raise FileNotFoundError(f"Missing translations directory for {lang.value}")

        merged_translations = {}
        key_origins = {}

        for yaml_file in sorted(lang_dir.rglob("*.yaml")):
            with yaml_file.open(encoding="utf8") as f:
                data = yaml.load(f, Loader=yaml.SafeLoader) or {}
                if not isinstance(data, dict):
                    raise ValueError(f"Invalid YAML structure in {yaml_file}")

                for key, value in data.items():
                    if key in merged_translations:
                        raise ValueError(
                            f"Duplicate translation key '{key}' found in:\n"
                            f"  - {key_origins[key]}\n"
                            f"  - {yaml_file}"
                        )
                    merged_translations[key] = value
                    key_origins[key] = yaml_file

        translations[lang] = merged_translations

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

        st.session_state.language = selected_language
