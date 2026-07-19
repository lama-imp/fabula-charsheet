import math

from data.models import (
    AttributeName,
    CharClass,
    ClassName,
    Companion,
    CompanionSkill,
    CompanionSkillName,
    DamageType,
    HeroicSkill,
    HeroicSkillName,
    Skill,
    Species,
    Status,
)


def with_faithful_companion(controller, level, companion, heroic_skills=None):
    controller.character.classes = [
        CharClass(name=ClassName.wayfarer, skills=[Skill(name="faithful_companion", current_level=level, max_level=10)])
    ]
    controller.character.special.companion = companion
    if heroic_skills:
        controller.character.heroic_skills = heroic_skills


# --- companion_skill_level / max_hp / crisis / current_hp ---

def test_companion_skill_level_defaults_to_zero_without_skill(controller):
    assert controller.companion_skill_level() == 0


def test_companion_max_hp_base_formula(controller):
    controller.character.level = 10
    companion = Companion(might=5)
    with_faithful_companion(controller, level=3, companion=companion)
    expected = 3 * 5 + math.floor(10 / 2)
    assert controller.companion_max_hp() == expected


def test_companion_max_hp_improved_hit_points_and_heroic_bonus(controller):
    controller.character.level = 10
    companion = Companion(might=5, skills=[
        CompanionSkill(name=CompanionSkillName.improved_hit_points),
        CompanionSkill(name=CompanionSkillName.improved_hit_points),
    ])
    with_faithful_companion(
        controller, level=3, companion=companion,
        heroic_skills=[HeroicSkill(name=HeroicSkillName.heroic_companion)],
    )
    expected = 3 * 5 + math.floor(10 / 2) + 10 * 2 + 10
    assert controller.companion_max_hp() == expected


def test_companion_crisis_value_and_current_hp(controller):
    controller.character.level = 10
    companion = Companion(might=5)
    with_faithful_companion(controller, level=3, companion=companion)
    max_hp = controller.companion_max_hp()
    assert controller.companion_crisis_value() == math.floor(max_hp / 2)
    controller.state.companion_minus_hp = max_hp + 10
    assert controller.companion_current_hp() == 0  # clamped at 0


# --- defense / magic defense ---

def test_companion_defense_with_improved_defenses_defense_option(controller):
    companion = Companion(dexterity=9, skills=[
        CompanionSkill(name=CompanionSkillName.improved_defenses, defense_option="defense")
    ])
    controller.character.special.companion = companion
    assert controller.companion_defense() == 9 + 2
    assert controller.companion_magic_defense() == companion.insight + 1


def test_companion_defense_with_improved_defenses_magic_defense_option(controller):
    companion = Companion(dexterity=9, insight=7, skills=[
        CompanionSkill(name=CompanionSkillName.improved_defenses, defense_option="magic_defense")
    ])
    controller.character.special.companion = companion
    assert controller.companion_defense() == 9 + 1
    assert controller.companion_magic_defense() == 7 + 2


# --- check bonus / attack damage bonus ---

def test_companion_check_bonus_matches_skill_level(controller):
    with_faithful_companion(controller, level=4, companion=Companion())
    assert controller.companion_check_bonus() == 4


def test_companion_attack_damage_bonus_matches_attack_index(controller):
    companion = Companion(skills=[
        CompanionSkill(name=CompanionSkillName.improved_damage, attack_index=0),
        CompanionSkill(name=CompanionSkillName.improved_damage, attack_index=0),
        CompanionSkill(name=CompanionSkillName.improved_damage, attack_index=1),
    ])
    controller.character.special.companion = companion
    assert controller.companion_attack_damage_bonus(0) == 10
    assert controller.companion_attack_damage_bonus(1) == 5
    assert controller.companion_attack_damage_bonus(2) == 0


# --- resistances / immunities / absorptions / vulnerabilities ---

def test_companion_all_resistances_combines_innate_and_skill(controller):
    companion = Companion(species=Species.construct, skills=[
        CompanionSkill(name=CompanionSkillName.damage_resistance, damage_types=[DamageType.fire])
    ])
    controller.character.special.companion = companion
    resistances = controller.companion_all_resistances()
    assert DamageType.earth in resistances  # innate for construct
    assert DamageType.fire in resistances


def test_companion_all_immunities_combines_innate_and_skill(controller):
    companion = Companion(species=Species.construct, skills=[
        CompanionSkill(name=CompanionSkillName.damage_immunity, damage_types=[DamageType.ice])
    ])
    controller.character.special.companion = companion
    immunities = controller.companion_all_immunities()
    assert DamageType.poison in immunities  # innate for construct
    assert DamageType.ice in immunities


def test_companion_all_absorptions_only_from_skills(controller):
    companion = Companion(skills=[
        CompanionSkill(name=CompanionSkillName.damage_absorption, damage_types=[DamageType.dark]),
    ])
    controller.character.special.companion = companion
    assert controller.companion_all_absorptions() == [DamageType.dark]


def test_companion_all_vulnerabilities_from_species_choice(controller):
    companion = Companion(species=Species.plant, species_damage_choice=DamageType.fire)
    controller.character.special.companion = companion
    assert controller.companion_all_vulnerabilities() == [DamageType.fire]


def test_companion_all_status_immunities_combines_innate_and_skill(controller):
    companion = Companion(species=Species.plant, skills=[
        CompanionSkill(name=CompanionSkillName.status_effect_immunity, statuses=[Status.poisoned]),
    ])
    controller.character.special.companion = companion
    immunities = controller.companion_all_status_immunities()
    assert Status.dazed in immunities  # innate for plant
    assert Status.poisoned in immunities


# --- max skills / heroic companion attribute bonus ---

def test_companion_max_skills_by_species_and_heroic_bonus(controller):
    controller.character.level = 10
    companion = Companion(species=Species.beast)
    controller.character.special.companion = companion
    assert controller.companion_max_skills() == 4

    controller.character.heroic_skills = [HeroicSkill(name=HeroicSkillName.heroic_companion)]
    assert controller.companion_max_skills() == 5

    controller.character.level = 40
    assert controller.companion_max_skills() == 6


def test_companion_max_skills_without_companion_is_zero(controller):
    controller.character.special.companion = None
    assert controller.companion_max_skills() == 0


def test_apply_heroic_companion_attribute_increments_and_clamps(controller):
    companion = Companion(might=11)
    controller.character.special.companion = companion
    controller.apply_heroic_companion_attribute(AttributeName.might)
    assert companion.might == 12  # 11 + 2 clamped at MAX_ATTRIBUTE_VALUE


# --- set_companion / remove_companion / companion_flee ---

def test_set_companion_resets_companion_hp_state(controller):
    controller.state.companion_minus_hp = 20
    controller.set_companion(Companion(name="fido"))
    assert controller.character.special.companion.name == "fido"
    assert controller.state.companion_minus_hp == 0


def test_remove_companion_clears_companion_and_hp_state(controller):
    controller.set_companion(Companion(name="fido"))
    controller.state.companion_minus_hp = 5
    controller.remove_companion()
    assert controller.character.special.companion is None
    assert controller.state.companion_minus_hp == 0


def test_companion_flee_sets_hp_to_crisis_value(controller):
    controller.character.level = 10
    companion = Companion(might=5)
    with_faithful_companion(controller, level=3, companion=companion)
    controller.companion_flee()
    assert controller.state.companion_minus_hp == controller.companion_max_hp() - controller.companion_crisis_value()
