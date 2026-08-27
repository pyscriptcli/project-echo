import sys
import os
import streamlit as st

# Ensure root directory is resolvable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.sidebar import setup_page_layout
from utils.echo_ai import render_echo_chat

# 1. Page Configuration
st.set_page_config(
    page_title="Project Echo - Global Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)
setup_page_layout()

# 2. Page Header
st.markdown("""
<h2 style="font-family: 'Playfair Display', serif; font-style: italic; color: #1A2B4C; margin-bottom: 0.2rem;">
Echo Global Intelligence
</h2>
<p style="font-size: 0.85rem; color: #555E68; margin-bottom: 1.5rem;">
Dedicated workspace for deep-dive analysis across all meeting archives, transcripts, and action logs.
</p>
""", unsafe_allow_html=True)

# 3. Render the Echo Chat Plugin (Full Page Mode)
# We give it a larger height (e.g., 850px) since it is the main focus of this page.
render_echo_chat(
    container=st,
    height=850, 
    title="Ask Echo — Global Intelligence",
    caption="Synthesize meeting archives, transcripts, and action logs."
)
