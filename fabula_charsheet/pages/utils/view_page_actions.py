from __future__ import annotations

import streamlit as st

from config import MAX_ATTRIBUTE_VALUE
from pages.controller import CharacterController, ClassController
from data.models import AttributeName, Weapon, GripType, WeaponCategory, \
    WeaponRange, ClassName, SpellTarget, Spell, SpellDuration, DamageType, Armor, Shield, Accessory, Item, \
    Skill, LocNamespace, HeroicSkill, Species, ChimeristSpell, Therioform, HeroicSkillName, Dance, Arcanum, Invention, \
    Status, Companion, CompanionAttack, CompanionSkill, CompanionSkillName, SPECIES_STARTING_SKILLS, \
    PLANT_VULNERABILITY_CHOICES
from .table_writer import SkillTableWriter, HeroicSkillTableWriter, SpellTableWriter, TherioformTableWriter, \
    DanceTableWriter, ArcanumTableWriter, InventionTableWriter
from .classes_page_actions import add_new_class
from .common import join_with_and
from data import compendium as c

COMPANION_ATTRIBUTE_ARRAYS = {
    "jack_of_all_trades": [8, 8, 8, 8],
    "standard": [10, 8, 8, 6],
    "specialized": [10, 10, 6, 6],
    "super_specialized": [12, 8, 6, 6],
}
COMPANION_ALLOWED_SPECIES = [Species.beast, Species.construct, Species.elemental, Species.plant]
COMPANION_SELECTABLE_DAMAGE_TYPES = [
    d for d in DamageType if d not in (DamageType.no_damage, DamageType.no_type)
]


def avatar_update(controller: CharacterController, loc: LocNamespace):
    uploaded_avatar = st.file_uploader(
        "avatar uploader", accept_multiple_files=False,
        type=["jpg", "jpeg", "png", "gif"],
        label_visibility="hidden"
    )
    if uploaded_avatar is not None:
        st.image(uploaded_avatar, width=100)
    if st.button(loc.use_avatar_button, disabled=not uploaded_avatar):
        controller.dump_avatar(uploaded_avatar)
        st.rerun()


def level_up(controller: CharacterController, loc: LocNamespace):
    st.session_state.selected_hero_skills = []
    st.session_state.class_spells = []

    sorted_classes = sorted(
        [char_class for char_class in controller.character.classes if char_class.class_level() < 10],
        key=lambda x: x.class_level(),
        reverse=True
    )

    writer = SkillTableWriter(loc)
    writer.columns = writer.level_up_columns

    for char_class in sorted_classes:
        st.markdown(f"#### {char_class.name.localized_name(loc)}")
        writer.write_in_columns([skill for skill in char_class.skills if skill.current_level < skill.max_level])

    class_controller = ClassController()
    if controller.can_add_class():
        add_new_class(controller, class_controller, loc, mode="addition")

    if st.session_state.selected_hero_skills:
        selected_skill: Skill = st.session_state.selected_hero_skills[0]

        if selected_skill.can_add_spell:
            class_name = c.COMPENDIUM.get_class_name_from_skill(selected_skill)
            class_spells = c.COMPENDIUM.spells.get_spells(class_name)

            class_spells = [spell for spell in class_spells if
                            spell not in controller.character.get_spells_by_class(class_name)]
            max_n_spells = 1

            with st.expander(loc.page_class_select_spells_expander):
                SpellTableWriter(loc).write_in_columns(class_spells)
            total_class_spells = len(st.session_state.class_spells)

            if total_class_spells != max_n_spells:
                st.error(loc.error_class_select_exact_spells.format(
                    max_n_spells=max_n_spells,
                    casting_skill=selected_skill.localized_name(loc)
                ))

    if st.button(loc.confirm_button, disabled=(len(st.session_state.selected_hero_skills) != 1)):
        selected_class_name = c.COMPENDIUM.get_class_name_from_skill(selected_skill)
        new_class = class_controller.char_class if not controller.is_class_added(selected_class_name) else None
        controller.apply_levelup(
            skill=selected_skill,
            class_name=selected_class_name,
            new_class=new_class,
            spells=list(st.session_state.class_spells),
        )
        st.rerun()


def add_spell(controller: CharacterController, class_name: ClassName, loc: LocNamespace):
    selected_spells = list()

    def single_spell_selector(spell: Spell, idx=None):
        if st.checkbox("add spell",
                       value=(spell in selected_spells),
                       label_visibility="hidden",
                       key=f"{spell.name}-toggle"
                       ):
            if spell not in selected_spells:
                selected_spells.append(spell)
        else:
            if spell in selected_spells:
                selected_spells.remove(spell)

    class_spells = c.COMPENDIUM.spells.get_spells(class_name)
    available_spells = [spell for spell in class_spells if spell not in controller.character.get_spells_by_class(class_name)]

    writer = SpellTableWriter(loc)
    writer.columns = writer.add_one_spell_columns(single_spell_selector)
    writer.write_in_columns(available_spells)

    if st.button(loc.add_spell_button, disabled=(len(selected_spells) != 1)):
        controller.add_spell(selected_spells[0], class_name)
        st.rerun()


def add_chimerist_spell(controller: CharacterController, loc: LocNamespace):

    input_dict = {
        "name": st.text_input(loc.page_view_spell_name),
        "description": st.text_input(loc.page_view_spell_description),
        "is_offensive": st.checkbox(label=loc.page_view_spell_offensive),
        "mp_cost": st.number_input(loc.page_view_spell_mp_cost, value=0, step=5),
        "target": st.pills(loc.page_view_spell_target, [t for t in SpellTarget], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "duration": st.pills(loc.page_view_spell_duration, [t for t in SpellDuration], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "damage_type": st.pills(loc.page_view_spell_damage_type, [t for t in DamageType], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "species": st.pills(loc.page_view_spell_species, [t for t in Species], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
        "char_class": ClassName.chimerist,
    }

    if st.button(loc.add_spell_button):
        try:
            new_spell = ChimeristSpell(
                **input_dict
            )
            controller.add_spell(new_spell, ClassName.chimerist)
            st.toast(loc.msg_spell_added.format(spell_name=input_dict['name']))
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning(loc.error_adding_spell, icon="🪬")


def remove_chimerist_spell(controller: CharacterController, loc: LocNamespace):
    chimerist_spells = controller.character.spells[ClassName.chimerist]
    for spell in chimerist_spells:
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(spell.localized_name(loc))
        with c2:
            if st.button(loc.remove_button, key=f"{spell.name}-remove"):
                controller.remove_spell(spell, ClassName.chimerist)
                st.rerun()


def add_item(controller: CharacterController, loc: LocNamespace):
    item_type = st.segmented_control(
        loc.page_view_item_type,
        [Weapon, Armor, Shield, Accessory, Item],
        format_func=lambda x: loc[f"item_{x.__name__.lower()}"],
        selection_mode="single"
    )

    if item_type:
        name = st.text_input(loc.page_view_item_name)
        item_dict = {
            "name": name.lower() if name else name,
            "cost": st.number_input(loc.page_view_item_cost, value=0, step=50),
            "quality": st.text_input(loc.page_view_item_quality, value=loc.item_no_quality),
         }
        input_dict = {}
        if item_type.__name__ == "Weapon":
            def accuracy_input():
                st.write(loc.page_view_item_accuracy_check)
                c1, c2 = st.columns(2)
                with c1:
                    accuracy1 = st.selectbox("accuracy_selector_1",
                                             [a for a in AttributeName],
                                             key="acc-1",
                                             label_visibility="hidden",
                                             format_func=lambda x: AttributeName.to_alias(x, loc))
                with c2:
                    accuracy2 = st.selectbox("accuracy_selector_2",
                                             [a for a in AttributeName],
                                             key="acc-2",
                                             label_visibility="hidden",
                                             format_func=lambda x: AttributeName.to_alias(x, loc))

                return [accuracy1, accuracy2]

            input_dict = {
                "martial": st.checkbox(label=loc.page_view_item_martial),
                "grip_type": st.pills(loc.page_view_item_grip, [t for t in GripType], format_func=lambda s: s.localized_name(loc), selection_mode="single"),
                "range": st.pills(loc.page_view_item_range, [t for t in WeaponRange], format_func=lambda s: s.localized_name(loc),
                                      selection_mode="single"),
                "weapon_category": st.pills(loc.page_view_item_category, [t for t in WeaponCategory], format_func=lambda s: s.localized_name(loc),
                                      selection_mode="single"),
                "damage_type": st.pills(loc.page_view_item_damage_type, [t for t in DamageType],
                                        format_func=lambda s: s.localized_name(loc), selection_mode="single"),
                "accuracy": accuracy_input(),
                "bonus_accuracy": st.number_input(loc.page_view_item_bonus_accuracy, value=0, step=1),
                "bonus_damage": st.number_input(loc.page_view_item_bonus_damage, value=0, step=1),
                "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
            }

        if item_type.__name__ == "Armor":
            def defense_input():
                def_type = st.pills(
                    loc.page_view_item_select_defense_type,
                    [loc.page_view_item_defense_type_dexterity_dice, loc.page_view_item_defense_type_flat]
                )
                if def_type == loc.page_view_item_defense_type_dexterity_dice:
                    return AttributeName.dexterity
                elif def_type == loc.page_view_item_defense_type_flat:
                    defense = st.number_input(loc.page_view_item_provide_defense_value, value=0, step=1)
                    return defense

            input_dict = {
                "martial": st.checkbox(label=loc.page_view_item_martial),
                "defense": defense_input(),
                "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
                "bonus_initiative": st.number_input(loc.page_view_item_bonus_initiative, value=0, step=1),
            }

        if item_type.__name__ == "Shield":
            input_dict = {
                "martial": st.checkbox(label=loc.page_view_item_martial),
                "bonus_defense": st.number_input(loc.page_view_item_bonus_defense, value=0, step=1),
                "bonus_magic_defense": st.number_input(loc.page_view_item_bonus_magic_defense, value=0, step=1),
                "bonus_initiative": st.number_input(loc.page_view_item_bonus_initiative, value=0, step=1),
            }

    if st.button(loc.page_view_add_item_button, disabled=(not item_type)):
        try:
            combined_dict = item_dict | input_dict
            new_item = item_type(
                **combined_dict
            )
            controller.add_item(new_item)
            st.toast(loc.page_view_added_item_to_equipment.format(name=combined_dict['name']))
            st.rerun()
        except Exception as e:
            st.error(e)
            st.warning(loc.page_view_error_adding_item, icon="🪨")


def remove_item(controller: CharacterController, loc: LocNamespace):
    all_items = controller.character.inventory.backpack.all_items()
    for i, item in enumerate(all_items):
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            st.write(f"{item.__class__.__name__} - {item.name.title()}")
        with c2:
            if st.button(loc.remove_button, key=f"{item.name}-{i}-remove"):
                controller.remove_item(item)
                st.rerun()


def unequip_item(controller, category: str):
    try:
        controller.unequip_item(category)
    except Exception as e:
        st.warning(e, icon="💢")


def add_heroic_skill(controller: CharacterController, loc: LocNamespace):
    st.session_state.selected_hero_skills = []

    st.write(loc.msg_add_heroic_skill)
    writer = HeroicSkillTableWriter(loc)
    sorted_skills = sorted(c.COMPENDIUM.heroic_skills.heroic_skills, key=lambda x: x.localized_name(loc))
    writer.write_in_columns([skill for skill in sorted_skills if controller.is_heroic_skill_available(skill)])

    if HeroicSkillName.extra_spells in [skill.name for skill in st.session_state.selected_hero_skills]:
        selected_class_name = st.pills(
            loc.page_view_select_class_for_extra_spells,
            [ClassName.elementalist, ClassName.entropist, ClassName.spiritist],
            format_func=lambda x: x.localized_name(loc)
        )
        if selected_class_name:
            selected_spells = list()

            def single_spell_selector(spell: Spell, idx=None):
                if st.checkbox("add spell",
                               value=(spell in selected_spells),
                               label_visibility="hidden",
                               key=f"{spell.name}-toggle"
                               ):
                    if spell not in selected_spells:
                        selected_spells.append(spell)
                else:
                    if spell in selected_spells:
                        selected_spells.remove(spell)

            class_spells = c.COMPENDIUM.spells.get_spells(selected_class_name)
            available_spells = [spell for spell in class_spells if
                                spell not in controller.character.get_spells_by_class(selected_class_name)]

            writer = SpellTableWriter(loc)
            writer.columns = writer.add_one_spell_columns(single_spell_selector)
            writer.write_in_columns(available_spells)

            if st.button(loc.confirm_button,
                         key="add-extra-spells-skill",
                         disabled=(len(st.session_state.selected_hero_skills) != 1)
                                  or (len(selected_spells) != 2)):
                controller.add_heroic_skill(st.session_state.selected_hero_skills[0])
                for spell in selected_spells:
                    controller.add_spell(spell, selected_class_name)
                st.rerun()

    elif HeroicSkillName.heroic_companion in [skill.name for skill in st.session_state.selected_hero_skills]:
        companion = controller.character.special.companion
        eligible_attributes = [a for a in AttributeName if getattr(companion, a.value) < MAX_ATTRIBUTE_VALUE]
        chosen_attribute = st.pills(
            loc.companion_heroic_attribute_choice,
            eligible_attributes,
            format_func=lambda a: f"{a.localized_name(loc)} ({loc.dice_prefix}{getattr(companion, a.value)})",
            key="heroic-companion-attribute",
        )
        if st.button(loc.confirm_button,
                     key="add-heroic-companion-skill",
                     disabled=(len(st.session_state.selected_hero_skills) != 1) or chosen_attribute is None):
            controller.add_heroic_skill(st.session_state.selected_hero_skills[0])
            controller.apply_heroic_companion_attribute(chosen_attribute)
            st.rerun()

    elif HeroicSkillName.revelation in [skill.name for skill in st.session_state.selected_hero_skills]:
        st.markdown(loc.page_view_revelation_intro)
        arcanum_name = st.text_input(loc.page_view_arcanum_name, key="revelation-arcanum-name")
        arcanum_domains = st.text_area(loc.column_domains, key="revelation-arcanum-domains")
        arcanum_merge = st.text_area(loc.arcana_merge, key="revelation-arcanum-merge")
        arcanum_dismiss = st.text_area(loc.arcana_dismiss, key="revelation-arcanum-dismiss")
        can_confirm = bool(arcanum_name) and bool(arcanum_domains) and bool(arcanum_merge) and bool(arcanum_dismiss)
        if st.button(loc.confirm_button,
                     key="add-revelation-skill",
                     disabled=(len(st.session_state.selected_hero_skills) != 1) or not can_confirm):
            controller.add_heroic_skill(st.session_state.selected_hero_skills[0])
            controller.character.special.arcana.append(Arcanum(
                name=arcanum_name,
                custom_domains=arcanum_domains,
                custom_merge=arcanum_merge,
                custom_dismiss=arcanum_dismiss,
            ))
            st.rerun()

    else:
        if st.button(loc.confirm_button,
                     key="add-heroic-skill",
                     disabled=(len(st.session_state.selected_hero_skills) != 1)):
            controller.add_heroic_skill(st.session_state.selected_hero_skills[0])
            st.rerun()



def increase_attribute(controller: CharacterController, loc: LocNamespace):
    st.markdown(loc.msg_increase_attribute)
    attributes = [
        controller.character.dexterity,
        controller.character.might,
        controller.character.insight,
        controller.character.willpower,
    ]

    for attribute in attributes:
        if attribute.base < 12:
            with st.container():
                col1, col2, col3 = st.columns([0.2, 0.5, 0.3])
                with col2:
                    s = f"**{attribute.name.localized_name(loc)}**: {loc.dice_prefix}{attribute.base} :material/keyboard_double_arrow_right: {loc.dice_prefix}{attribute.base + 2}"
                    st.markdown(s)
                with col3:
                    if st.button(
                            ":material/add_task:",
                            key=attribute.name,
                    ):
                        attribute.base += 2
                        st.rerun()


def add_therioform(controller: CharacterController, loc: LocNamespace):
    selected_therioform = list()
    def single_selector(therioform: Therioform, idx=None):
        if st.checkbox("add therioform",
                       value=(therioform in selected_therioform),
                       label_visibility="hidden",
                       key=f"{therioform.name}-toggle"
                       ):
            if therioform not in selected_therioform:
                selected_therioform.append(therioform)
        else:
            if therioform in selected_therioform:
                selected_therioform.remove(therioform)

    sorted_therioforms = sorted(c.COMPENDIUM.therioforms, key=lambda x: x.localized_name(loc))
    available_therioforms = [t for t in sorted_therioforms if t not in controller.character.special.therioforms]

    writer = TherioformTableWriter(loc)
    writer.columns = writer.add_one_therioform_columns(single_selector)
    writer.write_in_columns(available_therioforms, description=False)

    if st.button(loc.add_therioform_button, key="add-new-therioform", disabled=(len(selected_therioform) != 1)):
        therioform = selected_therioform[0]
        controller.character.special.therioforms.append(therioform)
        st.rerun()


def add_dance(controller: CharacterController, loc: LocNamespace):
    selected_dance = list()
    def single_selector(dance: Dance, idx=None):
        if st.checkbox("add dance",
                       value=(dance in selected_dance),
                       label_visibility="hidden",
                       key=f"{dance.name}-toggle"
                       ):
            if dance not in selected_dance:
                selected_dance.append(dance)
        else:
            if dance in selected_dance:
                selected_dance.remove(dance)

    sorted_dances = sorted(c.COMPENDIUM.dances, key=lambda x: x.localized_name(loc))
    available_dances = [t for t in sorted_dances if t not in controller.character.special.dances]

    writer = DanceTableWriter(loc)
    writer.columns = writer.add_one_dance_columns(single_selector)
    writer.write_in_columns(available_dances, description=False)

    if st.button(loc.add_spell_button, disabled=(len(selected_dance) != 1)):
        dance = selected_dance[0]
        controller.character.special.dances.append(dance)
        st.rerun()

def add_invention(controller: CharacterController, loc: LocNamespace):
    selected_invention = list()
    def single_selector(invention: Invention, idx=None):
        if st.checkbox("add invention",
                       value=(invention in selected_invention),
                       label_visibility="hidden",
                       key=f"{invention.name}-toggle"
                       ):
            if invention not in selected_invention:
                selected_invention.append(invention)
        else:
            if invention in selected_invention:
                selected_invention.remove(invention)

    sorted_inventions = sorted(c.COMPENDIUM.inventions, key=lambda x: x.localized_name(loc))
    available_inventions = [i for i in sorted_inventions if i not in controller.character.special.inventions]

    writer = InventionTableWriter(loc)
    writer.columns = writer.add_one_invention_columns(single_selector)
    writer.write_in_columns(available_inventions, description=False)

    if st.button(loc.add_invention_button, disabled=(len(selected_invention) != 1), key="add_invention"):
        invention = selected_invention[0]
        controller.character.special.inventions.append(invention)
        st.rerun()


def manifest_therioform(controller: CharacterController, loc: LocNamespace):
    selected_therioforms = list()
    can_manifest_number = 0
    def selector(therioform: Therioform, idx=None):
        if st.checkbox("add therioform",
                       value=(therioform in selected_therioforms),
                       label_visibility="hidden",
                       key=f"{therioform.name}-toggle"
                       ):
            if therioform not in selected_therioforms:
                selected_therioforms.append(therioform)
        else:
            if therioform in selected_therioforms:
                selected_therioforms.remove(therioform)

    st.markdown(loc.page_view_manifest_therioform_selection)
    key = "skill_{skill_name}"
    skill = st.pills(
        "therioform selection",
        ["theriomorphosis", "genoclepsis"],
        format_func=lambda x: getattr(loc, key.format(skill_name=x), x),
        label_visibility="hidden"
    )
    available_therioforms = sorted(
        controller.available_therioforms_for_skill(skill or ""),
        key=lambda x: x.localized_name(loc),
    )

    if skill:
        can_manifest_number = controller.max_manifest_therioforms(skill)
        writer = TherioformTableWriter(loc)
        writer.columns = writer.add_one_therioform_columns(selector)
        writer.write_in_columns(available_therioforms, description=False)
        too_many = (len(selected_therioforms) > can_manifest_number)
        too_low_hp = not controller.can_manifest_therioform()
        if too_many:
            st.warning(loc.warn_therioform_number_warning.format(
                number=can_manifest_number,
                skill=loc[f"skill_{skill}"],
            ), icon="🫰")
        if too_low_hp:
            st.warning(loc.warn_therioform_health_warning, icon="🤏")

        if st.button(loc.confirm_button, key="confirm-therioform", disabled=too_many or too_low_hp):
            controller.apply_manifest_therioform(selected_therioforms)
            st.rerun()


def display_equipped_item(controller: CharacterController,
                          item: Item,
                          category: str,
                          loc: LocNamespace):
    if not item:
        return

    if isinstance(item, Weapon):
        icon = "⚔️"
    elif isinstance(item, Shield):
        icon = "🛡️"
    elif isinstance(item, Armor):
        icon = "🧥"
    else:
        icon = "💍"

    # Write header
    category_name = {
        "main_hand": loc.item_main_hand,
        "off_hand": loc.item_off_hand,
        "armor": loc.column_armor,
        "accessory": loc.column_accessory
    }.get(category, category)
    st.write(f"**{category_name}**")

    # Columns setup
    c1, c2, c3, c4 = st.columns([0.3, 0.3, 0.3, 0.1]) if category != "accessory" else st.columns([0.3, 0.5, 0.1, 0.1])
    # c1, c2, c3 = cols[0], cols[1], cols[2]
    # c4 = cols[3] if len(cols) > 3 else None

    # Column 1: icon and name
    with c1:
        st.markdown(icon)
        st.write(item.localized_name(loc))

    # Column 2: accuracy/defense/magic defense
    with c2:
        if isinstance(item, Weapon):
            st.markdown(f"_{loc.column_accuracy}_")
            accuracy_str = " + ".join(f"{loc.dice_prefix}{getattr(controller.character, attr).current}" for attr in item.accuracy)
            if item.bonus_accuracy:
                accuracy_str += f" + {item.bonus_accuracy}"
            st.write(accuracy_str)
        elif isinstance(item, Armor):
            st.markdown(f"_{loc.column_defense}_")
            if isinstance(item.defense, AttributeName):
                bonus = f" + {item.bonus_defense}" if item.bonus_defense > 0 else ""
                st.write(f"{loc.dice_prefix}{getattr(controller.character, item.defense).current}{bonus}")
            else:
                st.write(str(item.defense))
        elif isinstance(item, Shield):
            st.markdown(f"_{loc.column_defense}_")
            st.write(item.bonus_defense)
        elif isinstance(item, Accessory):
            st.write(f"_{loc.column_quality}_")
            st.write(item.localized_quality(loc))

    # Column 3: damage/magic defense/initiative
    with c3:
        if isinstance(item, Weapon):
            st.markdown(f"_{loc.column_damage}_")
            st.markdown(f"{loc.hr} + {item.bonus_damage}\n\n{item.damage_type.localized_name(loc)}")
        elif isinstance(item, Armor):
            st.markdown(f"_{loc.column_magic_defense}_")
            if isinstance(item.magic_defense, AttributeName):
                bonus = f" + {item.bonus_magic_defense}" if item.bonus_magic_defense > 0 else ""
                st.write(f"{loc.dice_prefix}{getattr(controller.character, item.magic_defense).current}{bonus}")
            else:
                st.write(str(item.magic_defense))
        elif isinstance(item, Shield):
            st.markdown(f"_{loc.column_magic_defense}_")
            st.write(item.bonus_magic_defense)
        elif isinstance(item, Accessory):
            pass

    # Column 4: unequip button
    with c4:
        disabled = (isinstance(item, Weapon) and item.name == "unarmed_strike")
        if st.button("", icon=":material/arrow_downward:", key=f"{category}-unequip", help=loc.page_view_unequip_help, disabled=disabled):
            unequip_item(controller, category)
            st.rerun()

    # Footer line
    if isinstance(item, Weapon):
        st.write(" ◆ ".join([
            item.grip_type.localized_name(loc),
            item.range.localized_name(loc),
            item.localized_quality(loc),
        ]))
    elif isinstance(item, Armor):
        st.write(f"{item.localized_quality(loc)} ◆ {loc.column_initiative}: {item.bonus_initiative}")
    elif isinstance(item, Shield):
        st.write(f"{item.localized_quality(loc)} ◆ {loc.column_initiative}: {item.bonus_initiative}")


def add_arcanum(controller: CharacterController, loc: LocNamespace):
    selected_arcanum = list()
    def single_selector(arcanum: Arcanum, idx=None):
        if st.checkbox("add arcanum",
                       value=(arcanum in selected_arcanum),
                       label_visibility="hidden",
                       key=f"{arcanum.name}-toggle"
                       ):
            if arcanum not in selected_arcanum:
                selected_arcanum.append(arcanum)
        else:
            if arcanum in selected_arcanum:
                selected_arcanum.remove(arcanum)

    sorted_arcana = sorted(c.COMPENDIUM.arcana, key=lambda x: x.localized_name(loc))
    available_arcana = [t for t in sorted_arcana if t not in controller.character.special.arcana]

    writer = ArcanumTableWriter(loc)
    writer.columns = writer.add_one_dance_columns(single_selector)
    writer.write_in_columns(available_arcana)

    if st.button(loc.add_arcanum_button,
                 key="add-selected-arcanum",
                 disabled=(len(selected_arcanum) != 1)):
        arcanum = selected_arcanum[0]
        controller.character.special.arcana.append(arcanum)
        st.rerun()


def _describe_companion_skill(skill: CompanionSkill, loc: LocNamespace,
                               attacks: list[CompanionAttack] | None = None) -> str:
    match skill.name:
        case CompanionSkillName.damage_resistance:
            return join_with_and([d.localized_name(loc) for d in skill.damage_types], loc)
        case CompanionSkillName.damage_immunity:
            return join_with_and([d.localized_name(loc) for d in skill.damage_types], loc)
        case CompanionSkillName.damage_absorption:
            return join_with_and([d.localized_name(loc) for d in skill.damage_types], loc)
        case CompanionSkillName.status_effect_immunity:
            return join_with_and([s.localized_name(loc) for s in skill.statuses], loc)
        case CompanionSkillName.improved_defenses:
            key = f"companion_defense_option_{skill.defense_option}"
            return getattr(loc, key, skill.defense_option or "")
        case CompanionSkillName.specialized:
            key = f"companion_check_type_{skill.check_type}"
            base = getattr(loc, key, skill.check_type or "")
            if skill.check_type == "opposed" and skill.check_context:
                return f"{base} ({skill.check_context})"
            return base
        case CompanionSkillName.improved_damage:
            if attacks and skill.attack_index is not None and skill.attack_index < len(attacks):
                attack_name = attacks[skill.attack_index].name
                if attack_name:
                    return attack_name
            return loc.companion_skill_attack_target + f" #{(skill.attack_index or 0) + 1}"
        case CompanionSkillName.improved_hit_points | CompanionSkillName.flying:
            return ""
        case _:
            return skill.description


def _companion_skill_extra_inputs(
        skill_name: CompanionSkillName,
        loc: LocNamespace,
        attacks: list[CompanionAttack],
        absorbable_types: list[DamageType],
        key_prefix: str = "companion-skill",
) -> tuple[dict, bool]:
    match skill_name:
        case CompanionSkillName.damage_resistance:
            types = st.multiselect(loc.page_view_select_damage, COMPANION_SELECTABLE_DAMAGE_TYPES,
                                    format_func=lambda d: d.localized_name(loc), max_selections=2,
                                    key=f"{key_prefix}-resistance-types")
            return {"damage_types": types or []}, len(types or []) == 2
        case CompanionSkillName.damage_immunity:
            damage_type = st.selectbox(loc.page_view_select_damage, COMPANION_SELECTABLE_DAMAGE_TYPES,
                                        format_func=lambda d: d.localized_name(loc),
                                        key=f"{key_prefix}-immunity-type")
            return {"damage_types": [damage_type]}, damage_type is not None
        case CompanionSkillName.damage_absorption:
            if not absorbable_types:
                st.warning(loc.error_companion_no_absorbable_damage)
                return {}, False
            damage_type = st.selectbox(loc.page_view_select_damage, absorbable_types,
                                        format_func=lambda d: d.localized_name(loc),
                                        key=f"{key_prefix}-absorption-type")
            return {"damage_types": [damage_type]}, damage_type is not None
        case CompanionSkillName.status_effect_immunity:
            statuses = st.multiselect(loc.page_view_select_status, [s for s in Status],
                                       format_func=lambda s: s.localized_name(loc), max_selections=2,
                                       key=f"{key_prefix}-status-types")
            return {"statuses": statuses or []}, len(statuses or []) == 2
        case CompanionSkillName.improved_defenses:
            option = st.pills(
                loc.companion_defense_option,
                ["defense", "magic_defense"],
                format_func=lambda o: getattr(loc, f"companion_defense_option_{o}"),
                key=f"{key_prefix}-defense-option",
            )
            return {"defense_option": option}, option is not None
        case CompanionSkillName.specialized:
            check_type = st.pills(
                loc.companion_check_type,
                ["accuracy", "magic", "opposed"],
                format_func=lambda o: getattr(loc, f"companion_check_type_{o}"),
                key=f"{key_prefix}-check-type",
            )
            context = None
            if check_type == "opposed":
                context = st.text_input(loc.companion_check_context, key=f"{key_prefix}-check-context")
            valid = check_type is not None and (check_type != "opposed" or bool(context))
            return {"check_type": check_type, "check_context": context}, valid
        case CompanionSkillName.improved_damage:
            if not attacks:
                st.warning(loc.companion_basic_attacks)
                return {}, False
            attack_index = st.selectbox(
                loc.companion_skill_attack_target,
                list(range(len(attacks))),
                format_func=lambda i: attacks[i].name or f"#{i + 1}",
                key=f"{key_prefix}-attack-index",
            )
            return {"attack_index": attack_index}, attack_index is not None
        case CompanionSkillName.improved_hit_points | CompanionSkillName.flying:
            return {}, True
        case _:
            description = st.text_area(loc.companion_skill_free_text, key=f"{key_prefix}-description")
            return {"description": description}, bool(description)


def add_companion(controller: CharacterController, loc: LocNamespace):
    name = st.text_input(loc.companion_name)
    species = st.pills(
        loc.companion_species,
        COMPANION_ALLOWED_SPECIES,
        format_func=lambda s: s.localized_name(loc),
        key="companion-species",
    )

    species_damage_choice = None
    if species == Species.elemental:
        choices = [d for d in COMPANION_SELECTABLE_DAMAGE_TYPES if d != DamageType.poison]
        species_damage_choice = st.selectbox(
            loc.companion_species_damage_choice_elemental, choices,
            format_func=lambda d: d.localized_name(loc), key="companion-species-choice",
        )
        st.caption(loc.companion_innate_elemental)
    elif species == Species.plant:
        species_damage_choice = st.selectbox(
            loc.companion_species_damage_choice_plant, PLANT_VULNERABILITY_CHOICES,
            format_func=lambda d: d.localized_name(loc), key="companion-species-choice",
        )
        st.caption(loc.companion_innate_plant)
    elif species == Species.construct:
        st.caption(loc.companion_innate_construct)

    st.markdown(f"##### {loc.companion_attribute_array}")
    dexterity = st.select_slider(loc.attr_dexterity, options=[6, 8, 10, 12], value=8, key="companion-dex")
    might = st.select_slider(loc.attr_might, options=[6, 8, 10, 12], value=8, key="companion-mig")
    insight = st.select_slider(loc.attr_insight, options=[6, 8, 10, 12], value=8, key="companion-ins")
    willpower = st.select_slider(loc.attr_willpower, options=[6, 8, 10, 12], value=8, key="companion-wlp")

    picked_array = sorted([dexterity, might, insight, willpower], reverse=True)
    is_valid_array = picked_array in [sorted(a, reverse=True) for a in COMPANION_ATTRIBUTE_ARRAYS.values()]
    if not is_valid_array:
        st.error(loc.error_companion_invalid_array)
        for key in COMPANION_ATTRIBUTE_ARRAYS:
            st.caption(getattr(loc, f"companion_array_{key}"))

    # NOTE: this dialog must NEVER call st.rerun() except in the final "create companion"
    # submit below — st.rerun() closes an open st.dialog (it forces a full-script rerun
    # instead of just re-running this dialog's own fragment), so every intermediate
    # add/remove step here relies on the dialog's own automatic fragment rerun instead.
    st.divider()
    st.markdown(f"##### {loc.companion_basic_attacks}")
    st.session_state.companion_attacks = st.session_state.get("companion_attacks", [])

    if len(st.session_state.companion_attacks) < 2:
        with st.expander(loc.companion_add_attack_button):
            attack_name = st.text_input(loc.companion_attack_name, key="companion-attack-name")
            c1, c2 = st.columns(2)
            with c1:
                acc1 = st.selectbox("companion-acc1", [a for a in AttributeName], key="companion-attack-acc1",
                                    label_visibility="hidden", format_func=lambda a: AttributeName.to_alias(a, loc))
            with c2:
                acc2 = st.selectbox("companion-acc2", [a for a in AttributeName], key="companion-attack-acc2",
                                    label_visibility="hidden", format_func=lambda a: AttributeName.to_alias(a, loc))
            damage_type = st.pills(loc.page_view_item_damage_type, COMPANION_SELECTABLE_DAMAGE_TYPES,
                                   format_func=lambda d: d.localized_name(loc), key="companion-attack-dmg")
            attack_range = st.pills(loc.page_view_item_range, [r for r in WeaponRange],
                                    format_func=lambda r: r.localized_name(loc), key="companion-attack-range")
            if st.button(loc.companion_add_attack_button, key="companion-attack-add",
                         disabled=not (attack_name and damage_type and attack_range)):
                st.session_state.companion_attacks.append(CompanionAttack(
                    name=attack_name, accuracy=[acc1, acc2], damage_type=damage_type, range=attack_range,
                ))
    else:
        st.info(loc.error_companion_max_attacks)

    for i, attack in enumerate(st.session_state.companion_attacks):
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            acc = " + ".join(AttributeName.to_alias(a, loc) for a in attack.accuracy)
            st.markdown(
                f"**{attack.name}** ◆ {acc} ◆ {loc.hr} + 5 {attack.damage_type.localized_name(loc)} "
                f"◆ {attack.range.localized_name(loc)}"
            )
        with c2:
            if st.button(loc.remove_button, key=f"companion-attack-remove-{i}"):
                st.session_state.companion_attacks.pop(i)

    st.divider()
    st.markdown(f"##### {loc.companion_skills}")
    st.session_state.companion_skills = st.session_state.get("companion_skills", [])
    max_skills = SPECIES_STARTING_SKILLS.get(species, 0)

    if species and len(st.session_state.companion_skills) < max_skills:
        with st.expander(loc.companion_add_skill_button):
            limited_taken = {
                s.name for s in st.session_state.companion_skills
                if s.name in (CompanionSkillName.flying, CompanionSkillName.final_act)
            }
            selectable = [s for s in CompanionSkillName if s not in limited_taken]
            skill_name = st.selectbox(
                loc.companion_skill_name, selectable,
                format_func=lambda s: CompanionSkill(name=s).localized_name(loc),
                key="companion-skill-select",
            )
            if skill_name is not None:
                st.caption(CompanionSkill(name=skill_name).localized_description(loc))

            temp_companion = Companion(species=species, species_damage_choice=species_damage_choice)
            absorbable = sorted(set(
                temp_companion.innate_resistances() + temp_companion.innate_immunities()
                + [dt for s in st.session_state.companion_skills
                   if s.name in (CompanionSkillName.damage_resistance, CompanionSkillName.damage_immunity)
                   for dt in s.damage_types]
            ), key=lambda d: d.value)

            extra_kwargs, is_valid = _companion_skill_extra_inputs(
                skill_name, loc, st.session_state.companion_attacks, absorbable,
            )

            if st.button(loc.companion_add_skill_button, key="companion-skill-add", disabled=not is_valid):
                st.session_state.companion_skills.append(CompanionSkill(name=skill_name, **extra_kwargs))
    elif species:
        st.info(loc.error_companion_max_skills.format(max_skills=max_skills))

    for i, skill in enumerate(st.session_state.companion_skills):
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            specific = _describe_companion_skill(skill, loc, st.session_state.companion_attacks)
            st.markdown(f"**{skill.localized_name(loc)}**" + (f" — {specific}" if specific else ""))
            st.caption(skill.localized_description(loc))
        with c2:
            if st.button(loc.remove_button, key=f"companion-skill-remove-{i}"):
                st.session_state.companion_skills.pop(i)

    can_confirm = bool(name) and species is not None and is_valid_array
    if st.button(loc.add_companion_button, key="companion-create-confirm", disabled=not can_confirm):
        companion = Companion(
            name=name,
            species=species,
            dexterity=dexterity,
            might=might,
            insight=insight,
            willpower=willpower,
            species_damage_choice=species_damage_choice,
            basic_attacks=st.session_state.companion_attacks,
            skills=st.session_state.companion_skills,
        )
        controller.set_companion(companion)
        st.session_state.companion_attacks = []
        st.session_state.companion_skills = []
        st.toast(loc.msg_companion_added.format(name=companion.name))
        st.rerun()


def add_companion_skill(controller: CharacterController, loc: LocNamespace):
    companion = controller.character.special.companion

    limited_taken = {
        s.name for s in companion.skills
        if s.name in (CompanionSkillName.flying, CompanionSkillName.final_act)
    }
    selectable = [s for s in CompanionSkillName if s not in limited_taken]
    skill_name = st.selectbox(
        loc.companion_skill_name, selectable,
        format_func=lambda s: CompanionSkill(name=s).localized_name(loc),
        key="companion-view-skill-select",
    )
    if skill_name is not None:
        st.caption(CompanionSkill(name=skill_name).localized_description(loc))

    absorbable = sorted(set(
        companion.innate_resistances() + companion.innate_immunities()
        + [dt for s in companion.skills
           if s.name in (CompanionSkillName.damage_resistance, CompanionSkillName.damage_immunity)
           for dt in s.damage_types]
    ), key=lambda d: d.value)

    extra_kwargs, is_valid = _companion_skill_extra_inputs(
        skill_name, loc, companion.basic_attacks, absorbable, key_prefix="companion-view-skill",
    )

    if st.button(loc.companion_add_skill_button, key="companion-view-skill-add", disabled=not is_valid):
        companion.skills.append(CompanionSkill(name=skill_name, **extra_kwargs))
        st.rerun()


def display_companion(controller: CharacterController, loc: LocNamespace):
    companion = controller.character.special.companion
    if companion is None:
        return

    c1, c2 = st.columns([0.8, 0.2])
    with c1:
        st.markdown(f"##### {companion.name} — _{companion.species.localized_name(loc)}_")
    with c2:
        if st.button(loc.remove_companion_button, key="companion-remove"):
            controller.remove_companion()
            st.rerun()

    st.caption(loc.companion_no_initiative)
    st.markdown(f"**{loc.companion_check_bonus.format(bonus=controller.companion_check_bonus())}**")

    att_col1, att_col2, hp_col = st.columns([0.25, 0.25, 0.5])
    with att_col1:
        st.markdown(f"**{loc.attr_dexterity}**: {loc.dice_prefix}{companion.dexterity}")
        st.markdown(f"**{loc.attr_might}**: {loc.dice_prefix}{companion.might}")
        st.markdown(f"**{loc.column_defense}**: {controller.companion_defense()}")
    with att_col2:
        st.markdown(f"**{loc.attr_insight}**: {loc.dice_prefix}{companion.insight}")
        st.markdown(f"**{loc.attr_willpower}**: {loc.dice_prefix}{companion.willpower}")
        st.markdown(f"**{loc.column_magic_defense}**: {controller.companion_magic_defense()}")
    with hp_col:
        max_hp = controller.companion_max_hp()
        current_hp = controller.companion_current_hp()
        st.progress(
            max(current_hp / max_hp, 0) if max_hp else 0,
            text=f"{loc.companion_hp} {current_hp} / {max_hp}"
        )
        hc1, hc2, hc3, hc4 = st.columns([0.4, 0.2, 0.2, 0.2])
        with hc1:
            hp_input = st.number_input("companion_hp_input", min_value=0, label_visibility="hidden", value=10,
                                       key="companion-hp-input")
        with hc2:
            st.write("")
            if st.button("", icon=":material/add:", key="companion-hp-add"):
                controller.state.companion_minus_hp = max(0, controller.state.companion_minus_hp - hp_input)
                st.rerun()
        with hc3:
            st.write("")
            if st.button("", icon=":material/remove:", key="companion-hp-subtract"):
                controller.state.companion_minus_hp = min(max_hp, controller.state.companion_minus_hp + hp_input)
                st.rerun()
        with hc4:
            st.write("")
            if st.button("", icon=":material/laps:", key="companion-hp-reset", help="Reset HP"):
                controller.state.companion_minus_hp = 0
                st.rerun()

    if current_hp <= 0:
        if st.button(loc.companion_flee_button, key="companion-flee"):
            controller.companion_flee()
            st.rerun()

    if companion.basic_attacks:
        st.divider()
        st.markdown(f"###### {loc.companion_basic_attacks}")
        for idx, attack in enumerate(companion.basic_attacks):
            acc = " + ".join(f"{loc.dice_prefix}{getattr(companion, a)}" for a in attack.accuracy)
            dmg_bonus = controller.companion_attack_damage_bonus(idx)
            ac1, ac2, ac3, ac4, _ = st.columns([0.15, 0.1, 0.1, 0.3, 0.35])
            with ac1:
                st.markdown("⚔️")
                st.write(attack.name)
            with ac2:
                st.markdown("_&nbsp;_")
                st.write(attack.range.localized_name(loc))
            with ac3:
                st.markdown(f"_{loc.column_accuracy}_")
                st.write(acc)
            with ac4:
                st.markdown(f"_{loc.column_damage}_")
                st.markdown(f"{loc.hr} + {5 + dmg_bonus} ◆ {attack.damage_type.localized_name(loc)}")

    max_skills = controller.companion_max_skills()
    if companion.skills or max_skills > 0:
        st.divider()

        @st.dialog(loc.page_view_add_companion_skill_dialog_title, width="large")
        def add_companion_skill_dialog():
            add_companion_skill(controller, loc)

        sk_col1, sk_col2 = st.columns([0.8, 0.2])
        with sk_col1:
            st.markdown(f"###### {loc.companion_skills}")
        with sk_col2:
            if len(companion.skills) < max_skills:
                if st.button(loc.companion_add_skill_button, key="companion-view-add-skill-button"):
                    add_companion_skill_dialog()

        for skill in companion.skills:
            specific = _describe_companion_skill(skill, loc, companion.basic_attacks)
            st.markdown(f"_{skill.localized_name(loc)}_" + (f" — **{specific}**" if specific else ""))
            desc_col, _ = st.columns([0.5, 0.5])
            with desc_col:
                st.markdown(skill.localized_description(loc))

    resistances = controller.companion_all_resistances()
    immunities = controller.companion_all_immunities()
    absorptions = controller.companion_all_absorptions()
    vulnerabilities = controller.companion_all_vulnerabilities()
    status_immunities = controller.companion_all_status_immunities()

    if any((resistances, immunities, absorptions, vulnerabilities, status_immunities)):
        st.divider()
        if resistances:
            st.markdown(f"**{loc.companion_resistances}**: {join_with_and([d.localized_name(loc) for d in resistances], loc)}")
        if immunities:
            st.markdown(f"**{loc.companion_immunities}**: {join_with_and([d.localized_name(loc) for d in immunities], loc)}")
        if absorptions:
            st.markdown(f"**{loc.companion_absorptions}**: {join_with_and([d.localized_name(loc) for d in absorptions], loc)}")
        if vulnerabilities:
            st.markdown(f"**{loc.companion_vulnerabilities}**: {join_with_and([d.localized_name(loc) for d in vulnerabilities], loc)}")
        if status_immunities:
            st.markdown(f"**{loc.companion_status_immunities}**: {join_with_and([s.localized_name(loc) for s in status_immunities], loc)}")

