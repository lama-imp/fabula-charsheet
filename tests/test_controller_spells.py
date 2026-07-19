from data.models import CharClass, ClassName, HeroicSkill, HeroicSkillName, Skill, Spell


def test_add_spell_appends_and_dedups(controller):
    spell = Spell(name="fireball", mp_cost=10)
    controller.add_spell(spell, ClassName.elementalist)
    controller.add_spell(spell, ClassName.elementalist)
    assert controller.character.spells[ClassName.elementalist] == [spell]


def test_remove_spell_removes_if_present(controller):
    spell = Spell(name="fireball", mp_cost=10)
    controller.add_spell(spell, ClassName.elementalist)
    controller.remove_spell(spell, ClassName.elementalist)
    assert controller.character.spells[ClassName.elementalist] == []


def test_remove_spell_missing_is_a_no_op(controller):
    spell = Spell(name="fireball", mp_cost=10)
    controller.remove_spell(spell, ClassName.elementalist)  # should not raise
    assert controller.character.spells.get(ClassName.elementalist, []) == []


def test_can_add_spell_requires_class_and_casting_skill(controller):
    assert controller.can_add_spell(ClassName.elementalist) is False

    controller.character.classes = [CharClass(name=ClassName.elementalist, skills=[])]
    assert controller.can_add_spell(ClassName.elementalist) is False

    casting_skill = Skill(name="elemental_magic", current_level=2, max_level=10, can_add_spell=True)
    controller.character.classes = [CharClass(name=ClassName.elementalist, skills=[casting_skill])]
    assert controller.can_add_spell(ClassName.elementalist) is True

    controller.character.spells[ClassName.elementalist] = [
        Spell(name="a", mp_cost=5), Spell(name="b", mp_cost=5)
    ]
    assert controller.can_add_spell(ClassName.elementalist) is False


def test_chimerist_max_spells(controller):
    assert controller.chimerist_max_spells() == 2  # no spell_mimic skill: 0 + 2

    controller.character.classes = [
        CharClass(name=ClassName.chimerist, skills=[Skill(name="spell_mimic", current_level=3, max_level=10)])
    ]
    assert controller.chimerist_max_spells() == 5

    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.chimeric_mastery)]
    assert controller.chimerist_max_spells() == 7
