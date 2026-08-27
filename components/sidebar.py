# In components/sidebar.py
import streamlit as st

def setup_page_layout():
    """
    Renders a persistent luxury sidebar navigation with Cormorant Garamond italic labels,
    pure SVG icons, and a hidden top header.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Montserrat:wght@400;500;600&display=swap');

    /* 1. HIDE TOP HEADER, DECORATION & DEFAULT MENUS ONLY */
    header[data-testid="stHeader"], 
    .stApp > header, 
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], 
    #MainMenu, 
    footer {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* 2. RECLAIM PAGE TOP PADDING */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. PERSISTENT LUXURY SIDEBAR CONTAINER */
    section[data-testid="stSidebar"] {
        background-color: #171819 !important;
        border-right: 1px solid rgba(201, 168, 76, 0.25) !important;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.35) !important;
        width: 250px !important;
        min-width: 250px !important;
    }

    /* Hide native multi-page navigation links to avoid duplication */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Sidebar Content Wrapper Padding */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* 4. BASE SIDEBAR LINK STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 8px !important;
        padding: 0.65rem 1rem !important;
        margin-bottom: 0.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.22s ease !important;
        text-decoration: none !important;
    }

    /* Typography */
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
    }

    /* 5. HOVER EFFECT */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
        background-color: rgba(201, 168, 76, 0.12) !important;
        border-color: rgba(201, 168, 76, 0.35) !important;
        transform: translateX(3px) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover span[data-testid="stPageLink-Text"] {
        color: #F2E4C4 !important;
    }

    /* 6. ACTIVE (SELECTED) TAB STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][data-active="true"] {
        background: linear-gradient(90deg, rgba(201, 168, 76, 0.22) 0%, rgba(201, 168, 76, 0.05) 100%) !important;
        border-left: 3px solid #C9A84C !important;
        border-top: 1px solid rgba(201, 168, 76, 0.3) !important;
        border-right: 1px solid rgba(201, 168, 76, 0.3) !important;
        border-bottom: 1px solid rgba(201, 168, 76, 0.3) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"] span[data-testid="stPageLink-Text"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICONS */
    section[data-testid="stSidebar"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 8. PURE SVG ICONS BEFORE LINK LABELS */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 16px;
        height: 16px;
        margin-right: 10px;
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

    /* Dashboard Icon (Grid / Matrix) */
    section[data-testid="stSidebar"] a[href$="app.py"]::before,
    section[data-testid="stSidebar"] a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings Icon (Calendar Agenda) */
    section[data-testid="stSidebar"] a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* MoM Icon (Document / Notes) */
    section[data-testid="stSidebar"] a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # 5. Render Navigation Directly Inside st.sidebar
    with st.sidebar:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard", use_container_width=True)
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM", use_container_width=True)

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
