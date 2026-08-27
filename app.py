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
if "chat_fullscreen" not in st.session_state:
    st.session_state["chat_fullscreen"] = False

today = datetime.datetime.now().date()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# 3. Global & Dashboard CSS (Your exact UI preserved)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,500;1,600&family=Cormorant+Garamond:wght@400;500;600;700&display=swap');

/* --- Canvas & Minimal Outer Margins --- */
.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
.block-container { 
    padding-top: 1rem !important; 
    padding-bottom: 1.5rem !important;
    padding-right: 1.5rem !important; 
    padding-left: 1.5rem !important;
    max-width: 100% !important;
}

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }

/* --- Warm Cream Architectural Grid Background --- */
.stApp {
    background-color: #F5F1E8 !important;
    background-image: 
        linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px) !important;
    background-size: 80px 80px !important;
    background-position: 0 0 !important;
    color: #1A1A1A;
}

/* --- Section Headings --- */
.section-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; 
    font-weight: 600 !important; 
    color: #1A2B4C !important; 
    font-size: 1.15rem !important;
    margin: 0 !important;
}
.section-caption {
    font-size: 0.75rem;
    color: #555E68;
    margin-bottom: 0.5rem;
}

/* --- Tight 2x2 KPI Grid --- */
.kpi-grid-2x2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.35rem;
    margin-bottom: 0.4rem;
}
.kpi-mini-card {
    background: #FFFFFF;
    border-radius: 6px;
    padding: 0.5rem 0.65rem;
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-left: 3.5px solid #22252A;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-mini-title {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6C727A;
    margin-bottom: 0.1rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-mini-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    line-height: 1;
}

/* --- Scaled-down Date Picker --- */
div[data-testid="stPopover"] { margin-bottom: 0.5rem !important; }
div[data-testid="stPopover"] > button {
    background-color: #FFFFFF !important;
    color: #22252A !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    border-radius: 6px !important;
    padding: 0.15rem 0.5rem !important;
    font-size: 0.72rem !important;
    min-height: 28px !important;
    height: 28px !important;
}
div[data-testid="stPopover"] > button:hover {
    border-color: #22252A !important;
    background-color: #FAF8F5 !important;
}

/* --- Containers --- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.025) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    padding: 1rem !important;
}

/* --- Buttons --- */
.stButton > button {
    background-color: #22252A !important;
    color: #FFFFFF !important;
    border: 1px solid #111315 !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    padding: 0.3rem 0.75rem !important;
    min-height: 28px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background-color: #111315 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
}

/* Minimal Icon Buttons (Clear & Fullscreen) */
.icon-action-btn div[data-testid="stButton"] > button {
    background-color: #FFFFFF !important;
    color: #22252A !important;
    border: 1px solid rgba(0, 0, 0, 0.12) !important;
    border-radius: 6px !important;
    padding: 0 !important;
    width: 30px !important;
    min-width: 30px !important;
    height: 30px !important;
    min-height: 30px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
}
.icon-action-btn div[data-testid="stButton"] > button:hover {
    background-color: #FAF8F5 !important;
    border-color: #22252A !important;
    transform: none !important;
}
.icon-action-btn div[data-testid="stButton"] > button span {
    font-size: 1.1rem !important;
}

/* --- Recent Meetings Cards --- */
.gallery-card {
    background-color: #FAF8F5;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 6px;
    padding: 0.65rem 0.8rem;
    margin-bottom: 0.35rem;
}
.gallery-title { 
    font-family: 'Playfair Display', serif; 
    font-style: italic; 
    font-size: 0.95rem; 
    font-weight: 600;
    color: #1A2B4C; 
    margin: 0 0 0.1rem 0; 
}
.gallery-sub { 
    font-size: 0.68rem; 
    color: #6C727A; 
    margin-bottom: 0.3rem; 
    font-weight: 500;
}
.gallery-desc { 
    font-size: 0.74rem; 
    color: #2D2D2D; 
    line-height: 1.4; 
    margin: 0;
}

/* --- Chat Overrides --- */
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 0.25rem 0 !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #FAF8F5 !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-left: 4px solid #22252A !important;
    border-radius: 0 8px 8px 0 !important;
    padding: 0.75rem 1rem !important;
    margin-bottom: 0.6rem !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) div[data-testid="stMarkdownContainer"] * {
    color: #1A1A1A !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #22252A !important;
    border-radius: 10px 10px 2px 10px !important;
    padding: 0.65rem 1rem !important;
    margin-bottom: 0.6rem !important;
    margin-left: auto !important;
    max-width: 82% !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08) !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stMarkdownContainer"] * {
    color: #FFFFFF !important;
    font-weight: 500 !important;
}

/* Chat Tables */
div[data-testid="stChatMessage"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 0.5rem 0 !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
}
div[data-testid="stChatMessage"] th {
    background-color: #F1EFE9 !important;
    color: #1A2B4C !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 6px 10px !important;
    border-bottom: 1px solid #E5E7EB !important;
    font-size: 0.75rem !important;
}
div[data-testid="stChatMessage"] td {
    padding: 6px 10px !important;
    border-bottom: 1px solid #F3F4F6 !important;
    color: #2D2D2D !important;
    font-size: 0.75rem !important;
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

# 5. Layout Composition
if st.session_state["chat_fullscreen"]:
    col_left, col_right = None, st.container()
else:
    col_left, col_right = st.columns([1, 2.3], gap="small")

# Left Column (Overview, Date Filter, Feed)
if not st.session_state["chat_fullscreen"]:
    with col_left:
        with st.container(height=720, border=True):
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

            # Compact Popover directly underneath
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

            st.markdown('<p class="section-title" style="margin-top: 0.4rem !important;">Recent Meetings</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-caption">Scroll to explore filtered meetings.</p>', unsafe_allow_html=True)
            
            feed_container = st.container(height=310)
            with feed_container:
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
                            <p class="gallery-desc">{summary[:90]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("View Details", key=f"btn_view_{m_id}_{idx}", use_container_width=True):
                            st.session_state["selected_meeting_id"] = m_id
                            st.switch_page("pages/2_meeting_details.py")
                        st.markdown("<div style='margin-bottom: 0.35rem;'></div>", unsafe_allow_html=True)
                else:
                    st.info("No records found.")

# Right Column (AI Chat Plugin)
with col_right:
    render_echo_chat(
        container=st,
        height=720,
        title="Ask Echo — Global Intelligence",
        caption="Synthesize meeting archives, transcripts, and action logs."
    )
