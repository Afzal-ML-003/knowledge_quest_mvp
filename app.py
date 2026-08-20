import streamlit as st

from game import state as gstate
from ui.styles import inject_css
from ui.screens import (
    render_menu, render_setup, render_playing,
    render_level_complete, render_results,
)

st.set_page_config(
    page_title="Knowledge Quest",
    page_icon="🧭",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_css()
gstate.init_state()

state = gstate.gs()
screen = state["screen"]

if screen == "menu":
    render_menu()
elif screen == "setup":
    render_setup()
elif screen == "playing":
    render_playing()
elif screen == "level_complete":
    render_level_complete()
elif screen == "results":
    render_results()
else:
    st.error(f"Unknown screen: {screen}")
    gstate.reset_game()
    st.rerun()
