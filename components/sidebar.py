import streamlit as st

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="Project Echo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Hide Topbar, Main Menu, Native Sidebar & Reset Padding
st.markdown("""
<style>
/* 1. HIDE THE TOP BAR (HEADER) */
.stApp > header {
    display: none !important;
    visibility: hidden !important;
}

/* 2. HIDE THE THREE-DOT MAIN MENU */
#MainMenu {
    visibility: hidden !important;
}

/* 3. HIDE THE NATIVE SIDEBAR COMPLETELY */
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNav"] {
    display: none !important;
    visibility: hidden !important;
}

/* 4. ADJUST MAIN CONTENT PADDING */
.block-container {
    padding-top: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

/* 5. OPTIONAL: HORIZONTAL NAVBAR SPACING & STYLE */
div[data-testid="stHorizontalBlock"]:has(a[data-testid="stPageLink"]) {
    gap: 0.75rem !important;
    margin-bottom: 1.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Horizontal Custom Navigation Bar
def render_custom_navbar():
    col1, col2, col3, _ = st.columns([1.2, 1.2, 2.0, 5.6])
    
    with col1:
        st.page_link("app.py", label="Dashboard", icon=":material/dashboard:", use_container_width=True)
    with col2:
        st.page_link("pages/2_meeting_details.py", label="Meetings", icon=":material/menu_book:", use_container_width=True)
    with col3:
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Minutes of the Meeting", icon=":material/edit_note:", use_container_width=True)

# Render Navbar at the top of your page
render_custom_navbar()
