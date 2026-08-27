import sys
import os
import calendar
import datetime

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import streamlit as st
import json
import requests
import pandas as pd
from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout

# 1. Page Configuration (MUST be first)
st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

setup_page_layout()

# 2. Global & Dashboard CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&family=Cormorant+Garamond:wght@400;500;600;700&display=swap');

/* --- GLOBAL: Hide Top Bar & Main Menu --- */
.stApp > header { display: none !important; visibility: hidden !important; }
#MainMenu { visibility: hidden !important; }
.block-container { padding-top: 1.5rem !important; padding-right: 1.5rem !important; padding-left: 1.5rem !important;}

/* --- GLOBAL: Sidebar Styling --- */
section[data-testid="stSidebar"] {
    background-color: #272828 !important;
    border-right: 1px solid #3a3a3a !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
    background-color: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    margin: 0.2rem 0.5rem !important;
    padding: 0.6rem 1rem !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
    background-color: rgba(201, 168, 76, 0.1) !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stPageLink-Text"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: #c9a84c !important;
    letter-spacing: 0.03em !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"] span[data-testid="stIconMaterial"] {
    color: #c9a84c !important;
    font-size: 1.4rem !important;
}

/* --- DASHBOARD SPECIFIC --- */
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp {
    background-color: #F3EFE6; 
    background-image: linear-gradient(rgba(0, 0, 0, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    color: #2D2D2D;
}

h3 {
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important; font-weight: 500 !important; 
    color: #1A2B4C !important; letter-spacing: 0.01em; margin-bottom: 0.15rem; font-size: 1.15rem !important;
}

/* 3D KPI Cards - Ultra Compact */
.kpi-card {
    background: linear-gradient(145deg, #ffffff, #f9f9f9);
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    box-shadow: 
        0px 6px 10px -3px rgba(0, 0, 0, 0.1), 
        0px 2px 4px -2px rgba(0, 0, 0, 0.05),
        inset 0px 1px 0px 0px rgba(255, 255, 255, 1);
    border: 1px solid rgba(0,0,0,0.06);
    border-bottom: 3px solid #222222;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    margin-bottom: 0.5rem;
}
.kpi-card:hover {
    transform: translateY(-2px);
    border-bottom-color: #c9a84c;
}
.kpi-title {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #777777;
    margin-bottom: 0rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 2.2rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    text-shadow: 1px 1px 1px rgba(0,0,0,0.05);
}

/* Containers with Depth */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: rgba(255, 255, 255, 0.6) !important; 
    backdrop-filter: blur(5px);
    border-radius: 10px !important;
    box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.04) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important; 
    padding: 1.2rem !important; 
}

/* Uniform Pill Buttons */
.stButton > button {
    background-color: #222222 !important; 
    color: #FFFFFF !important;
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.5px; 
    padding: 0.2rem 1rem !important;
    min-height: 32px !important;
    height: 32px !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important; 
}
.stButton > button:hover {
    background-color: #D4AF37 !important;
    color: #161616 !important;
    transform: translateY(-1px);
}

/* Compact Gallery Item Card */
.gallery-card {
    background-color: #FFFFFF;
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 8px;
    padding: 0.8rem;
    margin-bottom: 0.6rem;
}
.gallery-title { font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.05rem; color: #1A2B4C; margin: 0 0 0.1rem 0; }
.gallery-sub { font-size: 0.75rem; color: #777; margin-bottom: 0.3rem; }
.gallery-desc { font-size: 0.8rem; color: #333; line-height: 1.3; }

/* AI Chat Styling - Enhanced for Visual Hierarchy */
.chat-container { display: flex; flex-direction: column; gap: 0.8rem; margin-top: 0.5rem; padding-bottom: 1rem; }
.chat-ai { 
    align-self: flex-start; 
    background: linear-gradient(to right, #ffffff, #f0f4f8);
    border-left: 3px solid #D4AF37;
    color: #1A1A1A; 
    padding: 0.8rem 1rem; 
    border-radius: 0 8px 8px 8px;
    max-width: 92%; 
    font-size: 0.85rem; 
    line-height: 1.5; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.03);
}
.chat-user-wrap { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 0.2rem; }
.chat-user { 
    background-color: #222222; 
    color: #FFFFFF; 
    padding: 0.6rem 1rem; 
    border-radius: 12px 12px 0 12px; 
    max-width: 80%; 
    font-size: 0.85rem; 
    line-height: 1.4; 
    box-shadow: 0 2px 4px rgba(0,0,0,0.08); 
}
</style>
""", unsafe_allow_html=True)

# 4. Global Session State (Includes Date Picker State)
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

now = datetime.datetime.now()
today = now.date()

if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)

# 5. Global AI Query Function
def query_global_team_archive(question, archive_records, chat_history):
    DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not DEEPSEEK_API_KEY:
        return "DeepSeek API Key is missing. Please add it to your Streamlit Cloud Secrets."
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)
    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Answer user questions accurately by synthesizing past meeting records. "
        "Format responses in concise, professional corporate English with bullet points and tables"
        "Ask follow up questions to keep the conversation productive"
    )
    messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:28000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})
    payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.2, "max_tokens": 750}
    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200: return resp.json()["choices"][0]["message"]["content"].strip()
        return f"Service Notice ({resp.status_code}): {resp.text}"
    except Exception as e: return f"Connection error: {e}"

# 6. Fetch Data
supabase_records = fetch_meeting_archives(limit=100)

# 7. Header & Custom Popover Date Picker
top_left, top_right = st.columns([2.5, 1.5])

with top_right:
    col_pop, col_reset = st.columns([3, 1])
    
    with col_pop:
        date_label = f"{st.session_state['start_date'].strftime('%b %d, %Y')} — {st.session_state['end_date'].strftime('%b %d, %Y')}"
        with st.popover(date_label, use_container_width=True):
            p_col1, p_col2 = st.columns([1, 2])
            
            with p_col1:
                st.caption("PRESETS")
                if st.button("This Week", use_container_width=True):
                    st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday())
                    st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                    st.rerun()
                if st.button("Last Week", use_container_width=True):
                    st.session_state["start_date"] = today - datetime.timedelta(days=today.weekday() + 7)
                    st.session_state["end_date"] = st.session_state["start_date"] + datetime.timedelta(days=6)
                    st.rerun()
                if st.button("This Month", use_container_width=True):
                    st.session_state["start_date"] = today.replace(day=1)
                    _, last = calendar.monthrange(today.year, today.month)
                    st.session_state["end_date"] = today.replace(day=last)
                    st.rerun()
                if st.button("Last Month", use_container_width=True):
                    first_this = today.replace(day=1)
                    last_prev = first_this - datetime.timedelta(days=1)
                    st.session_state["start_date"] = last_prev.replace(day=1)
                    st.session_state["end_date"] = last_prev
                    st.rerun()
                if st.button("Clear", use_container_width=True):
                    st.session_state["start_date"] = today.replace(day=1)
                    _, last = calendar.monthrange(today.year, today.month)
                    st.session_state["end_date"] = today.replace(day=last)
                    st.rerun()
                    
            with p_col2:
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
                        
    with col_reset:
        if st.button("Reset", use_container_width=True):
            st.session_state["start_date"] = today.replace(day=1)
            _, last = calendar.monthrange(today.year, today.month)
            st.session_state["end_date"] = today.replace(day=last)
            st.rerun()

# 8. Filter Data based on State
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

# 9. KPI Cards (Ultra Compact)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Meetings (Selected)</div><div class="kpi-value">{total_range_meetings}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Team Meetings</div><div class="kpi-value">{total_team_meetings}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Internal</div><div class="kpi-value">{total_internal_meetings}</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total External</div><div class="kpi-value">{total_external_meetings}</div></div>', unsafe_allow_html=True)


# 10. Main Split Layout - AI Emphasized Ratio (40/60 Split)
col_left, col_right = st.columns([1.2, 1.8])

with col_left:
    with st.container(height=520, border=True):
        st.markdown('<h3>Recent Meetings</h3>', unsafe_allow_html=True)
        st.caption("Browse archived meetings for the selected date range.")
        
        if filtered_records:
            for idx, m in enumerate(filtered_records):
                m_id = m.get("meeting_id") or f"MOM-{idx}"
                client = m.get("client_name") or "Meeting Record"
                m_date = str(m.get("meeting_date", "N/A"))[:10]
                location = m.get("location") or "Location N/A"
                prep = m.get("prepared_by") or "CRD Team"
                summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                
                with st.container(border=False):
                    st.markdown(f"""
                    <div class="gallery-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <p class='gallery-title'>{client}</p>
                                <p class='gallery-sub'>{m_date} &bull; {prep}</p>
                            </div>
                        </div>
                        <p class='gallery-desc'>{summary[:90]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("View", key=f"btn_view_{m_id}_{idx}", use_container_width=True):
                        st.session_state["selected_meeting_id"] = m_id
                        st.switch_page("pages/2_meeting_details.py")
        else:
            st.info("No meeting archives found for the selected date range.")

with col_right:
    with st.container(height=520, border=True):
        st.markdown('<h3>Ask Echo — Global Intelligence</h3>', unsafe_allow_html=True)
        st.caption("Query all stored meeting transcripts, action items, and client records directly.")

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if not st.session_state["global_chat_history"]:
            st.markdown('<div class="chat-ai"><strong>System Online:</strong> Hello. I am Echo. Ask me any question across your entire meeting archive.</div>', unsafe_allow_html=True)
        else:
            for msg in st.session_state["global_chat_history"]:
                if msg["role"] == "assistant":
                    st.markdown(f'<div class="chat-ai">{msg["content"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-user-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if global_query := st.chat_input("Ask Echo"):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Echo is analyzing meeting archives..."):
                ans = query_global_team_archive(global_query, supabase_records, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()
