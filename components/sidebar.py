# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a fixed mini-sidebar icon rail (64px) that expands smoothly on hover (220px),
    styled with luxury dark tones, gold SVG icons, and Cormorant Garamond italic labels.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&display=swap');

    /* 1. HIDE ALL DEFAULT STREAMLIT HEADER & COLLAPSE CONTROLS */
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

    /* 2. MAIN CONTENT OFFSET: Push content to the right so sidebar never overlaps */
    .stApp {
        padding-left: 64px !important;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. FIXED MINI-SIDEBAR RAIL */
    section[data-testid="stSidebar"] {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        height: 100vh !important;
        width: 64px !important;
        min-width: 64px !important;
        max-width: 64px !important;
        background-color: #171819 !important;
        border-right: 1px solid rgba(201, 168, 76, 0.25) !important;
        box-shadow: 4px 0 18px rgba(0, 0, 0, 0.45) !important;
        transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1), max-width 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow: hidden !important;
        z-index: 999999 !important;
    }

    /* EXPAND ON HOVER */
    section[data-testid="stSidebar"]:hover {
        width: 220px !important;
        min-width: 220px !important;
        max-width: 220px !important;
        box-shadow: 12px 0 32px rgba(0, 0, 0, 0.65) !important;
    }

    /* Override Streamlit inner sidebar wrappers */
    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"],
    section[data-testid="stSidebar"] > div:first-child {
        width: 220px !important;
        min-width: 220px !important;
        padding: 1.5rem 0.5rem 0 0.5rem !important;
        overflow: hidden !important;
        background: transparent !important;
    }

    /* 4. BASE LINK CONTAINER */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        height: 42px !important;
        min-height: 42px !important;
        width: 48px !important;
        padding: 0 !important;
        margin: 0 0 0.6rem 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-decoration: none !important;
        transition: all 0.22s ease !important;
        overflow: hidden !important;
    }

    /* Expand button width when sidebar is hovered */
    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"] {
        width: 100% !important;
        padding: 0 10px !important;
    }

    /* 5. TYPOGRAPHY: HIDDEN BY DEFAULT, VISIBLE ON HOVER */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.03em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        opacity: 0 !important;
        transform: translateX(-10px) !important;
        transition: opacity 0.2s ease, transform 0.2s ease !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"] p {
        opacity: 1 !important;
        transform: translateX(0) !important;
        pointer-events: auto !important;
    }

    /* 6. HOVER STATE PER BUTTON */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
        background-color: rgba(201, 168, 76, 0.12) !important;
        border-color: rgba(201, 168, 76, 0.35) !important;
    }

    section[data-testid="stSidebar"]:hover a[data-testid="stPageLink"]:hover span[data-testid="stPageLink-Text"] {
        color: #F2E4C4 !important;
    }

    /* 7. ACTIVE (SELECTED) TAB STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][data-active="true"] {
        background: linear-gradient(90deg, rgba(201, 168, 76, 0.25) 0%, rgba(201, 168, 76, 0.08) 100%) !important;
        border: 1px solid rgba(201, 168, 76, 0.6) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"] span[data-testid="stPageLink-Text"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* 8. HIDE DEFAULT MATERIAL ICONS */
    section[data-testid="stSidebar"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 9. PURE SVG ICONS BEFORE TEXT */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 18px;
        height: 18px;
        min-width: 18px;
        margin-left: 14px;
        margin-right: 14px;
        background-color: #C9A84C;
        flex-shrink: 0 !important;
        transition: background-color 0.2s ease;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover::before {
        background-color: #F2E4C4;
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

    /* MoM SVG (Document Notes) */
    section[data-testid="stSidebar"] a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # 10. RENDER PAGE LINKS INSIDE SIDEBAR
    with st.sidebar:
        st.page_link("app.py", label="Dashboard", use_container_width=True)
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM", use_container_width=True)

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
