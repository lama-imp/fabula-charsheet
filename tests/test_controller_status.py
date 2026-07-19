import pytest

from data.models import AttributeName, Status, Therioform


@pytest.mark.parametrize("status,attribute,expected", [
    (Status.dazed, "insight", 6),
    (Status.enraged, "insight", 6),
    (Status.enraged, "dexterity", 6),
    (Status.poisoned, "might", 6),
    (Status.poisoned, "willpower", 6),
    (Status.shaken, "willpower", 6),
    (Status.slow, "dexterity", 6),
    (Status.weak, "might", 6),
])
def test_apply_status_single_status_modifier(controller, status, attribute, expected):
    controller.state.statuses = [status]
    controller.apply_status()
    assert getattr(controller.character, attribute).current == expected


def test_apply_status_improved_attribute_adds_bonus(controller):
    controller.state.improved_attributes = [AttributeName.might]
    controller.apply_status()
    assert controller.character.might.current == 10


@pytest.mark.parametrize("therioform_name,attribute", [
    ("arpaktida", "insight"),
    ("dynamotheria", "might"),
    ("tachytheria", "dexterity"),
])
def test_apply_status_active_therioform_bonus(controller, therioform_name, attribute):
    controller.state.active_therioforms = [Therioform(name=therioform_name)]
    controller.apply_status()
    assert getattr(controller.character, attribute).current == 10


def test_apply_status_clamps_at_minimum(controller):
    controller.state.statuses = [Status.enraged, Status.slow]  # dexterity -2 twice
    controller.apply_status()
    assert controller.character.dexterity.current == 6


def test_apply_status_clamps_at_maximum(controller):
    controller.character.might.base = 12
    controller.state.improved_attributes = [AttributeName.might]
    controller.apply_status()
    assert controller.character.might.current == 12


def test_apply_status_with_nothing_active_resets_to_base(controller):
    controller.character.willpower.base = 8
    controller.character.willpower.current = 2
    controller.apply_status()
    assert controller.character.willpower.current == 8
