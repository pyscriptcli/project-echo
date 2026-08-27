import streamlit as st
import datetime
from utils.db import fetch_meeting_archives
from utils.ai import query_global_team_archive

# 1. Page Config (MUST be first Streamlit command)
st.set_page_config(page_title="Project Echo - Executive Hub", layout="wide", initial_sidebar_state="expanded")

# 2. Global State Initialization
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

# 3. Custom CSS - Theming, Fonts, Responsive SVG Sidebar, and Top Bar Removal
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

/* Base Font */
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* Background */
.stApp {
    background-color: #F3EFE6; 
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

/* ================= COMPLETE TOP BAR REMOVAL ================= */
header[data-testid="stHeader"], 
.stApp > header,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

/* Main Content Spacing */
.block-container { 
    padding-top: 1.5rem !important;
    padding-right: 2rem !important;
    padding-left: 2rem !important;
}

/* ================= SIDEBAR STYLING (#272828 & Cormorant Garamond) ================= */
section[data-testid="stSidebar"] {
    background-color: #272828 !important;
    border-right: 1px solid rgba(201, 168, 76, 0.2) !important;
    box-shadow: 4px 0 20px rgba(0, 0, 0, 0.35) !important;
    font-family: 'Cormorant Garamond', serif !important;
}

section[data-testid="stSidebar"] * {
    font-family: 'Cormorant Garamond', serif !important;
}

/* Sidebar Toggle / Collapse Button */
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important; 
    position: absolute !important;
    bottom: 24px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    background-color: #1f2020 !important;
    border: 1px solid #c9a84c !important;
    border-radius: 50% !important;
    color: #c9a84c !important;
    padding: 0 !important;
    margin: 0 !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.25s ease !important;
    z-index: 999999 !important;
}

button[data-testid="stSidebarCollapseButton"]:hover {
    background-color: #c9a84c !important;
    color: #272828 !important;
    box-shadow: 0 0 12px rgba(201, 168, 76, 0.4) !important;
}

button[data-testid="stSidebarCollapseButton"] svg {
    color: #c9a84c !important;
    fill: #c9a84c !important;
}

button[data-testid="stSidebarCollapseButton"]:hover svg {
    color: #272828 !important;
    fill: #272828 !important;
}

/* Nav Item Container */
section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    padding: 1.5rem 0.6rem !important;
    gap: 0.75rem !important;
}

/* Sidebar Page Links (Expanded: Icon + Text) */
section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
    width: 100% !important;
    min-height: 44px !important;
    padding: 0.5rem 0.85rem !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    border-radius: 8px !important;
    background-color: transparent !important;
    border: 1px solid transparent !important;
    color: #c9a84c !important;
    transition: all 0.2s ease !important;
    text-decoration: none !important;
}

section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
    background-color: rgba(201, 168, 76, 0.12) !important;
    border: 1px solid rgba(201, 168, 76, 0.3) !important;
    color: #e5cf8e !important;
}

/* Link Text Styling */
section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] {
    display: inline-block !important;
    font-size: 1.18rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    color: #c9a84c !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Sidebar Custom SVG Icons */
.sidebar-svg {
    width: 20px;
    height: 20px;
    min-width: 20px;
    fill: #c9a84c;
    transition: fill 0.2s ease;
    display: inline-block;
    vertical-align: middle;
}

section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover .sidebar-svg {
    fill: #e5cf8e;
}

/* ================= COLLAPSED BEHAVIOR ================= */
/* When sidebar collapses, hide text and center icons */
section[data-testid="stSidebar"][aria-expanded="false"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] {
    display: none !important;
}

section[data-testid="stSidebar"][aria-expanded="false"] a[data-testid="stPageLink"] {
    width: 44px !important;
    height: 44px !important;
    padding: 0 !important;
    justify-content: center !important;
    margin: 0 auto !important;
}

/* KPI Cards */
.kpi-card {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-title {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #888888;
    margin-bottom: 0.25rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.9rem;
    color: #1A2B4C;
    margin: 0;
}

/* Vertical Containers with Depth */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}

/* Buttons */
.stButton > button {
    background-color: #272828 !important; 
    color: #c9a84c !important;
    border: 1px solid rgba(201, 168, 76, 0.3) !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px; 
    padding: 0.4rem 1.2rem !important;
    min-height: 36px !important;
    height: 36px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #c9a84c !important;
    color: #272828 !important;
    box-shadow: 0 6px 12px rgba(201, 168, 76, 0.3) !important;
    transform: translateY(-1px);
}

/* Minimalist Chat */
.chat-container { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; padding-bottom: 1rem; }
.chat-ai {
    align-self: flex-start;
    background-color: transparent;
    color: #1A1A1A;
    padding: 0.2rem;
    max-width: 95%;
    font-size: 0.88rem;
    line-height: 1.5;
}
.chat-user-wrap { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 0.2rem; }
.chat-user {
    background-color: #F3F4F6;
    color: #1A1A1A;
    padding: 0.55rem 0.95rem;
    border-radius: 14px;
    max-width: 82%;
    font-size: 0.88rem;
    line-height: 1.45;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

/* Content SVG Icons */
.svg-icon {
    width: 15px;
    height: 15px;
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
    fill: #888888;
}

h3 {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; font-weight: 400 !important; 
    color: #1A2B4C !important; letter-spacing: 0.02em; margin-bottom: 0.25rem; font-size: 1.25rem !important;
}

.gallery-title {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #1A2B4C;
    margin: 0 0 0.25rem 0;
}

.gallery-sub {
    font-size: 0.82rem;
    color: #666666;
    margin: 0 0 0.5rem 0;
}

.gallery-desc {
    font-size: 0.85rem;
    color: #444444;
    line-height: 1.5;
    margin: 0;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Content SVG Icons definitions
CALENDAR_ICON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/></svg>'
LOCATION_ICON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'
USER_ICON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'

# Sidebar Navigation with SVG Icons & Cormorant Garamond Text
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 1.5rem; font-size: 1.45rem; font-weight: 700; color: #c9a84c; letter-spacing: 1px;">PROJECT ECHO</div>', unsafe_allow_html=True)
    
    # Custom SVG Navigation Links
    st.markdown("""
        <a href="/" target="_self" data-testid="stPageLink">
            <svg class="sidebar-svg" viewBox="0 0 24 24"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>
            <span data-testid="stPageLink-Text">Dashboard</span>
        </a>
        <a href="/generator" target="_self" data-testid="stPageLink">
            <svg class="sidebar-svg" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
            <span data-testid="stPageLink-Text">Generator</span>
        </a>
        <a href="/archives" target="_self" data-testid="stPageLink">
            <svg class="sidebar-svg" viewBox="0 0 24 24"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
            <span data-testid="stPageLink-Text">Archives</span>
        </a>
    """, unsafe_allow_html=True)

# Fetch current live data from Supabase
supabase_records = fetch_meeting_archives()

# ========== METRICS COMPUTATION ==========
now = datetime.datetime.now()
current_month_name = now.strftime("%B")
current_year = now.year
current_month = now.month

total_month_meetings = 0
total_team_meetings = len(supabase_records)
total_internal_meetings = 0
total_external_meetings = 0

for m in supabase_records:
    m_date_raw = str(m.get("meeting_date", ""))
    try:
        parsed_d = datetime.datetime.strptime(m_date_raw[:10], "%Y-%m-%d")
        if parsed_d.year == current_year and parsed_d.month == current_month:
            total_month_meetings += 1
    except Exception:
        pass

    client_name_str = str(m.get("client_name", "")).strip().lower()
    raw_payload = m.get("raw_payload", {}) or {}
    meeting_details_dict = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
    external_atts = meeting_details_dict.get("external_attendees", [])
    
    if "internal" in client_name_str or "prime" in client_name_str or (not external_atts and not client_name_str):
        total_internal_meetings += 1
    else:
        total_external_meetings += 1

# ========== MAIN DASHBOARD VIEW ==========
# 1. Four KPI Number Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Meetings ({current_month_name})</div><div class="kpi-value">{total_month_meetings}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Team Meetings</div><div class="kpi-value">{total_team_meetings}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Internal Meetings</div><div class="kpi-value">{total_internal_meetings}</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total External Meetings</div><div class="kpi-value">{total_external_meetings}</div></div>', unsafe_allow_html=True)

st.write("")

# 2. Main Split: Meeting Gallery (Left) & Ask Echo Global (Right)
col_left, col_right = st.columns(2)

with col_left:
    with st.container(height=580, border=True):
        st.markdown('<h3>Meeting Gallery</h3>', unsafe_allow_html=True)
        st.caption("Browse all archived meetings. Click any entry to inspect full details, transcript, and edit minutes.")
        
        if supabase_records:
            for idx, m in enumerate(supabase_records):
                m_id = m.get("meeting_id") or f"MOM-{idx}"
                client = m.get("client_name") or "Meeting Record"
                m_date = str(m.get("meeting_date", "N/A"))[:10]
                location = m.get("location") or "Location N/A"
                prep = m.get("prepared_by") or "CRD Team"
                summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                if not summary:
                    summary = "Minutes generated and stored in Supabase archive."
                
                with st.container(border=True):
                    gc1, gc2 = st.columns([7.5, 2.5])
                    with gc1:
                        st.markdown(f"<p class='gallery-title'>{client}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='gallery-sub'>{CALENDAR_ICON} {m_date} &bull; {LOCATION_ICON} {location} &bull; {USER_ICON} {prep}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='gallery-desc'>{summary[:160]}...</p>", unsafe_allow_html=True)
                    with gc2:
                        st.write("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                        if st.button("View Meeting", key=f"btn_view_{m_id}_{idx}"):
                            st.session_state["selected_meeting_id"] = m_id
                            st.switch_page("pages/2_meeting_details.py")
        else:
            st.info("No meeting archives found in Supabase.")

with col_right:
    with st.container(height=580, border=True):
        st.markdown('<h3>Ask Echo &mdash; Global Intelligence</h3>', unsafe_allow_html=True)
        st.caption("Query all stored meeting transcripts, action items, and client records.")

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if not st.session_state["global_chat_history"]:
            st.markdown(
                '<div class="chat-ai">Hello. I am Echo Global. Ask me any question across your Supabase meeting archive.</div>',
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state["global_chat_history"]:
                if msg["role"] == "assistant":
                    formatted_content = msg["content"].replace("\n", "<br>")
                    st.markdown(f'<div class="chat-ai">{formatted_content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-user-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if global_query := st.chat_input("Query whole company archive (e.g. 'What are the deliverables for Regis?')"):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing Supabase archives..."):
                ans = query_global_team_archive(global_query, supabase_records, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()
