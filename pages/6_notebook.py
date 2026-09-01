# pages/6_notebook.py
# -*- coding: utf-8 -*-
"""Project Echo - Notebook
Two-tab page: Notepad (document editor) and Daily Log (Kanban task board)."""

import sys, os, datetime, uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from components.sidebar import setup_page_layout

# ── CSS ───────────────────────────────────────────────────────────────
NOTEBOOK_CSS = '''
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap");
header[data-testid="stHeader"], .stApp > header, [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu, footer {
    display: none !important; visibility: hidden !important; height: 0 !important; width: 0 !important;
}
.stApp { background-color: #F3EFE6 !important; }
.stTabs [data-baseweb="tab-list"] {
    gap: 0 !important; border-bottom: 1px solid rgba(26,43,76,0.12) !important; margin-bottom: 1rem !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: "Playfair Display", serif !important;
    font-style: italic !important; font-size: 1.1rem !important; font-weight: 600 !important;
    color: #6C727A !important; padding: 0.5rem 1rem !important;
    border: none !important; background: transparent !important;
}
.stTabs [aria-selected="true"] { color: #1A2B4C !important; border-bottom: 2px solid #D4AF37 !important; }
h1.nb-title {
    font-family: "Playfair Display", serif !important; font-style: italic !important;
    font-weight: 600 !important; color: #1A2B4C !important; font-size: 1.8rem !important; margin: 0 0 0.2rem 0 !important;
}
.nb-subtitle { font-size: 0.8rem; color: #6C727A; margin: 0 0 1rem 0; }

/* Kanban column */
.nb-col {
    background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06); border-radius: 6px;
    padding: 10px; min-height: 200px;
}
.nb-col-header {
    display: flex; align-items: center; gap: 6px; padding-bottom: 8px; margin-bottom: 8px;
    border-bottom: 2px solid #D4AF37; font-family: "Playfair Display", serif;
    font-style: italic; font-size: 0.9rem; font-weight: 600; color: #1A2B4C;
}
.nb-col-header svg { flex-shrink: 0; }
.nb-col-count {
    font-size: 0.65rem; font-weight: 600; color: #6C727A; background: #F5F4F0;
    border-radius: 10px; padding: 1px 8px; margin-left: auto;
}

/* Task card */
.nb-card {
    background: #FAFAFA; border: 1px solid rgba(0,0,0,0.05); border-radius: 6px;
    padding: 10px; margin-bottom: 8px;
}
.nb-card textarea {
    font-family: "Inter", sans-serif !important; font-size: 0.82rem !important;
    line-height: 1.45 !important; border: none !important; background: transparent !important;
    resize: vertical !important; min-height: 60px !important; padding: 0 !important;
    color: #1A2B4C !important;
}
.nb-card textarea:focus { outline: none !important; box-shadow: none !important; }
.nb-card-meta {
    display: flex; align-items: center; gap: 6px; font-size: 0.65rem;
    color: #8B949E; margin-top: 6px; padding-top: 6px;
    border-top: 1px solid rgba(0,0,0,0.04);
}
.nb-empty {
    text-align: center; padding: 30px 10px; color: #B0B4B9;
    font-size: 0.78rem; font-style: italic;
}
</style>
'''

# ── SVG ICONS (small inline, for column headers only) ──────────────────
SVG = {
    "client":  '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L12 11m8-4v10m0 0l-8-4v-10"/></svg>',
    "admin":   '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="12" y2="17"/></svg>',
    "adhoc":   '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    "meeting": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>',
}

# ── COLUMN CONFIG ──────────────────────────────────────────────────────
COLUMNS = [
    {"key": "client",  "label": "Client Related Tasks", "color": "#3B82F6"},
    {"key": "admin",   "label": "Admin Tasks",          "color": "#10B981"},
    {"key": "adhoc",   "label": "Adhoc Tasks",          "color": "#F59E0B"},
    {"key": "meeting", "label": "Meetings",             "color": "#8B5CF6"},
]

# ── SESSION STATE INIT ─────────────────────────────────────────────────
def init_session():
    defaults = {
        "nb_content": "", "nb_title": "Untitled.txt",
        "dl_date": datetime.date.today(), "dl_view": "Day",
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v
    for col in COLUMNS:
        if f"dl_{col['key']}" not in st.session_state:
            st.session_state[f"dl_{col['key']}"] = []

def _make_id():
    return uuid.uuid4().hex[:8]

def _date_range(view, date):
    if view == "Day":   return date, date
    if view == "Week":  s = date - datetime.timedelta(days=date.weekday()); return s, s + datetime.timedelta(days=6)
    s = date.replace(day=1); import calendar; _, l = calendar.monthrange(date.year, date.month)
    return s, date.replace(day=l)

# ── NOTEPAD TAB ────────────────────────────────────────────────────────
def render_notepad():
    st.markdown('<h1 class="nb-title">Notepad</h1>', unsafe_allow_html=True)
    st.markdown('<p class="nb-subtitle">Create, edit, and save text documents.</p>', unsafe_allow_html=True)
    init_session()

    # Toolbar row
    t1, t2, t3, t4, t5, t6 = st.columns([1, 1, 1, 1, 2.5, 0.8])
    with t1:
        if st.button("New", icon=":material/note_add:", key="np_new", use_container_width=True):
            st.session_state.nb_content = ""; st.session_state.nb_title = "Untitled.txt"; st.rerun()
    with t2:
        if st.button("Open", icon=":material/folder_open:", key="np_open", use_container_width=True):
            pass
    with t3:
        if st.button("Save", icon=":material/save:", key="np_save", use_container_width=True):
            st.toast("Document saved", icon=":material/check_circle:")
    with t4:
        if st.button("Save As", icon=":material/save_as:", key="np_saveas", use_container_width=True):
            pass
    with t5:
        st.text_input("doc", value=st.session_state.nb_title, key="np_title_in", label_visibility="collapsed")
    with t6:
        if st.button(" ", icon=":material/delete:", key="np_del", use_container_width=True, help="Clear document"):
            st.session_state.nb_content = ""; st.session_state.nb_title = "Untitled.txt"; st.rerun()
    st.session_state.nb_title = st.session_state.np_title_in

    # Formatting row
    fb = st.columns(7)
    with fb[0]: st.button(label="B", icon=":material/format_bold:", key="fmtb", help="Bold")
    with fb[1]: st.button(label="I", icon=":material/format_italic:", key="fmti", help="Italic")
    with fb[2]: st.button(label="U", icon=":material/format_underlined:", key="fmtu", help="Underline")
    with fb[3]: st.button(label="List", icon=":material/format_list_bulleted:", key="fmtl", help="Bullet list")
    with fb[4]: st.button(label="List", icon=":material/format_list_numbered:", key="fmtn", help="Numbered list")
    with fb[5]: st.caption(f"Words: {len(st.session_state.get('nb_content','').split())}")
    with fb[6]: st.caption("Auto-save: On")

    # Editor
    st.session_state.nb_content = st.text_area(
        "editor", value=st.session_state.nb_content, height=480,
        key="np_editor", label_visibility="collapsed",
        placeholder="Start typing...  Use - or * for bullet lists"
    )

    # Edit controls
    eb = st.columns(6)
    with eb[0]: st.button("Undo", icon=":material/undo:", key="np_undo", use_container_width=True)
    with eb[1]: st.button("Redo", icon=":material/redo:", key="np_redo", use_container_width=True)
    with eb[2]: st.button("Cut",  icon=":material/content_cut:",  key="np_cut",  use_container_width=True)
    with eb[3]: st.button("Copy", icon=":material/content_copy:", key="np_copy", use_container_width=True)
    with eb[4]: st.button("Paste", icon=":material/content_paste:", key="np_paste", use_container_width=True)
    with eb[5]: st.caption(f"Chars: {len(st.session_state.get('nb_content',''))}")

# ── DAILY LOG TAB ─────────────────────────────────────────────────────
def render_dailylog():
    st.markdown('<h1 class="nb-title">Daily Log</h1>', unsafe_allow_html=True)
    st.markdown('<p class="nb-subtitle">Track tasks across categories with day/week/month filters.</p>', unsafe_allow_html=True)
    init_session()

    # Filter bar
    f1, f2, f3, f4, f5 = st.columns([2, 2, 1, 1, 2])
    with f1: st.date_input("Date", key="dl_date", label_visibility="collapsed")
    with f2: st.segmented_control("View", ["Day","Week","Month"], key="dl_view", label_visibility="collapsed")
    with f3:
        if st.button("Task", icon=":material/add_task:", key="dl_task_btn", use_container_width=True):
            st.session_state.dl_dlg = "task"
    with f4:
        if st.button("Meet", icon=":material/event_available:", key="dl_meet_btn", use_container_width=True):
            st.session_state.dl_dlg = "meeting"
    with f5: st.text_input("Search", placeholder="Search...", label_visibility="collapsed", key="dl_search")

    dr = _date_range(st.session_state.dl_view, st.session_state.dl_date)
    st.caption(f"Showing: {dr[0].strftime('%b %d')} - {dr[1].strftime('%b %d, %Y')}")

    # ── Add Task Dialog ──
    if st.session_state.get("dl_dlg") == "task":
        with st.expander("New Task", expanded=True):
            cat = st.selectbox("Category", [c["key"] for c in COLUMNS],
                               format_func=lambda x: next(c["label"] for c in COLUMNS if c["key"]==x),
                               key="dl_new_cat")
            text = st.text_area("Content", placeholder="- First item\n- Second item", key="dl_new_text", height=100)
            if st.button("Add Task", type="primary", key="dl_add_task_ok", use_container_width=True):
                if text.strip():
                    st.session_state[f"dl_{cat}"].append({
                        "id": _make_id(), "content": text, "created": datetime.date.today().isoformat()
                    })
                    st.session_state.dl_dlg = None
                    st.rerun()

    # ── Add Meeting Dialog ──
    if st.session_state.get("dl_dlg") == "meeting":
        with st.expander("New Meeting", expanded=True):
            mt = st.text_input("Title", key="dl_meet_title")
            md = st.text_area("Notes", placeholder="- Agenda item", key="dl_meet_note", height=80)
            if st.button("Add Meeting", type="primary", key="dl_add_meet_ok", use_container_width=True):
                text = f"**{mt}**\n\n{md}" if md else f"**{mt}**"
                if mt.strip():
                    st.session_state["dl_meeting"].append({
                        "id": _make_id(), "content": text, "created": datetime.date.today().isoformat()
                    })
                    st.session_state.dl_dlg = None
                    st.rerun()

    # ── KANBAN BOARD ──
    cols = st.columns(4, gap="small")
    for i, col_cfg in enumerate(COLUMNS):
        k = col_cfg["key"]
        svg = SVG.get(k, "")
        with cols[i]:
            # Header
            st.markdown(
                f'<div class="nb-col-header" style="border-bottom-color:{col_cfg["color"]};">'
                f'{svg} <span>{col_cfg["label"]}</span>'
                f'<span class="nb-col-count">{len(st.session_state.get(f"dl_{k}",[]))}</span></div>',
                unsafe_allow_html=True
            )
            # Tasks
            tasks = st.session_state.get(f"dl_{k}", [])
            search = st.session_state.get("dl_search", "").strip().lower()
            if not tasks:
                st.markdown('<div class="nb-empty">No entries</div>', unsafe_allow_html=True)
            for j, task in enumerate(tasks):
                if search and search not in task["content"].lower():
                    continue
                cid = task["id"]
                st.markdown('<div class="nb-card">', unsafe_allow_html=True)
                task["content"] = st.text_area(
                    f"t_{k}_{j}", value=task["content"],
                    key=f"dl_t_{cid}", label_visibility="collapsed", height=80
                )
                meta = st.columns([1.5, 1, 0.6])
                with meta[0]: st.caption(task.get("created", "")[:10])
                with meta[1]: st.caption(col_cfg["label"])
                with meta[2]:
                    if st.button(" ", icon=":material/delete:", key=f"dl_del_{cid}", help="Delete"):
                        st.session_state[f"dl_{k}"].remove(task)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            # Add button
            if st.button("Add", icon=":material/add:", key=f"dl_add_{k}", use_container_width=True):
                st.session_state.dl_new_cat = k
                st.session_state.dl_dlg = "task"
                st.rerun()

# ── MAIN PAGE ─────────────────────────────────────────────────────────
st.set_page_config(page_title="Project Echo - Notebook", layout="wide", initial_sidebar_state="expanded")
setup_page_layout()
st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
t1, t2 = st.tabs(["Notepad", "Daily Log"])
with t1: render_notepad()
with t2: render_dailylog()
