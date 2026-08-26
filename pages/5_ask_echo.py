import streamlit as st
from components.floating_chat import render_chat_body

st.set_page_config(page_title="Project Echo - AI Assistant", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp { background-color: #F3EFE6; }
h2 { font-family: 'Playfair Display', serif !important; font-style: italic !important; color: #1A2B4C !important; }
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; border-radius: 12px !important;
    box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1) !important; padding: 2rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("## Ask Echo &mdash; Enterprise Intelligence Hub")
st.caption("Ask cross-meeting queries across all team records, deliverables, transcripts, and commitments.")

with st.container(border=True):
    render_chat_body(history_key="global_chat_history")
