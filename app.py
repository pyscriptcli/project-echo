import sys
import os
import calendar
import datetime
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout
from utils.auth import init_supabase, login, logout, is_authenticated

st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

supabase = init_supabase()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600;700&display=swap');

/* ---- Header: hide content, NOT the element (sidebar expand button lives there) ---- */
header[data-testid="stHeader"],
.stApp > header {
    background: transparent !important;
    height: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"],
#MainMenu,
footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

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

.cal-scroll-area {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 0.5rem;
    background: rgba(255,255,255,0.6);
    border-radius: 8px;
    border: 1px solid rgba(0,0,0,0.05);
}

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

.month-cell {
    background: #FFFFFF;
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.05);
    padding: 6px;
    min-height: 80px;
    transition: box-shadow 0.2s;
    margin-bottom: 6px;
}
.month-cell:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.month-cell.today {
    border-color: #111A2B;
    border-width: 2px;
}
.month-cell.weekend {
    background: #111A2B;
    border-color: #111A2B;
}
.month-cell.dim {
    background: rgba(0,0,0,0.02);
    border: none;
}
.month-day-num {
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    font-size: 1rem;
    color: #1A2B4C;
    margin-bottom: 4px;
}
.month-cell.weekend .month-day-num {
    color: #FFFFFF;
}
.month-cell.weekend .month-more {
    color: #FFFFFF;
}
.month-task {
    background: #F8F7F4;
    border-radius: 4px;
    padding: 3px 5px;
    font-size: 0.65rem;
    color: #2D2D2D;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
    width: 100%;
    text-align: left;
    border: none;
    cursor: pointer;
    transition: background 0.2s;
}
.month-task:hover {
    background: #F0EEE6;
}
.month-cell.weekend .month-task {
    background: rgba(255,255,255,0.12);
    color: #FFFFFF;
}
.month-more {
    font-size: 0.6rem;
    color: #6C727A;
    padding-left: 5px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOGIN SCREEN (A2 + B-series + C1 + D1)
# ------------------------------------------------------------
if not is_authenticated():
    st.markdown("""
    <style>
    /* Card styling for the login container */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        border-radius: 12px !important;
        border-top: 3px solid #D4AF37 !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08) !important;
        padding: 2rem !important;
        margin: 2rem auto !important;
        max-width: 450px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .login-icon {
        text-align: center;
        margin-bottom: 0.5rem;
        color: #1A2B4C;
    }
    .login-icon svg {
        width: 56px;
        height: 56px;
        fill: none;
        stroke: currentColor;
        stroke-width: 1.5;
        stroke-linecap: round;
        stroke-linejoin: round;
    }

    .login-brand {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 2rem;
        font-weight: 600;
        color: #1A2B4C;
        text-align: center;
    }
    .login-tagline {
        font-size: 0.9rem;
        color: #6C727A;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* Inputs */
    .stTextInput input {
        background-color: #FAFAFA !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 0.75rem !important;
    }
    .stTextInput input:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 2px rgba(212,175,55,0.15) !important;
        background: #FFFFFF !important;
    }

    /* Button */
    .stFormSubmitButton > button {
        background-color: #111A2B !important;
        color: #FFFFFF !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        min-height: 36px !important;
        width: 100% !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stFormSubmitButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.12);
    }

    /* Error / warning states */
    .login-error {
        background: #FDF0EF;
        border-left: 3px solid #E74C3C;
        color: #9B1C1C;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-top: 0.75rem;
    }
    .login-warning {
        background: #FFFBEB;
        border-left: 3px solid #F59E0B;
        color: #92400E;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            # Monochrome SVG icon
            st.markdown(
                '<div class="login-icon">'
                '<svg viewBox="0 0 24 24" aria-hidden="true">'
                '<path d="M12 3a9 9 0 0 0 0 18" />'
                '<path d="M12 7a5 5 0 0 0 0 10" />'
                '<path d="M12 11a1 1 0 0 0 0 2" />'
                '</svg>'
                '</div>'
                '<div class="login-brand">Project Echo</div>'
                '<div class="login-tagline">Sign in to your AI Assistant</div>',
                unsafe_allow_html=True
            )

            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    key="login_username",
                    placeholder="Enter your username",
                    autocomplete="username"
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                    placeholder="Enter your password",
                    autocomplete="current-password"
                )
                submitted = st.form_submit_button(
                    "Sign In",
                    use_container_width=True,
                    type="primary"
                )

            if submitted:
                errors = []
                if not username.strip():
                    errors.append("Username is required.")
                if not password.strip():
                    errors.append("Password is required.")
                if errors:
                    for e in errors:
                        st.markdown(f'<div class="login-error">{e}</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Signing in..."):
                        success, error_msg, user = login(username, password)
                    if success:
                        st.toast("Logged in successfully!", icon="✅")
                        st.session_state["user"] = user
                        st.rerun()
                    else:
                        st.markdown(f'<div class="login-error">{error_msg}</div>', unsafe_allow_html=True)

            # Caps Lock heuristic warning (optional; purely cosmetic)
            if password and password.isalpha() and password.isupper():
                st.markdown(
                    '<div class="login-warning">Caps Lock is on.</div>',
                    unsafe_allow_html=True
                )

    st.stop()

# ------------------------------------------------------------
# EXISTING DASHBOARD CODE — UNCHANGED
# ------------------------------------------------------------
setup_page_layout()

if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.datetime.now().date()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

if "cal_view" not in st.session_state:
    st.session_state["cal_view"] = "Month"
if "cal_focus_date" not in st.session_state:
    st.session_state["cal_focus_date"] = today

supabase_records = fetch_meeting_archives(limit=100)

supabase_client = get_supabase_client()
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
hex_colors = ["#FF6B4A", "#6366F1", "#10B981", "#EF4444"]
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

        hour = 8 + (len(calendar_events_by_date[d_str]) * 2) % 8
        am_pm = "AM" if hour < 12 else "PM"
        disp_hour = hour if hour <= 12 else hour - 12

        calendar_events_by_date[d_str].append({
            "title": title,
            "owner": owner,
            "hex_color": hex_colors[c_idx % len(hex_colors)],
            "time": f"{disp_hour}:00 {am_pm}",
            "source": "meeting",
            "id": None,
            "description": item.get("description", ""),
            "due_date": d_str,
            "status": "todo"
        })
        c_idx += 1

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
    status = t.get("status", "todo")
    if status == "done":
        color = "#27AE60"
    elif status == "in_progress":
        color = "#2980B9"
    else:
        color = "#E67E22"

    calendar_events_by_date[d_str].append({
        "title": task_title,
        "owner": task_assignee,
        "hex_color": color,
        "time": "",
        "source": "task",
        "id": t.get("id"),
        "description": t.get("description", ""),
        "due_date": d_str,
        "status": status
    })

col_left, col_right = st.columns([1, 2.5])

with col_left:
    with st.container(border=False):
        st.markdown('<div class="sync-height-scope"></div>', unsafe_allow_html=True)
        
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
        
        st.markdown('<div class="left-card" style="padding-bottom: 0.5rem;">', unsafe_allow_html=True)
        date_label = f"{st.session_state['start_date'].strftime('%b %d')} — {st.session_state['end_date'].strftime('%b %d, %Y')}"
        with st.popover(date_label, use_container_width=True):
            p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
                st.caption("PRESETS")
                if st.button("This Week", key="btn_tw", use_container_width=True):
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

with col_right:
    with st.container(border=False):
        st.markdown('<div class="sync-height-scope"></div>', unsafe_allow_html=True)
        
        header_row = st.columns([1.5, 1.2, 1.5, 1.5])
        
        with header_row[0]:
            st.markdown('<h2 style="font-family:\'Playfair Display\', serif; font-style:italic; color:#1A2B4C; margin:0; font-size: 1.8rem;">Calendar</h2>', unsafe_allow_html=True)
        
        with header_row[1]:
            seg_cols = st.columns(3, gap="small")
            view_labels = ["Day", "Week", "Month"]
            for idx, opt in enumerate(view_labels):
                with seg_cols[idx]:
                    if st.button(opt, key=f"seg_{opt.lower()}", help=f"{opt} view"):
                        st.session_state["cal_view"] = opt
                        st.rerun()
            
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
        
        with header_row[2]:
            nav_cols = st.columns([1, 1.2, 1], gap="small")
            with nav_cols[0]:
                if st.button("◀", key="cal_prev", help="Previous"):
                    if st.session_state["cal_view"] == "Day":
                        st.session_state["cal_focus_date"] -= datetime.timedelta(days=1)
                    elif st.session_state["cal_view"] == "Week":
                        st.session_state["cal_focus_date"] -= datetime.timedelta(days=7)
                    else:
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
                    else:
                        if st.session_state["cal_focus_date"].month == 12:
                            st.session_state["cal_focus_date"] = st.session_state["cal_focus_date"].replace(year=st.session_state["cal_focus_date"].year+1, month=1)
                        else:
                            st.session_state["cal_focus_date"] = st.session_state["cal_focus_date"].replace(month=st.session_state["cal_focus_date"].month+1)
                    st.rerun()
        
        with header_row[3]:
            month_label = st.session_state["cal_focus_date"].strftime("%B %Y")
            with st.popover(month_label, use_container_width=False):
                selected_date = st.date_input("Pick a date", value=st.session_state["cal_focus_date"].replace(day=1), 
                                             min_value=datetime.date(2000,1,1), max_value=datetime.date(2100,12,31))
                if selected_date != st.session_state["cal_focus_date"].replace(day=1):
                    st.session_state["cal_focus_date"] = selected_date.replace(day=1)
                    st.rerun()
        
        if st.session_state["cal_view"] == "Day":
            period_label = st.session_state["cal_focus_date"].strftime("%A, %B %d, %Y")
        elif st.session_state["cal_view"] == "Week":
            week_start = st.session_state["cal_focus_date"] - datetime.timedelta(days=st.session_state["cal_focus_date"].weekday() + 1) if st.session_state["cal_focus_date"].weekday() != 6 else st.session_state["cal_focus_date"]
            week_end = week_start + datetime.timedelta(days=6)
            period_label = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
        else:
            period_label = st.session_state["cal_focus_date"].strftime("%B %Y")
        
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
        
        st.markdown('<div class="cal-scroll-area">', unsafe_allow_html=True)

        if st.session_state["cal_view"] == "Day":
            day_str = st.session_state["cal_focus_date"].strftime("%Y-%m-%d")
            events = calendar_events_by_date.get(day_str, [])
            if events:
                for evt in events:
                    if st.button(f"{evt['title']} - {evt['owner']}", key=f"day_evt_{evt['id']}_{evt['title']}", use_container_width=True):
                        st.session_state['selected_event'] = evt
                        st.rerun()
            else:
                st.markdown("""
                <div style='text-align:center; color:#9CA3AF; font-size:0.9rem; margin-top: 3rem; font-style:italic;'>
                    No tasks scheduled for this day.
                </div>
                """, unsafe_allow_html=True)
        
        elif st.session_state["cal_view"] == "Week":
            if st.session_state["cal_focus_date"].weekday() == 6:
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
                    
                    events = calendar_events_by_date.get(curr_date_str, [])
                    if events:
                        for evt in events:
                            if st.button(f"{evt['title']} | {evt['owner']}", key=f"wk_btn_{evt['id']}_{evt['title']}", use_container_width=True):
                                st.session_state['selected_event'] = evt
                                st.rerun()
                    else:
                        st.markdown("""
                        <div style='text-align:center; color:#9CA3AF; font-size:0.75rem; margin-top: 1.5rem; font-style:italic;'>
                            No tasks
                        </div>
                        """, unsafe_allow_html=True)
        
        elif st.session_state["cal_view"] == "Month":
            focus = st.session_state["cal_focus_date"]
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdatescalendar(focus.year, focus.month)
            
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
            header_cols = st.columns(7, gap="small")
            for i, name in enumerate(day_names):
                with header_cols[i]:
                    is_weekend = (i == 0 or i == 6)
                    header_style = "background:#111A2B; color:#FFFFFF; border-radius:6px 6px 0 0;" if is_weekend else "background:#FFFFFF; color:#1A2B4C;"
                    st.markdown(f"<div style='text-align:center; padding:0.5rem; font-size:0.65rem; font-weight:700; text-transform:uppercase; {header_style}'>{name}</div>", unsafe_allow_html=True)
            
            for week in month_days:
                week_cols = st.columns(7, gap="small")
                for i, date_val in enumerate(week):
                    with week_cols[i]:
                        is_weekend = (i == 0 or i == 6)
                        if date_val.month != focus.month:
                            st.markdown("<div style='height:60px; background:rgba(0,0,0,0.02); border-radius:6px;'></div>", unsafe_allow_html=True)
                            continue
                        
                        date_str = date_val.strftime("%Y-%m-%d")
                        events = calendar_events_by_date.get(date_str, [])
                        is_today = (date_val == today)
                        
                        cell_class = "month-cell"
                        if is_today:
                            cell_class += " today"
                        if is_weekend:
                            cell_class += " weekend"
                        
                        st.markdown(f'<div class="{cell_class}">', unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='month-day-num'>{date_val.day}</div>", unsafe_allow_html=True)
                        
                        for evt in events[:3]:
                            if st.button(evt['title'], key=f"month_{date_str}_{evt['id']}_{evt['title']}", use_container_width=True):
                                st.session_state['selected_event'] = evt
                                st.rerun()
                        
                        if len(events) > 3:
                            st.markdown(f"<div class='month-more'>+{len(events)-3} more</div>", unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

        if 'selected_event' in st.session_state:
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
            show_event_modal()
        
        st.markdown('</div>', unsafe_allow_html=True)
