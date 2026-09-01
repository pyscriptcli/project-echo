import sys
import os
import datetime
import uuid
import streamlit as st

# Add project root to sys.path to allow imports from components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.sidebar import setup_page_layout

# ------------------------------
# Page configuration
# ------------------------------
st.set_page_config(
    page_title="Project Echo - Notebook",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------
# CSS
# ------------------------------
NOTEBOOK_CSS = """
<style>
    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background-color: #F3EFE6;
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Titles and subtitles */
    .notebook-title {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 2.8rem;
        color: #1A2B4C;
        margin-bottom: 0.25rem;
    }
    .notebook-subtitle {
        font-size: 1rem;
        color: #6C727A;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #D4AF37;
        padding-bottom: 0.75rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #D4AF37;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.2rem;
        color: #1A2B4C;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #D4AF37 !important;
        border-bottom: 3px solid #D4AF37;
    }

    /* Notepad specific */
    .doc-browser {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .toolbar {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        align-items: center;
        margin-bottom: 1rem;
    }
    .editor-area textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
        color: #1A2B4C !important;
        padding: 1rem !important;
    }
    .status-footer {
        display: flex;
        justify-content: space-between;
        color: #6C727A;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        border-top: 1px solid #E0E0E0;
        padding-top: 0.5rem;
    }

    /* Daily Log specific */
    .filter-bar {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        margin-bottom: 1rem;
    }
    .date-caption {
        font-size: 0.9rem;
        color: #6C727A;
        margin-bottom: 0.75rem;
    }
    .kanban-board {
        display: flex;
        gap: 0.75rem;
    }
    .kanban-column {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E0E0E0;
        padding: 0.75rem;
        min-height: 400px;
    }
    .kanban-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 0.5rem;
    }
    .kanban-header svg {
        width: 20px;
        height: 20px;
        flex-shrink: 0;
    }
    .kanban-header .label {
        font-weight: 600;
        color: #1A2B4C;
    }
    .kanban-header .count {
        background-color: #F3EFE6;
        color: #1A2B4C;
        border-radius: 12px;
        padding: 0.1rem 0.5rem;
        font-size: 0.8rem;
        margin-left: auto;
    }
    .kanban-card {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 6px;
        padding: 0.6rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kanban-card textarea {
        background-color: transparent !important;
        border: none !important;
        resize: none !important;
        font-size: 0.9rem !important;
        color: #1A2B4C !important;
        padding: 0 !important;
        line-height: 1.4;
    }
    .card-meta {
        font-size: 0.75rem;
        color: #6C727A;
        margin-top: 0.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .empty-state {
        text-align: center;
        color: #6C727A;
        font-style: italic;
        padding: 2rem 0;
    }

    /* Popover styles */
    div[data-testid="stPopover"] > div {
        background-color: #FFFFFF;
        border: 1px solid #D4AF37;
        border-radius: 8px;
        padding: 1rem;
    }

    /* Hide Streamlit widgets default styling where needed */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        background-color: #FFFFFF;
        color: #1A2B4C;
        border: 1px solid #D4AF37;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #F3EFE6;
        border-color: #D4AF37;
    }
    .stButton > button[kind="primary"] {
        background-color: #D4AF37;
        color: #1A2B4C;
        border: none;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #c4a030;
    }

    /* Ensure columns have equal height in kanban */
    .stHorizontalBlock {
        align-items: stretch;
    }
</style>
"""

# ------------------------------
# Constants
# ------------------------------

COLUMNS = [
    {"key": "client", "label": "Client Related Tasks", "color": "#3B82F6"},
    {"key": "admin", "label": "Admin Tasks", "color": "#10B981"},
    {"key": "adhoc", "label": "Adhoc Tasks", "color": "#F59E0B"},
    {"key": "meeting", "label": "Meetings", "color": "#8B5CF6"},
]

SVG_DICT = {
    "client": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="8.5" cy="7" r="4"></circle>
            <line x1="20" y1="8" x2="20" y2="14"></line>
            <line x1="23" y1="11" x2="17" y2="11"></line>
        </svg>
    """,
    "admin": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <line x1="3" y1="9" x2="21" y2="9"></line>
            <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
    """,
    "adhoc": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 20h9"></path>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
        </svg>
    """,
    "meeting": """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
    """
}

# ------------------------------
# Helper functions
# ------------------------------

def _make_id():
    """Generate a short UUID."""
    return uuid.uuid4().hex[:8]

def _date_range(view, date_obj):
    """
    Return (start_date, end_date) inclusive for the given view and reference date.
    view: 'Day', 'Week', 'Month'
    date_obj: datetime.date
    """
    if view == "Day":
        return date_obj, date_obj
    elif view == "Week":
        start = date_obj - datetime.timedelta(days=date_obj.weekday())  # Monday
        end = start + datetime.timedelta(days=6)
        return start, end
    elif view == "Month":
        start = date_obj.replace(day=1)
        # Last day of month
        if date_obj.month == 12:
            next_month = datetime.date(date_obj.year + 1, 1, 1)
        else:
            next_month = datetime.date(date_obj.year, date_obj.month + 1, 1)
        end = next_month - datetime.timedelta(days=1)
        return start, end
    else:
        return date_obj, date_obj

def _format_date(d):
    """Format datetime/date to short string."""
    if isinstance(d, datetime.datetime):
        return d.strftime("%b %d, %Y")
    elif isinstance(d, datetime.date):
        return d.strftime("%b %d, %Y")
    return str(d)

# ------------------------------
# Session state initialization
# ------------------------------

def init_session():
    """Initialize all session state variables."""
    # Notepad documents
    if "nb_docs" not in st.session_state:
        st.session_state.nb_docs = {}
        # Seed with a welcome document
        welcome_id = _make_id()
        st.session_state.nb_docs[welcome_id] = {
            "title": "Welcome to Notebook",
            "content": "This is your digital notebook.\n\nUse the tabs above to switch between Notepad and Daily Log.\n\nStart typing here...",
            "created": datetime.datetime.now().isoformat(),
            "updated": datetime.datetime.now().isoformat(),
        }
        st.session_state.nb_current_id = welcome_id
    if "nb_current_id" not in st.session_state:
        st.session_state.nb_current_id = list(st.session_state.nb_docs.keys())[0] if st.session_state.nb_docs else None

    # Notepad clipboard and undo state
    if "np_clipboard" not in st.session_state:
        st.session_state.np_clipboard = ""
    if "np_last_saved_content" not in st.session_state:
        current_doc = st.session_state.nb_docs.get(st.session_state.nb_current_id)
        st.session_state.np_last_saved_content = current_doc["content"] if current_doc else ""
    if "np_redo_content" not in st.session_state:
        st.session_state.np_redo_content = ""

    # Daily Log
    if "dl_tasks" not in st.session_state:
        # Initialize empty dict with keys for each column
        st.session_state.dl_tasks = {col["key"]: [] for col in COLUMNS}
        # Seed with a couple of sample tasks
        sample_date = datetime.datetime.now()
        st.session_state.dl_tasks["client"].append({
            "id": _make_id(),
            "content": "Prepare quarterly report for client A",
            "created": sample_date.isoformat()
        })
        st.session_state.dl_tasks["admin"].append({
            "id": _make_id(),
            "content": "Update internal documentation",
            "created": sample_date.isoformat()
        })
        st.session_state.dl_tasks["meeting"].append({
            "id": _make_id(),
            "content": "Team sync meeting at 3 PM",
            "created": sample_date.isoformat()
        })
    if "dl_date" not in st.session_state:
        st.session_state.dl_date = datetime.date.today()
    if "dl_view" not in st.session_state:
        st.session_state.dl_view = "Day"
    if "dl_search" not in st.session_state:
        st.session_state.dl_search = ""

# ------------------------------
# Notepad CRUD helpers
# ------------------------------

def _new_doc():
    """Create a new document and set as current."""
    doc_id = _make_id()
    now = datetime.datetime.now().isoformat()
    st.session_state.nb_docs[doc_id] = {
        "title": "Untitled.txt",
        "content": "",
        "created": now,
        "updated": now,
    }
    st.session_state.nb_current_id = doc_id
    st.session_state.np_last_saved_content = ""
    st.session_state.np_redo_content = ""

def _save_current_doc():
    """Save the current doc (title and content) to session state."""
    current_id = st.session_state.nb_current_id
    if current_id and current_id in st.session_state.nb_docs:
        doc = st.session_state.nb_docs[current_id]
        doc["title"] = st.session_state.np_title
        doc["content"] = st.session_state.np_content
        doc["updated"] = datetime.datetime.now().isoformat()
        st.session_state.np_last_saved_content = st.session_state.np_content
        st.session_state.np_redo_content = ""
        st.toast("Document saved", icon=":material/check:")

def _delete_current_doc():
    """Delete the current doc and switch to another if available."""
    current_id = st.session_state.nb_current_id
    if current_id and current_id in st.session_state.nb_docs:
        del st.session_state.nb_docs[current_id]
        if st.session_state.nb_docs:
            st.session_state.nb_current_id = list(st.session_state.nb_docs.keys())[0]
            doc = st.session_state.nb_docs[st.session_state.nb_current_id]
            st.session_state.np_title = doc["title"]
            st.session_state.np_content = doc["content"]
            st.session_state.np_last_saved_content = doc["content"]
        else:
            st.session_state.nb_current_id = None
            st.session_state.np_title = ""
            st.session_state.np_content = ""
            st.session_state.np_last_saved_content = ""
        st.session_state.np_redo_content = ""
        st.toast("Document deleted", icon=":material/delete:")

# ------------------------------
# Render: Notepad
# ------------------------------

def render_notepad():
    st.markdown('<div class="notebook-title">Notepad</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Your personal document studio</div>', unsafe_allow_html=True)

    # Ensure np_title and np_content are in sync with current doc
    current_id = st.session_state.nb_current_id
    current_doc = st.session_state.nb_docs.get(current_id, None)
    if current_doc:
        # Use session_state keys for title and content to allow interactive editing
        if "np_title" not in st.session_state or st.session_state.np_title != current_doc["title"]:
            st.session_state.np_title = current_doc["title"]
        if "np_content" not in st.session_state or st.session_state.np_content != current_doc["content"]:
            st.session_state.np_content = current_doc["content"]
    else:
        st.session_state.np_title = ""
        st.session_state.np_content = ""

    # Document browser strip
    with st.container():
        col_browser, col_new = st.columns([4, 1])
        with col_browser:
            doc_options = list(st.session_state.nb_docs.keys())
            if doc_options:
                # Create a mapping from title to id for selectbox
                # We'll use titles as display, but need to handle duplicate titles? Use id in key.
                # We'll show title and update key to include id.
                # Better: use selectbox with format_func to show title.
                current_index = doc_options.index(current_id) if current_id in doc_options else 0
                selected_id = st.selectbox(
                    "Open document",
                    options=doc_options,
                    index=current_index,
                    format_func=lambda x: st.session_state.nb_docs[x]["title"],
                    key="np_doc_selector",
                    label_visibility="collapsed"
                )
                # If selection changed, update current doc
                if selected_id != current_id:
                    st.session_state.nb_current_id = selected_id
                    doc = st.session_state.nb_docs[selected_id]
                    st.session_state.np_title = doc["title"]
                    st.session_state.np_content = doc["content"]
                    st.session_state.np_last_saved_content = doc["content"]
                    st.session_state.np_redo_content = ""
                    st.rerun()
            else:
                st.write("No documents yet.")
        with col_new:
            if st.button("New Document", key="np_new_btn", use_container_width=True, icon=":material/note_add:"):
                _new_doc()
                st.rerun()

    # Toolbar row: Save, Save As, Delete, Undo, Redo, Cut, Copy, Paste
    st.markdown('<div class="toolbar">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        if st.button("Save", key="np_save_btn", use_container_width=True, icon=":material/save:"):
            _save_current_doc()
            st.rerun()
    with col2:
        # Save As using popover
        with st.popover("Save As", key="np_saveas_pop", use_container_width=True):
            new_title = st.text_input("New title", value=st.session_state.np_title + " copy", key="np_saveas_title")
            if st.button("Confirm Save As", key="np_saveas_confirm", use_container_width=True):
                new_id = _make_id()
                now = datetime.datetime.now().isoformat()
                st.session_state.nb_docs[new_id] = {
                    "title": new_title,
                    "content": st.session_state.np_content,
                    "created": now,
                    "updated": now,
                }
                st.session_state.nb_current_id = new_id
                st.session_state.np_title = new_title
                st.session_state.np_last_saved_content = st.session_state.np_content
                st.session_state.np_redo_content = ""
                st.toast("Saved as new document", icon=":material/check:")
                st.rerun()
    with col3:
        # Delete with confirmation popover
        with st.popover("Delete", key="np_delete_pop", use_container_width=True):
            st.warning("Are you sure you want to delete this document?")
            if st.button("Confirm Delete", key="np_delete_confirm", use_container_width=True):
                _delete_current_doc()
                st.rerun()
    with col4:
        if st.button("Undo", key="np_undo_btn", use_container_width=True, icon=":material/undo:"):
            # Revert to last saved content
            if st.session_state.np_content != st.session_state.np_last_saved_content:
                st.session_state.np_redo_content = st.session_state.np_content
                st.session_state.np_content = st.session_state.np_last_saved_content
                st.toast("Undone", icon=":material/undo:")
                st.rerun()
    with col5:
        if st.button("Redo", key="np_redo_btn", use_container_width=True, icon=":material/redo:"):
            # Restore content from redo buffer
            if st.session_state.np_redo_content:
                st.session_state.np_content = st.session_state.np_redo_content
                st.session_state.np_redo_content = ""
                st.toast("Redone", icon=":material/redo:")
                st.rerun()
    with col6:
        if st.button("Cut", key="np_cut_btn", use_container_width=True, icon=":material/content_cut:"):
            st.session_state.np_clipboard = st.session_state.np_content
            st.session_state.np_content = ""
            st.toast("Content cut to clipboard", icon=":material/content_cut:")
            st.rerun()
    with col7:
        if st.button("Copy", key="np_copy_btn", use_container_width=True, icon=":material/content_copy:"):
            st.session_state.np_clipboard = st.session_state.np_content
            st.toast("Content copied to clipboard", icon=":material/content_copy:")
    with col8:
        if st.button("Paste", key="np_paste_btn", use_container_width=True, icon=":material/content_paste:"):
            if st.session_state.np_clipboard:
                st.session_state.np_content = st.session_state.np_content + st.session_state.np_clipboard
                st.toast("Clipboard content pasted", icon=":material/content_paste:")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Title input
    st.text_input("Title", key="np_title", label_visibility="collapsed", placeholder="Document title")

    # Editor
    st.text_area(
        "Content",
        key="np_content",
        height=500,
        placeholder="Start typing... Use bullet points and paragraphs.",
        label_visibility="collapsed",
    )

    # Detect changes to content after widget rendering
    # If content changed from what we had before the widget, update doc and handle undo state
    # But we can rely on st.session_state.np_content being the new value now.
    # We need to update the current doc's content in session state (but not saved yet).
    if current_id and current_id in st.session_state.nb_docs:
        # We update the doc content as the user types (autosave)
        st.session_state.nb_docs[current_id]["content"] = st.session_state.np_content
        st.session_state.nb_docs[current_id]["title"] = st.session_state.np_title
        # We can also update last_saved? No, that's only on explicit Save.
        # But we might want to track unsaved changes? For simplicity, we autosave to session but not mark as saved.
        # We'll handle 'Save' separately.

    # Status footer
    word_count = len(st.session_state.np_content.split())
    char_count = len(st.session_state.np_content)
    if current_doc:
        updated_str = _format_date(datetime.datetime.fromisoformat(current_doc["updated"])) if "updated" in current_doc else "Not saved"
    else:
        updated_str = "No document"
    st.markdown(f"""
        <div class="status-footer">
            <span>Words: {word_count} | Characters: {char_count}</span>
            <span>Auto-save: On | Last saved: {updated_str}</span>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------
# Render: Daily Log
# ------------------------------

def render_dailylog():
    st.markdown('<div class="notebook-title">Daily Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Kanban board for your daily tasks and meetings</div>', unsafe_allow_html=True)

    # Filter bar
    with st.container():
        col_date, col_view, col_addtask, col_addmeet, col_search = st.columns([2, 2, 1, 1, 3])
        with col_date:
            st.date_input("Date", key="dl_date", value=st.session_state.dl_date, label_visibility="collapsed")
        with col_view:
            st.segmented_control(
                "View",
                options=["Day", "Week", "Month"],
                key="dl_view",
                default=st.session_state.dl_view,
                label_visibility="collapsed"
            )
        with col_addtask:
            with st.popover("+Task", key="dl_addtask_pop", use_container_width=True):
                st.markdown("**Add Task**")
                column_key = st.selectbox("Column", [c["key"] for c in COLUMNS], format_func=lambda x: next(c["label"] for c in COLUMNS if c["key"]==x), key="dl_addtask_col")
                task_content = st.text_area("Content", key="dl_addtask_content", height=100)
                if st.button("Add", key="dl_addtask_confirm", use_container_width=True):
                    if task_content.strip():
                        new_task = {
                            "id": _make_id(),
                            "content": task_content.strip(),
                            "created": datetime.datetime.now().isoformat()
                        }
                        st.session_state.dl_tasks[column_key].append(new_task)
                        st.toast("Task added", icon=":material/check:")
                        st.rerun()
                    else:
                        st.warning("Task content cannot be empty")
        with col_addmeet:
            with st.popover("+Meet", key="dl_addmeet_pop", use_container_width=True):
                st.markdown("**Add Meeting**")
                meeting_content = st.text_area("Meeting notes", key="dl_addmeet_content", height=100)
                if st.button("Add Meeting", key="dl_addmeet_confirm", use_container_width=True):
                    if meeting_content.strip():
                        new_task = {
                            "id": _make_id(),
                            "content": meeting_content.strip(),
                            "created": datetime.datetime.now().isoformat()
                        }
                        st.session_state.dl_tasks["meeting"].append(new_task)
                        st.toast("Meeting added", icon=":material/check:")
                        st.rerun()
                    else:
                        st.warning("Meeting notes cannot be empty")
        with col_search:
            st.text_input("Search", key="dl_search", value=st.session_state.dl_search, placeholder="Search cards...", label_visibility="collapsed")

    # Compute date range
    selected_date = st.session_state.dl_date
    view = st.session_state.dl_view
    start_date, end_date = _date_range(view, selected_date)
    date_caption = f"Showing: {_format_date(start_date)} - {_format_date(end_date)}"
    st.markdown(f'<div class="date-caption">{date_caption}</div>', unsafe_allow_html=True)

    # Filter tasks by date range and search
    search_query = st.session_state.dl_search.lower().strip()
    filtered_tasks = {col_key: [] for col_key in st.session_state.dl_tasks}
    for col_key, tasks in st.session_state.dl_tasks.items():
        for task in tasks:
            # Parse created datetime
            try:
                task_dt = datetime.datetime.fromisoformat(task["created"])
                task_date = task_dt.date()
            except:
                task_date = datetime.date.today()  # fallback
            # Date filter
            if start_date <= task_date <= end_date:
                # Search filter
                if search_query and search_query not in task["content"].lower():
                    continue
                filtered_tasks[col_key].append(task)
        # Sort newest first
        filtered_tasks[col_key].sort(key=lambda x: x["created"], reverse=True)

    # Kanban board: single row of 4 columns
    cols = st.columns(4, gap="small")
    for idx, col_def in enumerate(COLUMNS):
        col_key = col_def["key"]
        with cols[idx]:
            # Column header
            header_html = f"""
            <div class="kanban-header">
                {SVG_DICT[col_key]}
                <span class="label">{col_def['label']}</span>
                <span class="count">{len(filtered_tasks[col_key])}</span>
            </div>
            """
            st.markdown(header_html, unsafe_allow_html=True)

            # Tasks in this column
            if not filtered_tasks[col_key]:
                st.markdown('<div class="empty-state">No entries</div>', unsafe_allow_html=True)
            else:
                for task in filtered_tasks[col_key]:
                    task_id = task["id"]
                    # Card container
                    with st.container():
                        st.markdown('<div class="kanban-card">', unsafe_allow_html=True)
                        # Editable content
                        new_content = st.text_area(
                            "Content",
                            value=task["content"],
                            key=f"dl_task_content_{task_id}",
                            height=80,
                            label_visibility="collapsed",
                        )
                        # Update content if changed
                        if new_content != task["content"]:
                            task["content"] = new_content
                            # No need to rerun; Streamlit will update state.
                        # Meta row: date and delete button
                        col_meta_date, col_meta_del = st.columns([4, 1])
                        with col_meta_date:
                            st.markdown(f'<div class="card-meta">{_format_date(datetime.datetime.fromisoformat(task["created"]))}</div>', unsafe_allow_html=True)
                        with col_meta_del:
                            with st.popover("", key=f"dl_delete_pop_{task_id}", use_container_width=False, icon=":material/delete:"):
                                st.markdown("**Delete this card?**")
                                if st.button("Confirm", key=f"dl_delete_confirm_{task_id}", use_container_width=True):
                                    # Remove task
                                    st.session_state.dl_tasks[col_key] = [t for t in st.session_state.dl_tasks[col_key] if t["id"] != task_id]
                                    st.toast("Card deleted", icon=":material/delete:")
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

            # Add button at bottom of column
            st.markdown('<div style="margin-top: 0.5rem;">', unsafe_allow_html=True)
            with st.popover("+ Add", key=f"dl_add_btn_{col_key}", use_container_width=True):
                st.markdown(f"**Add to {col_def['label']}**")
                add_content = st.text_area("Content", key=f"dl_add_content_{col_key}", height=80)
                if st.button("Add", key=f"dl_add_confirm_{col_key}", use_container_width=True):
                    if add_content.strip():
                        new_task = {
                            "id": _make_id(),
                            "content": add_content.strip(),
                            "created": datetime.datetime.now().isoformat()
                        }
                        st.session_state.dl_tasks[col_key].append(new_task)
                        st.toast("Card added", icon=":material/check:")
                        st.rerun()
                    else:
                        st.warning("Content cannot be empty")
            st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# Main app
# ------------------------------

def main():
    setup_page_layout()
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    init_session()

    tab_notepad, tab_dailylog = st.tabs(["Notepad", "Daily Log"])
    with tab_notepad:
        render_notepad()
    with tab_dailylog:
        render_dailylog()

if __name__ == "__main__":
    main()
