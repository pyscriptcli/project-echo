import streamlit as st
import datetime
from utils.db import fetch_meeting_archives
from utils.ai import query_global_team_archive

# 1. Page Config (MUST be first)
st.set_page_config(
    page_title="Project Echo - Executive Hub", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. Global State Initialization
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

# 3. Custom CSS - Complete Sidebar Removal & Clean Top Bar
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* Background Grid */
.stApp {
    background-color: #F3EFE6; 
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

/* ================= 1. HIDE ALL SIDEBAR ARTIFACTS ================= */
section[data-testid="stSidebar"],
button[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
}

/* ================= 2. HIDE STREAMLIT DEFAULT TOP HEADER ================= */
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

/* Full Width Main Container Spacing */
.block-container { 
    padding-top: 1.5rem !important;
    padding-right: 2.5rem !important;
    padding-left: 2.5rem !important;
    max-width: 100% !important;
}

/* ================= 3. TOP NAVIGATION BAR ================= */
.top-nav-container {
    background-color: #272828;
    border-radius: 12px;
    padding: 0.6rem 1.75rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(201, 168, 76, 0.25);
}

.top-brand {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #c9a84c !important;
    letter-spacing: 0.1em;
    display: flex;
    align-items: center;
    height: 100%;
}

/* Nav Action Buttons */
div[data-testid="stHorizontalBlock"]:has(button[key^="nav_"]) {
    background-color: #272828;
    padding: 0.5rem 1.25rem;
    border-radius: 12px;
    border: 1px solid rgba(201, 168, 76, 0.25);
    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    margin-bottom: 1.8rem;
    align-items: center;
}

button[key^="nav_"] {
    background-color: transparent !important;
    color: #c9a84c !important;
    border: 1px solid transparent !important;
    border-radius: 50px !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    height: 38px !important;
    transition: all 0.2s ease !important;
}

button[key^="nav_"]:hover {
    background-color: rgba(201, 168, 76, 0.15) !important;
    border-color: rgba(201, 168, 76, 0.4) !important;
    color: #ffffff !important;
    box-shadow: 0 0 10px rgba(201, 168, 76, 0.2) !important;
}

button[key="nav_dashboard"] {
    background-color: rgba(201, 168, 76, 0.18) !important;
    border-color: rgba(201, 168, 76, 0.45) !important;
    color: #e5cf8e !important;
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

/* Vertical Block Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}

/* Content Buttons */
.stButton > button:not([key^="nav_"]) {
    background-color: #272828 !important; 
    color: #c9a84c !important;
    border: 1px solid rgba(201, 168, 76, 0.3) !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 1.2rem !important;
    min-height: 36px !important;
    height: 36px !important;
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:not([key^="nav_"]):hover {
    background-color: #c9a84c !important;
    color: #272828 !important;
    box-shadow: 0 4px 12px rgba(201, 168, 76, 0.3) !important;
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

# 4. Top Navigation Bar (Integrated Horizontal Menu)
nav_brand, nav_gap, nav_item1, nav_item2, nav_item3, nav_item4 = st.columns([3.5, 2.5, 1.5, 1.5, 1.8, 1.5])

with nav_brand:
    st.markdown('<div class="top-brand">PROJECT ECHO</div>', unsafe_allow_html=True)
with nav_item1:
    if st.button("Dashboard", key="nav_dashboard"):
        st.rerun()
with nav_item2:
    if st.button("Generator", key="nav_generator"):
        st.switch_page("pages/1_generator.py")
with nav_item3:
    if st.button("Meeting Details", key="nav_details"):
        st.switch_page("pages/2_meeting_details.py")
with nav_item4:
    if st.button("Archives", key="nav_archives"):
        st.switch_page("pages/3_archives.py")

# SVG Icons
CALENDAR_ICON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z"/></svg>'
LOCATION_ICON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>'
USER_ICON = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>'

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
# 1. KPI Cards
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

# 2. Main Symmetrical Split: Meeting Gallery (Left) & Ask Echo Global (Right)
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
