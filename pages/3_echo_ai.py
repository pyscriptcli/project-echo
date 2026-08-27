import sys
import os
import streamlit as st

# Ensure root directory is resolvable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.sidebar import setup_page_layout
from utils.echo_ai import render_echo_chat

# 1. Page Configuration
st.set_page_config(
    page_title="Ask Echo",
    layout="wide",
    initial_sidebar_state="collapsed"
)
setup_page_layout()

# 2. Lock outside page scrolling & optimize top padding
st.markdown("""
<style>
/* Prevent scrolling outside the chat box */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Render the Unified Ask Echo Interface
render_echo_chat(
    container=st,
    height=860,
    title="Ask Echo"
)
