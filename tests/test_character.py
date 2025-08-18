import pytest
import json

from fabula_charsheet.data.models import Character, HeroicSkill, HeroicSkillName
from fabula_charsheet.data.models.character import InvalidCharacterField
from fabula_charsheet.data import compendium
from fabula_charsheet.data.localizator import init_localizator
from fabula_charsheet.data.models import LangEnum


def _setup_loc(streamlit_stub, tmp_path):
    en_dir = tmp_path / 'en'
    en_dir.mkdir()
    content = {
        "error_name_empty": "Name should not be empty.",
        "error_invalid_level": "Level {level} should be between 1 and 60.",
        "error_identity_empty": "Identity should not be empty.",
        "error_theme_empty": "Theme should not be empty.",
        "error_origin_empty": "Origin should not be empty."
    }
    (en_dir / 'base.yaml').write_text(json.dumps(content))
    ru_dir = tmp_path / 'ru'
    ru_dir.mkdir()
    (ru_dir / 'base.yaml').write_text('{}')
    init_localizator(tmp_path)
    return streamlit_stub.session_state['localizator'].get(LangEnum.en)


def test_character_field_validations(streamlit_stub, tmp_path):
    loc = _setup_loc(streamlit_stub, tmp_path)
    char = Character()
    char.set_level(10, loc)
    assert char.level == 10
    with pytest.raises(InvalidCharacterField):
        char.set_level(0, loc)
    with pytest.raises(InvalidCharacterField):
        char.set_identity('', loc)
    char.set_identity('Hero', loc)
    with pytest.raises(InvalidCharacterField):
        char.set_name('', loc)
    char.set_name('Alice', loc)
    with pytest.raises(InvalidCharacterField):
        char.set_theme('', loc)
    char.set_theme('Hope', loc)
    with pytest.raises(InvalidCharacterField):
        char.set_origin('', loc)
    char.set_origin('Village', loc)


def test_character_utility_methods(assets_dir, streamlit_stub, tmp_path):
    loc = _setup_loc(streamlit_stub, tmp_path)
    compendium.COMPENDIUM = None
    compendium.init(assets_dir)
    c = compendium.COMPENDIUM
    from fabula_charsheet.data.models.skill import Skill
    for cls in c.classes.classes:
        cls.skills = [Skill(**s) if isinstance(s, dict) else s for s in cls.skills]
    char = Character()
    arcanist = c.classes.get_class('arcanist')
    arcanist.skills[0].current_level = 1
    arcanist.skills[1].current_level = 2
    char.classes = [arcanist]
    assert char.get_n_skill() == 3
    assert char.get_class('arcanist') is arcanist
    assert char.get_class(None) is None
    spells = c.spells.get_spells('elementalist')
    char.spells = {'elementalist': spells}
    assert char.get_spells_by_class('elementalist') == spells
    assert char.get_spells_by_class(None) == []
    spiritist_spells = c.spells.get_spells('spiritist')
    char.spells['spiritist'] = spiritist_spells
    assert len(char.get_all_spells()) == len(spells) + len(spiritist_spells)
    hs = HeroicSkill(name='deep_pockets')
    char.heroic_skills = [hs]
    assert char.has_heroic_skill(HeroicSkillName.deep_pockets)
    char.heroic_skills = []
    assert not char.has_heroic_skill(HeroicSkillName.deep_pockets)
