import streamlit as st
import requests
import json
from utils.db import fetch_meeting_archives, fetch_echo_context

def render_echo_chat(container=None, height=720, title="Ask Echo — Global Intelligence", caption="Synthesize meeting archives, transcripts, and action logs."):
    """
    Renders the global Ask Echo chat interface as a reusable component.
    """
    target = container if container else st
    
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []

    with target.container(height=height, border=True):
        # Header & Action Buttons
        chat_header_col, btn_clear_col, btn_full_col = st.columns([1, 0.04, 0.04])
        
        with chat_header_col:
            st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="section-caption">{caption}</p>', unsafe_allow_html=True)
            
        with btn_clear_col:
            st.markdown('<div class="icon-action-btn">', unsafe_allow_html=True)
            if st.button("", icon=":material/delete:", key="btn_clear_chat", help="Clear chat"):
                st.session_state["global_chat_history"] = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with btn_full_col:
            st.markdown('<div class="icon-action-btn">', unsafe_allow_html=True)
            is_fullscreen = st.session_state.get("chat_fullscreen", False)
            full_icon = ":material/fullscreen_exit:" if is_fullscreen else ":material/fullscreen:"
            tooltip = "Exit Fullscreen" if is_fullscreen else "Fullscreen"
            if st.button("", icon=full_icon, key="btn_fullscreen_chat", help=tooltip):
                st.session_state["chat_fullscreen"] = not is_fullscreen
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # Chat Feed (Inherits your custom CSS for stChatMessage)
        chat_feed_height = height - 175 
        chat_history_container = st.container(height=chat_feed_height)
        
        with chat_history_container:
            if not st.session_state["global_chat_history"]:
                with st.chat_message("assistant"):
                    st.markdown("**System Online:** Hello. I am Echo. Ask me anything across your entire meeting archive.")
            else:
                for msg in st.session_state["global_chat_history"]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        # Chat Input
        if global_query := st.chat_input("Ask Echo a question..."):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing meeting archives..."):
                archives = fetch_meeting_archives(limit=100)
                ans = _query_echo_backend(global_query, archives, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()

def _query_echo_backend(question: str, archive_records: list, chat_history: list) -> str:
    """Internal function to handle the AI API call with Context Injection."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "⚠️ DeepSeek API Key is missing in Streamlit Secrets."
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)
    
    # 1. Fetch Live Context from Supabase
    context_data = fetch_echo_context()
    
    # 2. Format it for the AI
    team_list = ", ".join(context_data.get('team', []))
    jargon_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('jargon', {}).items()])
    projects = ", ".join(context_data.get('projects', []))
    
    context_string = f"""
ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
---------------------------------------
TEAM MEMBERS: {team_list}
ACTIVE PROJECTS: {projects}
TECHNICAL JARGON:
{jargon_list}

INSTRUCTION: Use this knowledge base to correct proper nouns, acronyms, and project names in the archives. 
If the archive says 'Cool Berneties' but the Knowledge Base says 'Kubernetes', you MUST use 'Kubernetes'.
"""

    # 3. Build System Prompt with Context Injection
    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Answer user questions accurately by synthesizing past meeting records, deadlines, and assigned persons-in-charge. "
        "Format responses cleanly in Markdown using bullet points and Markdown tables where appropriate. "
        "Do not use emojis; use plain text. Ask follow-up questions when useful."
        f"\n\n{context_string}\n"
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
