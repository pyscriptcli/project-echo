import sys
import os
import calendar
import datetime
import streamlit as st

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.db import fetch_meeting_archives, get_supabase_client
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
/* Monochrome Segmented control */
.mono-segmented {
    display: flex;
    align-items: center;
    gap: 0;
    background: #FFFFFF;
    border: 1px solid rgba(0,0,0,0.1);
    border-radius: 24px;
    padding: 3px;
    width: max-content;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.mono-seg-btn {
    background: transparent;
    border: none;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #1A2B4C;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Inter', sans-serif;
}
.mono-seg-btn:hover {
    background: #F0EEE6;
}
.mono-seg-btn.active {
    background: #111A2B;
    color: #FFFFFF;
    box-shadow: 0 2px 4px rgba(0,0,0,0.12);
}

/* Navigation buttons (monochrome) */
.mono-nav-btn {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
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
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    transition: all 0.2s !important;
}
.mono-nav-btn:hover {
    background: #F0EEE6 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
}

/* Today button (monochrome) */
.mono-today-btn {
    background: #FFFFFF !important;
    color: #1A2B4C !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    border-radius: 20px !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    padding: 0.25rem 1rem !important;
    height: 32px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
.mono-today-btn:hover {
    background: #F0EEE6 !important;
}

/* Month picker button (monochrome) */
.mono-month-btn {
    background: #FFFFFF !important;
    color: #1A2B4C !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    border-radius: 20px !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 0.25rem 1rem !important;
    height: 32px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
.mono-month-btn:hover {
    background: #F0EEE6 !important;
}

/* Month Grid - Streamlit containers will handle layout, we add min-height and styling */
.month-container {
    background: #FFFFFF;
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.05);
    min-height: 100px;
    padding: 6px;
    transition: box-shadow 0.2s;
    margin-bottom: 4px;
}
.month-container:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.month-container.today {
    border-color: #111A2B;
    border-width: 2px;
}
.month-container.weekend {
    background: #111A2B;
    border-color: #111A2B;
    color: #FFFFFF;
}
.month-container.dim {
    background: rgba(0,0,0,0.02);
    border: none;
}

/* Task card button inside month cell */
.month-task-btn {
    background: #F8F7F4 !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 4px 6px !important;
    font-size: 0.65rem !important;
    color: #2D2D2D !important;
    text-align: left !important;
    width: 100% !important;
    margin-bottom: 4px !important;
    line-height: 1.2 !important;
    box-shadow: none !important;
    display: block !important;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.month-task-btn:hover {
    background: #F0EEE6 !important;
}
.month-task-btn .task-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    margin-right: 4px;
    vertical-align: middle;
}
.month-task-btn.weekend {
    background: rgba(255,255,255,0.12) !important;
    color: #FFFFFF !important;
}

/* Week view task cards (clickable) */
.week-task-btn {
    background: #FFFFFF !important;
    border: 1px solid rgba(0,0,0,0.06) !important;
    border-left: 3px solid #E67E22 !important;
    border-radius: 6px !important;
    padding: 6px !important;
    font-size: 0.75rem !important;
    color: #1A2B4C !important;
    text-align: left !important;
    width: 100% !important;
    margin-bottom: 4px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    transition: transform 0.1s;
}
.week-task-btn:hover {
    box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    transform: translateY(-1px);
}

/* Modal styling */
[data-testid="stDialog"] {
    background: #FFFFFF;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    padding: 1rem;
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

# 7. Fetch Data & Extract Actions
supabase_records = fetch_meeting_archives(limit=100)

# Fetch tasks from DB
supabase_client = get_supabase_client()  # assuming this exists
tasks_from_db = []
if supabase_client:
    try:
        res = supabase_client.table("tasks").select("*").order("due_date", desc=False).execute()
        tasks_from_db = res.data if res.data else []
    except Exception as e:
        st.warning(f"Could not fetch tasks: {e}")

total_team_meetings = len(supabase_records)
total_range_meetings = 0
total_internal_meetings = 0
total_external_meetings = 0
filtered_records = []

calendar_events_by_date = {}
# Modern accent colors for the calendar tasks
hex_colors = ["#FF6B4A", "#6366F1", "#10B981", "#EF4444"]
c_idx = 0

# Process meeting action items
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

    # Right Column Calendar tasks from meeting action items
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
            "time": f"{disp_hour}:00 {am_pm}",
            "source": "meeting",
            "id": None,  # no task ID
            "description": item.get("description", ""),
            "due_date": d_str,
            "status": "todo"
        })
        c_idx += 1

# Process tasks from DB
for t in tasks_from_db:
    due_raw = t.get("due_date")
    if not due_raw:
        continue
    try:
        d_str = datetime.datetime.strptime(due_raw[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        continue

    if d_str not in calendar_events_by_date:
        calendar_events_by_date[d_str] = []

    task_title = t.get("title") or "Untitled Task"
    task_assignee = t.get("assignee") or "Unassigned"
    # Use a deterministic color based on status or index
    status = t.get("status", "todo")
    if status == "done":
        color = "#27AE60"  # green
    elif status == "in_progress":
        color = "#2980B9"  # blue
    else:
        color = "#E67E22"  # orange

    calendar_events_by_date[d_str].append({
        "title": task_title,
        "owner": task_assignee,
        "hex_color": color,
        "time": "",  # no specific time for DB tasks
        "source": "task",
        "id": t.get("id"),
        "description": t.get("description", ""),
        "due_date": d_str,
        "status": status
    })

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
                    # Week starts Sunday
                    st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday() + 1) if today.weekday() != 6 else today
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
        
        # 1. Calendar Header Controls - Aligned and Well-Spaced
        header_row = st.columns([1.5, 1.2, 1.5, 1.5])
        
        # Title
        with header_row[0]:
            st.markdown('<h2 style="font-family:\'Playfair Display\', serif; font-style:italic; color:#1A2B4C; margin:0; font-size: 1.8rem;">Calendar</h2>', unsafe_allow_html=True)
        
        # Segmented control (Day/Week/Month) - fully monochrome
        with header_row[1]:
            seg_cols = st.columns(3, gap="small")
            view_labels = ["Day", "Week", "Month"]
            for idx, opt in enumerate(view_labels):
                with seg_cols[idx]:
                    if st.button(opt, key=f"seg_{opt.lower()}", help=f"{opt} view"):
                        st.session_state["cal_view"] = opt
                        st.rerun()
            
            # Style the segmented control
            st.markdown("""
            <style>
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_day"]),
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_week"]),
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_month"]) {
                background: #FFFFFF;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 24px;
                padding: 3px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
                display: flex;
                gap: 0;
                width: max-content;
            }
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_day"]) button,
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_week"]) button,
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_month"]) button {
                background: transparent !important;
                border: none !important;
                color: #1A2B4C !important;
                font-size: 0.75rem !important;
                font-weight: 600 !important;
                padding: 6px 16px !important;
                border-radius: 20px !important;
                box-shadow: none !important;
            }
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_day"]) button:hover,
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_week"]) button:hover,
            div[data-testid="stHorizontalBlock"]:has(button[key="seg_month"]) button:hover {
                background: rgba(0,0,0,0.05) !important;
            }
            </style>
            """, unsafe_allow_html=True)
        
        # Navigation buttons (prev, today, next) - monochrome
        with header_row[2]:
            nav_cols = st.columns([1, 1.2, 1], gap="small")
            with nav_cols[0]:
                if st.button("◀", key="cal_prev", help="Previous"):
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
        
        # Month picker - monochrome
        with header_row[3]:
            month_label = st.session_state["cal_focus_date"].strftime("%B %Y")
            with st.popover(month_label, use_container_width=False):
                selected_date = st.date_input("Pick a date", value=st.session_state["cal_focus_date"].replace(day=1), 
                                             min_value=datetime.date(2000,1,1), max_value=datetime.date(2100,12,31))
                if selected_date != st.session_state["cal_focus_date"].replace(day=1):
                    st.session_state["cal_focus_date"] = selected_date.replace(day=1)
                    st.rerun()
        
        # 2. Period label
        if st.session_state["cal_view"] == "Day":
            period_label = st.session_state["cal_focus_date"].strftime("%A, %B %d, %Y")
        elif st.session_state["cal_view"] == "Week":
            week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday() + 1) if st.session_state["cal_focus_date"].weekday() != 6 else st.session_state["cal_focus_date"]
            week_end = week_start + datetime.timedelta(days=6)
            period_label = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
        else:
            period_label = st.session_state["cal_focus_date"].strftime("%B %Y")
        
        # Count events in current period
        total_events = 0
        if st.session_state["cal_view"] == "Day":
            total_events = len(calendar_events_by_date.get(st.session_state["cal_focus_date"].strftime("%Y-%m-%d"), []))
        elif st.session_state["cal_view"] == "Week":
            week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday() + 1) if st.session_state["cal_focus_date"].weekday() != 6 else st.session_state["cal_focus_date"]
            for i in range(7):
                d_str = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                total_events += len(calendar_events_by_date.get(d_str, []))
        else:
            focus = st.session_state["cal_focus_date"]
            for d_str, events in calendar_events_by_date.items():
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
        
        # Helper to open task details modal
        def open_modal_for_event(event):
            st.session_state['selected_event'] = event
            st.rerun()
        
        # Modal definition
        @st.dialog("Task Details", width="medium")
        def show_event_modal():
            event = st.session_state.get('selected_event')
            if not event:
                st.warning("No event selected.")
                if st.button("Close", use_container_width=True):
                    st.session_state.pop('selected_event', None)
                    st.rerun()
                return
            
            st.markdown(f"**{event['title']}**")
            st.caption(f"Due: {event['due_date']} | Owner: {event['owner']}")
            st.caption(f"Source: {'Meeting' if event['source'] == 'meeting' else 'Task Database'}")
            st.markdown("---")
            st.markdown("**Description:**")
            st.write(event.get('description') or 'No description provided.')
            
            if event['source'] == 'task':
                st.markdown("**Status:**")
                status = event.get('status', 'todo')
                status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
                st.write(status_map.get(status, status))
            
            if st.button("Close", use_container_width=True):
                st.session_state.pop('selected_event', None)
                st.rerun()
        
        if st.session_state["cal_view"] == "Day":
            # ----- DAY VIEW -----
            day_str = st.session_state["cal_focus_date"].strftime("%Y-%m-%d")
            events = calendar_events_by_date.get(day_str, [])
            if events:
                for evt in events:
                    # Use a button to make it clickable
                    if st.button(f"{evt['title']} - {evt['owner']}", key=f"day_evt_{evt['id']}_{evt['title']}", use_container_width=True):
                        open_modal_for_event(evt)
            else:
                st.markdown("""
                <div style='text-align:center; color:#9CA3AF; font-size:0.9rem; margin-top: 3rem; font-style:italic;'>
                    No tasks scheduled for this day.
                </div>
                """, unsafe_allow_html=True)
        
        elif st.session_state["cal_view"] == "Week":
            # ----- WEEK VIEW (Sunday-first) -----
            if st.session_state["cal_focus_date"].weekday() == 6:  # Sunday
                week_start = st.session_state["cal_focus_date"]
            else:
                week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday() + 1)
            
            day_cols = st.columns(7, gap="small")
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            for i in range(7):
                curr_date = week_start + datetime.timedelta(days=i)
                curr_date_str = curr_date.strftime("%Y-%m-%d")
                day_name = day_names[i]
                day_num = curr_date.strftime("%d")
                is_weekend = (i == 0 or i == 6)
                is_today = (curr_date == today)
                
                with day_cols[i]:
                    # Day Header
                    if is_today:
                        bg_color = "#D4AF37"
                        text_color = "#111A2B"
                    elif is_weekend:
                        bg_color = "#111A2B"
                        text_color = "#FFFFFF"
                    else:
                        bg_color = "#FFFFFF"
                        text_color = "#1A2B4C"
                    border = "none" if is_today else "1px solid rgba(0,0,0,0.08)"
                    
                    st.markdown(f"""
                    <div style='text-align:center; padding: 0.6rem 0; margin-bottom: 0.8rem; border-radius: 8px; background: {bg_color}; color: {text_color}; border: {border}; box-shadow: 0 1px 2px rgba(0,0,0,0.02);'>
                        <div style='font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; opacity:0.9;'>{day_name}</div>
                        <div style='font-size:1.3rem; font-family:"Playfair Display", serif; font-weight:600;'>{day_num}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Events
                    events = calendar_events_by_date.get(curr_date_str, [])
                    if events:
                        for evt in events:
                            # Use a styled button for clickable card
                            btn_style = "week-task-btn"
                            if is_weekend:
                                btn_style += " weekend"
                            st.markdown(f"""
                            <button class="{btn_style}" key="wk_{evt['id']}_{evt['title']}" onclick="alert('clicked')">
                                <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:{evt['hex_color']}; margin-right:4px;"></span>
                                <b>{evt['title']}</b><br>
                                <small>{evt['owner']}</small>
                            </button>
                            """, unsafe_allow_html=True)
                            # We can't directly handle onclick in Streamlit, so we use a st.button instead
                            # For native click, we'll use st.button and style it
                            if st.button(f"{evt['title']} | {evt['owner']}", key=f"wk_btn_{evt['id']}_{evt['title']}", use_container_width=True):
                                open_modal_for_event(evt)
                    else:
                        st.markdown("""
                        <div style='text-align:center; color:#9CA3AF; font-size:0.75rem; margin-top: 1.5rem; font-style:italic;'>
                            No tasks
                        </div>
                        """, unsafe_allow_html=True)
        
        elif st.session_state["cal_view"] == "Month":
            # ----- MONTH VIEW (Sunday-first) -----
            focus = st.session_state["cal_focus_date"]
            cal = calendar.Calendar(firstweekday=6)  # Sunday first
            
            month_days = cal.monthdatescalendar(focus.year, focus.month)
            
            # We'll use st.columns for each week row
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            # Header row
            header_cols = st.columns(7, gap="small")
            for i, name in enumerate(day_names):
                with header_cols[i]:
                    is_weekend = (i == 0 or i == 6)
                    header_style = "background:#111A2B; color:#FFFFFF; border-radius:6px 6px 0 0;" if is_weekend else "background:#FFFFFF; color:#1A2B4C;"
                    st.markdown(f"<div style='text-align:center; padding:0.5rem; font-size:0.65rem; font-weight:700; text-transform:uppercase; {header_style}'>{name}</div>", unsafe_allow_html=True)
            
            # Now weeks
            for week in month_days:
                week_cols = st.columns(7, gap="small")
                for i, date_val in enumerate(week):
                    with week_cols[i]:
                        is_weekend = (i == 0 or i == 6)
                        if date_val.month != focus.month:
                            # Dim cell
                            st.markdown("<div style='height:60px; background:rgba(0,0,0,0.02); border-radius:6px;'></div>", unsafe_allow_html=True)
                            continue
                        
                        date_str = date_val.strftime("%Y-%m-%d")
                        events = calendar_events_by_date.get(date_str, [])
                        is_today = (date_val == today)
                        
                        # Build container style
                        container_class = "month-container"
                        if is_today:
                            container_class += " today"
                        if is_weekend:
                            container_class += " weekend"
                        
                        # We'll create the container with st.container
                        # Actually, to allow dynamic height and clickable buttons, we need to use st.container and put buttons inside
                        # We'll use a st.container with border=True, but we can style it with custom CSS via a wrapper class
                        with st.container(border=True):
                            # The container's border is default Streamlit; we'll style it via CSS targeting the parent
                            # We'll use a unique key to style, but simpler: we'll just rely on default styling and add CSS for month-container
                            # Actually st.container(border=True) creates a bordered container; we can override with CSS
                            # We'll add a class to the container? Not directly. We'll use st.container(border=False) and use our own HTML for the cell.
                            # Since we need interactive buttons, we need to place st.button inside the container, so we must use st.container.
                            
                            # We'll use st.container(border=False) and render an HTML div with the content, but we need buttons inside.
                            # Let's use a st.container(border=True) and add a custom class via CSS: we can use the key of the container.
                            # Actually, we can use st.container(border=True) and style it with CSS targeting the [data-testid="stVerticalBlockBorderWrapper"]? Not easy to target per cell.
                            # Better: we'll use st.container(border=True) and rely on default styling, but we can add CSS for the border color based on weekend.
                            
                            # We'll manually render the day number and tasks, then use st.button for each task.
                            # Let's do this:
                            
                            # Day number
                            num_color = "#FFFFFF" if is_weekend else "#1A2B4C"
                            st.markdown(f"<div style='font-family:Playfair Display, serif; font-size:1rem; font-weight:600; color:{num_color}; margin-bottom:4px;'>{date_val.day}</div>", unsafe_allow_html=True)
                            
                            # Tasks
                            if events:
                                # Show up to 3 tasks as buttons, and "+N more" as text
                                display_events = events[:3]
                                for evt in display_events:
                                    # Use st.button with a custom class via CSS
                                    # We'll use a key and style the button via CSS targeting [key]
                                    if st.button(f"{evt['title']}", key=f"m_{evt['id']}_{evt['title']}", use_container_width=True):
                                        open_modal_for_event(evt)
                                    # Add a small dot indicator? We'll rely on the button text.
                                if len(events) > 3:
                                    more_color = "#FFFFFF" if is_weekend else "#6C727A"
                                    st.markdown(f"<span style='font-size:0.65rem; color:{more_color};'>+{len(events)-3} more</span>", unsafe_allow_html=True)
                            else:
                                if not is_weekend:
                                    st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
                            
                            # We'll style the container with CSS:
                            # We can't easily target each container, but we can style based on the container's border attribute.
                            # Let's just rely on the default container styling and add a CSS rule to make the container look like a month cell.
                            # We'll add a CSS class by using a markdown comment? Not possible.
                            # Given the complexity, we'll use st.container(border=True) and style via CSS: 
                            # We'll add a CSS rule for [data-testid="stVerticalBlockBorderWrapper"] within the calendar area? But it will affect all.
                            # Instead, we can use a custom HTML structure for the cell, but then we lose the ability to have buttons.
                            # A workaround: we can use a st.button for each task and place them in a regular column; we can use CSS to make the button look like a card.
                            # We'll rely on the default container and style it via the parent class using `st.container(border=True)` and applying CSS to that specific container's key? There's no direct way.
                            # So we'll create the cell manually using HTML, but we need interactive buttons. We can embed an iframe? Not good.
                            # Given the constraints, we'll keep the month view using HTML as before but make the cells clickable via a button overlay? 
                            # Actually, we can use a button that covers the entire cell, but then multiple tasks would overlap.
                            # Better approach: We'll use st.container(border=True) and use the default styling, but add CSS to change the border-left color based on weekend? Not dynamic.
                            # For simplicity, we'll use the original HTML approach but add a clickable area for each date using a button positioned at the bottom.
                            # However, the user wants to click a date box to view tasks. We can make the entire cell a button that, when clicked, shows a modal with all tasks for that date. But that's not ideal because they want to click individual tasks.
                            # Given the time, I'll implement a compromise: In month view, we'll show a compact list of tasks as text with a button to view details. We'll use the st.container approach and style it with a custom CSS class using `st.container(border=True)` and a unique key via the `key` parameter? 
                            # Streamlit container doesn't have a key parameter. 
                            # We'll just use the default border and add a CSS rule for [data-testid="stVerticalBlockBorderWrapper"] to have rounded corners and a border. That's fine.
                            # We'll also add a CSS rule to differentiate weekend cells by adding a class to the parent column? Not easily.
                            # Given the complexity, I'll revert to the HTML month grid but use st.button inside the cell via using st.columns inside each cell? That would break layout.
                            
                            # I'll go with the st.container approach and accept that the weekend styling will be based on the overall column background, which we can set by CSS on the column itself (since weekend columns have different background). Actually we can set the column background using st.markdown with a wrapper.
                            
                            # Let's just implement it using st.container and style it with CSS based on a custom class using the `st.container(border=True)` and adding a CSS rule that targets `stVerticalBlockBorderWrapper` within the calendar area? But that would affect all containers.
                            
                            # I'll simplify: I'll use `st.container(border=True)` for each day cell, and apply CSS to make it look like a card. For weekend, we'll set the container's background via inline style? We can't inline style a container.
                            
                            # We'll just use the default white background and add a border-left color for weekend via CSS class added to the button? Actually we can add a wrapper div with a class using st.markdown before the container, but that doesn't wrap the container.
                            
                            # I'll propose: Use st.columns(7) for each week, and inside each column, use a `with st.container(border=True):` and then apply CSS to the parent block based on a data attribute? Not possible.
                            
                            # I'll accept the default container styling and add a CSS rule to make all containers in the month view have a consistent look. For weekend, we'll add a colored border-left via CSS using the container's index? Not possible.
                            
                            # Let's just keep the previous HTML month grid but make the task cards clickable using a trick: we can place a button inside each cell using st.button in a hidden way? No, we need to render the grid with st.columns.
                            
                            # I'll go with the st.columns approach and style the container with a custom class via the `st.container(border=True)` and use CSS to set a background color for weekend cells by wrapping the column in a div with a class. We can do that by using st.markdown to open a div, then the column content, then close the div. But the column content is generated by Streamlit, so we need to place the div around the column block. We can do that by using a `with st.container():` and inside, we call st.columns(7). Then each column is a streamlit element; we can style them with CSS using the `stHorizontalBlock`? Not per column.
                            
                            # I'll give up on per-cell weekend styling in month view and just use the original HTML grid, but add a button overlay for each task using st.button inside the HTML? No, st.button can't be inside raw HTML.
                            
                            # Alternative: Use st.columns and for each cell, we can add a `st.button` that represents the entire day, and inside the button we embed the day number and task text. But that would be a single button per day, not individual tasks. However, the requirement is to put tasks inside the date box and clicking the box opens a modal with task details. So we can make the entire date box a button! When clicked, it opens a modal showing all tasks for that day. That's acceptable.
                            
                            # Let's do that: each date cell is a st.button (full width) that displays the day number and a compact list of task titles. When clicked, it opens a modal with all tasks for that date.
                            
                            # That simplifies things. We'll do that for month view.
                            
                            # So we create a button for each day, with a key, and inside the label we show day number and tasks. The label can be HTML with multiple lines.
                            # We'll style the button to look like a calendar cell.
                            
                            # Let's implement this.
                            
                            # Create the button label as a string with HTML.
                            day_label = f"<div style='font-family:Playfair Display, serif; font-weight:600; font-size:1rem; color:{num_color};'>{date_val.day}</div>"
                            if events:
                                # Show up to 3 tasks
                                for evt in events[:3]:
                                    day_label += f"<div style='font-size:0.65rem; color:{'#FFFFFF' if is_weekend else '#2D2D2D'}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>• {evt['title']}</div>"
                                if len(events) > 3:
                                    day_label += f"<div style='font-size:0.6rem; color:{'#FFFFFF' if is_weekend else '#6C727A'};'>+{len(events)-3} more</div>"
                            
                            # Use st.button with HTML label
                            if st.button(f"{day_label}", key=f"date_{date_str}", use_container_width=True):
                                # Open a modal showing all tasks for this date
                                st.session_state['selected_date_events'] = events
                                st.rerun()
                            
                            # Style the button with CSS to look like a month cell
                            # We'll add CSS for button with key starting with "date_"
                            
            # After the loop, add CSS for the date buttons
            st.markdown("""
            <style>
            /* Style the date buttons in month view */
            div[data-testid="stButton"] > button {
                background: #FFFFFF;
                border: 1px solid rgba(0,0,0,0.05);
                border-radius: 6px;
                padding: 6px;
                text-align: left;
                height: auto;
                min-height: 80px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.02);
                transition: all 0.2s;
            }
            div[data-testid="stButton"] > button:hover {
                box-shadow: 0 2px 8px rgba(0,0,0,0.04);
                transform: translateY(-1px);
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Also add a modal for date events if selected
            if 'selected_date_events' in st.session_state:
                @st.dialog("Tasks on this date", width="medium")
                def show_date_events():
                    events = st.session_state.get('selected_date_events')
                    if events:
                        for evt in events:
                            st.markdown(f"**{evt['title']}**")
                            st.caption(f"Owner: {evt['owner']} | Due: {evt['due_date']}")
                            st.markdown("---")
                    else:
                        st.info("No tasks on this date.")
                    if st.button("Close", use_container_width=True):
                        st.session_state.pop('selected_date_events', None)
                        st.rerun()
                show_date_events()
        
        # Close the modal if selected_event is set
        if 'selected_event' in st.session_state:
            show_event_modal()
        
        st.markdown('</div>', unsafe_allow_html=True)  # end cal-scroll-area
