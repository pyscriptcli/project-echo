import sys
import os
import calendar
import datetime
import textwrap
import streamlit as st

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.db import fetch_meeting_archives
from components.sidebar import setup_page_layout
from utils.auth import init_supabase, login, logout, is_authenticated

# 1. Page Configuration
st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Supabase client
supabase = init_supabase()

# 3. Global & Dashboard CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600;700&display=swap');

/* Canvas & Margins */
.stApp > header { display: none !important; visibility: hidden !important; }
[data-testid="stHeader"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
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

/* Warm Cream Architectural Large 80px Grid Background */
[data-testid="stAppViewContainer"], .stApp {
    background-color: #F5F1E8 !important;
    background-image: 
        linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px) !important;
    background-size: 80px 80px !important;
    background-position: 0 0 !important;
    color: #1A1A1A;
}

[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important; 
}

/* Synchronize Outer Containers */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-left-card-scope) {
    background-color: transparent !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    height: calc(100vh - 130px) !important;
    max-height: calc(100vh - 130px) !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin-top: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.dashboard-left-card-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    padding: 0.5rem 0.85rem !important;
    gap: 0 !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

/* Make Right Column Borderless for Custom Native UI */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-calendar-scope) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: calc(100vh - 110px) !important;
    padding: 0 !important;
}

/* ---------------- CUSTOM NATIVE CALENDAR UI ---------------- */
.cal-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
}
.cal-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #1B1B1B;
    margin: 0;
}
.btn-add-schedule {
    background-color: #FF6B4A;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.4rem;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(255, 107, 74, 0.3);
    transition: background-color 0.2s;
}
.btn-add-schedule:hover { background-color: #E85A3A; }

.cal-app-container {
    display: flex;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    height: calc(100vh - 150px);
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

/* Sidebar */
.cal-sidebar {
    width: 250px;
    border-right: 1px solid #E5E7EB;
    padding: 1.2rem;
    display: flex;
    flex-direction: column;
    background: #FAFAFA;
}
.cal-dropdown {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 0.8rem;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
    font-weight: 500;
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
.mini-cal-date.active { background-color: #FF6B4A; color: white; font-weight: 600; }
.mini-cal-date.dim { color: #D1D5DB; }

.my-schedule-title {
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1B1B1B;
    display: flex;
    justify-content: space-between;
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

/* Main Grid */
.cal-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #FFFFFF;
}
.cal-main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #E5E7EB;
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
.cal-view-toggles button.active { background: #1F2937; color: white; }

/* Timetable */
.cal-timetable { flex: 1; display: flex; overflow-y: auto; overflow-x: hidden; position: relative; }
.cal-time-axis {
    width: 60px;
    border-right: 1px solid #E5E7EB;
    display: flex;
    flex-direction: column;
    background: #FFFFFF;
}
.cal-time-slot { height: 60px; border-bottom: 1px solid #F3F4F6; position: relative; }
.cal-time-label { position: absolute; top: -8px; right: 8px; font-size: 0.7rem; color: #9CA3AF; font-weight: 500; }
.cal-days-grid { flex: 1; display: flex; }
.cal-day-col {
    flex: 1;
    border-right: 1px solid #E5E7EB;
    display: flex;
    flex-direction: column;
}
.cal-day-header {
    text-align: center;
    padding: 0.8rem 0;
    border-bottom: 1px solid #E5E7EB;
    height: 60px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    background: #FFFFFF;
}
.cal-day-name { font-size: 0.85rem; font-weight: 600; color: #111827; }
.cal-day-sub { font-size: 0.65rem; color: #9CA3AF; margin-top: 0.1rem; }

.cal-day-body {
    flex: 1;
    position: relative;
    background-image: linear-gradient(to bottom, #F9FAFB 1px, transparent 1px);
    background-size: 100% 60px; /* Maps to 1 hour slots */
    min-height: 540px; /* 9 hours * 60px */
}

/* Event Cards */
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
.evt-avatars {
    margin-top: auto;
    display: flex;
    justify-content: flex-end;
}
.avatar {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid white;
    margin-left: -6px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.5rem;
    font-weight: 600;
    color: white;
}

/* Specific Event Themes */
.bg-orange { background-color: #FEF2EB; border-left-color: #FF6B4A; }
.bg-orange .evt-time { color: #FF6B4A; }

.bg-blue { background-color: #EEF2FF; border-left-color: #6366F1; }
.bg-blue .evt-time { color: #6366F1; }

.bg-red { background-color: #FEF2F2; border-left-color: #EF4444; }
.bg-red .evt-time { color: #EF4444; }

.bg-green { background-color: #ECFDF5; border-left-color: #10B981; }
.bg-green .evt-time { color: #10B981; }

/* Left Column Overrides */
.section-title { font-family: 'Playfair Display', serif !important; font-style: italic !important; font-weight: 600 !important; color: #1A2B4C !important; font-size: 1.05rem !important; margin: 0 !important; line-height: 1.2 !important; }
.section-caption { font-size: 0.72rem; color: #6C727A; margin: 0 0 0.35rem 0 !important; }
.kpi-grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem; margin-bottom: 0.35rem; flex-shrink: 0; }
.kpi-mini-card { background: rgba(255, 255, 255, 0.9); border-radius: 4px; padding: 0.4rem 0.55rem; border: 1px solid rgba(0, 0, 0, 0.07); border-left: 3.5px solid #111A2B; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02); display: flex; flex-direction: column; justify-content: center; }
.kpi-mini-title { font-size: 0.58rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #6C727A; margin-bottom: 0.05rem; }
.kpi-mini-value { font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.15rem; font-weight: 600; color: #1A2B4C; margin: 0; line-height: 1; }
.left-feed-container { flex: 1 1 auto !important; min-height: 0 !important; overflow: hidden !important; display: flex !important; flex-direction: column !important; }
.left-feed-container > div[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255, 255, 255, 0.8) !important; border: 1px solid rgba(0, 0, 0, 0.06) !important; border-radius: 6px !important; overflow-y: auto !important; padding: 0.5rem 0.75rem !important; height: 100% !important; }
.gallery-card { background-color: #FFFFFF; border: 1px solid rgba(0, 0, 0, 0.06); border-radius: 4px; padding: 0.5rem 0.65rem; margin-bottom: 0.25rem; }
.gallery-title { font-family: 'Playfair Display', serif; font-style: italic; font-size: 0.88rem; font-weight: 600; color: #1A2B4C; margin: 0 0 0.1rem 0; }
.gallery-sub { font-size: 0.65rem; color: #6C727A; margin-bottom: 0.2rem; font-weight: 500; }
.gallery-desc { font-size: 0.72rem; color: #2D2D2D; line-height: 1.35; margin: 0; }
div[data-testid="stPopover"] { margin-bottom: 0.4rem !important; flex-shrink: 0 !important; }
div[data-testid="stPopover"] > button { background-color: #111A2B !important; color: #F8FAFC !important; border: 1px solid #D4AF37 !important; border-radius: 20px !important; padding: 0.1rem 0.75rem !important; font-size: 0.72rem !important; min-height: 28px !important; height: 28px !important; }
.stButton > button { background-color: #111A2B !important; color: #FFFFFF !important; border: 1px solid #D4AF37 !important; border-radius: 20px !important; font-size: 0.72rem !important; padding: 0.2rem 0.75rem !important; min-height: 26px !important; height: 26px !important; }
</style>
""", unsafe_allow_html=True)

# 4. Authentication Check
if not is_authenticated():
    st.markdown("""
    <style>
    [data-testid="stMainBlockContainer"] { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<p style="font-family:\'Playfair Display\', serif; font-style:italic; font-size:4rem; font-weight:600; color:#1A2B4C; margin-bottom:0.5rem; line-height:1.1;">Project Echo</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.9rem; color:#6C727A; margin-bottom:1.5rem; font-style:italic;">Sign in to access your dashboard</p>', unsafe_allow_html=True)
        email = st.text_input("Email", value="")
        password = st.text_input("Password", type="password", value="")
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        if st.button("Sign In", use_container_width=True):
            if login(email, password):
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    st.stop()

# 5. Page Layout Setup
setup_page_layout()

with st.sidebar:
    st.markdown("---")
    if st.button("Logout", key="logout_btn"):
        logout()
        st.rerun()

# 6. Session State Initialization
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.datetime.now().date()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# 7. Fetch Data & Extract Calendar Action Items based on Delivery/Due Dates
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
    
    # Left panel filters
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
        
    # Extract Action Items & Discussion Points mapped to Calendar
    raw = m.get("raw_payload", {}) or {}
    details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
    items = details.get("action_items", [])
    if not items:
        items = details.get("discussion_points", [])
        
    for item in items:
        # Prioritize delivery_date or due_date 
        date_val = item.get("delivery_date") or item.get("due_date") or m_date_raw[:10]
        if not date_val: continue
        
        try:
            d_str = datetime.datetime.strptime(date_val[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            d_str = m_date_raw[:10]
            
        title = item.get("task") or item.get("topic") or item.get("action") or "Action Required"
        owner = item.get("owner") or item.get("assigned_to") or "Team"
        
        if d_str not in calendar_events_by_date:
            calendar_events_by_date[d_str] = []
            
        # Simulate visual UI staggered times (8AM to 4PM limits)
        hour = 8 + (len(calendar_events_by_date[d_str]) * 2) % 8
        am_pm = "AM" if hour < 12 else "PM"
        disp_hour = hour if hour <= 12 else hour - 12
        
        calendar_events_by_date[d_str].append({
            "title": title,
            "owner": owner,
            "color": theme_colors[c_idx % len(theme_colors)],
            "time": f"{disp_hour}:00{am_pm}",
            "top_px": (hour - 8) * 60, # 60px slot per hour starting from 8AM
            "height_px": 80 if len(title) > 20 else 60
        })
        c_idx += 1

# 8. Dashboard Grid Composition
col_left, col_right = st.columns([1, 2.3], gap="small")

# Left Column (Overview, Date Filter, Feed)
with col_left:
    with st.container(border=True):
        st.markdown('<div class="dashboard-left-card-scope"></div>', unsafe_allow_html=True)
        
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
                selected_dates = st.date_input("Date Range", value=(st.session_state["start_date"], st.session_state["end_date"]), label_visibility="collapsed")
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


# Generate the Dynamic Native Calendar Layout for Right Column
week_start = today - datetime.timedelta(days=today.weekday() + 1) # Sunday Start
if today.weekday() == 6: week_start = today

day_columns_html = ""
for i in range(7):
    curr_date = week_start + datetime.timedelta(days=i)
    curr_date_str = curr_date.strftime("%Y-%m-%d")
    day_name = curr_date.strftime("%b %-d")
    
    events_html = ""
    for evt in calendar_events_by_date.get(curr_date_str, []):
        owner_initial = evt['owner'][0].upper() if evt['owner'] else "T"
        events_html += f"""
        <div class="cal-event {evt['color']}" style="top: {evt['top_px']}px; height: {evt['height_px']}px;">
            <div class="evt-time">{evt['time']}</div>
            <div class="evt-title">{evt['title'][:45]}{"..." if len(evt['title']) > 45 else ""}</div>
            <div class="evt-avatars">
                <div class="avatar" style="background:#4B5563;">{owner_initial}</div>
            </div>
        </div>
        """
        
    day_columns_html += f"""
    <div class="cal-day-col">
        <div class="cal-day-header">
            <div class="cal-day-name">{day_name}</div>
        </div>
        <div class="cal-day-body">
            {events_html}
        </div>
    </div>
    """

# Right Column (Full Custom Native Calendar UI)
with col_right:
    with st.container(border=False):
        st.markdown('<div class="custom-calendar-scope"></div>', unsafe_allow_html=True)
        
        # Remove indentation on this block so Streamlit doesn't render it as a Markdown Code Block
        calendar_html = textwrap.dedent(f"""
<div class="cal-header-bar">
    <h1 class="cal-title">Calendar</h1>
    <button class="btn-add-schedule">+ Add New Schedule</button>
</div>

<div class="cal-app-container">
    <!-- Sidebar Navigation -->
    <div class="cal-sidebar">
        <div class="cal-dropdown">
            <span>📅 All Calendar</span>
            <span style="color:#9CA3AF; font-size:0.7rem;">▼</span>
        </div>
        
        <div class="mini-cal-header">
            <span>{today.strftime('%B %Y')}</span>
            <div>
                <span style="color:#9CA3AF; cursor:pointer; margin-right:8px;">&lt;</span>
                <span style="color:#9CA3AF; cursor:pointer;">&gt;</span>
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
        
        <hr style="border:0; border-top:1px solid #E5E7EB; margin-bottom:1.5rem;">
        
        <div class="my-schedule-title">My Schedule <span style="color:#9CA3AF; transform: rotate(180deg); display:inline-block; font-size:0.7rem;">▼</span></div>
        <ul class="schedule-list">
            <li class="schedule-item"><input type="checkbox" checked> Schedule Meeting</li>
            <li class="schedule-item"><input type="checkbox" checked> Project Review</li>
            <li class="schedule-item"><input type="checkbox" checked> Online Meeting</li>
            <li class="schedule-item"><input type="checkbox"> Recess Break</li>
            <li class="schedule-item"><input type="checkbox"> Coffee Date</li>
            <li class="schedule-item"><input type="checkbox"> Other</li>
        </ul>
    </div>
    
    <!-- Main Calendar Timetable -->
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
