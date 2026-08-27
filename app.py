# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a minimalist, purely left-aligned text navigation bar. 
    Completely overrides Streamlit's column grid to shrink-wrap the links to the left.
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

    /* 3. MINIMALIST TOPBAR CONTAINER - FORCED LEFT ALIGNMENT */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 2.5rem !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important; /* Locks contents to the extreme left */
        align-items: center !important;
        width: 100% !important;
        gap: 2rem !important; /* Exact spacing between the words */
    }

    /* Nuke Streamlit's Native Column Widths - Force Shrink-Wrap */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) > div[data-testid="column"] {
        width: max-content !important;
        min-width: 0 !important;
        max-width: max-content !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* 4. BASE LINK STYLING (Pure Text) */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[data-testid="stPageLink"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) div[data-testid="stPageLink"] > a {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        height: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        box-shadow: none !important;
    }

    /* Typography - Base Gold */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a p,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.45rem !important;
        font-weight: 500 !important;
        color: #B59345 !important;
        letter-spacing: 0.02em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        transition: color 0.2s ease !important;
    }

    /* 5. HOVER EFFECT */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover {
        background-color: transparent !important;
    }

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
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) span[data-testid="stIconMaterial"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a::before {
        display: none !important;
        content: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Topbar Layout
    # Using tiny fractional widths; CSS takes over to shrink-wrap them to the text length
    col1, col2, col3, _ = st.columns([0.01, 0.01, 0.01, 0.97])
    
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
