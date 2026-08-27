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

# 2. Render Compact Ask Echo Interface
render_echo_chat(title="Ask Echo")
