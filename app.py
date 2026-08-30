import sys
import os
import calendar
import datetime
import textwrap
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.db import fetch_meeting_archives
from components.sidebar import setup_page_layout
from utils.auth import init_supabase, login, logout, is_authenticated

st.set_page_config(
    page_title="Project Echo - Calendar",
    layout="wide",
    initial_sidebar_state="expanded"
)

supabase = init_supabase()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600;700&display=swap');

/* Hide default Streamlit chrome */
header[data-testid="stHeader"], 
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu { display: none !important; }

/* Base app styling */
.stApp {
    background-color: #F5F1E8 !important;
    background-image: 
        linear-gradient(to right, rgba(0,0,0,0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0,0,0,0.05) 1px, transparent 1px) !important;
    background-size: 80px 80px !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important; 
    gap: 1.5rem !important;
}

/* Left Panel - Native Streamlit Targeting */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.left-panel-scope) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: calc(100vh - 80px) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.left-panel-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    gap: 0.8rem !important;
}

.left-card {
    background: rgba(255,255,255,0.95);
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    flex-shrink: 0;
}

.left-card-scroll {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    margin-bottom: 0.5rem;
}

/* Typography */
.section-title {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-weight: 600;
    color: #1A2B4C;
    font-size: 1.1rem;
    margin: 0 0 0.2rem 0;
}
.section-caption {
    font-size: 0.75rem;
    color: #6C727A;
    margin: 0 0 0.8rem 0;
}

/* KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
}
.kpi-card {
    background: #fff;
    border-radius: 4px;
    padding: 0.5rem 0.65rem;
    border: 1px solid rgba(0,0,0,0.07);
    border-left: 3.5px solid #111A2B;
}
.kpi-title {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6C727A;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1A2B4C;
}

/* Meeting Cards */
.meeting-card {
    background: #fff;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 4px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.5rem;
}
.meeting-title {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 0.9rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0 0 0.1rem 0;
}
.meeting-sub {
    font-size: 0.65rem;
    color: #6C727A;
    margin-bottom: 0.3rem;
}
.meeting-desc {
    font-size: 0.75rem;
    color: #2D2D2D;
    line-height: 1.35;
    margin: 0;
}

/* Make Right Column Borderless for Custom Native UI */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-calendar-scope) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: calc(100vh - 80px) !important;
    padding: 0 !important;
}

/* Calendar Header */
.cal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}
.cal-title-text {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1B1B1B;
    margin: 0;
}
.btn-add {
    background: #FF6B4A;
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.4rem;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(255,107,74,0.3);
    transition: background-color 0.2s;
}
.btn-add:hover { background: #E85A3A; }

/* Calendar App Container */
.cal-app {
    display: flex;
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    height: calc(100vh - 140px);
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

/* Calendar Sidebar */
.cal-sidebar {
    width: 260px;
    border-right: 1px solid #E5E7EB;
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    background: #FAFAFA;
    overflow-y: auto;
    flex-shrink: 0;
}
.cal-dropdown {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0.8rem;
    background: #fff;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
}
.mini-cal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    margin-bottom: 0.8rem;
    font-size: 0.9rem;
}
.mini-cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.2rem;
    text-align: center;
    font-size: 0.75rem;
    color: #6B7280;
    margin-bottom: 1.5rem;
}
.mini-cal-day { font-weight: 600; padding: 0.2rem; color: #374151; }
.mini-cal-date { padding: 0.3rem 0; cursor: pointer; border-radius: 50%; color: #4B5563; }
.mini-cal-date.active { background: #FF6B4A; color: #fff; font-weight: 600; }
.mini-cal-date.dim { color: #D1D5DB; }
.my-schedule-title {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1B1B1B;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.schedule-list { list-style: none; padding: 0; margin: 0; }
.schedule-item {
    display: flex;
    align-items: center;
    font-size: 0.85rem;
    color: #4B5563;
    margin-bottom: 0.8rem;
}
.schedule-item input { margin-right: 0.6rem; accent-color: #FF6B4A; transform: scale(1.1); }

/* Calendar Main */
.cal-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-width: 0;
}
.cal-main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #E5E7EB;
    flex-shrink: 0;
}
.cal-nav { font-size: 1.25rem; font-weight: 600; color: #111827; }
.cal-view-toggles {
    display: flex;
    background: #F3F4F6;
    border-radius: 8px;
    padding: 0.2rem;
}
.cal-view-toggles button {
    border: none;
    background: transparent;
    padding: 0.4rem 1rem;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #4B5563;
    cursor: pointer;
}
.cal-view-toggles button.active { background: #1F2937; color: #fff; }

/* Timetable */
.cal-timetable {
    flex: 1;
    display: flex;
    overflow-y: auto;
    overflow-x: hidden;
    position: relative;
}
.cal-time-axis {
    width: 60px;
    border-right: 1px solid #E5E7EB;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
    background: #fff;
}
.cal-time-slot {
    height: 60px;
    border-bottom: 1px solid #F3F4F6;
    position: relative;
}
.cal-time-label {
    position: absolute;
    top: -8px;
    right: 8px;
    font-size: 0.7rem;
    color: #9CA3AF;
    font-weight: 500;
}
.cal-days-grid {
    flex: 1;
    display: flex;
    min-width: 0;
}
.cal-day-col {
    flex: 1;
    border-right: 1px solid #E5E7EB;
    display: flex;
    flex-direction: column;
    min-width: 0;
}
.cal-day-header {
    text-align: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid #E5E7EB;
    height: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    flex-shrink: 0;
    background: #fff;
}
.cal-day-name { font-size: 0.85rem; font-weight: 600; color: #111827; }
.cal-day-sub { font-size: 0.65rem; color: #9CA3AF; margin-top: 0.1rem; }
.cal-day-body {
    flex: 1;
    position: relative;
    background-image: linear-gradient(to bottom, #F9FAFB 1px, transparent 1px);
    background-size: 100% 60px;
    min-height: 540px;
}

/* Events */
.cal-event {
    position: absolute;
    left: 4px;
    right: 4px;
    border-radius: 6px;
    padding: 0.5rem;
    font-size: 0.75rem;
    display: flex;
    flex-direction: column;
    border-left: 3px solid transparent;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    overflow: hidden;
    z-index: 10;
}
.evt-time { font-weight: 600; margin-bottom: 0.15rem; font-size: 0.7rem; }
.evt-title { color: #1F2937; line-height: 1.2; font-weight: 500; }
.evt-avatars { margin-top: auto; display: flex; justify-content: flex-end; }
.avatar {
    width: 18px; height: 18px;
    border-radius: 50%;
    border: 2px solid #fff;
    margin-left: -6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.5rem;
    font-weight: 600;
    color: #fff;
}

.bg-orange { background: #FEF2EB; border-left-color: #FF6B4A; }
.bg-orange .evt-time { color: #FF6B4A; }
.bg-blue { background: #EEF2FF; border-left-color: #6366F1; }
.bg-blue .evt-time { color: #6366F1; }
.bg-red { background: #FEF2F2; border-left-color: #EF4444; }
.bg-red .evt-time { color: #EF4444; }
.bg-green { background: #ECFDF5; border-left-color: #10B981; }
.bg-green .evt-time { color: #10B981; }

/* Streamlit popovers and buttons */
div[data-testid="stPopover"] { margin-bottom: 0 !important; }
div[data-testid="stPopover"] > button {
    background-color: #111A2B !important;
    color: #fff !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    font-size: 0.75rem !important;
    min-height: 32px !important;
    height: 32px !important;
}
.stButton > button {
    background-color: #111A2B !important;
    color: #fff !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.75rem !important;
    min-height: 28px !important;
    height: 28px !important;
}
</style>
""", unsafe_allow_html=True)

# Auth Check
if not is_authenticated():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<p style="font-family:\'Playfair Display\',serif;font-style:italic;font-size:3rem;font-weight:600;color:#1A2B4C;text-align:center;">Project Echo</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.9rem;color:#6C727A;text-align:center;font-style:italic;">Sign in to access your dashboard</p>', unsafe_allow_html=True)
        email = st.text_input("Email", value="")
        password = st.text_input("Password", type="password", value="")
        if st.button("Sign In", key="login_btn", use_container_width=True):
            if login(email, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
    st.stop()

setup_page_layout()

with st.sidebar:
    st.markdown("---")
    if st.button("Logout", key="logout_btn"):
        logout()
        st.rerun()

# Session State
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.datetime.now().date()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# Fetch Data
supabase_records = fetch_meeting_archives(limit=100)

total_team_meetings = len(supabase_records)
total_range_meetings = 0
total_internal_meetings = 0
total_external_meetings = 0
filtered_records = []
calendar_events_by_date = {}
theme_colors = ["bg-orange", "bg-blue", "bg-green", "bg-red"]
c_idx = 0

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

    raw = m.get("raw_payload", {}) or {}
    details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
    items = details.get("action_items", [])
    if not items:
        items = details.get("discussion_points", [])

    for item in items:
        # Prioritize delivery_date/due_date over meeting date
        date_val = item.get("delivery_date") or item.get("due_date") or m_date_raw[:10]
        if not date_val:
            continue
        try:
            d_str = datetime.datetime.strptime(date_val[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            d_str = m_date_raw[:10]

        title = item.get("task") or item.get("topic") or item.get("action") or "Action Required"
        owner = item.get("owner") or item.get("assigned_to") or "Team"

        if d_str not in calendar_events_by_date:
            calendar_events_by_date[d_str] = []

        # Stagger overlapping events aesthetically 
        hour = 8 + (len(calendar_events_by_date[d_str]) * 2) % 8
        am_pm = "AM" if hour < 12 else "PM"
        disp_hour = hour if hour <= 12 else hour - 12

        calendar_events_by_date[d_str].append({
            "title": title,
            "owner": owner,
            "color": theme_colors[c_idx % len(theme_colors)],
            "time": f"{disp_hour}:00{am_pm}",
            "top_px": (hour - 8) * 60,
            "height_px": 80 if len(title) > 20 else 60
        })
        c_idx += 1

# Build Calendar HTML
week_start = today - datetime.timedelta(days=today.weekday() + 1)
if today.weekday() == 6:
    week_start = today

day_columns_html = ""
for i in range(7):
    curr_date = week_start + datetime.timedelta(days=i)
    curr_date_str = curr_date.strftime("%Y-%m-%d")
    day_name = curr_date.strftime("%b %-d")

    events_html = ""
    for evt in calendar_events_by_date.get(curr_date_str, []):
        owner_initial = evt['owner'][0].upper() if evt['owner'] else "T"
        events_html += f"""
        <div class="cal-event {evt['color']}" style="top:{evt['top_px']}px;height:{evt['height_px']}px;">
            <div class="evt-time">{evt['time']}</div>
            <div class="evt-title">{evt['title'][:45]}{'...' if len(evt['title']) > 45 else ''}</div>
            <div class="evt-avatars">
                <div class="avatar" style="background:#4B5563;">{owner_initial}</div>
            </div>
        </div>"""

    day_columns_html += f"""
    <div class="cal-day-col">
        <div class="cal-day-header">
            <div class="cal-day-name">{day_name}</div>
        </div>
        <div class="cal-day-body">
            {events_html}
        </div>
    </div>"""

# Layout
col_left, col_right = st.columns([1, 2.5])

# LEFT COLUMN (Restored safe Streamlit Scoping)
with col_left:
    with st.container(border=False):
        st.markdown('<div class="left-panel-scope"></div>', unsafe_allow_html=True)
        
        # KPI Card
        st.markdown(f"""
        <div class="left-card">
            <p class="section-title">Overview & Metrics</p>
            <p class="section-caption">Summary of records in selected scope.</p>
            <div class="kpi-grid">
                <div class="kpi-card"><span class="kpi-title">Selected</span><span class="kpi-value">{total_range_meetings}</span></div>
                <div class="kpi-card"><span class="kpi-title">Team Archive</span><span class="kpi-value">{total_team_meetings}</span></div>
                <div class="kpi-card"><span class="kpi-title">Internal</span><span class="kpi-value">{total_internal_meetings}</span></div>
                <div class="kpi-card"><span class="kpi-title">External</span><span class="kpi-value">{total_external_meetings}</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Date Filter
        st.markdown('<div class="left-card" style="padding-bottom: 0.5rem;">', unsafe_allow_html=True)
        date_label = f"{st.session_state['start_date'].strftime('%b %d')} — {st.session_state['end_date'].strftime('%b %d, %Y')}"
        with st.popover(date_label, use_container_width=True):
            p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
                st.caption("PRESETS")
                if st.button("This Week", key="btn_tw", use_container_width=True):
                    st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday())
                    st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                    st.rerun()
                if st.button("Last Month", key="btn_lm", use_container_width=True):
                    first_this = today.replace(day=1)
                    last_prev = first_this - datetime.timedelta(days=1)
                    st.session_state["start_date"] = last_prev.replace(day=1)
                    st.session_state["end_date"] = last_prev
                    st.rerun()
                if st.button("Reset", key="btn_reset", use_container_width=True):
                    st.session_state["start_date"] = today.replace(day=1)
                    _, last = calendar.monthrange(today.year, today.month)
                    st.session_state["end_date"] = today.replace(day=last)
                    st.rerun()
            with p_col2:
                st.caption("CUSTOM RANGE")
                selected_dates = st.date_input("Date Range", value=(st.session_state["start_date"], st.session_state["end_date"]), label_visibility="collapsed")
                if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                    if st.session_state["start_date"] != selected_dates[0] or st.session_state["end_date"] != selected_dates[1]:
                        st.session_state["start_date"] = selected_dates[0]
                        st.session_state["end_date"] = selected_dates[1]
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Meetings Feed
        st.markdown('<div class="left-card left-card-scroll">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">Recent Meetings</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Filtered meeting archives.</p>', unsafe_allow_html=True)

        if filtered_records:
            for idx, m in enumerate(filtered_records):
                m_id = m.get("meeting_id") or f"MOM-{idx}"
                client = m.get("client_name") or "Meeting Record"
                m_date = str(m.get("meeting_date", "N/A"))[:10]
                prep = m.get("prepared_by") or "CRD Team"
                summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                st.markdown(f"""
                <div class="meeting-card">
                    <p class="meeting-title">{client}</p>
                    <p class="meeting-sub">{m_date} &bull; {prep}</p>
                    <p class="meeting-desc">{summary[:85]}...</p>
                </div>""", unsafe_allow_html=True)
                if st.button("View Details", key=f"btn_view_{m_id}_{idx}", use_container_width=True):
                    st.session_state["selected_meeting_id"] = m_id
                    st.switch_page("pages/2_meeting_details.py")
        else:
            st.info("No records found.")
        st.markdown('</div>', unsafe_allow_html=True)

# RIGHT COLUMN (HTML Indentation Removed)
with col_right:
    with st.container(border=False):
        st.markdown('<div class="custom-calendar-scope"></div>', unsafe_allow_html=True)
        
        calendar_html = textwrap.dedent(f"""
<div class="cal-header">
    <h1 class="cal-title-text">Calendar</h1>
    <button class="btn-add">+ Add New Schedule</button>
</div>

<div class="cal-app">
    <div class="cal-sidebar">
        <div class="cal-dropdown">
            <span>📅 All Calendar</span>
            <span style="color:#9CA3AF;font-size:0.7rem;">▼</span>
        </div>
        <div class="mini-cal-header">
            <span>{today.strftime('%B %Y')}</span>
            <div>
                <span style="color:#9CA3AF;cursor:pointer;margin-right:8px;">&lt;</span>
                <span style="color:#9CA3AF;cursor:pointer;">&gt;</span>
            </div>
        </div>
        <div class="mini-cal-grid">
            <div class="mini-cal-day">Sun</div><div class="mini-cal-day">Mon</div><div class="mini-cal-day">Tue</div><div class="mini-cal-day">Wed</div><div class="mini-cal-day">Thu</div><div class="mini-cal-day">Fri</div><div class="mini-cal-day">Sat</div>
            <div class="mini-cal-date dim">26</div><div class="mini-cal-date dim">27</div><div class="mini-cal-date dim">28</div><div class="mini-cal-date dim">29</div><div class="mini-cal-date dim">30</div><div class="mini-cal-date dim">31</div><div class="mini-cal-date">1</div>
            <div class="mini-cal-date">2</div><div class="mini-cal-date">3</div><div class="mini-cal-date">4</div><div class="mini-cal-date">5</div><div class="mini-cal-date">6</div><div class="mini-cal-date">7</div><div class="mini-cal-date">8</div>
            <div class="mini-cal-date">9</div><div class="mini-cal-date">10</div><div class="mini-cal-date">11</div><div class="mini-cal-date">12</div><div class="mini-cal-date">13</div><div class="mini-cal-date">14</div><div class="mini-cal-date">15</div>
            <div class="mini-cal-date">16</div><div class="mini-cal-date">17</div><div class="mini-cal-date">18</div><div class="mini-cal-date">19</div><div class="mini-cal-date">20</div><div class="mini-cal-date">21</div><div class="mini-cal-date">22</div>
            <div class="mini-cal-date active">23</div><div class="mini-cal-date">24</div><div class="mini-cal-date">25</div><div class="mini-cal-date">26</div><div class="mini-cal-date">27</div><div class="mini-cal-date">28</div><div class="mini-cal-date">29</div>
        </div>
        <hr style="border:0;border-top:1px solid #E5E7EB;margin-bottom:1.5rem;">
        <div class="my-schedule-title">My Schedule <span style="color:#9CA3AF;font-size:0.7rem;">▼</span></div>
        <ul class="schedule-list">
            <li class="schedule-item"><input type="checkbox" checked> Schedule Meeting</li>
            <li class="schedule-item"><input type="checkbox" checked> Project Review</li>
            <li class="schedule-item"><input type="checkbox" checked> Online Meeting</li>
            <li class="schedule-item"><input type="checkbox"> Recess Break</li>
            <li class="schedule-item"><input type="checkbox"> Coffee Date</li>
            <li class="schedule-item"><input type="checkbox"> Other</li>
        </ul>
    </div>
    
    <div class="cal-main">
        <div class="cal-main-header">
            <div class="cal-nav">&lt; {today.strftime('%B')} &gt;</div>
            <div class="cal-view-toggles">
                <button>Day</button>
                <button class="active">Week</button>
                <button>Month</button>
            </div>
        </div>
        <div class="cal-timetable">
            <div class="cal-time-axis">
                <div class="cal-time-slot" style="height:60px;"></div>
                <div class="cal-time-slot"><span class="cal-time-label">9AM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">10AM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">11AM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">12PM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">1PM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">2PM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">3PM</span></div>
                <div class="cal-time-slot"><span class="cal-time-label">4PM</span></div>
            </div>
            <div class="cal-days-grid">
                {day_columns_html}
            </div>
        </div>
    </div>
</div>
        """)
        
        st.markdown(calendar_html, unsafe_allow_html=True)
