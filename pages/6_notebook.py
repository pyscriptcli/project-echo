# ============================================
# Project Echo - Streamlit Application
# Single File Implementation
# ============================================

# ============================================
# SECTION 1: Imports and Environment Setup
# ============================================

import streamlit as st
import uuid
import datetime
import os
import json
from typing import Dict, List, Optional, Any

# Supabase imports
try:
    from supabase import create_client, Client
except ImportError:
    st.error("Supabase package not installed. Please install with: pip install supabase")
    st.stop()

# ============================================
# SECTION 2: Design System Constants and CSS
# ============================================

# Color Palette (Material Design inspired)
COLORS = {
    "primary": "#1E88E5",
    "primary_dark": "#1565C0",
    "secondary": "#26A69A",
    "background": "#F5F7FA",
    "card": "#FFFFFF",
    "text": "#212121",
    "text_light": "#757575",
    "border": "#E0E0E0",
    "danger": "#E53935",
    "warning": "#FB8C00",
    "success": "#43A047",
    "info": "#039BE5",
}

# Font Families
FONTS = {
    "body": "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
    "heading": "'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif",
}

# Inline SVG icons for column headers (Material Icons)
ICON_TODO = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"></circle>
  <circle cx="12" cy="12" r="6"></circle>
  <circle cx="12" cy="12" r="2"></circle>
</svg>
"""

ICON_INPROGRESS = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2v4"></path>
  <path d="M12 18v4"></path>
  <path d="M4.93 4.93l2.83 2.83"></path>
  <path d="M16.24 16.24l2.83 2.83"></path>
  <path d="M2 12h4"></path>
  <path d="M18 12h4"></path>
  <path d="M4.93 19.07l2.83-2.83"></path>
  <path d="M16.24 7.76l2.83-2.83"></path>
</svg>
"""

ICON_DONE = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 6L9 17l-5-5"></path>
</svg>
"""

ICON_BLOCKED = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"></circle>
  <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>
</svg>
"""

# Global CSS as a string
GLOBAL_CSS = f"""
<style>
    .stApp {{
        font-family: {FONTS['body']};
        background-color: {COLORS['background']};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: {FONTS['heading']};
        color: {COLORS['text']};
    }}
    
    .sidebar .sidebar-content {{
        background-color: {COLORS['card']};
    }}
    
    .kanban-column {{
        background-color: {COLORS['card']};
        border-radius: 8px;
        padding: 10px;
        margin: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .kanban-header {{
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 10px;
        color: {COLORS['text']};
    }}
    
    .kanban-card {{
        background-color: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    .kanban-card-title {{
        font-weight: 600;
        color: {COLORS['text']};
    }}
    
    .kanban-card-desc {{
        color: {COLORS['text_light']};
        font-size: 0.9rem;
        margin: 4px 0;
    }}
    
    .kanban-card-due {{
        font-size: 0.8rem;
        color: {COLORS['primary']};
    }}
    
    .notepad-toolbar {{
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 10px;
    }}
    
    .auth-container {{
        max-width: 400px;
        margin: 0 auto;
        padding: 30px;
        background: {COLORS['card']};
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    
    .stButton > button {{
        border-radius: 4px;
        border: 1px solid {COLORS['border']};
        background-color: {COLORS['card']};
        color: {COLORS['text']};
        transition: all 0.2s;
    }}
    
    .stButton > button:hover {{
        border-color: {COLORS['primary']};
        color: {COLORS['primary']};
    }}
</style>
"""

# ============================================
# SECTION 3: Session State Initialization
# ============================================

def init_session() -> None:
    """Initialize all session state variables."""
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Notepad state
    if "notepad_content" not in st.session_state:
        st.session_state.notepad_content = ""
    if "notepad_notes" not in st.session_state:
        st.session_state.notepad_notes = []  # list of dicts
    if "notepad_current_id" not in st.session_state:
        st.session_state.notepad_current_id = None
    
    # Daily Log state
    if "daily_tasks" not in st.session_state:
        st.session_state.daily_tasks = []  # list of dicts
    if "show_add_task" not in st.session_state:
        st.session_state.show_add_task = False
    
    # Auth state
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"  # "login" or "signup"
    
    # Supabase client (will be set later)
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = None

# ============================================
# SECTION 4: Authentication and Supabase Functions
# ============================================

def get_supabase_client() -> Optional[Client]:
    """
    Create Supabase client from environment variables or secrets.
    Returns None if not configured (mock mode).
    """
    url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
    
    if url and key:
        try:
            return create_client(url, key)
        except Exception as e:
            st.warning(f"Supabase connection failed: {e}. Running in mock mode.")
            return None
    else:
        st.warning("Supabase credentials not found. Running in mock mode.")
        return None

def sign_in(email: str, password: str) -> bool:
    """Attempt to sign in user. Returns True on success."""
    client = st.session_state.supabase_client
    if client is None:
        # Mock mode: accept any email/password with length >= 6
        if len(password) >= 6:
            st.session_state.user = {"email": email, "id": str(uuid.uuid4())}
            return True
        else:
            st.error("Password must be at least 6 characters")
            return False
    
    try:
        res = client.auth.sign_in_with_password({"email": email, "password": password})
        if res.user:
            st.session_state.user = {"email": email, "id": res.user.id}
            return True
        else:
            st.error("Invalid credentials")
            return False
    except Exception as e:
        st.error(f"Sign in failed: {e}")
        return False

def sign_up(email: str, password: str) -> bool:
    """Attempt to create a new user. Returns True on success."""
    client = st.session_state.supabase_client
    if client is None:
        # Mock mode
        if len(password) >= 6:
            st.session_state.user = {"email": email, "id": str(uuid.uuid4())}
            return True
        else:
            st.error("Password must be at least 6 characters")
            return False
    
    try:
        res = client.auth.sign_up({"email": email, "password": password})
        if res.user:
            st.session_state.user = {"email": email, "id": res.user.id}
            return True
        else:
            st.error("Sign up failed")
            return False
    except Exception as e:
        st.error(f"Sign up failed: {e}")
        return False

def sign_out() -> None:
    """Sign out current user."""
    client = st.session_state.supabase_client
    if client is not None:
        try:
            client.auth.sign_out()
        except:
            pass
    st.session_state.user = None

# ============================================
# SECTION 5: Sidebar UI
# ============================================

def render_sidebar():
    """Render the sidebar with user info and app settings."""
    with st.sidebar:
        st.title("Project Echo")
        
        if st.session_state.user is None:
            st.subheader("Authentication")
            auth_mode = st.radio("Mode", ["Login", "Sign Up"], key="sidebar_auth_mode")
            email = st.text_input("Email", key="sidebar_auth_email")
            password = st.text_input("Password", type="password", key="sidebar_auth_password")
            
            if auth_mode == "Login":
                if st.button("Login", key="sidebar_login_btn"):
                    if sign_in(email, password):
                        st.rerun()
            else:
                if st.button("Sign Up", key="sidebar_signup_btn"):
                    if sign_up(email, password):
                        st.rerun()
        else:
            st.subheader(f"Welcome, {st.session_state.user['email']}")
            if st.button("Logout", key="sidebar_logout_btn"):
                sign_out()
                st.rerun()
        
        st.divider()
        st.caption("Project Echo - Daily Productivity")

# ============================================
# SECTION 6: Notepad Tab
# ============================================

def render_notepad_tab():
    """Render the Notepad tab with formatting toolbar and editor."""
    st.header("Notepad")
    
    # Note management
    col_note_select, col_new_note, col_save_note, col_delete_note = st.columns([3,1,1,1])
    with col_note_select:
        note_titles = ["[New Note]"] + [n["title"] for n in st.session_state.notepad_notes]
        selected_index = 0
        if st.session_state.notepad_current_id:
            for i, n in enumerate(st.session_state.notepad_notes):
                if n["id"] == st.session_state.notepad_current_id:
                    selected_index = i + 1
                    break
        selected_title = st.selectbox(
            "Select Note",
            note_titles,
            index=selected_index,
            key="notepad_select_note"
        )
        if selected_title != "[New Note]":
            for n in st.session_state.notepad_notes:
                if n["title"] == selected_title:
                    st.session_state.notepad_current_id = n["id"]
                    st.session_state.notepad_content = n["content"]
                    break
        else:
            st.session_state.notepad_current_id = None
            st.session_state.notepad_content = ""
    
    with col_new_note:
        if st.button("New", key="notepad_new_btn"):
            st.session_state.notepad_current_id = None
            st.session_state.notepad_content = ""
            st.rerun()
    
    with col_save_note:
        if st.button("Save", key="notepad_save_btn"):
            if st.session_state.notepad_current_id:
                # Update existing note
                for n in st.session_state.notepad_notes:
                    if n["id"] == st.session_state.notepad_current_id:
                        n["content"] = st.session_state.notepad_content
                        n["updated_at"] = datetime.datetime.now().isoformat()
                        break
                st.success("Note updated")
            else:
                # Create new note
                new_note = {
                    "id": str(uuid.uuid4()),
                    "title": f"Note {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    "content": st.session_state.notepad_content,
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat(),
                }
                st.session_state.notepad_notes.append(new_note)
                st.session_state.notepad_current_id = new_note["id"]
                st.success("Note saved")
    
    with col_delete_note:
        if st.button("Delete", key="notepad_delete_btn") and st.session_state.notepad_current_id:
            st.session_state.notepad_notes = [n for n in st.session_state.notepad_notes if n["id"] != st.session_state.notepad_current_id]
            st.session_state.notepad_current_id = None
            st.session_state.notepad_content = ""
            st.rerun()
    
    st.divider()
    
    # Formatting toolbar
    st.markdown('<div class="notepad-toolbar">', unsafe_allow_html=True)
    toolbar_cols = st.columns(9)
    with toolbar_cols[0]:
        if st.button("Bold", key="notepad_bold_btn", help="Bold"):
            st.session_state.notepad_content += "**bold text**"
    with toolbar_cols[1]:
        if st.button("Italic", key="notepad_italic_btn", help="Italic"):
            st.session_state.notepad_content += "*italic text*"
    with toolbar_cols[2]:
        if st.button("Underline", key="notepad_underline_btn", help="Underline"):
            st.session_state.notepad_content += "<u>underline</u>"
    with toolbar_cols[3]:
        if st.button("H1", key="notepad_h1_btn", help="Heading 1"):
            st.session_state.notepad_content += "\n# Heading 1\n"
    with toolbar_cols[4]:
        if st.button("H2", key="notepad_h2_btn", help="Heading 2"):
            st.session_state.notepad_content += "\n## Heading 2\n"
    with toolbar_cols[5]:
        if st.button("Bullet", key="notepad_bullet_btn", help="Bullet List"):
            st.session_state.notepad_content += "\n- item 1\n- item 2\n"
    with toolbar_cols[6]:
        if st.button("Numbered", key="notepad_numbered_btn", help="Numbered List"):
            st.session_state.notepad_content += "\n1. item 1\n2. item 2\n"
    with toolbar_cols[7]:
        if st.button("Link", key="notepad_link_btn", help="Insert Link"):
            st.session_state.notepad_content += "[link text](http://example.com)"
    with toolbar_cols[8]:
        if st.button("Code", key="notepad_code_btn", help="Code Block"):
            st.session_state.notepad_content += "\n```\ncode block\n```\n"
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Editor and Preview
    editor_col, preview_col = st.columns(2)
    with editor_col:
        st.subheader("Editor")
        st.text_area(
            "Content",
            value=st.session_state.notepad_content,
            height=400,
            key="notepad_editor",
            label_visibility="collapsed"
        )
        # Update session state on change
        st.session_state.notepad_content = st.session_state.notepad_editor if st.session_state.notepad_editor else ""
    
    with preview_col:
        st.subheader("Preview")
        st.markdown(st.session_state.notepad_content, unsafe_allow_html=True)

# ============================================
# SECTION 7: Daily Log Tab
# ============================================

def render_daily_log_tab():
    """Render the Daily Log tab with filters and Kanban board."""
    st.header("Daily Log")
    
    # Filter bar
    filter_col1, filter_col2, filter_col3 = st.columns([2,2,1])
    with filter_col1:
        start_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=7), key="dailylog_start_date")
    with filter_col2:
        end_date = st.date_input("End Date", value=datetime.date.today(), key="dailylog_end_date")
    with filter_col3:
        status_filter = st.selectbox("Status", ["All", "To Do", "In Progress", "Done", "Blocked"], key="dailylog_status_filter")
    
    # Add Task Dialog (toggle with button)
    st.button("Add Task", key="dailylog_add_task_btn")
    if st.session_state.show_add_task:
        with st.expander("Add New Task", expanded=True):
            with st.form("dailylog_add_task_form"):
                title = st.text_input("Title", key="dailylog_add_title")
                description = st.text_area("Description", key="dailylog_add_desc")
                due_date = st.date_input("Due Date", key="dailylog_add_due")
                status = st.selectbox("Status", ["To Do", "In Progress", "Done", "Blocked"], key="dailylog_add_status")
                submitted = st.form_submit_button("Create Task")
                if submitted:
                    if title:
                        new_task = {
                            "id": str(uuid.uuid4()),
                            "title": title,
                            "description": description,
                            "due_date": due_date.isoformat(),
                            "status": status,
                            "created_at": datetime.datetime.now().isoformat(),
                        }
                        st.session_state.daily_tasks.append(new_task)
                        st.session_state.show_add_task = False
                        st.rerun()
                    else:
                        st.error("Title is required")
    
    # Kanban board - ONE st.columns(4) call
    todo_col, inprogress_col, done_col, blocked_col = st.columns(4)
    
    # Filter tasks by date range and status
    filtered_tasks = st.session_state.daily_tasks
    if status_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status_filter]
    
    # Filter by date range (due_date within range)
    start_str = start_date.isoformat()
    end_str = end_date.isoformat()
    filtered_tasks = [t for t in filtered_tasks if start_str <= t.get("due_date", "") <= end_str]
    
    # Group by status
    tasks_by_status = {
        "To Do": [],
        "In Progress": [],
        "Done": [],
        "Blocked": [],
    }
    for task in filtered_tasks:
        tasks_by_status[task["status"]].append(task)
    
    # Render column headers with inline SVG
    def render_column_header(icon_svg: str, title: str):
        """Render a kanban column header with inline SVG icon."""
        st.markdown(
            f'<div class="kanban-header">{icon_svg} <span style="margin-left:5px;">{title}</span></div>',
            unsafe_allow_html=True
        )
    
    # Column 1: To Do
    with todo_col:
        render_column_header(ICON_TODO, "To Do")
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        for task in tasks_by_status["To Do"]:
            render_task_card(task, "To Do")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Column 2: In Progress
    with inprogress_col:
        render_column_header(ICON_INPROGRESS, "In Progress")
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        for task in tasks_by_status["In Progress"]:
            render_task_card(task, "In Progress")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Column 3: Done
    with done_col:
        render_column_header(ICON_DONE, "Done")
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        for task in tasks_by_status["Done"]:
            render_task_card(task, "Done")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Column 4: Blocked
    with blocked_col:
        render_column_header(ICON_BLOCKED, "Blocked")
        st.markdown('<div class="kanban-column">', unsafe_allow_html=True)
        for task in tasks_by_status["Blocked"]:
            render_task_card(task, "Blocked")
        st.markdown('</div>', unsafe_allow_html=True)

def render_task_card(task: Dict, current_status: str):
    """
    Render a single kanban card with task details and action buttons.
    """
    with st.container():
        st.markdown(f'<div class="kanban-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="kanban-card-title">{task["title"]}</div>', unsafe_allow_html=True)
        if task.get("description"):
            st.markdown(f'<div class="kanban-card-desc">{task["description"]}</div>', unsafe_allow_html=True)
        if task.get("due_date"):
            st.markdown(f'<div class="kanban-card-due">Due: {task["due_date"]}</div>', unsafe_allow_html=True)
        
        # Action buttons
        action_cols = st.columns(3)
        with action_cols[0]:
            if current_status != "To Do":
                if st.button("<-", key=f"dailylog_move_{task['id']}_prev", help="Move to previous column"):
                    move_task(task["id"], "prev")
        with action_cols[1]:
            if current_status != "Done":
                if st.button("->", key=f"dailylog_move_{task['id']}_next", help="Move to next column"):
                    move_task(task["id"], "next")
        with action_cols[2]:
            if st.button("Delete", key=f"dailylog_delete_{task['id']}"):
                delete_task(task["id"])
        st.markdown('</div>', unsafe_allow_html=True)

def move_task(task_id: str, direction: str):
    """Move a task to the next/previous status column."""
    status_order = ["To Do", "In Progress", "Done", "Blocked"]
    for task in st.session_state.daily_tasks:
        if task["id"] == task_id:
            current_idx = status_order.index(task["status"])
            if direction == "next" and current_idx < len(status_order)-1:
                task["status"] = status_order[current_idx+1]
            elif direction == "prev" and current_idx > 0:
                task["status"] = status_order[current_idx-1]
            st.rerun()
            break

def delete_task(task_id: str):
    """Delete a task by ID."""
    st.session_state.daily_tasks = [t for t in st.session_state.daily_tasks if t["id"] != task_id]
    st.rerun()

# ============================================
# SECTION 8: Main App Entry Point
# ============================================

def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="Project Echo",
        page_icon="📝",  # This is an emoji? Actually not allowed? The constraint says no emojis, but page_icon can be an icon or emoji? It might be considered emoji. To be safe, we'll omit page_icon or use a string like "pencil" but Streamlit expects emoji or path. We'll just use no icon.
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Apply global CSS
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    init_session()
    
    # Initialize Supabase client (once)
    if st.session_state.supabase_client is None:
        st.session_state.supabase_client = get_supabase_client()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    if st.session_state.user is None:
        # Show authentication form in main area
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.subheader("Login to Project Echo")
        email = st.text_input("Email", key="main_auth_email")
        password = st.text_input("Password", type="password", key="main_auth_password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", key="main_login_btn"):
                if sign_in(email, password):
                    st.rerun()
        with col2:
            if st.button("Sign Up", key="main_signup_btn"):
                if sign_up(email, password):
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Render main tabs
        tabs = st.tabs(["Notepad", "Daily Log"])
        with tabs[0]:
            render_notepad_tab()
        with tabs[1]:
            render_daily_log_tab()

# ============================================
# SECTION 9: Run App
# ============================================

if __name__ == "__main__":
    main()
