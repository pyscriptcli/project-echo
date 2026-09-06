import sys
import os
import calendar
import datetime
import hashlib
import html
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import pandas as pd

from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout
from utils.auth import init_supabase, require_login, get_all_users
from utils.notebook_db import fetch_all_daily_logs

st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Montserrat:wght@400;500;600&family=Bebas+Neue&display=swap');

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
    background-color: #f4f1ec !important;
    font-family: 'Montserrat', sans-serif !important;
    color: #1b1d1e;
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
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 1rem;
    box-shadow: none;
    color: #1b1d1e;
    flex-shrink: 0;
}

.left-card-scroll {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    margin-bottom: 0.5rem;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 600;
    color: #003366;
    font-size: 1.6rem;
    margin: 0 0 0.2rem 0;
}
.section-caption {
    font-size: 0.8rem;
    color: #69727d;
    margin: 0 0 0.8rem 0;
}

.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
}
.kpi-card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 6px;
    padding: 0.5rem 0.65rem;
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-left: 3.5px solid #003366;
}
.kpi-title {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #69727d;
}
.kpi-value {
    font-family: 'Bebas Neue', 'Cormorant Garamond', serif;
    font-style: normal;
    font-size: 1.6rem;
    font-weight: 400;
    color: #003366;
}

.meeting-card {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.5rem;
}
.meeting-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1rem;
    font-weight: 600;
    color: #003366;
    margin: 0 0 0.1rem 0;
}
.meeting-sub {
    font-size: 0.65rem;
    color: #69727d;
    margin-bottom: 0.3rem;
}
.meeting-desc {
    font-size: 0.78rem;
    color: #1b1d1e;
    line-height: 1.35;
    margin: 0;
}

.dashboard-topbar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.75rem;
}
.page-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #69727d;
    text-transform: uppercase;
    margin: 0 0 0.15rem 0;
}
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 600;
    color: #003366;
    font-size: 2rem;
    line-height: 1;
    margin: 0;
}
.dash-card {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 0.75rem 0.85rem;
    margin-bottom: 0.5rem;
}
.dash-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #003366;
    line-height: 1.25;
    margin: 0 0 0.2rem 0;
}
.dash-card-meta {
    font-size: 0.68rem;
    color: #69727d;
    margin: 0;
}
.dash-card-body {
    font-size: 0.76rem;
    line-height: 1.35;
    color: #1b1d1e;
    margin: 0.25rem 0 0 0;
}
.attention-tag {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid rgba(0, 51, 102, 0.12);
    background: #ffffff;
    color: #003366;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 1px 8px;
    margin-bottom: 0.35rem;
}
.attention-tag.danger {
    color: #c53a3f;
    border-color: rgba(197, 58, 63, 0.24);
    background: #FDF0EF;
}
.attention-tag.warning {
    color: #8C6D23;
    border-color: rgba(212, 175, 55, 0.32);
    background: #FFF9E8;
}
.agenda-day {
    font-size: 0.7rem;
    font-weight: 700;
    color: #003366;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid rgba(0, 51, 102, 0.12);
    padding-bottom: 0.25rem;
    margin: 0.35rem 0;
}
.activity-row {
    display: grid;
    grid-template-columns: 120px 1fr 42px;
    gap: 0.6rem;
    align-items: center;
    font-size: 0.72rem;
    color: #1b1d1e;
    margin-bottom: 0.45rem;
}
.activity-track {
    height: 7px;
    border-radius: 999px;
    background: rgba(0, 51, 102, 0.08);
    overflow: hidden;
}
.activity-fill {
    height: 100%;
    border-radius: 999px;
    background: #003366;
}
.activity-fill.gold { background: #c9ab4c; }
.activity-fill.danger { background: #c53a3f; }
.empty-state {
    color: #69727d;
    font-size: 0.8rem;
    font-style: italic;
    padding: 0.5rem 0;
}

div[data-testid="stPopover"] { margin-bottom: 0 !important; }
div[data-testid="stPopover"] > button {
    background-color: #0c0c0e !important;
    color: #ffffff !important;
    border: 1px solid #c9ab4c !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    min-height: 32px !important;
    height: 32px !important;
}
.stButton > button,
[data-testid="stDownloadButton"] > button {
    background-color: #0c0c0e !important;
    color: #ffffff !important;
    border: 1px solid #c9ab4c !important;
    border-radius: 6px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.75rem !important;
    min-height: 28px !important;
    height: 28px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover,
[data-testid="stDownloadButton"] > button:hover,
div[data-testid="stPopover"] > button:hover {
    background-color: #003366 !important;
    border-color: #d9bc5d !important;
    color: #ffffff !important;
}

/* ===== tasks.py Calendar Styles ===== */
:root {
    --bg: #f4f1ec;
    --surface: #ffffff;
    --ink: #003366;
    --muted: #69727d;
    --gold: #c9ab4c;
    --danger: #c53a3f;
    --radius: 6px;
    --control-height: 28px;
}

h3 {
    font-family: 'Cormorant Garamond', serif !important;
    font-style: italic !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    font-size: 1.4rem !important;
    margin-bottom: 0.2rem !important;
}



.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div,
.stDateInput > div > div {
    min-height: var(--control-height) !important;
    border-radius: var(--radius) !important;
    font-size: 0.78rem !important;
    border-color: rgba(0, 51, 102, 0.2) !important;
    background: rgba(255,255,255,0.8) !important;
    color: #1b1d1e !important;
}

.assignee-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #003366;
    color: #fff;
    font-size: 0.52rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    flex-shrink: 0;
}

.due-chip {
    display: inline-flex;
    align-items: center;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.62rem;
    font-weight: 600;
    background: #ffffff;
    color: #1b1d1e;
    border: 1px solid rgba(0, 51, 102, 0.12);
    white-space: nowrap;
}
.due-chip.overdue {
    background: #FDF0EF;
    color: var(--danger);
    border-color: rgba(231, 76, 60, 0.3);
}
.due-chip.due-today {
    background: #FFF9E8;
    color: #8C6D23;
    border-color: rgba(212, 175, 55, 0.35);
}

.cal-filter-row {
    display: flex;
    align-items: center;
    gap: 6px;
}
.cal-filter-row .stSelectbox,
.cal-filter-row .stDateInput,
.cal-filter-row .stMultiselect {
    flex-shrink: 1;
}
.cal-filter-row [data-testid="stBaseButton-secondary"] {
    width: 28px !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stPopover"] > button {
    height: var(--control-height) !important;
    min-height: var(--control-height) !important;
    min-width: 32px !important;
    border-radius: var(--radius) !important;
    border: 1px solid rgba(26, 43, 76, 0.15) !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    padding: 0 8px !important;
}

.cal-month-cell {
    background: var(--surface);
    border: 1px solid rgba(0, 51, 102, 0.1);
    border-radius: var(--radius);
    padding: 4px;
    min-height: 78px;
    height: auto !important;
    box-sizing: border-box;
}
.cal-month-cell:hover { border-color: rgba(0, 51, 102, 0.35); }
.cal-month-cell.dim { background: rgba(255, 255, 255, 0.35); border: none; }
.cal-month-cell.weekend { background: rgba(0, 51, 102, 0.06); border-color: rgba(0, 51, 102, 0.18); }
.cal-month-cell.today { border: 2px solid #003366; }

.cal-month-day-num {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: 'Bebas Neue', 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--ink);
    padding: 1px 2px 3px 2px;
}
.cal-month-cell.weekend .cal-month-day-num { color: #003366; }

.today-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gold);
    display: inline-block;
    flex-shrink: 0;
}

.cal-more {
    font-size: 0.58rem;
    color: var(--muted);
    padding-left: 2px;
    margin-top: 1px;
}

.cal-unscheduled {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: var(--radius);
    padding: 0.35rem 0.5rem;
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# AUTH GATE — enforced on every page (login required)
# ------------------------------------------------------------
require_login()

supabase = init_supabase()

# ------------------------------------------------------------
# DASHBOARD (AUTHENTICATED)
# ------------------------------------------------------------
setup_page_layout()

if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.date.today()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)
if "dash_date_range" not in st.session_state:
    st.session_state["dash_date_range"] = (st.session_state["start_date"], st.session_state["end_date"])

# Calendar session state
if "tasks_cal_focus_date" not in st.session_state:
    st.session_state["tasks_cal_focus_date"] = today
if "tasks_cal_view" not in st.session_state:
    st.session_state["tasks_cal_view"] = "Month"

# ------------------------------------------------------------
# DATA FETCHING
# ------------------------------------------------------------
supabase_records = fetch_meeting_archives(limit=100)
meetings = supabase_records

def fetch_tasks():
    if not supabase:
        st.error("Data service is not ready.")
        return []
    try:
        res = supabase.table("tasks").select("*").order("due_date", desc=False).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Could not load tasks: {e}")
        return []

tasks = fetch_tasks()

# ------------------------------------------------------------
# CONSTANTS & HELPERS
# ------------------------------------------------------------
SPECIFIC_PEOPLE = [
    "Sondi Tuazon", "Meliza Zapata", "Dykstra Pineda", "Kristina Balajadia",
    "Carlo Medina", "Cedtrix Rena", "Dave Policarpio", "Irish Rima"
]
GROUP_OPTIONS = ["All Team Members", "All Advisors"]

def parse_calendar_date(raw_val):
    if not raw_val:
        return None
    raw_s = str(raw_val).strip()
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(raw_s[:10], fmt).date()
        except ValueError:
            pass
    return None

def format_mm_dd_yyyy(d):
    if d is None:
        return "No date"
    return d.strftime("%m-%d-%Y")

def get_initials(name_str):
    if not name_str:
        return "—"
    parts = name_str.replace(",", " ").split()
    initials = "".join([p[0].upper() for p in parts if p][:2])
    return initials or "—"

def get_due_chip_info(due_dt, status):
    if not due_dt:
        return "No date", ""
    today = datetime.date.today()
    if status != "done" and due_dt < today:
        days = (today - due_dt).days
        return f"Overdue · {days}d", "overdue"
    if due_dt == today:
        return "Today", "due-today"
    if due_dt == today + datetime.timedelta(days=1):
        return "Tomorrow", ""
    return format_mm_dd_yyyy(due_dt), ""

def generate_stable_id(meeting_id, discussion_text, action_text):
    source = f"{meeting_id}-{discussion_text}-{action_text}"
    return hashlib.md5(source.encode()).hexdigest()

def add_task(title, description, assignee, due_date, meeting_id=None, discussion_point_id=None):
    if not supabase:
        st.error("Data service is not ready.")
        return False
    payload = {
        "title": title.strip(),
        "description": description.strip(),
        "assignee": assignee if assignee else None,
        "due_date": due_date.isoformat() if due_date else None,
        "meeting_id": meeting_id,
        "status": "todo",
        "discussion_point_id": discussion_point_id
    }
    try:
        supabase.table("tasks").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Failed to add task: {e}")
        return False

def update_task(task_id, new_status, new_assignee=None, new_due_date=None):
    if not supabase:
        return
    try:
        update_payload = {
            "status": new_status,
            "status_updated_by": st.session_state.get("user", {}).get("username", "System"),
            "status_updated_at": "now()",
            "updated_at": "now()"
        }
        if new_assignee is not None:
            update_payload["assignee"] = new_assignee
        if new_due_date is not None:
            update_payload["due_date"] = new_due_date.isoformat()
        supabase.table("tasks").update(update_payload).eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Failed to update task: {e}")

def delete_task(task_id):
    if not supabase:
        return
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Failed to delete task: {e}")

def get_assignee_ui_state(assignee_str):
    if assignee_str in GROUP_OPTIONS:
        return "Group", assignee_str, []
    elif assignee_str:
        selected_ind = [name.strip() for name in assignee_str.split(",") if name.strip() in SPECIFIC_PEOPLE]
        if selected_ind:
            return "Specific Individuals", "", selected_ind
    return "Group", GROUP_OPTIONS[0], []

def build_calendar_events():
    events = []
    today = datetime.date.today()

    for t in tasks:
        due_date = parse_calendar_date(t.get("due_date"))
        if not due_date:
            continue
        status = t.get("status", "todo")
        events.append({
            "id": t.get("id"),
            "title": t.get("title", "Untitled Task"),
            "date": due_date,
            "source": "task",
            "status": status,
            "assignee": t.get("assignee") or "",
            "meeting_id": t.get("meeting_id"),
            "meeting_label": "",
            "overdue": due_date < today and status != "done",
        })

    for m in meetings:
        m_id = m.get("meeting_id")
        client_name = m.get("client_name", "Meeting")
        table_items = m.get("table_items") or []
        if not table_items:
            raw = m.get("raw_payload") or {}
            details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
            table_items = details.get("action_items") or []

        for idx, item in enumerate(table_items):
            action = (item.get("Action Plan") or item.get("Discussion Points") or
                      item.get("task") or item.get("topic") or item.get("action") or "")
            if not action:
                continue
            due_date = parse_calendar_date(
                item.get("Indicative Delivery Date") or item.get("delivery_date") or item.get("due_date")
            )
            if not due_date:
                continue
            assignee = item.get("Person-in-charge") or item.get("owner") or item.get("assigned_to") or ""
            events.append({
                "id": f"meeting_{m_id}_{idx}",
                "title": str(action)[:60],
                "date": due_date,
                "source": "meeting_action",
                "status": "n/a",
                "assignee": assignee,
                "meeting_id": m_id,
                "meeting_label": client_name,
                "overdue": due_date < today,
            })

    return events

def apply_calendar_filters(events, assignee_filters, status_filters, meeting_filter, start_date, end_date):
    result = []
    for e in events:
        if not (start_date <= e["date"] <= end_date):
            continue

        if assignee_filters and "All Assignees" not in assignee_filters:
            matched = False
            if "Unassigned" in assignee_filters and not e.get("assignee"):
                matched = True
            if not matched:
                for f in assignee_filters:
                    if f in GROUP_OPTIONS and e.get("assignee") == f:
                        matched = True
                        break
                    if f in SPECIFIC_PEOPLE and f in (e.get("assignee") or ""):
                        matched = True
                        break
            if not matched:
                continue

        if e["source"] == "task" and status_filters and e["status"] not in status_filters:
            continue

        if meeting_filter:
            search_text = f"{e.get('meeting_id', '')} {e.get('meeting_label', '')}".lower()
            if meeting_filter.lower() not in search_text:
                continue

        result.append(e)
    return result

def get_event_icon(evt):
    if evt["overdue"]:
        return ":material/error:"
    if evt["source"] == "meeting_action":
        return ":material/event:"
    status = evt.get("status", "todo")
    if status == "done":
        return ":material/check_circle:"
    if status == "in_progress":
        return ":material/play_circle:"
    return ":material/radio_button_unchecked:"

def get_event_label(evt):
    initials = get_initials(evt.get("assignee", ""))
    return f"{initials} · {evt['title']}"

def get_event_tooltip(evt):
    if evt["source"] == "meeting_action":
        line2 = evt.get("meeting_label") or f"Meeting: {evt.get('meeting_id') or '—'}"
    else:
        line2 = "Task"
    return f"{evt['title']}\n{line2}\nDue: {format_mm_dd_yyyy(evt['date'])}"

# ------------------------------------------------------------
# DIALOGS
# ------------------------------------------------------------
@st.dialog("Task Details", width="large")
def open_task_details():
    task = st.session_state.get('selected_task')
    if not task:
        st.warning("No task selected.")
        if st.button("Close", width="stretch"):
            st.session_state.pop('selected_task', None)
            st.rerun()
        return

    meeting_id = task.get('meeting_id')
    meeting_details = next((m for m in meetings if m.get('meeting_id') == meeting_id), None)

    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        status_options = list(status_map.keys())
        current_status = task.get('status', 'todo')
        current_index = status_options.index(current_status) if current_status in status_options else 0

        existing_due_date = parse_calendar_date(task.get('due_date'))

        st.markdown(f"### {task['title']}")
        st.caption(f"ID: {task['id']}")

        st.markdown("**Description**")
        st.write(task.get('description', 'No description provided.'))

        st.markdown("---")
        st.markdown("**Status**")
        new_status = st.selectbox(
            "Status",
            status_options,
            index=current_index,
            format_func=lambda x: status_map[x],
            label_visibility="collapsed",
            key=f"modal_status_{task['id']}"
        )

        st.markdown("**Assignee**")
        assignee_type, group_val, individuals = get_assignee_ui_state(task.get('assignee', ""))

        assign_type = st.radio(
            "Assignment Type",
            ["Group", "Specific Individuals"],
            index=0 if assignee_type == "Group" else 1,
            horizontal=True,
            label_visibility="collapsed",
            key=f"modal_assign_type_{task['id']}"
        )

        if assign_type == "Group":
            group_idx = GROUP_OPTIONS.index(group_val) if group_val in GROUP_OPTIONS else 0
            new_assignee = st.selectbox("Select Group", GROUP_OPTIONS, index=group_idx, key=f"modal_group_{task['id']}")
        else:
            new_assignee_list = st.multiselect(
                "Select Individuals",
                SPECIFIC_PEOPLE,
                default=individuals,
                key=f"modal_individuals_{task['id']}"
            )
            new_assignee = ", ".join(new_assignee_list)

        st.markdown("**Due Date**")
        new_due_date = st.date_input(
            "Due Date",
            value=existing_due_date,
            label_visibility="collapsed",
            key=f"modal_due_{task['id']}"
        )

        if st.button("Save Changes", width="stretch", type="primary"):
            update_task(task['id'], new_status, new_assignee, new_due_date)
            st.session_state.pop('selected_task', None)
            st.session_state["task_flash"] = "Task updated successfully."
            st.rerun()

        st.markdown("---")
        st.caption(f"Status Updated By: {task.get('status_updated_by') or '—'}")
        st.caption(f"Status Updated At: {task.get('status_updated_at') or '—'}")

    with right_col:
        st.markdown("### Meeting Origin")
        if meeting_details:
            st.markdown(f"**{meeting_details.get('client_name', 'Meeting Record')}**")
            st.caption(f"Date: {format_mm_dd_yyyy(parse_calendar_date(meeting_details.get('meeting_date')))}")
            st.caption(f"Prepared By: {meeting_details.get('prepared_by') or '—'}")
            st.markdown("---")
            st.markdown("**Summary**")
            st.write(meeting_details.get('summary_md', 'No summary available.'))
        else:
            st.info("This task is not linked to a specific meeting.")

    if st.button("Close", width="stretch", key="close_modal_btn"):
        st.session_state.pop('selected_task', None)
        st.rerun()

@st.dialog("Create Task", width="large")
def new_task_dialog():
    prefill_date = st.session_state.get("cal_new_task_date")

    with st.form("cal_new_task_form", clear_on_submit=True):
        st.markdown("### New Task")
        left, right = st.columns(2)

        with left:
            title = st.text_input("Task Title *", placeholder="e.g., Prepare Q3 report")
            st.caption("Required. Brief, actionable summary of the task.")

            description = st.text_area("Description", placeholder="Add context, links, or dependencies...")
            st.caption("Optional. One or two lines are plenty.")

        with right:
            assign_type_new = st.radio(
                "Assignment Type",
                ["Group", "Specific Individuals"],
                horizontal=True,
                key="cal_dlg_assign_type"
            )

            if assign_type_new == "Group":
                assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="cal_dlg_group")
                st.caption("Assign to a whole team or group.")
            else:
                assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="cal_dlg_individuals")
                assignee = ", ".join(assignee_list)
                st.caption("Select one or more specific people.")

            due_date = st.date_input("Due Date", value=prefill_date or datetime.date.today(), key="cal_dlg_due_date")
            st.caption(f"Format: MM-DD-YYYY · {format_mm_dd_yyyy(due_date)}")

            meeting_id = st.text_input(
                "Linked Meeting ID (optional)",
                key="cal_dlg_meeting",
                placeholder="e.g., MOM-20260831-1230"
            )
            st.caption("Paste a meeting ID to trace the origin.")

        submitted = st.form_submit_button("Create Task", type="primary", width="stretch")
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                success = add_task(title, description, assignee, due_date, meeting_id if meeting_id else None)
                if success:
                    st.session_state.pop("cal_new_task_date", None)
                    st.session_state["task_flash"] = "Task created successfully."
                    st.rerun()

# ------------------------------------------------------------
# METRICS & MEETING LIST (LEFT COLUMN)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# BUILD CALENDAR EVENTS
# ------------------------------------------------------------
all_events = build_calendar_events()

# ------------------------------------------------------------
# TEAM + PERSONAL STATS (dashboard)
# ------------------------------------------------------------
style_ink = "#003366"
style_gold = "#c9ab4c"
style_muted = "#69727d"

# Task status buckets
status_labels = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
task_status = {"todo": 0, "in_progress": 0, "done": 0}
task_overdue = 0
for t in tasks:
    s = t.get("status", "todo")
    task_status[s] = task_status.get(s, 0) + 1
    d = parse_calendar_date(t.get("due_date"))
    if d and d < today and s != "done":
        task_overdue += 1
task_open = task_status["todo"] + task_status["in_progress"]
task_total = len(tasks)

# Meetings-over-time: count per month (team scope = range)
meet_by_month = {}
for m in filtered_records:
    md = str(m.get("meeting_date", ""))[:10]
    try:
        pm = datetime.datetime.strptime(md, "%Y-%m-%d").date()
    except ValueError:
        continue
    key = pm.strftime("%Y-%m")
    meet_by_month[key] = meet_by_month.get(key, 0) + 1

# Daily-log activity (team, date-scoped)
dlog_rows = fetch_all_daily_logs(st.session_state["start_date"], st.session_state["end_date"])
cat_keys = ["client", "admin", "adhoc", "meeting"]
team_days_logged = len(dlog_rows)

# Per-user stats: union of task assignees (display names) + admin usernames
_user_rows = get_all_users()
user_id_to_name = {str(u.get("id")): str(u.get("username") or "").strip() for u in _user_rows}
display_set = set([name.strip() for name in SPECIFIC_PEOPLE if name.strip()])
username_set = set(v for k, v in user_id_to_name.items() if v)
all_members = sorted(display_set | username_set, key=lambda n: n.lower())

def _member_name_in_assignee(member, assignee_str):
    if not assignee_str:
        return False
    return member.lower() in str(assignee_str).lower()

person_stats = {}
for member in all_members:
    person_stats[member] = {
        "tasks_open": 0, "tasks_done": 0, "tasks_overdue": 0,
        "days_logged": 0, "cat_chars": {k: 0 for k in cat_keys},
    }
    for t in tasks:
        if _member_name_in_assignee(member, t.get("assignee")):
            s = t.get("status", "todo")
            if s == "done":
                person_stats[member]["tasks_done"] += 1
            else:
                person_stats[member]["tasks_open"] += 1
                dd = parse_calendar_date(t.get("due_date"))
                if dd and dd < today:
                    person_stats[member]["tasks_overdue"] += 1
    # daily logs for this member: match uuid -> username -> member
    member_ids = [uid for uid, nm in user_id_to_name.items() if nm == member]
    for r in dlog_rows:
        if str(r.get("user_id")) in member_ids:
            person_stats[member]["days_logged"] += 1
            for k in cat_keys:
                person_stats[member]["cat_chars"][k] += len(str(r.get(k) or ""))

def get_meeting_items(meeting):
    table_items = meeting.get("table_items") or []
    if table_items:
        return table_items
    raw = meeting.get("raw_payload") or {}
    details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
    return details.get("action_items") or []

def get_item_action(item):
    return (
        item.get("Action Plan")
        or item.get("Discussion Points")
        or item.get("task")
        or item.get("topic")
        or item.get("action")
        or ""
    )

def get_item_due_date(item):
    return parse_calendar_date(
        item.get("Indicative Delivery Date") or item.get("delivery_date") or item.get("due_date")
    )

def render_dashboard_card(tag, title, meta, body="", tag_class="", key=None, task=None, meeting_id=None):
    safe_body = html.escape(str(body or ""))
    st.markdown(
        f"""
        <div class="dash-card">
            <span class="attention-tag {tag_class}">{html.escape(str(tag))}</span>
            <p class="dash-card-title">{html.escape(str(title or "Untitled"))}</p>
            <p class="dash-card-meta">{html.escape(str(meta or ""))}</p>
            {f'<p class="dash-card-body">{safe_body}</p>' if safe_body else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if task is not None:
        if st.button("Open task", key=f"dash_task_{key}", icon=":material/open_in_new:", width="stretch"):
            st.session_state["selected_task"] = task
            st.rerun()
    elif meeting_id:
        if st.button("Open meeting", key=f"dash_meeting_{key}", icon=":material/open_in_new:", width="stretch"):
            st.session_state["selected_meeting_id"] = meeting_id
            st.switch_page("pages/2_meeting_details.py")

def render_empty_state(message):
    st.markdown(f'<div class="empty-state">{html.escape(message)}</div>', unsafe_allow_html=True)

def render_activity_row(label, count, total, kind=""):
    pct = 0 if total <= 0 else min(100, int((count / total) * 100))
    st.markdown(
        f"""
        <div class="activity-row">
            <span>{html.escape(str(label))}</span>
            <span class="activity-track"><span class="activity-fill {kind}" style="width:{pct}%;"></span></span>
            <strong>{count}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

due_soon_cutoff = today + datetime.timedelta(days=7)
overdue_tasks = []
due_soon_tasks = []
unassigned_tasks = []
for t in tasks:
    status = t.get("status", "todo")
    if status == "done":
        continue
    due_date = parse_calendar_date(t.get("due_date"))
    if due_date and due_date < today:
        overdue_tasks.append(t)
    elif due_date and today <= due_date <= due_soon_cutoff:
        due_soon_tasks.append(t)
    if not str(t.get("assignee") or "").strip():
        unassigned_tasks.append(t)

missing_due_actions = []
for m in filtered_records:
    meeting_id = m.get("meeting_id")
    meeting_label = m.get("client_name") or "Meeting record"
    for idx, item in enumerate(get_meeting_items(m)):
        action = str(get_item_action(item)).strip()
        if action and not get_item_due_date(item):
            missing_due_actions.append({
                "meeting_id": meeting_id,
                "meeting_label": meeting_label,
                "action": action,
                "idx": idx,
            })

agenda_events = sorted(
    [
        e for e in all_events
        if e["date"] >= today and e["date"] <= due_soon_cutoff and e.get("status") != "done"
    ],
    key=lambda e: (e["date"], e["title"].lower()),
)
due_soon_count = len(due_soon_tasks)

if st.session_state.pop("cal_open_new_dialog", False):
    new_task_dialog()

# ------------------------------------------------------------
# DASHBOARD CONTROLS
# ------------------------------------------------------------
st.markdown('<p class="page-eyebrow">Project Echo</p>', unsafe_allow_html=True)

top_cols = st.columns([3.8, 2.4, 1, 0.8, 1.05, 1], gap="small", vertical_alignment="bottom")
with top_cols[0]:
    st.markdown('<p class="page-title">Dashboard</p>', unsafe_allow_html=True)
    st.caption(
        f"{st.session_state['start_date'].strftime('%b %d, %Y')} - "
        f"{st.session_state['end_date'].strftime('%b %d, %Y')}"
    )
with top_cols[1]:
    _dash_range = st.date_input(
        "Dashboard period",
        value=(st.session_state["start_date"], st.session_state["end_date"]),
        key="dash_date_range",
    )
with top_cols[2]:
    if st.button("This month", key="dash_this_month", width="stretch"):
        st.session_state["start_date"] = today.replace(day=1)
        _, _last = calendar.monthrange(today.year, today.month)
        st.session_state["end_date"] = today.replace(day=_last)
        st.session_state["dash_date_range"] = (st.session_state["start_date"], st.session_state["end_date"])
        st.rerun()
with top_cols[3]:
    if st.button("All", key="dash_all", width="stretch"):
        st.session_state["start_date"] = datetime.date(2000, 1, 1)
        st.session_state["end_date"] = today
        st.session_state["dash_date_range"] = (st.session_state["start_date"], st.session_state["end_date"])
        st.rerun()
with top_cols[4]:
    if st.button("New minutes", key="dash_new_minutes", icon=":material/edit_note:", width="stretch"):
        st.switch_page("pages/1_minutes_of_the_meeting.py")
with top_cols[5]:
    if st.button("New task", key="dash_new_task", icon=":material/add_task:", width="stretch"):
        st.session_state["cal_new_task_date"] = today
        st.session_state["cal_open_new_dialog"] = True
        st.rerun()

if isinstance(_dash_range, tuple) and len(_dash_range) == 2:
    if st.session_state["start_date"] != _dash_range[0] or st.session_state["end_date"] != _dash_range[1]:
        st.session_state["start_date"] = _dash_range[0]
        st.session_state["end_date"] = _dash_range[1]
        st.rerun()

# ------------------------------------------------------------
# KPI ROW
# ------------------------------------------------------------
kpi_cells = [
    ("Meetings", total_range_meetings),
    ("Open tasks", task_open),
    ("Overdue", task_overdue),
    ("Due soon", due_soon_count),
    ("Completed", task_status["done"]),
]
kpi_html = '<div class="kpi-grid" style="grid-template-columns:repeat(5,1fr); margin:0.75rem 0 1rem 0;">'
for label, val in kpi_cells:
    kpi_html += (
        f'<div class="kpi-card"><span class="kpi-title">{html.escape(label)}</span>'
        f'<span class="kpi-value">{val}</span></div>'
    )
kpi_html += "</div>"
st.markdown(kpi_html, unsafe_allow_html=True)

# ------------------------------------------------------------
# MAIN COMMAND CENTER
# ------------------------------------------------------------
left_col, right_col = st.columns([1.35, 1], gap="medium")

with left_col:
    st.markdown('<p class="section-title">Needs attention</p>', unsafe_allow_html=True)
    st.caption("Work that can block follow-through.")

    attention_count = 0
    for idx, task in enumerate(overdue_tasks[:4]):
        due_date = parse_calendar_date(task.get("due_date"))
        render_dashboard_card(
            "Overdue",
            task.get("title", "Untitled task"),
            f"{format_mm_dd_yyyy(due_date)} · {task.get('assignee') or 'Unassigned'}",
            task.get("description", ""),
            "danger",
            key=f"overdue_{idx}_{task.get('id')}",
            task=task,
        )
        attention_count += 1

    for idx, task in enumerate(due_soon_tasks[:4]):
        due_date = parse_calendar_date(task.get("due_date"))
        render_dashboard_card(
            "Due soon",
            task.get("title", "Untitled task"),
            f"{format_mm_dd_yyyy(due_date)} · {task.get('assignee') or 'Unassigned'}",
            task.get("description", ""),
            "warning",
            key=f"soon_{idx}_{task.get('id')}",
            task=task,
        )
        attention_count += 1

    for idx, task in enumerate(unassigned_tasks[:3]):
        render_dashboard_card(
            "Unassigned",
            task.get("title", "Untitled task"),
            f"Status: {status_labels.get(task.get('status', 'todo'), 'To Do')}",
            task.get("description", ""),
            "",
            key=f"unassigned_{idx}_{task.get('id')}",
            task=task,
        )
        attention_count += 1

    for idx, action in enumerate(missing_due_actions[:3]):
        render_dashboard_card(
            "Missing date",
            action["action"][:120],
            action["meeting_label"],
            "",
            "warning",
            key=f"missing_due_{idx}_{action['meeting_id']}_{action['idx']}",
            meeting_id=action["meeting_id"],
        )
        attention_count += 1

    if attention_count == 0:
        render_empty_state("Nothing needs attention in this period.")

with right_col:
    st.markdown('<p class="section-title">Today and upcoming</p>', unsafe_allow_html=True)
    st.caption("Next seven days.")

    if agenda_events:
        last_day = None
        for idx, evt in enumerate(agenda_events[:8]):
            if evt["date"] != last_day:
                st.markdown(
                    f'<div class="agenda-day">{evt["date"].strftime("%a, %b %d")}</div>',
                    unsafe_allow_html=True,
                )
                last_day = evt["date"]
            render_dashboard_card(
                "Meeting action" if evt["source"] == "meeting_action" else status_labels.get(evt.get("status", "todo"), "Task"),
                evt["title"],
                evt.get("meeting_label") or evt.get("assignee") or "Unassigned",
                "",
                "danger" if evt.get("overdue") else "",
                key=f"agenda_{idx}_{evt['id']}",
                task=next((t for t in tasks if str(t.get("id")) == str(evt["id"])), None) if evt["source"] == "task" else None,
                meeting_id=evt.get("meeting_id") if evt["source"] == "meeting_action" else None,
            )
    else:
        render_empty_state("No scheduled work in the next seven days.")

    st.markdown('<p class="section-title" style="margin-top:1rem;">Recent meetings</p>', unsafe_allow_html=True)
    st.caption("Latest records in selected period.")
    if filtered_records:
        for idx, meeting in enumerate(filtered_records[:5]):
            meeting_id = meeting.get("meeting_id") or f"MOM-{idx}"
            summary = str(meeting.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
            render_dashboard_card(
                "Meeting",
                meeting.get("client_name") or "Meeting record",
                f"{str(meeting.get('meeting_date', 'No date'))[:10]} · {meeting.get('prepared_by') or 'Prepared by team'}",
                summary[:120],
                "",
                key=f"recent_{idx}_{meeting_id}",
                meeting_id=meeting_id,
            )
    else:
        render_empty_state("No meetings found in this period.")

st.markdown('<p class="section-title" style="margin-top:1rem;">Team activity</p>', unsafe_allow_html=True)
st.caption("Simple status counts for the selected period.")
activity_cols = st.columns(3, gap="medium")
with activity_cols[0]:
    with st.container(border=True):
        st.markdown("**Task status**")
        status_total = max(task_total, 1)
        render_activity_row("To do", task_status["todo"], status_total, "gold")
        render_activity_row("In progress", task_status["in_progress"], status_total)
        render_activity_row("Done", task_status["done"], status_total)
with activity_cols[1]:
    with st.container(border=True):
        st.markdown("**Meeting mix**")
        meeting_total = max(total_range_meetings, 1)
        render_activity_row("Internal", total_internal_meetings, meeting_total)
        render_activity_row("External", total_external_meetings, meeting_total, "gold")
        render_activity_row("Archive total", total_team_meetings, max(total_team_meetings, 1))
with activity_cols[2]:
    with st.container(border=True):
        st.markdown("**Daily logs**")
        render_activity_row("Log days", team_days_logged, max(team_days_logged, 1))
        for cat_key in cat_keys:
            filled = sum(1 for row in dlog_rows if str(row.get(cat_key) or "").strip())
            render_activity_row(cat_key.title(), filled, max(team_days_logged, 1), "gold" if cat_key == "meeting" else "")

# ------------------------------------------------------------
# TASK DETAILS MODAL (if triggered)
# ------------------------------------------------------------
if 'selected_task' in st.session_state:
    open_task_details()
