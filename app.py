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

/* --- Page Canvas & Padding --- */
.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
.block-container { 
    padding-top: 2rem !important; 
    padding-bottom: 3.5rem !important;
    padding-right: 3rem !important; 
    padding-left: 3rem !important;
    max-width: 100% !important;
}

html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp {
    background-color: #F6F3EC;
    background-image: radial-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 24px 24px;
    color: #1A1A1A;
}

/* --- Section Typography --- */
.section-title {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; 
    font-weight: 600 !important; 
    color: #1A2B4C !important; 
    font-size: 1.35rem !important;
    margin: 0 0 0.25rem 0 !important;
}
.section-caption {
    font-size: 0.82rem;
    color: #555E68;
    margin-bottom: 1.25rem;
}

/* --- KPI Cards --- */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2rem;
    margin-bottom: 2.25rem;
}
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 1.4rem 1rem;
    border: 1px solid rgba(0, 0, 0, 0.07);
    border-bottom: 3.5px solid #22252A;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
    text-align: center;
    transition: all 0.2s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    border-bottom-color: #111315;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
}
.kpi-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #555E68;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 2.35rem;
    font-weight: 600;
    color: #1A2B4C;
    line-height: 1.1;
    margin: 0;
}

/* --- Streamlit Container Panels --- */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    padding: 1.85rem !important;
}

/* --- Buttons --- */
.stButton > button {
    background-color: #22252A !important;
    color: #FFFFFF !important;
    border: 1px solid #111315 !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.03em;
    padding: 0.4rem 1.1rem !important;
    min-height: 36px !important;
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
    border-radius: 10px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.gallery-title { 
    font-family: 'Playfair Display', serif; 
    font-style: italic; 
    font-size: 1.1rem; 
    font-weight: 600;
    color: #1A2B4C; 
    margin: 0 0 0.2rem 0; 
}
.gallery-sub { 
    font-size: 0.75rem; 
    color: #6C727A; 
    margin-bottom: 0.6rem; 
    font-weight: 500;
}
.gallery-desc { 
    font-size: 0.82rem; 
    color: #2D2D2D; 
    line-height: 1.5; 
    margin: 0;
}

/* --- Chat Overrides & High-Contrast Typography --- */
div[data-testid="stChatMessage"] {
    background-color: transparent !important;
    padding: 0.4rem 0 !important;
}

/* Assistant Message Bubble */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #FAF8F5 !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-left: 4px solid #22252A !important;
    border-radius: 0 10px 10px 0 !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 1rem !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) div[data-testid="stMarkdownContainer"] * {
    color: #1A1A1A !important;
}

/* User Message Bubble */
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
    background-color: #22252A !important;
    border-radius: 12px 12px 2px 12px !important;
    padding: 0.85rem 1.25rem !important;
    margin-bottom: 1rem !important;
    margin-left: auto !important;
    max-width: 82% !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
}
div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) div[data-testid="stMarkdownContainer"] * {
    color: #FFFFFF !important;
    font-weight: 500 !important;
}

/* Modern Chat Tables */
div[data-testid="stChatMessage"] table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 0.8rem 0 !important;
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
    padding: 8px 12px !important;
    border-bottom: 1px solid #E5E7EB !important;
    font-size: 0.8rem !important;
}
div[data-testid="stChatMessage"] td {
    padding: 8px 12px !important;
    border-bottom: 1px solid #F3F4F6 !important;
    color: #2D2D2D !important;
    font-size: 0.8rem !important;
}

/* Compact Bottom Date Picker Popover */
div[data-testid="stPopover"] > button {
    background-color: #FFFFFF !important;
    color: #22252A !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 6px !important;
    padding: 0.25rem 0.65rem !important;
    font-size: 0.76rem !important;
    min-height: 30px !important;
    height: 30px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
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
        "Ask follow-up questions when useful."
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

# 6. KPI Metrics Grid
st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card"><div class="kpi-title">Meetings (Selected)</div><div class="kpi-value">{total_range_meetings}</div></div>
    <div class="kpi-card"><div class="kpi-title">Total Team Meetings</div><div class="kpi-value">{total_team_meetings}</div></div>
    <div class="kpi-card"><div class="kpi-title">Total Internal</div><div class="kpi-value">{total_internal_meetings}</div></div>
    <div class="kpi-card"><div class="kpi-title">Total External</div><div class="kpi-value">{total_external_meetings}</div></div>
</div>
""", unsafe_allow_html=True)

# 7. Main Content Panels
col_left, col_right = st.columns([1, 1.4], gap="large")

with col_left:
    with st.container(height=650, border=True):
        st.markdown('<p class="section-title">Recent Meetings</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Browse archived meetings for the selected window.</p>', unsafe_allow_html=True)
        
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
                    <p class="gallery-desc">{summary[:110]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Meeting Details", key=f"btn_view_{m_id}_{idx}", use_container_width=True):
                    st.session_state["selected_meeting_id"] = m_id
                    st.switch_page("pages/2_meeting_details.py")
                st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)
        else:
            st.info("No meeting archives found for the selected date range.")

with col_right:
    with st.container(height=650, border=True):
        st.markdown('<p class="section-title">Ask Echo — Global Intelligence</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-caption">Synthesize stored meeting transcripts, action items, and records.</p>', unsafe_allow_html=True)

        chat_history_container = st.container(height=460)
        with chat_history_container:
            if not st.session_state["global_chat_history"]:
                with st.chat_message("assistant"):
                    st.markdown("**System Online:** Hello. I am Echo. Ask me anything across your entire meeting archive.")
            else:
                for msg in st.session_state["global_chat_history"]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        if global_query := st.chat_input("Ask Echo a question..."):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing meeting archives..."):
                ans = query_global_team_archive(global_query, supabase_records, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()

# 8. Bottom Date Filter Bar (Compact & Integrated Reset)
st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
foot_l, foot_r = st.columns([3, 1])

with foot_r:
    date_label = f"{st.session_state['start_date'].strftime('%b %d, %Y')} — {st.session_state['end_date'].strftime('%b %d, %Y')}"
    
    with st.popover(f"Filter: {date_label}", use_container_width=True):
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
