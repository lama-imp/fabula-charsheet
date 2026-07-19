import math

from data.models import AttributeName, Accessory, Armor, CharClass, ClassName, Skill, Therioform


def test_defense_no_armor_uses_dexterity(controller):
    controller.character.dexterity.current = 9
    assert controller.defense() == 9


def test_defense_sums_equipped_item_bonuses(controller):
    controller.character.dexterity.current = 9
    controller.character.inventory.equipped.accessory = Accessory(name="ring", bonus_defense=2)
    assert controller.defense() == 11


def test_defense_armor_with_flat_int_defense(controller):
    controller.character.dexterity.current = 9
    controller.character.inventory.equipped.armor = Armor(name="plate", defense=10, bonus_defense=1)
    assert controller.defense() == 10 + 1


def test_defense_armor_with_attribute_based_defense(controller):
    controller.character.dexterity.current = 11
    controller.character.inventory.equipped.armor = Armor(name="robe", defense=AttributeName.dexterity)
    assert controller.defense() == 11


def test_defense_rogue_dodge_bonus(controller):
    controller.character.dexterity.current = 8
    controller.character.classes = [
        CharClass(name=ClassName.rogue, skills=[Skill(name="dodge", current_level=3, max_level=5)])
    ]
    assert controller.defense() == 8 + 3


def test_defense_placophora_overrides_when_higher(controller):
    controller.character.dexterity.current = 8
    controller.character.classes = [
        CharClass(name=ClassName.mutant, skills=[Skill(name="theriomorphosis", current_level=4, max_level=10)])
    ]
    controller.state.active_therioforms = [Therioform(name="placophora")]
    expected = 13 + math.floor(4 / 2)
    assert controller.defense() == expected


def test_defense_placophora_does_not_lower_higher_defense(controller):
    controller.character.dexterity.current = 8
    controller.character.inventory.equipped.armor = Armor(name="plate", defense=20)
    controller.character.classes = [
        CharClass(name=ClassName.mutant, skills=[Skill(name="theriomorphosis", current_level=4, max_level=10)])
    ]
    controller.state.active_therioforms = [Therioform(name="placophora")]
    assert controller.defense() == 20


def test_magic_defense_uses_insight_and_item_bonuses(controller):
    controller.character.insight.current = 7
    controller.character.inventory.equipped.accessory = Accessory(name="amulet", bonus_magic_defense=3)
    assert controller.magic_defense() == 10


def test_initiative_with_no_bonus(controller, loc):
    controller.character.insight.current = 8
    controller.character.dexterity.current = 9
    assert controller.initiative() == "d8 + d9"


def test_initiative_with_positive_bonus(controller):
    controller.character.insight.current = 8
    controller.character.dexterity.current = 9
    controller.character.inventory.equipped.accessory = Accessory(name="boots", bonus_initiative=4)
    assert controller.initiative() == "d8 + d9 +4"


def test_initiative_with_negative_bonus(controller):
    controller.character.insight.current = 8
    controller.character.dexterity.current = 9
    controller.character.inventory.equipped.main_hand = None
    controller.character.inventory.equipped.accessory = Accessory(name="cursed_ring", bonus_initiative=-3)
    assert controller.initiative() == "d8 + d9 -3"
