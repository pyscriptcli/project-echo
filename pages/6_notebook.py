import sys
import os
import datetime
import uuid
import streamlit as st
import pandas as pd

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
# CSS (UI Matched to Reference)
# ------------------------------
NOTEBOOK_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400;1,600&family=Inter:wght@300;400;500;600&display=swap');

    /* Hide Streamlit default elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Background and typography */
    .stApp {
        background-color: #f4f1ea;
        background-image: linear-gradient(#e5e0d8 1px, transparent 1px), linear-gradient(90deg, #e5e0d8 1px, transparent 1px);
        background-size: 40px 40px;
        font-family: 'Inter', sans-serif;
        color: #333333;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    /* Titles and subtitles */
    .notebook-title {
        font-family: 'Playfair Display', serif;
        font-weight: 400;
        font-style: italic;
        font-size: 2.2rem;
        color: #1a2b4c;
        margin-bottom: 0.25rem;
    }
    .notebook-subtitle {
        font-size: 0.95rem;
        color: #666666;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem;
        border-bottom: 1px solid #d4d0c8;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-weight: 500;
        font-size: 1.1rem;
        color: #666666;
        padding: 0.5rem 0.25rem;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #1a2b4c !important;
        border-bottom: 2px solid #1a2b4c;
    }

    /* Containers */
    .stTextArea textarea, .stTextInput input, .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        color: #333333 !important;
        box-shadow: none !important;
    }
    
    .gallery-container, .kanban-card, div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
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
        font-family: 'Playfair Display', serif;
        font-style: italic;
        font-size: 1.5rem;
        color: #1a2b4c;
        margin-bottom: 1rem;
        border-bottom: 1px solid #d4d0c8;
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
        color: #1a2b4c;
    }
    .empty-state {
        text-align: center;
        color: #a0aec0;
        font-size: 0.85rem;
        padding: 2rem 0;
        font-style: italic;
    }
    .day-col-header {
        text-align: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    /* Button Uniform Styling (Reference Matched) */
    .stButton > button, div[data-testid="stPopover"] > button {
        border-radius: 24px !important;
        font-weight: 500 !important;
        background-color: #111827 !important;
        color: #ffffff !important;
        border: none !important;
        transition: all 0.2s !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        padding: 0.25rem 1rem !important;
        font-size: 0.9rem !important;
    }
    .stButton > button:hover, div[data-testid="stPopover"] > button:hover {
        background-color: #374151 !important;
        color: #ffffff !important;
    }
    
    /* Secondary Note Gallery Buttons override */
    button[kind="secondary"] {
        background-color: transparent !important;
        color: #1a2b4c !important;
        border: 1px solid #cbd5e1 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #f8fafc !important;
        color: #1a2b4c !important;
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
    if "dl_logs" not in st.session_state:
        st.session_state.dl_logs = {}
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
        
        st.markdown("<hr style='margin: 1rem 0; border: 0; border-top: 1px solid #d4d0c8;'>", unsafe_allow_html=True)
        
        filtered_docs = {
            k: v for k, v in st.session_state.nb_docs.items()
            if search_query in v["title"].lower() or search_query in v["content"].lower()
        }
        sorted_docs = sorted(filtered_docs.items(), key=lambda x: x[1]["updated"], reverse=True)
        
        gallery_cont = st.container(height=450, border=False)
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
    start, end = _date_range("Week", selected_date)
    days = [start + datetime.timedelta(days=i) for i in range(7)]
    
    st.markdown('<div class="view-header">Weekly Planner</div>', unsafe_allow_html=True)
    cols = st.columns(7, gap="small")
    
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"""
                <div class="day-col-header">
                    <div style="font-size: 0.8rem; color: #718096;">{day.strftime('%a').upper()}</div>
                    <div style="font-size: 1.1rem; color: #1a2b4c;">{day.strftime('%d')}</div>
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
                            <div class="kanban-card" style="font-size: 0.8rem; padding: 0.75rem;">
                                <div style="color: #718096; font-size: 0.7rem; margin-bottom: 0.3rem; font-weight: 600;">{col_def['label'].upper()}</div>
                                <div style="white-space: pre-wrap; color: #333333;">{val}</div>
                            </div>
                        """, unsafe_allow_html=True)

def render_month_view(selected_date):
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
        st.markdown(f"<div style='font-family: \"Playfair Display\", serif; font-size: 1.1rem; color: #1a2b4c; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem;'>{d.strftime('%A, %b %d')}</div>", unsafe_allow_html=True)
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
    st.markdown('<div class="notebook-title">Daily Log Statistics</div>', unsafe_allow_html=True)
    st.markdown('<div class="notebook-subtitle">Monitor your logging consistency and productivity.</div>', unsafe_allow_html=True)

    if not st.session_state.dl_logs:
        st.info("No logs available to generate statistics.")
        return

    # Parse all logged dates
    valid_dates = []
    for d_str, logs in st.session_state.dl_logs.items():
        try:
            d = datetime.date.fromisoformat(d_str)
            valid_dates.append((d, logs))
        except:
            continue
            
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
        # show last 30 days or total days
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
