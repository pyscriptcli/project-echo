# pages/tasks.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import date, timedelta
import pandas as pd

from utils.auth import require_auth
from utils.db import get_supabase_client, fetch_meeting_archives

# 1. Page config (must be first)
st.set_page_config(
    page_title="Project Echo - Task Board",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Authentication check
require_auth()

# 3. Custom CSS (reuse design system)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }

.stApp {
    background-color: #F3EFE6; 
    background-image: linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}
.stApp > header { display: none !important; }
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

.playfair-label {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important;
    color: #1A2B4C !important; 
    font-size: 1.05rem !important; 
    margin-bottom: 0.25rem !important; 
    display: block;
}

/* Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08), 0 3px 8px rgba(0, 0, 0, 0.04) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}

/* Form inputs */
.stTextInput input, .stTextArea textarea, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div {
    background-color: #FAFAFA !important; 
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important;
}

/* Buttons */
.stButton > button {
    background-color: #161616 !important; 
    color: #FFFFFF !important; 
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 0.82rem !important; 
    height: 38px !important; 
    padding: 0 1.5rem !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important; 
    transition: all 0.2s ease !important; 
    width: 100% !important;
}
.stButton > button:hover { 
    background-color: #D4AF37 !important; 
    color: #161616 !important; 
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 14px rgba(212, 175, 55, 0.3) !important;
}

/* Status badge colors */
.status-todo { color: #E67E22; font-weight: 600; }
.status-inprogress { color: #2980B9; font-weight: 600; }
.status-done { color: #27AE60; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# 4. Helper functions for Supabase tasks
supabase = get_supabase_client()

def fetch_tasks():
    """Fetch all tasks from Supabase, ordered by due date."""
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
    """Insert a new task."""
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

def update_task_status(task_id, new_status):
    """Update task status."""
    if not supabase:
        return
    try:
        supabase.table("tasks").update({"status": new_status, "updated_at": "now()"}).eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Failed to update status: {e}")

def delete_task(task_id):
    """Delete a task."""
    if not supabase:
        return
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        st.error(f"Failed to delete task: {e}")

# 5. Fetch data
tasks = fetch_tasks()
meetings = fetch_meeting_archives(limit=100)  # for import

# 6. Page layout
st.markdown("<h3>Task Board</h3>", unsafe_allow_html=True)
st.caption("Manage tasks derived from meeting action items or create new ones.")

# 7. Tabs: Board View | Import from Meeting | New Task
tab_board, tab_import, tab_new = st.tabs(["📋 Board", "📥 Import from Meeting", "➕ New Task"])

# ---------------- Board Tab ----------------
with tab_board:
    if not tasks:
        st.info("No tasks yet. Create one or import from meetings.")
    else:
        # Convert to DataFrame for easy display
        df = pd.DataFrame(tasks)
        # Map status to friendly names
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        df["Status"] = df["status"].map(status_map).fillna(df["status"])
        df["Due Date"] = pd.to_datetime(df["due_date"]).dt.strftime("%Y-%m-%d")
        # Keep only relevant columns
        display_cols = ["title", "description", "assignee", "Due Date", "Status", "meeting_id"]
        df_display = df[display_cols].rename(columns={
            "title": "Task",
            "description": "Description",
            "assignee": "Assignee",
            "meeting_id": "Source Meeting"
        })

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("#### Update Status")
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            task_options = {t["id"]: t["title"] for t in tasks}
            selected_task_id = st.selectbox("Select Task", options=list(task_options.keys()), format_func=lambda x: task_options[x])
        with col2:
            new_status = st.selectbox("New Status", ["todo", "in_progress", "done"], format_func=lambda x: status_map[x])
        with col3:
            if st.button("Update Status", key="btn_update_status"):
                update_task_status(selected_task_id, new_status)
                st.success("Status updated!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### Delete Task")
        if st.button("Delete Selected Task", key="btn_delete_task"):
            delete_task(selected_task_id)
            st.success("Task deleted.")
            st.rerun()

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
                            # When import button is clicked, add task
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
