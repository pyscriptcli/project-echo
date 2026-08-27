import streamlit as st

def setup_page_layout():
    """
    Renders an overhauled, premium native sidebar styled with dark luxury tones,
    edge-to-edge hover states, gold SVG icons, and elegant typography.
    """
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Montserrat:wght@400;500;600&display=swap');

    /* 1. HIDE TOP HEADER & NATIVE APP ARTIFACTS */
    header[data-testid="stHeader"], 
    .stApp > header, 
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], 
    #MainMenu, 
    footer,
    [data-testid="stSidebarNav"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* 2. MAIN CONTENT ADJUSTMENTS */
    .block-container {
        padding-top: 2rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }

    /* 3. SIDEBAR CONTAINER OVERHAUL */
    section[data-testid="stSidebar"] {
        background-color: #121315 !important; /* Deepest luxury charcoal */
        border-right: 1px solid rgba(201, 168, 76, 0.15) !important;
        width: 260px !important;
        min-width: 260px !important;
    }

    /* Clean up internal spacing in sidebar */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* 4. BASE LINK STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
        background-color: transparent !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 !important;
        margin: 0 !important;
        padding: 0.85rem 1.5rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        transition: all 0.2s ease !important;
        text-decoration: none !important;
    }

    /* Typography */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"] p {
        font-family: 'Cormorant Garamond', serif !important;
        font-style: italic !important;
        font-size: 1.3rem !important;
        font-weight: 500 !important;
        color: #7A7E85 !important; /* Muted gray for inactive */
        letter-spacing: 0.02em !important;
        line-height: 1 !important;
        transition: color 0.2s ease !important;
    }

    /* 5. HOVER EFFECT */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
        background-color: rgba(255, 255, 255, 0.02) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover span[data-testid="stPageLink-Text"] {
        color: #C9A84C !important;
    }

    /* 6. ACTIVE (SELECTED) TAB STYLING */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"],
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][data-active="true"] {
        background: linear-gradient(90deg, rgba(201, 168, 76, 0.12) 0%, transparent 100%) !important;
        border-left: 3px solid #C9A84C !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"] span[data-testid="stPageLink-Text"] {
        color: #D4AF37 !important;
        font-weight: 700 !important;
    }

    /* 7. HIDE DEFAULT MATERIAL ICONS */
    section[data-testid="stSidebar"] span[data-testid="stIconMaterial"] {
        display: none !important;
    }

    /* 8. PURE SVG ICONS BEFORE TEXT */
    section[data-testid="stSidebar"] a[data-testid="stPageLink"]::before {
        content: "";
        display: inline-block;
        width: 17px;
        height: 17px;
        min-width: 17px;
        margin-right: 14px;
        background-color: #7A7E85; /* Muted icon default */
        flex-shrink: 0 !important;
        transition: background-color 0.2s ease;
    }

    section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover::before,
    section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"]::before {
        background-color: #D4AF37 !important; /* Gold active/hover */
    }

    /* Dashboard SVG */
    section[data-testid="stSidebar"] a[href$="app.py"]::before,
    section[data-testid="stSidebar"] a[href="/"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Meetings SVG */
    section[data-testid="stSidebar"] a[href*="meeting_details"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* MoM SVG */
    section[data-testid="stSidebar"] a[href*="minutes_of_the_meeting"]::before {
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E") no-repeat center;
    }

    /* Custom Scrollbar for sidebar */
    section[data-testid="stSidebar"]::-webkit-scrollbar {
        width: 6px;
    }
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {
        background: rgba(201, 168, 76, 0.3);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Render Native Sidebar Content
    with st.sidebar:
        # Branding Header inside the Sidebar
        st.markdown("""
            <div style="padding: 0 1.5rem 2.5rem 1.5rem;">
                <h2 style="font-family: 'Playfair Display', serif; font-style: italic; color: #D4AF37; margin: 0; font-size: 1.8rem; font-weight: 400; letter-spacing: 0.05em;">Project Echo</h2>
                <p style="font-family: 'Montserrat', sans-serif; color: #7A7E85; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.15em; text-transform: uppercase; margin: 0.2rem 0 0 0;">Executive Hub</p>
            </div>
        """, unsafe_allow_html=True)

        # Main Navigation Links
        st.page_link("app.py", label="Dashboard")
        st.page_link("pages/2_meeting_details.py", label="Meetings")
        st.page_link("pages/1_minutes_of_the_meeting.py", label="MoM")

# Compatibility aliases
single_page_layout = setup_page_layout
render_custom_sidebar = setup_page_layout
