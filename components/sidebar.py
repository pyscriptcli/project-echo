import streamlit as st

def setup_page_layout():
    """
    Renders an ultra-compact, premium top bar with luxury dark styling,
    gold typography, vertical separators, and SVG icons.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Montserrat:wght@400;500;600;700&display=swap');

    /* 1. HIDE DEFAULT STREAMLIT UI */
    header[data-testid="stHeader"], .stApp > header, [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], #MainMenu, footer,
    section[data-testid="stSidebar"], [data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"], button[data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }

    /* 2. RECLAIM PAGE TOP OFFSET */
    .block-container {
        padding-top: 0.85rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. SLEEK LUXURY TOPBAR CONTAINER */
    div[data-testid="stHorizontalBlock"]:has(a[data-testid="stPageLink"]) {
        background: #171819 !important;
        border: 1px solid rgba(201, 168, 76, 0.22) !important;
        border-radius: 8px !important;
        padding: 0.25rem 0.6rem !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), 0 1px 3px rgba(0, 0, 0, 0.2) !important;
        margin-bottom: 1.25rem !important;
        align-items: center !important;
        gap: 0.2rem !important;
        width: fit-content !important;
    }

    /* 4. BASE LINK STYLING */
    a[data-testid="stPageLink"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 5px !important;
        height: 28px !important;
        min-height: 28px !important;
        padding: 0 0.85rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-decoration: none !important;
        position: relative !important;
    }

    /* Vertical Divider between links */
    a[data-testid="stPageLink"]:not(:last-child)::after {
        content: "";
        position: absolute;
        right: -0.15rem;
        top: 25%;
        height: 50%;
        width: 1px;
        background: rgba(201, 168, 76, 0.18);
    }

    a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #C9A84C !important;
        letter-spacing: 0.04em !important;
        line-height: 1 !important;
        white-space: nowrap !important;
        transition: color 0.2s ease !important;
    }

    /* 5. HOVER EFFECT */
    a[data-testid="stPageLink"]:hover {
        background-color: rgba(201, 168, 76, 0.08) !important;
        border-color: rgba(201, 168, 76, 0.25) !important;
    }
    
    a[data-testid="stPageLink"]:hover span[data-testid="stPageLink-Text"] {
        color: #E8D39B !important;
    }

    /* 6. DISTINCT ACTIVE (SELECTED) TAB */
    a[data-testid="stPageLink"][aria-current="page"] {
        background: linear-gradient(180deg, rgba(201, 168, 76, 0.2) 0%, rgba(201, 168, 76, 0.08) 100%) !important;
        border: 1px solid rgba(201, 168, 76, 0.6) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    a[data-testid="stPageLink"][aria-current="page"] span[data-testid="stPageLink-Text"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6) !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICON GLYPHS */
    a[data-testid="stPageLink"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 8. PURE SVG ICONS VIA CSS MASKS (Compact 14px) */
    a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 14px;
        height: 14px;
        margin-right: 6px;
        background-color: #C9A84C;
        transition: background-color 0.2s ease;
        flex-shrink: 0 !important;
    }

    a[data-testid="stPageLink"]:hover::before {
        background-color: #E8D39B;
    }

    a[data-testid="stPageLink"][aria-current="page"]::before {
        background-color: #FFFFFF !important;
    }

    /* Dashboard Icon (Grid / Matrix) */
    a[href$="app.py"]::before, a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings Icon (Agenda / Calendar) */
    a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Minutes of Meeting Icon (Document / Quill) */
    a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }
    </style>
    """, unsafe_allow_html=True)

    # Tight Column layout hugging the top-left edge
    col1, col2, col3, _ = st.columns([1.0, 1.0, 1.45, 6.55])
    with col1:
        st.page_link("app.py", label="Dashboard", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", use_container_width=True)
