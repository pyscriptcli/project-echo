import sys
import os
import calendar
import datetime
import hashlib
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

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
    background-color: #0A1128 !important;
    font-family: 'Montserrat', sans-serif !important;
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
    background: rgba(16,30,56,0.9);
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 0;
    padding: 1rem;
    box-shadow: none;
    color: #F5F5F0;
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
    font-weight: 500;
    color: #F5F5F0;
    font-size: 1.5rem;
    margin: 0 0 0.2rem 0;
}
.section-caption {
    font-size: 0.8rem;
    color: #8A9BAE;
    margin: 0 0 0.8rem 0;
}

.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
}
.kpi-card {
    background: #101E38;
    border-radius: 0;
    padding: 0.5rem 0.65rem;
    border: 1px solid rgba(212,175,55,0.2);
    border-left: 3.5px solid #D4AF37;
}
.kpi-title {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #8A9BAE;
}
.kpi-value {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1.35rem;
    font-weight: 500;
    color: #F5F5F0;
}

.meeting-card {
    background: #101E38;
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 0;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.5rem;
}
.meeting-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 0.95rem;
    font-weight: 500;
    color: #F5F5F0;
    margin: 0 0 0.1rem 0;
}
.meeting-sub {
    font-size: 0.65rem;
    color: #8A9BAE;
    margin-bottom: 0.3rem;
}
.meeting-desc {
    font-size: 0.75rem;
    color: #C9D2DE;
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
.stButton > button,
[data-testid="stDownloadButton"] > button {
    background-color: #111A2B !important;
    color: #fff !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.75rem !important;
    min-height: 28px !important;
    height: 28px !important;
    box-shadow: 0 4px 10px rgba(26, 43, 76, 0.18) !important;
    transition: all 0.2s ease !important;
}

/* ===== tasks.py Calendar Styles ===== */
:root {
    --bg: #0A1128;
    --surface: #101E38;
    --ink: #F5F5F0;
    --muted: #8A9BAE;
    --gold: #D4AF37;
    --danger: #E5484D;
    --radius: 6px;
    --control-height: 28px;
}

h3 {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    font-size: 1.35rem !important;
    margin-bottom: 0.2rem !important;
}



.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div,
.stDateInput > div > div {
    min-height: var(--control-height) !important;
    border-radius: var(--radius) !important;
    font-size: 0.78rem !important;
    border-color: rgba(26, 43, 76, 0.15) !important;
}

.assignee-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: var(--ink);
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
    background: #F5F4F0;
    color: var(--muted);
    border: 1px solid rgba(0, 0, 0, 0.05);
    white-space: nowrap;
}
.due-chip.overdue {
    background: #FDF0EF;
    color: var(--danger);
    border-color: rgba(231, 76, 60, 0.2);
}
.due-chip.due-today {
    background: #FFF9E8;
    color: #8C6D23;
    border-color: rgba(212, 175, 55, 0.25);
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
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: var(--radius);
    padding: 4px;
    min-height: 78px;
    height: auto !important;
    box-sizing: border-box;
}
.cal-month-cell:hover { border-color: rgba(212, 175, 55, 0.4); }
.cal-month-cell.dim { background: rgba(138, 155, 174, 0.05); border: none; }
.cal-month-cell.weekend { background: rgba(212, 175, 55, 0.12); border-color: rgba(212, 175, 55, 0.3); }
.cal-month-cell.today { border: 1px solid rgba(212, 175, 55, 0.75); }

.cal-month-day-num {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--ink);
    padding: 1px 2px 3px 2px;
}
.cal-month-cell.weekend .cal-month-day-num { color: #fff; }

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
        st.error("Supabase client not initialized.")
        return []
    try:
        res = supabase.table("tasks").select("*").order("due_date", desc=False).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Failed to fetch tasks: {e}")
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
        st.error("Supabase client not initialized.")
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
        if st.button("Close", use_container_width=True):
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

        if st.button("Save Changes", use_container_width=True, type="primary"):
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

    if st.button("Close", use_container_width=True, key="close_modal_btn"):
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

        submitted = st.form_submit_button("Create Task", type="primary", use_container_width=True)
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
style_ink = "#F5F5F0"
style_gold = "#D4AF37"
style_muted = "#8A9BAE"

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

# ------------------------------------------------------------
# DASHBOARD DATE FILTER (shared by both tabs)
# ------------------------------------------------------------
_dash_fc = st.columns([3.2, 1, 1], gap="small")
with _dash_fc[0]:
    _dash_range = st.date_input(
        "Dashboard period",
        value=(st.session_state["start_date"], st.session_state["end_date"]),
        key="dash_date_range",
    )
with _dash_fc[1]:
    if st.button("This Month", key="dash_this_month", use_container_width=True):
        st.session_state["start_date"] = today.replace(day=1)
        _, _last = calendar.monthrange(today.year, today.month)
        st.session_state["end_date"] = today.replace(day=_last)
        st.rerun()
with _dash_fc[2]:
    if st.button("All", key="dash_all", use_container_width=True):
        st.session_state["start_date"] = datetime.date(2000, 1, 1)
        st.session_state["end_date"] = today
        st.rerun()

if isinstance(_dash_range, tuple) and len(_dash_range) == 2:
    if st.session_state["start_date"] != _dash_range[0] or st.session_state["end_date"] != _dash_range[1]:
        st.session_state["start_date"] = _dash_range[0]
        st.session_state["end_date"] = _dash_range[1]
        st.rerun()

# ------------------------------------------------------------
# ------------------------------------------------------------
# DASHBOARD (Team Overview KPIs)
# ------------------------------------------------------------
st.markdown('<p class="page-eyebrow">Project Echo</p>', unsafe_allow_html=True)
st.markdown('<p class="page-title">Dashboard</p>', unsafe_allow_html=True)
st.markdown(f'<p class="section-caption">Meetings & tasks for {st.session_state["start_date"].strftime("%b %d, %Y")} \u2014 {st.session_state["end_date"].strftime("%b %d, %Y")}</p>', unsafe_allow_html=True)

# Simple KPI tiles
kpi_cells = [
    ("Meetings", total_range_meetings),
    ("Open Tasks", task_open),
    ("Done", task_status["done"]),
    ("Log Days", team_days_logged),
]
kpi_html = '<div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);">'
for label, val in kpi_cells:
    kpi_html += f'<div class="kpi-card"><span class="kpi-title">{label}</span><span class="kpi-value">{val}</span></div>'
kpi_html += "</div>"
st.markdown(kpi_html, unsafe_allow_html=True)

# ------------------------------------------------------------
# LAYOUT
# ------------------------------------------------------------
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
        
        # Title + Add Task button
        title_col, add_col = st.columns([3, 1], gap="medium")
        with title_col:
            st.markdown('<h2 style="font-family:\'Cormorant Garamond\', serif; font-style:italic; color:#F5F5F0; margin:0; font-size: 1.8rem;">Calendar</h2>', unsafe_allow_html=True)
        with add_col:
            if st.button("+ Add Task", key="cal_add_task_global", use_container_width=True):
                st.session_state["cal_new_task_date"] = today
                st.session_state["cal_open_new_dialog"] = True
        
        # Filter row (from tasks.py)
        filter_cols = st.columns([2.6, 1.4, 0.55, 1.6], gap="small")

        with filter_cols[0]:
            assignee_options = ["All Assignees", "Unassigned"] + GROUP_OPTIONS + SPECIFIC_PEOPLE
            cal_assignee = st.multiselect(
                "Assignee",
                options=assignee_options,
                default=["All Assignees"],
                key="cal_assignee_filter",
                label_visibility="collapsed"
            )
        if not cal_assignee:
            cal_assignee = ["All Assignees"]

        with filter_cols[1]:
            picked_date = st.date_input(
                "Date",
                value=st.session_state["tasks_cal_focus_date"],
                key="cal_jump_date",
                label_visibility="collapsed"
            )
            if picked_date != st.session_state["tasks_cal_focus_date"]:
                st.session_state["tasks_cal_focus_date"] = picked_date

        focus = st.session_state["tasks_cal_focus_date"]

        with filter_cols[2]:
            with st.popover("", icon=":material/filter_list:", help="Filters"):
                st.markdown("**Status**")
                status_labels = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
                cal_status = st.multiselect(
                    "Status",
                    options=["todo", "in_progress", "done"],
                    default=["todo", "in_progress", "done"],
                    format_func=lambda x: status_labels[x],
                    key="cal_status_filter",
                    label_visibility="collapsed"
                )

                st.markdown("**Linked Meeting**")
                cal_meeting = st.text_input(
                    "Meeting",
                    placeholder="Meeting ID or client...",
                    key="cal_meeting_filter",
                    label_visibility="collapsed"
                )

                st.markdown("---")

                unscheduled_tasks = [t for t in tasks if not t.get("due_date")]
                show_unscheduled = st.toggle(
                    f"Unscheduled ({len(unscheduled_tasks)})",
                    value=False,
                    key="cal_show_unscheduled"
                )
                if show_unscheduled:
                    if not unscheduled_tasks:
                        st.caption("No unscheduled tasks.")
                    else:
                        for ut in unscheduled_tasks:
                            u_initials = get_initials(ut.get('assignee', ''))
                            st.markdown(
                                f"""
                                <div style="display:flex;align-items:center;gap:6px;padding:4px 0;border-bottom:1px solid rgba(0,0,0,0.04);">
                                    <span class="assignee-avatar">{u_initials}</span>
                                    <span style="flex:1;font-size:0.72rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{ut.get('title')}</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

        with filter_cols[3]:
            cal_view = st.segmented_control(
                "View",
                options=["Day", "Week", "Month"],
                default="Month",
                key="tasks_cal_view",
                label_visibility="collapsed"
            )
        cal_view = cal_view or "Month"

        # Date range based on view
        if cal_view == "Day":
            start_date = focus
            end_date = focus
        elif cal_view == "Week":
            if focus.weekday() == 6:
                week_start = focus
            else:
                week_start = focus - datetime.timedelta(days=focus.weekday() + 1)
            start_date = week_start
            end_date = week_start + datetime.timedelta(days=6)
        else:
            start_date = focus.replace(day=1)
            _, last_day = calendar.monthrange(focus.year, focus.month)
            end_date = focus.replace(day=last_day)

        # Filter events
        filtered = apply_calendar_filters(
            all_events,
            assignee_filters=cal_assignee,
            status_filters=cal_status,
            meeting_filter=(cal_meeting or "").strip(),
            start_date=start_date,
            end_date=end_date
        )

        events_by_date = {}
        for evt in filtered:
            d_str = evt["date"].strftime("%Y-%m-%d")
            events_by_date.setdefault(d_str, []).append(evt)

        # ===== DAY VIEW =====
        if cal_view == "Day":
            day_str = focus.strftime("%Y-%m-%d")
            day_events = events_by_date.get(day_str, [])

            st.markdown(f"#### {format_mm_dd_yyyy(focus)}")

            if day_events:
                for evt in day_events:
                    if st.button(
                        get_event_label(evt),
                        key=f"cal_d_{evt['id']}_{day_str}",
                        icon=get_event_icon(evt),
                        help=get_event_tooltip(evt),
                        use_container_width=True
                    ):
                        st.session_state["cal_clicked_event"] = evt
                        st.session_state["cal_open_event"] = True
            else:
                st.caption("No events scheduled on this day.")

            if st.button("+ Add Task", key=f"cal_add_day_{day_str}", use_container_width=True):
                st.session_state["cal_new_task_date"] = focus
                st.session_state["cal_open_new_dialog"] = True

        # ===== WEEK VIEW =====
        elif cal_view == "Week":
            if focus.weekday() == 6:
                week_start = focus
            else:
                week_start = focus - datetime.timedelta(days=focus.weekday() + 1)

            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

            for i in range(7):
                day = week_start + datetime.timedelta(days=i)
                day_str = day.strftime("%Y-%m-%d")
                day_events = events_by_date.get(day_str, [])
                is_today = (day == datetime.date.today())

                st.markdown(
                    f"<div style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.02em;"
                    f"padding-bottom:0.25rem;margin-bottom:0.35rem;{('color:#D4AF37;border-bottom:2px solid #D4AF37;' if is_today else 'color:#F5F5F0;border-bottom:1px solid rgba(212,175,55,0.3);')}'"
                    f">{day_names[i]} · {format_mm_dd_yyyy(day)}</div>",
                    unsafe_allow_html=True
                )

                if day_events:
                    for evt in day_events:
                        if st.button(
                            get_event_label(evt),
                            key=f"cal_w_{day_str}_{evt['id']}",
                            icon=get_event_icon(evt),
                            help=get_event_tooltip(evt),
                            use_container_width=True
                        ):
                            st.session_state["cal_clicked_event"] = evt
                            st.session_state["cal_open_event"] = True
                else:
                    st.caption("No events")
                    if st.button("", key=f"cal_add_{day_str}", icon=":material/add:",
                                 help="Add task", use_container_width=True):
                        st.session_state["cal_new_task_date"] = day
                        st.session_state["cal_open_new_dialog"] = True

        # ===== MONTH VIEW =====
        else:
            cal = calendar.Calendar(firstweekday=6)
            month_days = cal.monthdatescalendar(focus.year, focus.month)
            day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

            header_cols = st.columns(7, gap="small")
            for i, name in enumerate(day_names):
                with header_cols[i]:
                    is_weekend = (i == 0 or i == 6)
                    header_style = (
                        "background:rgba(212,175,55,0.25); color:#F5F5F0;"
                        if is_weekend
                        else "background:#101E38; color:#F5F5F0; border:1px solid rgba(212,175,55,0.25); border-bottom:none;"
                    )
                    st.markdown(
                        f"<div style='text-align:center; padding:0.4rem; font-size:0.65rem; font-weight:700; "
                        f"text-transform:uppercase; {header_style}'>{name}</div>",
                        unsafe_allow_html=True
                    )

            for week in month_days:
                week_cols = st.columns(7, gap="small")
                for i, day_val in enumerate(week):
                    with week_cols[i]:
                        in_month = (day_val.month == focus.month)
                        is_weekend = (i == 0 or i == 6)
                        is_today = (day_val == datetime.date.today())

                        with st.container(border=True):
                            if in_month:
                                dot = '<span class="today-dot"></span>' if is_today else ''
                                st.markdown(
                                    f"<div style='display:flex;align-items:center;gap:4px;font-family:Cormorant Garamond,serif;"
                                    f"font-size:0.95rem;font-weight:500;color:#F5F5F0;padding:1px 2px 3px 2px;'>{day_val.day}{dot}</div>",
                                    unsafe_allow_html=True
                                )

                                day_str = day_val.strftime("%Y-%m-%d")
                                day_events = events_by_date.get(day_str, [])

                                for evt in day_events[:3]:
                                    if st.button(
                                        get_event_label(evt),
                                        key=f"cal_m_{day_str}_{evt['id']}",
                                        icon=get_event_icon(evt),
                                        help=get_event_tooltip(evt),
                                        use_container_width=True
                                    ):
                                        st.session_state["cal_clicked_event"] = evt
                                        st.session_state["cal_open_event"] = True

                                if len(day_events) > 3:
                                    st.markdown(
                                        f"<div style='font-size:0.58rem;color:#8A9BAE;padding-left:2px;'>+{len(day_events) - 3} more</div>",
                                        unsafe_allow_html=True
                                    )

                                if not day_events:
                                    if st.button("", key=f"cal_add_{day_str}", icon=":material/add:",
                                                 help="Add task", use_container_width=True):
                                        st.session_state["cal_new_task_date"] = day_val
                                        st.session_state["cal_open_new_dialog"] = True
                            else:
                                st.markdown(
                                    f"<div style='font-family:Playfair Display,serif;font-size:0.9rem;font-weight:600;"
                                    f"color:rgba(138,155,174,0.3);padding:1px 2px 3px 2px;'>{day_val.day}</div>",
                                    unsafe_allow_html=True
                                )

        # ===== HANDLE CALENDAR CLICKS =====
        if st.session_state.pop("cal_open_event", False):
            evt = st.session_state.pop("cal_clicked_event", None)
            if evt:
                if evt["source"] == "task":
                    task = next((t for t in tasks if str(t.get("id")) == str(evt["id"])), None)
                    if task:
                        st.session_state["selected_task"] = task
                        st.rerun()
                else:
                    st.session_state["selected_meeting_id"] = evt["meeting_id"]
                    st.switch_page("pages/2_meeting_details.py")

        if st.session_state.pop("cal_open_new_dialog", False):
            new_task_dialog()

# ------------------------------------------------------------
# TASK DETAILS MODAL (if triggered)
# ------------------------------------------------------------
if 'selected_task' in st.session_state:
    open_task_details()
