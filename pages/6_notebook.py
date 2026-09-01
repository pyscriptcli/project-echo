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
# SVG ICON REGISTRY (unchanged, all SVGs are valid)
# ---------------------------------------------------------------------------
NOTEBOOK_ICONS = {
    "new": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5l-3 3m0 0l-3-3m3 3V2M4 9v2a3 3 0 003 3h2"/><path d="M4 14v2a2 2 0 002 2h8a2 2 0 002-2v-2"/></svg>""",
    "open": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 012-2h4l2 2h4a2 2 0 012 2v2"/><path d="M3 7v7a2 2 0 002 2h10a2 2 0 002-2V7"/><path d="M3 7h14"/></svg>""",
    "save": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3H5a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V4l-2-2"/><path d="M14 3v4H7V3"/><path d="M7 13h6"/><path d="M7 10h6"/></svg>""",
    "save-as": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3H5a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2V4l-2-2"/><path d="M14 3v4H7V3"/><path d="M10 10v5"/><path d="M8 13l2 2 2-2"/></svg>""",
    "undo": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/></svg>""",
    "redo": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="19 4 19 10 13 10"/><path d="M16.49 15a9 9 0 11-2.13-9.36L19 10"/></svg>""",
    "cut": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="14" r="3"/><line x1="8.12" y1="8.12" x2="12" y2="12"/><line x1="12" y1="12" x2="15" y2="15"/><path d="M15 5l-3 3"/></svg>""",
    "copy": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg>""",
    "paste": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 012 2v10a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>""",
    "bold": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 014 4 4 4 0 01-4 4H6z"/><path d="M6 12h9a4 4 0 010 8H6z"/><line x1="6" y1="4" x2="6" y2="20"/></svg>""",
    "italic": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>""",
    "underline": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3v7a6 6 0 006 6 6 6 0 006-6V3"/><line x1="4" y1="21" x2="20" y2="21"/></svg>""",
    "bullet-list": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="4" cy="6" r="1.5"/><circle cx="4" cy="12" r="1.5"/><circle cx="4" cy="18" r="1.5"/></svg>""",
    "numbered-list": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><text x="2" y="8" font-size="6" font-weight="bold" fill="currentColor">1</text><text x="2" y="14" font-size="6" font-weight="bold" fill="currentColor">2</text><text x="2" y="20" font-size="6" font-weight="bold" fill="currentColor">3</text></svg>""",
    "add-task": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>""",
    "add-meeting": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><circle cx="17" cy="17" r="3"/><line x1="17" y1="15" x2="17" y2="19"/><line x1="15" y1="17" x2="19" y2="17"/></svg>""",
    "calendar-day": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><circle cx="12" cy="16" r="2"/></svg>""",
    "calendar-week": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><line x1="7" y1="14" x2="7" y2="18"/><line x1="12" y1="14" x2="12" y2="18"/><line x1="17" y1="14" x2="17" y2="18"/></svg>""",
    "calendar-month": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/><rect x="6" y="14" width="4" height="4" rx="1"/><rect x="14" y="14" width="4" height="4" rx="1"/></svg>""",
    "filter": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>""",
    "search": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>""",
    "delete": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>""",
    "client-tasks": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10l-8 4m8-4v10m0 0l-8-4v-10"/></svg>""",
    "admin-tasks": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="12" y2="17"/></svg>""",
    "adhoc-tasks": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>""",
    "meetings": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>""",
    "ellipsis": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="4" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="20" cy="12" r="1"/></svg>""",
    "move": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 9 2 12 5 15"/><polyline points="9 5 12 2 15 5"/><polyline points="15 19 12 22 9 19"/><polyline points="19 15 22 12 19 9"/><line x1="12" y1="2" x2="12" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/></svg>""",
}

# ---------------------------------------------------------------------------
# ICON HELPER – used only for static HTML rendering (e.g., headers)
# ---------------------------------------------------------------------------
def icon(name, size=18, label=None):
    svg = NOTEBOOK_ICONS.get(name, '')
    if not svg:
        return ''
    svg = svg.replace('20', str(size), 2)
    html = '<span style="display:inline-flex;align-items:center;gap:4px;vertical-align:middle;">' + svg
    if label:
        html += '<span style="font-family:Inter,sans-serif;font-size:0.85rem;font-weight:500;">' + label + '</span>'
    html += '</span>'
    return html

# ---------------------------------------------------------------------------
# PAGE CSS (unchanged)
# ---------------------------------------------------------------------------
NOTEBOOK_CSS = '''
<style>
.stApp { background-color: #F3EFE6 !important; }
.stTabs [data-baseweb=tab-list] { gap: 0 !important; border-bottom: 1px solid rgba(26,43,76,0.12) !important; margin-bottom: 1rem !important; }
.stTabs [data-baseweb=tab] { font-family: 'Playfair Display', serif !important; font-style: italic !important; font-size: 1.1rem !important; font-weight: 600 !important; color: #6C727A !important; padding: 0.5rem 1rem !important; border: none !important; }
.stTabs [aria-selected=true] { color: #1A2B4C !important; border-bottom: 2px solid #D4AF37 !important; }
.nb-btn { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; background: #FFFFFF; border: 1px solid rgba(26,43,76,0.15); border-radius: 6px; font-size: 0.78rem; cursor: pointer; transition: all 0.15s ease; }
.nb-btn:hover { border-color: #D4AF37; background: #FFFDF6; }
.task-card { background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06); border-radius: 6px; padding: 12px; margin-bottom: 10px; }
.task-card:hover { border-color: rgba(212,175,55,0.4); }
.col-header { display: flex; align-items: center; gap: 6px; padding: 8px 0; margin-bottom: 8px; border-bottom: 2px solid #D4AF37; font-family: 'Playfair Display', serif; font-style: italic; font-size: 0.95rem; font-weight: 600; color: #1A2B4C; }
h1.page-title { font-family: 'Playfair Display', serif !important; font-style: italic !important; font-weight: 600 !important; color: #1A2B4C !important; font-size: 1.8rem !important; }
</style>
'''

# ---------------------------------------------------------------------------
# COLUMN CONFIG
# ---------------------------------------------------------------------------
COLUMN_CONFIG = {
    "client":  {"label": "Client Related Tasks", "icon": "client-tasks", "color": "#3B82F6"},
    "admin":   {"label": "Admin Tasks",          "icon": "admin-tasks",  "color": "#10B981"},
    "adhoc":   {"label": "Adhoc Tasks",          "icon": "adhoc-tasks",  "color": "#F59E0B"},
    "meeting": {"label": "Meetings",             "icon": "meetings",     "color": "#8B5CF6"},
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

# ---------------------------------------------------------------------------
# NOTEPAD TAB
# ---------------------------------------------------------------------------
def render_notepad_tab():
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Notepad</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6C727A;margin:0 0 1rem 0;">Create, open, save, and edit text documents with bullet list support.</p>', unsafe_allow_html=True)

    # Use plain text buttons with emojis for actions
    c1, c2, c3, c4, c5 = st.columns([1,1,1,1,3])
    with c1:
        if st.button("📄 New", use_container_width=True):
            st.session_state.update({'nb_content': '', 'nb_title': 'Untitled.txt'})
    with c2:
        st.button("📂 Open", use_container_width=True)
    with c3:
        if st.button("💾 Save", use_container_width=True):
            st.toast('Document saved', icon='checkmark')
    with c4:
        st.button("💾 Save As", use_container_width=True)
    with c5:
        st.text_input('', value='Untitled.txt', key='nb_title', label_visibility='collapsed')

    # Formatting row – plain text
    fc = st.columns(6)
    with fc[0]: st.button("B", key='fmt_bold', help="Bold")
    with fc[1]: st.button("I", key='fmt_italic', help="Italic")
    with fc[2]: st.button("U", key='fmt_underline', help="Underline")
    with fc[3]: st.button("•", key='fmt_list', help="Bullet List")
    with fc[4]: st.button("1.", key='fmt_olist', help="Numbered List")
    with fc[5]: st.button("☰", key='fmt_more', help="More formatting")

    content_key = 'nb_content'
    if content_key not in st.session_state:
        st.session_state[content_key] = ''
    st.session_state[content_key] = st.text_area(
        'Editor', value=st.session_state[content_key], height=500,
        key='nb_editor', label_visibility='collapsed',
        placeholder='Start typing...\n- Use - or * for bullets\n- Press Enter for next bullet'
    )

    # Edit actions – plain text
    ec = st.columns(6)
    with ec[0]: st.button("↩ Undo", use_container_width=True)
    with ec[1]: st.button("↪ Redo", use_container_width=True)
    with ec[2]: st.button("✂ Cut", use_container_width=True)
    with ec[3]: st.button("📋 Copy", use_container_width=True)
    with ec[4]: st.button("📋 Paste", use_container_width=True)
    with ec[5]:
        words = len(st.session_state.get('nb_content','').split())
        st.caption(f'Words: {words}')

# ---------------------------------------------------------------------------
# DAILY LOG TAB
# ---------------------------------------------------------------------------
def render_daily_log_tab():
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Daily Log</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6C727A;margin:0 0 1rem 0;">Track tasks across categories with day/week/month filtering.</p>', unsafe_allow_html=True)

    if 'dl_date' not in st.session_state:
        st.session_state.dl_date = datetime.date.today()
    if 'dl_view' not in st.session_state:
        st.session_state.dl_view = 'Day'
    for k in ['client','admin','adhoc','meeting']:
        if f'dl_{k}' not in st.session_state:
            st.session_state[f'dl_{k}'] = []

    r1, r2, r3, r4, r5 = st.columns([2,2,1,1,2])
    with r1:
        st.date_input('Date', key='dl_date', label_visibility='collapsed')
    with r2:
        st.segmented_control('View', ['Day','Week','Month'], key='dl_view', label_visibility='collapsed')
    with r3:
        if st.button("➕ Task", key='dl_add_task_btn', use_container_width=True):
            st.session_state.dl_show_add = True
    with r4:
        if st.button("📅 Meet", key='dl_add_meet_btn', use_container_width=True):
            st.session_state.dl_show_meet = True
    with r5:
        st.text_input('Search', placeholder='Search...', label_visibility='collapsed', key='dl_search')

    date_from, date_to = _get_date_range(st.session_state.dl_view, st.session_state.dl_date)
    st.caption(f'Showing: {date_from.strftime("%b %d")} - {date_to.strftime("%b %d, %Y")}')

    if st.session_state.get('dl_show_add'):
        with st.expander('New Task', expanded=True):
            cat_sel = st.selectbox('Category', ['client','admin','adhoc','meeting'], format_func=lambda x: COLUMN_CONFIG[x]['label'], key='dl_new_cat')
            content = st.text_area('Content', placeholder='- First item\n- Second item\n- Third item', key='dl_new_content', height=100)
            if st.button('Add', type='primary', use_container_width=True, key='dl_add_confirm'):
                if content.strip():
                    new_id = hashlib.md5(content.encode()).hexdigest()[:8]
                    st.session_state[f'dl_{cat_sel}'].append({
                        'id': new_id, 'content': content,
                        'due_date': st.session_state.dl_date.isoformat(), 'column_type': cat_sel,
                    })
                    st.session_state.dl_show_add = False
                    st.rerun()

    if st.session_state.get('dl_show_meet'):
        with st.expander('New Meeting', expanded=True):
            mt = st.text_input('Meeting title', key='dl_meet_title')
            md = st.text_area('Notes', placeholder='- Agenda item 1\n- Agenda item 2', key='dl_meet_detail', height=80)
            if st.button('Add Meeting', type='primary', use_container_width=True, key='dl_meet_confirm'):
                text = mt + '\n' + md if md else mt
                if text.strip():
                    new_id = hashlib.md5(text.encode()).hexdigest()[:8]
                    st.session_state['dl_meeting'].append({
                        'id': new_id, 'content': text,
                        'due_date': st.session_state.dl_date.isoformat(), 'column_type': 'meeting',
                    })
                    st.session_state.dl_show_meet = False
                    st.rerun()

    kanban_cols = st.columns(4, gap='small')
    for idx, (k, v) in enumerate(COLUMN_CONFIG.items()):
        with kanban_cols[idx]:
            # Use icon() only here – static HTML is safe
            st.markdown(f'<div class="col-header" style="border-bottom-color:{v["color"]};">{icon(v["icon"], size=18, label=v["label"])}</div>', unsafe_allow_html=True)
            tasks = st.session_state.get(f'dl_{k}', [])
            search_term = st.session_state.get('dl_search', '').strip().lower()
            if not tasks:
                st.markdown('<div style="color:#6C727A;font-size:0.75rem;font-style:italic;text-align:center;padding:20px 0;">No entries</div>', unsafe_allow_html=True)
            else:
                for t in tasks:
                    if search_term and search_term not in t.get('content','').lower():
                        continue
                    st.markdown('<div class="task-card">', unsafe_allow_html=True)
                    edited = st.text_area('Task', value=t['content'], height=max(90, min(200, len(t['content'].split('\n'))*24+60)), key=f'dl_task_{k}_{t["id"]}', label_visibility='collapsed')
                    t['content'] = edited
                    meta_c = st.columns([1,1,1])
                    with meta_c[0]: st.caption(f'Due: {t.get("due_date","")[:10]}')
                    with meta_c[1]: st.caption(v['label'])
                    with meta_c[2]:
                        if st.button('✕', key=f'dl_del_{k}_{t["id"]}'):
                            tasks.remove(t)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            # Use plain text for the "Add" button
            if st.button("➕ Add", key=f'dl_add_{k}', use_container_width=True):
                st.session_state.dl_show_add = True
                st.rerun()

# ---------------------------------------------------------------------------
# MAIN PAGE
# ---------------------------------------------------------------------------
st.set_page_config(page_title='Project Echo - Notebook', layout='wide', initial_sidebar_state='expanded')
setup_page_layout()
st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)

# Use plain text (with emojis) for tab labels – HTML is not allowed in st.tabs()
tab1, tab2 = st.tabs(["📝 Notepad", "📅 Daily Log"])

with tab1:
    render_notepad_tab()
with tab2:
    render_daily_log_tab()
