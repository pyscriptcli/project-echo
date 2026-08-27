# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders an ultra-minimalist, pure-text sidebar navigation without any SVG icons.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Montserrat:wght@400;500&display=swap');

    /* 1. HIDE ALL DEFAULT STREAMLIT HEADER & NAV ARTIFACTS */
    header[data-testid="stHeader"], 
    .stApp > header, 
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], 
    #MainMenu, 
    footer,
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* 2. MINIMAL SIDEBAR BACKGROUND & BORDERS */
    section[data-testid="stSidebar"] {
        background-color: #121212 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        box-shadow: none !important;
    }

    /* Ensure content inside sidebar container flows cleanly */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        padding: 2.5rem 1.5rem !important;
        gap: 1.25rem !important;
    }

    /* 3. STRICTLY REMOVE ALL SVG ICONS & ICON WRAPPERS */
    section[data-testid="stSidebar"] svg,
    section[data-testid="stSidebar"] span[data-testid="stIconMaterial"],
    section[data-testid="stSidebar"] [data-testid="stPageLink-Icon"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 4. PURE TEXT LINK STYLING */
    section[data-testid="stSidebar"] a {
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0.35rem 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        text-decoration: none !important;
        justify-content: flex-start !important;
        transition: color 0.2s ease !important;
    }

    /* Typography - Default Muted Gold */
    section[data-testid="stSidebar"] a span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"] a p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        color: #A89060 !important;
        letter-spacing: 0.03em !important;
        line-height: 1.2 !important;
        transition: color 0.2s ease, transform 0.2s ease !important;
    }

    /* Hover State */
    section[data-testid="stSidebar"] a:hover span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"] a:hover p {
        color: #F1D483 !important;
    }

    /* Active / Current Page State */
    section[data-testid="stSidebar"] a[aria-current="page"] span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"] a[data-active="true"] span[data-testid="stPageLink-Text"] {
        color: #E2BC5A !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.page_link("app.py", label="Dashboard")
        st.page_link("pages/2_meeting_details.py", label="Meetings")
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM")

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
