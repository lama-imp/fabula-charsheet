from data.models import CharClass, HeroicSkill, HeroicSkillName


def test_max_hp_base_formula(controller):
    controller.character.level = 5
    controller.character.might.base = 8
    assert controller.max_hp() == 5 + 8 * 5


def test_max_hp_includes_class_bonuses(controller):
    controller.character.level = 5
    controller.character.might.base = 8
    controller.character.classes = [
        CharClass(class_bonus="hp", bonus_value=5),
        CharClass(class_bonus="hp", bonus_value=3),
        CharClass(class_bonus="mp", bonus_value=100),  # should not count towards HP
    ]
    assert controller.max_hp() == 5 + 8 * 5 + 5 + 3


def test_max_hp_extra_hp_heroic_skill_below_level_40(controller):
    controller.character.level = 10
    controller.character.might.base = 8
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.extra_hp)]
    assert controller.max_hp() == 10 + 8 * 5 + 10


def test_max_hp_extra_hp_heroic_skill_at_level_40(controller):
    controller.character.level = 40
    controller.character.might.base = 8
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.extra_hp)]
    assert controller.max_hp() == 40 + 8 * 5 + 20


def test_max_mp_base_formula_and_bonuses(controller):
    controller.character.level = 5
    controller.character.willpower.base = 9
    controller.character.classes = [CharClass(class_bonus="mp", bonus_value=4)]
    assert controller.max_mp() == 5 + 9 * 5 + 4


def test_max_mp_extra_mp_heroic_skill(controller):
    controller.character.level = 40
    controller.character.willpower.base = 8
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.extra_mp)]
    assert controller.max_mp() == 40 + 8 * 5 + 20


def test_max_ip_base_and_bonuses(controller):
    controller.character.classes = [CharClass(class_bonus="ip", bonus_value=2)]
    assert controller.max_ip() == 6 + 2


def test_max_ip_extra_ip_heroic_skill(controller):
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.extra_ip)]
    assert controller.max_ip() == 6 + 4


def test_current_pools_subtract_state_deltas(controller):
    controller.character.level = 5
    controller.character.might.base = 8
    controller.character.willpower.base = 8
    controller.state.minus_hp = 10
    controller.state.minus_mp = 5
    controller.state.minus_ip = 1
    assert controller.current_hp() == controller.max_hp() - 10
    assert controller.current_mp() == controller.max_mp() - 5
    assert controller.current_ip() == controller.max_ip() - 1


def test_crisis_value_is_floor_half_max_hp(controller):
    controller.character.level = 5
    controller.character.might.base = 8
    assert controller.max_hp() == 45
    assert controller.crisis_value() == 22
