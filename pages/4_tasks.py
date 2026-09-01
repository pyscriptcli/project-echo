# pages/4_tasks.py
import sys
import os
import hashlib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import date, timedelta, datetime
import calendar

from utils.auth import require_login
from utils.db import get_supabase_client, fetch_meeting_archives
from components.sidebar import setup_page_layout

# 1. Page config (must be first)
st.set_page_config(
    page_title="Project Echo - Task Board",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Authentication check (must run before rendering the sidebar)
require_login()

# 3. Render the custom navigation bar
setup_page_layout()

# 4. Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

/* Hide Streamlit chrome */
header[data-testid="stHeader"], .stApp > header, [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu, footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.stApp {
    background-color: #F9F8F6 !important;
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
    --ink: #412D15;
    --muted: #8A7A5F;
    --gold: #C9B59C;
    --danger: #E74C3C;
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

/* ===================== GLOBAL CONTROLS ===================== */
.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div,
.stDateInput > div > div {
    min-height: var(--control-height) !important;
    border-radius: var(--radius) !important;
    font-size: 0.78rem !important;
    border-color: rgba(26, 43, 76, 0.15) !important;
}

/* ===================== BOARD VIEW ===================== */
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
.dot-meeting { background: #6366F1; }

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

.import-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    color: #03543F;
    background: #DEF7EC;
    border: 1px solid rgba(39, 174, 96, 0.25);
    border-radius: 10px;
    padding: 2px 8px;
    white-space: nowrap;
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
.cal-filter-row .stDateInput,
.cal-filter-row .stMultiselect {
    flex-shrink: 1;
}
.cal-filter-row [data-testid="stBaseButton-secondary"] {
    width: 28px !important;
    padding: 0 !important;
}

/* Popover (filter) */
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
.cal-month-cell.dim { background: rgba(0, 0, 0, 0.02); border: none; }
.cal-month-cell.weekend { background: #C9B59C; border-color: #C9B59C; }
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


# Select All handler (callback runs before rerun, so row checkboxes pick up state)
def handle_select_all_change(meeting_id, importable_indices):
    select_val = st.session_state.get(f"select_all_{meeting_id}", False)
    for idx in importable_indices:
        st.session_state[f"import_{meeting_id}_{idx}"] = select_val


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
                "overdue": due_date < today,
            })

    return events


def apply_calendar_filters(events, assignee_filters, status_filters, meeting_filter, start_date, end_date):
    result = []
    for e in events:
        if not (start_date <= e["date"] <= end_date):
            continue

        # Assignee filter (multiselect, OR-based)
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

        # Status filter (tasks only)
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
    if evt["source"] == "meeting_action":
        line2 = evt.get("meeting_label") or f"Meeting: {evt.get('meeting_id') or '—'}"
    else:
        line2 = "Task"
    return f"{evt['title']}\n{line2}\nDue: {format_mm_dd_yyyy(evt['date'])}"


# ===================== MODALS =====================
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

            due_date = st.date_input("Due Date", value=prefill_date or date.today(), key="cal_dlg_due_date")
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


# 7. Page layout
st.markdown("<h3>Task Board</h3>", unsafe_allow_html=True)
st.caption("Manage tasks derived from meeting action items or create new ones.")

# 8. Tabs
tab_board, tab_import, tab_new, tab_calendar = st.tabs(["Board", "Import from Meeting", "New Task", "Calendar"])


# ---------------- BOARD TAB ----------------
with tab_board:
    if "task_flash" in st.session_state:
        st.success(st.session_state.pop("task_flash"))

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
            return sum(
                1 for t in task_list
                if parse_calendar_date(t.get('due_date'))
                and parse_calendar_date(t.get('due_date')) < date.today()
                and t.get('status') != 'done'
            )

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

            c_status, c_view, c_del = st.columns([2, 0.6, 0.6], gap="small")
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
            with c_view:
                if st.button("", icon=":material/visibility:", key=f"view_{task_id}",
                             help="View details", use_container_width=True):
                    st.session_state['selected_task'] = task
                    st.rerun()
            with c_del:
                if st.button("", icon=":material/delete:", key=f"del_{task_id}",
                             help="Delete task", use_container_width=True):
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

    if "import_flash" in st.session_state:
        st.success(st.session_state.pop("import_flash"))

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

                importable_indices = []
                for idx, item in enumerate(table_items):
                    dp_id = item.get('discussion_point_id') or item.get('id') or generate_stable_id(
                        selected_meeting_id,
                        item.get('Discussion Points', ''),
                        item.get('Action Plan', '')
                    )
                    if dp_id not in existing_discussion_ids:
                        importable_indices.append(idx)

                hdr_c1, hdr_c2 = st.columns([3, 1], gap="small")
                with hdr_c1:
                    st.caption(f"Found **{len(table_items)}** action item(s) · **{len(importable_indices)}** available to import")
                with hdr_c2:
                    st.checkbox(
                        "Select All",
                        key=f"select_all_{selected_meeting_id}",
                        on_change=handle_select_all_change,
                        args=(selected_meeting_id, importable_indices)
                    )

                st.markdown("<hr style='margin:0.3rem 0 0.6rem 0; border:none; border-top:1px solid rgba(0,0,0,0.07);'>", unsafe_allow_html=True)

                for idx, item in enumerate(table_items):
                    dp_id = item.get('discussion_point_id') or item.get('id') or generate_stable_id(
                        selected_meeting_id,
                        item.get('Discussion Points', ''),
                        item.get('Action Plan', '')
                    )
                    already_imported = dp_id in existing_discussion_ids

                    action_title = item.get("Action Plan") or item.get("Discussion Points", "Untitled Task")
                    discussion_desc = item.get("Discussion Points", "")
                    due_dt = parse_calendar_date(item.get("Indicative Delivery Date", ""))
                    due_display = format_mm_dd_yyyy(due_dt) if due_dt else "No date"
                    pic = item.get("Person-in-charge", "")
                    initials = get_initials(pic)

                    st.markdown(f"""
                        <div class="task-card">
                            <div class="task-card-header">
                                <span class="task-status-dot dot-meeting"></span>
                                <span class="task-card-title">{str(action_title)[:90]}</span>
                            </div>
                            <div class="task-card-desc">{(discussion_desc or '')[:100]}</div>
                            <div class="task-card-footer">
                                <span class="assignee-avatar">{initials}</span>
                                <span class="due-chip">{due_display}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    a1, a2 = st.columns([3, 1.2], gap="small")
                    with a1:
                        if not already_imported:
                            st.checkbox("Select for import", key=f"import_{selected_meeting_id}_{idx}")
                        else:
                            st.markdown('<span class="import-badge">✓ Already Imported</span>', unsafe_allow_html=True)
                    with a2:
                        if not already_imported:
                            if st.button("Add Task", key=f"add_{selected_meeting_id}_{idx}", use_container_width=True):
                                ok = add_task(
                                    item.get("Action Plan") or item.get("Discussion Points", "Untitled Task"),
                                    item.get("Discussion Points", ""),
                                    item.get("Person-in-charge", ""),
                                    parse_calendar_date(item.get("Indicative Delivery Date", "")),
                                    meeting_id=selected_meeting_id,
                                    discussion_point_id=dp_id
                                )
                                if ok:
                                    st.session_state["import_flash"] = "Task added to board."
                                    st.rerun()

                selected_rows = [
                    idx for idx in importable_indices
                    if st.session_state.get(f"import_{selected_meeting_id}_{idx}", False)
                ]
                if selected_rows:
                    st.write("")
                    if st.button(f"Import Selected ({len(selected_rows)})", type="primary", use_container_width=True):
                        imported_count = 0
                        for idx in selected_rows:
                            item = table_items[idx]
                            dp_id = item.get('discussion_point_id') or item.get('id') or generate_stable_id(
                                selected_meeting_id,
                                item.get('Discussion Points', ''),
                                item.get('Action Plan', '')
                            )
                            ok = add_task(
                                item.get("Action Plan") or item.get("Discussion Points", "Untitled Task"),
                                item.get("Discussion Points", ""),
                                item.get("Person-in-charge", ""),
                                parse_calendar_date(item.get("Indicative Delivery Date", "")),
                                meeting_id=selected_meeting_id,
                                discussion_point_id=dp_id
                            )
                            if ok:
                                imported_count += 1
                        st.session_state["import_flash"] = f"Imported {imported_count} task(s) from meeting."
                        st.rerun()
            else:
                st.info("This meeting has no action items.")


# ---------------- NEW TASK TAB ----------------
with tab_new:
    if "task_flash" in st.session_state:
        st.success(st.session_state.pop("task_flash"))

    st.markdown("#### Create New Task")
    with st.form("new_task_form", clear_on_submit=True):
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
                key="assign_type_new"
            )

            if assign_type_new == "Group":
                assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="group_select_new")
                st.caption("Assign to a whole team or group.")
            else:
                assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="individual_new")
                assignee = ", ".join(assignee_list)
                st.caption("Select one or more specific people.")

            due_date = st.date_input("Due Date", value=None)
            st.caption(f"Format: MM-DD-YYYY · {format_mm_dd_yyyy(due_date) if due_date else 'No date selected'}")

            meeting_id = st.text_input(
                "Linked Meeting ID (optional)",
                placeholder="e.g., MOM-20260831-1230",
                help="Paste a meeting ID to link this task."
            )

        submitted = st.form_submit_button("Create Task", type="primary", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                success = add_task(title, description, assignee, due_date, meeting_id if meeting_id else None)
                if success:
                    st.session_state["task_flash"] = "Task created successfully."
                    st.rerun()


# ---------------- CALENDAR TAB ----------------
with tab_calendar:
    if "tasks_cal_focus_date" not in st.session_state:
        st.session_state["tasks_cal_focus_date"] = date.today()

    cal_assignee = ["All Assignees"]
    cal_status = ["todo", "in_progress", "done"]
    cal_meeting = ""
    show_unscheduled = False

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

    # ===== BUILD & FILTER EVENTS =====
    all_events = build_calendar_events()

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

    # ===== RENDER: DAY VIEW =====
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

    # ===== RENDER: WEEK VIEW =====
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

            header_class = "week-day-header today" if is_today else "week-day-header"
            st.markdown(
                f"<div style='font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.02em;"
                f"padding-bottom:0.25rem;margin-bottom:0.35rem;{('color:#8C6D23;border-bottom:2px solid var(--gold);' if is_today else 'color:var(--ink);border-bottom:1px solid rgba(0,0,0,0.06);')}'"
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

    # ===== RENDER: MONTH VIEW =====
    else:
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdatescalendar(focus.year, focus.month)
        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

        header_cols = st.columns(7, gap="small")
        for i, name in enumerate(day_names):
            with header_cols[i]:
                is_weekend = (i == 0 or i == 6)
                header_style = (
                    "background:#C9B59C; color:#412D15; border-radius:6px 6px 0 0;"
                    if is_weekend
                    else "background:#FFFFFF; color:#412D15; border:1px solid rgba(65,45,21,0.15); border-bottom:none;"
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
                    is_today = (day_val == date.today())

                    marker_classes = "cell-marker"
                    if in_month and is_weekend:
                        marker_classes += " cell-weekend"
                    if is_today and in_month:
                        marker_classes += " cell-today"
                    if not in_month:
                        marker_classes += " cell-dim"

                    with st.container(border=True):
                        st.markdown(f'<span class="{marker_classes}" style="display:none;"></span>', unsafe_allow_html=True)

                        if in_month:
                            dot = '<span class="today-dot"></span>' if is_today else ''
                            st.markdown(
                                f"<div style='display:flex;align-items:center;gap:4px;font-family:Playfair Display,serif;"
                                f"font-size:0.9rem;font-weight:600;color:#412D15;padding:1px 2px 3px 2px;'>{day_val.day}{dot}</div>",
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
                                    f"<div style='font-size:0.58rem;color:#8A7A5F;padding-left:2px;'>+{len(day_events) - 3} more</div>",
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
                                f"color:rgba(0,0,0,0.3);padding:1px 2px 3px 2px;'>{day_val.day}</div>",
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


# Trigger Task Details modal if session state is set
if 'selected_task' in st.session_state:
    open_task_details()
