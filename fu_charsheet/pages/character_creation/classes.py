import streamlit as st

from pages.character_creation.creation_state import CreationState
from pages.character_creation.utils import set_creation_state, SkillTableWriter, if_show_spells, SpellTableWriter, \
    list_skills, show_martial
from pages.character_creation.controller import CharacterController, ClassController
from data.models.character_config import ClassName, Skill, Spell
from data import compendium as c


@st.dialog("Add a class", width="large")
@st.fragment
def add_new_class(character_controller: CharacterController, class_controller: ClassController):

    class_not_ready = True
    selected_class_name = st.selectbox(
        "New class",
        [str(char_class.name).title() for char_class in c.COMPENDIUM.classes.classes],
        index=None,
        placeholder="Select a class",
        accept_new_options=False,
    )
    selected_class = c.COMPENDIUM.classes.get_class(selected_class_name)
    selected_class_name = selected_class_name.lower() if selected_class_name else selected_class_name

    if selected_class:
        if character_controller.is_class_added(selected_class):
            st.error("You already added this class")
        else:
            class_bonus = selected_class.class_bonus
            bonus_message = f"Your maximum **{class_bonus.upper()}** is permanently increased by **{selected_class.bonus_value}**."
            st.markdown(bonus_message)

            show_martial(selected_class)

            if selected_class.rituals:
                st.write(f"Your character can perform Rituals whose effects fall within the {', '.join(r.title() for r in selected_class.rituals)} discipline.")


            class_controller.char_class = selected_class
            casting_skill = class_controller.char_class.get_spell_skill()

            with st.expander("Choose skills"):
                SkillTableWriter().write_in_columns(selected_class.skills)

            can_add_skill_number: int = character_controller.can_add_skill_number() - class_controller.char_class.class_level()

            if class_controller.char_class.class_level() < 1:
                class_not_ready = True
                st.error("You need to select at least one skill to add this class.")
            elif can_add_skill_number < 0:
                st.error(f"Remove {(abs(can_add_skill_number))} level(s) from your skills.")
                class_not_ready = True
            else:
                list_skills(class_controller, can_add_skill_number)
                class_not_ready = False

            if if_show_spells(casting_skill):
                class_spells = c.COMPENDIUM.spells.get_spells(class_controller.char_class.name)
                with st.expander("Select spells"):
                    SpellTableWriter().write_in_columns(class_spells)
                total_class_spells = len(st.session_state["class_spells"])
                max_n_spells = casting_skill.current_level

                if total_class_spells != max_n_spells:
                    class_not_ready = True
                    st.error(f"You need to select exactly {max_n_spells} spells (one for each level in {casting_skill.name.title()}).")
                else:
                    class_not_ready = False


            # try:
            #
            #     class_not_ready = False
            # except Exception as e:
            #     st.error(e, icon="🚨")

    if st.button("Add this class", disabled=class_not_ready):
        character_controller.add_class(class_controller.char_class)
        character_controller.character.spells[selected_class_name] = st.session_state.class_spells
        st.session_state.class_spells = []
        st.info(f"Added {selected_class} to your character.")
        st.rerun()


def build(character_controller: CharacterController):
    st.session_state.class_controller = ClassController()
    st.session_state.class_spells = st.session_state.get("class_spells", [])
    not_ready_for_the_next_step = not character_controller.has_enough_skills()
    st.title("Character classes")
    current_classes = character_controller.get_character().classes
    st.write(f"Your character has {len(current_classes)} following classes: {', '.join([c.name.title() for c in current_classes])}")
    st.write(f"You added {character_controller.get_character().get_n_skill()} skills from {character_controller.get_character().level} available.")
    if st.button("Add a class", disabled=character_controller.has_enough_skills()):
        add_new_class(character_controller, st.session_state.class_controller)

    if st.button("Next", disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.attributes)
