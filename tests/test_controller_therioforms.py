import math

from data.models import CharClass, ClassName, Skill, Therioform


def test_can_add_therioform_gated_by_theriomorphosis_skill_level(controller):
    controller.character.special.therioforms = [Therioform(name="a")]
    controller.character.classes = [
        CharClass(name=ClassName.mutant, skills=[Skill(name="theriomorphosis", current_level=1, max_level=10)])
    ]
    assert controller.can_add_therioform() is False  # already has 1, level allows 1

    controller.character.classes = [
        CharClass(name=ClassName.mutant, skills=[Skill(name="theriomorphosis", current_level=2, max_level=10)])
    ]
    assert controller.can_add_therioform() is True


def test_available_therioforms_for_theriomorphosis_returns_learned_ones(controller):
    learned = [Therioform(name="a"), Therioform(name="b")]
    controller.character.special.therioforms = learned
    assert controller.available_therioforms_for_skill("theriomorphosis") == learned


def test_available_therioforms_for_genoclepsis_returns_compendium_therioforms(controller, monkeypatch):
    import types
    fake_compendium = types.SimpleNamespace(therioforms=[Therioform(name="all_a"), Therioform(name="all_b")])
    monkeypatch.setattr("data.compendium.COMPENDIUM", fake_compendium)
    result = controller.available_therioforms_for_skill("genoclepsis")
    assert [t.name for t in result] == ["all_a", "all_b"]


def test_available_therioforms_unknown_skill_returns_empty(controller):
    assert controller.available_therioforms_for_skill("unrelated_skill") == []


def test_max_manifest_therioforms(controller):
    assert controller.max_manifest_therioforms("theriomorphosis") == 2

    controller.character.classes = [
        CharClass(name=ClassName.mutant, skills=[Skill(name="genoclepsis", current_level=3, max_level=10)])
    ]
    assert controller.max_manifest_therioforms("genoclepsis") == 3
    assert controller.max_manifest_therioforms("unrelated_skill") == 0


def test_can_manifest_therioform_requires_at_least_3_hp(controller):
    controller.character.level = 5
    controller.character.might.base = 8  # max_hp = 45
    controller.state.minus_hp = 44  # current_hp = 1
    assert controller.can_manifest_therioform() is False
    controller.state.minus_hp = 42  # current_hp = 3
    assert controller.can_manifest_therioform() is True


def test_apply_manifest_therioform_costs_a_third_of_current_hp(controller):
    controller.character.level = 5
    controller.character.might.base = 8  # max_hp = 45
    assert controller.current_hp() == 45
    therioforms = [Therioform(name="chosen")]
    controller.apply_manifest_therioform(therioforms)
    assert controller.state.minus_hp == math.floor(45 / 3)
    assert controller.state.active_therioforms == therioforms
