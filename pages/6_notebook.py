# pages/6_notebook.py
# -*- coding: utf-8 -*-

import sys, os, re, json, datetime, hashlib
from typing import Optional
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from components.sidebar import setup_page_layout
from utils.auth import require_auth
from utils.db import get_supabase_client

# SVG ICON REGISTRY
NOTEBOOK_ICONS = {
    "client": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10l-8 4m8-4v10m0 0l-8-4v-10"/></svg>""",
    "admin": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="12" y2="17"/></svg>""",
    "adhoc": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>""",
    "meeting": """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>""",
}

NOTEBOOK_CSS = '''<style>
.stApp { background-color: #F3EFE6 !important; }
.stTabs [data-baseweb=tab] { font-family: Playfair Display, serif !important; font-style: italic !important; }
.stTabs [aria-selected=true] { color: #1A2B4C !important; border-bottom: 2px solid #D4AF37 !important; }
.task-card { background: #FFFFFF; border: 1px solid rgba(0,0,0,0.06); border-radius: 6px; padding: 12px; margin-bottom: 10px; }
.task-card:hover { border-color: rgba(212,175,55,0.4); }
.col-header { display: flex; align-items: center; gap: 6px; padding: 8px 0; margin-bottom: 8px; border-bottom: 2px solid #D4AF37; font-family: Playfair Display, serif; font-style: italic; font-size: 0.95rem; font-weight: 600; color: #1A2B4C; }
h1.page-title { font-family: Playfair Display, serif !important; font-style: italic !important; font-weight: 600 !important; }
</style>'''

COLUMN_CONFIG = {
    "client": {"label": "Client Related Tasks", "color": "#3B82F6"},
    "admin": {"label": "Admin Tasks", "color": "#10B981"},
    "adhoc": {"label": "Adhoc Tasks", "color": "#F59E0B"},
    "meeting": {"label": "Meetings", "color": "#8B5CF6"},
}

def _get_date_range(v, d):
    if v == "Day": return d, d
    elif v == "Week": s = d - datetime.timedelta(days=d.weekday()); return s, s + datetime.timedelta(days=6)
    else: s = d.replace(day=1); import calendar; _, l = calendar.monthrange(d.year, d.month); return s, d.replace(day=l)

def _init_state():
    for k, v in {"nb_content": "", "nb_title": "Untitled.txt", "dl_date": datetime.date.today(), "dl_view": "Day", "_dl_id_counter": 0}.items():
        if k not in st.session_state: st.session_state[k] = v
    for k in ["client", "admin", "adhoc", "meeting"]:
        if ("dl_" + k) not in st.session_state: st.session_state["dl_" + k] = []

def render_notepad_tab():
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class=page-title>Notepad</h1>', unsafe_allow_html=True)
    _init_state()
    c1,c2,c3,c4,c5,c6 = st.columns([1.1,1.1,1.1,1.1,2.5,0.9])
    with c1:
        if st.button("New", icon=":material/note_add:", key="nb_new", use_container_width=True):
            st.session_state.nb_content = ''; st.session_state.nb_title = 'Untitled.txt'; st.rerun()
    with c2:
        if st.button("Open", icon=":material/folder_open:", key="nb_open", use_container_width=True): pass
    with c3:
        if st.button("Save", icon=":material/save:", key="nb_save", use_container_width=True):
            st.toast("Document saved", icon=":material/check_circle:")
    with c4:
        if st.button("Save As", icon=":material/save_as:", key="nb_saveas", use_container_width=True): pass
    with c5:
        st.text_input("Document", value=st.session_state.nb_title, key="nb_title_input", label_visibility="collapsed")
    with c6:
        if st.button(" ", icon=":material/delete:", key="nb_delete", use_container_width=True, help="Delete document"):
            st.session_state.nb_content = ''; st.session_state.nb_title = 'Untitled.txt'; st.rerun()
    st.session_state.nb_title = st.session_state.nb_title_input
    fc = st.columns(7)
    with fc[0]: st.button(icon=":material/format_bold:", key="fmt_bold", label="B", help="Bold")
    with fc[1]: st.button(icon=":material/format_italic:", key="fmt_italic", label="I", help="Italic")
    with fc[2]: st.button(icon=":material/format_underlined:", key="fmt_uline", label="U", help="Underline")
    with fc[3]: st.button(icon=":material/format_list_bulleted:", key="fmt_list", label="List", help="Bullet list")
    with fc[4]: st.button(icon=":material/format_list_numbered:", key="fmt_olist", label="List", help="Numbered list")
    with fc[5]: st.caption(f'Words: {len(st.session_state.get("nb_content", "").split())}')
    with fc[6]: st.caption("Auto-save: On")
    st.session_state.nb_content = st.text_area('Editor', value=st.session_state.nb_content, height=500, key='nb_editor', label_visibility='collapsed', placeholder='Start typing...')
    ec = st.columns(6)
    with ec[0]: st.button("Undo", icon=":material/undo:", key="nb_undo", use_container_width=True)
    with ec[1]: st.button("Redo", icon=":material/redo:", key="nb_redo", use_container_width=True)
    with ec[2]: st.button("Cut", icon=":material/content_cut:", key="nb_cut", use_container_width=True)
    with ec[3]: st.button("Copy", icon=":material/content_copy:", key="nb_copy", use_container_width=True)
    with ec[4]: st.button("Paste", icon=":material/content_paste:", key="nb_paste", use_container_width=True)
    with ec[5]: st.caption(f'Chars: {len(st.session_state.get("nb_content", ""))}')

def render_daily_log_tab():
    st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
    st.markdown('<h1 class=page-title>Daily Log</h1>', unsafe_allow_html=True)
    _init_state()
    r1,r2,r3,r4,r5 = st.columns([2,2,1.2,1.2,2])
    with r1: st.date_input("Date", key="dl_date", label_visibility="collapsed")
    with r2: st.segmented_control("View", ["Day","Week","Month"], key="dl_view", label_visibility="collapsed")
    with r3:
        if st.button("Task", icon=":material/add_task:", key="dl_add_task_btn", use_container_width=True):
            st.session_state.dl_show_add = True
    with r4:
        if st.button("Meet", icon=":material/event_available:", key="dl_add_meet_btn", use_container_width=True):
            st.session_state.dl_show_meet = True
    with r5:
        st.text_input("Search", placeholder="Search...", label_visibility="collapsed", key="dl_search")
    df, dt = _get_date_range(st.session_state.dl_view, st.session_state.dl_date)
    st.caption(f'Showing: {df.strftime("%b %d")} - {dt.strftime("%b %d, %Y")}')
    if st.session_state.get('dl_show_add'):
        with st.expander('New Task', expanded=True):
            st.selectbox('Category', ['client','admin','adhoc','meeting'], format_func=lambda x: COLUMN_CONFIG[x]['label'], key='dl_new_cat')
            c = st.text_area('Content', key='dl_new_content', height=100)
            if st.button('Add', type='primary', key='dl_add_confirm', use_container_width=True):
                if c.strip():
                    st.session_state._dl_id_counter += 1
                    nid = 't' + str(st.session_state._dl_id_counter)
                    st.session_state['dl_' + st.session_state.dl_new_cat].append({'id': nid, 'content': c, 'due_date': st.session_state.dl_date.isoformat()})
                    st.session_state.dl_show_add = False; st.rerun()
    if st.session_state.get('dl_show_meet'):
        with st.expander('New Meeting', expanded=True):
            mt = st.text_input("Meeting title", key="dl_meet_title")
            md = st.text_area("Notes", key="dl_meet_detail", height=80)
            if st.button('Add Meeting', type='primary', key='dl_meet_confirm', use_container_width=True):
                t = mt + chr(10) + md if md else mt
                if t.strip():
                    st.session_state._dl_id_counter += 1
                    nid = 't' + str(st.session_state._dl_id_counter)
                    st.session_state['dl_meeting'].append({'id': nid, 'content': t, 'due_date': st.session_state.dl_date.isoformat()})
                    st.session_state.dl_show_meet = False; st.rerun()
    for idx, (k, v) in enumerate(COLUMN_CONFIG.items()):
        with st.columns(4, gap="small")[idx]:
            s = NOTEBOOK_ICONS.get(k, '')
            st.markdown(f'<div class=col-header style=border-bottom-color:{v["color"]};>{s} <span>{v["label"]}</span></div>', unsafe_allow_html=True)
            for t in st.session_state.get('dl_' + k, []):
                st.markdown('<div class=task-card>', unsafe_allow_html=True)
                edited = st.text_area('Task', value=t['content'], key='dl_task_' + k + '_' + t['id'], label_visibility='collapsed')
                t['content'] = edited
                mc = st.columns([1,1,1])
                with mc[0]: st.caption(f"Due: {t.get('due_date', '')[:10]}")
                with mc[1]: st.caption(v['label'])
                with mc[2]:
                    if st.button(label=' ', icon=':material/delete:', key='dl_del_' + k + '_' + t['id'], help='Delete'):
                        st.session_state['dl_' + k].remove(t); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            if st.button('Add', icon=':material/add:', key='dl_add_' + k, use_container_width=True):
                st.session_state.dl_show_add = True; st.rerun()

st.set_page_config(page_title='Project Echo - Notebook', layout='wide', initial_sidebar_state='expanded')
setup_page_layout()
st.markdown(NOTEBOOK_CSS, unsafe_allow_html=True)
tab1, tab2 = st.tabs(['Notepad', 'Daily Log'])
with tab1: render_notepad_tab()
with tab2: render_daily_log_tab()
