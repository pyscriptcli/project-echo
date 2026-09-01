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
# CSS (Monochrome & Minimalist)
# ------------------------------
NOTEBOOK_CSS = """
<style>
    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background-color: #FFFFFF;
        font-family: 'Inter', sans-serif;
        color: #111111;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Titles and subtitles */
    .notebook-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        font-size: 2.2rem;
        color: #000000;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .notebook-subtitle {
        font-size: 0.95rem;
        color: #666666;
        margin-bottom: 2rem;
        border-bottom: 1px solid #EAEAEA;
        padding-bottom: 1rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #EAEAEA;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        font-size: 1rem;
        color: #888888;
        padding: 0.5rem 0.25rem;
    }
    .stTabs [aria-selected="true"] {
        color: #000000 !important;
        border-bottom: 2px solid #000000;
    }

    /* Notepad specific */
    .editor-area textarea {
        background-color: #FAFAFA !important;
        border: 1px solid #EAEAEA !important;
        border-radius: 4px !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-size: 0.95rem !important;
        color: #000000 !important;
        padding: 1.5rem !important;
        box-shadow: none !important;
    }
    .editor-area textarea:focus {
        border-color: #CCCCCC !important;
    }
    .status-footer {
        display: flex;
        justify-content: space-between;
        color: #999999;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }

    /* Kanban & Views */
    .view-header {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #000000;
        border-bottom: 1px solid #EEEEEE;
        padding-bottom: 0.5rem;
    }
    .kanban-column {
        background-color: #FAFAFA;
        border-radius: 4px;
        border: 1px solid #EAEAEA;
        padding: 0.75rem;
        min-height: 500px;
    }
    .kanban-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .kanban-header .label {
        font-weight: 600;
        font-size: 0.95rem;
        color: #000000;
    }
    .kanban-header .count {
        background-color: #EEEEEE;
        color: #333333;
        border-radius: 12px;
        padding: 0.1rem 0.5rem;
        font-size: 0.75rem;
        margin-left: auto;
    }
    .kanban-card {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-radius: 4px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .card-meta {
        font-size: 0.7rem;
        color: #999999;
        margin-top: 0.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .empty-state {
        text-align: center;
        color: #AAAAAA;
        font-size: 0.85rem;
        padding: 2rem 0;
    }
    .day-col-header {
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    /* Button Uniform Styling (Monochrome) */
    .stButton > button, div[data-testid="stPopover"] > button {
        border-radius: 4px;
        font-weight: 500;
        background-color: #FFFFFF;
        color: #000000;
        border: 1px solid #DDDDDD;
        transition: all 0.2s;
        height: 36px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 0.25rem 0.5rem;
        font-size: 0.9rem;
    }
    .stButton > button:hover, div[data-testid="stPopover"] > button:hover {
        background-color: #F5F5F5;
        border-color: #BBBBBB;
    }
</style>
"""

# ------------------------------
# Constants
# ------------------------------

COLUMNS = [
    {"key": "client", "label": "Client"},
    {"key": "admin", "label": "Admin"},
    {"key": "adhoc", "label": "Adhoc"},
    {"key": "meeting", "label": "Meetings"},
]

# ------------------------------
# Helper functions
# ------------------------------

def _make_id():
    return uuid.uuid4().hex[:8]

def _date_range(view, date_obj):
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
    return date_obj, date_obj

def _format_date(d):
    if isinstance(d, datetime.datetime):
        return d.strftime("%b %d, %Y")
    elif isinstance(d, datetime.date):
        return d.strftime("%b %d, %Y")
    return str(d)

# ------------------------------
# Session state initialization
# ------------------------------

def init_session():
    # Notepad init
    if "nb_docs" not in st.session_state:
        st.session_state.nb_docs = {}
        welcome_id = _make_id()
        now = datetime.datetime.now().isoformat()
        st.session_state.nb_docs[welcome_id] = {
            "title": "Welcome to Notepad",
            "content": "Minimal text editor.\n\nUse this space for quick drafts or notes.",
            "created": now,
            "updated": now,
        }
        st.session_state.nb_current_id = welcome_id
        st.session_state.np_title = "Welcome to Notepad"
        st.session_state.np_content = "Minimal text editor.\n\nUse this space for quick drafts or notes."

    if "nb_current_id" not in st.session_state:
        st.session_state.nb_current_id = None
        st.session_state.np_title = ""
        st.session_state.np_content = ""

    # Daily Log init
    if "dl_tasks" not in st.session_state:
        st.session_state.dl_tasks = {col["key"]: [] for col in COLUMNS}
        sample_date = datetime.datetime.now()
        st.session_state.dl_tasks["client"].append({
            "id": _make_id(), "content": "Prepare quarterly report", "created": sample_date.isoformat()
        })
        st.session_state.dl_tasks["admin"].append({
            "id": _make_id(), "content": "Update documentation", "created": sample_date.isoformat()
        })
        
    if "dl_date" not in st.session_state:
        st.session_state.dl_date = datetime.date.today()
    if "dl_view" not in st.session_state:
        st.session_state.dl_view = "Day"

# ------------------------------
# Notepad Logic
# ------------------------------

def handle_doc_switch():
    cid = st.session_state.np_doc_selector
    st.session_state.nb_current_id = cid
    if cid and cid in st.session_state.nb_docs:
        st.session_state.np_title = st.session_state.nb_docs[cid]["title"]
        st.session_state.np_content = st.session_state.nb_docs[cid]["content"]

def create_new_doc():
    new_id = _make_id()
    now = datetime.datetime.now().isoformat()
    st.session_state.nb_docs[new_id] = {
        "title": "Untitled",
        "content": "",
        "created": now,
        "updated": now,
    }
    st.session_state.nb_current_id = new_id
    st.session_state.np_title = "Untitled"
    st.session_state.np_content = ""

def delete_current_doc():
    cid = st.session_state.nb_current_id
    if cid and cid in st.session_state.nb_docs:
        del st.session_state.nb_docs[cid]
        if st.session_state.nb_docs:
            next_id = list(st.session_state.nb_docs.keys())[0]
            st.session_state.nb_current_id = next_id
            st.session_state.np_title = st.session_state.nb_docs[next_id]["title"]
            st.session_state.np_content = st.session_state.nb_docs[next_id]["content"]
        else:
            st.session_state.nb_current_id = None
            st.session_state.np_title = ""
            st.session_state.np_content = ""
        st.toast("Document deleted")

def save_current_doc():
    cid = st.session_state.nb_current_id
    if cid and cid in st.session_state.nb_docs:
        st.session_state.nb_docs[cid]["title"] = st.session_state.np_title
        st.session_state.nb_docs[cid]["content"] = st.session_state.np_content
        st.session_state.nb_docs[cid]["updated"] = datetime.datetime.now().isoformat()
        st.toast("Saved successfully")

def render_notepad():
    st.markdown('<div class="notebook-title">Notepad</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">A minimal environment for your thoughts.</div>', unsafe_allow_html=True)

    doc_options = list(st.session_state.nb_docs.keys())
    has_docs = bool(doc_options)
    
    col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
    
    with col1:
        if has_docs:
            current_index = doc_options.index(st.session_state.nb_current_id) if st.session_state.nb_current_id in doc_options else 0
            st.selectbox(
                "Open document",
                options=doc_options,
                index=current_index,
                format_func=lambda x: st.session_state.nb_docs[x]["title"],
                key="np_doc_selector",
                on_change=handle_doc_switch,
                label_visibility="collapsed"
            )
        else:
            st.selectbox("Open", ["No documents"], disabled=True, label_visibility="collapsed")

    with col2:
        st.button("+ New", on_click=create_new_doc, use_container_width=True)

    with col3:
        st.button("Delete", on_click=delete_current_doc, use_container_width=True, disabled=not has_docs)

    with col4:
        st.button("Save", on_click=save_current_doc, use_container_width=True, disabled=not has_docs)

    if has_docs and st.session_state.nb_current_id:
        st.text_input("Title", key="np_title", label_visibility="collapsed", placeholder="Document Title")
        
        st.markdown('<div class="editor-area">', unsafe_allow_html=True)
        st.text_area(
            "Content",
            key="np_content",
            height=450,
            label_visibility="collapsed",
            placeholder="Start typing..."
        )
        st.markdown('</div>', unsafe_allow_html=True)

        doc_meta = st.session_state.nb_docs[st.session_state.nb_current_id]
        word_count = len(st.session_state.np_content.split())
        updated_str = _format_date(datetime.datetime.fromisoformat(doc_meta["updated"]))
        
        st.markdown(f"""
            <div class="status-footer">
                <span>{word_count} words</span>
                <span>Last saved: {updated_str}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Your notepad is empty. Create a new document to begin.")


# ------------------------------
# Daily Log Views & Render
# ------------------------------

def get_tasks_for_date(target_date):
    """Retrieve all tasks across categories for a specific date."""
    daily_tasks = []
    for col_def in COLUMNS:
        col_key = col_def["key"]
        for task in st.session_state.dl_tasks[col_key]:
            try:
                t_date = datetime.datetime.fromisoformat(task["created"]).date()
            except:
                t_date = datetime.date.today()
            if t_date == target_date:
                daily_tasks.append({"cat_label": col_def["label"], "cat_key": col_key, **task})
    return sorted(daily_tasks, key=lambda x: x["created"], reverse=True)

def render_day_view(selected_date):
    """Standard Kanban grouped by Category"""
    cols = st.columns(4, gap="small")
    for idx, col_def in enumerate(COLUMNS):
        col_key = col_def["key"]
        with cols[idx]:
            # Filter tasks for this category for the exact day
            tasks = [t for t in st.session_state.dl_tasks[col_key] 
                     if datetime.datetime.fromisoformat(t["created"]).date() == selected_date]
            tasks.sort(key=lambda x: x["created"], reverse=True)

            st.markdown(f"""<div class="kanban-header">
                <span class="label">{col_def['label']}</span>
                <span class="count">{len(tasks)}</span>
            </div>""", unsafe_allow_html=True)

            if not tasks:
                st.markdown('<div class="empty-state">No tasks</div>', unsafe_allow_html=True)
            else:
                for task in tasks:
                    task_id = task["id"]
                    st.markdown(f"""
                        <div class="kanban-card">
                            <div>{task['content']}</div>
                            <div class="card-meta">
                                <span>{datetime.datetime.fromisoformat(task['created']).strftime('%H:%M')}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Delete", key=f"del_{task_id}", help="Remove task"):
                        st.session_state.dl_tasks[col_key] = [t for t in st.session_state.dl_tasks[col_key] if t["id"] != task_id]
                        st.rerun()

            with st.popover("+ Add", key=f"add_pop_{col_key}", use_container_width=True):
                add_content = st.text_area("Content", key=f"add_content_{col_key}", height=80, label_visibility="collapsed")
                if st.button("Confirm", key=f"add_confirm_{col_key}", use_container_width=True):
                    if add_content.strip():
                        t_ref = datetime.datetime.combine(selected_date, datetime.datetime.now().time())
                        st.session_state.dl_tasks[col_key].append({
                            "id": _make_id(),
                            "content": add_content.strip(),
                            "created": t_ref.isoformat()
                        })
                        st.toast("Task added")
                        st.rerun()

def render_week_view(selected_date):
    """Weekly board grouped by Days (Mon-Sun)"""
    start, end = _date_range("Week", selected_date)
    days = [start + datetime.timedelta(days=i) for i in range(7)]
    
    st.markdown('<div class="view-header">Weekly Planner</div>', unsafe_allow_html=True)
    cols = st.columns(7, gap="small")
    
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"""
                <div class="day-col-header">
                    <div style="font-size: 0.8rem; color: #666;">{day.strftime('%a').upper()}</div>
                    <div style="font-size: 1.1rem; color: #000;">{day.strftime('%d')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            tasks = get_tasks_for_date(day)
            if not tasks:
                st.markdown('<div class="empty-state" style="padding: 1rem 0;">Empty</div>', unsafe_allow_html=True)
            else:
                for task in tasks:
                    st.markdown(f"""
                        <div class="kanban-card" style="font-size: 0.8rem; padding: 0.5rem;">
                            <div style="color: #666; font-size: 0.65rem; margin-bottom: 0.2rem; font-weight: 600;">{task['cat_label'].upper()}</div>
                            {task['content']}
                        </div>
                    """, unsafe_allow_html=True)

def render_month_view(selected_date):
    """List grouped by Date for the entire Month"""
    start, end = _date_range("Month", selected_date)
    st.markdown('<div class="view-header">Monthly Overview</div>', unsafe_allow_html=True)
    
    # Collect all tasks for the month
    month_tasks = []
    for col_def in COLUMNS:
        col_key = col_def["key"]
        for task in st.session_state.dl_tasks[col_key]:
            try:
                t_date = datetime.datetime.fromisoformat(task["created"]).date()
            except:
                t_date = datetime.date.today()
            if start <= t_date <= end:
                month_tasks.append({"date": t_date, "cat_label": col_def["label"], **task})
                
    month_tasks.sort(key=lambda x: (x["date"], x["created"]), reverse=True)
    
    if not month_tasks:
        st.info("No tasks recorded for this month.")
        return

    # Group by date for rendering
    grouped_tasks = {}
    for task in month_tasks:
        d = task["date"]
        if d not in grouped_tasks:
            grouped_tasks[d] = []
        grouped_tasks[d].append(task)
        
    for d, tasks in grouped_tasks.items():
        st.markdown(f"**{d.strftime('%A, %b %d')}**")
        for task in tasks:
            st.markdown(f"""
                <div class="kanban-card" style="display: flex; gap: 1rem; align-items: center; padding: 0.5rem 1rem;">
                    <span style="font-size: 0.75rem; color: #888; width: 80px; font-weight: 600;">{task['cat_label']}</span>
                    <span>{task['content']}</span>
                </div>
            """, unsafe_allow_html=True)

def render_dailylog():
    st.markdown('<div class="notebook-title">Daily Log</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Organize and track your daily operations.</div>', unsafe_allow_html=True)

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

    st.markdown("<br>", unsafe_allow_html=True)
    
    view = st.session_state.dl_view
    date_val = st.session_state.dl_date

    if view == "Day":
        render_day_view(date_val)
    elif view == "Week":
        render_week_view(date_val)
    elif view == "Month":
        render_month_view(date_val)


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
