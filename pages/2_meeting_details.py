import streamlit as st
import pandas as pd
from datetime import datetime
from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout

# 1. Page Config
st.set_page_config(
    page_title="Project Echo - Meeting Details",
    layout="wide",
    initial_sidebar_state="expanded"
)
setup_page_layout()


# 2. Custom CSS (Sidebar styling removed - handled globally by app.py)
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
.block-container { padding-top: 2rem !important; padding-right: 2rem !important; }

h3 {
    font-family: 'Playfair Display', serif !important; font-style: italic !important; font-weight: 400 !important; 
    color: #1A2B4C !important; letter-spacing: 0.02em; margin-bottom: 0.25rem; font-size: 1.25rem !important;
}
.playfair-label {
    font-family: 'Playfair Display', serif !important; font-style: italic !important;
    color: #1A2B4C !important; font-size: 1.05rem !important; margin-bottom: 0.25rem !important; display: block;
}

/* Containers & Inputs */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}
.stTextArea textarea, .stTextInput input, [data-baseweb="input"] {
    background-color: #FAFAFA !important; 
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important; 
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    background-color: #FFFFFF !important; 
    border-color: #D4AF37 !important;
}

/* Buttons */
.stButton > button, div[data-testid="stPopover"] > button {
    background-color: #222222 !important; 
    color: #FFFFFF !important; 
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; 
    font-size: 0.82rem !important; 
    height: 38px !important; 
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important; 
    transition: all 0.2s ease !important; 
    width: 100% !important;
}
.stButton > button:hover, div[data-testid="stPopover"] > button:hover { 
    background-color: #D4AF37 !important; 
    color: #161616 !important; 
}
.stButton > button[key^="del_"] {
    background-color: #FDF9F9 !important; 
    color: #B23A3A !important; 
    border: 1px solid rgba(178, 58, 58, 0.25) !important;
}
.stButton > button[key^="del_"]:hover { 
    background-color: #B23A3A !important; 
    color: #FFFFFF !important; 
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 4. SVG Icons (No Emojis)
TRASH_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="vertical-align: middle; margin-right: 4px;"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>'
SAVE_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="vertical-align: middle; margin-right: 6px;"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>'

# 5. Data Fetching
meetings = fetch_meeting_archives(limit=500)

if not meetings:
    st.info("No meeting records found in Supabase.")
    st.stop()

# Helper function to extract normalized YYYY-MM-DD
def get_iso_date(meeting_item):
    raw_d = str(meeting_item.get("meeting_date", ""))
    return raw_d[:10] if len(raw_d) >= 10 else ""

meeting_dates = sorted(list({get_iso_date(m) for m in meetings if get_iso_date(m)}), reverse=True)

# 6. Search & Calendar Filter Bar
with st.container(border=True):
    st.markdown("<h3>Find & Inspect Meeting</h3>", unsafe_allow_html=True)
    
    col_search, col_cal, col_reset = st.columns([7.5, 1.2, 1.3])
    
    with col_search:
        search_query = st.text_input(
            "Search Meetings",
            placeholder="Search by client, ID, topic, transcript, PIC...",
            label_visibility="collapsed",
            key="meeting_search_query"
        )
    
    with col_cal:
        with st.popover(":material/calendar_month:", help="Filter by Date"):
            st.markdown("**Select Meeting Date**")
            
            if meeting_dates:
                st.caption("Active meeting dates:")
                st.markdown(" ".join([f"`• {d}`" for d in meeting_dates[:6]]))
            
            picked_date = st.date_input("Meeting Date", value=None, key="calendar_date_picker")
            if picked_date:
                st.session_state["selected_iso_date"] = picked_date.strftime("%Y-%m-%d")
                
    with col_reset:
        if st.button("Clear", help="Clear all search filters"):
            st.session_state["meeting_search_query"] = ""
            st.session_state["selected_iso_date"] = None
            st.session_state["selected_meeting_id"] = None
            st.rerun()

# 7. Filtering Logic
filtered_meetings = meetings

# Filter by selected date
active_date_filter = st.session_state.get("selected_iso_date")
if active_date_filter:
    filtered_meetings = [m for m in filtered_meetings if get_iso_date(m) == active_date_filter]

# Filter by keyword query
if search_query:
    q = search_query.lower()
    def matches(m):
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
        return q in searchable_corpus
    
    filtered_meetings = [m for m in filtered_meetings if matches(m)]

if not filtered_meetings:
    st.warning("No meetings found matching your search or date criteria.")
    st.stop()

# Determine selected meeting automatically or via matching chips
selected_id = st.session_state.get("selected_meeting_id")
valid_ids = [m.get("meeting_id") for m in filtered_meetings]

if selected_id not in valid_ids:
    selected_meeting = filtered_meetings[0]
    st.session_state["selected_meeting_id"] = selected_meeting.get("meeting_id")
else:
    selected_meeting = next(m for m in filtered_meetings if m.get("meeting_id") == selected_id)

m_id = selected_meeting.get("meeting_id")

# Multi-result quick chips
if len(filtered_meetings) > 1:
    st.caption(f"Showing **{len(filtered_meetings)}** matching meetings. Select one:")
    chip_cols = st.columns(min(len(filtered_meetings), 4))
    for idx, m in enumerate(filtered_meetings):
        with chip_cols[idx % min(len(filtered_meetings), 4)]:
            chip_label = f"{m.get('client_name', 'Client')} ({get_iso_date(m)})"
            is_current = (m.get("meeting_id") == m_id)
            btn_type = "primary" if is_current else "secondary"
            if st.button(chip_label, key=f"chip_{m.get('meeting_id')}", type=btn_type):
                st.session_state["selected_meeting_id"] = m.get("meeting_id")
                st.rerun()

# 8. Meeting Details Card
with st.container(border=True):
    st.markdown("<h3>Meeting Details</h3>", unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        st.write(f"**Client / Company:** {selected_meeting.get('client_name', 'N/A')}")
        st.write(f"**Meeting Date:** {selected_meeting.get('meeting_date', 'N/A')}")
    with d2:
        st.write(f"**Location:** {selected_meeting.get('location', 'N/A')}")
        st.write(f"**Prepared by:** {selected_meeting.get('prepared_by', 'N/A')}")
    with d3:
        st.write(f"**Confirmed by:** {selected_meeting.get('confirmed_by', 'N/A')}")
        st.write(f"**Meeting ID:** `{m_id}`")

# 9. Full Transcript
raw_transcript = selected_meeting.get("transcript_md", "No transcript stored.")
with st.expander("Full Transcript (Click to Expand)", expanded=False):
    st.text_area(
        "Full Transcript", 
        value=raw_transcript.replace("### Transcript", "").strip(), 
        height=260, 
        disabled=True, 
        label_visibility="collapsed"
    )

# 10. Minutes of Meeting Interactive Editor
with st.container(border=True):
    st.markdown("<h3>Minutes of Meeting Editor</h3>", unsafe_allow_html=True)
    st.caption("Edit action items and discussion points inline. Changes are saved to Supabase when you click 'Save All Changes'.")
    
    editor_key = f"mom_rows_{m_id}"
    
    if editor_key not in st.session_state:
        raw_items = selected_meeting.get("table_items", [])
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
                if st.button(f"{TRASH_ICON} Delete", key=f"del_{m_id}_{idx}", help="Delete Row"):
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

    # Add Item Button
    add_c1, _ = st.columns([2, 8])
    with add_c1:
        if st.button("+ Add Item", key=f"btn_add_{m_id}"):
            rows_to_keep.append({
                "Discussion Points": "", "Action Plan": "", 
                "Indicative Delivery Date": "", "Person-in-charge": ""
            })
            st.session_state[editor_key] = rows_to_keep
            st.rerun()

    # Summary / Other Discussions
    st.markdown('<span class="playfair-label" style="margin-top:0.75rem;">Summary & Other Discussions</span>', unsafe_allow_html=True)
    current_summary = str(selected_meeting.get("summary_md", "")).replace("### Summary", "").strip()
    summary_val = st.text_area(
        "Summary Content",
        value=current_summary,
        height=100,
        label_visibility="collapsed",
        key=f"summary_{m_id}"
    )

    # Save Updates
    st.write("")
    sv_col1, sv_col2 = st.columns([7.5, 2.5])
    with sv_col2:
        if st.button(f"{SAVE_ICON} Save All Changes", key=f"btn_save_{m_id}", type="primary"):
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
