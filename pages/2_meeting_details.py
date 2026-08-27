import streamlit as st
import pandas as pd
from utils.db import fetch_meeting_archives, get_supabase_client

# 1. Page Config
st.set_page_config(
    page_title="Project Echo - Meeting Details",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. SVG Icons (No Emojis)
TRASH_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="vertical-align: middle;"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>'
SAVE_ICON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="vertical-align: middle; margin-right: 6px;"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>'

# 3. Custom CSS (Topbar removed, UI preserved)
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

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: #161616 !important; border-right: 1px solid #2B2B2B !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.2) !important; z-index: 999995 !important;
}
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important; position: absolute !important; bottom: 24px !important; left: 50% !important;
    transform: translateX(-50%) !important; width: 40px !important; height: 40px !important;
    background-color: #222222 !important; border: 1px solid #333333 !important; border-radius: 50% !important;
    color: #C5A059 !important; transition: all 0.2s ease !important; z-index: 999999 !important;
}
button[data-testid="stSidebarCollapseButton"]:hover { background-color: #D4AF37 !important; color: #161616 !important; }
section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
    width: 48px !important; height: 48px !important; padding: 0 !important; display: flex !important;
    align-items: center !important; justify-content: center !important; border-radius: 10px !important;
    background-color: #222222 !important; border: 1px solid #333333 !important; transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover { background-color: #D4AF37 !important; }
section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] { display: none !important; }
section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stIconMaterial"] { font-size: 1.5rem !important; color: #C5A059 !important; }
section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover span[data-testid="stIconMaterial"] { color: #161616 !important; }

/* Containers & Inputs */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; padding: 1.5rem !important; margin-bottom: 1.25rem !important;
}
.stTextArea textarea, .stTextInput input {
    background-color: #FAFAFA !important; border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    background-color: #FFFFFF !important; border-color: #D4AF37 !important;
}

/* Buttons */
.stButton > button {
    background-color: #222222 !important; color: #FFFFFF !important; border: none !important; 
    border-radius: 50px !important; font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important; font-size: 0.82rem !important; height: 36px !important; 
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important; transition: all 0.2s ease !important; width: 100% !important;
}
.stButton > button:hover { background-color: #D4AF37 !important; color: #161616 !important; }
.stButton > button[key^="del_"] {
    background-color: #FDF9F9 !important; color: #B23A3A !important; border: 1px solid rgba(178, 58, 58, 0.25) !important;
}
.stButton > button[key^="del_"]:hover { background-color: #B23A3A !important; color: #FFFFFF !important; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 4. Data Fetching
meetings = fetch_meeting_archives(limit=500)

if not meetings:
    st.info("No meeting records found in Supabase.")
    st.stop()

# 5. Meeting Selection Logic
meeting_map = {f"{m.get('client_name', 'Client')} ({str(m.get('meeting_date', ''))[:10]}) - {m.get('meeting_id')}": m for m in meetings}

default_idx = 0
selected_id = st.session_state.get("selected_meeting_id")
if selected_id:
    for idx, label in enumerate(meeting_map.keys()):
        if str(meeting_map[label].get("meeting_id")) == str(selected_id):
            default_idx = idx
            break

sel_label = st.selectbox("Select Meeting to Inspect", options=list(meeting_map.keys()), index=default_idx)
selected_meeting = meeting_map[sel_label]
m_id = selected_meeting.get("meeting_id")

# 6. Meeting Details Card
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

# 7. Full Transcript
raw_transcript = selected_meeting.get("transcript_md", "No transcript stored.")
with st.expander("Full Transcript (Click to Expand)", expanded=False):
    st.text_area(
        "Full Transcript", 
        value=raw_transcript.replace("### Transcript", "").strip(), 
        height=260, 
        disabled=True, 
        label_visibility="collapsed"
    )

# 8. Minutes of Meeting Interactive Editor (Bug-Free State Logic)
with st.container(border=True):
    st.markdown("<h3>Minutes of Meeting Editor</h3>", unsafe_allow_html=True)
    st.caption("Edit action items and discussion points inline. Changes are saved to Supabase when you click 'Save All Changes'.")
    
    editor_key = f"mom_rows_{m_id}"
    
    # Initialize state with list of dicts (prevents DataFrame index-shifting bugs)
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
                if st.button(TRASH_ICON, key=f"del_{m_id}_{idx}", help="Delete Row"):
                    continue  # Skip adding this row to rows_to_keep
            
            # Capture updated values for rows that were NOT deleted
            rows_to_keep.append({
                "Discussion Points": st.session_state[f"dp_{m_id}_{idx}"],
                "Action Plan": st.session_state[f"ap_{m_id}_{idx}"],
                "Indicative Delivery Date": st.session_state[f"date_{m_id}_{idx}"],
                "Person-in-charge": st.session_state[f"pic_{m_id}_{idx}"]
            })

    # If a row was deleted, update state and rerun to prevent index mismatch
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
    sv_col1, sv_col2 = st.columns([8, 2])
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
                        # Clear editor state to force reload of fresh data
                        if editor_key in st.session_state:
                            del st.session_state[editor_key]
                    except Exception as e:
                        st.error(f"Update failed: {e}")
