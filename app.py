import sys
import os
import calendar
import datetime
import json
import requests
import pandas as pd
import streamlit as st

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout

# 1. Page Configuration
st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

setup_page_layout()

# 2. Global & Dashboard CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,400;1,500;1,600&family=Cormorant+Garamond:wght@400;500;600;700&display=swap');

/* --- Page Canvas & Spacing --- */
.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
.block-container { 
    padding-top: 1.5rem !important; 
    padding-bottom: 2rem !important;
    padding-right: 2.5rem !important; 
    padding-left: 2.5rem !important;
    max-width: 100% !important;
}

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp {
    background-color: #F7F5F0;
    background-image: radial-gradient(rgba(0, 0, 0, 0.035) 1px, transparent 1px);
    background-size: 24px 24px;
    color: #1A1A1A;
}

/* --- Section Typography --- */
.section-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; 
    font-weight: 600 !important; 
    color: #1A2B4C !important; 
    font-size: 1.25rem !important;
    margin: 0 0 0.15rem 0 !important;
}
.section-caption {
    font-size: 0.8rem;
    color: #555E68;
    margin-bottom: 0.85rem;
}

/* --- Compact Left Column Metrics --- */
.kpi-column {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    margin-bottom: 1.25rem;
}
.kpi-card {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 0.65rem 0.9rem;
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-left: 4px solid #22252A;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.2s ease;
}
.kpi-card:hover {
    border-left-color: #111315;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.kpi-title {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #555E68;
    margin: 0;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.45rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    line-height: 1;
}

/* --- Streamlit Container Panels --- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.025) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    padding: 1.4rem !important;
}

/* --- Buttons --- */
.stButton > button {
    background-color: #22252A !important;
    color: #FFFFFF !important;
    border: 1px solid #111315 !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.02em;
    padding: 0.35rem 0.9rem !important;
    min-height: 32px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #111315 !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
}

/* --- Meeting Card Feed --- */
.gallery-card {
    background-color: #FAF8F5;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 8px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.4rem;
}
.gallery-title { 
    font-family: 'Playfair Display', serif; 
    font-style: italic; 
    font-size: 1.05rem; 
    font-weight: 600;
    color: #1A2B4C; 
    margin: 0 0 0.15rem 0; 
}
.gallery-sub { 
    font-size: 0.72rem; 
    color: #6C727A; 
    margin-bottom: 0.45rem; 
    font-weight: 500;
}
.gallery-desc { 
    font-size: 0.8rem; 
    color: #2D2D2D; 
    line-height: 1.45; 
    margin: 0;
}

/* --- Chat Overrides --- */
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 0.3rem 0 !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #FAF8F5 !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-left: 4px solid #22252A !important;
    border-radius: 0 8px 8px 0 !important;
    padding: 0.9rem 1.15rem !important;
    margin-bottom: 0.85rem !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) div[data-testid="stMarkdownContainer"] * {
    color: #1A1A1A !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #22252A !important;
    border-radius: 10px 10px 2px 10px !important;
    padding: 0.75rem 1.15rem !important;
    margin-bottom: 0.85rem !important;
    margin-left: auto !important;
    max-width: 82% !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stMarkdownContainer"] * {
    color: #FFFFFF !important;
    font-weight: 500 !important;
}

/* Chat Tables */
div[data-testid="stChatMessage"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 0.75rem 0 !important;
    background-color: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}
div[data-testid="stChatMessage"] th {
    background-color: #F1EFE9 !important;
    color: #1A2B4C !important;
    font-weight: 600 !important;
    text-align: left !important;
    padding: 7px 10px !important;
    border-bottom: 1px solid #E5E7EB !important;
    font-size: 0.78rem !important;
}
div[data-testid="stChatMessage"] td {
    padding: 7px 10px !important;
    border-bottom: 1px solid #F3F4F6 !important;
    color: #2D2D2D !important;
    font-size: 0.78rem !important;
}

/* Compact Bottom Date Picker Popover */
div[data-testid="stPopover"] > button {
    background-color: #FFFFFF !important;
    color: #22252A !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 6px !important;
    padding: 0.25rem 0.65rem !important;
    font-size: 0.75rem !important;
    min-height: 28px !important;
    height: 28px !important;
}
div[data-testid="stPopover"] > button:hover {
    border-color: #22252A !important;
    background-color: #FAF8F5 !important;
}
</style>
""", unsafe_allow_html=True)

# 3. Global Session State
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.datetime.now().date()

if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# 4. Global AI Query Function
def query_global_team_archive(question, archive_records, chat_history):
    DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not DEEPSEEK_API_KEY:
        return "DeepSeek API Key is missing. Please add it to your Streamlit Cloud Secrets."
    
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)
    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Answer user questions accurately by synthesizing past meeting records. "
        "Format responses cleanly in Markdown using bullet points and Markdown tables where appropriate. "
        "Do not use emojis; use standard text formatting. Ask follow-up questions when useful."
    )
    messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:28000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})
    payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.2, "max_tokens": 750}
    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"Service Notice ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"

# 5. Fetch and Filter Data
supabase_records = fetch_meeting_archives(limit=100)

total_team_meetings = len(supabase_records)
total_range_meetings = 0
total_internal_meetings = 0
total_external_meetings = 0
filtered_records = []

for m in supabase_records:
    m_date_raw = str(m.get("meeting_date", ""))
    try:
        parsed_d = datetime.datetime.strptime(m_date_raw[:10], "%Y-%m-%d").date()
        if st.session_state["start_date"] <= parsed_d <= st.session_state["end_date"]:
            filtered_records.append(m)
            total_range_meetings += 1
            
            client_name_str = str(m.get("client_name", "")).strip().lower()
            raw_payload = m.get("raw_payload", {}) or {}
            meeting_details_dict = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
            external_atts = meeting_details_dict.get("external_attendees", [])
            
            if "internal" in client_name_str or "prime" in client_name_str or (not external_atts and not client_name_str):
                total_internal_meetings += 1
            else:
                total_external_meetings += 1
    except Exception:
        pass

# 6. Optimized Split Workspace Layout
col_left, col_right = st.columns([1, 2.1], gap="large")

with col_left:
    with st.container(height=700, border=True):
        st.markdown('<p class="section-title">Overview & Metrics</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Summary of records in selected scope.</p>', unsafe_allow_html=True)
        
        # Vertical KPI summary stack
        st.markdown(f"""
        <div class="kpi-column">
            <div class="kpi-card"><span class="kpi-title">In Selected Range</span><span class="kpi-value">{total_range_meetings}</span></div>
            <div class="kpi-card"><span class="kpi-title">Total Team Archive</span><span class="kpi-value">{total_team_meetings}</span></div>
            <div class="kpi-card"><span class="kpi-title">Internal Meetings</span><span class="kpi-value">{total_internal_meetings}</span></div>
            <div class="kpi-card"><span class="kpi-title">External Meetings</span><span class="kpi-value">{total_external_meetings}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-title" style="margin-top: 1rem !important;">Recent Meetings</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Scroll to explore filtered meetings.</p>', unsafe_allow_html=True)
        
        feed_container = st.container(height=260)
        with feed_container:
            if filtered_records:
                for idx, m in enumerate(filtered_records):
                    m_id = m.get("meeting_id") or f"MOM-{idx}"
                    client = m.get("client_name") or "Meeting Record"
                    m_date = str(m.get("meeting_date", "N/A"))[:10]
                    prep = m.get("prepared_by") or "CRD Team"
                    summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                    
                    st.markdown(f"""
                    <div class="gallery-card">
                        <p class="gallery-title">{client}</p>
                        <p class="gallery-sub">{m_date} &bull; {prep}</p>
                        <p class="gallery-desc">{summary[:95]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("View Meeting", key=f"btn_view_{m_id}_{idx}", use_container_width=True):
                        st.session_state["selected_meeting_id"] = m_id
                        st.switch_page("pages/2_meeting_details.py")
                    st.markdown("<div style='margin-bottom: 0.6rem;'></div>", unsafe_allow_html=True)
            else:
                st.info("No records found.")

with col_right:
    with st.container(height=700, border=True):
        st.markdown('<p class="section-title">Ask Echo — Global Intelligence</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Synthesize meeting archives, transcripts, and action logs.</p>', unsafe_allow_html=True)

        chat_history_container = st.container(height=525)
        with chat_history_container:
            if not st.session_state["global_chat_history"]:
                with st.chat_message("assistant", avatar="utils/assistant_icon.svg" if os.path.exists("utils/assistant_icon.svg") else None):
                    st.markdown("**System Online:** Hello. I am Echo. Ask me anything across your entire meeting archive.")
            else:
                for msg in st.session_state["global_chat_history"]:
                    avatar_path = ("utils/assistant_icon.svg" if os.path.exists("utils/assistant_icon.svg") else None) if msg["role"] == "assistant" else None
                    with st.chat_message(msg["role"], avatar=avatar_path):
                        st.markdown(msg["content"])

        if global_query := st.chat_input("Ask Echo a question..."):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing meeting archives..."):
                ans = query_global_team_archive(global_query, supabase_records, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()

# 7. Bottom Compact Date Picker with Embedded Reset
st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
foot_l, foot_r = st.columns([3.5, 1.2])

with foot_r:
    date_label = f"{st.session_state['start_date'].strftime('%b %d, %Y')} — {st.session_state['end_date'].strftime('%b %d, %Y')}"
    
    with st.popover(date_label, use_container_width=True):
        p_col1, p_col2 = st.columns([1.1, 1.9])
        
        with p_col1:
            st.caption("PRESETS")
            if st.button("This Week", key="btn_tw", use_container_width=True):
                st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday())
                st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                st.rerun()
            if st.button("Last Week", key="btn_lw", use_container_width=True):
                st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday() + 7)
                st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                st.rerun()
            if st.button("This Month", key="btn_tm", use_container_width=True):
                st.session_state["start_date"] = today.replace(day=1)
                _, last = calendar.monthrange(today.year, today.month)
                st.session_state["end_date"] = today.replace(day=last)
                st.rerun()
            if st.button("Last Month", key="btn_lm", use_container_width=True):
                first_this = today.replace(day=1)
                last_prev = first_this - datetime.timedelta(days=1)
                st.session_state["start_date"] = last_prev.replace(day=1)
                st.session_state["end_date"] = last_prev
                st.rerun()
                
            st.markdown("<div style='margin-top: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("Reset Range", key="btn_reset_inside", use_container_width=True):
                st.session_state["start_date"] = today.replace(day=1)
                _, last = calendar.monthrange(today.year, today.month)
                st.session_state["end_date"] = today.replace(day=last)
                st.rerun()

        with p_col2:
            st.caption("CUSTOM RANGE")
            selected_dates = st.date_input(
                "Date Range",
                value=(st.session_state["start_date"], st.session_state["end_date"]),
                label_visibility="collapsed"
            )
            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                if st.session_state["start_date"] != selected_dates[0] or st.session_state["end_date"] != selected_dates[1]:
                    st.session_state["start_date"] = selected_dates[0]
                    st.session_state["end_date"] = selected_dates[1]
                    st.rerun()
