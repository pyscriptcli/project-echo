# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a minimalist, left-aligned pure text navigation bar. 
    Forces columns to shrink-wrap their content and hug the left margin.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&display=swap');

    /* 1. HIDE ALL DEFAULT STREAMLIT HEADER & SIDEBAR ARTIFACTS */
    header[data-testid="stHeader"], 
    .stApp > header, 
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], 
    #MainMenu, 
    footer,
    section[data-testid="stSidebar"], 
    [data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"], 
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* 2. RECLAIM PAGE TOP PADDING */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. MINIMALIST TOPBAR CONTAINER (FLEX ALIGN LEFT) */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 2rem !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important; /* Force everything to the left */
        align-items: center !important;
        width: 100% !important;
        gap: 2.5rem !important; /* Exact spacing between the links */
    }

    /* Strip column widths so they shrink to fit the text exactly */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) > div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
    }

    /* 4. BASE LINK STYLING (Pure Text) */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        height: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        text-decoration: none !important;
        box-shadow: none !important;
    }

    /* Typography - Base Gold */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.4rem !important;
        font-weight: 500 !important;
        color: #B59345 !important;
        letter-spacing: 0.03em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        transition: color 0.2s ease !important;
    }

    /* 5. HOVER EFFECT */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover p {
        color: #82631D !important;
    }

    /* 6. ACTIVE SELECTED TAB */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"] span,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[data-active="true"] span {
        color: #D4AF37 !important;
        font-weight: 700 !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICONS */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) span[data-testid="stIconMaterial"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Topbar Layout
    # Assigning massive weight to the empty 4th column naturally pushes the first three tight to the left
    col1, col2, col3, _ = st.columns([1, 1, 1, 99])
    
    with col1:
        st.markdown('<div class="nav-item-marker"></div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard")
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings")
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM")

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
