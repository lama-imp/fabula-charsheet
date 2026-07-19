import sys
import types
import json
from pathlib import Path
import pytest

# Ensure package root in path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PKG = ROOT / 'fabula_charsheet'
if str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

# Stub streamlit module (pages/controller.py and most model code never touch it;
# only data/localizator.py and UI code do, via st.session_state).
class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

st_stub = types.SimpleNamespace(session_state=SessionState())
sys.modules.setdefault('streamlit', st_stub)

# yaml, pydantic and annotated_types are used for real (not stubbed) so that
# model validation, per-instance default_factory behavior, and enum/type
# coercion match production exactly.

@pytest.fixture(scope='session')
def streamlit_stub():
    return st_stub

@pytest.fixture(autouse=True)
def clear_session_state(streamlit_stub):
    streamlit_stub.session_state.clear()
    yield
    streamlit_stub.session_state.clear()

@pytest.fixture
def assets_dir(tmp_path: Path) -> Path:
    # Build minimal assets structure as JSON
    equipment = tmp_path / 'equipment'
    equipment.mkdir()
    weapons = [
        {
            "name": "staff",
            "weapon_category": "arcane",
            "range": "melee",
            "accuracy": ["dexterity", "might"],
            "bonus_damage": 6,
        }
    ]
    (equipment / 'weapons.yaml').write_text(json.dumps(weapons))
    (equipment / 'armors.yaml').write_text('[]')
    (equipment / 'shields.yaml').write_text('[]')

    classes = tmp_path / 'classes'
    classes.mkdir()
    elementalist = {
        "name": "elementalist",
        "skills": [
            {"name": "cataclysm", "current_level": 0, "max_level": 3},
            {"name": "elemental_magic", "current_level": 0, "max_level": 10, "can_add_spell": True},
        ]
    }
    sharpshooter = {
        "name": "sharpshooter",
        "martial_ranged": True,
        "martial_shields": True,
        "skills": []
    }
    arcanist = {
        "name": "arcanist",
        "skills": [
            {"name": "arcane_circle", "current_level": 0, "max_level": 4},
            {"name": "arcane_regeneration", "current_level": 0, "max_level": 2}
        ]
    }
    (classes / 'elementalist.yaml').write_text(json.dumps(elementalist))
    (classes / 'sharpshooter.yaml').write_text(json.dumps(sharpshooter))
    (classes / 'arcanist.yaml').write_text(json.dumps(arcanist))

    spells = tmp_path / 'spells'
    spells.mkdir()
    (spells / 'elementalist.yaml').write_text(json.dumps([
        {"name": "aura", "is_offensive": False, "mp_cost": 5, "target": "one_creature", "duration": "scene"}
    ]))
    (spells / 'spiritist.yaml').write_text(json.dumps([
        {"name": "heal", "is_offensive": False, "mp_cost": 5, "target": "one_creature", "duration": "scene"}
    ]))

    skills_dir = tmp_path / 'skills'
    skills_dir.mkdir()
    (skills_dir / 'heroic_skills.yaml').write_text(json.dumps([
        {"name": "ambidextrous"}
    ]))

    special = tmp_path / 'special'
    special.mkdir()
    (special / 'dances.yaml').write_text('[]')
    (special / 'therioforms.yaml').write_text('[]')

    qualities = tmp_path / 'qualities'
    qualities.mkdir()

    return tmp_path


@pytest.fixture
def loc():
    from data.models import LocNamespace
    return LocNamespace(root={
        "dice_prefix": "d",
        "error_class_not_found": "Class {class_name} not found.",
        "error_unexpected_class_type": "Unexpected class type: {class_type}",
        "error_equipping_item": "Cannot equip this item.",
    })


@pytest.fixture
def controller(loc):
    from pages.controller import CharacterController
    return CharacterController(loc)
