import sys
import os
import datetime
import uuid
import streamlit as st
import pandas as pd

# Add project root to sys.path to allow imports from components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.sidebar import setup_page_layout
from utils.auth import get_current_user, require_login
from utils.notebook_db import (
    fetch_docs,
    upsert_doc,
    delete_doc,
    fetch_logs_in_range,
    upsert_log,
)

# ------------------------------
# Page configuration
# ------------------------------
st.set_page_config(
    page_title="Project Echo - Notebook",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------
# CSS (UI Matched to Reference)
# ------------------------------
NOTEBOOK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&family=Inter:wght@300;400;500;600&display=swap');

    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Background and typography (Matched to Grid Image) */
    .stApp {
        background-color: #A3ACB5;
        font-family: 'Montserrat', sans-serif;
        color: #2A3441;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }

    /* Titles and subtitles */
    .notebook-title {
        font-family: 'Cormorant Garamond', serif;
        font-weight: 600;
        font-style: italic;
        font-size: 2.4rem;
        color: #0D1B3E;
        margin-bottom: 0.25rem;
    }
    .notebook-subtitle {
        font-size: 1rem;
        color: #5A607A;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid rgba(13,27,62,0.2);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 1.1rem;
        color: #5A607A;
        padding: 0.5rem 0.25rem;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #0D1B3E !important;
        border-bottom: 2px solid #333333;
    }

    /* Containers */
    .stTextArea textarea, .stTextInput input, .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(13,27,62,0.2) !important;
        border-radius: 0 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1rem !important;
        color: #2A3441 !important;
        box-shadow: none !important;
        line-height: 1.6 !important;
    }

    /* Daily Log: hide the vertical scrollbar on edit boxes (text still scrolls) */
    .dl-log-scroll .stTextArea textarea,
    .dl-log-scroll textarea {
        scrollbar-width: none;          /* Firefox */
        -ms-overflow-style: none;       /* IE/Edge */
    }
    .dl-log-scroll textarea::-webkit-scrollbar {
        display: none;                  /* Chrome/Safari/Edge */
        width: 0;
        height: 0;
    }

    .kanban-card, div[data-testid="stMetric"], .dialog-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 0.5rem 0.65rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    .status-footer {
        display: flex;
        justify-content: space-between;
        color: #718096;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }

    /* Kanban & Views */
    .view-header {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.5rem;
        color: #0D1B3E;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(13, 27, 62, 0.15);
        padding-bottom: 0.5rem;
    }
    .kanban-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.35rem;
    }
    .kanban-header .label {
        font-weight: 600;
        font-size: 0.85rem;
        color: #0D1B3E;
    }
    .empty-state {
        text-align: center;
        color: #a0aec0;
        font-size: 0.85rem;
        padding: 0.75rem 0;
        font-style: italic;
    }
    .day-col-header {
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    /* Button Uniform Styling — navy, gold border, flat */
    .stButton > button,
    div[data-testid="stPopover"] > button,
    div[data-testid="stDownloadButton"] > button {
        border-radius: 0 !important;
        font-weight: 600 !important;
        background-color: #333333 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
        min-height: 28px !important;
        height: 28px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.1rem 0.5rem !important;
        width: auto !important;
        font-size: 0.68rem !important;
    }
    .stButton > button:hover,
    div[data-testid="stPopover"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #1f1f1f !important;
        border-color: #1f1f1f !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }
    
    /* Secondary Buttons override (dark gray) */
    button[kind="secondary"] {
        background-color: #333333 !important;
        color: #FFFFFF !important;
        border: 1px solid #333333 !important;
        box-shadow: none !important;
    }
    button[kind="secondary"]:hover {
        background-color: #1f1f1f !important;
        border-color: #1f1f1f !important;
        color: #FFFFFF !important;
        box-shadow: none !important;
    }
    
    /* Notepad Editor Expansion */
    .stTextArea {
        margin-top: 0.5rem;
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
    return str(uuid.uuid4())

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


def _current_user_id():
    user = get_current_user()
    return user["id"] if user and user.get("id") else None


def _empty_log():
    return {c["key"]: "" for c in COLUMNS}


def _load_log(user_id, date_str):
    """Return the {client, admin, adhoc, meeting} dict for a user+date.

    Caches in st.session_state.dl_logs so edits are only re-read on refresh,
    but the source of truth is Supabase (write-through on each edit).
    """
    if date_str in st.session_state.dl_logs:
        return st.session_state.dl_logs[date_str]

    loaded = _empty_log()
    try:
        d = datetime.date.fromisoformat(date_str)
    except ValueError:
        d = None
    if user_id and d is not None:
        rows = fetch_logs_in_range(user_id, d, d)
        if rows:
            row = rows[0]
            for c in COLUMNS:
                loaded[c["key"]] = row.get(c["key"]) or ""
    st.session_state.dl_logs[date_str] = loaded
    return loaded


def _save_log(user_id, date_str, col_key, value):
    """Auto-save a single category field to Supabase; keep session in sync."""
    st.session_state.dl_logs.setdefault(date_str, _empty_log())
    st.session_state.dl_logs[date_str][col_key] = value
    if user_id:
        try:
            d = datetime.date.fromisoformat(date_str)
        except ValueError:
            return
        upsert_log(user_id, d, st.session_state.dl_logs[date_str])

# ------------------------------
# Session state initialization
# ------------------------------

def init_session():
    current_user = get_current_user()
    user_id = _current_user_id() if current_user else None

    # Notepad init (per-user, DB-backed)
    if "nb_docs" not in st.session_state:
        st.session_state.nb_docs = {}

        if user_id:
            docs_rows = fetch_docs(user_id)
            for row in docs_rows:
                st.session_state.nb_docs[row["id"]] = {
                    "title": row.get("title") or "Untitled",
                    "content": row.get("content") or "",
                    "created": row.get("created_at") or "",
                    "updated": row.get("updated_at") or "",
                }

        # Seed a default welcome doc only when this user has none.
        if not st.session_state.nb_docs:
            welcome_id = _make_id()
            now = datetime.datetime.now().isoformat()
            st.session_state.nb_docs[welcome_id] = {
                "title": "Welcome to Notepad",
                "content": "Minimal text editor.\n\nUse this space for quick drafts, notes, or ideas. Click 'Notes Gallery' to view your previous notes.",
                "created": now,
                "updated": now,
            }
            # Nothing is persisted to Supabase until the user saves a note.

    if "nb_current_id" not in st.session_state:
        first_id = next(iter(st.session_state.nb_docs), None)
        st.session_state.nb_current_id = first_id
        first_doc = st.session_state.nb_docs.get(first_id, {}) if first_id else {}
        st.session_state.np_title = first_doc.get("title", "")
        st.session_state.np_content = first_doc.get("content", "")
    if "nb_save_state" not in st.session_state:
        st.session_state["nb_save_state"] = "saved"
    if "nb_saved_at" not in st.session_state:
        st.session_state["nb_saved_at"] = None

    # Daily Log init (view state only; log data is loaded per-date from Supabase)
    if "dl_logs" not in st.session_state:
        st.session_state.dl_logs = {}
    if "dl_date" not in st.session_state:
        st.session_state.dl_date = datetime.date.today()
    if "dl_view" not in st.session_state:
        st.session_state.dl_view = "Day"

# ------------------------------
# Notepad Logic & Modals
# ------------------------------

def select_doc(doc_id):
    st.session_state.nb_current_id = doc_id
    if doc_id in st.session_state.nb_docs:
        st.session_state.np_title = st.session_state.nb_docs[doc_id]["title"]
        st.session_state.np_content = st.session_state.nb_docs[doc_id]["content"]

def create_new_doc():
    new_id = _make_id()
    now = datetime.datetime.now().isoformat()
    st.session_state.nb_docs[new_id] = {
        "title": "Untitled Note",
        "content": "",
        "created": now,
        "updated": now,
    }
    select_doc(new_id)

    user_id = _current_user_id()
    if user_id:
        upsert_doc(user_id, new_id, "Untitled Note", "")

def delete_current_doc():
    cid = st.session_state.nb_current_id
    if cid and cid in st.session_state.nb_docs:
        del st.session_state.nb_docs[cid]
        user_id = _current_user_id()
        if user_id:
            delete_doc(user_id, cid)
        if st.session_state.nb_docs:
            next_id = list(st.session_state.nb_docs.keys())[0]
            select_doc(next_id)
        else:
            st.session_state.nb_current_id = None
            st.session_state.np_title = ""
            st.session_state.np_content = ""

def save_current_doc():
    cid = st.session_state.nb_current_id
    if cid and cid in st.session_state.nb_docs:
        st.session_state.nb_docs[cid]["title"] = st.session_state.np_title
        st.session_state.nb_docs[cid]["content"] = st.session_state.np_content
        st.session_state.nb_docs[cid]["updated"] = datetime.datetime.now().isoformat()
        st.session_state["nb_save_state"] = "saving"
        user_id = _current_user_id()
        if user_id:
            upsert_doc(user_id, cid, st.session_state.np_title, st.session_state.np_content)
        st.session_state["nb_save_state"] = "saved"
        st.session_state["nb_saved_at"] = datetime.datetime.now().strftime("%I:%M:%S %p")

@st.dialog("Notes Gallery", width="large")
def notes_gallery_modal():
    search_query = st.text_input("Search", placeholder="Search by title or content...", label_visibility="collapsed").lower()
    
    st.markdown("<hr style='border: none; border-top: 1px solid #e2e8f0; margin: 1rem 0;'>", unsafe_allow_html=True)
    
    filtered_docs = {
        k: v for k, v in st.session_state.nb_docs.items()
        if search_query in v["title"].lower() or search_query in v["content"].lower()
    }
    sorted_docs = sorted(filtered_docs.items(), key=lambda x: x[1]["updated"], reverse=True)
    
    if not sorted_docs:
        st.markdown("<div class='empty-state'>No notes found. Create a new one to get started!</div>", unsafe_allow_html=True)
        return

    # Create a responsive grid layout
    cols = st.columns(3, gap="medium")
    for idx, (doc_id, doc) in enumerate(sorted_docs):
        with cols[idx % 3]:
            title = doc["title"] if doc["title"].strip() else "Untitled"
            date_str = datetime.datetime.fromisoformat(doc["updated"]).strftime("%b %d, %Y")
            preview = doc["content"][:80] + "..." if len(doc["content"]) > 80 else doc["content"]
            if not preview.strip():
                preview = "Empty note"
            
            with st.container(border=True):
                st.markdown(f"<div style='font-family: \"Cormorant Garamond\", serif; font-size: 1.2rem; font-weight: 600; color: #0D1B3E; margin-bottom: 0.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{title}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 0.75rem; color: #5A607A; margin-bottom: 0.8rem;'>{date_str}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size: 0.85rem; color: #3A4454; height: 3.5rem; overflow: hidden; margin-bottom: 1rem; line-height: 1.4;'>{preview}</div>", unsafe_allow_html=True)
                
                # Active styling logic
                btn_type = "primary" if doc_id == st.session_state.nb_current_id else "secondary"
                if st.button("Edit Note", key=f"open_modal_{doc_id}", use_container_width=True, type=btn_type):
                    select_doc(doc_id)
                    st.rerun()

def render_notepad():
    st.markdown('<p class="page-eyebrow">Notebook</p>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-title">Notepad</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">A distraction-free environment for your thoughts.</div>', unsafe_allow_html=True)

    # Top Toolbar
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 4, 1.5, 1.5])
    
    with col1:
        if st.button("Notes Gallery", use_container_width=True):
            notes_gallery_modal()
    with col2:
        st.button("+ New Note", on_click=create_new_doc, use_container_width=True, type="secondary")
    
    has_docs = bool(st.session_state.nb_docs)
    
    with col4:
        st.button("Delete Note", on_click=delete_current_doc, use_container_width=True, type="secondary", disabled=not has_docs)
    with col5:
        st.button("Save Changes", on_click=save_current_doc, use_container_width=True, disabled=not has_docs)

    # Main Editor Area
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    if has_docs and st.session_state.nb_current_id in st.session_state.nb_docs:
        doc_meta = st.session_state.nb_docs[st.session_state.nb_current_id]
        
        # Title Input
        st.text_input(
            "Title",
            key="np_title",
            label_visibility="collapsed",
            placeholder="Document Title",
            on_change=save_current_doc,
        )

        # Content Area (auto-saves on every change)
        st.text_area(
            "Content",
            key="np_content",
            height=550,
            label_visibility="collapsed",
            placeholder="Start typing your note here...",
            on_change=save_current_doc,
        )

        word_count = len(st.session_state.np_content.split())
        auto_saved_at = st.session_state.get("nb_saved_at")
        auto_saved_html = (
            f'<span style="color:#2a6e3f;font-weight:600;">Auto-saved · {auto_saved_at}</span>'
            if auto_saved_at else "<span>Auto-save on</span>"
        )
        st.markdown(f"""
            <div class="status-footer">
                <span>{word_count} words</span>
                <span>{auto_saved_html}</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Your notepad is empty. Click '+ New Note' to create one.")


# ------------------------------
# Daily Log Views & Render
# ------------------------------

def render_day_view(selected_date):
    date_str = selected_date.isoformat()
    user_id = _current_user_id()
    logs = _load_log(user_id, date_str)

    cols = st.columns(4, gap="small")
    for idx, col_def in enumerate(COLUMNS):
        col_key = col_def["key"]
        with cols[idx]:
            st.markdown(f"""
                <div class="kanban-header">
                    <span class="label">{col_def['label']}</span>
                </div>
            """, unsafe_allow_html=True)

            current_text = logs.get(col_key, "")

            st.markdown('<div class="dl-log-scroll">', unsafe_allow_html=True)
            new_text = st.text_area(
                f"{col_def['label']} Area",
                value=current_text,
                key=f"dl_area_{date_str}_{col_key}",
                height=300,
                label_visibility="collapsed",
                placeholder=f"Log your {col_def['label'].lower()} tasks here..."
            )
            st.markdown('</div>', unsafe_allow_html=True)

            if new_text != current_text:
                _save_log(user_id, date_str, col_key, new_text)

def render_week_view(selected_date):
    start, end = _date_range("Week", selected_date)
    days = [start + datetime.timedelta(days=i) for i in range(7)]
    
    st.markdown('<div class="view-header">Weekly Planner</div>', unsafe_allow_html=True)
    cols = st.columns(7, gap="small")
    
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"""
                <div class="day-col-header">
                    <div style="font-size: 0.8rem; color: #718096;">{day.strftime('%a').upper()}</div>
                    <div style="font-size: 1.25rem; font-family: 'Bebas Neue', sans-serif; color: #0D1B3E;">{day.strftime('%d')}</div>
                </div>
            """, unsafe_allow_html=True)
            
            date_str = day.isoformat()
            logs = _load_log(_current_user_id(), date_str)
            has_logs = any(logs.values())
            
            if not has_logs:
                st.markdown('<div class="empty-state" style="padding: 1rem 0;">Empty</div>', unsafe_allow_html=True)
            else:
                for col_def in COLUMNS:
                    val = logs.get(col_def["key"], "").strip()
                    if val:
                        st.markdown(f"""
                            <div class="kanban-card" style="font-size: 0.8rem; padding: 0.75rem;">
                                <div style="color: #718096; font-size: 0.7rem; margin-bottom: 0.3rem; font-weight: 600;">{col_def['label'].upper()}</div>
                                <div style="white-space: pre-wrap; color: #333333;">{val}</div>
                            </div>
                        """, unsafe_allow_html=True)

def render_month_view(selected_date):
    start, end = _date_range("Month", selected_date)
    st.markdown('<div class="view-header">Monthly Overview</div>', unsafe_allow_html=True)
    
    month_logs = []
    user_id = _current_user_id()
    for row in fetch_logs_in_range(user_id, start, end):
        try:
            d = datetime.date.fromisoformat(str(row["log_date"][:10]))
        except (ValueError, TypeError):
            continue
        logs = {
            c["key"]: (row.get(c["key"]) or "") for c in COLUMNS
        }
        if any(logs.values()):
            month_logs.append((d, logs))

    month_logs.sort(key=lambda x: x[0], reverse=True)
    
    if not month_logs:
        st.info("No tasks recorded for this month.")
        return

    for d, logs in month_logs:
        st.markdown(f"<div style='font-family: \"Cormorant Garamond\", serif; font-size: 1.3rem; color: #0D1B3E; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem;'>{d.strftime('%A, %b %d')}</div>", unsafe_allow_html=True)
        for col_def in COLUMNS:
            val = logs.get(col_def["key"], "").strip()
            if val:
                st.markdown(f"""
                    <div class="kanban-card" style="display: flex; gap: 1rem; padding: 1rem;">
                        <span style="font-size: 0.85rem; color: #718096; width: 100px; font-weight: 600; flex-shrink: 0;">{col_def['label']}</span>
                        <span style="white-space: pre-wrap; font-size: 0.95rem; color: #333333;">{val}</span>
                    </div>
                """, unsafe_allow_html=True)

def render_dailylog():
    st.markdown('<p class="page-eyebrow">Notebook</p>', unsafe_allow_html=True)
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
# Statistics View
# ------------------------------

def render_statistics():
    st.markdown('<p class="page-eyebrow">Notebook</p>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-title">Daily Log Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Monitor your logging consistency and productivity.</div>', unsafe_allow_html=True)

    # Load the user's persisted daily logs (from last year -> today) per-user.
    user_id = _current_user_id()
    end_date = datetime.date.today()
    start = end_date - datetime.timedelta(days=365)
    valid_dates = []
    for row in fetch_logs_in_range(user_id, start, end_date):
        try:
            d = datetime.date.fromisoformat(str(row["log_date"][:10]))
        except (ValueError, TypeError):
            continue
        logs = {c["key"]: (row.get(c["key"]) or "") for c in COLUMNS}
        valid_dates.append((d, logs))

    if not valid_dates:
        st.info("No valid date records found.")
        return

    dates_only = [x[0] for x in valid_dates]
    start_date = min(dates_only)
    end_date = datetime.date.today()
    
    # Calculate days
    total_days = (end_date - start_date).days + 1
    
    filled_dates = []
    for d, logs in valid_dates:
        if any(v.strip() for v in logs.values()):
            filled_dates.append(d)
            
    missed_dates = []
    for i in range(total_days):
        current = start_date + datetime.timedelta(days=i)
        if current not in filled_dates and current <= end_date:
            missed_dates.append(current)

    filled_count = len(filled_dates)
    missed_count = len(missed_dates)
    completeness = (filled_count / total_days) * 100 if total_days > 0 else 0

    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Days Tracked", total_days)
    col2.metric("Days Logged", filled_count)
    col3.metric("Days Missed", missed_count)
    col4.metric("Completeness", f"{completeness:.1f}%")

    st.markdown("<hr style='border: 0; border-top: 1px solid #d4d0c8; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown('<div class="view-header">Summary Table</div>', unsafe_allow_html=True)
        
        # Build Dataframe for recent logs
        table_data = []
        check_days = min(total_days, 30)
        for i in range(check_days):
            d = end_date - datetime.timedelta(days=i)
            status = "Logged" if d in filled_dates else "Missed"
            table_data.append({"Date": d.strftime("%Y-%m-%d"), "Status": status})
            
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with c2:
        st.markdown('<div class="view-header">Missed Dates</div>', unsafe_allow_html=True)
        if not missed_dates:
            st.success("You have a perfect streak! No missed dates.")
        else:
            missed_dates.sort(reverse=True)
            for md in missed_dates:
                st.markdown(f"""
                    <div class="kanban-card" style="padding: 0.75rem 1rem; color: #e53e3e; font-size: 0.95rem;">
                        <strong>{md.strftime('%A, %b %d, %Y')}</strong>
                    </div>
                """, unsafe_allow_html=True)


# ------------------------------
# Main app
# ------------------------------

def main():
    require_login()
    setup_page_layout()
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    init_session()

    tab_notepad, tab_dailylog, tab_stats = st.tabs(["Notepad", "Daily Log", "Statistics"])
    
    with tab_notepad:
        render_notepad()
    with tab_dailylog:
        render_dailylog()
    with tab_stats:
        render_statistics()

if __name__ == "__main__":
    main()
