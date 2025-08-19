from fabula_charsheet.data import compendium
from fabula_charsheet.data.models.skill import Skill


def _get_class(name, assets_dir):
    compendium.COMPENDIUM = None
    compendium.init(assets_dir)
    cls = compendium.COMPENDIUM.classes.get_class(name)
    cls.skills = [Skill(**s) if isinstance(s, dict) else s for s in cls.skills]
    return cls


def test_char_class_methods(assets_dir):
    elementalist = _get_class('elementalist', assets_dir)
    # class_level
    elementalist.skills[0].current_level = 2
    elementalist.skills[1].current_level = 1
    assert elementalist.class_level() == 3
    # get_skill and get_skill_level
    skill = elementalist.get_skill('cataclysm')
    assert skill is not None
    assert elementalist.get_skill('unknown') is None
    elementalist.levelup_skill('cataclysm')
    assert elementalist.get_skill_level('cataclysm') == skill.current_level
    # get_spell_skill
    spell_skill = elementalist.get_spell_skill()
    assert spell_skill is not None and spell_skill.can_add_spell
    # can_equip_list and can_equip_weapon for sharpshooter
    sharpshooter = _get_class('sharpshooter', assets_dir)
    assert set(sharpshooter.can_equip_list()) == {'martial_ranged', 'martial_shields'}
    assert sharpshooter.can_equip_weapon('ranged')
    assert not sharpshooter.can_equip_weapon('melee')
    # clear_skills
    elementalist.clear_skills()
    assert elementalist.skills == []
