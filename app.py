import os
import sys
import json
import datetime
import pandas as pd
import requests
import streamlit as st
from supabase import create_client, Client

# ========== CONFIG (Must be called first) ==========
st.set_page_config(
    page_title="Project Echo - Executive Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure root directory is on Python path for navbar import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "pages" in __file__ else os.path.abspath("."))
from navigation import render_global_navbar

# Render Topbar & Left Rail
render_global_navbar("Project Echo &mdash; Executive Hub")

# --- PROGRAMMATIC LIGHT MODE & 200MB LIMIT ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
os.makedirs(_config_dir, exist_ok=True)
with open(_config_file, "w", encoding="utf-8") as f:
    f.write('[theme]\nbase="light"\n[server]\nmaxUploadSize = 200\n')

# API Keys & Supabase Credentials
DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"

SUPABASE_URL = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")
if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL[:-8]

SUPABASE_KEY = "".join(str(st.secrets.get("SUPABASE_KEY", "")).split())

# ========== SUPABASE CLIENT & DATA HELPERS ==========
@st.cache_resource
def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

def fetch_meeting_archives_from_supabase(limit: int = 100):
    client = init_supabase()
    if not client:
        return []
    try:
        resp = client.table("meeting_archives").select("*").order("meeting_date", desc=True).limit(limit).execute()
        return resp.data if resp and resp.data else []
    except Exception as e:
        st.warning(f"Could not retrieve meeting archives: {e}")
        return []

# ========== GLOBAL SESSION STATE ==========
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

# ========== COMPLETE SELF-CONTAINED CSS & FLOATING NAVBAR ==========
CUSTOM_LAYOUT_HTML = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* Crisp Technical Background */
.stApp {
    background-color: #F3EFE6; 
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

.stApp > header { display: none !important; }

/* Remove native sidebar elements */
section[data-testid="stSidebar"],
button[data-testid="stSidebarCollapseButton"],
div[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Main content spacing */
.block-container { 
    padding-top: 5.5rem !important;
    padding-left: 6.2rem !important;
    padding-right: 2rem !important;
    max-width: 98% !important;
}

/* Fixed Topbar */
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

/* Permanent Viewport Left Icon Rail */
.echo-nav-rail {
    position: fixed;
    top: 60px;
    left: 0;
    bottom: 0;
    width: 68px;
    background-color: #161616;
    border-right: 1px solid #2B2B2B;
    box-shadow: 4px 0 15px rgba(0,0,0,0.2);
    z-index: 999980;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.25rem 0;
    gap: 1.25rem;
}

.echo-nav-item {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background-color: #222222;
    border: 1px solid #333333;
    display: flex;
    align-items: center;
    justify-content: center;
    text-decoration: none;
    transition: all 0.2s ease;
    cursor: pointer;
}

.echo-nav-item svg {
    width: 22px;
    height: 22px;
    stroke: #C5A059;
    fill: none;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    transition: all 0.2s ease;
}

.echo-nav-item:hover {
    background-color: #D4AF37;
    border-color: #D4AF37;
    transform: translateY(-1px);
}

.echo-nav-item:hover svg {
    stroke: #161616;
}

/* Metric KPI Cards */
.kpi-card {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-title {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: #888888;
    margin-bottom: 0.25rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.9rem;
    color: #1A2B4C;
    margin: 0;
}

/* Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}

.gallery-title {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.15rem;
    color: #1A2B4C;
    margin: 0 0 0.25rem 0;
}
.gallery-sub {
    font-size: 0.82rem;
    color: #666;
    margin-bottom: 0.4rem;
}
.gallery-desc {
    font-size: 0.86rem;
    color: #2D2D2D;
    line-height: 1.4;
}

.stButton > button {
    background-color: #222222 !important; 
    color: #FFFFFF !important;
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px; 
    padding: 0.4rem 1.2rem !important;
    height: 36px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #D4AF37 !important;
    color: #161616 !important;
    transform: translateY(-1px);
}

.chat-container { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; padding-bottom: 1rem; }
.chat-ai {
    align-self: flex-start;
    color: #1A1A1A;
    padding: 0.2rem;
    max-width: 95%;
    font-size: 0.88rem;
    line-height: 1.5;
}
.chat-user-wrap { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 0.2rem; }
.chat-user {
    background-color: #F3F4F6;
    color: #1A1A1A;
    padding: 0.55rem 0.95rem;
    border-radius: 14px;
    max-width: 82%;
    font-size: 0.88rem;
    line-height: 1.45;
}
</style>

<!-- Topbar -->
<div class="echo-topbar-wrapper">
    <h1 class="echo-title">Project <span>Echo</span> &mdash; Executive Hub</h1>
</div>

<!-- Left Rail with Exact Matched Routes -->
<div class="echo-nav-rail">
    <a href="/" target="_self" class="echo-nav-item" title="Executive Dashboard">
        <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
    </a>
    <a href="/1_minutes_of_the_meeting" target="_self" class="echo-nav-item" title="MoM Generator">
        <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
    </a>
    <a href="/2_meeting_details" target="_self" class="echo-nav-item" title="Meeting Browser">
        <svg viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
    </a>
    <a href="/5_ask_echo" target="_self" class="echo-nav-item" title="Ask Echo AI">
        <svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="10" rx="2"></rect><circle cx="12" cy="5" r="2"></circle><path d="M12 7v4"></path><line x1="8" y1="16" x2="8.01" y2="16"></line><line x1="16" y1="16" x2="16.01" y2="16"></line></svg>
    </a>
</div>
"""
st.markdown(CUSTOM_LAYOUT_HTML, unsafe_allow_html=True)

# Fetch Supabase Data
supabase_records = fetch_meeting_archives_from_supabase()

# ========== METRICS COMPUTATION ==========
now = datetime.datetime.now()
current_month_name = now.strftime("%B")
current_year = now.year
current_month = now.month

total_month_meetings = 0
total_team_meetings = len(supabase_records)
total_internal_meetings = 0
total_external_meetings = 0

for m in supabase_records:
    m_date_raw = str(m.get("meeting_date", ""))
    try:
        parsed_d = datetime.datetime.strptime(m_date_raw[:10], "%Y-%m-%d")
        if parsed_d.year == current_year and parsed_d.month == current_month:
            total_month_meetings += 1
    except Exception:
        pass

    client_name_str = str(m.get("client_name", "")).strip().lower()
    raw_payload = m.get("raw_payload", {}) or {}
    meeting_details_dict = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
    external_atts = meeting_details_dict.get("external_attendees", [])
    
    if "internal" in client_name_str or "prime" in client_name_str or (not external_atts and not client_name_str):
        total_internal_meetings += 1
    else:
        total_external_meetings += 1

# 1. Four Big KPI Number Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Meetings ({current_month_name})</div><div class="kpi-value">{total_month_meetings}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Team Meetings</div><div class="kpi-value">{total_team_meetings}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Internal Meetings</div><div class="kpi-value">{total_internal_meetings}</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total External Meetings</div><div class="kpi-value">{total_external_meetings}</div></div>', unsafe_allow_html=True)

st.write("")

# 2. Main Symmetrical Split: Meeting Gallery & Ask Echo Global
col_left, col_right = st.columns(2)

with col_left:
    with st.container(height=580, border=True):
        st.markdown('<h3>Meeting Gallery</h3>', unsafe_allow_html=True)
        st.caption("Browse all archived meetings. Click any entry to inspect full details, transcript, and edit minutes.")
        
        if supabase_records:
            for idx, m in enumerate(supabase_records):
                m_id = m.get("meeting_id") or f"MOM-{idx}"
                client = m.get("client_name") or "Meeting Record"
                m_date = str(m.get("meeting_date", "N/A"))[:10]
                location = m.get("location") or "Location N/A"
                prep = m.get("prepared_by") or "CRD Team"
                summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                if not summary:
                    summary = "Minutes generated and stored in Supabase archive."
                
                with st.container(border=True):
                    gc1, gc2 = st.columns([7.5, 2.5])
                    with gc1:
                        st.markdown(f"<p class='gallery-title'>{client}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='gallery-sub'>Date: {m_date} &bull; {location} &bull; Prepared by: {prep}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p class='gallery-desc'>{summary[:160]}...</p>", unsafe_allow_html=True)
                    with gc2:
                        st.write("<div style='height: 18px;'></div>", unsafe_allow_html=True)
                        if st.button("View Meeting", key=f"btn_view_{m_id}_{idx}"):
                            st.session_state["selected_meeting_id"] = m_id
                            st.switch_page("pages/2_meeting_details.py")
        else:
            st.info("No meeting archives found in Supabase.")

with col_right:
    with st.container(height=580, border=True):
        st.markdown('<h3>Ask Echo &mdash; Global Intelligence</h3>', unsafe_allow_html=True)
        st.caption("Query all stored meeting transcripts, action items, and client records.")

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if not st.session_state["global_chat_history"]:
            st.markdown(
                '<div class="chat-ai">Hello. I am Echo Global. Ask me any question across your Supabase meeting archive.</div>',
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state["global_chat_history"]:
                if msg["role"] == "assistant":
                    formatted_content = msg["content"].replace("\n", "<br>")
                    st.markdown(f'<div class="chat-ai">{formatted_content}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-user-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if global_query := st.chat_input("Query whole company archive (e.g. 'What are the deliverables for Regis?')"):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing Supabase archives..."):
                headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
                archive_context = json.dumps(supabase_records, indent=1)
                system_prompt = (
                    "You are Echo Global, an executive AI analyst for PRIME Philippines. "
                    "You have direct access to the team's Supabase meeting archives, deliverables, summaries, and transcripts. "
                    "Answer user questions accurately with clean markdown bullet points."
                )
                messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:28000]}"}]
                for m_item in st.session_state["global_chat_history"][-6:]:
                    messages.append({"role": m_item["role"], "content": m_item["content"]})
                messages.append({"role": "user", "content": global_query})
                try:
                    resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json={"model": "deepseek-chat", "messages": messages, "temperature": 0.2, "max_tokens": 750}, timeout=60)
                    ans = resp.json()["choices"][0]["message"]["content"].strip() if resp.status_code == 200 else f"Notice ({resp.status_code}): {resp.text}"
                except Exception as ex:
                    ans = f"Connection error: {ex}"
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()
