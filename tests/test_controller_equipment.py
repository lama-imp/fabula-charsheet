from data.models import (
    Accessory,
    Armor,
    CharClass,
    ClassName,
    GripType,
    HeroicSkill,
    HeroicSkillName,
    Shield,
    Skill,
    Weapon,
    WeaponRange,
)


def one_handed(name="sword", **kwargs):
    return Weapon(name=name, grip_type=GripType.one_handed, **kwargs)


def two_handed(name="greatsword", **kwargs):
    return Weapon(name=name, grip_type=GripType.two_handed, **kwargs)


# --- can_equip_martial ---

def test_can_equip_martial_non_martial_item_always_true(controller):
    assert controller.can_equip_martial(Weapon(name="dagger", martial=False)) is True


def test_can_equip_martial_weapon_requires_class_support(controller):
    weapon = Weapon(name="bow", martial=True, range=WeaponRange.ranged)
    assert controller.can_equip_martial(weapon) is False
    controller.character.classes = [CharClass(name=ClassName.sharpshooter, martial_ranged=True)]
    assert controller.can_equip_martial(weapon) is True


def test_can_equip_martial_armor_requires_class_support(controller):
    armor = Armor(name="plate", martial=True)
    assert controller.can_equip_martial(armor) is False
    controller.character.classes = [CharClass(name=ClassName.guardian, martial_armor=True)]
    assert controller.can_equip_martial(armor) is True


def test_can_equip_martial_shield_requires_class_support(controller):
    shield = Shield(name="tower_shield", martial=True)
    assert controller.can_equip_martial(shield) is False
    controller.character.classes = [CharClass(name=ClassName.guardian, martial_shields=True)]
    assert controller.can_equip_martial(shield) is True


# --- equip_item: armor / accessory ---

def test_equip_armor_replaces_current_armor(controller):
    controller.equip_item(Armor(name="robe"))
    controller.equip_item(Armor(name="plate"))
    assert controller.character.inventory.equipped.armor.name == "plate"


def test_equip_accessory_replaces_current_accessory(controller):
    controller.equip_item(Accessory(name="ring"))
    controller.equip_item(Accessory(name="amulet"))
    assert controller.character.inventory.equipped.accessory.name == "amulet"


# --- equip_item: weapons ---

def test_equip_two_handed_weapon_without_monkey_grip_clears_both_hands(controller):
    equipped = controller.character.inventory.equipped
    equipped.main_hand = one_handed("dagger")
    equipped.off_hand = one_handed("dagger2")
    controller.equip_item(two_handed("greatsword"))
    assert equipped.main_hand.name == "greatsword"
    assert equipped.off_hand is None


def test_equip_one_handed_weapon_into_empty_main_hand(controller):
    controller.equip_item(one_handed("sword"))
    assert controller.character.inventory.equipped.main_hand.name == "sword"


def test_equip_one_handed_weapon_dual_wields_into_off_hand(controller):
    controller.equip_item(one_handed("sword"))
    controller.equip_item(one_handed("dagger"))
    equipped = controller.character.inventory.equipped
    assert equipped.main_hand.name == "sword"
    assert equipped.off_hand.name == "dagger"


def test_equip_one_handed_weapon_replaces_main_hand_when_incompatible(controller):
    equipped = controller.character.inventory.equipped
    equipped.main_hand = two_handed("greatsword")
    controller.equip_item(one_handed("dagger"))
    assert equipped.main_hand.name == "dagger"
    assert equipped.off_hand is None


def test_equip_weapon_replaces_main_hand_when_both_hands_full(controller):
    equipped = controller.character.inventory.equipped
    equipped.main_hand = one_handed("sword")
    equipped.off_hand = one_handed("dagger")
    controller.equip_item(one_handed("axe"))
    assert equipped.main_hand.name == "axe"
    assert equipped.off_hand.name == "dagger"


def test_equip_two_handed_weapons_dual_wielded_with_monkey_grip(controller):
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.monkey_grip)]
    controller.equip_item(two_handed("greatsword_a"))
    controller.equip_item(two_handed("greatsword_b"))
    equipped = controller.character.inventory.equipped
    assert equipped.main_hand.name == "greatsword_a"
    assert equipped.off_hand.name == "greatsword_b"


# --- equip_item: shields ---

def test_equip_shield_normal_case_clears_two_handed_main_hand(controller):
    equipped = controller.character.inventory.equipped
    equipped.main_hand = two_handed("greatsword")
    controller.equip_item(Shield(name="buckler"))
    assert equipped.main_hand is None
    assert equipped.off_hand.name == "buckler"


def test_equip_shield_normal_case_keeps_one_handed_main_hand(controller):
    equipped = controller.character.inventory.equipped
    equipped.main_hand = one_handed("sword")
    controller.equip_item(Shield(name="buckler"))
    assert equipped.main_hand.name == "sword"
    assert equipped.off_hand.name == "buckler"


def test_equip_shield_with_monkey_grip_does_not_clear_main_hand(controller):
    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.monkey_grip)]
    equipped = controller.character.inventory.equipped
    equipped.main_hand = two_handed("greatsword")
    controller.equip_item(Shield(name="buckler"))
    assert equipped.main_hand.name == "greatsword"
    assert equipped.off_hand.name == "buckler"


def test_equip_shield_with_dual_shieldbearer_into_empty_off_hand(controller):
    controller.character.classes = [
        CharClass(name=ClassName.guardian, skills=[Skill(name="dual_shieldbearer", current_level=1, max_level=1)])
    ]
    controller.equip_item(Shield(name="buckler"))
    assert controller.character.inventory.equipped.off_hand.name == "buckler"


def test_equip_shield_with_dual_shieldbearer_merges_into_twin_shields(controller):
    controller.character.classes = [
        CharClass(name=ClassName.guardian, skills=[Skill(name="dual_shieldbearer", current_level=1, max_level=1)])
    ]
    equipped = controller.character.inventory.equipped
    equipped.off_hand = Shield(name="buckler", bonus_defense=1, bonus_magic_defense=1)
    controller.equip_item(Shield(name="tower_shield", cost=50, bonus_defense=2, bonus_magic_defense=3))
    assert equipped.main_hand.name == "twin_shields"
    assert equipped.main_hand.bonus_defense == 2
    assert equipped.main_hand.bonus_magic_defense == 3
    assert equipped.main_hand.bonus_damage == 5
    # the previously equipped shield is left untouched in the off hand
    assert equipped.off_hand.name == "buckler"


def test_equip_shield_with_dual_shieldbearer_replaces_non_shield_off_hand(controller):
    controller.character.classes = [
        CharClass(name=ClassName.guardian, skills=[Skill(name="dual_shieldbearer", current_level=1, max_level=1)])
    ]
    equipped = controller.character.inventory.equipped
    equipped.off_hand = one_handed("dagger")
    controller.equip_item(Shield(name="buckler"))
    assert equipped.off_hand.name == "buckler"


# --- unequip_item / equipped_items ---

def test_unequip_item_clears_valid_category(controller):
    controller.character.inventory.equipped.armor = Armor(name="plate")
    controller.unequip_item("armor")
    assert controller.character.inventory.equipped.armor is None


def test_unequip_item_ignores_unknown_category(controller):
    controller.character.inventory.equipped.armor = Armor(name="plate")
    controller.unequip_item("weapon")  # not a real Equipped field
    assert controller.character.inventory.equipped.armor is not None


def test_equipped_items_lists_only_non_none_slots(controller):
    equipped = controller.character.inventory.equipped
    equipped.main_hand = one_handed("sword")
    equipped.armor = Armor(name="plate")
    items = controller.equipped_items()
    assert {i.name for i in items} == {"sword", "plate"}


# --- remove_item ---

def test_remove_item_unequips_weapon_from_main_hand_and_removes_from_backpack(controller):
    weapon = one_handed("sword")
    controller.add_item(weapon)
    controller.equip_item(weapon)
    controller.remove_item(weapon)
    assert controller.character.inventory.equipped.main_hand is None
    assert weapon not in controller.character.inventory.backpack.weapons


def test_remove_item_unequips_shield_from_off_hand_and_removes_from_backpack(controller):
    shield = Shield(name="buckler")
    controller.add_item(shield)
    controller.equip_item(shield)
    controller.remove_item(shield)
    assert controller.character.inventory.equipped.off_hand is None
    assert shield not in controller.character.inventory.backpack.shields


def test_remove_item_unequips_armor_and_accessory(controller):
    armor = Armor(name="plate")
    accessory = Accessory(name="ring")
    controller.add_item(armor)
    controller.add_item(accessory)
    controller.equip_item(armor)
    controller.equip_item(accessory)
    controller.remove_item(armor)
    controller.remove_item(accessory)
    equipped = controller.character.inventory.equipped
    assert equipped.armor is None
    assert equipped.accessory is None


def test_remove_item_not_equipped_only_removes_from_backpack(controller):
    weapon = one_handed("spare_dagger")
    controller.add_item(weapon)
    controller.remove_item(weapon)
    assert weapon not in controller.character.inventory.backpack.weapons
