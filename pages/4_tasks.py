# pages/4_tasks.py (or pages/tasks.py)
import sys
import os
import hashlib  # Imported for fallback ID generation
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

# 4. Custom CSS (Ultra-Compact, Native, Monochrome)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

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

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }

.stApp {
    background-color: #F3EFE6; 
    background-image: linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

.block-container { padding-top: 1rem !important; padding-right: 1.5rem !important; padding-left: 1.5rem !important; }

h3 {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important; 
    font-weight: 400 !important; 
    color: #1A2B4C !important; 
    letter-spacing: 0.02em; 
    margin-bottom: 0.25rem; 
    font-size: 1.2rem !important;
}

/* ------------------------- ULTRA-COMPACT CARD CSS ------------------------- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 6px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important; 
    border-left: 4px solid #E67E22 !important; 
    padding: 0.2rem 0.4rem !important; 
    margin-bottom: 0.2rem !important; /* Tightly stacked */
}

div[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
    gap: 0.1rem !important;
}

/* Compact Text */
div[data-testid="stVerticalBlockBorderWrapper"] p {
    font-size: 0.75rem !important;
    margin-bottom: 0.1rem !important;
    line-height: 1.2 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stCaptionContainer"] {
    font-size: 0.65rem !important;
    line-height: 1.1 !important;
}

/* Compact Dropdown */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stSelectbox"] {
    margin-bottom: 0 !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stSelectbox"] > div > div {
    min-height: 24px !important;
    font-size: 0.65rem !important;
}

/* Compact Buttons */
div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stButton"] > button {
    height: 24px !important;
    font-size: 0.6rem !important;
    padding: 0 0.25rem !important;
    border: none !important;
    width: 100% !important;
}

/* Status specific border colors */
.task-todo { border-left: 4px solid #E67E22 !important; }
.task-in_progress { border-left: 4px solid #2980B9 !important; }
.task-done { border-left: 4px solid #27AE60 !important; }

/* Overdue text color */
.overdue { color: #E74C3C !important; font-weight: 600 !important; }

/* Native Modal Styling */
[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
    padding: 0.5rem !important;
}
[data-testid="stDialog"] h3 {
    margin-bottom: 0.2rem !important;
    font-size: 1.1rem !important;
}

/* ===================== CALENDAR VIEW ===================== */
/* Compact filter + nav controls */
.cal-filter-row {
    margin-bottom: 0.35rem !important;
}
.cal-filter-row [data-testid="stSelectbox"] > div,
.cal-filter-row [data-testid="stMultiselect"] > div,
.cal-filter-row [data-testid="stTextInput"] > div {
    margin-bottom: 0 !important;
}
.cal-filter-row [data-testid="stBaseButton-secondary"] {
    height: 28px !important;
    min-height: 28px !important;
    font-size: 0.72rem !important;
    padding: 0 0.5rem !important;
    border-radius: 6px !important;
}
.cal-filter-row [data-testid="stSegmentedControl"] button {
    height: 28px !important;
    min-height: 28px !important;
    font-size: 0.72rem !important;
    padding: 0 0.6rem !important;
}
.cal-filter-row [data-testid="stCheckbox"] label,
.cal-filter-row [data-testid="stToggle"] label {
    font-size: 0.72rem !important;
    min-height: 24px !important;
}

/* Calendar grid */
.cal-month-grid {
    margin-top: 0.5rem;
}
.cal-month-cell {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 6px;
    padding: 4px;
    min-height: 82px;
    margin-bottom: 4px;
    transition: box-shadow 0.2s;
}
.cal-month-cell:hover { box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05); }
.cal-month-cell.dim { background: rgba(0, 0, 0, 0.02); border: none; }
.cal-month-cell.weekend { background: #111A2B; border-color: #111A2B; }
.cal-month-cell.today { border: 2px solid #D4AF37; }

.cal-month-day-num {
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: #1A2B4C;
    margin-bottom: 2px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.cal-month-cell.weekend .cal-month-day-num { color: #FFFFFF; }

.cal-month-add-btn {
    background: transparent;
    border: 1px dashed rgba(0, 0, 0, 0.15);
    border-radius: 4px;
    font-size: 0.65rem;
    color: #6C727A;
    padding: 1px 4px;
    cursor: pointer;
    width: 100%;
    transition: all 0.2s;
}
.cal-month-add-btn:hover { border-color: #D4AF37; color: #1A2B4C; }

.cal-month-task {
    background: #F8F7F4;
    border-radius: 3px;
    padding: 2px 4px;
    font-size: 0.65rem;
    color: #2D2D2D;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
    width: 100%;
    text-align: left;
    border: none;
    cursor: pointer;
}
.cal-month-task:hover { background: #E8E6E0; }
.cal-month-task.meeting-action { background: rgba(99, 102, 241, 0.08); }
.cal-month-cell.weekend .cal-month-task { background: rgba(255, 255, 255, 0.12); color: #FFF; }

.cal-more { font-size: 0.6rem; color: #6C727A; padding-left: 2px; }

/* Compact day/week header */
.cal-slot-header {
    text-align: center;
    padding: 0.5rem 0;
    margin-bottom: 0.6rem;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

/* Unscheduled task list */
.cal-unscheduled {
    margin-top: 0.4rem;
    padding: 0.5rem;
    background: rgba(255,255,255,0.5);
    border-radius: 6px;
    border: 1px solid rgba(0,0,0,0.05);
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

# Function to generate a stable hash if no ID is provided in the archive
def generate_stable_id(meeting_id, discussion_text, action_text):
    source = f"{meeting_id}-{discussion_text}-{action_text}"
    return hashlib.md5(source.encode()).hexdigest()

# Add Discussion Point ID to add_task
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
        "discussion_point_id": discussion_point_id  # Added here
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

# Build a set of existing discussion point IDs to check for duplicates
existing_discussion_ids = {t.get('discussion_point_id') for t in tasks if t.get('discussion_point_id')}

# ===================== CALENDAR DATA HELPERS =====================
def parse_calendar_date(raw_val):
    """Parse a date string from either a task or meeting action item."""
    if not raw_val:
        return None
    raw_s = str(raw_val).strip()[:10]
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw_s, fmt).date()
        except ValueError:
            pass
    return None

def build_calendar_events():
    """Merge tasks + meeting action items into a unified event list."""
    events = []
    today = date.today()

    # Tasks from `tasks` table
    for t in tasks:
        due_date = parse_calendar_date(t.get("due_date"))
        if not due_date:
            continue
        status = t.get("status", "todo")
        if status == "done":
            color = "#27AE60"
        elif status == "in_progress":
            color = "#2980B9"
        else:
            color = "#E67E22"
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
            "color": color,
            "overdue": due_date < today and status != "done",
        })

    # Meeting action items from meeting_archives -> table_items
    for m in meetings:
        m_id = m.get("meeting_id")
        client_name = m.get("client_name", "Meeting")
        table_items = m.get("table_items") or []
        for idx, item in enumerate(table_items):
            action = item.get("Action Plan") or item.get("Discussion Points", "")
            if not action:
                continue
            delivery_raw = item.get("Indicative Delivery Date", "")
            due_date = parse_calendar_date(delivery_raw)
            if not due_date:
                continue
            events.append({
                "id": f"meeting_{m_id}_{idx}",
                "title": f"[Action] {str(action)[:60]}",
                "date": due_date,
                "source": "meeting_action",
                "status": "n/a",
                "assignee": item.get("Person-in-charge", ""),
                "meeting_id": m_id,
                "meeting_label": client_name,
                "description": item.get("Discussion Points", ""),
                "color": "#6366F1",
                "overdue": due_date < today,
            })

    return events

def apply_calendar_filters(events, assignee_filter, status_filters, meeting_filter, start_date, end_date):
    """Filter events by assignee, status, meeting search, and a date range."""
    result = []
    for e in events:
        if not (start_date <= e["date"] <= end_date):
            continue

        # Assignee filter
        if assignee_filter and assignee_filter != "All Assignees":
            if assignee_filter == "Unassigned":
                if e.get("assignee"):
                    continue
            elif assignee_filter in GROUP_OPTIONS:
                if e.get("assignee") != assignee_filter:
                    continue
            elif assignee_filter in SPECIFIC_PEOPLE:
                if assignee_filter not in (e.get("assignee") or ""):
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
    """Return a native monochrome material icon for the event type."""
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

# 6.5 The View & Edit Modal
@st.dialog("Task Details", width="medium")
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

    tab1, tab2 = st.tabs(["Task Details", "Meeting Origin"])
    
    with tab1:
        st.markdown(f"**{task['title']}**")
        st.caption(f"ID: {task['id']}")
        st.markdown("---")
        
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        status_options = list(status_map.keys())
        current_status = task.get('status', 'todo')
        current_index = status_options.index(current_status) if current_status in status_options else 0
        
        existing_due_date = task.get('due_date')
        if existing_due_date:
            try:
                existing_due_date = datetime.strptime(existing_due_date[:10], "%Y-%m-%d").date()
            except:
                existing_due_date = None

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Status**")
            new_status = st.selectbox("Status", status_options, index=current_index, format_func=lambda x: status_map[x], label_visibility="collapsed")
        
        with c2:
            st.markdown("**Assigned To**")
            assignee_type, group_val, individuals = get_assignee_ui_state(task.get('assignee', ""))
            
            assign_type = st.radio(
                "Assignment Type", 
                ["Group", "Specific Individuals"], 
                index=0 if assignee_type == "Group" else 1, 
                horizontal=True, 
                label_visibility="collapsed",
                key="assign_type_modal"
            )
            
            if assign_type == "Group":
                group_idx = GROUP_OPTIONS.index(group_val) if group_val in GROUP_OPTIONS else 0
                new_assignee = st.selectbox("Select Group", GROUP_OPTIONS, index=group_idx, key="group_select_modal")
            else:
                new_assignee_list = st.multiselect(
                    "Select Individuals", 
                    SPECIFIC_PEOPLE, 
                    default=individuals, 
                    key="individual_modal"
                )
                new_assignee = ", ".join(new_assignee_list)
        
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**Due Date**")
            new_due_date = st.date_input("Due Date", value=existing_due_date, label_visibility="collapsed")

        if st.button("Save Changes", use_container_width=True):
            update_task(task['id'], new_status, new_assignee, new_due_date)
            st.session_state.pop('selected_task', None)
            st.success("Task updated successfully!")
            st.rerun()

        st.markdown("---")
        st.markdown(f"**Status Updated By:** {task.get('status_updated_by', 'N/A')}")
        st.markdown(f"**Status Updated At:** {task.get('status_updated_at', 'Never')}")
        
        st.markdown("**Description:**")
        st.write(task.get('description', 'No description provided.'))

    with tab2:
        if meeting_details:
            st.markdown(f"**{meeting_details.get('client_name', 'Meeting Record')}**")
            st.caption(f"Date: {meeting_details.get('meeting_date')}")
            st.caption(f"Prepared By: {meeting_details.get('prepared_by')}")
            st.markdown("---")
            st.markdown("**Summary:**")
            st.write(meeting_details.get('summary_md', 'No summary available.'))
        else:
            st.info("This task is not linked to a specific meeting.")
    
    if st.button("Close", use_container_width=True, key="close_modal_btn"):
        st.session_state.pop('selected_task', None)
        st.rerun()

# Create Task Dialog (used from Calendar empty-day clicks)
@st.dialog("Create Task", width="medium")
def new_task_dialog():
    prefill_date = st.session_state.get("cal_new_task_date")
    
    with st.form("cal_new_task_form", clear_on_submit=True):
        title = st.text_input("Task Title *")
        description = st.text_area("Description")
        
        assign_type_new = st.radio("Assignment Type", ["Group", "Specific Individuals"], horizontal=True, key="cal_dlg_assign_type")
        
        if assign_type_new == "Group":
            assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="cal_dlg_group")
        else:
            assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="cal_dlg_individuals")
            assignee = ", ".join(assignee_list)
            
        due_date = st.date_input("Due Date", value=prefill_date or date.today(), key="cal_dlg_due_date")
        meeting_id = st.text_input("Linked Meeting ID (optional)", key="cal_dlg_meeting", help="Paste a meeting ID to link this task.")
        
        submitted = st.form_submit_button("Create Task")
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

# ---------------- Board Tab (ULTRA-COMPACT KANBAN) ----------------
with tab_board:
    if not tasks:
        st.info("No tasks yet. Create one or import from meetings.")
    else:
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        status_options = list(status_map.keys())

        # Sort tasks newest to oldest
        def sort_by_newest(task_list):
            return sorted(task_list, key=lambda x: x.get('created_at', ''), reverse=True)

        todo_tasks = sort_by_newest([t for t in tasks if t.get('status') == 'todo'])
        in_progress_tasks = sort_by_newest([t for t in tasks if t.get('status') == 'in_progress'])
        done_tasks = sort_by_newest([t for t in tasks if t.get('status') == 'done'])

        col_todo, col_progress, col_done = st.columns(3)

        # Helper function to render an ultra-compact stacked task card
        def render_card(task):
            task_id = task['id']
            card_class = f"task-{task.get('status', 'todo')}"

            with st.container(border=True):
                st.markdown(f'<div class="{card_class}" style="display:none"></div>', unsafe_allow_html=True)

                # Title & Description (Tightly spaced)
                st.markdown(f"**{task['title']}**")
                desc = task['description'] or ""
                st.caption(desc[:65] + "..." if len(desc) > 65 else desc)

                # Assignee & Due Date (Combined into a single line for compactness)
                assignee = task['assignee'] or "N/A"
                
                due_date_raw = task.get('due_date')
                due_date_str = due_date_raw if isinstance(due_date_raw, str) and due_date_raw else "N/A"
                
                if due_date_str != "N/A":
                    try:
                        due_date_obj = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                        if due_date_obj < date.today() and task.get('status') != 'done':
                            st.markdown(
                                f"<span style='font-size:0.65rem;'>Assigned: {assignee} | Due: <span class='overdue'>{due_date_str[:10]}</span></span>", 
                                unsafe_allow_html=True
                            )
                        else:
                            st.caption(f"Assigned: {assignee} | Due: {due_date_str[:10]}")
                    except:
                        st.caption(f"Assigned: {assignee} | Due: {due_date_str[:10]}")
                else:
                    st.caption(f"Assigned: {assignee} | Due: N/A")

                # Compact Row: Status, View, Delete
                c_status, c_view, c_del = st.columns([2.5, 1, 1])
                
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
                    if st.button("View", icon=":material/visibility:", key=f"view_{task_id}", use_container_width=True):
                        st.session_state['selected_task'] = task
                        st.rerun()
                with c_del:
                    if st.button("Delete", icon=":material/delete:", key=f"del_{task_id}", use_container_width=True):
                        delete_task(task_id)
                        st.rerun()

        # Column 1: To Do
        with col_todo:
            with st.container(border=True):
                st.markdown(f"#### To Do ({len(todo_tasks)})")
                if not todo_tasks:
                    st.caption("No tasks pending.")
                for task in todo_tasks:
                    render_card(task)

        # Column 2: In Progress
        with col_progress:
            with st.container(border=True):
                st.markdown(f"#### In Progress ({len(in_progress_tasks)})")
                if not in_progress_tasks:
                    st.caption("No tasks in progress.")
                for task in in_progress_tasks:
                    render_card(task)

        # Column 3: Done
        with col_done:
            with st.container(border=True):
                st.markdown(f"#### Done ({len(done_tasks)})")
                if not done_tasks:
                    st.caption("No completed tasks.")
                for task in done_tasks:
                    render_card(task)

# ---------------- Import from Meeting Tab (Anti-Duplicate Logic) ----------------
with tab_import:
    st.markdown("#### Import Action Items from Meetings")
    if not meetings:
        st.info("No meetings found to import from.")
    else:
        meeting_options = {m.get("meeting_id"): m.get("client_name", "Unnamed") for m in meetings}
        selected_meeting_id = st.selectbox("Select Meeting", options=list(meeting_options.keys()), format_func=lambda x: f"{meeting_options[x]} ({x})")
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
                            st.write(f"**Due:** {item.get('Indicative Delivery Date', '')}")
                        with c4:
                            st.write(f"**PIC:** {item.get('Person-in-charge', '')}")
                        
                        # Extract or Generate Discussion Point ID
                        dp_id = item.get('discussion_point_id') or item.get('id') or None
                        if not dp_id:
                            dp_id = generate_stable_id(
                                selected_meeting_id, 
                                item.get('Discussion Points', ''), 
                                item.get('Action Plan', '')
                            )

                        # Check for duplicates
                        if dp_id in existing_discussion_ids:
                            with c5:
                                st.success("✓ Already Imported")
                        else:
                            with c5:
                                import_this = st.checkbox("Import", key=f"import_{selected_meeting_id}_{idx}")
                            if import_this:
                                if st.button("Add as Task", key=f"add_{selected_meeting_id}_{idx}"):
                                    title = item.get("Action Plan") or item.get("Discussion Points", "Untitled Task")
                                    description = item.get("Discussion Points", "")
                                    assignee = item.get("Person-in-charge", "")
                                    due_date_str = item.get("Indicative Delivery Date", "")
                                    due_date = None
                                    if due_date_str:
                                        due_date = parse_calendar_date(due_date_str)
                                    success = add_task(title, description, assignee, due_date, meeting_id=selected_meeting_id, discussion_point_id=dp_id)
                                    if success:
                                        st.success("Task added!")
                                        st.rerun()
            else:
                st.info("This meeting has no action items.")

# ---------------- New Task Tab ----------------
with tab_new:
    st.markdown("#### Create New Task")
    with st.form("new_task_form", clear_on_submit=True):
        title = st.text_input("Task Title *")
        description = st.text_area("Description")
        
        assign_type_new = st.radio("Assignment Type", ["Group", "Specific Individuals"], horizontal=True, key="assign_type_new")
        
        if assign_type_new == "Group":
            assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="group_select_new")
        else:
            assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="individual_new")
            assignee = ", ".join(assignee_list)
            
        due_date = st.date_input("Due Date", value=None)
        meeting_id = st.text_input("Linked Meeting ID (optional)", help="Paste a meeting ID to link this task.")
        
        submitted = st.form_submit_button("Create Task")
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                success = add_task(title, description, assignee, due_date, meeting_id if meeting_id else None)
                if success:
                    st.success("Task created!")
                    st.rerun()

# ---------------- Calendar Tab ----------------
with tab_calendar:
    # Initialize calendar session state
    if "tasks_cal_focus_date" not in st.session_state:
        st.session_state["tasks_cal_focus_date"] = date.today()
    if "tasks_cal_view" not in st.session_state:
        st.session_state["tasks_cal_view"] = "Month"

    focus = st.session_state["tasks_cal_focus_date"]

    # ========== COMPACT FILTER ROW ==========
    filter_cols = st.columns([2.3, 2.7, 2.5, 1.7, 2.0], gap="small")

    with filter_cols[0]:
        assignee_options = ["All Assignees", "Unassigned"] + GROUP_OPTIONS + SPECIFIC_PEOPLE
        cal_assignee = st.selectbox(
            "Assignee",
            assignee_options,
            key="cal_assignee_filter",
            label_visibility="collapsed"
        )

    with filter_cols[1]:
        status_labels = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        cal_status = st.multiselect(
            "Status",
            options=["todo", "in_progress", "done"],
            default=["todo", "in_progress", "done"],
            format_func=lambda x: status_labels[x],
            key="cal_status_filter",
            label_visibility="collapsed"
        )

    with filter_cols[2]:
        cal_meeting = st.text_input(
            "Meeting",
            placeholder="Linked meeting...",
            key="cal_meeting_filter",
            label_visibility="collapsed"
        )

    with filter_cols[3]:
        unscheduled_tasks = [t for t in tasks if not t.get("due_date")]
        show_unscheduled = st.toggle(
            f"Unscheduled ({len(unscheduled_tasks)})",
            value=False,
            key="cal_show_unscheduled"
        )

    with filter_cols[4]:
        cal_view = st.segmented_control(
            "View",
            options=["Day", "Week", "Month"],
            default="Month",
            key="tasks_cal_view",
            label_visibility="collapsed"
        )

    # Unscheduled task list (toggled)
    if show_unscheduled:
        with st.container(border=False):
            st.markdown('<div class="cal-unscheduled">', unsafe_allow_html=True)
            st.markdown("**Unscheduled Tasks**")
            if not unscheduled_tasks:
                st.caption("No unscheduled tasks.")
            else:
                for ut in unscheduled_tasks:
                    st.markdown(
                        f"- {ut.get('title')} — *{ut.get('assignee') or 'Unassigned'}* "
                        f"`{ut.get('due_date') or 'No due date'}`"
                    )
            st.markdown('</div>', unsafe_allow_html=True)

    # ========== DATE NAVIGATION ==========
    nav_cols = st.columns([1, 1, 1.6, 1, 4.5], gap="small")

    with nav_cols[0]:
        if st.button("◀", key="cal_prev", help="Previous", use_container_width=True):
            if cal_view == "Day":
                st.session_state["tasks_cal_focus_date"] = focus - timedelta(days=1)
            elif cal_view == "Week":
                st.session_state["tasks_cal_focus_date"] = focus - timedelta(days=7)
            else:
                if focus.month == 1:
                    st.session_state["tasks_cal_focus_date"] = focus.replace(year=focus.year - 1, month=12)
                else:
                    st.session_state["tasks_cal_focus_date"] = focus.replace(month=focus.month - 1)
            st.rerun()

    with nav_cols[1]:
        if st.button("Today", key="cal_today", help="Today", use_container_width=True):
            st.session_state["tasks_cal_focus_date"] = date.today()
            st.rerun()

    with nav_cols[2]:
        if st.button("▶", key="cal_next", help="Next", use_container_width=True):
            if cal_view == "Day":
                st.session_state["tasks_cal_focus_date"] = focus + timedelta(days=1)
            elif cal_view == "Week":
                st.session_state["tasks_cal_focus_date"] = focus + timedelta(days=7)
            else:
                if focus.month == 12:
                    st.session_state["tasks_cal_focus_date"] = focus.replace(year=focus.year + 1, month=1)
                else:
                    st.session_state["tasks_cal_focus_date"] = focus.replace(month=focus.month + 1)
            st.rerun()

    with nav_cols[3]:
        # Period label
        if cal_view == "Day":
            period_label = focus.strftime("%A, %B %d, %Y")
        elif cal_view == "Week":
            if focus.weekday() == 6:
                week_start = focus
            else:
                week_start = focus - timedelta(days=focus.weekday() + 1)
            week_end = week_start + timedelta(days=6)
            period_label = f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}"
        else:
            period_label = focus.strftime("%B %Y")
        st.markdown(
            f"<p style='font-size:0.8rem; color:#1A2B4C; font-weight:600; margin:0; padding-top:0.3rem;'>{period_label}</p>",
            unsafe_allow_html=True
        )

    # ========== COMPUTE DATE RANGE ==========
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

    # ========== BUILD & FILTER EVENTS ==========
    all_calendar_events = build_calendar_events()
    filtered_events = apply_calendar_filters(
        all_calendar_events,
        assignee_filter=cal_assignee,
        status_filters=cal_status,
        meeting_filter=cal_meeting.strip(),
        start_date=start_date,
        end_date=end_date
    )

    # Group by date string
    events_by_date = {}
    for evt in filtered_events:
        d_str = evt["date"].strftime("%Y-%m-%d")
        events_by_date.setdefault(d_str, []).append(evt)

    # ========== RENDER CALENDAR ==========
    # ----- DAY VIEW -----
    if cal_view == "Day":
        day_str = focus.strftime("%Y-%m-%d")
        day_events = events_by_date.get(day_str, [])

        if day_events:
            for evt in day_events:
                icon = get_event_icon(evt)
                if st.button(
                    evt["title"],
                    key=f"cal_d_{evt['id']}_{day_str}",
                    icon=icon,
                    use_container_width=True
                ):
                    st.session_state["cal_clicked_event"] = evt
                    st.session_state["cal_open_event"] = True
        else:
            st.caption("No events scheduled on this day.")

        if st.button("+ Add Task", key=f"cal_add_day_{day_str}", use_container_width=True):
            st.session_state["cal_new_task_date"] = focus
            st.session_state["cal_open_new_dialog"] = True

    # ----- WEEK VIEW -----
    elif cal_view == "Week":
        if focus.weekday() == 6:
            week_start = focus
        else:
            week_start = focus - timedelta(days=focus.weekday() + 1)

        day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        week_cols = st.columns(7, gap="small")

        for i in range(7):
            day = week_start + timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            is_weekend = (i == 0 or i == 6)
            is_today = (day == date.today())

            with week_cols[i]:
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

                st.markdown(
                    f"<div class='cal-slot-header' style='background:{bg_color}; color:{text_color}; border:{border};'>"
                    f"<div style='font-size:0.65rem; font-weight:700; text-transform:uppercase; opacity:0.9;'>{day_names[i]}</div>"
                    f"<div style='font-size:1.1rem; font-family:Playfair Display, serif; font-weight:600;'>{day.day}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                day_events = events_by_date.get(day_str, [])
                if day_events:
                    for evt in day_events:
                        icon = get_event_icon(evt)
                        if st.button(
                            evt["title"],
                            key=f"cal_w_{day_str}_{evt['id']}",
                            icon=icon,
                            use_container_width=True
                        ):
                            st.session_state["cal_clicked_event"] = evt
                            st.session_state["cal_open_event"] = True
                else:
                    if st.button(
                        "",
                        key=f"cal_add_{day_str}",
                        icon=":material/add:",
                        use_container_width=True,
                        help="Add task for this day"
                    ):
                        st.session_state["cal_new_task_date"] = day
                        st.session_state["cal_open_new_dialog"] = True

    # ----- MONTH VIEW -----
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
                    else "background:#FFFFFF; color:#1A2B4C;"
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
                            "<div style='height:82px; background:rgba(0,0,0,0.02); border-radius:6px;'></div>",
                            unsafe_allow_html=True
                        )
                        continue

                    day_str = day_val.strftime("%Y-%m-%d")
                    day_events = events_by_date.get(day_str, [])
                    is_today = (day_val == date.today())

                    cell_class = "cal-month-cell"
                    if is_today:
                        cell_class += " today"
                    if is_weekend:
                        cell_class += " weekend"

                    st.markdown(f'<div class="{cell_class}" style="min-height:82px;">', unsafe_allow_html=True)
                    st.markdown(f"<div class='cal-month-day-num'>{day_val.day}</div>", unsafe_allow_html=True)

                    for evt in day_events[:3]:
                        icon = get_event_icon(evt)
                        if st.button(
                            evt["title"],
                            key=f"cal_m_{day_str}_{evt['id']}",
                            icon=icon,
                            use_container_width=True
                        ):
                            st.session_state["cal_clicked_event"] = evt
                            st.session_state["cal_open_event"] = True

                    if len(day_events) > 3:
                        st.markdown(f"<div class='cal-more'>+{len(day_events) - 3} more</div>", unsafe_allow_html=True)

                    if not day_events:
                        if st.button(
                            "",
                            key=f"cal_add_{day_str}",
                            icon=":material/add:",
                            use_container_width=True,
                            help="Add task for this day"
                        ):
                            st.session_state["cal_new_task_date"] = day_val
                            st.session_state["cal_open_new_dialog"] = True

                    st.markdown('</div>', unsafe_allow_html=True)

    # ========== HANDLE CALENDAR CLICKS ==========
    # Open Event (Task detail or Meeting detail)
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

    # Open New Task dialog
    if st.session_state.pop("cal_open_new_dialog", False):
        new_task_dialog()

# Trigger Modal if session state is set
if 'selected_task' in st.session_state:
    open_task_details()
