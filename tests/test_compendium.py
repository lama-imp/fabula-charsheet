from fabula_charsheet.data import compendium


def test_compendium_initialization(assets_dir):
    compendium.COMPENDIUM = None
    compendium.init(assets_dir)
    assert compendium.COMPENDIUM is not None
    equipment = compendium.COMPENDIUM.equipment
    categories = equipment.weapons_by_categories()
    assert 'arcane' in categories
    assert all(w.weapon_category == 'arcane' for w in categories['arcane'])


def test_compendium_retrieval_methods(assets_dir):
    compendium.COMPENDIUM = None
    compendium.init(assets_dir)
    c = compendium.COMPENDIUM
    from fabula_charsheet.data.models.skill import Skill
    for cls in c.classes.classes:
        cls.skills = [Skill(**s) if isinstance(s, dict) else s for s in cls.skills]
    arcanist = c.classes.get_class('arcanist')
    assert arcanist is not None and arcanist.name == 'arcanist'
    assert c.classes.get_class('unknown') is None
    spells = c.spells.get_spells('elementalist')
    assert isinstance(spells, list) and spells
    assert c.spells.get_spells('unknown') == []
    heroic = c.heroic_skills.get_skill('ambidextrous')
    assert heroic is not None and heroic.name == 'ambidextrous'
    assert c.heroic_skills.get_skill('unknown') is None
    skill = arcanist.skills[0]
    assert c.get_class_name_from_skill(skill) == 'arcanist'
