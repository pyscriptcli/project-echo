import sys
import os
import streamlit as st

# Ensure root directory is resolvable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.sidebar import setup_page_layout
from utils.echo_ai import render_echo_chat
from utils.auth import require_login

# 1. Page Configuration
st.set_page_config(
    page_title="Ask Echo",
    layout="wide",
    initial_sidebar_state="expanded"
)
require_login()
setup_page_layout()

# 2. Large Architectural Grid Canvas (Matching Meeting Gallery)
st.markdown("""
<style>
/* Enable vertical scrolling on root viewports */
html, body, [data-testid="stAppViewContainer"], .stApp, .main, .block-container {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scrollbar-width: none !important; /* Firefox */
    -ms-overflow-style: none !important;  /* IE and Edge */
}

/* Hide scrollbars across WebKit browsers (Chrome, Safari, Edge) */
html::-webkit-scrollbar,
body::-webkit-scrollbar,
[data-testid="stAppViewContainer"]::-webkit-scrollbar,
.stApp::-webkit-scrollbar,
.main::-webkit-scrollbar,
.block-container::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    background: transparent !important;
}

[data-testid="stAppViewContainer"], .stApp {
    background-color: #ECEBDE !important;
}

.main, .block-container {
    padding-top: 1rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Render Ask Echo Viewport
render_echo_chat(title="Ask Echo")
