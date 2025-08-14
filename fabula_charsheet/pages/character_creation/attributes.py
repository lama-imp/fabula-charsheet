import streamlit as st

from data.models import Dexterity, Might, Insight, Willpower, LocNamespace
from .creation_state import CreationState
from pages.utils import set_creation_state
from pages.controller import CharacterController


def build(controller: CharacterController):
    loc: LocNamespace = st.session_state.localizator.get(st.session_state.language)
    st.title(loc.page_attributes_title)
    st.markdown(loc.page_attributes_title)
    dexterity = st.select_slider(
        loc.attr_dexterity,
        options=[6, 8, 10, 12],
        value=8,
    )
    might = st.select_slider(
        loc.attr_might,
        options=[6, 8, 10, 12],
        value=8
    )
    insight = st.select_slider(
        loc.attr_insight,
        options=[6, 8, 10, 12],
        value=8
    )
    willpower = st.select_slider(
        loc.attr_willpower,
        options=[6, 8, 10, 12],
        value=8
    )
    not_ready_for_the_next_step = (sum([dexterity, might, insight, willpower]) != 32)
    if not_ready_for_the_next_step:
        st.error(loc.page_attributes_sum_error, icon="🎲")
    try:
        controller.character.dexterity = Dexterity(base=dexterity, current=dexterity)
        controller.character.might = Might(base=might, current=might)
        controller.character.insight = Insight(base=insight, current=insight)
        controller.character.willpower = Willpower(base=willpower, current=willpower)
    except Exception as e:
        st.error(e, icon="🚨")

    if st.button(loc.page_next_button, disabled=not_ready_for_the_next_step):
        set_creation_state(CreationState.equipment)
