import sys
import os
import calendar
import datetime
import streamlit as st

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.db import fetch_meeting_archives
from utils.echo_ai import render_echo_chat
from components.sidebar import setup_page_layout

# 1. Page Configuration
st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
setup_page_layout()

# 2. Session State Initialization
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.datetime.now().date()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# 3. Global & Dashboard CSS (Pill Buttons & Architectural Canvas)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600;700&display=swap');

/* Canvas & Margins */
.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }

html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow: hidden !important;
    padding-top: 0.8rem !important;
    padding-bottom: 0.5rem !important;
    padding-right: 1.5rem !important;
    padding-left: 1.5rem !important;
    max-width: 100% !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Warm Ivory Architectural Grid Canvas */
[data-testid="stAppViewContainer"], .stApp {
    background-color: #F6F2EA !important;
    background-image: 
        linear-gradient(to right, #E8E2D5 1px, transparent 1px),
        linear-gradient(to bottom, #E8E2D5 1px, transparent 1px) !important;
    background-size: 32px 32px !important;
    color: #1A1A1A;
}

/* Synchronize Dashboard Card Containers */
.dashboard-left-card > div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) {
    background-color: transparent !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    height: calc(100vh - 130px) !important;
    max-height: calc(100vh - 130px) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

.dashboard-left-card > div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    padding: 0.5rem 0.85rem !important;
    gap: 0 !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

/* Section Headings */
.section-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-weight: 600 !important;
    color: #1A2B4C !important;
    font-size: 1.05rem !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.section-caption {
    font-size: 0.72rem;
    color: #6C727A;
    margin: 0 0 0.35rem 0 !important;
}

/* 2x2 KPI Grid */
.kpi-grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.35rem;
    margin-bottom: 0.35rem;
    flex-shrink: 0;
}
.kpi-mini-card {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 6px;
    padding: 0.4rem 0.55rem;
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-left: 3.5px solid #111A2B;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-mini-title {
    font-size: 0.58rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6C727A;
    margin-bottom: 0.05rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-mini-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.15rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    line-height: 1;
}

/* Date Picker Popover Pill */
div[data-testid="stPopover"] {
    margin-bottom: 0.4rem !important;
    flex-shrink: 0 !important;
}
div[data-testid="stPopover"] > button {
    background-color: #111A2B !important;
    color: #F8FAFC !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    padding: 0.1rem 0.75rem !important;
    font-size: 0.72rem !important;
    min-height: 28px !important;
    height: 28px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stPopover"] > button:hover {
    border-color: #F1C40F !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3) !important;
}

/* Left Column Inner Feed Auto-Scroll */
.left-feed-container {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}
.left-feed-container > div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.75) !important;
    backdrop-filter: blur(4px) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: 6px !important;
    overflow-y: auto !important;
    padding: 0.5rem 0.75rem !important;
    height: 100% !important;
}

/* Meeting Cards */
.gallery-card {
    background-color: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 6px;
    padding: 0.5rem 0.65rem;
    margin-bottom: 0.25rem;
}
.gallery-title { 
    font-family: 'Playfair Display', serif; 
    font-style: italic; 
    font-size: 0.88rem; 
    font-weight: 600; 
    color: #1A2B4C; 
    margin: 0 0 0.1rem 0; 
}
.gallery-sub { 
    font-size: 0.65rem; 
    color: #6C727A; 
    margin-bottom: 0.2rem; 
    font-weight: 500;
}
.gallery-desc { 
    font-size: 0.72rem; 
    color: #2D2D2D; 
    line-height: 1.35; 
    margin: 0;
}

/* Charcoal Black & Gold Accent Pill Buttons */
.stButton > button {
    background-color: #111A2B !important;
    color: #FFFFFF !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.75rem !important;
    min-height: 26px !important;
    height: 26px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    border-color: #F1C40F !important;
    background-color: #1A263D !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# 4. Fetch and Filter Data
supabase_records = fetch_meeting_archives(limit=100)

total_team_meetings = len(supabase_records)
total_range_meetings = 0
total_internal_meetings = 0
total_external_meetings = 0
filtered_records = []

for m in supabase_records:
    m_date_raw = str(m.get("meeting_date", ""))
    try:
        parsed_d = datetime.datetime.strptime(m_date_raw[:10], "%Y-%m-%d").date()
        if st.session_state["start_date"] <= parsed_d <= st.session_state["end_date"]:
            filtered_records.append(m)
            total_range_meetings += 1
            
            client_name_str = str(m.get("client_name", "")).strip().lower()
            raw_payload = m.get("raw_payload", {}) or {}
            meeting_details_dict = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
            external_atts = meeting_details_dict.get("external_attendees", [])
            
            if "internal" in client_name_str or "prime" in client_name_str or (not external_atts and not client_name_str):
                total_internal_meetings += 1
            else:
                total_external_meetings += 1
    except Exception:
        pass

# 5. Dashboard Grid Composition
col_left, col_right = st.columns([1, 2.3], gap="small")

# Left Column (Overview, Date Filter, Feed)
with col_left:
    st.markdown('<div class="dashboard-left-card">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<p class="section-title">Overview & Metrics</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Summary of records in selected scope.</p>', unsafe_allow_html=True)
        
        # 2x2 Mini KPI Grid
        st.markdown(f"""
        <div class="kpi-grid-2x2">
            <div class="kpi-mini-card">
                <span class="kpi-mini-title">Selected</span>
                <span class="kpi-mini-value">{total_range_meetings}</span>
            </div>
            <div class="kpi-mini-card">
                <span class="kpi-mini-title">Team Archive</span>
                <span class="kpi-mini-value">{total_team_meetings}</span>
            </div>
            <div class="kpi-mini-card">
                <span class="kpi-mini-title">Internal</span>
                <span class="kpi-mini-value">{total_internal_meetings}</span>
            </div>
            <div class="kpi-mini-card">
                <span class="kpi-mini-title">External</span>
                <span class="kpi-mini-value">{total_external_meetings}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Date Picker Popover Pill
        date_label = f"{st.session_state['start_date'].strftime('%b %d')} — {st.session_state['end_date'].strftime('%b %d, %Y')}"
        with st.popover(date_label, use_container_width=True):
            p_col1, p_col2 = st.columns([1.1, 1.9])
            with p_col1:
                st.caption("PRESETS")
                if st.button("This Week", key="btn_tw", use_container_width=True):
                    st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday())
                    st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                    st.rerun()
                if st.button("Last Week", key="btn_lw", use_container_width=True):
                    st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday() + 7)
                    st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                    st.rerun()
                if st.button("This Month", key="btn_tm", use_container_width=True):
                    st.session_state["start_date"] = today.replace(day=1)
                    _, last = calendar.monthrange(today.year, today.month)
                    st.session_state["end_date"] = today.replace(day=last)
                    st.rerun()
                if st.button("Last Month", key="btn_lm", use_container_width=True):
                    first_this = today.replace(day=1)
                    last_prev = first_this - datetime.timedelta(days=1)
                    st.session_state["start_date"] = last_prev.replace(day=1)
                    st.session_state["end_date"] = last_prev
                    st.rerun()
                st.markdown("<div style='margin-top: 0.3rem;'></div>", unsafe_allow_html=True)
                if st.button("Reset", key="btn_reset_inside", use_container_width=True):
                    st.session_state["start_date"] = today.replace(day=1)
                    _, last = calendar.monthrange(today.year, today.month)
                    st.session_state["end_date"] = today.replace(day=last)
                    st.rerun()

            with p_col2:
                st.caption("CUSTOM RANGE")
                selected_dates = st.date_input(
                    "Date Range",
                    value=(st.session_state["start_date"], st.session_state["end_date"]),
                    label_visibility="collapsed"
                )
                if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                    if st.session_state["start_date"] != selected_dates[0] or st.session_state["end_date"] != selected_dates[1]:
                        st.session_state["start_date"] = selected_dates[0]
                        st.session_state["end_date"] = selected_dates[1]
                        st.rerun()

        st.markdown('<p class="section-title">Recent Meetings</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Filtered meeting archives.</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="left-feed-container">', unsafe_allow_html=True)
        with st.container():
            if filtered_records:
                for idx, m in enumerate(filtered_records):
                    m_id = m.get("meeting_id") or f"MOM-{idx}"
                    client = m.get("client_name") or "Meeting Record"
                    m_date = str(m.get("meeting_date", "N/A"))[:10]
                    prep = m.get("prepared_by") or "CRD Team"
                    summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                    
                    st.markdown(f"""
                    <div class="gallery-card">
                        <p class="gallery-title">{client}</p>
                        <p class="gallery-sub">{m_date} &bull; {prep}</p>
                        <p class="gallery-desc">{summary[:85]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("View Details", key=f"btn_view_{m_id}_{idx}", use_container_width=True):
                        st.session_state["selected_meeting_id"] = m_id
                        st.switch_page("pages/2_meeting_details.py")
            else:
                st.info("No records found.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Right Column (Ask Echo AI Plugin)
with col_right:
    render_echo_chat(title="Ask Echo")
