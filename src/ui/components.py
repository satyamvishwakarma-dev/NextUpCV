import streamlit as st
import time

def flash_success(message, duration=3):
    """Displays a success message and removes it after X seconds."""
    placeholder = st.empty()
    placeholder.success(message)
    time.sleep(duration)
    placeholder.empty()


def flash_error(message, duration=3):
    """Displays an error message and removes it after X seconds."""
    placeholder = st.empty()
    placeholder.error(message)
    time.sleep(duration)
    placeholder.empty()
