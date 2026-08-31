# components/sidebar.py
"""
Project Echo — Global Sidebar Navigation (Non-collapsible)

Native Streamlit sidebar + custom branding & grouped navigation.
- Brand block: "Echo" in Cormorant Garamond italic (no logo image)
- Nav: Dashboard first, then Ask Echo.ai
- Active page: gold left border + tinted background (via aria-current)
- Footer pinned to bottom: user chip (initials + username) + gold pill Sign Out
- No collapse: all collapse controls are hidden and sidebar is fixed open.

Design rules:
- No DOM restructuring, styling-only CSS (scoped to [data-testid="stSidebar"])
- The auto-generated multipage nav ([data-testid="stSidebarNav"]) is hidden
  so our custom links are the single source of navigation.
- Sidebar cannot be collapsed; collapse/expand controls are hidden entirely.
"""

import re
import streamlit as st

from utils.auth import get_current_user, logout


def _get_initials(name: str) -> str:
    """Return up to two initials from a full name."""
    if not name:
        return "??"
    parts = [p for p in name.strip().split() if p]
    if not parts:
        return "??"
    if len(parts) == 1:
        return parts[0][0].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def render_sidebar():
    """Render the custom non-collapsible sidebar."""
    user = get_current_user()
    username = user.get("name") if isinstance(user, dict) else getattr(user, "name", None)
    if not username:
        username = "User"
    initials = _get_initials(username)

    st.markdown("""
    <style>
    /* Hide Streamlit auto-generated multipage nav and all collapse controls */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapsedControl"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Sidebar base */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #2b3138;
        padding: 1.5rem 1rem;
    }

    /* Brand */
    .echo-brand {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 2rem;
        font-weight: 500;
        color: #e6c200;
        margin-bottom: 2rem;
        padding-left: 0.25rem;
        letter-spacing: 0.5px;
    }

    /* Custom nav links (all sidebar page_link anchors) */
    section[data-testid="stSidebar"] a {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        width: 100%;
        box-sizing: border-box;
        padding: 0.625rem 0.875rem;
        margin-bottom: 0.25rem;
        color: #c9d1d9;
        text-decoration: none;
        border-radius: 8px;
        border-left: 3px solid transparent;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    }
    section[data-testid="stSidebar"] a:hover {
        background-color: #161b22;
        color: #f0f6fc;
    }
    section[data-testid="stSidebar"] a[aria-current="page"] {
        background-color: rgba(230, 194, 0, 0.08);
        border-left-color: #e6c200;
        color: #f0e6c8;
    }

    /* Footer pinned to bottom of sidebar */
    .st-key-sidebar_footer {
        position: sticky;
        bottom: 0;
        background-color: #0d1117;
        padding: 1rem 0 0.5rem 0;
        border-top: 1px solid #2b3138;
        margin-top: 1rem;
        z-index: 10;
    }
    .user-chip {
        display: flex;
        align-items: center;
        gap: 0.625rem;
        margin-bottom: 0.75rem;
        color: #c9d1d9;
    }
    .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #21262d;
        border: 1px solid #30363d;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
        color: #e6c200;
    }
    .st-key-sidebar_footer .stButton > button {
        width: 100%;
        background-color: #e6c200;
        color: #0d1117;
        border: none;
        border-radius: 999px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: background-color 0.2s ease;
    }
    .st-key-sidebar_footer .stButton > button:hover {
        background-color: #d4b100;
        color: #0d1117;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="echo-brand">Echo</div>', unsafe_allow_html=True)

        # Navigation order: Dashboard first, then Ask Echo.ai
        st.page_link("app.py", label="Dashboard", icon=":material/dashboard:")
        st.page_link("pages/Ask_Echo.py", label="Ask Echo.ai", icon=":material/chat:")

        # Footer pinned to bottom
        with st.container(key="sidebar_footer"):
            st.markdown(
                f"""
                <div class="user-chip">
                    <span class="user-avatar">{initials}</span>
                    <span>{username}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Sign Out", key="sign_out", use_container_width=True):
                logout()
