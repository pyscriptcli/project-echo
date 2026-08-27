# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """Hides default UI elements and renders the custom horizontal navbar with Cormorant Garamond italic labels and custom SVG icons."""
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

    /* 2. RECLAIM PAGE WIDTH & ALIGNMENT */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. CUSTOM NAVBAR CONTAINER */
    div[data-testid="stHorizontalBlock"]:has(a[data-testid="stPageLink"]) {
        background-color: #272828 !important;
        padding: 0.5rem 1.25rem !important;
        border-radius: 12px !important;
        border: 1px solid rgba(201, 168, 76, 0.25) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
        margin-bottom: 1.5rem !important;
        align-items: center !important;
        gap: 0.75rem !important;
    }

    /* 4. BASE LINK STYLING (Cormorant Garamond Italic) */
    a[data-testid="stPageLink"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 50px !important;
        height: 38px !important;
        padding: 0 1.15rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.25s ease !important;
        text-decoration: none !important;
    }

    a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.03em !important;
        line-height: 1 !important;
    }

    /* 5. HOVER EFFECT */
    a[data-testid="stPageLink"]:hover {
        background-color: rgba(201, 168, 76, 0.12) !important;
        border-color: rgba(201, 168, 76, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    a[data-testid="stPageLink"]:hover span[data-testid="stPageLink-Text"] {
        color: #E5CF8E !important;
    }

    /* 6. DISTINCT ACTIVE (SELECTED) TAB STYLING */
    a[data-testid="stPageLink"][aria-current="page"] {
        background: linear-gradient(135deg, rgba(201, 168, 76, 0.25), rgba(201, 168, 76, 0.12)) !important;
        border: 1px solid #C9A84C !important;
        box-shadow: 0 0 14px rgba(201, 168, 76, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.1) !important;
    }

    a[data-testid="stPageLink"][aria-current="page"] span[data-testid="stPageLink-Text"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5) !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICON GLYPHS */
    a[data-testid="stPageLink"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 8. PURE SVG ICONS VIA CSS MASKS */
    a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        margin-right: 8px;
        background-color: #C9A84C;
        transition: background-color 0.25s ease;
    }

    a[data-testid="stPageLink"]:hover::before {
        background-color: #E5CF8E;
    }

    a[data-testid="stPageLink"][aria-current="page"]::before {
        background-color: #FFFFFF !important;
    }

    /* Dashboard SVG (Grid layout) */
    a[href$="app.py"]::before, a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings SVG (Calendar / Agenda) */
    a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Minutes of Meeting SVG (Document / Notes) */
    a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render Horizontal Navbar
    col1, col2, col3, _ = st.columns([1.3, 1.3, 2.2, 5.2])
    with col1:
        st.page_link("app.py", label="Dashboard", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", use_container_width=True)
