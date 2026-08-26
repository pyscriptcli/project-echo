import os
import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from components.navigation import render_global_navigation

# ========== CONFIG ==========
st.set_page_config(
    page_title="Project Echo - Meeting Details",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render Global Navigation
render_global_navigation()

# ========== SUPABASE SETUP ==========
SUPABASE_URL = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL[:-8]
SUPABASE_KEY = "".join(str(st.secrets.get("SUPABASE_KEY", "")).split())

@st.cache_resource
def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

def get_all_meetings():
    client = init_supabase()
    if not client:
        return []
    try:
        resp = client.table("meeting_archives").select("*").order("meeting_date", desc=True).execute()
        return resp.data if resp and resp.data else []
    except Exception:
        return []

def update_meeting_archive(meeting_id, updated_table_items, updated_summary):
    client = init_supabase()
    if not client:
        return False, "Supabase client uninitialized."
    try:
        client.table("meeting_archives").update({
            "table_items": updated_table_items,
            "summary_md": updated_summary
        }).eq("meeting_id", meeting_id).execute()
        return True, "Meeting record updated successfully!"
    except Exception as e:
        return False, str(e)

# ========== CUSTOM CSS ==========
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

.stApp {
    background-color: #F3EFE6; 
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

.stApp > header { display: none !important; }

/* Let Streamlit handle left padding dynamically to prevent overlap/gaps */
.block-container { 
    padding-top: 5.5rem !important;
    padding-right: 2rem !important;
}

.echo-topbar-wrapper {
    position: fixed; top: 0; left: 0; right: 0; height: 60px;
    background-color: #161616;
    border-bottom: 1px solid #333333;
    z-index: 999990; box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    display: flex; align-items: center; justify-content: flex-start;
    padding: 0 2rem;
}

.echo-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; font-weight: 400 !important;
    font-size: 1.35rem !important; color: #FFFFFF !important; margin: 0 !important;
}
.echo-title span { color: #D4AF37 !important; }

h3 {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; font-weight: 400 !important; 
    color: #1A2B4C !important; letter-spacing: 0.02em; margin-bottom: 0.25rem; font-size: 1.25rem !important;
}

.playfair-label {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    color: #1A2B4C !important;
    font-size: 1.05rem !important;
    margin-bottom: 0.25rem !important;
    display: block;
}

/* ========== ROBUST SIDEBAR STYLING ========== */
section[data-testid="stSidebar"] {
    background-color: #161616 !important;
    border-right: 1px solid #2B2B2B !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.2) !important;
    z-index: 999995 !important;
}

/* CRITICAL: Make the collapse/expand button ALWAYS visible and styled */
button[data-testid="stSidebarCollapseButton"] {
    display: flex !important; 
    position: absolute !important;
    bottom: 24px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    background-color: #222222 !important;
    border: 1px solid #333333 !important;
    border-radius: 50% !important;
    color: #C5A059 !important;
    padding: 0 !important;
    margin: 0 !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    z-index: 999999 !important;
}

button[data-testid="stSidebarCollapseButton"]:hover {
    background-color: #D4AF37 !important;
    border-color: #D4AF37 !important;
    color: #161616 !important;
}

button[data-testid="stSidebarCollapseButton"] svg {
    color: #C5A059 !important;
    width: 20px !important;
    height: 20px !important;
}

button[data-testid="stSidebarCollapseButton"]:hover svg {
    color: #161616 !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding: 1.2rem 0 !important;
    gap: 1.1rem !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}

section[data-testid="stSidebar"] a {
    width: 44px !important;
    height: 44px !important;
    min-height: 44px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 10px !important;
    background-color: #222222 !important;
    border: 1px solid #333333 !important;
    color: #ECE9DF !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] a span[data-testid="stPageLink-Text"] { display: none !important; }
section[data-testid="stSidebar"] a span[data-testid="stIconMaterial"] { font-size: 1.4rem !important; color: #C5A059 !important; }

section[data-testid="stSidebar"] a:hover { background-color: #D4AF37 !important; border-color: #D4AF37 !important; }
section[data-testid="stSidebar"] a:hover span[data-testid="stIconMaterial"] { color: #161616 !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}

.stTextArea textarea, .stTextInput input, div[data-baseweb="select"] > div {
    background-color: #FAFAFA !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus, div[data-baseweb="select"] > div:focus-within {
    background-color: #FFFFFF !important;
    border-color: #D4AF37 !important;
}

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

button[key^="del_"] {
    background-color: #FDF9F9 !important;
    color: #B23A3A !important;
    border: 1px solid rgba(178, 58, 58, 0.25) !important;
}
button[key^="del_"]:hover {
    background-color: #B23A3A !important;
    color: #FFFFFF !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="echo-topbar-wrapper">
 <h1 class="echo-title">Project <span>Echo</span> &mdash; Meeting Details</h1>
</div>
""", unsafe_allow_html=True)

# ========== MEETING SELECTION ==========
meetings = get_all_meetings()

if not meetings:
    st.info("No meeting records found in Supabase.")
    st.stop()

# Build dropdown mapping
meeting_map = {f"{m.get('client_name', 'Client')} ({str(m.get('meeting_date', ''))[:10]}) - {m.get('meeting_id')}": m for m in meetings}

# Auto-select based on session state (from Dashboard gallery click)
default_idx = 0
selected_id = st.session_state.get("selected_meeting_id")
if selected_id:
    for idx, (label, m) in enumerate(meeting_map.items()):
        if str(m.get("meeting_id")) == str(selected_id):
            default_idx = idx
            break

sel_label = st.selectbox("Select Meeting to Inspect", options=list(meeting_map.keys()), index=default_idx)
selected_meeting = meeting_map[sel_label]
m_id = selected_meeting.get("meeting_id")

# ========== MEETING DETAILS CARD ==========
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

# ========== FULL TRANSCRIPT ==========
raw_transcript = selected_meeting.get("transcript_md", "No transcript stored.")
with st.expander("Full Transcript (Click to Expand)", expanded=False):
    st.text_area(
        "Full Transcript", 
        value=raw_transcript.replace("### Transcript", "").strip(), 
        height=260, 
        disabled=True, 
        label_visibility="collapsed"
    )

# ========== MINUTES OF MEETING INTERACTIVE EDITOR ==========
with st.container(border=True):
    st.markdown("<h3>Minutes of Meeting Editor</h3>", unsafe_allow_html=True)
    st.caption("Edit action items and discussion points inline. Changes are saved to Supabase when you click 'Save All Changes'.")
    
    # Initialize session state for this specific meeting's editor
    editor_key = f"editor_df_{m_id}"
    if editor_key not in st.session_state:
        raw_items = selected_meeting.get("table_items", [])
        if isinstance(raw_items, list) and len(raw_items) > 0:
            st.session_state[editor_key] = pd.DataFrame(raw_items)
        else:
            st.session_state[editor_key] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
    
    df = st.session_state[editor_key].copy().reset_index(drop=True)
    
    # Ensure all required columns exist
    for col in ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]:
        if col not in df.columns:
            df[col] = ""

    row_to_delete = None
    
    # Render rows
    for idx in range(len(df)):
        with st.container(border=True):
            c_disc, c_act, c_date, c_pic, c_del = st.columns([3.2, 3.2, 1.8, 1.8, 0.6])
            with c_disc:
                st.markdown('<span class="playfair-label">Discussion Points</span>', unsafe_allow_html=True)
                st.text_area("DP", value=str(df.at[idx, "Discussion Points"]), key=f"md_dp_{idx}", height=75, label_visibility="collapsed")
            with c_act:
                st.markdown('<span class="playfair-label">Action Plan</span>', unsafe_allow_html=True)
                st.text_area("AP", value=str(df.at[idx, "Action Plan"]), key=f"md_ap_{idx}", height=75, label_visibility="collapsed")
            with c_date:
                st.markdown('<span class="playfair-label">Delivery Date</span>', unsafe_allow_html=True)
                st.text_area("DD", value=str(df.at[idx, "Indicative Delivery Date"]), key=f"md_date_{idx}", height=75, label_visibility="collapsed")
            with c_pic:
                st.markdown('<span class="playfair-label">Person-in-charge</span>', unsafe_allow_html=True)
                st.text_area("PIC", value=str(df.at[idx, "Person-in-charge"]), key=f"md_pic_{idx}", height=75, label_visibility="collapsed")
            with c_del:
                st.write("<div style='height: 38px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_md_{idx}", help="Delete Row"):
                    row_to_delete = idx

    # Handle Deletion
    if row_to_delete is not None:
        df = df.drop(index=row_to_delete).reset_index(drop=True)
        st.session_state[editor_key] = df
        st.rerun()

    # Collect updated values from session state
    rows_data = []
    for idx in range(len(df)):
        rows_data.append({
            "Discussion Points": st.session_state.get(f"md_dp_{idx}", df.at[idx, "Discussion Points"]),
            "Action Plan": st.session_state.get(f"md_ap_{idx}", df.at[idx, "Action Plan"]),
            "Indicative Delivery Date": st.session_state.get(f"md_date_{idx}", df.at[idx, "Indicative Delivery Date"]),
            "Person-in-charge": st.session_state.get(f"md_pic_{idx}", df.at[idx, "Person-in-charge"])
        })

    # Add Item Button
    add_c1, _ = st.columns([2, 8])
    with add_c1:
        if st.button("+ Add Item", key="btn_add_item_md"):
            rows_data.append({
                "Discussion Points": "", 
                "Action Plan": "", 
                "Indicative Delivery Date": "", 
                "Person-in-charge": ""
            })
            st.session_state[editor_key] = pd.DataFrame(rows_data)
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
        if st.button("💾 Save All Changes", key="btn_save_updates", type="primary"):
            with st.spinner("Saving to Supabase..."):
                ok, msg = update_meeting_archive(m_id, rows_data, f"### Summary\n{summary_val}")
                if ok:
                    st.success(msg)
                    # Clear editor state to force reload of fresh data on next interaction
                    if editor_key in st.session_state:
                        del st.session_state[editor_key]
                else:
                    st.error(f"Update failed: {msg}")
