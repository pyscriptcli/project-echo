import sys
import os
import datetime
import uuid
import streamlit as st

# Add project root to sys.path to allow imports from components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.sidebar import setup_page_layout
from utils.auth import require_login

# ------------------------------
# Page configuration
# ------------------------------
st.set_page_config(
    page_title="Project Echo - Notebook",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------
# CSS (Native Echo look: Playfair + Inter, navy/gold on light)
# ------------------------------
NOTEBOOK_CSS = """
<style>
    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {
        background-color: #F5F1E8;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1A2B4C;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Titles and subtitles */
    .notebook-title {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 2.2rem;
        color: #1A2B4C;
        margin-bottom: 0.25rem;
        letter-spacing: 0.01em;
    }
    .notebook-subtitle {
        font-size: 0.95rem;
        color: #6C727A;
        margin-bottom: 2rem;
        border-bottom: 1px solid rgba(26, 43, 76, 0.1);
        padding-bottom: 1rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid rgba(26, 43, 76, 0.1);
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 1rem;
        color: #6C727A;
        padding: 0.5rem 0.25rem;
    }
    .stTabs [aria-selected="true"] {
        color: #1A2B4C !important;
        border-bottom: 2px solid #D4AF37;
    }

    /* Text Areas (Notepad & Daily Log) */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        border: 1px solid rgba(26, 43, 76, 0.12) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        color: #1A2B4C !important;
        padding: 1rem !important;
        box-shadow: none !important;
        line-height: 1.5 !important;
    }
    .stTextArea textarea:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 2px rgba(212, 175, 55, 0.15) !important;
    }

    .status-footer {
        display: flex;
        justify-content: space-between;
        color: #6C727A;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }

    /* Kanban & Views */
    .view-header {
        font-weight: 600;
        margin-bottom: 1rem;
        color: #1A2B4C;
        border-bottom: 1px solid rgba(26, 43, 76, 0.1);
        padding-bottom: 0.5rem;
    }
    .kanban-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .kanban-header .label {
        font-weight: 600;
        font-size: 0.95rem;
        color: #1A2B4C;
    }
    .kanban-card {
        background-color: #FFFFFF;
        border: 1px solid rgba(26, 43, 76, 0.1);
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 2px 6px rgba(26, 43, 76, 0.06);
        font-size: 0.9rem;
        line-height: 1.4;
        color: #1A2B4C;
    }
    .empty-state {
        text-align: center;
        color: #8B94A0;
        font-size: 0.85rem;
        padding: 2rem 0;
    }
    .day-col-header {
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        color: #1A2B4C;
    }

    /* Buttons — deep charcoal, gold accent, rounded, drop shadow */
    .stButton > button, div[data-testid="stPopover"] > button {
        border-radius: 18px;
        font-weight: 600;
        background-color: #111A2B;
        color: #FFFFFF;
        border: 1px solid #D4AF37;
        transition: all 0.2s;
        min-height: 36px !important;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 0.25rem 0.6rem;
        font-size: 0.9rem;
        box-shadow: 0 4px 10px rgba(26, 43, 76, 0.18);
    }
    .stButton > button:hover, div[data-testid="stPopover"] > button:hover {
        background-color: #1A2B4C;
        border-color: #E6C44D;
        color: #FFFFFF;
        box-shadow: 0 6px 14px rgba(212, 175, 55, 0.25);
    }

    /* Primary button override */
    .stButton > button[kind="primary"] {
        background-color: #111A2B;
        color: #F5F1E8;
        border: 1px solid #D4AF37;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1A2B4C;
        border-color: #E6C44D;
        color: #F5F1E8;
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

    # Daily Log init - replaced individual cards with a dictionary of texts per date
    if "dl_logs" not in st.session_state:
        st.session_state.dl_logs = {}

        # Populate a sample log for today
        today_str = datetime.date.today().isoformat()
        st.session_state.dl_logs[today_str] = {
            "client": "- Prep quarterly report\n- Send email update to Client A",
            "admin": "- Update internal docs",
            "adhoc": "",
            "meeting": "- Sync at 3 PM\n- Discuss Q4 goals"
        }

    if "dl_date" not in st.session_state:
        st.session_state.dl_date = datetime.date.today()
    if "dl_view" not in st.session_state:
        st.session_state.dl_view = "Day"

# ------------------------------
# Notepad Logic
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

def delete_current_doc():
    cid = st.session_state.nb_current_id
    if cid and cid in st.session_state.nb_docs:
        del st.session_state.nb_docs[cid]
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

def render_notepad():
    st.markdown('<div class="notebook-title">Notepad</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">A minimal environment for your thoughts.</div>', unsafe_allow_html=True)

    col_gallery, col_editor = st.columns([1, 2.5], gap="large")

    with col_gallery:
        st.button("+ New Note", on_click=create_new_doc, use_container_width=True)
        search_query = st.text_input("Search", placeholder="Search notes...", label_visibility="collapsed").lower()

        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)

        filtered_docs = {
            k: v for k, v in st.session_state.nb_docs.items()
            if search_query in v["title"].lower() or search_query in v["content"].lower()
        }
        sorted_docs = sorted(filtered_docs.items(), key=lambda x: x[1]["updated"], reverse=True)

        gallery_cont = st.container(height=450)
        with gallery_cont:
            if not sorted_docs:
                st.markdown("<div class='empty-state'>No notes found</div>", unsafe_allow_html=True)
            for doc_id, doc in sorted_docs:
                title = doc["title"] if doc["title"].strip() else "Untitled"
                date_str = datetime.datetime.fromisoformat(doc["updated"]).strftime("%b %d")

                is_active = (doc_id == st.session_state.nb_current_id)
                btn_type = "primary" if is_active else "secondary"

                st.button(
                    f"{title} ({date_str})",
                    key=f"sel_{doc_id}",
                    on_click=select_doc,
                    args=(doc_id,),
                    use_container_width=True,
                    type=btn_type
                )

    with col_editor:
        has_docs = bool(st.session_state.nb_docs)
        if has_docs and st.session_state.nb_current_id in st.session_state.nb_docs:
            doc_meta = st.session_state.nb_docs[st.session_state.nb_current_id]

            e_col1, e_col2, e_col3 = st.columns([6, 1, 1])
            with e_col2:
                st.button("Delete", on_click=delete_current_doc, use_container_width=True)
            with e_col3:
                st.button("Save", on_click=save_current_doc, use_container_width=True)

            st.text_input("Title", key="np_title", label_visibility="collapsed", placeholder="Document Title")

            st.text_area(
                "Content",
                key="np_content",
                height=400,
                label_visibility="collapsed",
                placeholder="Start typing..."
            )

            word_count = len(st.session_state.np_content.split())
            updated_str = _format_date(datetime.datetime.fromisoformat(doc_meta["updated"]))

            st.markdown(f"""
                <div class="status-footer">
                    <span>{word_count} words</span>
                    <span>Last saved: {updated_str}</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Select a note from the gallery or create a new one.")


# ------------------------------
# Daily Log Views & Render
# ------------------------------

def render_day_view(selected_date):
    """Day view with a single long text box per column for continuous logging."""
    date_str = selected_date.isoformat()

    if date_str not in st.session_state.dl_logs:
        st.session_state.dl_logs[date_str] = {c["key"]: "" for c in COLUMNS}

    cols = st.columns(4, gap="small")
    for idx, col_def in enumerate(COLUMNS):
        col_key = col_def["key"]
        with cols[idx]:
            st.markdown(f"""
                <div class="kanban-header">
                    <span class="label">{col_def['label']}</span>
                </div>
            """, unsafe_allow_html=True)

            current_text = st.session_state.dl_logs[date_str].get(col_key, "")

            new_text = st.text_area(
                f"{col_def['label']} Area",
                value=current_text,
                key=f"dl_area_{date_str}_{col_key}",
                height=500,
                label_visibility="collapsed",
                placeholder=f"Log your {col_def['label'].lower()} tasks here..."
            )

            if new_text != current_text:
                st.session_state.dl_logs[date_str][col_key] = new_text

def render_week_view(selected_date):
    """Weekly board showing summaries of the daily logs."""
    start, end = _date_range("Week", selected_date)
    days = [start + datetime.timedelta(days=i) for i in range(7)]

    st.markdown('<div class="view-header">Weekly Planner</div>', unsafe_allow_html=True)
    cols = st.columns(7, gap="small")

    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"""
                <div class="day-col-header">
                    <div style="font-size: 0.8rem; color: #6C727A;">{day.strftime('%a').upper()}</div>
                    <div style="font-size: 1.1rem; color: #1A2B4C;">{day.strftime('%d')}</div>
                </div>
            """, unsafe_allow_html=True)

            date_str = day.isoformat()
            logs = st.session_state.dl_logs.get(date_str, {})
            has_logs = any(logs.values())

            if not has_logs:
                st.markdown('<div class="empty-state" style="padding: 1rem 0;">Empty</div>', unsafe_allow_html=True)
            else:
                for col_def in COLUMNS:
                    val = logs.get(col_def["key"], "").strip()
                    if val:
                        st.markdown(f"""
                            <div class="kanban-card" style="font-size: 0.8rem; padding: 0.5rem;">
                                <div style="color: #6C727A; font-size: 0.65rem; margin-bottom: 0.2rem; font-weight: 600;">{col_def['label'].upper()}</div>
                                <div style="white-space: pre-wrap;">{val}</div>
                            </div>
                        """, unsafe_allow_html=True)

def render_month_view(selected_date):
    """Monthly list view showing all logs for the current month."""
    start, end = _date_range("Month", selected_date)
    st.markdown('<div class="view-header">Monthly Overview</div>', unsafe_allow_html=True)

    month_logs = []
    for date_str, logs in st.session_state.dl_logs.items():
        try:
            d = datetime.date.fromisoformat(date_str)
        except:
            continue
        if start <= d <= end and any(logs.values()):
            month_logs.append((d, logs))

    month_logs.sort(key=lambda x: x[0], reverse=True)

    if not month_logs:
        st.info("No tasks recorded for this month.")
        return

    for d, logs in month_logs:
        st.markdown(f"<div style='font-weight: 600; margin-top: 1rem; margin-bottom: 0.5rem; color:#1A2B4C;'>{d.strftime('%A, %b %d')}</div>", unsafe_allow_html=True)
        for col_def in COLUMNS:
            val = logs.get(col_def["key"], "").strip()
            if val:
                st.markdown(f"""
                    <div class="kanban-card" style="display: flex; gap: 1rem; padding: 0.75rem 1rem;">
                        <span style="font-size: 0.85rem; color: #6C727A; width: 100px; font-weight: 600; flex-shrink: 0;">{col_def['label']}</span>
                        <span style="white-space: pre-wrap; font-size: 0.9rem;">{val}</span>
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
    require_login()
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
