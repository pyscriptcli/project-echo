import sys
import os

# Ensure root directory is resolvable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout

# 1. Page Config (MUST be first)
st.set_page_config(
    page_title="Project Echo - Meetings Workspace",
    layout="wide",
    initial_sidebar_state="collapsed"
)
setup_page_layout()

# 2. Native Harmonized Styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }

.stApp {
    background-color: #F3EFE6; 
    background-image: linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}
.stApp > header { display: none !important; }
.block-container { padding-top: 1.5rem !important; padding-right: 2rem !important; padding-left: 2rem !important; }

h3 {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important; 
    font-weight: 400 !important; 
    color: #1A2B4C !important; 
    letter-spacing: 0.02em; 
    margin-bottom: 0.25rem; 
    font-size: 1.25rem !important;
}

.playfair-label {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important;
    color: #1A2B4C !important; 
    font-size: 1.05rem !important; 
    margin-bottom: 0.25rem !important; 
    display: block;
}

/* Master-Detail White Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.25rem !important; 
    margin-bottom: 1rem !important;
}

.stTextArea textarea, .stTextInput input, [data-baseweb="input"], [data-baseweb="select"] {
    background-color: #FAFAFA !important; 
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important; 
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    background-color: #FFFFFF !important; 
    border-color: #D4AF37 !important;
}

/* Base Buttons */
.stButton > button {
    background-color: #222222 !important; 
    color: #FFFFFF !important; 
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 0.82rem !important; 
    height: 36px !important; 
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important; 
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:hover { 
    background-color: #D4AF37 !important; 
    color: #161616 !important; 
}

/* Active Meeting Card Indicator */
.stButton > button[key^="sel_m_"] {
    border-radius: 8px !important;
    height: auto !important;
    min-height: 48px !important;
    padding: 0.6rem 0.8rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    background-color: #FAFAFA !important;
    color: #2D2D2D !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    box-shadow: none !important;
}

.stButton > button[key^="sel_m_"]:hover {
    border-color: #D4AF37 !important;
    background-color: #FFFFFF !important;
    color: #1A2B4C !important;
}

/* Save Button Icon */
.stButton > button[key^="btn_save_"]::before {
    content: "";
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 6px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
}

/* Delete Button Icon */
.stButton > button[key^="del_"] { 
    background-color: #FDF9F9 !important; 
    color: #B23A3A !important; 
    border: 1px solid rgba(178, 58, 58, 0.25) !important; 
}
.stButton > button[key^="del_"]:hover { 
    background-color: #B23A3A !important; 
    color: #FFFFFF !important; 
}
.stButton > button[key^="del_"]::before {
    content: "";
    display: inline-block;
    width: 15px;
    height: 15px;
    margin-right: 4px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E") no-repeat center;
}

/* Gallery Meta Tags */
.meta-chip {
    display: inline-block;
    font-size: 0.76rem;
    color: #666;
    margin-right: 8px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 3. Data Fetching
meetings = fetch_meeting_archives(limit=500)

if not meetings:
    st.info("No meeting records found in Supabase.")
    st.stop()

def get_iso_date(meeting_item):
    raw_d = str(meeting_item.get("meeting_date", ""))
    return raw_d[:10] if len(raw_d) >= 10 else ""

all_dates = sorted(list({get_iso_date(m) for m in meetings if get_iso_date(m)}), reverse=True)

# 4. Master-Detail Split Workspace Layout
col_gallery, col_viewer = st.columns([3.5, 6.5], gap="medium")

# ================= LEFT: Meeting Gallery Pane =================
with col_gallery:
    with st.container(border=True):
        st.markdown("<h3>Meeting Gallery</h3>", unsafe_allow_html=True)
        st.caption("Search, filter, and select a meeting to inspect.")
        
        search_q = st.text_input("Search", placeholder="Client, ID, PIC, Topic...", label_visibility="collapsed", key="search_query")
        
        f_date = st.selectbox("Date Filter", options=["All Dates"] + all_dates, index=0, label_visibility="collapsed", key="date_dropdown")
        
        # Filtering records
        filtered_meetings = meetings
        if f_date != "All Dates":
            filtered_meetings = [m for m in filtered_meetings if get_iso_date(m) == f_date]
        if search_q:
            q_low = search_q.lower()
            filtered_meetings = [
                m for m in filtered_meetings if q_low in " ".join([
                    str(m.get("client_name", "")),
                    str(m.get("meeting_id", "")),
                    str(m.get("meeting_date", "")),
                    str(m.get("location", "")),
                    str(m.get("prepared_by", "")),
                    str(m.get("confirmed_by", "")),
                    str(m.get("transcript_md", "")),
                    str(m.get("summary_md", "")),
                    str(m.get("table_items", ""))
                ]).lower()
            ]

        st.caption(f"Showing **{len(filtered_meetings)}** record(s)")
        st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

        # Scrollable gallery listing
        with st.container(height=650):
            if not filtered_meetings:
                st.warning("No records matched.")
            else:
                current_sel_id = st.session_state.get("selected_meeting_id")
                for idx, m in enumerate(filtered_meetings):
                    m_id_val = m.get("meeting_id", f"MOM-{idx}")
                    client_lbl = m.get("client_name") or "Meeting Record"
                    d_val = get_iso_date(m)
                    prep_val = m.get("prepared_by") or "CRD Team"
                    
                    is_active = (m_id_val == current_sel_id)
                    btn_label = f"{'▶ ' if is_active else ''}{client_lbl}\n📅 {d_val}  |  👤 {prep_val}"
                    
                    if st.button(btn_label, key=f"sel_m_{m_id_val}_{idx}"):
                        st.session_state["selected_meeting_id"] = m_id_val
                        st.rerun()

# Determine currently selected meeting for right viewer
if not filtered_meetings:
    with col_viewer:
        st.info("Select or clear filter to display meeting details.")
    st.stop()

selected_id = st.session_state.get("selected_meeting_id")
valid_ids = [m.get("meeting_id") for m in filtered_meetings]

if selected_id not in valid_ids:
    active_meeting = filtered_meetings[0]
    st.session_state["selected_meeting_id"] = active_meeting.get("meeting_id")
else:
    active_meeting = next(m for m in filtered_meetings if m.get("meeting_id") == selected_id)

m_id = active_meeting.get("meeting_id")

# ================= RIGHT: Meeting Inspector & Editor =================
with col_viewer:
    # 1. Metadata Header Card
    with st.container(border=True):
        head_c1, head_c2 = st.columns([7, 3])
        with head_c1:
            st.markdown(f"<h3>{active_meeting.get('client_name', 'Client Meeting')}</h3>", unsafe_allow_html=True)
            st.caption(f"Meeting ID: `{m_id}`")
        with head_c2:
            st.write(f"**Date:** {active_meeting.get('meeting_date', 'N/A')}")
            st.write(f"**Location:** {active_meeting.get('location', 'N/A')}")

        m_c1, m_c2 = st.columns(2)
        with m_c1:
            st.write(f"**Prepared By:** {active_meeting.get('prepared_by', 'N/A')}")
        with m_c2:
            st.write(f"**Confirmed By:** {active_meeting.get('confirmed_by', 'N/A')}")

    # 2. Workspace View Tabs (Editor / Transcript / Raw Payload)
    tab_editor, tab_transcript = st.tabs(["Minutes of Meeting Editor", "Full Transcript"])

    with tab_editor:
        with st.container(border=True):
            st.markdown("<h3>Minutes of Meeting Items</h3>", unsafe_allow_html=True)
            st.caption("Inline editable cards. Changes are synchronized to Supabase.")

            editor_key = f"mom_rows_{m_id}"
            if editor_key not in st.session_state:
                raw_items = active_meeting.get("table_items", [])
                if isinstance(raw_items, list) and len(raw_items) > 0:
                    st.session_state[editor_key] = raw_items
                else:
                    st.session_state[editor_key] = [{
                        "Discussion Points": "", "Action Plan": "",
                        "Indicative Delivery Date": "", "Person-in-charge": ""
                    }]

            rows = st.session_state[editor_key]
            rows_to_keep = []

            for idx, row in enumerate(rows):
                with st.container(border=True):
                    c_disc, c_act, c_date, c_pic, c_del = st.columns([3.2, 3.2, 1.8, 1.8, 0.6])

                    with c_disc:
                        st.markdown('<span class="playfair-label">Discussion Points</span>', unsafe_allow_html=True)
                        st.text_area("DP", value=str(row.get("Discussion Points", "")), key=f"dp_{m_id}_{idx}", height=75, label_visibility="collapsed")
                    with c_act:
                        st.markdown('<span class="playfair-label">Action Plan</span>', unsafe_allow_html=True)
                        st.text_area("AP", value=str(row.get("Action Plan", "")), key=f"ap_{m_id}_{idx}", height=75, label_visibility="collapsed")
                    with c_date:
                        st.markdown('<span class="playfair-label">Delivery Date</span>', unsafe_allow_html=True)
                        st.text_area("DD", value=str(row.get("Indicative Delivery Date", "")), key=f"date_{m_id}_{idx}", height=75, label_visibility="collapsed")
                    with c_pic:
                        st.markdown('<span class="playfair-label">Person-in-charge</span>', unsafe_allow_html=True)
                        st.text_area("PIC", value=str(row.get("Person-in-charge", "")), key=f"pic_{m_id}_{idx}", height=75, label_visibility="collapsed")
                    with c_del:
                        st.write("<div style='height: 38px;'></div>", unsafe_allow_html=True)
                        if st.button("Delete", key=f"del_{m_id}_{idx}", help="Delete Row"):
                            continue

                    rows_to_keep.append({
                        "Discussion Points": st.session_state[f"dp_{m_id}_{idx}"],
                        "Action Plan": st.session_state[f"ap_{m_id}_{idx}"],
                        "Indicative Delivery Date": st.session_state[f"date_{m_id}_{idx}"],
                        "Person-in-charge": st.session_state[f"pic_{m_id}_{idx}"]
                    })

            if len(rows_to_keep) != len(rows):
                st.session_state[editor_key] = rows_to_keep
                st.rerun()

            # Add Row Control
            add_c1, _ = st.columns([2.5, 7.5])
            with add_c1:
                if st.button("+ Add Item", key=f"btn_add_{m_id}"):
                    rows_to_keep.append({
                        "Discussion Points": "", "Action Plan": "",
                        "Indicative Delivery Date": "", "Person-in-charge": ""
                    })
                    st.session_state[editor_key] = rows_to_keep
                    st.rerun()

            # Summary Box
            st.markdown('<span class="playfair-label" style="margin-top:0.75rem;">Summary & Other Discussions</span>', unsafe_allow_html=True)
            current_summary = str(active_meeting.get("summary_md", "")).replace("### Summary", "").strip()
            summary_val = st.text_area(
                "Summary Content",
                value=current_summary,
                height=100,
                label_visibility="collapsed",
                key=f"summary_{m_id}"
            )

            # Persist Updates
            st.write("")
            sv_col1, sv_col2 = st.columns([7.5, 2.5])
            with sv_col2:
                if st.button("Save All Changes", key=f"btn_save_{m_id}"):
                    with st.spinner("Saving to Supabase..."):
                        client = get_supabase_client()
                        if not client:
                            st.error("Supabase client uninitialized.")
                        else:
                            try:
                                client.table("meeting_archives").update({
                                    "table_items": rows_to_keep,
                                    "summary_md": f"### Summary\n{summary_val}"
                                }).eq("meeting_id", m_id).execute()

                                st.success("Meeting record updated successfully!")
                                if editor_key in st.session_state:
                                    del st.session_state[editor_key]
                            except Exception as e:
                                st.error(f"Update failed: {e}")

    with tab_transcript:
        with st.container(border=True):
            raw_tx = active_meeting.get("transcript_md", "No transcript stored.")
            clean_tx = raw_tx.replace("### Transcript", "").strip()
            st.text_area(
                "Transcript Stream",
                value=clean_tx,
                height=520,
                disabled=True,
                label_visibility="collapsed"
            )
