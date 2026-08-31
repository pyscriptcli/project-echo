# pages/4_tasks.py
import sys
import os
import hashlib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import date, timedelta, datetime
import calendar
import pandas as pd

from utils.auth import require_auth
from utils.db import get_supabase_client, fetch_meeting_archives
from components.sidebar import setup_page_layout

# 1. Page config (must be first)
st.set_page_config(
    page_title="Project Echo - Task Board",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Render the custom navigation bar
setup_page_layout()

# 3. Authentication check
require_auth()

# 4. Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

/* Hide Streamlit chrome */
header[data-testid="stHeader"], .stApp > header, [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu, footer,
section[data-testid="stSidebar"], [data-testid="collapsedControl"],
button[data-testid="stSidebarCollapseButton"], button[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarNav"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.stApp {
    background-color: #F3EFE6 !important;
    background-image: linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

.block-container {
    padding-top: 1rem !important;
    padding-right: 1.5rem !important;
    padding-left: 1.5rem !important;
}

:root {
    --bg: #F3EFE6;
    --surface: #FFFFFF;
    --ink: #1A2B4C;
    --muted: #6C727A;
    --gold: #D4AF37;
    --danger: #E74C3C;
    --radius: 6px;
    --control-height: 28px;
    --space-xs: 2px;
    --space-sm: 4px;
    --space-md: 8px;
    --space-lg: 16px;
}

h3 {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    font-size: 1.35rem !important;
    margin-bottom: 0.2rem !important;
}

/* ===================== GLOBAL CONTROLS ===================== */
.stButton > button,
[data-testid="stBaseButton-secondary"] {
    height: var(--control-height) !important;
    min-height: var(--control-height) !important;
    border-radius: var(--radius) !important;
    font-size: 0.75rem !important;
    padding: 0 0.6rem !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid rgba(26, 43, 76, 0.15) !important;
    box-shadow: none !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover,
[data-testid="stBaseButton-secondary"]:hover {
    border-color: var(--gold) !important;
    color: var(--ink) !important;
    background: #FFFDF6 !important;
    box-shadow: 0 1px 3px rgba(212, 175, 55, 0.2) !important;
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

/* Modal */
[data-testid="stDialog"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 0.4rem 0.4rem 0 0.4rem !important;
}
[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}

/* ===================== BOARD VIEW ===================== */
.board-column {
    background: rgba(255, 255, 255, 0.25) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}

.board-column-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.25rem 0.15rem 0.5rem 0.15rem;
    margin-bottom: 0.4rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.board-col-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--ink);
    display: flex;
    align-items: center;
    gap: 5px;
}
.board-col-count {
    font-size: 0.68rem;
    color: var(--muted);
    background: rgba(0, 0, 0, 0.04);
    border-radius: 10px;
    padding: 1px 8px;
}
.board-col-overdue {
    font-size: 0.65rem;
    color: var(--danger);
    font-weight: 600;
}

.task-card {
    background: var(--surface);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: var(--radius);
    padding: 0.5rem 0.55rem;
    margin-bottom: 0.35rem;
    transition: all 0.15s ease;
}
.task-card:hover {
    border-color: rgba(212, 175, 55, 0.5);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.task-card-header {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 2px;
}
.task-status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot-todo { background: #E67E22; }
.dot-in_progress { background: #2980B9; }
.dot-done { background: #27AE60; }

.task-card-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.3;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.task-card-desc {
    font-size: 0.7rem;
    color: #666;
    line-height: 1.3;
    margin-bottom: 0.3rem;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.task-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
    margin-top: 0.2rem;
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

.card-actions {
    margin-top: 0.25rem;
}

/* ===================== CALENDAR VIEW ===================== */
.cal-scope [data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
}
.cal-scope div[data-testid="stHorizontalBlock"] > div {
    display: flex !important;
    flex-direction: column !important;
}

.cal-filter-row {
    display: flex;
    align-items: center;
    gap: 6px;
}
.cal-filter-row .stSelectbox,
.cal-filter-row .stDateInput {
    flex-shrink: 1;
}
.cal-filter-row [data-testid="stBaseButton-secondary"] {
    width: 28px !important;
    padding: 0 !important;
}

/* Calendar month cell container */
.cal-month-cell {
    background: var(--surface);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: var(--radius);
    padding: 4px;
    min-height: 78px;
    height: 100% !important;
    box-sizing: border-box;
    transition: border-color 0.15s ease;
}
.cal-month-cell:hover { border-color: rgba(212, 175, 55, 0.4); }
.cal-month-cell.dim { background: rgba(0, 0, 0, 0.02); border: none; }
.cal-month-cell.weekend { background: #111A2B; border-color: #111A2B; }
.cal-month-cell.today { border: 2px solid var(--gold); }

.cal-month-day-num {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--ink);
    padding: 1px 2px 3px 2px;
}
.cal-month-cell.weekend .cal-month-day-num { color: #fff; }

/* Event buttons inside month cells — minimal tag style */
.cal-month-cell button {
    background: #F6F5F2;
    border-radius: 3px;
    font-size: 0.62rem;
    padding: 1px 3px;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
    transition: background 0.15s ease;
    display: block;
    width: 100%;
    height: auto !important;
    min-height: 18px !important;
    border: 1px solid transparent !important;
}
.cal-month-cell button:hover {
    background: #EAE9E4 !important;
    border-color: rgba(212, 175, 55, 0.3) !important;
}
.cal-month-cell button.overdue { border-left: 2px solid var(--danger) !important; }
.cal-month-cell button.meeting-action { background: rgba(99, 102, 241, 0.1); }
.cal-month-cell.weekend button { background: rgba(255, 255, 255, 0.1); color: #fff; }
.cal-month-cell.weekend button .initials { color: var(--gold); }

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

# 5. Helper functions & Constants
SPECIFIC_PEOPLE = [
    "Sondi Tuazon", "Meliza Zapata", "Dykstra Pineda", "Kristina Balajadia",
    "Carlo Medina", "Cedtrix Rena", "Dave Policarpio", "Irish Rima"
]
GROUP_OPTIONS = ["All Team Members", "All Advisors"]

supabase = get_supabase_client()


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


def parse_calendar_date(raw_val):
    if not raw_val:
        return None
    raw_s = str(raw_val).strip()
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw_s[:10], fmt).date()
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
    today = date.today()
    if status != "done" and due_dt < today:
        days = (today - due_dt).days
        return f"Overdue · {days}d", "overdue"
    if due_dt == today:
        return "Today", "due-today"
    if due_dt == today + timedelta(days=1):
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


def handle_status_change(task_id):
    new_status = st.session_state.get(f"status_{task_id}")
    update_task(task_id, new_status)


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


# 6. Fetch data
tasks = fetch_tasks()
meetings = fetch_meeting_archives(limit=100)
existing_discussion_ids = {t.get('discussion_point_id') for t in tasks if t.get('discussion_point_id')}


# ===================== CALENDAR DATA HELPERS =====================
def build_calendar_events():
    events = []
    today = date.today()

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
            "description": t.get("description", ""),
            "overdue": due_date < today and status != "done",
        })

    for m in meetings:
        m_id = m.get("meeting_id")
        client_name = m.get("client_name", "Meeting")
        table_items = m.get("table_items") or []
        for idx, item in enumerate(table_items):
            action = item.get("Action Plan") or item.get("Discussion Points", "")
            if not action:
                continue
            due_date = parse_calendar_date(item.get("Indicative Delivery Date", ""))
            if not due_date:
                continue
            events.append({
                "id": f"meeting_{m_id}_{idx}",
                "title": str(action)[:60],
                "date": due_date,
                "source": "meeting_action",
                "status": "n/a",
                "assignee": item.get("Person-in-charge", ""),
                "meeting_id": m_id,
                "meeting_label": client_name,
                "description": item.get("Discussion Points", ""),
                "overdue": due_date < today,
            })

    return events


def apply_calendar_filters(events, assignee_filters, status_filters, meeting_filter, start_date, end_date):
    result = []
    for e in events:
        if not (start_date <= e["date"] <= end_date):
            continue

        # Assignee filter (multiselect)
        if assignee_filters and "All Assignees" not in assignee_filters:
            if "Unassigned" in assignee_filters:
                if e.get("assignee"):
                    continue
            else:
                match = False
                for f in assignee_filters:
                    if f in GROUP_OPTIONS:
                        if e.get("assignee") == f:
                            match = True
                            break
                    elif f in SPECIFIC_PEOPLE:
                        if f in (e.get("assignee") or ""):
                            match = True
                            break
                if not match:
                    continue

        # Status filter (only applies to tasks)
        if e["source"] == "task" and status_filters and e["status"] not in status_filters:
            continue

        # Meeting search filter
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
    line2 = evt.get("meeting_label") or ("Meeting: " + (evt.get("meeting_id") or "—")) if evt["source"] == "meeting_action" else "Task"
    return f"{evt['title']}\n{line2}\nDue: {format_mm_dd_yyyy(evt['date'])}"


# 6.5 Modals
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

        if st.button("Save Changes", use_container_width=True):
            update_task(task['id'], new_status, new_assignee, new_due_date)
            st.session_state.pop('selected_task', None)
            st.success("Task updated successfully!")
            st.rerun()

        st.markdown("---")
        st.markdown(f"**Status Updated By:** {task.get('status_updated_by', 'N/A')}")
        st.markdown(f"**Status Updated At:** {task.get('status_updated_at', 'Never')}")

    with right_col:
        st.markdown("### Meeting Origin")
        if meeting_details:
            st.markdown(f"**{meeting_details.get('client_name', 'Meeting Record')}**")
            st.caption(f"Date: {format_mm_dd_yyyy(parse_calendar_date(meeting_details.get('meeting_date')))}")
            st.caption(f"Prepared By: {meeting_details.get('prepared_by')}")
            st.markdown("---")
            st.markdown("**Summary:**")
            st.write(meeting_details.get('summary_md', 'No summary available.'))
        else:
            st.info("This task is not linked to a specific meeting.")

    if st.button("Close", use_container_width=True, key="close_modal_btn"):
        st.session_state.pop('selected_task', None)
        st.rerun()


@st.dialog("Create Task", width="medium")
def new_task_dialog():
    prefill_date = st.session_state.get("cal_new_task_date")

    with st.form("cal_new_task_form", clear_on_submit=True):
        st.markdown("### New Task")
        title = st.text_input("Task Title *", placeholder="e.g., Prepare Q3 report")
        st.caption("Required. Brief, actionable summary of the task.")

        description = st.text_area("Description", placeholder="Add context, links, or dependencies...")
        st.caption("Optional. One or two lines are plenty.")

        assign_type_new = st.radio("Assignment Type", ["Group", "Specific Individuals"], horizontal=True, key="cal_dlg_assign_type")

        if assign_type_new == "Group":
            assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="cal_dlg_group")
            st.caption("Assign to a whole team or group.")
        else:
            assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="cal_dlg_individuals")
            assignee = ", ".join(assignee_list)
            st.caption("Select one or more specific people.")

        due_date = st.date_input("Due Date", value=prefill_date or date.today(), key="cal_dlg_due_date")
        st.caption(f"Date format: MM-DD-YYYY · Current: {format_mm_dd_yyyy(due_date)}")

        meeting_id = st.text_input("Linked Meeting ID (optional)", key="cal_dlg_meeting", placeholder="e.g., MOM-20260831-1230")
        st.caption("Paste a meeting ID to trace the origin.")

        submitted = st.form_submit_button("Create Task", type="primary")
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                success = add_task(title, description, assignee, due_date, meeting_id if meeting_id else None)
                if success:
                    st.session_state.pop("cal_new_task_date", None)
                    st.success("Task created!")
                    st.rerun()


# 7. Page layout
st.markdown("<h3>Task Board</h3>", unsafe_allow_html=True)
st.caption("Manage tasks derived from meeting action items or create new ones.")

# 8. Tabs
tab_board, tab_import, tab_new, tab_calendar = st.tabs(["Board", "Import from Meeting", "New Task", "Calendar"])


# ---------------- BOARD TAB ----------------
with tab_board:
    if not tasks:
        st.info("No tasks yet. Create one or import from meetings.")
    else:
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        status_options = list(status_map.keys())

        def sort_by_newest(task_list):
            return sorted(task_list, key=lambda x: x.get('created_at', ''), reverse=True)

        todo_tasks = sort_by_newest([t for t in tasks if t.get('status') == 'todo'])
        in_progress_tasks = sort_by_newest([t for t in tasks if t.get('status') == 'in_progress'])
        done_tasks = sort_by_newest([t for t in tasks if t.get('status') == 'done'])

        def count_overdue(task_list):
            return sum(1 for t in task_list if parse_calendar_date(t.get('due_date')) and parse_calendar_date(t.get('due_date')) < date.today() and t.get('status') != 'done')

        col_todo, col_progress, col_done = st.columns(3)

        def render_card(task):
            task_id = task['id']
            status_class = task.get('status', 'todo')
            due_dt = parse_calendar_date(task.get('due_date'))
            due_display, due_class = get_due_chip_info(due_dt, status_class)

            assignee_initials = get_initials(task.get('assignee', '')) if task.get('assignee') else "—"

            st.markdown(f"""
                <div class="task-card">
                    <div class="task-card-header">
                        <span class="task-status-dot dot-{status_class}"></span>
                        <span class="task-card-title">{task['title']}</span>
                    </div>
                    <div class="task-card-desc">{(task.get('description') or '')[:80]}</div>
                    <div class="task-card-footer">
                        <span class="assignee-avatar">{assignee_initials}</span>
                        <span class="due-chip {due_class}">{due_display}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            c_status, c_actions = st.columns([1.7, 1])
            with c_status:
                current_index = status_options.index(task['status']) if task['status'] in status_options else 0
                st.selectbox(
                    "Status",
                    status_options,
                    index=current_index,
                    key=f"status_{task_id}",
                    label_visibility="collapsed",
                    format_func=lambda x: status_map[x],
                    on_change=handle_status_change,
                    args=(task_id,)
                )
            with c_actions:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("", icon=":material/visibility:", key=f"view_{task_id}", help="View details"):
                        st.session_state['selected_task'] = task
                        st.rerun()
                with c2:
                    if st.button("", icon=":material/delete:", key=f"del_{task_id}", help="Delete task"):
                        delete_task(task_id)
                        st.rerun()

        with col_todo:
            todo_overdue = count_overdue(todo_tasks)
            st.markdown(f"""
                <div class="board-column-header">
                    <span class="board-col-title"><span class="task-status-dot dot-todo"></span>To Do</span>
                    <span><span class="board-col-count">{len(todo_tasks)}</span>{f' <span class="board-col-overdue">· {todo_overdue} overdue</span>' if todo_overdue else ''}</span>
                </div>
            """, unsafe_allow_html=True)
            if not todo_tasks:
                st.caption("No pending tasks.")
            for task in todo_tasks:
                render_card(task)

        with col_progress:
            prog_overdue = count_overdue(in_progress_tasks)
            st.markdown(f"""
                <div class="board-column-header">
                    <span class="board-col-title"><span class="task-status-dot dot-in_progress"></span>In Progress</span>
                    <span><span class="board-col-count">{len(in_progress_tasks)}</span>{f' <span class="board-col-overdue">· {prog_overdue} overdue</span>' if prog_overdue else ''}</span>
                </div>
            """, unsafe_allow_html=True)
            if not in_progress_tasks:
                st.caption("No tasks in progress.")
            for task in in_progress_tasks:
                render_card(task)

        with col_done:
            done_overdue = count_overdue(done_tasks)
            st.markdown(f"""
                <div class="board-column-header">
                    <span class="board-col-title"><span class="task-status-dot dot-done"></span>Done</span>
                    <span><span class="board-col-count">{len(done_tasks)}</span>{f' <span class="board-col-overdue">· {done_overdue} overdue</span>' if done_overdue else ''}</span>
                </div>
            """, unsafe_allow_html=True)
            if not done_tasks:
                st.caption("No completed tasks.")
            for task in done_tasks:
                render_card(task)


# ---------------- IMPORT TAB ----------------
with tab_import:
    st.markdown("#### Import Action Items from Meetings")
    if not meetings:
        st.info("No meetings found to import from.")
    else:
        meeting_options = {m.get("meeting_id"): m.get("client_name", "Unnamed") for m in meetings}
        selected_meeting_id = st.selectbox(
            "Select Meeting",
            options=list(meeting_options.keys()),
            format_func=lambda x: f"{meeting_options[x]} ({x})"
        )
        selected_meeting = next((m for m in meetings if m.get("meeting_id") == selected_meeting_id), None)

        if selected_meeting:
            table_items = selected_meeting.get("table_items", [])
            if isinstance(table_items, list) and len(table_items) > 0:
                st.caption(f"Found {len(table_items)} action item(s). Select which to import as tasks.")
                for idx, item in enumerate(table_items):
                    with st.container(border=True):
                        c1, c2, c3, c4, c5 = st.columns([3, 3, 1.5, 1.5, 1])
                        with c1:
                            st.write(f"**Discussion:** {item.get('Discussion Points', '')[:100]}")
                        with c2:
                            st.write(f"**Action:** {item.get('Action Plan', '')[:100]}")
                        with c3:
                            due_d = parse_calendar_date(item.get('Indicative Delivery Date', ''))
                            st.write(f"**Due:** {format_mm_dd_yyyy(due_d) if due_d else item.get('Indicative Delivery Date', '')}")
                        with c4:
                            st.write(f"**PIC:** {item.get('Person-in-charge', '')}")

                        dp_id = item.get('discussion_point_id') or item.get('id') or None
                        if not dp_id:
                            dp_id = generate_stable_id(
                                selected_meeting_id,
                                item.get('Discussion Points', ''),
                                item.get('Action Plan', '')
                            )

                        if dp_id in existing_discussion_ids:
                            with c5:
                                st.success("✓")
                        else:
                            with c5:
                                import_this = st.checkbox("Import", key=f"import_{selected_meeting_id}_{idx}")
                            if import_this:
                                if st.button("Add as Task", key=f"add_{selected_meeting_id}_{idx}"):
                                    title = item.get("Action Plan") or item.get("Discussion Points", "Untitled Task")
                                    description = item.get("Discussion Points", "")
                                    assignee = item.get("Person-in-charge", "")
                                    due_date = parse_calendar_date(item.get("Indicative Delivery Date", ""))
                                    success = add_task(title, description, assignee, due_date, meeting_id=selected_meeting_id, discussion_point_id=dp_id)
                                    if success:
                                        st.success("Task added!")
                                        st.rerun()
            else:
                st.info("This meeting has no action items.")


# ---------------- NEW TASK TAB ----------------
with tab_new:
    st.markdown("#### Create New Task")
    with st.form("new_task_form", clear_on_submit=True):
        title = st.text_input("Task Title *", placeholder="e.g., Prepare Q3 report")
        st.caption("Required. Brief, actionable summary of the task.")

        description = st.text_area("Description", placeholder="Add context, links, or dependencies...")
        st.caption("Optional. One or two lines are plenty.")

        assign_type_new = st.radio("Assignment Type", ["Group", "Specific Individuals"], horizontal=True, key="assign_type_new")

        if assign_type_new == "Group":
            assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="group_select_new")
            st.caption("Assign to a whole team or group.")
        else:
            assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="individual_new")
            assignee = ", ".join(assignee_list)
            st.caption("Select one or more specific people.")

        due_date = st.date_input("Due Date", value=None)
        st.caption(f"Date format: MM-DD-YYYY · Selected: {format_mm_dd_yyyy(due_date) if due_date else 'No date selected'}")

        meeting_id = st.text_input("Linked Meeting ID (optional)", placeholder="e.g., MOM-20260831-1230", help="Paste a meeting ID to link this task.")

        submitted = st.form_submit_button("Create Task", type="primary")
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                success = add_task(title, description, assignee, due_date, meeting_id if meeting_id else None)
                if success:
                    st.success("Task created!")
                    st.rerun()


# ---------------- CALENDAR TAB ----------------
with tab_calendar:
    st.markdown('<div class="cal-scope">', unsafe_allow_html=True)

    if "tasks_cal_focus_date" not in st.session_state:
        st.session_state["tasks_cal_focus_date"] = date.today()

    # ===== COMPACT FILTER ROW =====
    filter_cols = st.columns([3.0, 1.6, 0.7, 1.8], gap="small")

    # Assignee: multiselect (visible text)
    with filter_cols[0]:
        assignee_options = ["All Assignees", "Unassigned"] + GROUP_OPTIONS + SPECIFIC_PEOPLE
        cal_assignee = st.multiselect(
            "Assignee",
            options=assignee_options,
            default=["All Assignees"],
            key="cal_assignee_filter",
            label_visibility="collapsed"
        )

    # Date picker (visible text)
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

    # Filter icon: status + meeting + unscheduled
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

            unscheduled_tasks = [t for t in tasks if not t.get("due_date")]
            show_unscheduled = st.toggle(
                f"Show unscheduled ({len(unscheduled_tasks)})",
                value=False,
                key="cal_show_unscheduled"
            )

    # View toggle
    with filter_cols[3]:
        cal_view = st.segmented_control(
            "View",
            options=["Day", "Week", "Month"],
            default="Month",
            key="tasks_cal_view",
            label_visibility="collapsed"
        )

    # Unscheduled list
    if "cal_show_unscheduled" in st.session_state and st.session_state["cal_show_unscheduled"]:
        unscheduled_tasks = [t for t in tasks if not t.get("due_date")]
        with st.container(border=False):
            st.markdown('<div class="cal-unscheduled">', unsafe_allow_html=True)
            st.markdown("**Unscheduled Tasks**")
            if not unscheduled_tasks:
                st.caption("No unscheduled tasks.")
            else:
                for ut in unscheduled_tasks:
                    initials = get_initials(ut.get('assignee', ''))
                    st.markdown(
                        f"{initials} — {ut.get('title')} — *{ut.get('assignee') or 'Unassigned'}*"
                    )
            st.markdown('</div>', unsafe_allow_html=True)

    # ===== DATE RANGE =====
    if cal_view == "Day":
        start_date = focus
        end_date = focus
    elif cal_view == "Week":
        if focus.weekday() == 6:
            week_start = focus
        else:
            week_start = focus - timedelta(days=focus.weekday() + 1)
        start_date = week_start
        end_date = week_start + timedelta(days=6)
    else:
        start_date = focus.replace(day=1)
        _, last_day = calendar.monthrange(focus.year, focus.month)
        end_date = focus.replace(day=last_day)

    # ===== BUILD EVENTS =====
    all_events = build_calendar_events()

    if "cal_status_filter" not in st.session_state:
        st.session_state["cal_status_filter"] = ["todo", "in_progress", "done"]
    if "cal_meeting_filter" not in st.session_state:
        st.session_state["cal_meeting_filter"] = ""

    filtered = apply_calendar_filters(
        all_events,
        assignee_filters=cal_assignee,
        status_filters=st.session_state["cal_status_filter"],
        meeting_filter=st.session_state["cal_meeting_filter"].strip(),
        start_date=start_date,
        end_date=end_date
    )

    events_by_date = {}
    for evt in filtered:
        d_str = evt["date"].strftime("%Y-%m-%d")
        events_by_date.setdefault(d_str, []).append(evt)

    # ===== RENDER =====
    # Day view (agenda style)
    if cal_view == "Day":
        day_str = focus.strftime("%Y-%m-%d")
        day_events = events_by_date.get(day_str, [])

        st.markdown(f"#### {format_mm_dd_yyyy(focus)}")

        if day_events:
            for evt in day_events:
                icon = get_event_icon(evt)
                label = get_event_label(evt)
                tooltip = get_event_tooltip(evt)
                if st.button(label, key=f"cal_d_{evt['id']}_{day_str}", icon=icon, help=tooltip, use_container_width=True):
                    st.session_state["cal_clicked_event"] = evt
                    st.session_state["cal_open_event"] = True
        else:
            st.caption("No events scheduled on this day.")

        if st.button("+ Add Task", key=f"cal_add_day_{day_str}", use_container_width=True):
            st.session_state["cal_new_task_date"] = focus
            st.session_state["cal_open_new_dialog"] = True

    # Week view (agenda per day)
    elif cal_view == "Week":
        if focus.weekday() == 6:
            week_start = focus
        else:
            week_start = focus - timedelta(days=focus.weekday() + 1)

        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        for i in range(7):
            day = week_start + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_events = events_by_date.get(day_str, [])

            is_today = (day == date.today())
            title_style = "color:#8C6D23; border-bottom:2px solid var(--gold);" if is_today else "color:var(--ink); border-bottom:1px solid rgba(0,0,0,0.06);"

            st.markdown(
                f"<h4 style='font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em; "
                f"padding-bottom:0.25rem; margin-bottom:0.35rem; {title_style}'>{day_names[i]} · {format_mm_dd_yyyy(day)}</h4>",
                unsafe_allow_html=True
            )

            if day_events:
                for evt in day_events:
                    icon = get_event_icon(evt)
                    label = get_event_label(evt)
                    tooltip = get_event_tooltip(evt)
                    if st.button(label, key=f"cal_w_{day_str}_{evt['id']}", icon=icon, help=tooltip, use_container_width=True):
                        st.session_state["cal_clicked_event"] = evt
                        st.session_state["cal_open_event"] = True
            else:
                st.caption("No events")
                if st.button("+", key=f"cal_add_{day_str}", icon=":material/add:", use_container_width=True, help="Add task"):
                    st.session_state["cal_new_task_date"] = day
                    st.session_state["cal_open_new_dialog"] = True

    # Month view (grid)
    else:
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdatescalendar(focus.year, focus.month)
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        header_cols = st.columns(7, gap="small")
        for i, name in enumerate(day_names):
            with header_cols[i]:
                is_weekend = (i == 0 or i == 6)
                header_style = (
                    "background:#111A2B; color:#FFFFFF; border-radius:6px 6px 0 0;"
                    if is_weekend
                    else "background:#FFFFFF; color:var(--ink);"
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
                    is_weekend = (i == 0 or i == 6)

                    if day_val.month != focus.month:
                        st.markdown(
                            "<div style='min-height:78px; background:rgba(0,0,0,0.02); border-radius:6px;'></div>",
                            unsafe_allow_html=True
                        )
                        continue

                    day_str = day_val.strftime("%Y-%m-%d")
                    day_events = events_by_date.get(day_str, [])
                    is_today = (day_val == date.today())

                    cell_class = "cal-month-cell"
                    if is_today: cell_class += " today"
                    if is_weekend: cell_class += " weekend"

                    st.markdown(f'<div class="{cell_class}">', unsafe_allow_html=True)
                    st.markdown(f"<div class='cal-month-day-num'>{day_val.day}</div>", unsafe_allow_html=True)

                    for evt in day_events[:3]:
                        icon = get_event_icon(evt)
                        label = get_event_label(evt)
                        tooltip = get_event_tooltip(evt)

                        # Add CSS class if overdue / meeting action
                        evt_class = ""
                        if evt["overdue"]: evt_class = " overdue"
                        if evt["source"] == "meeting_action": evt_class += " meeting-action"

                        # We use st.button; wrap it so we can add a class via CSS? 
                        # Instead we'll rely on the generic styling plus a key.
                        if st.button(label, key=f"cal_m_{day_str}_{evt['id']}", icon=icon, help=tooltip, use_container_width=True):
                            st.session_state["cal_clicked_event"] = evt
                            st.session_state["cal_open_event"] = True

                    if len(day_events) > 3:
                        st.markdown(f"<div class='cal-more'>+{len(day_events) - 3} more</div>", unsafe_allow_html=True)

                    if not day_events:
                        if st.button("", key=f"cal_add_{day_str}", icon=":material/add:", use_container_width=True, help="Add task"):
                            st.session_state["cal_new_task_date"] = day_val
                            st.session_state["cal_open_new_dialog"] = True

                    st.markdown('</div>', unsafe_allow_html=True)

    # ===== HANDLE CLICKS =====
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

    st.markdown('</div>', unsafe_allow_html=True)


# Trigger modal if session state is set
if 'selected_task' in st.session_state:
    open_task_details()
