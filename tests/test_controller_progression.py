from data.models import (
    Accessory,
    CharClass,
    ClassName,
    HeroicSkill,
    HeroicSkillName,
    Quality,
    Skill,
    Spell,
)


# --- apply_levelup ---

def test_apply_levelup_increments_level_and_levels_up_existing_skill(controller):
    controller.character.level = 5
    skill = Skill(name="dodge", current_level=1, max_level=5)
    controller.character.classes = [CharClass(name=ClassName.rogue, skills=[skill])]
    controller.apply_levelup(skill, ClassName.rogue, None, [])
    assert controller.character.level == 6
    assert controller.character.classes[0].get_skill_level("dodge") == 2


def test_apply_levelup_adds_new_class(controller):
    controller.character.level = 5
    controller.character.classes = []
    new_class = CharClass(name=ClassName.guardian)
    skill = Skill(name="unrelated_skill")
    controller.apply_levelup(skill, ClassName.guardian, new_class, [])
    assert controller.character.level == 6
    assert controller.is_class_added(ClassName.guardian)


def test_apply_levelup_sets_spells_when_skill_grants_them(controller):
    controller.character.level = 5
    skill = Skill(name="elemental_magic", current_level=1, max_level=10, can_add_spell=True)
    controller.character.classes = [CharClass(name=ClassName.elementalist, skills=[skill])]
    spells = [Spell(name="fireball", mp_cost=10)]
    controller.apply_levelup(skill, ClassName.elementalist, None, spells)
    assert controller.character.spells[ClassName.elementalist] == spells


# --- can_add_heroic_skill ---

def test_can_add_heroic_skill_true_when_mastered_class_without_heroic_skill(controller):
    skill = Skill(name="s", current_level=10, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.guardian, skills=[skill])]
    assert controller.can_add_heroic_skill() is True


def test_can_add_heroic_skill_false_when_already_matched(controller):
    skill = Skill(name="s", current_level=10, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.guardian, skills=[skill])]
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.extra_hp)]
    assert controller.can_add_heroic_skill() is False


def test_can_add_heroic_skill_false_when_no_mastered_class(controller):
    skill = Skill(name="s", current_level=5, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.guardian, skills=[skill])]
    assert controller.can_add_heroic_skill() is False


# --- is_heroic_skill_available ---

def test_is_heroic_skill_available_already_owned_respects_repeatable_flag(controller):
    skill = HeroicSkill(name=HeroicSkillName.extra_hp, can_add_several_times=False)
    controller.character.heroic_skills = [skill]
    assert controller.is_heroic_skill_available(skill) is False

    repeatable = HeroicSkill(name=HeroicSkillName.extra_mp, can_add_several_times=True)
    controller.character.heroic_skills = [repeatable]
    assert controller.is_heroic_skill_available(repeatable) is True


def test_is_heroic_skill_available_heroic_companion_requires_companion(controller):
    skill = HeroicSkill(name=HeroicSkillName.heroic_companion)
    assert controller.is_heroic_skill_available(skill) is False


def test_is_heroic_skill_available_no_required_class_is_always_true(controller):
    skill = HeroicSkill(name=HeroicSkillName.comet)
    assert controller.is_heroic_skill_available(skill) is True


def test_is_heroic_skill_available_requires_mastered_class(controller):
    skill = HeroicSkill(name=HeroicSkillName.comet, required_class=[ClassName.entropist])
    assert controller.is_heroic_skill_available(skill) is False

    mastered = Skill(name="s", current_level=10, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.entropist, skills=[mastered])]
    assert controller.is_heroic_skill_available(skill) is True


def test_is_heroic_skill_available_requires_specific_skill_level(controller):
    required_skill = Skill(name="dodge")
    skill = HeroicSkill(
        name=HeroicSkillName.comet,
        required_class=[ClassName.rogue],
        required_skill=required_skill,
    )
    mastered = Skill(name="s", current_level=10, max_level=10)
    dodge_unlearned = Skill(name="dodge", current_level=0, max_level=5)
    controller.character.classes = [CharClass(name=ClassName.rogue, skills=[mastered, dodge_unlearned])]
    assert controller.is_heroic_skill_available(skill) is False

    dodge_learned = Skill(name="dodge", current_level=1, max_level=5)
    mastered_minus_dodge = Skill(name="s", current_level=9, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.rogue, skills=[mastered_minus_dodge, dodge_learned])]
    assert controller.is_heroic_skill_available(skill) is True


# --- can_add_class / can_increase_attribute / has_enough_skills ---

def test_can_add_class_allows_up_to_two_non_mastered_classes(controller):
    controller.character.classes = [CharClass(name=ClassName.rogue), CharClass(name=ClassName.guardian)]
    assert controller.can_add_class() is True
    controller.character.classes.append(CharClass(name=ClassName.fury))
    assert controller.can_add_class() is False


def test_can_increase_attribute_only_at_thresholds(controller):
    controller.character.level = 21
    assert controller.can_increase_attribute() is False

    controller.character.level = 20
    controller.character.dexterity.base = 8
    controller.character.might.base = 8
    controller.character.insight.base = 8
    controller.character.willpower.base = 8  # sum = 32 < 34
    assert controller.can_increase_attribute() is True

    controller.character.dexterity.base = 10  # sum = 34, not < 34
    assert controller.can_increase_attribute() is False


def test_has_enough_skills(controller):
    controller.character.level = 3
    controller.character.classes = []
    assert controller.has_enough_skills() is False

    skill = Skill(name="s", current_level=3, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.guardian, skills=[skill])]
    assert controller.has_enough_skills() is True


def test_can_add_skill_number(controller):
    controller.character.level = 5
    skill = Skill(name="s", current_level=2, max_level=10)
    controller.character.classes = [CharClass(name=ClassName.guardian, skills=[skill])]
    assert controller.can_add_skill_number() == 3


# --- add_heroic_skill / apply_heroic_skill_effect ---

def test_add_heroic_skill_comet_grants_entropist_spell(controller):
    controller.add_heroic_skill(HeroicSkill(name=HeroicSkillName.comet))
    spells = controller.character.spells[ClassName.entropist]
    assert any(s.name == "comet" for s in spells)


def test_add_heroic_skill_hope_grants_spiritist_spell(controller):
    controller.add_heroic_skill(HeroicSkill(name=HeroicSkillName.hope))
    spells = controller.character.spells[ClassName.spiritist]
    assert any(s.name == "hope" for s in spells)


def test_add_heroic_skill_volcano_grants_elementalist_spell(controller):
    controller.add_heroic_skill(HeroicSkill(name=HeroicSkillName.volcano))
    spells = controller.character.spells[ClassName.elementalist]
    assert any(s.name == "volcano" for s in spells)


def test_add_heroic_skill_without_spell_effect_is_a_no_op(controller):
    controller.add_heroic_skill(HeroicSkill(name=HeroicSkillName.deep_pockets))
    assert controller.character.heroic_skills[-1].name == HeroicSkillName.deep_pockets
    assert controller.character.spells == {}


# --- apply_quality_effects ---

def test_apply_quality_effects_amulet(controller):
    item = Accessory(name="ring")
    controller.apply_quality_effects(item, Quality(name="amulet"))
    assert item.bonus_magic_defense == 1
    assert item.bonus_defense == 0


def test_apply_quality_effects_bulwark(controller):
    item = Accessory(name="ring")
    controller.apply_quality_effects(item, Quality(name="bulwark"))
    assert item.bonus_defense == 1


def test_apply_quality_effects_omnishield(controller):
    item = Accessory(name="ring")
    controller.apply_quality_effects(item, Quality(name="omnishield"))
    assert item.bonus_defense == 1
    assert item.bonus_magic_defense == 1


def test_apply_quality_effects_initiative_up(controller):
    item = Accessory(name="ring")
    controller.apply_quality_effects(item, Quality(name="initiative_up"))
    assert item.bonus_initiative == 4


def test_apply_quality_effects_unknown_quality_is_a_no_op(controller):
    item = Accessory(name="ring")
    controller.apply_quality_effects(item, Quality(name="not_a_real_quality"))
    assert item.bonus_defense == 0
    assert item.bonus_magic_defense == 0
    assert item.bonus_initiative == 0
