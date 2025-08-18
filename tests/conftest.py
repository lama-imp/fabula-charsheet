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

# Stub streamlit module
class SessionState(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__

st_stub = types.SimpleNamespace(session_state=SessionState())
sys.modules.setdefault('streamlit', st_stub)

# Stub yaml module using json
yaml_stub = types.SimpleNamespace()

def _yaml_load(stream, Loader=None):
    return json.load(stream)

yaml_stub.load = _yaml_load
yaml_stub.SafeLoader = yaml_stub.UnsafeLoader = yaml_stub.Loader = object
sys.modules.setdefault('yaml', yaml_stub)

# Stub pydantic module
pydantic_stub = types.SimpleNamespace()

class BaseModel:
    def __init__(self, **data):
        for k, v in data.items():
            setattr(self, k, v)

def Field(*, default=None, default_factory=None):
    if default_factory is not None:
        return default_factory()
    return default

class RootModel(BaseModel):
    def __init__(self, root=None):
        super().__init__()
        self.root = root

    def __class_getitem__(cls, item):
        return cls

class ConfigDict(dict):
    pass

def conint(**kwargs):
    return int

pydantic_stub.BaseModel = BaseModel
pydantic_stub.Field = Field
pydantic_stub.RootModel = RootModel
pydantic_stub.ConfigDict = ConfigDict
pydantic_stub.conint = conint
sys.modules.setdefault('pydantic', pydantic_stub)

# Stub annotated_types
annotated_stub = types.SimpleNamespace(Len=lambda *args, **kwargs: None)
sys.modules.setdefault('annotated_types', annotated_stub)

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

    return tmp_path
