# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a streamlined topbar navigation where buttons auto-fit their content,
    styled in luxury dark charcoal, Cormorant Garamond italic typography, and gold accents.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Montserrat:wght@400;500;600;700&display=swap');

    /* 1. HIDE ALL DEFAULT STREAMLIT HEADERS & SIDEBARS */
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
        padding-top: 1rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. NAVBAR CAPSULE WRAPPER (Auto-sized, flex layout) */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) {
        display: inline-flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        justify-content: flex-start !important;
        background: #171819 !important;
        border: 1px solid rgba(201, 168, 76, 0.28) !important;
        border-radius: 8px !important;
        padding: 4px 8px !important;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35) !important;
        margin-bottom: 1.5rem !important;
        width: auto !important;
        min-width: 480px !important;
        max-width: 100% !important;
        gap: 4px !important;
    }

    /* Remove column bounding constraints inside navbar */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) > div[data-testid="column"] {
        width: auto !important;
        min-width: unset !important;
        flex: 0 0 auto !important;
    }

    /* 4. NAVBAR BUTTON LINKS */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"] {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 6px !important;
        height: 32px !important;
        min-height: 32px !important;
        padding: 0 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-decoration: none !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: nowrap !important;
    }

    /* Cormorant Garamond Italic Typography */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"] span,
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"] p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.03em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
    }

    /* 5. HOVER STATE */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"]:hover {
        background-color: rgba(201, 168, 76, 0.12) !important;
        border-color: rgba(201, 168, 76, 0.35) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"]:hover span,
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"]:hover p {
        color: #F3E2B8 !important;
    }

    /* 6. ACTIVE SELECTED TAB */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"][aria-current="page"] {
        background: linear-gradient(180deg, rgba(201, 168, 76, 0.24) 0%, rgba(201, 168, 76, 0.08) 100%) !important;
        border: 1px solid rgba(201, 168, 76, 0.65) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 2px 8px rgba(0, 0, 0, 0.4) !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"][aria-current="page"] span,
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"][aria-current="page"] p {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.7) !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICONS */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 8. PURE SVG ICONS BEFORE LINK TEXT */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 15px;
        height: 15px;
        margin-right: 8px;
        background-color: #C9A84C;
        flex-shrink: 0 !important;
        transition: background-color 0.2s ease;
    }

    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"]:hover::before {
        background-color: #F3E2B8;
    }

    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[data-testid="stPageLink"][aria-current="page"]::before {
        background-color: #FFFFFF !important;
    }

    /* Dashboard SVG Icon */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[href$="app.py"]::before,
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings SVG Icon */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Minutes of Meeting SVG Icon */
    div[data-testid="stHorizontalBlock"]:has(.nav-anchor-point) a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # 4 Columns: 3 links + 1 tiny anchor column
    c1, c2, c3, c_anchor = st.columns([1, 1, 1, 0.01])
    with c1:
        st.page_link("app.py", label="Dashboard", use_container_width=True)
    with c2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
    with c3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", use_container_width=True)
    with c_anchor:
        st.markdown('<div class="nav-anchor-point"></div>', unsafe_allow_html=True)

# Backwards compatibility alias
setup_page_layout = single_page_layout
