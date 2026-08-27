# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a premium, luxury dark top bar with pure text (Cormorant Garamond italic)
    in gold, without any icons, completely hiding the native sidebar.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Montserrat:wght@400;500;600&display=swap');

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

    /* 3. LUXURY TOPBAR CONTAINER */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) {
        background: #171819 !important;
        border: 1px solid rgba(201, 168, 76, 0.25) !important;
        border-radius: 10px !important;
        padding: 6px 16px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.25) !important;
        margin-bottom: 2rem !important;
        align-items: center !important;
        width: 100% !important;
        display: flex !important;
        gap: 0.5rem !important;
    }

    /* Remove column spacing inside the navbar */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) [data-testid="column"] {
        width: auto !important;
        flex: 0 1 auto !important;
        min-width: fit-content !important;
    }

    /* 4. BASE LINK STYLING */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[data-testid="stPageLink"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) div[data-testid="stPageLink"] > a {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 6px !important;
        height: 36px !important;
        padding: 0 16px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }

    /* Typography - Set to Gold */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a p,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.35rem !important; /* Slightly larger to compensate for no icons */
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.04em !important;
        line-height: 1 !important;
        transition: color 0.2s ease !important;
    }

    /* 5. HOVER EFFECT */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover {
        background-color: rgba(201, 168, 76, 0.08) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover span,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover p {
        color: #F0DFC0 !important; /* Lighter bright gold on hover */
    }

    /* 6. ACTIVE SELECTED TAB */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[data-active="true"] {
        background: linear-gradient(180deg, rgba(201, 168, 76, 0.15) 0%, transparent 100%) !important;
        border: 1px solid rgba(201, 168, 76, 0.5) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"] span,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"] p {
        color: #D4AF37 !important; /* Vivid active gold */
        font-weight: 700 !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICONS AND ANY RESIDUAL SVG BEFORE BLOCKS */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) span[data-testid="stIconMaterial"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a::before {
        display: none !important;
        content: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Topbar Layout (Left-aligned links with a flex container)
    col1, col2, col3, _ = st.columns([1.5, 1.5, 1.5, 6.0])
    
    with col1:
        st.markdown('<div class="nav-item-marker"></div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM", use_container_width=True)

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
