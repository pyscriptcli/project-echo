# In components/navigation.py (or components/sidebar.py)
import streamlit as st

def render_global_navigation():
    """
    Renders an ultra-minimalist, pure-text top bar navigation with no SVG icons.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&display=swap');

    /* 1. HIDE DEFAULT STREAMLIT HEADER, FOOTER, & SIDEBAR */
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
        padding-top: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }

    /* 3. STRICTLY ELIMINATE ALL SVG ICONS & WRAPPERS */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) svg,
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) span[data-testid="stIconMaterial"],
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) [data-testid="stPageLink-Icon"] {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 4. TOP BAR ROW CONTAINER (Left-Aligned, Tight-Fit) */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin-bottom: 2.5rem !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-start !important;
        align-items: center !important;
        width: 100% !important;
        gap: 3rem !important;
    }

    /* Auto-width columns to wrap text tightly */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) > div[data-testid="column"] {
        width: auto !important;
        min-width: 0 !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
    }

    /* 5. PURE TEXT LINK STYLING */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) a {
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

    /* Typography - Refined Muted Gold */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) a span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) a p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.35rem !important;
        font-weight: 500 !important;
        color: #A89060 !important;
        letter-spacing: 0.04em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        transition: color 0.2s ease !important;
    }

    /* Hover State */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) a:hover span[data-testid="stPageLink-Text"],
    div[data-testid="top-nav-marker"] a:hover p {
        color: #F1D483 !important;
    }

    /* Active / Current Page State */
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) a[aria-current="page"] span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.top-nav-marker) a[data-active="true"] span[data-testid="stPageLink-Text"] {
        color: #E2BC5A !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
