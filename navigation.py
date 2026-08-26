import streamlit as st

# ==========================================
# 1. PAGE DEFINITIONS & WRAPPERS
# ==========================================
def dashboard_view():
    render_global_navbar()
    st.title("Executive Dashboard")
    st.write("Welcome to the Project Echo Executive Hub.")

def mom_view():
    render_global_navbar()
    st.title("MoM Generator")
    st.write("Generate and review minutes of meetings.")

def meeting_details_view():
    render_global_navbar()
    st.title("Meeting Browser")
    st.write("Search and browse historical meeting records.")

def ask_echo_view():
    render_global_navbar()
    st.title("Ask Echo AI")
    st.write("Direct Q&A assistant for executive insights.")

# Note: You can point to python files directly using: st.Page("pages/1_mom.py", url_path="1_minutes_of_the_meeting")
pages = [
    st.Page(dashboard_view, title="Dashboard", url_path=""),
    st.Page(mom_view, title="MoM Generator", url_path="1_minutes_of_the_meeting"),
    st.Page(meeting_details_view, title="Meeting Browser", url_path="2_meeting_details"),
    st.Page(ask_echo_view, title="Ask Echo", url_path="5_ask_echo"),
]

# ==========================================
# 2. GLOBAL NAVBAR COMPONENT
# ==========================================
def render_global_navbar():
    nav_html = """
    <style>
    /* Remove native sidebar elements */
    section[data-testid="stSidebar"],
    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Content offsets for fixed rail and topbar */
    .block-container {
        padding-top: 5rem !important;
        padding-left: 5.8rem !important;
        padding-right: 2rem !important;
        max-width: 98% !important;
    }

    /* Fixed Topbar Header */
    .echo-topbar-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background-color: #161616;
        border-bottom: 1px solid #333333;
        z-index: 999990;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 0 2rem;
    }

    .echo-title {
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        font-weight: 400 !important;
        font-size: 1.35rem !important;
        color: #FFFFFF !important;
        margin: 0 !important;
    }
    .echo-title span { color: #D4AF37 !important; }

    /* Fixed Left Icon Rail */
    .echo-nav-rail {
        position: fixed;
        top: 60px;
        left: 0;
        bottom: 0;
        width: 68px;
        background-color: #161616;
        border-right: 1px solid #2B2B2B;
        box-shadow: 4px 0 15px rgba(0,0,0,0.2);
        z-index: 999980;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.25rem 0;
        gap: 1.25rem;
    }

    .echo-nav-item {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background-color: #222222;
        border: 1px solid #333333;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #C5A059;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .echo-nav-item svg {
        width: 22px;
        height: 22px;
        stroke: #C5A059;
        fill: none;
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
        transition: all 0.2s ease;
    }

    .echo-nav-item:hover {
        background-color: #D4AF37;
        border-color: #D4AF37;
        transform: translateY(-1px);
    }

    .echo-nav-item:hover svg {
        stroke: #161616;
    }
    </style>

    <!-- Fixed Topbar -->
    <div class="echo-topbar-wrapper">
        <h1 class="echo-title">Project <span>Echo</span> &mdash; Executive Hub</h1>
    </div>

    <!-- Fixed Left Icon Rail -->
    <div class="echo-nav-rail">
        <a href="/" target="_self" class="echo-nav-item" title="Executive Dashboard">
            <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
        </a>
        <a href="/1_minutes_of_the_meeting" target="_self" class="echo-nav-item" title="MoM Generator">
            <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
        </a>
        <a href="/2_meeting_details" target="_self" class="echo-nav-item" title="Meeting Browser">
            <svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
        </a>
        <a href="/5_ask_echo" target="_self" class="echo-nav-item" title="Ask Echo AI">
            <svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8.01" y2="16"></line><line x1="16" y1="16" x2="16.01" y2="16"></line></svg>
        </a>
    </div>
    """
    st.markdown(nav_html, unsafe_allow_html=True)

# ==========================================
# 3. ROUTER INITIALIZATION
# ==========================================
pg = st.navigation(pages, position="hidden")
pg.run()
