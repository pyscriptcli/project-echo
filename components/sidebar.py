# In components/navigation.py (or components/sidebar.py)
import streamlit as st

def render_global_navigation():
    # Top Bar Columns
    col1, col2, col3, _ = st.columns([1, 1, 1, 99])
    
    with col1:
        st.markdown('<div class="top-nav-marker"></div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard")
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings")
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM")

# Compatibility aliases
setup_page_layout = render_global_navigation
single_page_layout = render_global_navigation
render_custom_sidebar = render_global_navigation
