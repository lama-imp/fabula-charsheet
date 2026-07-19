from data.models import HeroicSkill, HeroicSkillName


def setup_pools(controller, level=5, might=8, willpower=8):
    controller.character.level = level
    controller.character.might.base = might
    controller.character.willpower.base = willpower


def test_use_health_potion_restores_hp_and_costs_ip(controller):
    setup_pools(controller)
    controller.state.minus_hp = 40
    controller.use_health_potion()
    assert controller.state.minus_hp == 0  # max(0, 40 - 50)
    assert controller.state.minus_ip == 3


def test_use_health_potion_ip_cost_reduced_by_deep_pockets(controller):
    setup_pools(controller)
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.deep_pockets)]
    controller.state.minus_hp = 40
    controller.use_health_potion()
    assert controller.state.minus_ip == 2


def test_use_mana_potion_restores_mp_and_costs_ip(controller):
    setup_pools(controller)
    controller.state.minus_mp = 40
    controller.use_mana_potion()
    assert controller.state.minus_mp == 0
    assert controller.state.minus_ip == 3


def test_use_magic_tent_restores_hp_and_mp_fully(controller):
    setup_pools(controller)
    controller.state.minus_hp = 999
    controller.state.minus_mp = 999
    controller.use_magic_tent()
    assert controller.state.minus_hp == 0
    assert controller.state.minus_mp == 0
    assert controller.state.minus_ip == 4


def test_use_magic_tent_ip_cost_reduced_by_deep_pockets(controller):
    setup_pools(controller)
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.deep_pockets)]
    controller.use_magic_tent()
    assert controller.state.minus_ip == 3


def test_can_use_potion_gated_on_current_ip(controller):
    setup_pools(controller)  # max_ip = 6
    controller.state.minus_ip = 4  # current_ip = 2, cost 3
    assert controller.can_use_potion() is False
    controller.state.minus_ip = 3  # current_ip = 3, cost 3
    assert controller.can_use_potion() is True


def test_can_use_potion_with_deep_pockets_lower_cost(controller):
    setup_pools(controller)
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.deep_pockets)]
    controller.state.minus_ip = 4  # current_ip = 2, cost 2
    assert controller.can_use_potion() is True


def test_can_use_magic_tent_gated_on_current_ip(controller):
    setup_pools(controller)  # max_ip = 6
    controller.state.minus_ip = 3  # current_ip = 3, cost 4
    assert controller.can_use_magic_tent() is False
    controller.state.minus_ip = 2  # current_ip = 4, cost 4
    assert controller.can_use_magic_tent() is True
