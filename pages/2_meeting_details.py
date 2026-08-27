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

# 2. Global State for View Mode
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "gallery"  # "gallery" or "details"
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

# 3. Custom CSS & Exact Tab Bar Styling
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
.block-container { padding-top: 1.5rem !important; padding-right: 2.5rem !important; padding-left: 2.5rem !important; }

h3 {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important; 
    font-weight: 400 !important; 
    color: #1A2B4C !important; 
    letter-spacing: 0.02em; 
    margin-bottom: 0.25rem; 
    font-size: 1.35rem !important;
}

.playfair-label {
    font-family: 'Playfair Display', serif !important; 
    font-style: italic !important;
    color: #1A2B4C !important; 
    font-size: 1.05rem !important; 
    margin-bottom: 0.25rem !important; 
    display: block;
}

/* White Card Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1rem !important;
}

/* Form Inputs */
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

/* Action Buttons */
.stButton > button {
    background-color: #1C1C1C !important; 
    color: #FFFFFF !important; 
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 0.82rem !important; 
    height: 36px !important; 
    padding: 0 1.25rem !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.12) !important; 
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:hover { 
    background-color: #D4AF37 !important; 
    color: #161616 !important; 
}

/* Back Button Pill */
.stButton > button[key="btn_back_gallery"] {
    background-color: transparent !important;
    color: #1A2B4C !important;
    border: 1px solid rgba(26, 43, 76, 0.3) !important;
    width: auto !important;
    min-width: 160px !important;
}
.stButton > button[key="btn_back_gallery"]:hover {
    background-color: #1A2B4C !important;
    color: #FFFFFF !important;
}

/* Gallery Typography */
.card-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-size: 1.22rem !important;
    color: #1A2B4C !important;
    margin: 0 0 0.2rem 0 !important;
}

.card-meta {
    font-size: 0.84rem !important;
    color: #666666 !important;
    margin-bottom: 0.5rem !important;
}

.card-desc {
    font-size: 0.88rem !important;
    color: #2D2D2D !important;
    line-height: 1.5 !important;
    margin: 0 !important;
}

/* ================= EXACT TAB STYLING (Image Match) ================= */
button[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    color: #1A2B4C !important;
    padding: 0.5rem 1rem !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FF4B4B !important;
    border-bottom: 2px solid #FF4B4B !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #FF4B4B !important;
}

/* Delete Row Button Styling & SVG Icon */
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
    width: 14px;
    height: 14px;
    margin-right: 4px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E") no-repeat center;
}

/* Save Button Icon */
.stButton > button[key^="btn_save_"]::before {
    content: "";
    display: inline-block;
    width: 15px;
    height: 15px;
    margin-right: 6px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 4. Data Ingestion
meetings = fetch_meeting_archives(limit=500)

if not meetings:
    st.info("No meeting records found in Supabase.")
    st.stop()

def get_iso_date(meeting_item):
    raw_d = str(meeting_item.get("meeting_date", ""))
    return raw_d[:10] if len(raw_d) >= 10 else ""

all_dates = sorted(list({get_iso_date(m) for m in meetings if get_iso_date(m)}), reverse=True)
all_clients = sorted(list({str(m.get("client_name", "Unknown")).strip() for m in meetings if m.get("client_name")}))

# ==============================================================================
# MODE 1: FULL-SCREEN MEETING GALLERY
# ==============================================================================
if st.session_state["view_mode"] == "gallery":
    with st.container(border=True):
        st.markdown("<h3>Meeting Gallery & Search Hub</h3>", unsafe_allow_html=True)
        st.caption("Search across meeting topics, filter by dates/clients, or inspect complete minutes.")
        
        # Comprehensive Filter Bar
        f_c1, f_c2, f_c3, f_c4 = st.columns([4.5, 2.2, 2.2, 1.1])
        
        with f_c1:
            search_q = st.text_input("Search", placeholder="Search by client, ID, topic, transcript, PIC...", label_visibility="collapsed", key="gal_search_q")
        with f_c2:
            f_client = st.selectbox("Client Filter", options=["All Clients"] + all_clients, index=0, label_visibility="collapsed", key="gal_client_f")
        with f_c3:
            f_date = st.selectbox("Date Filter", options=["All Dates"] + all_dates, index=0, label_visibility="collapsed", key="gal_date_f")
        with f_c4:
            if st.button("Reset", key="btn_reset_filters"):
                st.session_state["gal_search_q"] = ""
                st.session_state["gal_client_f"] = "All Clients"
                st.session_state["gal_date_f"] = "All Dates"
                st.rerun()

        # Filtering Logic
        filtered_meetings = meetings
        if f_client != "All Clients":
            filtered_meetings = [m for m in filtered_meetings if str(m.get("client_name", "")).strip() == f_client]
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

        st.caption(f"Showing **{len(filtered_meetings)}** matching meeting archive(s)")
        st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border: none; border-top: 1px solid rgba(0,0,0,0.06);'>", unsafe_allow_html=True)

        if not filtered_meetings:
            st.warning("No meeting records matched your search parameters.")
        else:
            for idx, m in enumerate(filtered_meetings):
                m_id_val = m.get("meeting_id", f"MOM-{idx}")
                client_lbl = m.get("client_name") or "Meeting Record"
                d_val = get_iso_date(m) or "____________"
                loc_val = m.get("location") or "____________"
                prep_val = m.get("prepared_by") or "CRD Team"
                
                summary_raw = str(m.get("summary_md", "")).replace("### Summary", "").strip()
                if not summary_raw:
                    summary_raw = "No summary recorded. Minutes generated and stored in Supabase archive."
                preview_text = summary_raw[:220] + ("..." if len(summary_raw) > 220 else "")

                with st.container(border=True):
                    c_info, c_act = st.columns([8.2, 1.8])
                    with c_info:
                        st.markdown(f"<p class='card-title'>{client_lbl}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='card-meta'>Date: {d_val} &bull; {loc_val} &bull; Prepared by: {prep_val}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='card-desc'>{preview_text}</p>", unsafe_allow_html=True)
                    with c_act:
                        st.write("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                        if st.button("View Meeting", key=f"view_btn_{m_id_val}_{idx}"):
                            st.session_state["selected_meeting_id"] = m_id_val
                            st.session_state["view_mode"] = "details"
                            st.rerun()

# ==============================================================================
# MODE 2: FULL-SCREEN MEETING VIEWER & INSPECTOR
# ==============================================================================
elif st.session_state["view_mode"] == "details":
    target_id = st.session_state.get("selected_meeting_id")
    active_meeting = next((m for m in meetings if m.get("meeting_id") == target_id), None)

    if not active_meeting:
        st.session_state["view_mode"] = "gallery"
        st.rerun()

    m_id = active_meeting.get("meeting_id")

    # Header Navigation Bar
    top_nav1, top_nav2 = st.columns([2.5, 7.5])
    with top_nav1:
        if st.button("← Back to Gallery", key="btn_back_gallery"):
            st.session_state["view_mode"] = "gallery"
            st.rerun()

    # Meeting Metadata Card
    with st.container(border=True):
        m_head1, m_head2 = st.columns([6.5, 3.5])
        with m_head1:
            st.markdown(f"<h3>{active_meeting.get('client_name', 'Client Meeting')}</h3>", unsafe_allow_html=True)
            st.caption(f"Meeting ID: `{m_id}`")
        with m_head2:
            st.write(f"**Date:** {active_meeting.get('meeting_date', 'N/A')}")
            st.write(f"**Location:** {active_meeting.get('location', 'N/A')}")

        d_c1, d_c2 = st.columns(2)
        with d_c1:
            st.write(f"**Prepared By:** {active_meeting.get('prepared_by', 'N/A')}")
        with d_c2:
            st.write(f"**Confirmed By:** {active_meeting.get('confirmed_by', 'N/A')}")

    # Tabs (Matching Attached Screenshot Styling)
    tab_editor, tab_transcript = st.tabs(["Minutes of Meeting Editor", "Full Transcript"])

    with tab_editor:
        with st.container(border=True):
            st.markdown("<h3>Minutes of Meeting Items</h3>", unsafe_allow_html=True)
            st.caption("Inline editable cards. Changes are synchronized directly to Supabase.")

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

            add_c1, _ = st.columns([2, 8])
            with add_c1:
                if st.button("+ Add Item", key=f"btn_add_{m_id}"):
                    rows_to_keep.append({
                        "Discussion Points": "", "Action Plan": "",
                        "Indicative Delivery Date": "", "Person-in-charge": ""
                    })
                    st.session_state[editor_key] = rows_to_keep
                    st.rerun()

            st.markdown('<span class="playfair-label" style="margin-top:0.75rem;">Summary & Other Discussions</span>', unsafe_allow_html=True)
            current_summary = str(active_meeting.get("summary_md", "")).replace("### Summary", "").strip()
            summary_val = st.text_area(
                "Summary Content",
                value=current_summary,
                height=110,
                label_visibility="collapsed",
                key=f"summary_{m_id}"
            )

            st.write("")
            sv_col1, sv_col2 = st.columns([7.5, 2.5])
            with sv_col2:
                if st.button("Save All Changes", key=f"btn_save_{m_id}"):
                    with st.spinner("Saving updates to Supabase..."):
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
