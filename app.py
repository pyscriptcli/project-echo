import sys
import os
import calendar
import datetime
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
    gap: 1rem !important;
}

/* Synchronize Outer Containers */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.sync-height-scope) {
    background: transparent !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    height: calc(100vh - 80px) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.sync-height-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    gap: 0.8rem !important;
}

/* Left Panel Specifics */
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

/* Calendar Scroll Area */
.cal-scroll-area {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0.5rem;
    background: rgba(255,255,255,0.6);
    border-radius: 8px;
    border: 1px solid rgba(0,0,0,0.05);
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

/* ===== CALENDAR SPECIFIC ===== */
/* Segmented control */
.segmented-control {
    display: flex;
    background: rgba(0,0,0,0.05);
    border-radius: 20px;
    padding: 3px;
    gap: 2px;
    width: max-content;
}
.segmented-btn {
    background: transparent;
    border: none;
    border-radius: 17px;
    padding: 6px 16px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #6C727A;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
}
.segmented-btn.active {
    background: #FFFFFF;
    color: #1A2B4C;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12);
}

/* Navigation buttons */
.nav-btn {
    background: rgba(255,255,255,0.7) !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    color: #1A2B4C !important;
    border-radius: 50% !important;
    width: 36px !important;
    height: 36px !important;
    padding: 0 !important;
    font-size: 0.8rem !important;
    line-height: 1 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    transition: all 0.2s !important;
}
.nav-btn:hover {
    background: #FFFFFF !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
}
.today-btn {
    background: #111A2B !important;
    color: #fff !important;
    border: 1px solid #111A2B !important;
    border-radius: 20px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.8rem !important;
    height: 32px !important;
}

/* Search input */
.search-wrapper {
    background: rgba(255,255,255,0.7);
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    display: flex;
    align-items: center;
}
.search-wrapper input {
    border: none;
    background: transparent;
    font-size: 0.75rem;
    color: #1A2B4C;
    outline: none;
    width: 100%;
}
.search-wrapper input::placeholder {
    color: #9CA3AF;
}

/* Calendar Month Grid */
.month-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    margin-top: 10px;
}
.month-day-header {
    text-align: center;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #6C727A;
    padding: 8px 0;
    border-bottom: 1px solid rgba(0,0,0,0.05);
}
.month-cell {
    background: #FFFFFF;
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.05);
    min-height: 100px;
    padding: 6px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: box-shadow 0.2s;
}
.month-cell:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.month-cell.today {
    border-color: #111A2B;
    border-width: 2px;
}
.month-cell.dim {
    background: rgba(0,0,0,0.02);
    border: none;
    pointer-events: none;
}
.month-day-num {
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    font-size: 1rem;
    color: #1A2B4C;
    margin-bottom: 4px;
}
.month-event {
    background: #F8F7F4;
    border-radius: 4px;
    padding: 3px 5px;
    font-size: 0.6rem;
    color: #2D2D2D;
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.month-event-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}
.month-more {
    font-size: 0.6rem;
    color: #6C727A;
    padding-left: 5px;
}
</style>
""", unsafe_allow_html=True)

# 4. Auth Check
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

# 5. Page Layout Setup
setup_page_layout()

with st.sidebar:
    st.markdown("---")
    if st.button("Logout", key="logout_btn"):
        logout()
        st.rerun()

# 6. Session State
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.datetime.now().date()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# Calendar session state
if "cal_view" not in st.session_state:
    st.session_state["cal_view"] = "Month"
if "cal_focus_date" not in st.session_state:
    st.session_state["cal_focus_date"] = today
if "cal_search" not in st.session_state:
    st.session_state["cal_search"] = ""

# 7. Fetch Data & Extract Actions
supabase_records = fetch_meeting_archives(limit=100)

total_team_meetings = len(supabase_records)
total_range_meetings = 0
total_internal_meetings = 0
total_external_meetings = 0
filtered_records = []

calendar_events_by_date = {}
# Modern accent colors for the calendar tasks
hex_colors = ["#FF6B4A", "#6366F1", "#10B981", "#EF4444"]
c_idx = 0

for m in supabase_records:
    m_date_raw = str(m.get("meeting_date", ""))
    
    # Left Column metrics
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

    # Right Column Calendar tasks
    raw = m.get("raw_payload", {}) or {}
    details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
    items = details.get("action_items", [])
    if not items:
        items = details.get("discussion_points", [])

    for item in items:
        # Map to delivery date, fallback to meeting date
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

        # Assign a staggered mock time for UI purposes
        hour = 8 + (len(calendar_events_by_date[d_str]) * 2) % 8
        am_pm = "AM" if hour < 12 else "PM"
        disp_hour = hour if hour <= 12 else hour - 12

        calendar_events_by_date[d_str].append({
            "title": title,
            "owner": owner,
            "hex_color": hex_colors[c_idx % len(hex_colors)],
            "time": f"{disp_hour}:00 {am_pm}"
        })
        c_idx += 1

# 8. Dashboard Layout
col_left, col_right = st.columns([1, 2.5])

# ----- LEFT COLUMN -----
with col_left:
    with st.container(border=False):
        st.markdown('<div class="sync-height-scope"></div>', unsafe_allow_html=True)
        
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

# ----- RIGHT COLUMN (Calendar) -----
with col_right:
    with st.container(border=False):
        st.markdown('<div class="sync-height-scope"></div>', unsafe_allow_html=True)
        
        # 1. Calendar Header Controls
        header_row = st.columns([1, 1, 1, 2])
        
        # Title
        with header_row[0]:
            st.markdown('<h2 style="font-family:\'Playfair Display\', serif; font-style:italic; color:#1A2B4C; margin:0; font-size: 1.6rem;">Action Calendar</h2>', unsafe_allow_html=True)
        
        # Segmented control (Day/Week/Month)
        with header_row[1]:
            # We'll use a custom HTML segmented control with buttons
            cal_view = st.session_state["cal_view"]
            seg_html = """
            <div class="segmented-control">
            """
            for opt in ["Day", "Week", "Month"]:
                active = "active" if cal_view == opt else ""
                seg_html += f'<button class="segmented-btn {active}" onclick="window.location.href=?view={opt}">{opt}</button>'
            seg_html += "</div>"
            # Since onclick won't work in Streamlit, we'll use actual buttons in a row
            # We'll use a different approach: three buttons with CSS
            btn_cols = st.columns(3, gap="small")
            with btn_cols[0]:
                if st.button("Day", key="view_day", help="Day view"):
                    st.session_state["cal_view"] = "Day"
                    st.rerun()
            with btn_cols[1]:
                if st.button("Week", key="view_week", help="Week view"):
                    st.session_state["cal_view"] = "Week"
                    st.rerun()
            with btn_cols[2]:
                if st.button("Month", key="view_month", help="Month view"):
                    st.session_state["cal_view"] = "Month"
                    st.rerun()
            # Style the buttons as segmented control via CSS
            st.markdown("""
            <style>
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="stButton"]) {
                background: rgba(0,0,0,0.05);
                border-radius: 20px;
                padding: 3px;
                width: max-content;
            }
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="stButton"]) button {
                background: transparent !important;
                border: none !important;
                color: #6C727A !important;
                font-size: 0.75rem !important;
                font-weight: 600 !important;
                padding: 6px 16px !important;
                border-radius: 17px !important;
            }
            div[data-testid="stHorizontalBlock"]:has(button[data-testid="stButton"]:hover) button {
                background: #FFFFFF !important;
                color: #1A2B4C !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Navigation buttons
        with header_row[2]:
            nav_cols = st.columns(3, gap="small")
            with nav_cols[0]:
                if st.button("◀", key="cal_prev", help="Previous"):
                    # navigation logic
                    if st.session_state["cal_view"] == "Day":
                        st.session_state["cal_focus_date"] -= datetime.timedelta(days=1)
                    elif st.session_state["cal_view"] == "Week":
                        st.session_state["cal_focus_date"] -= datetime.timedelta(days=7)
                    else:  # Month
                        if st.session_state["cal_focus_date"].month == 1:
                            st.session_state["cal_focus_date"] = st.session_state["cal_focus_date"].replace(year=st.session_state["cal_focus_date"].year-1, month=12)
                        else:
                            st.session_state["cal_focus_date"] = st.session_state["cal_focus_date"].replace(month=st.session_state["cal_focus_date"].month-1)
                    st.rerun()
            with nav_cols[1]:
                if st.button("Today", key="cal_today", help="Go to today"):
                    st.session_state["cal_focus_date"] = today
                    st.rerun()
            with nav_cols[2]:
                if st.button("▶", key="cal_next", help="Next"):
                    if st.session_state["cal_view"] == "Day":
                        st.session_state["cal_focus_date"] += datetime.timedelta(days=1)
                    elif st.session_state["cal_view"] == "Week":
                        st.session_state["cal_focus_date"] += datetime.timedelta(days=7)
                    else:  # Month
                        if st.session_state["cal_focus_date"].month == 12:
                            st.session_state["cal_focus_date"] = st.session_state["cal_focus_date"].replace(year=st.session_state["cal_focus_date"].year+1, month=1)
                        else:
                            st.session_state["cal_focus_date"] = st.session_state["cal_focus_date"].replace(month=st.session_state["cal_focus_date"].month+1)
                    st.rerun()
        
        # Search box
        with header_row[3]:
            st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)
            st.text_input("Search", key="cal_search", placeholder="Search tasks...", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. Period label
        if st.session_state["cal_view"] == "Day":
            period_label = st.session_state["cal_focus_date"].strftime("%A, %B %d, %Y")
        elif st.session_state["cal_view"] == "Week":
            week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday())
            week_end = week_start + datetime.timedelta(days=6)
            period_label = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
        else:
            period_label = st.session_state["cal_focus_date"].strftime("%B %Y")
        
        # Count events in current period (after search filter)
        search_term = st.session_state["cal_search"].strip().lower()
        filtered_events_by_date = {}
        if search_term:
            for date_str, events in calendar_events_by_date.items():
                filtered = []
                for evt in events:
                    if search_term in evt["title"].lower() or search_term in evt["owner"].lower():
                        filtered.append(evt)
                if filtered:
                    filtered_events_by_date[date_str] = filtered
        else:
            filtered_events_by_date = calendar_events_by_date
        
        total_events = 0
        if st.session_state["cal_view"] == "Day":
            total_events = len(filtered_events_by_date.get(st.session_state["cal_focus_date"].strftime("%Y-%m-%d"), []))
        elif st.session_state["cal_view"] == "Week":
            week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday())
            for i in range(7):
                d_str = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                total_events += len(filtered_events_by_date.get(d_str, []))
        else:
            focus = st.session_state["cal_focus_date"]
            for d_str, events in filtered_events_by_date.items():
                d = datetime.datetime.strptime(d_str, "%Y-%m-%d").date()
                if d.year == focus.year and d.month == focus.month:
                    total_events += len(events)
        
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; padding: 0 0.5rem;">
            <div>
                <p style="color:#6C727A; font-size:0.8rem; margin:0;">Currently showing</p>
                <p style="font-weight:600; color:#1A2B4C; font-size:1.1rem; margin:0;">{period_label}</p>
            </div>
            <div style="font-size:0.75rem; color:#6C727A;">
                <span style="background:#fff; padding:0.2rem 0.6rem; border-radius:12px; border:1px solid rgba(0,0,0,0.05);">
                    {total_events} events total
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Scrollable calendar area
        st.markdown('<div class="cal-scroll-area">', unsafe_allow_html=True)
        
        if st.session_state["cal_view"] == "Day":
            # ----- DAY VIEW -----
            day_str = st.session_state["cal_focus_date"].strftime("%Y-%m-%d")
            events = filtered_events_by_date.get(day_str, [])
            if events:
                for evt in events:
                    st.markdown(f"""
                    <div style='background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06); border-left: 4px solid {evt["hex_color"]}; border-radius: 8px; padding: 1rem; margin-bottom: 0.8rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02);'>
                        <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
                            <div>
                                <div style='font-size: 0.7rem; color: {evt["hex_color"]}; font-weight: 700; margin-bottom: 0.3rem;'>{evt["time"]}</div>
                                <div style='font-size: 1rem; color: #1A2B4C; font-weight: 600; margin-bottom: 0.4rem;'>{evt["title"]}</div>
                                <div style='font-size: 0.8rem; color: #6C727A;'>Assigned to: <b>{evt["owner"]}</b></div>
                            </div>
                            <span style='font-size: 0.7rem; color: #6C727A; background:#F3F4F6; padding:0.2rem 0.6rem; border-radius:12px;'>Action Item</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align:center; color:#9CA3AF; font-size:0.9rem; margin-top: 3rem; font-style:italic;'>
                    No tasks scheduled for this day.
                </div>
                """, unsafe_allow_html=True)
        
        elif st.session_state["cal_view"] == "Week":
            # ----- WEEK VIEW -----
            week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday())
            day_cols = st.columns(7, gap="small")
            for i in range(7):
                curr_date = week_start + datetime.timedelta(days=i)
                curr_date_str = curr_date.strftime("%Y-%m-%d")
                day_name = curr_date.strftime("%a")
                day_num = curr_date.strftime("%d")
                
                with day_cols[i]:
                    # Day Header
                    is_today = (curr_date == today)
                    bg_color = "#111A2B" if is_today else "#FFFFFF"
                    text_color = "#FFFFFF" if is_today else "#1A2B4C"
                    border = "none" if is_today else "1px solid rgba(0,0,0,0.08)"
                    
                    st.markdown(f"""
                    <div style='text-align:center; padding: 0.6rem 0; margin-bottom: 0.8rem; border-radius: 8px; background: {bg_color}; color: {text_color}; border: {border}; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                        <div style='font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; opacity:0.9;'>{day_name}</div>
                        <div style='font-size:1.3rem; font-family:"Playfair Display", serif; font-weight:600;'>{day_num}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Events
                    events = filtered_events_by_date.get(curr_date_str, [])
                    if events:
                        for evt in events:
                            st.markdown(f"""
                            <div style='background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06); border-left: 3px solid {evt["hex_color"]}; border-radius: 6px; padding: 0.6rem; margin-bottom: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02); transition: transform 0.1s;'>
                                <div style='font-size: 0.65rem; color: {evt["hex_color"]}; font-weight: 700; margin-bottom: 0.2rem;'>{evt["time"]}</div>
                                <div style='font-size: 0.75rem; color: #1A2B4C; font-weight: 600; line-height: 1.3; margin-bottom: 0.4rem;'>{evt["title"]}</div>
                                <div style='display:flex; justify-content:space-between; align-items:center;'>
                                    <span style='font-size: 0.6rem; color: #6C727A; background:#F3F4F6; padding:0.1rem 0.4rem; border-radius:12px;'>Assigned</span>
                                    <span style='font-size: 0.65rem; color: #1A2B4C; font-weight:500;'>{evt["owner"][:10]}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div style='text-align:center; color:#9CA3AF; font-size:0.75rem; margin-top: 1.5rem; font-style:italic;'>
                            No tasks
                        </div>
                        """, unsafe_allow_html=True)
        
        elif st.session_state["cal_view"] == "Month":
            # ----- MONTH VIEW (CSS Grid) -----
            focus = st.session_state["cal_focus_date"]
            cal = calendar.Calendar(firstweekday=0)  # Monday start
            month_days = cal.monthdatescalendar(focus.year, focus.month)
            
            # Build HTML grid
            month_html = '<div class="month-grid">'
            # Day headers
            day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for name in day_names:
                month_html += f'<div class="month-day-header">{name}</div>'
            
            # Weeks
            for week in month_days:
                for date_val in week:
                    if date_val.month != focus.month:
                        month_html += '<div class="month-cell dim"></div>'
                        continue
                    
                    date_str = date_val.strftime("%Y-%m-%d")
                    events = filtered_events_by_date.get(date_str, [])
                    is_today = (date_val == today)
                    cell_class = "month-cell"
                    if is_today:
                        cell_class += " today"
                    
                    month_html += f'<div class="{cell_class}">'
                    month_html += f'<div class="month-day-num">{date_val.day}</div>'
                    
                    # Show up to 2 events
                    display_events = events[:2]
                    for evt in display_events:
                        title_short = evt["title"][:18] + "..." if len(evt["title"]) > 18 else evt["title"]
                        month_html += f'<div class="month-event"><span class="month-event-dot" style="background:{evt["hex_color"]}"></span>{title_short}</div>'
                    
                    if len(events) > 2:
                        month_html += f'<div class="month-more">+{len(events)-2} more</div>'
                    
                    month_html += '</div>'
            
            month_html += '</div>'
            
            st.markdown(month_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)  # end cal-scroll-area
