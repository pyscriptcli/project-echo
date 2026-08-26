import os
import json
import datetime
import pandas as pd
import requests
import streamlit as st
from supabase import create_client, Client

# ========== CONFIG ==========
st.set_page_config(
    page_title="Project Echo - Executive Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# ========== CUSTOM CSS ==========
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* Crisp Technical Large Gridlines Background */
.stApp {
    background-color: #F3EFE6; 
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

.stApp > header { display: none !important; }

/* Main content offset for fixed topbar and icon sidebar */
.block-container { 
    padding-top: 5.5rem !important;
    padding-left: 5.8rem !important;
    padding-right: 2rem !important;
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

/* Persistent Fixed Icon-Only Rail Sidebar */
section[data-testid="stSidebar"] {
    position: fixed !important;
    width: 68px !important;
    min-width: 68px !important;
    max-width: 68px !important;
    background-color: #161616 !important;
    border-right: 1px solid #2B2B2B !important;
    box-shadow: 4px 0 15px rgba(0,0,0,0.2) !important;
    z-index: 999995 !important;
    top: 60px !important;
    height: calc(100vh - 60px) !important;
    display: block !important;
    visibility: visible !important;
}

button[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding: 1.2rem 0 !important;
    gap: 1.1rem !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}

/* Page Link Navigation Icons */
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

section[data-testid="stSidebar"] a span[data-testid="stPageLink-Text"] {
    display: none !important;
}

section[data-testid="stSidebar"] a span[data-testid="stIconMaterial"] {
    font-size: 1.4rem !important;
    margin: 0 !important;
    color: #C5A059 !important;
}

section[data-testid="stSidebar"] a:hover {
    background-color: #D4AF37 !important;
    border-color: #D4AF37 !important;
}

section[data-testid="stSidebar"] a:hover span[data-testid="stIconMaterial"] {
    color: #161616 !important;
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

/* Containers with Depth & Shadow */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
}

/* Gallery Item Card */
.gallery-card {
    background-color: #FAFAFA;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    padding: 1.1rem;
    margin-bottom: 0.85rem;
    transition: all 0.2s ease;
}
.gallery-card:hover {
    border-color: #D4AF37;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.12);
    transform: translateY(-2px);
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

/* Uniform Pill Buttons */
.stButton > button, .stDownloadButton > button {
    background-color: #222222 !important; 
    color: #FFFFFF !important;
    border: none !important; 
    border-radius: 50px !important; 
    font-family: 'Montserrat', sans-serif !important; 
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.5px; 
    padding: 0.4rem 1.2rem !important;
    min-height: 36px !important;
    height: 36px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    transition: all 0.2s ease !important; 
    width: 100% !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    background-color: #D4AF37 !important;
    color: #161616 !important;
    box-shadow: 0 6px 12px rgba(212, 175, 55, 0.2) !important;
    transform: translateY(-1px);
}

/* Claude Minimalist Chat */
.chat-container { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; padding-bottom: 1rem; }
.chat-ai {
    align-self: flex-start;
    background-color: transparent;
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
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ========== GLOBAL AI QUERY FUNCTION ==========
def query_global_team_archive(question, archive_records, chat_history):
    if not DEEPSEEK_API_KEY:
        return "DeepSeek API Key is missing. Please add it to your Streamlit Cloud Secrets."

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    archive_context = json.dumps(archive_records, indent=1)

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "You have direct access to the team's Supabase meeting archives, deliverables, summaries, and transcripts. "
        "Answer user questions accurately by synthesizing past meeting records, deadlines, and assigned persons-in-charge. "
        "Format responses in concise, professional corporate English with clean markdown bullet points."
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nCompany Supabase Meeting Archives:\n{archive_context[:28000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 750
    }

    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"Service Notice ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"

# Top Fixed Bar
st.markdown("""
<div class="echo-topbar-wrapper">
 <h1 class="echo-title">Project <span>Echo</span> &mdash; Executive Hub</h1>
</div>
""", unsafe_allow_html=True)

# Fetch current live data from Supabase
supabase_records = fetch_meeting_archives_from_supabase()

# ========== PERSISTENT ICON-ONLY SIDEBAR ==========
with st.sidebar:
    st.page_link("app.py", icon=":material/dashboard:", help="Executive Dashboard")
    
    if os.path.exists("pages/mom_generator.py"):
        st.page_link("pages/mom_generator.py", icon=":material/edit_document:", help="MoM Generator")
    elif os.path.exists("pages/1_MoM_Generator.py"):
        st.page_link("pages/1_MoM_Generator.py", icon=":material/edit_document:", help="MoM Generator")
        
    if os.path.exists("pages/meeting_details.py"):
        st.page_link("pages/meeting_details.py", icon=":material/menu_book:", help="Meeting Browser")
        
    if os.path.exists("pages/2_Ask_Echo.py"):
        st.page_link("pages/2_Ask_Echo.py", icon=":material/smart_toy:", help="Ask Echo AI")
    elif os.path.exists("pages/ask_echo.py"):
        st.page_link("pages/ask_echo.py", icon=":material/smart_toy:", help="Ask Echo AI")

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
    # Check date for dynamic current month
    m_date_raw = str(m.get("meeting_date", ""))
    try:
        parsed_d = datetime.datetime.strptime(m_date_raw[:10], "%Y-%m-%d")
        if parsed_d.year == current_year and parsed_d.month == current_month:
            total_month_meetings += 1
    except:
        pass

    # Check Internal vs External
    client_name_str = str(m.get("client_name", "")).strip().lower()
    raw_payload = m.get("raw_payload", {}) or {}
    meeting_details_dict = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
    external_atts = meeting_details_dict.get("external_attendees", [])
    
    if "internal" in client_name_str or "prime" in client_name_str or (not external_atts and not client_name_str):
        total_internal_meetings += 1
    else:
        total_external_meetings += 1

# ========== MAIN DASHBOARD VIEW ==========
# 1. Four Big KPI Number Cards in Requested Order
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

# 2. Main Symmetrical Split: Meeting Gallery (Left) & Ask Echo Global (Right)
col_left, col_right = st.columns(2)

with col_left:
    with st.container(height=580, border=True):
        st.markdown('<h3>Meeting Gallery</h3>', unsafe_allow_html=True)
        st.caption("Browse all archived meetings. Click any entry to inspect full details, transcript, and edit minutes.")
        
        if supabase_records:
            # Scrollable gallery container
            for idx, m in enumerate(supabase_records):
                m_id = m.get("meeting_id") or f"MOM-{idx}"
                client = m.get("client_name") or "Meeting Record"
                m_date = str(m.get("meeting_date", "N/A"))[:10]
                location = m.get("location") or "Location N/A"
                prep = m.get("prepared_by") or "CRD Team"
                summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()
                if not summary:
                    summary = "Minutes generated and stored in Supabase archive."
                
                # Render clean card
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
                            st.switch_page("pages/meeting_details.py")
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
                ans = query_global_team_archive(global_query, supabase_records, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()
