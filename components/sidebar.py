import streamlit as st

def render_custom_navbar():
    col1, col2, col3, _ = st.columns([1.2, 1.2, 2.0, 5.6])
    
    with col1:
        st.page_link("app.py", label="Dashboard", icon=":material/dashboard:", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", icon=":material/menu_book:", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", icon=":material/edit_note:", use_container_width=True)
