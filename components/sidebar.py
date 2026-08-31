# components/sidebar.py
"""
Project Echo — Global Sidebar Navigation (Streamlit 1.62 compatible)

Native Streamlit sidebar + custom branding & compact navigation.
- Brand block: "Echo" in Cormorant Garamond italic
- Compact nav via st.page_link with material icons
- Active page: gold left border + tinted background (via aria-current)
- Footer pinned to bottom: user chip (initials + username) + gold pill Sign Out
- Non-collapsible: collapse/expand controls are hidden AND the sidebar
  is force-locked open via CSS, making collapse visually impossible.
- Noticeable drop shadow for separation from main content
- Subtle deep charcoal & gold gradient overlay (opacity 5%)
"""

import re
import streamlit as st

from utils.auth import get_current_user, logout


# ---------------------------------------------------------------------------
# Navigation model
# ---------------------------------------------------------------------------
NAV_ITEMS = [
    ("app.py", "Dashboard", ":material/dashboard:"),
    ("pages/3_echo_ai.py", "Ask Echo.ai", ":material/smart_toy:"),
    ("pages/4_tasks.py", "Tasks & Calendar", ":material/calendar_month:"),
    ("pages/2_meeting_details.py", "Meetings", ":material/menu_book:"),
    ("pages/1_minutes_of_the_meeting.py", "Minutes of the Meeting", ":material/edit_note:"),
]


SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Inter:wght@400;500;600;700&display=swap');

/* ---------------- Hide app chrome (header kept alive, zero-height) ---------------- */
header[data-testid="stHeader"],
.stApp > header {
    background: transparent !important;
    height: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important;
}
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"],
[data-testid="stToolbar"],
#MainMenu,
footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* Hide Streamlit's auto-generated page list */
[data-testid="stSidebarNav"] { display: none !important; }

/* ---------------- Collapse prevention: hide ALL collapse/expand controls ---------------- */
/* Catch the collapse button in any version — it's a <button> wrapping a material icon */
section[data-testid="stSidebar"] button:has(span[data-testid="stIconMaterial"]),
/* Also hide the sidebar header's buttons (1.62 places the control there) */
[data-testid="stSidebarHeader"] button,
/* Hide the collapsed-state expand control (any version) */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
/* Kill the resize drag-handle entirely (1.62+) */
[data-testid="stSidebarResizeHandle"],
[data-testid="stSidebarResizeControl"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    pointer-events: none !important;
}

/* ---------------- Force-open lock: sidebar cannot visually collapse ---------------- */
/* Even if Streamlit's JS sets the collapsed state, these !important rules
   override both emotion classes and inline styles. */
section[data-testid="stSidebar"] {
    display: flex !important;
    flex-direction: column !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    min-width: 250px !important;
    width: 250px !important;
    max-width: 250px !important;
    pointer-events: auto !important;
}

/* ---------------- Main content breathing room ---------------- */
.block-container {
    padding-top: 1.5rem !important;
    padding-left: 2.2rem !important;
    padding-right: 2.2rem !important;
    max-width: 100% !important;
}

/* ---------------- Sidebar shell ---------------- */
section[data-testid="stSidebar"] {
    /* Base background + subtle deep charcoal & gold gradient overlay */
    background: linear-gradient(
        180deg,
        rgba(26, 43, 76, 0.05) 0%,
        rgba(212, 175, 55, 0.05) 100%
    ), #F5F1E8 !important;
    border-right: 1px solid rgba(0, 0, 0, 0.06) !important;
    /* Noticeable drop shadow for separation */
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.1), 2px 0 6px rgba(0, 0, 0, 0.05) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    height: 100%;
    display: flex;
    flex-direction: column;
    padding: 1.15rem 0.9rem 1rem 0.9rem !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > [data-testid="stVerticalBlock"] {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    gap: 0.25rem !important;
}

/* ---------------- Brand block ---------------- */
.sb-brand {
    font-family: 'Cormorant Garamond', 'Playfair Display', serif;
    font-style: italic;
    font-weight: 600;
    font-size: 2rem;
    line-height: 1;
    color: #1A2B4C;
    letter-spacing: 0.01em;
}
.sb-brand-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: #6C727A;
    margin-top: 3px;
}
.sb-brand-rule {
    height: 1px;
    margin: 0.85rem 0 0.9rem 0;
    background: linear-gradient(to right, rgba(212, 175, 55, 0.55), rgba(0, 0, 0, 0.05));
}

/* ---------------- Nav links (st.page_link) ---------------- */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {
    margin: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    border-radius: 6px !important;
    padding: 6px 10px !important;
    border-left: 3px solid transparent !important;
    color: #24344F !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a p {
    margin: 0 !important;
    font-size: 0.83rem !important;
    color: inherit !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    background: rgba(0, 0, 0, 0.045) !important;
    color: #111A2B !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"][aria-current="page"] a,
section[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    background: rgba(212, 175, 55, 0.12) !important;
    border-left-color: #D4AF37 !important;
    color: #111A2B !important;
    font-weight: 600 !important;
}

/* ---------------- Footer (pinned to bottom, separate container) ---------------- */
/* The footer container is marked with .sb-footer-scope and is placed in its own
   st.container() to ensure it sits at the bottom of the flex column. */
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-footer-scope) {
    margin-top: auto !important;
    flex-shrink: 0 !important;  /* Prevent shrinking */
}
.sb-footer-scope { display: none !important; }

.sb-user-wrap {
    border-top: 1px solid rgba(0, 0, 0, 0.07);
    padding-top: 0.8rem;
    margin-top: 0.9rem;
    margin-bottom: 0.55rem;
}
.sb-user {
    display: flex;
    align-items: center;
    gap: 9px;
    min-width: 0;
    margin-bottom: 0.55rem;
}
.sb-user-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #111A2B;
    color: #D4AF37;
    border: 1px solid rgba(212, 175, 55, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    flex-shrink: 0;
}
.sb-user-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: #1A2B4C;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Sign Out — gold-bordered pill, full width */
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-footer-scope) button {
    background: transparent !important;
    color: #8C6D23 !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 999px !important;
    height: 32px !important;
    min-height: 32px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.74rem !important;
    font-weight: 600 !important;
    box-shadow: none !important;
    transition: background 0.15s ease, color 0.15s ease;
}
section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-footer-scope) button:hover {
    background: rgba(212, 175, 55, 0.14) !important;
    color: #6B5313 !important;
}
</style>
"""


def _initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s._\-]+", (name or "").strip()) if p]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    return (name or "—")[:2].upper()


def setup_page_layout():
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(
            '<div class="sb-brand">Echo</div>'
            '<div class="sb-brand-sub">AI Assistant</div>'
            '<div class="sb-brand-rule"></div>',
            unsafe_allow_html=True,
        )

        for path, label, icon in NAV_ITEMS:
            st.page_link(path, label=label, icon=icon, use_container_width=True)

        # Footer in its own container, pinned to bottom via CSS
        user = get_current_user()
        with st.container():
            # Marker span for CSS :has() selector to target this container
            st.markdown('<span class="sb-footer-scope"></span>', unsafe_allow_html=True)

            if user:
                username = str(user.get("username", "user"))
                st.markdown(
                    f'<div class="sb-user-wrap">'
                    f'<div class="sb-user">'
                    f'<span class="sb-user-avatar">{_initials(username)}</span>'
                    f'<span class="sb-user-name">{username}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Sign Out", key="sb_logout", use_container_width=True):
                    logout()
                    st.rerun()
            else:
                st.markdown(
                    '<div class="sb-user-wrap">'
                    '<div class="sb-user">'
                    '<span class="sb-user-avatar">—</span>'
                    '<span class="sb-user-name">Guest</span>'
                    '</div></div>',
                    unsafe_allow_html=True,
                )
