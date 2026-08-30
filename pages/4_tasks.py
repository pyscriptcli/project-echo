# pages/4_tasks.py (or pages/tasks.py)
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import date, timedelta, datetime
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

# 4. Custom CSS (Native UI, Compact, Monochrome)
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

.block-container { padding-top: 1.5rem !important; padding-right: 2.5rem !important; padding-left: 2.5rem !important; }

h3 {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important; 
    font-weight: 400 !important; 
    color: #1A2B4C !important; 
    letter-spacing: 0.02em; 
    margin-bottom: 0.25rem; 
    font-size: 1.35rem !important;
}

/* Best Practice: Colored left borders based on status */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 8px !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important; 
    border-left: 5px solid #E67E22 !important; /* Default Orange */
    padding: 0.25rem 0.5rem !important; 
    margin-bottom: 0.5rem !important;
}

/* Status specific border colors */
.task-todo { border-left: 5px solid #E67E22 !important; }
.task-in_progress { border-left: 5px solid #2980B9 !important; }
.task-done { border-left: 5px solid #27AE60 !important; }

/* Overdue text color */
.overdue { color: #E74C3C !important; font-weight: 600 !important; }

/* Form inputs */
.stTextInput input, .stTextArea textarea, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #FAFAFA !important; 
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important;
}

/* Compact Monochrome Buttons */
.stButton > button {
    background-color: transparent !important; 
    color: #161616 !important; 
    border: 1px solid transparent !important; 
    border-radius: 8px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 0.65rem !important; 
    height: 28px !important; 
    padding: 0 0.4rem !important;
    transition: all 0.2s ease !important; 
    width: 100% !important;
}
.stButton > button:hover { 
    background-color: rgba(0, 0, 0, 0.05) !important; 
    color: #111A2B !important; 
    border: 1px solid #D4AF37 !important; 
}

/* Minimal, Native Modal Styling */
[data-testid="stDialog"] div[data-testid="stVerticalBlock"] {
    gap: 0.25rem !important;
    padding: 0.5rem !important;
}
[data-testid="stDialog"] h3 {
    margin-bottom: 0.2rem !important;
    font-size: 1.1rem !important;
}
</style>
""", unsafe_allow_html=True)

# 5. Helper functions for Supabase tasks
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

def add_task(title, description, assignee, due_date, meeting_id=None):
    if not supabase:
        st.error("Supabase client not initialized.")
        return False
    payload = {
        "title": title.strip(),
        "description": description.strip(),
        "assignee": assignee.strip() if assignee else None,
        "due_date": due_date.isoformat() if due_date else None,
        "meeting_id": meeting_id,
        "status": "todo"
    }
    try:
        supabase.table("tasks").insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Failed to add task: {e}")
        return False

# Update function to track WHO and WHEN
def update_task_status(task_id, new_status, username):
    if not supabase:
        return
    try:
        supabase.table("tasks").update({
            "status": new_status,
            "status_updated_by": username,
            "status_updated_at": "now()",
            "updated_at": "now()"
        }).eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Failed to update status: {e}")

# Callback for immediate status change
def handle_status_change(task_id):
    new_status = st.session_state.get(f"status_{task_id}")
    # Get current logged-in username from session state
    username = st.session_state.get("user", {}).get("username", "System")
    update_task_status(task_id, new_status, username)

def delete_task(task_id):
    if not supabase:
        return
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Failed to delete task: {e}")

# 6. Fetch data
tasks = fetch_tasks()
meetings = fetch_meeting_archives(limit=100)

# 6.5 The View Modal (Now includes Who and When)
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
        
        # Who and When
        st.markdown(f"**Assignee:** {task.get('assignee', 'Unassigned')}")
        st.markdown(f"**Due Date:** {task.get('due_date', 'No date set')}")
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

# 7. Page layout
st.markdown("<h3>Task Board</h3>", unsafe_allow_html=True)
st.caption("Manage tasks derived from meeting action items or create new ones.")

# 8. Tabs
tab_board, tab_import, tab_new = st.tabs(["Board", "Import from Meeting", "New Task"])

# ---------------- Board Tab (Instant Status Change) ----------------
with tab_board:
    if not tasks:
        st.info("No tasks yet. Create one or import from meetings.")
    else:
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        status_options = list(status_map.keys())

        for task in tasks:
            task_id = task['id']
            
            card_class = f"task-{task.get('status', 'todo')}"
            
            with st.container(border=True):
                st.markdown(f'<div class="{card_class}" style="display:none"></div>', unsafe_allow_html=True)

                # Columns: Title, Assignee, Due, Status (Instant), Actions
                c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1.5, 2.5, 2])
                
                with c1:
                    st.markdown(f"**{task['title']}**")
                    desc = task['description'] or ""
                    st.caption(desc[:50] + "..." if len(desc) > 50 else desc)
                
                with c2:
                    st.markdown("**Assignee**")
                    st.caption(task['assignee'] or "N/A")
                
                with c3:
                    st.markdown("**Due Date**")
                    due_date_str = task.get('due_date', None)
                    if due_date_str:
                        try:
                            due_date_obj = datetime.strptime(due_date_str[:10], "%Y-%m-%d").date()
                            if due_date_obj < date.today() and task.get('status') != 'done':
                                st.markdown(f'<span class="overdue">{due_date_str[:10]}</span>', unsafe_allow_html=True)
                            else:
                                st.caption(due_date_str[:10])
                        except:
                            st.caption(due_date_str[:10])
                    else:
                        st.caption("N/A")
                
                with c4:
                    current_index = status_options.index(task['status']) if task['status'] in status_options else 0
                    # Dropdown with on_change for immediate update (No Update button)
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
                
                with c5:
                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("View", icon=":material/visibility:", key=f"view_{task_id}", use_container_width=True):
                            st.session_state['selected_task'] = task
                            st.rerun()
                    with b2:
                        if st.button("Delete", icon=":material/delete:", key=f"del_{task_id}", use_container_width=True):
                            delete_task(task_id)
                            st.rerun()

# Trigger Modal if session state is set
if 'selected_task' in st.session_state:
    open_task_details()

# ---------------- Import from Meeting Tab ----------------
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
                                    try:
                                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                                    except:
                                        pass
                                success = add_task(title, description, assignee, due_date, meeting_id=selected_meeting_id)
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
        assignee = st.text_input("Assignee")
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
