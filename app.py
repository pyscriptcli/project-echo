import os
import json
import datetime
import pandas as pd
import requests
import streamlit as st

# ========== CONFIG ==========
st.set_page_config(
    page_title="Project Echo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROGRAMMATIC LIGHT MODE & 200MB LIMIT ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
os.makedirs(_config_dir, exist_ok=True)
with open(_config_file, "w", encoding="utf-8") as f:
    f.write('[theme]\nbase="light"\n[server]\nmaxUploadSize = 200\n')

# API Keys loaded strictly from Streamlit Cloud Secrets
DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"

# Global Archive JSON Storage
ARCHIVE_DB_FILE = ".echo_archive.json"

def load_archive_db():
    if os.path.exists(ARCHIVE_DB_FILE):
        try:
            with open(ARCHIVE_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_archive_db(data):
    try:
        with open(ARCHIVE_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# Seed sample data if database is fresh
if not os.path.exists(ARCHIVE_DB_FILE):
    sample_records = [
        {
            "id": "MOM-20260825-01",
            "date": "August 25, 2026",
            "client_name": "Regis Properties Inc.",
            "location": "GreatWork Mega Tower 32F - Board Room",
            "prepared_by": "Cedtrix Rena",
            "confirmed_by": "Mr. Raymond Santos",
            "summary": "Action plan alignment for the Bida project and commercial franchisee expansion.",
            "action_items": [
                {"task": "Communicate deliverables with franchisees", "pic": "Cedrics, Melissa, Carlo, Dyx", "due": "August 31, 2026"},
                {"task": "Deliver data analytics support deck", "pic": "Dave Policarpio, Irish Rima", "due": "September 05, 2026"}
            ],
            "transcript_sample": "Our meeting today is to discuss the action plan for the Bida project. Cedrics, Melissa, Carlo, and Dykes will handle accounts."
        }
    ]
    save_archive_db(sample_records)

# ========== GLOBAL SESSION STATE ==========
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []

# ========== CENTRAL PASSWORD GATE ==========
if not st.session_state["authenticated"]:
    st.markdown("""
    <div style="text-align: center; margin-top: 5rem; margin-bottom: 2rem;">
        <h1 style="font-family: 'Playfair Display', serif; font-style: italic; font-size: 2.2rem; color: #161616;">
            Project <span style="color: #D4AF37;">Echo</span>
        </h1>
        <p style="font-size: 0.95rem; color: #666;">PRIME Philippines Enterprise Intelligence Hub</p>
    </div>
    """, unsafe_allow_html=True)
    
    _, auth_col, _ = st.columns([1.5, 1.2, 1.5])
    with auth_col:
        with st.container(border=True):
            pw_input = st.text_input("Enter Team Access Key:", type="password")
            if st.button("Log In", use_container_width=True):
                configured_password = str(st.secrets.get("APP_PASSWORD", "crd3ch0")).strip()
                if pw_input == configured_password:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Invalid access key. Contact the administrator.")
    st.stop()

# ========== CUSTOM CSS: CLICKUP-STYLE COLLAPSIBLE SIDEBAR ==========
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif !important;
}

/* Technical Grid Background */
.stApp {
    background-color: #F3EFE6; 
    background-image: 
        linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px;
    color: #2D2D2D;
}

.stApp > header { display: none !important; }
.block-container { 
    padding-top: 5.5rem !important;
    padding-left: 5rem !important; 
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

/* ClickUp-Style Persistent Floating Collapsible Sidebar */
section[data-testid="stSidebar"] {
    width: 68px !important;
    min-width: 68px !important;
    max-width: 68px !important;
    background-color: #1B1B1B !important;
    border-right: 1px solid #333333 !important;
    box-shadow: 6px 0 20px rgba(0,0,0,0.15) !important;
    transition: width 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    overflow-x: hidden !important;
    z-index: 999995 !important;
    top: 60px !important;
    height: calc(100vh - 60px) !important;
}

/* Expand on Hover */
section[data-testid="stSidebar"]:hover {
    width: 290px !important;
    min-width: 290px !important;
    max-width: 290px !important;
}

/* Hide default collapse toggle button */
button[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}

/* Sidebar Elements Formatting */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    padding: 1rem 0.5rem !important;
    gap: 0.8rem !important;
}

section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] p, 
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #ECE9DF !important;
}

section[data-testid="stSidebar"] a {
    background-color: #242424 !important;
    border: 1px solid #383838 !important;
    border-radius: 8px !important;
    color: #ECE9DF !important;
    padding: 0.6rem 0.8rem !important;
    transition: all 0.2s ease !important;
}

section[data-testid="stSidebar"] a:hover {
    background-color: #D4AF37 !important;
    color: #161616 !important;
    border-color: #D4AF37 !important;
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

/* Main Dashboard Containers */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important; 
    border-radius: 12px !important;
    box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    margin-bottom: 1.25rem !important;
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
        "You have direct access to the entire company meeting database, archives, deliverables, and transcripts. "
        "Answer questions accurately, cross-synthesize topics, highlight specific deadlines, budgets, "
        "and name responsible persons-in-charge. "
        "Format responses in concise, professional corporate English with clean markdown bullet points."
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nCompany Meeting Archives:\n{archive_context[:28000]}"}]
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

# ========== CLICKUP-STYLE COLLAPSIBLE SIDEBAR ==========
archive_data = load_archive_db()

with st.sidebar:
    st.markdown("<h3 style='color:#FFFFFF !important; font-size:1.1rem !important;'>Navigation</h3>", unsafe_allow_html=True)
    
    # Page Switcher
    if os.path.exists("pages/mom_generator.py"):
        st.page_link("pages/mom_generator.py", label="MoM Generator", icon=":material/edit_document:")
    elif os.path.exists("pages/1_MoM_Generator.py"):
        st.page_link("pages/1_MoM_Generator.py", label="MoM Generator", icon=":material/edit_document:")
        
    st.markdown("---")
    st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#D4AF37;'>ARCHIVE EXPLORER</p>", unsafe_allow_html=True)
    
    search_query = st.text_input("Search archives", placeholder="Search client or topic...", label_visibility="collapsed")
    
    filtered_meetings = archive_data
    if search_query:
        q = search_query.lower()
        filtered_meetings = [
            m for m in archive_data 
            if q in m.get("client_name", "").lower() or q in m.get("summary", "").lower() or q in m.get("prepared_by", "").lower()
        ]
        
    st.caption(f"{len(filtered_meetings)} of {len(archive_data)} logs")
    for m in filtered_meetings[:5]:
        with st.expander(f"{m.get('client_name', 'Client')} ({m.get('date', 'Date')[:6]})"):
            st.caption(f"Location: {m.get('location', 'N/A')}")
            st.caption(f"Prepared by: {m.get('prepared_by', 'N/A')}")
            st.write(f"**Focus:** {m.get('summary', 'No summary logged.')}")

# ========== MAIN DASHBOARD VIEW ==========
# 1. High-Level KPI Metric Cards
total_meetings = len(archive_data)
total_action_items = sum(len(m.get("action_items", [])) for m in archive_data)
unique_clients = len(set(m.get("client_name") for m in archive_data if m.get("client_name")))

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Meetings</div><div class="kpi-value">{total_meetings}</div></div>', unsafe_allow_html=True)
with kpi2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Action Items Tracked</div><div class="kpi-value">{total_action_items}</div></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Corporate Clients</div><div class="kpi-value">{unique_clients}</div></div>', unsafe_allow_html=True)
with kpi4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Hub Status</div><div class="kpi-value" style="color:#2E7D32; font-size:1.6rem;">Operational</div></div>', unsafe_allow_html=True)

st.write("")

# 2. Main Symmetrical Split: Deliverables Matrix (Left) & Ask Echo Global (Right)
col_left, col_right = st.columns(2)

with col_left:
    with st.container(height=580, border=True):
        st.markdown('<h3>Cross-Meeting Deliverables Matrix</h3>', unsafe_allow_html=True)
        st.caption("Active action items aggregated across company meetings.")
        
        all_tasks = []
        for m in archive_data:
            client = m.get("client_name", "Client")
            for item in m.get("action_items", []):
                all_tasks.append({
                    "Client / Account": client,
                    "Action Plan / Deliverable": item.get("task", ""),
                    "Person-in-Charge": item.get("pic", "Unassigned"),
                    "Target Date": item.get("due", "TBD")
                })
        
        if all_tasks:
            task_df = pd.DataFrame(all_tasks)
            st.dataframe(
                task_df,
                use_container_width=True,
                height=450,
                hide_index=True
            )
        else:
            st.info("No active tasks found in the archive database.")

with col_right:
    with st.container(height=580, border=True):
        st.markdown('<h3>Ask Echo &mdash; Global Intelligence</h3>', unsafe_allow_html=True)
        st.caption("Query all past transcripts, commitments, deadlines, and client remarks.")

        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if not st.session_state["global_chat_history"]:
            st.markdown(
                '<div class="chat-ai">Hello. I am Echo Global. Ask me any question across your team\'s archived meeting records and deliverables.</div>',
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

        if global_query := st.chat_input("Query whole company archive (e.g. 'What are the deadlines for Regis?')"):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing team archives..."):
                ans = query_global_team_archive(global_query, archive_data, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()
