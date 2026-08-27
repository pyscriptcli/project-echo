# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a true flush edge-to-edge luxury top bar spanning the full screen
    without top or side padding gaps.
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

    /* 2. REMOVE CONTAINER PADDING TO MAKE FLUSH TOP BAR */
    .block-container {
        padding-top: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }

    /* 3. FLUSH EDGE-TO-EDGE TOPBAR CONTAINER */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) {
        background: #171819 !important;
        border-bottom: 1px solid rgba(201, 168, 76, 0.35) !important;
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
        border-radius: 0 !important;
        padding: 0.65rem 2.5rem !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35) !important;
        margin-top: 0 !important;
        margin-bottom: 1.8rem !important;
        align-items: center !important;
        width: 100% !important;
        display: flex !important;
        gap: 0.5rem !important;
    }

    /* Add normal page padding back to the rest of the page components */
    div[data-testid="stVerticalBlock"] > div:not(:has(div.nav-item-marker)) {
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
    }

    /* 4. BASE LINK STYLING */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) [data-testid="column"] {
        width: auto !important;
        flex: 0 1 auto !important;
        min-width: fit-content !important;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[data-testid="stPageLink"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) div[data-testid="stPageLink"] > a {
        background-color: transparent !important;
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 6px !important;
        height: 34px !important;
        min-height: 34px !important;
        padding: 0 16px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }

    /* Typography */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span[data-testid="stPageLink-Text"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a p,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a span {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.22rem !important;
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.04em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }

    /* 5. HOVER EFFECT */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover {
        background-color: rgba(201, 168, 76, 0.12) !important;
        border-color: rgba(201, 168, 76, 0.35) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover span,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover p {
        color: #F0DFC0 !important;
    }

    /* 6. ACTIVE SELECTED TAB */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"],
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[data-active="true"] {
        background: linear-gradient(180deg, rgba(201, 168, 76, 0.25) 0%, rgba(201, 168, 76, 0.08) 100%) !important;
        border: 1px solid rgba(201, 168, 76, 0.6) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"] span,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICONS */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 8. PURE SVG ICONS BEFORE TEXT */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 8px;
        background-color: #C9A84C;
        flex-shrink: 0 !important;
        transition: background-color 0.2s ease;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a:hover::before {
        background-color: #F0DFC0;
    }

    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[aria-current="page"]::before {
        background-color: #FFFFFF !important;
    }

    /* Dashboard Icon */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[href*="app"]::before,
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings Icon */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Minutes of Meeting Icon */
    div[data-testid="stHorizontalBlock"]:has(div.nav-item-marker) a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Edge-to-edge balanced column structure
    col1, col2, col3, _ = st.columns([1.6, 1.5, 2.8, 6.1])
    with col1:
        st.markdown('<div class="nav-item-marker"></div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", use_container_width=True)

# Compatibility alias
single_page_layout = setup_page_layout
