from pathlib import Path
import pytest

from fabula_charsheet.data.localizator import init_localizator
from fabula_charsheet.data.models import LangEnum


def test_init_localizator_loads_translations(streamlit_stub, tmp_path):
    en_dir = tmp_path / 'en'
    ru_dir = tmp_path / 'ru'
    en_dir.mkdir()
    ru_dir.mkdir()
    (en_dir / 'base.yaml').write_text('{"error_name_empty": "Name should not be empty.", "bond_explanation": "About Bonds"}')
    (ru_dir / 'base.yaml').write_text('{"error_name_empty": "Имя не должно быть пустым."}')
    init_localizator(tmp_path)
    localizator = streamlit_stub.session_state['localizator']
    en = localizator.get(LangEnum.en)
    ru = localizator.get(LangEnum.ru)
    assert en.error_name_empty == "Name should not be empty."
    assert ru.error_name_empty == "Имя не должно быть пустым."
    assert ru.bond_explanation == en.bond_explanation


def test_init_localizator_duplicate_keys(tmp_path, streamlit_stub):
    en_dir = tmp_path / 'en'
    ru_dir = tmp_path / 'ru'
    en_dir.mkdir()
    ru_dir.mkdir()
    (en_dir / 'a.yaml').write_text('{"key1": "value1"}')
    (en_dir / 'b.yaml').write_text('{"key1": "value2"}')
    (ru_dir / 'a.yaml').write_text('{"key1": "value1"}')
    with pytest.raises(ValueError):
        init_localizator(tmp_path)
