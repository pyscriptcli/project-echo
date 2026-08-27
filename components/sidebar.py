import streamlit as st

def setup_page_layout():
    """Hides default UI elements and renders the custom charcoal & gold navigation bar."""
    st.markdown("""
    <style>
    /* Hide default Streamlit UI */
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
        padding-top: 1rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* Charcoal & Gold Navbar Container */
    .navbar-container {
        background-color: #22252A !important; /* Charcoal Black */
        border-bottom: 3px solid #D4AF37 !important; /* Gold Accent Line */
        border-radius: 8px 8px 0 0 !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* Style the page links inside the navbar */
    .navbar-container div[data-testid="stPageLink-NavLink"] {
        background-color: transparent !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important; /* Subtle gold border */
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .navbar-container div[data-testid="stPageLink-NavLink"]:hover {
        background-color: rgba(212, 175, 55, 0.1) !important; /* Gold tint on hover */
        border-color: #D4AF37 !important;
        transform: translateY(-1px);
    }
    
    .navbar-container div[data-testid="stPageLink-NavLink"] a {
        color: #E0E0E0 !important; /* Light gray text */
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
    
    .navbar-container div[data-testid="stPageLink-NavLink"]:hover a {
        color: #D4AF37 !important; /* Gold text on hover */
    }
    </style>
    """, unsafe_allow_html=True)

    # Render Navbar Container
    st.markdown('<div class="navbar-container">', unsafe_allow_html=True)
    
    # Render your custom horizontal navbar with EQUAL width columns
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.page_link("app.py", label="Dashboard", icon=":material/dashboard:", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", icon=":material/menu_book:", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", icon=":material/edit_note:", use_container_width=True)
    with col4:
        st.page_link("pages/3_echo_ai.py", label="Ask Echo", icon=":material/smart_toy:", use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
