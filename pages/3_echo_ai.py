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

# 2. Global Canvas Background Grid & Scroll Lock
st.markdown("""
<style>
/* Global warm canvas background matching reference */
[data-testid="stAppViewContainer"], .stApp {
    background-color: #F6F2EA !important;
    background-image: 
        linear-gradient(to right, #E8E2D5 1px, transparent 1px),
        linear-gradient(to bottom, #E8E2D5 1px, transparent 1px) !important;
    background-size: 32px 32px !important;
    overflow: hidden !important;
}

.main, .block-container {
    overflow: hidden !important;
    padding-top: 1rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Render Ask Echo Viewport
render_echo_chat(title="Ask Echo")
