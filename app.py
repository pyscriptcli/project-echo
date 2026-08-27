import streamlit as st
import datetime
from utils.db import fetch_meeting_archives
from utils.ai import query_global_team_archive

# 1. Page Config (MUST be first Streamlit command)
st.set_page_config(page_title="Project Echo - Executive Hub", layout="wide", initial_sidebar_state="expanded")

# 2. Global State Initialization
if "global_chat_history" not in st.session_state:
    st.session_state["global_chat_history"] = []
if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

# 3. Custom CSS (Minimal & Stable)
st.markdown("""
<style>
.stApp { background-color: #F3EFE6; color: #2D2D2D; font-family: 'Montserrat', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif; font-style: italic; color: #1A2B4C; }
.echo-topbar { position: fixed; top: 0; left: 0; right: 0; height: 60px; background: #161616; border-bottom: 1px solid #333; z-index: 999; display: flex; align-items: center; padding: 0 2rem; }
.echo-title { font-family: 'Playfair Display', serif; font-style: italic; font-size: 1.35rem; color: #FFF; margin: 0; }
.echo-title span { color: #D4AF37; }
.block-container { padding-top: 5.5rem !important; }
.kpi-card { background: #FFF; border-radius: 12px; padding: 1.25rem; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid rgba(0,0,0,0.05); text-align: center; }
.kpi-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #888; margin-bottom: 0.5rem; }
.kpi-value { font-family: 'Playfair Display', serif; font-style: italic; font-size: 2rem; color: #1A2B4C; margin: 0; }
.chat-ai { background: transparent; color: #1A1A1A; padding: 0.5rem; max-width: 95%; font-size: 0.9rem; line-height: 1.5; }
.chat-user { background: #E9ECEF; color: #1A1A1A; padding: 0.6rem 1rem; border-radius: 14px; max-width: 85%; font-size: 0.9rem; margin-left: auto; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# 4. Fixed Topbar UI
st.markdown('<div class="echo-topbar"><h1 class="echo-title">Project <span>Echo</span> &mdash; Executive Hub</h1></div>', unsafe_allow_html=True)

# 5. Data Fetching
supabase_records = fetch_meeting_archives()

# 6. Metrics Computation (Optimized with generator expressions)
now = datetime.datetime.now()
current_month_name = now.strftime("%B")
current_year, current_month = now.year, now.month

total_month = sum(1 for m in supabase_records if str(m.get("meeting_date", ""))[:7] == f"{current_year}-{current_month:02d}")
total_team = len(supabase_records)
total_internal = sum(1 for m in supabase_records if "internal" in str(m.get("client_name", "")).lower() or "prime" in str(m.get("client_name", "")).lower())
total_external = total_team - total_internal

# 7. Main Layout
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.markdown(f'<div class="kpi-card"><div class="kpi-title">Meetings ({current_month_name})</div><div class="kpi-value">{total_month}</div></div>', unsafe_allow_html=True)
kpi2.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Team Meetings</div><div class="kpi-value">{total_team}</div></div>', unsafe_allow_html=True)
kpi3.markdown(f'<div class="kpi-card"><div class="kpi-title">Internal Meetings</div><div class="kpi-value">{total_internal}</div></div>', unsafe_allow_html=True)
kpi4.markdown(f'<div class="kpi-card"><div class="kpi-title">External Meetings</div><div class="kpi-value">{total_external}</div></div>', unsafe_allow_html=True)

st.write("") # Spacer

col_left, col_right = st.columns(2)

# Left: Meeting Gallery
with col_left:
    with st.container(height=580, border=True):
        st.markdown("### Meeting Gallery")
        st.caption("Browse archived meetings. Click to inspect details.")
        
        if supabase_records:
            for idx, m in enumerate(supabase_records):
                m_id = m.get("meeting_id") or f"MOM-{idx}"
                client = m.get("client_name") or "Meeting Record"
                m_date = str(m.get("meeting_date", "N/A"))[:10]
                summary = str(m.get("summary_md", "No summary recorded.")).replace("### Summary", "").strip()[:160]
                
                with st.container(border=True):
                    gc1, gc2 = st.columns([7, 3])
                    with gc1:
                        st.markdown(f"**{client}**")
                        st.caption(f"📅 {m_date} | 📍 {m.get('location', 'N/A')}")
                        st.markdown(f"<small style='color:#666'>{summary}...</small>", unsafe_allow_html=True)
                    with gc2:
                        st.write("") # Spacer
                        if st.button("View Details", key=f"view_{m_id}", use_container_width=True):
                            st.session_state["selected_meeting_id"] = m_id
                            st.switch_page("pages/2_meeting_details.py")
        else:
            st.info("No meeting archives found.")

# Right: Ask Echo AI
with col_right:
    with st.container(height=580, border=True):
        st.markdown("### Ask Echo — Global Intelligence")
        st.caption("Query all stored meeting transcripts and action items.")

        # Chat Display
        if not st.session_state["global_chat_history"]:
            st.markdown('<div class="chat-ai">Hello. I am Echo Global. Ask me any question across your Supabase meeting archive.</div>', unsafe_allow_html=True)
        else:
            for msg in st.session_state["global_chat_history"]:
                if msg["role"] == "assistant":
                    st.markdown(f'<div class="chat-ai">{msg["content"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)

        # Chat Input
        if global_query := st.chat_input("Query whole company archive..."):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing Supabase archives..."):
                ans = query_global_team_archive(global_query, supabase_records, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()
