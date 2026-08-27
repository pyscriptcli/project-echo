import streamlit as st

def render_custom_sidebar():
    # Navigation Links (Material Icons act as SVGs)
    st.page_link("app.py", label="Executive Dashboard", icon=":material/dashboard:")
    st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM Generator", icon=":material/edit_note:")
    st.page_link("pages/2_meeting_details.py", label="Meeting Browser", icon=":material/menu_book:")
