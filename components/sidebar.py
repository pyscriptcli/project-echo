import streamlit as st

def render_custom_sidebar():
    # Sidebar Title
    st.markdown("""
    <div style="padding: 2.5rem 1rem 1.5rem 1rem; text-align: center; border-bottom: 1px solid #3a3a3a; margin-bottom: 1rem;">
        <h1 style="font-family: 'Cormorant Garamond', serif; color: #c9a84c; font-size: 2.2rem; margin: 0; font-weight: 700; letter-spacing: 0.05em;">
            Project Echo
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Links (Material Icons act as SVGs)
    st.page_link("app.py", label="Executive Dashboard", icon=":material/dashboard:")
    st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM Generator", icon=":material/edit_note:")
    st.page_link("pages/2_meeting_details.py", label="Meeting Browser", icon=":material/menu_book:")
