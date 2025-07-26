import streamlit as st


title = 'error'
icon = "🚨"


def build(error_message):
    st.write(str(error_message))
