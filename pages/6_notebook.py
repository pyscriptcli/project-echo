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
        background-color: #F7F7F7;
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
        color: #111111;
        margin-bottom: 0.25rem;
    }
    .notebook-subtitle {
        font-size: 1rem;
        color: #555555;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #CCCCCC;
        padding-bottom: 0.75rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        border-bottom: 2px solid #CCCCCC;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.2rem;
        color: #555555;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #111111 !important;
        border-bottom: 3px solid #111111;
    }

    /* Notepad specific */
    .editor-area textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 4px !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-size: 0.95rem !important;
        color: #111111 !important;
        padding: 1rem !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.02);
    }
    .status-footer {
        display: flex;
        justify-content: space-between;
        color: #888888;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        border-top: 1px solid #E0E0E0;
        padding-top: 0.5rem;
    }

    /* Daily Log specific */
    .date-caption {
        font-size: 0.9rem;
        color: #555555;
        margin-bottom: 1rem;
    }
    .kanban-column {
        background-color: #FFFFFF;
        border-radius: 6px;
        border: 1px solid #E0E0E0;
        padding: 0.75rem;
        min-height: 400px;
    }
    .kanban-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #CCCCCC;
        padding-bottom: 0.5rem;
    }
    .kanban-header .emoji {
        font-size: 1.2rem;
        filter: grayscale(100%);
    }
    .kanban-header .label {
        font-weight: 600;
        color: #111111;
    }
    .kanban-header .count {
        background-color: #EEEEEE;
        color: #333333;
        border-radius: 12px;
        padding: 0.1rem 0.5rem;
        font-size: 0.8rem;
        margin-left: auto;
    }
    .kanban-card {
        background-color: #FAFAFA;
        border: 1px solid #E0E0E0;
        border-radius: 4px;
        padding: 0.6rem;
        margin-bottom: 0.5rem;
    }
    .kanban-card textarea {
        background-color: transparent !important;
        border: none !important;
        resize: none !important;
        font-size: 0.9rem !important;
        color: #111111 !important;
        padding: 0 !important;
        line-height: 1.4;
    }
    .card-meta {
        font-size: 0.75rem;
        color: #888888;
        margin-top: 0.25rem;
        display: flex;
        align-items: center;
    }
    .empty-state {
        text-align: center;
        color: #888888;
        font-style: italic;
        padding: 2rem 0;
    }

    /* Button Uniform Styling */
    .stButton > button, div[data-testid="stPopover"] > button {
        border-radius: 4px;
        font-weight: 500;
        background-color: #FFFFFF;
        color: #111111;
        border: 1px solid #CCCCCC;
        transition: all 0.2s;
        height: 38px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 0.25rem 0.5rem;
    }
    .stButton > button:hover, div[data-testid="stPopover"] > button:hover {
        background-color: #F0F0F0;
        border-color: #999999;
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
    {"key": "client", "label": "Client Related"},
    {"key": "admin", "label": "Admin"},
    {"key": "adhoc", "label": "Adhoc"},
    {"key": "meeting", "label": "Meetings"},
]

EMOJI_DICT = {
    "client": "👤",
    "admin": "⚙",
    "adhoc": "📌",
    "meeting": "🗓",
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
    """
    if view == "Day":
        return date_obj, date_obj
    elif view == "Week":
        start = date_obj - datetime.timedelta(days=date_obj.weekday())
        end = start + datetime.timedelta(days=6)
        return start, end
    elif view == "Month":
        start = date_obj.replace(day=1)
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
    if "nb_docs" not in st.session_state:
        st.session_state.nb_docs = {}
        welcome_id = _make_id()
        now = datetime.datetime.now().isoformat()
        st.session_state.nb_docs[welcome_id] = {
            "title": "Welcome to Notepad",
            "content": "Minimalist text editor.\n\nSelect '+ New' to create a new file.",
            "created": now,
            "updated": now,
        }
        st.session_state.nb_current_id = welcome_id

    if "dl_tasks" not in st.session_state:
        st.session_state.dl_tasks = {col["key"]: [] for col in COLUMNS}
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

# ------------------------------
# Notepad Logic Functions
# ------------------------------

def save_current_doc():
    current_id = st.session_state.nb_current_id
    if current_id and current_id in st.session_state.nb_docs:
        # Retrieve values directly from widget session state keys
        title_key = f"title_{current_id}"
        content_key = f"content_{current_id}"
        st.session_state.nb_docs[current_id]["title"] = st.session_state[title_key]
        st.session_state.nb_docs[current_id]["content"] = st.session_state[content_key]
        st.session_state.nb_docs[current_id]["updated"] = datetime.datetime.now().isoformat()
        st.toast("Saved successfully", icon="✓")

# ------------------------------
# Render: Notepad
# ------------------------------

def render_notepad():
    st.markdown('<div class="notebook-title">Notepad</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Minimal text editor</div>', unsafe_allow_html=True)

    doc_options = list(st.session_state.nb_docs.keys())
    
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    
    with col1:
        if doc_options:
            index = doc_options.index(st.session_state.nb_current_id) if st.session_state.nb_current_id in doc_options else 0
            selected_id = st.selectbox(
                "Open document",
                options=doc_options,
                index=index,
                format_func=lambda x: st.session_state.nb_docs[x]["title"],
                key="np_doc_selector",
                label_visibility="collapsed"
            )
            if selected_id != st.session_state.nb_current_id:
                st.session_state.nb_current_id = selected_id
                st.rerun()
        else:
            st.selectbox("Open document", ["No documents"], disabled=True, label_visibility="collapsed")

    with col2:
        if st.button("+ New", use_container_width=True):
            new_id = _make_id()
            now = datetime.datetime.now().isoformat()
            st.session_state.nb_docs[new_id] = {
                "title": "Untitled",
                "content": "",
                "created": now,
                "updated": now,
            }
            st.session_state.nb_current_id = new_id
            st.rerun()

    with col3:
        if st.button("× Delete", use_container_width=True, disabled=not bool(doc_options)):
            current_id = st.session_state.nb_current_id
            if current_id in st.session_state.nb_docs:
                del st.session_state.nb_docs[current_id]
                if st.session_state.nb_docs:
                    st.session_state.nb_current_id = list(st.session_state.nb_docs.keys())[0]
                else:
                    st.session_state.nb_current_id = None
                st.toast("Document deleted", icon="✓")
                st.rerun()

    with col4:
        st.button("✓ Save", on_click=save_current_doc, use_container_width=True, disabled=not bool(doc_options))

    # Editor Area
    current_id = st.session_state.nb_current_id
    if current_id and current_id in st.session_state.nb_docs:
        doc = st.session_state.nb_docs[current_id]
        
        st.text_input(
            "Title", 
            value=doc["title"], 
            key=f"title_{current_id}", 
            label_visibility="collapsed"
        )
        
        st.markdown('<div class="editor-area">', unsafe_allow_html=True)
        st.text_area(
            "Content",
            value=doc["content"],
            height=500,
            key=f"content_{current_id}",
            label_visibility="collapsed",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        word_count = len(st.session_state[f"content_{current_id}"].split()) if f"content_{current_id}" in st.session_state else len(doc["content"].split())
        char_count = len(st.session_state[f"content_{current_id}"]) if f"content_{current_id}" in st.session_state else len(doc["content"])
        updated_str = _format_date(datetime.datetime.fromisoformat(doc["updated"]))
        
        st.markdown(f"""
            <div class="status-footer">
                <span>Words: {word_count} | Characters: {char_count}</span>
                <span>Last saved: {updated_str}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No documents available. Click '+ New' to create one.")

# ------------------------------
# Render: Daily Log
# ------------------------------

def render_dailylog():
    st.markdown('<div class="notebook-title">Daily Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Kanban board for daily operations</div>', unsafe_allow_html=True)

    col_date, col_view, _ = st.columns([2, 2, 6])
    with col_date:
        st.date_input("Date", key="dl_date", label_visibility="collapsed")
    with col_view:
        st.segmented_control(
            "View",
            options=["Day", "Week", "Month"],
            key="dl_view",
            label_visibility="collapsed"
        )

    selected_date = st.session_state.dl_date
    view = st.session_state.dl_view
    start_date, end_date = _date_range(view, selected_date)
    
    if start_date == end_date:
        date_caption = f"Showing: {_format_date(start_date)}"
    else:
        date_caption = f"Showing: {_format_date(start_date)} - {_format_date(end_date)}"
    st.markdown(f'<div class="date-caption">{date_caption}</div>', unsafe_allow_html=True)

    filtered_tasks = {col_key: [] for col_key in st.session_state.dl_tasks}
    
    for col_key, tasks in st.session_state.dl_tasks.items():
        for task in tasks:
            try:
                task_dt = datetime.datetime.fromisoformat(task["created"])
                task_date = task_dt.date()
            except:
                task_date = datetime.date.today()
                
            if start_date <= task_date <= end_date:
                filtered_tasks[col_key].append(task)
        filtered_tasks[col_key].sort(key=lambda x: x["created"], reverse=True)

    cols = st.columns(4, gap="small")
    for idx, col_def in enumerate(COLUMNS):
        col_key = col_def["key"]
        with cols[idx]:
            header_html = f"""<div class="kanban-header">
                <span class="emoji">{EMOJI_DICT[col_key]}</span>
                <span class="label">{col_def['label']}</span>
                <span class="count">{len(filtered_tasks[col_key])}</span>
            </div>"""
            st.markdown(header_html, unsafe_allow_html=True)

            if not filtered_tasks[col_key]:
                st.markdown('<div class="empty-state">No entries</div>', unsafe_allow_html=True)
            else:
                for task in filtered_tasks[col_key]:
                    task_id = task["id"]
                    with st.container():
                        st.markdown('<div class="kanban-card">', unsafe_allow_html=True)
                        new_content = st.text_area(
                            "Content",
                            value=task["content"],
                            key=f"dl_task_content_{task_id}",
                            height=70,
                            label_visibility="collapsed",
                        )
                        if new_content != task["content"]:
                            task["content"] = new_content
                        
                        col_meta_date, col_meta_del = st.columns([5, 1])
                        with col_meta_date:
                            st.markdown(f'<div class="card-meta">{_format_date(datetime.datetime.fromisoformat(task["created"]))}</div>', unsafe_allow_html=True)
                        with col_meta_del:
                            if st.button("×", key=f"dl_del_{task_id}", help="Delete"):
                                st.session_state.dl_tasks[col_key] = [t for t in st.session_state.dl_tasks[col_key] if t["id"] != task_id]
                                st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

            with st.popover("+ Add", key=f"dl_add_pop_{col_key}", use_container_width=True):
                add_content = st.text_area("Content", key=f"dl_add_content_{col_key}", height=80, label_visibility="collapsed", placeholder="New entry...")
                if st.button("✓ Confirm", key=f"dl_add_confirm_{col_key}", use_container_width=True):
                    if add_content.strip():
                        # Link task creation time strictly to currently selected date so it doesn't vanish based on view limits
                        task_time_ref = datetime.datetime.combine(st.session_state.dl_date, datetime.datetime.now().time())
                        new_task = {
                            "id": _make_id(),
                            "content": add_content.strip(),
                            "created": task_time_ref.isoformat()
                        }
                        st.session_state.dl_tasks[col_key].append(new_task)
                        st.toast("Card added", icon="✓")
                        st.rerun()

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
