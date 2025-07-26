import streamlit as st

from .creation_state import CreationState
from .utils import set_creation_state
from .controller import CharacterController, ClassController
from data.models.character_config import ClassName, ClassBonus, Ritual, Skill, Dexterity, Might, Insight, Willpower


attributes_message = """Each of a Player Character’s main Attributes (**Dexterity**, **Insight**, **Might**, and **Willpower**) is represented by a die size, from a minimum of **d6** to a maximum of **d12**.
Bigger die sizes indicate a more trained Attribute or a stronger natural talent.

- **Dexterity** measures precision, coordination, finesse and reflexes.
- **Insight** represents observation, understanding and reasoning.
- **Might** is a measure of strength, resilience and physical fortitude.
- **Willpower** represents determination, charisma and the ability to influence others.

Choose one of the following profiles for your hero, then distribute the corresponding die sizes among their four Attributes.
- **Jack of All Trades**: d8, d8, d8, d8 
- **Average**: d10, d8, d8, d6 
- **Specialized**: d10, d10, d6, d6
"""

def build(view_model: CharacterController):
    st.title("Character attributes")
    st.markdown(attributes_message)
    dexterity = st.select_slider(
        "Dexterity",
        options=[6, 8, 10, 12],
        value=8,
    )
    might = st.select_slider(
        "Might",
        options=[6, 8, 10, 12],
        value=8
    )
    insight = st.select_slider(
        "Insight",
        options=[6, 8, 10, 12],
        value=8
    )
    willpower = st.select_slider(
        "Willpower",
        options=[6, 8, 10, 12],
        value=8
    )
    not_ready_for_the_next_step = (sum([dexterity, might, insight, willpower]) != 32)
    if not_ready_for_the_next_step:
        st.error("Sum of your attributes should be equal to 32.", icon="🎲")
    try:
        view_model.character.dexterity = Dexterity(base=dexterity, current=dexterity)
        view_model.character.might = Might(base=might, current=might)
        view_model.character.insight = Insight(base=insight, current=insight)
        view_model.character.willpower = Willpower(base=willpower, current=willpower)
    except Exception as e:
        st.error(e, icon="🚨")

    if st.button("Next", disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.equipment)
