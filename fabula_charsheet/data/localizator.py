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

    translations = {}

    def load_translations_from_dir(lang_dir: Path) -> dict:
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
        return merged_translations

    # Load English first as fallback
    english_translations = load_translations_from_dir(
        Path(locals_directory, LangEnum.en).resolve(strict=True)
    )
    translations[LangEnum.en] = english_translations

    # Load other languages, fallback to English
    for lang in LangEnum:
        if lang == LangEnum.en:
            continue

        lang_dir = Path(locals_directory, lang).resolve(strict=True)
        if not lang_dir.is_dir():
            raise FileNotFoundError(f"Missing translations directory for {lang.value}")

        lang_translations = load_translations_from_dir(lang_dir)

        merged_with_fallback = {**english_translations, **lang_translations}

        translations[lang] = merged_with_fallback

    st.session_state.localizator = Localizator(translations)


def select_local():
    with st.sidebar:
        if "language" not in st.session_state:
            st.session_state.language = LangEnum.en

        with st.sidebar:
            st.selectbox(
                "Select Language",
                options=list(LangEnum),
                format_func=lambda lang: lang.value.upper(),
                index=list(LangEnum).index(st.session_state.language),
                label_visibility="hidden",
                key="language",
            )

        if "char_controller" in st.session_state:
            st.session_state.char_controller.loc = st.session_state.localizator.get(st.session_state.language)
