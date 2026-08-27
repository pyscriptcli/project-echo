import sys
import os

# Ensure root directory is resolvable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout

# 1. Page Config (MUST be first)
st.set_page_config(
    page_title="Project Echo - Meetings Workspace",
    layout="wide",
    initial_sidebar_state="collapsed"
)
setup_page_layout()

# Default date filter to "This Month"
today = date.today()
first_day_of_month = today.replace(day=1)

# 2. Global State for View Mode & Filters
if "view_mode" not in st.session_state:
    st.session_state["view_mode"] = "gallery"
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None
if "gal_search_q" not in st.session_state:
    st.session_state["gal_search_q"] = ""
if "gal_type_f" not in st.session_state:
    st.session_state["gal_type_f"] = "All Meetings"
if "gal_date_range" not in st.session_state:
    st.session_state["gal_date_range"] = (first_day_of_month, today)
if "edit_meeting_details" not in st.session_state:
    st.session_state["edit_meeting_details"] = False

# 3. Custom CSS & Pure SVG Icon Button Injection
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

/* 3D Drop Shadow Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.08), 0 3px 8px rgba(0, 0, 0, 0.04) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
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

/* Base Buttons */
.stButton > button {
    background-color: #161616 !important; 
    color: #FFFFFF !important; 
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 0.82rem !important; 
    height: 38px !important; 
    padding: 0 1.5rem !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important; 
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:hover { 
    background-color: #D4AF37 !important; 
    color: #161616 !important; 
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 14px rgba(212, 175, 55, 0.3) !important;
}

/* Center Vertically & Right-Aligned View Meeting Button */
.view-btn-wrapper {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    height: 100% !important;
    min-height: 80px !important;
}

/* Topbar Date Picker Trigger Styling */
div[data-testid="stPopover"] > button {
    background-color: #FFFFFF !important;
    color: #003B6F !important;
    border: 1.5px solid #003B6F !important;
    border-radius: 6px !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    height: 38px !important;
    box-shadow: none !important;
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0 0.85rem !important;
}

div[data-testid="stPopover"] > button:hover {
    border-color: #00274B !important;
    background-color: #F8FAFC !important;
    color: #00274B !important;
    transform: none !important;
}

/* Popover Content Width for Split-Pane Date Picker */
div[data-testid="stPopoverBody"] {
    min-width: 560px !important;
    max-width: 600px !important;
    padding: 1.25rem !important;
    background-color: #FFFFFF !important;
    border-radius: 10px !important;
    box-shadow: 0 15px 35px rgba(0,0,0,0.18) !important;
}

/* Preset Buttons Inside Date Popover */
.stButton > button[key^="preset_"] {
    background-color: transparent !important;
    color: #4A5568 !important;
    border: 1px solid transparent !important;
    border-radius: 4px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 0.45rem 0.65rem !important;
    height: 34px !important;
    margin-bottom: 0.35rem !important;
    box-shadow: none !important;
}

.stButton > button[key^="preset_"]:hover {
    background-color: #EDF2F7 !important;
    color: #1A202C !important;
    transform: none !important;
}

.stButton > button[key="btn_apply_modal_date"] {
    background-color: #003B6F !important;
    color: #FFFFFF !important;
    border-radius: 4px !important;
    height: 36px !important;
    font-weight: 600 !important;
}
.stButton > button[key="btn_apply_modal_date"]:hover {
    background-color: #00284D !important;
    color: #FFFFFF !important;
    transform: none !important;
}

/* Back Button Pill */
.stButton > button[key="btn_back_gallery"] {
    background-color: transparent !important;
    color: #1A2B4C !important;
    border: 1px solid rgba(26, 43, 76, 0.3) !important;
    width: auto !important;
    min-width: 170px !important;
}
.stButton > button[key="btn_back_gallery"]:hover {
    background-color: #1A2B4C !important;
    color: #FFFFFF !important;
}

/* Details Action Buttons */
.stButton > button[key="btn_toggle_edit_details"] {
    background-color: #F4EAD4 !important;
    color: #8C6D23 !important;
    border: 1px solid rgba(201, 168, 76, 0.4) !important;
    height: 34px !important;
}
.stButton > button[key="btn_toggle_edit_details"]:hover {
    background-color: #D4AF37 !important;
    color: #161616 !important;
}

/* Gallery Typography */
.card-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-size: 1.25rem !important;
    color: #1A2B4C !important;
    margin: 0 0 0.25rem 0 !important;
    line-height: 1.3 !important;
}

.card-meta {
    font-size: 0.84rem !important;
    color: #666666 !important;
    margin-bottom: 0.55rem !important;
}

.card-desc {
    font-size: 0.88rem !important;
    color: #2D2D2D !important;
    line-height: 1.5 !important;
    margin: 0 !important;
}

/* Tabs Header */
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

/* Delete Row SVG Button */
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

/* Save Icon */
.stButton > button[key^="btn_save_"]::before,
.stButton > button[key="btn_save_meta"]::before {
    content: "";
    display: inline-block;
    width: 15px;
    height: 15px;
    margin-right: 6px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
}

/* SVG Icon in Popover Trigger */
.cal-svg-icon {
    display: inline-block;
    width: 16px;
    height: 16px;
    vertical-align: middle;
    margin-right: 6px;
    fill: currentColor;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 4. Data Ingestion & Date Normalization
meetings = fetch_meeting_archives(limit=500)

if not meetings:
    st.info("No meeting records found in Supabase.")
    st.stop()

def parse_meeting_date(raw_date_str):
    if not raw_date_str:
        return None
    raw_s = str(raw_date_str).strip()[:10]
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw_s, fmt).date()
        except ValueError:
            pass
    return None

def get_iso_date_str(meeting_item):
    parsed = parse_meeting_date(meeting_item.get("meeting_date", ""))
    return parsed.strftime("%Y-%m-%d") if parsed else ""

def categorize_meeting(meeting_item):
    client_name = str(meeting_item.get("client_name", "")).strip().lower()
    raw_payload = meeting_item.get("raw_payload", {}) or {}
    meeting_details = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
    external_atts = meeting_details.get("external_attendees", [])
    
    if "crd" in client_name:
        return "CRD Team Meetings"
    elif "internal" in client_name or "prime" in client_name or (not external_atts and not client_name):
        return "Internal Meetings"
    return "External Meetings"

# ==============================================================================
# MODE 1: FULL-SCREEN MEETING GALLERY
# ==============================================================================
if st.session_state["view_mode"] == "gallery":
    with st.container(border=True):
        st.markdown("<h3>Meeting Gallery</h3>", unsafe_allow_html=True)
        st.caption("Search across meeting topics, filter by category or date range, and review meetings.")
        
        # Filter Bar Layout
        f_c1, f_c2, f_c3, f_c4 = st.columns([4.2, 2.3, 2.5, 1.0])
        
        with f_c1:
            search_input = st.text_input(
                "Search",
                value=st.session_state["gal_search_q"],
                placeholder="Search by client, ID, topic, transcript, PIC...",
                label_visibility="collapsed",
                key="gal_search_input"
            )
            st.session_state["gal_search_q"] = search_input
            
        with f_c2:
            type_options = ["All Meetings", "Internal Meetings", "External Meetings", "CRD Team Meetings"]
            selected_type = st.selectbox(
                "Meeting Type",
                options=type_options,
                index=type_options.index(st.session_state["gal_type_f"]) if st.session_state["gal_type_f"] in type_options else 0,
                label_visibility="collapsed",
                key="gal_type_select"
            )
            st.session_state["gal_type_f"] = selected_type
            
        with f_c3:
            dr = st.session_state["gal_date_range"]
            if dr and len(dr) == 2:
                btn_label = f"{dr[0].strftime('%b %d, %Y')} — {dr[1].strftime('%b %d, %Y')} •"
            elif dr and len(dr) == 1:
                btn_label = f"{dr[0].strftime('%b %d, %Y')} •"
            else:
                btn_label = f"{first_day_of_month.strftime('%b %d, %Y')} — {today.strftime('%b %d, %Y')} •"

            with st.popover(btn_label, use_container_width=True):
                pop_left, pop_right = st.columns([1.1, 2.3], gap="medium")
                
                with pop_left:
                    st.markdown("<p style='font-size:0.75rem; color:#888; margin-bottom:0.4rem; text-transform:uppercase;'>Presets</p>", unsafe_allow_html=True)
                    
                    if st.button("This Week", key="preset_this_week"):
                        start_w = today - timedelta(days=today.weekday())
                        st.session_state["gal_date_range"] = (start_w, start_w + timedelta(days=6))
                        st.rerun()
                    if st.button("Last Week", key="preset_last_week"):
                        start_lw = today - timedelta(days=today.weekday() + 7)
                        st.session_state["gal_date_range"] = (start_lw, start_lw + timedelta(days=6))
                        st.rerun()
                    if st.button("This Month", key="preset_this_month"):
                        st.session_state["gal_date_range"] = (today.replace(day=1), today)
                        st.rerun()
                    if st.button("Last Month", key="preset_last_month"):
                        first_this = today.replace(day=1)
                        last_m_end = first_this - timedelta(days=1)
                        st.session_state["gal_date_range"] = (last_m_end.replace(day=1), last_m_end)
                        st.rerun()
                    if st.button("Clear", key="preset_clear"):
                        st.session_state["gal_date_range"] = ()
                        st.rerun()
                
                with pop_right:
                    picked_range = st.date_input(
                        "Custom Range",
                        value=st.session_state["gal_date_range"] if st.session_state["gal_date_range"] else (first_day_of_month, today),
                        label_visibility="collapsed",
                        key="modal_date_picker"
                    )
                    
                    st.write("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    app_c1, app_c2 = st.columns([5, 5])
                    with app_c2:
                        if st.button("Apply", key="btn_apply_modal_date"):
                            if isinstance(picked_range, tuple):
                                st.session_state["gal_date_range"] = picked_range
                            elif isinstance(picked_range, date):
                                st.session_state["gal_date_range"] = (picked_range, picked_range)
                            st.rerun()

        with f_c4:
            if st.button("Reset", key="btn_reset_all_filters"):
                st.session_state["gal_search_q"] = ""
                st.session_state["gal_type_f"] = "All Meetings"
                st.session_state["gal_date_range"] = (first_day_of_month, today)
                st.rerun()

        # Filtering Logic Execution
        filtered_meetings = []
        q_clean = st.session_state["gal_search_q"].strip().lower()
        active_type = st.session_state["gal_type_f"]
        active_dr = st.session_state["gal_date_range"]

        for m in meetings:
            if active_type != "All Meetings":
                if categorize_meeting(m) != active_type:
                    continue
            
            if active_dr:
                m_date_obj = parse_meeting_date(m.get("meeting_date", ""))
                if not m_date_obj:
                    continue
                if len(active_dr) == 1 and m_date_obj != active_dr[0]:
                    continue
                elif len(active_dr) == 2 and not (active_dr[0] <= m_date_obj <= active_dr[1]):
                    continue
            
            if q_clean:
                searchable_corpus = " ".join([
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
                if q_clean not in searchable_corpus:
                    continue
            
            filtered_meetings.append(m)

        is_filtered = bool(q_clean or active_type != "All Meetings" or active_dr != (first_day_of_month, today))
        if is_filtered:
            st.caption(f"Showing **{len(filtered_meetings)}** matching meeting archive(s)")
        else:
            st.caption(f"Showing all **{len(filtered_meetings)}** meeting archive(s) for this month")

        st.markdown("<hr style='margin: 0.5rem 0 1rem 0; border: none; border-top: 1px solid rgba(0,0,0,0.06);'>", unsafe_allow_html=True)

        if not filtered_meetings:
            st.warning("No meeting records matched your search parameters.")
        else:
            for idx, m in enumerate(filtered_meetings):
                m_id_val = m.get("meeting_id", f"MOM-{idx}")
                client_lbl = m.get("client_name") or "Meeting Record"
                d_val = get_iso_date_str(m) or "____________"
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
                        st.markdown('<div class="view-btn-wrapper">', unsafe_allow_html=True)
                        if st.button("View Meeting", key=f"view_btn_{m_id_val}_{idx}"):
                            st.session_state["selected_meeting_id"] = m_id_val
                            st.session_state["view_mode"] = "details"
                            st.session_state["edit_meeting_details"] = False
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

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

    # Header Navigation
    top_nav1, top_nav2 = st.columns([2.5, 7.5])
    with top_nav1:
        if st.button("← Back to Gallery", key="btn_back_gallery"):
            st.session_state["view_mode"] = "gallery"
            st.session_state["edit_meeting_details"] = False
            st.rerun()

    # Editable Meeting Metadata Card
    with st.container(border=True):
        m_head1, m_head2 = st.columns([7.5, 2.5])
        with m_head1:
            st.markdown(f"<h3>{active_meeting.get('client_name', 'Client Meeting')}</h3>", unsafe_allow_html=True)
            st.caption(f"Meeting ID: `{m_id}`")
        with m_head2:
            st.write("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            if not st.session_state["edit_meeting_details"]:
                if st.button("Edit Meeting Details", key="btn_toggle_edit_details"):
                    st.session_state["edit_meeting_details"] = True
                    st.rerun()
            else:
                if st.button("Cancel Edit", key="btn_cancel_edit_details"):
                    st.session_state["edit_meeting_details"] = False
                    st.rerun()

        if not st.session_state["edit_meeting_details"]:
            # Display Mode
            d_r1_c1, d_r1_c2 = st.columns(2)
            with d_r1_c1:
                st.write(f"**Date:** {active_meeting.get('meeting_date', 'N/A')}")
                st.write(f"**Prepared By:** {active_meeting.get('prepared_by', 'N/A')}")
            with d_r1_c2:
                st.write(f"**Location:** {active_meeting.get('location', 'N/A')}")
                st.write(f"**Confirmed By:** {active_meeting.get('confirmed_by', 'N/A')}")
        else:
            # Edit Mode
            e_r1_c1, e_r1_c2 = st.columns(2)
            with e_r1_c1:
                edit_client = st.text_input("Client / Company", value=str(active_meeting.get("client_name", "")), key=f"e_client_{m_id}")
                edit_date = st.text_input("Meeting Date", value=str(active_meeting.get("meeting_date", "")), key=f"e_date_{m_id}")
                edit_prep = st.text_input("Prepared By", value=str(active_meeting.get("prepared_by", "")), key=f"e_prep_{m_id}")
            with e_r1_c2:
                edit_loc = st.text_input("Location", value=str(active_meeting.get("location", "")), key=f"e_loc_{m_id}")
                edit_conf = st.text_input("Confirmed By", value=str(active_meeting.get("confirmed_by", "")), key=f"e_conf_{m_id}")

            st.write("")
            sm_c1, sm_c2 = st.columns([7.8, 2.2])
            with sm_c2:
                if st.button("Save Meeting Details", key="btn_save_meta"):
                    with st.spinner("Saving metadata to Supabase..."):
                        client = get_supabase_client()
                        if not client:
                            st.error("Supabase client uninitialized.")
                        else:
                            try:
                                client.table("meeting_archives").update({
                                    "client_name": edit_client.strip(),
                                    "meeting_date": edit_date.strip(),
                                    "location": edit_loc.strip(),
                                    "prepared_by": edit_prep.strip(),
                                    "confirmed_by": edit_conf.strip()
                                }).eq("meeting_id", m_id).execute()
                                
                                # Update locally in memory
                                active_meeting["client_name"] = edit_client.strip()
                                active_meeting["meeting_date"] = edit_date.strip()
                                active_meeting["location"] = edit_loc.strip()
                                active_meeting["prepared_by"] = edit_prep.strip()
                                active_meeting["confirmed_by"] = edit_conf.strip()

                                st.session_state["edit_meeting_details"] = False
                                st.success("Meeting details updated successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Metadata update failed: {e}")

    # Tabs (Matching Exact Image Styling)
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
