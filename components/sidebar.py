# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a compact mini-sidebar (icon-only by default, expands with labels on hover)
    styled with dark charcoal, gold SVG icons, and Cormorant Garamond italic typography.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Montserrat:wght@400;500;600&display=swap');

    /* 1. HIDE TOP HEADER, DECORATION, AND COLLAPSE ARROWS */
    header[data-testid="stHeader"], 
    .stApp > header, 
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], 
    #MainMenu, 
    footer,
    button[data-testid="stSidebarCollapseButton"], 
    button[data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* 2. RECLAIM PAGE PADDING & OFFSET FOR MINI-RAIL */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. MINI-SIDEBAR EXPANDABLE RAIL */
    section[data-testid="stSidebar"] {
        background-color: #171819 !important;
        border-right: 1px solid rgba(201, 168, 76, 0.25) !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.4) !important;
        width: 68px !important;
        min-width: 68px !important;
        max-width: 68px !important;
        transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-x: hidden !important;
        z-index: 999999 !important;
        position: fixed !important;
        height: 100vh !important;
    }

    /* Expand sidebar width on hover */
    section[data-testid="stSidebar"]:hover {
        width: 220px !important;
        max-width: 220px !important;
        box-shadow: 8px 0 28px rgba(0, 0, 0, 0.6) !important;
    }

    /* Content container adjustments */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem !important;
        padding-left: 10px !important;
        padding-right: 10px !important;
        width: 220px !important;
    }

    /* 4. BASE LINK STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 0 !important;
        height: 46px !important;
        min-height: 46px !important;
        width: 46px !important;
        margin-bottom: 0.75rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-decoration: none !important;
        overflow: hidden !important;
    }

    /* Expand button container width on hover */
    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"] {
        width: 100% !important;
        padding: 0 12px !important;
    }

    /* 5. TYPOGRAPHY: HIDDEN BY DEFAULT, FADES IN ON HOVER */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.22rem !important;
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.03em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        opacity: 0 !important;
        transform: translateX(-8px) !important;
        transition: opacity 0.2s ease, transform 0.2s ease !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"] p {
        opacity: 1 !important;
        transform: translateX(0) !important;
        pointer-events: auto !important;
    }

    /* 6. HOVER STATE PER ITEM */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
        background-color: rgba(201, 168, 76, 0.14) !important;
        border-color: rgba(201, 168, 76, 0.4) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover span[data-testid="stPageLink-Text"] {
        color: #F3E4C6 !important;
    }

    /* 7. ACTIVE (SELECTED) TAB STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][data-active="true"] {
        background: linear-gradient(90deg, rgba(201, 168, 76, 0.28) 0%, rgba(201, 168, 76, 0.08) 100%) !important;
        border: 1px solid #C9A84C !important;
        box-shadow: 0 0 14px rgba(201, 168, 76, 0.25) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"] span[data-testid="stPageLink-Text"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.6) !important;
    }

    /* 8. HIDE DEFAULT MATERIAL ICONS */
    section[data-testid="stSidebar"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 9. PURE SVG ICONS VIA CSS MASKS */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        min-width: 20px;
        margin-left: 12px;
        margin-right: 14px;
        background-color: #C9A84C;
        flex-shrink: 0 !important;
        transition: background-color 0.25s ease;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover::before {
        background-color: #F3E4C6;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"]::before {
        background-color: #FFFFFF !important;
    }

    /* Dashboard SVG (Matrix Grid) */
    section[data-testid="stSidebar"] a[href$="app.py"]::before,
    section[data-testid="stSidebar"] a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings SVG (Calendar Agenda) */
    section[data-testid="stSidebar"] a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* MoM SVG (Document / Notes) */
    section[data-testid="stSidebar"] a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # 10. RENDER NAVIGATION INSIDE ST.SIDEBAR
    with st.sidebar:
        st.page_link("app.py", label="Dashboard", use_container_width=True)
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM", use_container_width=True)

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
