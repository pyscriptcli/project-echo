import streamlit as st

def setup_page_layout():
    """Hides default UI elements and renders the custom navigation bar."""
    st.markdown("""
    <style>
    header[data-testid="stHeader"], .stApp > header, [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], #MainMenu, footer,
    section[data-testid="stSidebar"], [data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"], button[data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render your custom horizontal navbar with EQUAL width columns
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.page_link("app.py", label="Dashboard", icon=":material/dashboard:", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", icon=":material/menu_book:", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", icon=":material/edit_note:", use_container_width=True)
    with col4:
        st.page_link("pages/3_ask_echo.py", label="Ask Echo", icon=":material/smart_toy:", use_container_width=True)
