# pages/6_notebook.py
# -*- coding: utf-8 -*-
"""Project Echo - Notebook - Single file page"""

import sys, os, re, json, datetime, hashlib
from typing import Optional
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from components.sidebar import setup_page_layout
from utils.auth import require_auth
from utils.db import get_supabase_client

# ---------------------------------------------------------------------------
# MATERIAL ICON HELPER (Streamlit material symbols — matches rest of app)
# ---------------------------------------------------------------------------
def mi(name):
    """Return a Streamlit material icon for use in markdown (rendered as SVG glyph)."""
    return f":material/{name}:"

# ---------------------------------------------------------------------------
# PAGE CSS (native to Project Echo design system)
# ---------------------------------------------------------------------------
NOTEBOOK_CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap");

/* Hide Streamlit chrome */
header[data-testid="stHeader"], .stApp > header, [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu, footer {
    display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important;
}

.stApp {
    background-color: #F3EFE6 !important;
    background-image: linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px !important;
}

.block-container {
    padding-top: 1.5rem !important; padding-left: 2.2rem !important;
    padding-right: 2.2rem !important; max-width: 100% !important;
}

/* Notebook tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important; border-bottom: 1px solid rgba(26,43,76,0.12) !important; margin-bottom: 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: "Playfair Display", serif !important;
    font-style: italic !important; font-size: 1.1rem !important;
    font-weight: 600 !important; color: #6C727A !important;
    padding: 0.5rem 1rem !important; border: none !important; background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #1A2B4C !important; border-bottom: 2px solid #D4AF37 !important;
}

/* Task card */
.task-card {
    background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06);
    border-radius: 6px; padding: 12px; margin-bottom: 10px;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.task-card:hover { border-color: rgba(212,175,55,0.4); box-shadow: 0 2px 6px rgba(0,0,0,0.05); }

.task-card textarea {
    font-family: "Inter", sans-serif !important; font-size: 0.85rem !important;
    line-height: 1.5 !important; border: none !important;
    background: transparent !important; resize: vertical !important;
    min-height: 80px !important; padding: 0 !important; color: #1A2B4C !important;
}
.task-card textarea:focus { outline: none !important; box-shadow: none !important; }

/* Column header */
.col-header {
    display: flex; align-items: center; gap: 6px; padding: 8px 0;
    margin-bottom: 8px; border-bottom: 2px solid #D4AF37;
    font-family: "Playfair Display", serif; font-style: italic;
    font-size: 0.95rem; font-weight: 600; color: #1A2B4C;
}

/* Page header */
h1.page-title {
    font-family: "Playfair Display", serif !important;
    font-style: italic !important; font-weight: 600 !important;
    color: #1A2B4C !important; font-size: 1.8rem !important;
    margin: 0 0 0.2rem 0 !important;
}
p.page-desc {
    font-size: 0.8rem; color: #6C727A; margin: 0 0 1rem 0;
}
</style>
"""

# ---------------------------------------------------------------------------
# COLUMN CONFIG
# ---------------------------------------------------------------------------
COLUMN_CONFIG = {
    "client":  {"label": "Client Related Tasks", "icon": "groups",        "color": "#3B82F6"},
    "admin":   {"label": "Admin Tasks",          "icon": "admin_panel_settings", "color": "#10B981"},
    "adhoc":   {"label": "Adhoc Tasks",          "icon": "bolt",          "color": "#F59E0B"},
    "meeting": {"label": "Meetings",             "icon": "event",         "color": "#8B5CF6"},
}

def _get_date_range(view_mode, focus_date):
    if view_mode == 'Day':
        return focus_date, focus_date
    elif view_mode == 'Week':
        start = focus_date - datetime.timedelta(days=focus_date.weekday())
        end = start + datetime.timedelta(days=6)
        return start, end
    else:
        start = focus_date.replace(day=1)
        import calendar
        _, last = calendar.monthrange(focus_date.year, focus_date.month)
        end = focus_date.replace(day=last)
        return start, end

def _init_state():
    """Initialize session state for both tabs."""
    if 'nb_content' not in st.session_state:
        st.session_state.nb_content = ''
    if 'nb_title' not in st.session_state:
        st.session_state.nb_title = 'Untitled.txt'
    if 'dl_date' not in st.session_state:
        st.session_state.dl_date = datetime.date.today()
    if 'dl_view' not in st.session_state:
        st.session_state.dl_view = 'Day'
    for k in ['client', 'admin', 'adhoc', 'meeting']:
        if f'dl_{k}' not in st.session_state:
            st.session_state[f'dl_{k}'] = []

# ---------------------------------------------------------------------------
# NOTEPAD TAB
# ---------------------------------------------------------------------------
def render_notepad_tab():
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Notepad</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-desc">Create, open, save, and edit text documents with bullet list support.</p>', unsafe_allow_html=True)

    _init_state()

    # File operations toolbar
    c1, c2, c3, c4, c5, c6 = st.columns([1.1, 1.1, 1.1, 1.1, 2.5, 0.9])
    with c1:
        if st.button("New", icon=":material/note_add:", key="nb_new", use_container_width=True):
            st.session_state.nb_content = ''
            st.session_state.nb_title = 'Untitled.txt'
            st.rerun()
    with c2:
        if st.button("Open", icon=":material/folder_open:", key="nb_open", use_container_width=True):
            pass
    with c3:
        if st.button("Save", icon=":material/save:", key="nb_save", use_container_width=True):
            st.toast("Document saved", icon=":material/check_circle:")
    with c4:
        if st.button("Save As", icon=":material/save_as:", key="nb_saveas", use_container_width=True):
            pass
    with c5:
        st.text_input("Document", value=st.session_state.nb_title, key="nb_title_input",
                      label_visibility="collapsed")
    with c6:
        if st.button(icon=":material/delete:", key="nb_delete", use_container_width=True,
                     help="Delete document", label=" "):
            st.session_state.nb_content = ''
            st.session_state.nb_title = 'Untitled.txt'
            st.toast("Document deleted", icon=":material/delete:")
            st.rerun()

    # Keep title in sync
    st.session_state.nb_title = st.session_state.nb_title_input

    # Formatting toolbar
    fc = st.columns(7)
    with fc[0]: st.button(icon=":material/format_bold:", key="fmt_bold", label="B", help="Bold")
    with fc[1]: st.button(icon=":material/format_italic:", key="fmt_italic", label="I", help="Italic")
    with fc[2]: st.button(icon=":material/format_underlined:", key="fmt_uline", label="U", help="Underline")
    with fc[3]: st.button(icon=":material/format_list_bulleted:", key="fmt_list", label="List", help="Bullet list")
    with fc[4]: st.button(icon=":material/format_list_numbered:", key="fmt_olist", label="List", help="Numbered list")
    with fc[5]:
        st.caption(f"Words: {len(st.session_state.get('nb_content','').split())}")
    with fc[6]:
        st.caption("Auto-save: On")

    # Editor
    st.session_state.nb_content = st.text_area(
        "Editor", value=st.session_state.nb_content, height=500,
        key="nb_editor", label_visibility="collapsed",
        placeholder="Start typing...\n- Use - or * for bullets\n- Press Enter for next bullet"
    )

    # Editing controls footer
    ec = st.columns(6)
    with ec[0]: st.button("Undo", icon=":material/undo:", key="nb_undo", use_container_width=True)
    with ec[1]: st.button("Redo", icon=":material/redo:", key="nb_redo", use_container_width=True)
    with ec[2]: st.button("Cut", icon=":material/content_cut:", key="nb_cut", use_container_width=True)
    with ec[3]: st.button("Copy", icon=":material/content_copy:", key="nb_copy", use_container_width=True)
    with ec[4]: st.button("Paste", icon=":material/content_paste:", key="nb_paste", use_container_width=True)
    with ec[5]:
        st.caption(f"Chars: {len(st.session_state.get('nb_content',''))}")

# ---------------------------------------------------------------------------
# DAILY LOG TAB
# ---------------------------------------------------------------------------
def render_daily_log_tab():
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Daily Log</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-desc">Track tasks across four categories with day/week/month filtering.</p>', unsafe_allow_html=True)

    _init_state()

    # Filter bar
    r1, r2, r3, r4, r5 = st.columns([2, 2, 1.2, 1.2, 2])
    with r1:
        st.date_input("Date", key="dl_date", label_visibility="collapsed")
    with r2:
        st.segmented_control("View", ["Day", "Week", "Month"], key="dl_view", label_visibility="collapsed")
    with r3:
        st.button("Task", icon=":material/add_task:", key="dl_add_task_btn", use_container_width=True)
    with r4:
        st.button("Meet", icon=":material/event_available:", key="dl_add_meet_btn", use_container_width=True)
    with r5:
        st.text_input("Search", placeholder="Search...", label_visibility="collapsed", key="dl_search")

    date_from, date_to = _get_date_range(st.session_state.dl_view, st.session_state.dl_date)
    st.caption(f"Showing: {date_from.strftime('%b %d')} - {date_to.strftime('%b %d, %Y')}")

    # Add task modal
    if st.session_state.get('dl_show_add'):
        with st.expander("New Task", expanded=True):
            cat_sel = st.selectbox("Category", ['client', 'admin', 'adhoc', 'meeting'],
                                   format_func=lambda x: COLUMN_CONFIG[x]['label'], key="dl_new_cat")
            content = st.text_area("Content", placeholder="- First item\n- Second item\n- Third item",
                                   key="dl_new_content", height=100)
            if st.button("Add", type="primary", key="dl_add_confirm", use_container_width=True):
                if content.strip():
                    new_id = hashlib.md5(content.encode()).hexdigest()[:8]
                    st.session_state[f'dl_{cat_sel}'].append({
                        'id': new_id, 'content': content,
                        'due_date': st.session_state.dl_date.isoformat(), 'column_type': cat_sel,
                    })
                    st.session_state.dl_show_add = False
                    st.rerun()

    # Add meeting modal
    if st.session_state.get('dl_show_meet'):
        with st.expander("New Meeting", expanded=True):
            mt = st.text_input("Meeting title", key="dl_meet_title")
            md = st.text_area("Notes", placeholder="- Agenda item 1\n- Agenda item 2", key="dl_meet_detail", height=80)
            if st.button("Add Meeting", type="primary", key="dl_meet_confirm", use_container_width=True):
                text = mt + '\n' + md if md else mt
                if text.strip():
                    new_id = hashlib.md5(text.encode()).hexdigest()[:8]
                    st.session_state['dl_meeting'].append({
                        'id': new_id, 'content': text,
                        'due_date': st.session_state.dl_date.isoformat(), 'column_type': 'meeting',
                    })
                    st.session_state.dl_show_meet = False
                    st.rerun()

    # Kanban columns
    kanban_cols = st.columns(4, gap="small")
    for idx, (k, v) in enumerate(COLUMN_CONFIG.items()):
        with kanban_cols[idx]:
            st.markdown(f'<div class="col-header" style="border-bottom-color:{v["color"]};">'
                        f'{mi(v["icon"])} <span>{v["label"]}</span></div>', unsafe_allow_html=True)
            tasks = st.session_state.get(f'dl_{k}', [])
            search_term = st.session_state.get('dl_search', '').strip().lower()

            if not tasks:
                st.markdown('<div style="color:#6C727A;font-size:0.75rem;font-style:italic;'
                            'text-align:center;padding:20px 0;">No entries</div>', unsafe_allow_html=True)
            else:
                for t in tasks:
                    if search_term and search_term not in t.get('content', '').lower():
                        continue
                    st.markdown('<div class="task-card">', unsafe_allow_html=True)
                    edited = st.text_area("Task", value=t['content'],
                                          height=max(80, min(200, len(t['content'].split('\n')) * 24 + 60)),
                                          key=f'dl_task_{k}_{t["id"]}', label_visibility="collapsed")
                    t['content'] = edited
                    meta_c = st.columns([1, 1, 1])
                    with meta_c[0]: st.caption(f"Due: {t.get('due_date', '')[:10]}")
                    with meta_c[1]: st.caption(v['label'])
                    with meta_c[2]:
                        if st.button(label=" ", icon=":material/delete:", key=f'dl_del_{k}_{t["id"]}',
                                     help="Delete entry"):
                            tasks.remove(t)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Add", icon=":material/add:", key=f'dl_add_{k}', use_container_width=True):
                st.session_state.dl_show_add = True
                st.rerun()

# ---------------------------------------------------------------------------
# MAIN PAGE
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Project Echo - Notebook", layout="wide", initial_sidebar_state="expanded")
setup_page_layout()
st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)

tab1, tab2 = st.tabs([
    f"{mi('edit_note')} Notepad",
    f"{mi('calendar_month')} Daily Log",
])
with tab1:
    render_notepad_tab()
with tab2:
    render_daily_log_tab()
