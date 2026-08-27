import streamlit as st

def render_custom_sidebar():
    # Navigation Links (Material Icons act as SVGs)
    st.page_link("app.py", label="Dashboard", icon=":material/dashboard:")
    st.page_link("pages/2_meeting_details.py", label="Meetings", icon=":material/menu_book:")
    st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", icon=":material/edit_note:")

