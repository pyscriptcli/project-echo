import streamlit as st
import requests
import json
import re
from datetime import datetime
from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context

# --- Pure SVG Icon Assets ---
SVG_ECHO_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
</svg>
"""

SVG_USER_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
</svg>
"""

SVG_GLOBE_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="2" y1="12" x2="22" y2="12"></line>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
</svg>
"""

SVG_BRAIN_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

CHAT_COMPACT_CLEAN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Cormorant+Garamond:ital,wght@1,500;1,600;1,700&family=Playfair+Display:ital,wght@1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Prevent outer viewport scrolling */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow: hidden !important;
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Match the exact warm ivory architectural grid canvas */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) {
    background-color: #F9F6F0 !important;
    background-image: 
        linear-gradient(to right, #E7E0D3 1px, transparent 1px),
        linear-gradient(to bottom, #E7E0D3 1px, transparent 1px) !important;
    background-size: 32px 32px !important;
    border: 1px solid #DFD7C7 !important;
    border-radius: 8px !important;
    padding: 0 !important;
    box-shadow: none !important;
    overflow: hidden !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: calc(100vh - 120px) !important;
    max-height: calc(100vh - 120px) !important;
    padding: 0.65rem 1rem !important;
    gap: 0 !important;
    box-sizing: border-box !important;
}

/* Meeting Details Styled Header Row */
.echo-header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 0.35rem;
    margin-bottom: 0.35rem;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    flex-shrink: 0;
}

.echo-title-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
}

.echo-title {
    font-family: 'Playfair Display', 'Cormorant Garamond', Georgia, serif;
    font-style: italic;
    font-size: 1.35rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    line-height: 1.1;
    letter-spacing: 0.01em;
}

/* Dedicated Scrolling Chat Box with clean frosted white surface */
.echo-chat-box-container {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}

.echo-chat-box-container div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(8px) !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 6px !important;
    overflow-y: auto !important;
    padding: 0.75rem 1rem !important;
    height: 100% !important;
}

/* User Message Bubble */
.echo-msg-row-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
    margin-bottom: 0.75rem;
}

.echo-user-bubble {
    font-family: 'Plus Jakarta Sans', sans-serif;
    background: #111A2B;
    color: #FFFFFF !important;
    border: 1px solid #D4AF37;
    padding: 0.45rem 0.8rem;
    border-radius: 12px 2px 12px 12px;
    max-width: 75%;
    font-size: 0.82rem;
    line-height: 1.45;
    word-break: break-word;
}
.echo-user-bubble p {
    color: #FFFFFF !important;
    margin: 0;
}

.echo-avatar-user {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #111A2B;
    border: 1px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* AI Assistant Message */
.echo-msg-row-assistant {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: 0.85rem;
    background: transparent;
}

.echo-assistant-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 0.2rem;
}

.echo-avatar-assistant {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #111A2B;
    border: 1px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.echo-assistant-title {
    font-family: 'Cinzel', serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #854D0E;
}

.echo-assistant-badge-gold {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.55rem;
    padding: 1px 4px;
    border-radius: 3px;
    background: #FEF3C7;
    color: #92400E;
    font-weight: 600;
    border: 0.5px solid #FDE68A;
}

.echo-assistant-body {
    font-family: 'Plus Jakarta Sans', sans-serif;
    padding-left: 26px;
    color: #1E293B;
    font-size: 0.84rem;
    line-height: 1.55;
}
.echo-assistant-body strong {
    color: #0F172A;
}

/* Sources Pills */
.echo-sources-container {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 0.4rem;
    padding-left: 26px;
}
.echo-source-pill {
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: inline-flex;
    align-items: center;
    background: #F8FAFC;
    border: 1px solid rgba(212, 175, 55, 0.4);
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 0.68rem;
    color: #854D0E !important;
    text-decoration: none !important;
    font-weight: 500;
}
.echo-source-pill:hover {
    background: #FEFCE8;
    border-color: #D4AF37;
}

/* Tables */
.echo-assistant-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.45rem 0;
    font-size: 0.78rem;
    background: #FFFFFF;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
}
.echo-assistant-body th {
    font-family: 'Cinzel', serif;
    background: #111A2B;
    color: #D4AF37;
    font-weight: 700;
    letter-spacing: 0.04em;
    border: 1px solid #334155;
    padding: 4px 8px;
    text-align: left;
}
.echo-assistant-body td {
    border: 1px solid #E2E8F0;
    padding: 4px 8px;
    color: #334155;
}

/* Thinking Indicator */
.echo-thinking-wrapper {
    display: flex;
    align-items: center;
    gap: 6px;
    padding-left: 0.2rem;
    margin-bottom: 0.55rem;
}
.echo-thinking-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    border-radius: 4px;
    background: #F8FAFC;
    border: 1px solid rgba(212, 175, 55, 0.35);
    font-size: 0.72rem;
    color: #854D0E;
    font-weight: 500;
}
.echo-pulse-dot {
    width: 5px;
    height: 5px;
    background-color: #D4AF37;
    border-radius: 50%;
    animation: echo-pulse 1.4s infinite ease-in-out both;
}
@keyframes echo-pulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.2; }
    40% { transform: scale(1); opacity: 1; }
}

/* Knowledge Candidate Card */
.echo-knowledge-card {
    background: #F8FAFC;
    border: 1px solid #D4AF37;
    border-radius: 4px;
    padding: 0.45rem 0.65rem;
    margin-top: 0.3rem;
}

/* Docked Bottom Chat Input */
.echo-input-dock {
    padding-top: 0.35rem !important;
    flex-shrink: 0 !important;
}

div[data-testid="stChatInput"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}

div[data-testid="stChatInput"] > div {
    background: #FFFFFF !important;
    border: 1px solid rgba(212, 175, 55, 0.55) !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02) !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #0F172A !important;
    font-size: 0.84rem !important;
}
</style>
"""

def render_echo_chat(container=None, height=None, title="Ask Echo", caption=None, subtitle=None):
    target = container if container else st
    st.markdown(CHAT_COMPACT_CLEAN_CSS, unsafe_allow_html=True)

    # State Initializations
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "knowledge_proposal" not in st.session_state:
        st.session_state["knowledge_proposal"] = None
    if "echo_selected_model" not in st.session_state:
        st.session_state["echo_selected_model"] = "deepseek-chat"
    if "echo_source_archives" not in st.session_state:
        st.session_state["echo_source_archives"] = True
    if "echo_source_knowledge" not in st.session_state:
        st.session_state["echo_source_knowledge"] = True
    if "echo_source_web" not in st.session_state:
        st.session_state["echo_source_web"] = False

    with target.container(border=True):
        st.markdown('<div class="echo-main-card-scope"></div>', unsafe_allow_html=True)

        # Header Row: Logo, Refined Italic Title, and Action Controls
        h_left, h_mid, h_right = st.columns([0.035, 0.865, 0.10])
        with h_left:
            st.markdown(f'<div style="padding-top:2px;">{SVG_ECHO_LOGO}</div>', unsafe_allow_html=True)

        with h_mid:
            st.markdown(
                f'<div class="echo-header-row">'
                f'<div class="echo-title-wrap"><h2 class="echo-title">{title}</h2></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with h_right:
            c_settings, c_clr = st.columns(2)
            with c_settings:
                with st.popover("", icon=":material/settings:", help="Settings"):
                    st.markdown("<span style='font-family:Cinzel,serif; font-size:0.75rem; font-weight:700; color:#854D0E;'>AI MODEL</span>", unsafe_allow_html=True)
                    st.session_state["echo_selected_model"] = st.selectbox(
                        "Model",
                        options=["deepseek-chat", "deepseek-reasoner"],
                        index=0,
                        label_visibility="collapsed"
                    )
                    st.markdown("---")
                    st.markdown("<span style='font-family:Cinzel,serif; font-size:0.75rem; font-weight:700; color:#854D0E;'>DATA SOURCES</span>", unsafe_allow_html=True)
                    st.session_state["echo_source_archives"] = st.checkbox("Meeting Archives", value=st.session_state["echo_source_archives"])
                    st.session_state["echo_source_knowledge"] = st.checkbox("Echo Knowledge Base", value=st.session_state["echo_source_knowledge"])
                    st.session_state["echo_source_web"] = st.checkbox("Search Web", value=st.session_state["echo_source_web"])

            with c_clr:
                if st.button("", icon=":material/delete_sweep:", key="btn_clear_global_chat", help="Reset conversation"):
                    st.session_state["global_chat_history"] = []
                    st.session_state["knowledge_proposal"] = None
                    st.rerun()

        # ==========================================
        # --- Chat Stream Feed ---
        # ==========================================
        st.markdown('<div class="echo-chat-box-container">', unsafe_allow_html=True)
        chat_box = st.container()
        st.markdown('</div>', unsafe_allow_html=True)

        with chat_box:
            if not st.session_state["global_chat_history"]:
                st.markdown(
                    '<div class="echo-msg-row-assistant">'
                    '<div class="echo-assistant-header">'
                    f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                    '<span class="echo-assistant-title">ECHO GLOBAL</span>'
                    '<span class="echo-assistant-badge-gold">EXECUTIVE ANALYST</span>'
                    '</div>'
                    '<div class="echo-assistant-body">'
                    'Hi Team, this is Echo, ask me anything...'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                for msg in st.session_state["global_chat_history"]:
                    if msg["role"] == "user":
                        st.markdown(
                            f'<div class="echo-msg-row-user">'
                            f'<div class="echo-user-bubble">{msg["content"]}</div>'
                            f'<div class="echo-avatar-user">{SVG_USER_ICON}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div class="echo-msg-row-assistant">'
                            '<div class="echo-assistant-header">'
                            f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                            '<span class="echo-assistant-title">ECHO GLOBAL</span>'
                            '<span class="echo-assistant-badge-gold">EXECUTIVE ANALYST</span>'
                            '</div>'
                            '<div class="echo-assistant-body">',
                            unsafe_allow_html=True
                        )
                        st.markdown(msg["content"])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if msg.get("sources"):
                            sources_html = '<div class="echo-sources-container">'
                            for src in msg["sources"]:
                                sources_html += f'<a href="{src["url"]}" target="_blank" class="echo-source-pill">{SVG_GLOBE_ICON}{src["title"]}</a>'
                            sources_html += '</div>'
                            st.markdown(sources_html, unsafe_allow_html=True)
                            
                        st.markdown('</div>', unsafe_allow_html=True)

        # Knowledge Proposal Interactive Card
        if st.session_state["knowledge_proposal"]:
            prop = st.session_state["knowledge_proposal"]
            with st.container():
                st.markdown(
                    f'<div class="echo-knowledge-card">'
                    f'<div style="font-family:\'Cinzel\',serif; font-size:0.68rem; font-weight:700; color:#854D0E; margin-bottom:2px;">'
                    f'{SVG_BRAIN_ICON} Knowledge Base Candidate'
                    f'</div>'
                    f'<div style="font-size:0.75rem; color:#1F2937; margin-bottom:4px;">'
                    f'Register <b>{prop.get("key")}</b> ({prop.get("category")}): <i>{prop.get("value")}</i>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
                kp_c1, kp_c2 = st.columns([0.5, 0.5])
                with kp_c1:
                    if st.button("Confirm Addition", key="btn_confirm_prop", use_container_width=True):
                        upsert_echo_context(
                            category=prop["category"],
                            key=prop["key"],
                            value=prop["value"],
                            priority=prop.get("priority", 2)
                        )
                        st.session_state["global_chat_history"].append({
                            "role": "assistant",
                            "content": f"Confirmed: `{prop['key']}` registered into Echo Knowledge Base."
                        })
                        st.session_state["knowledge_proposal"] = None
                        st.rerun()
                with kp_c2:
                    if st.button("Dismiss", key="btn_reject_prop", use_container_width=True):
                        st.session_state["knowledge_proposal"] = None
                        st.rerun()

        # Docked Bottom Chat Input
        st.markdown('<div class="echo-input-dock">', unsafe_allow_html=True)
        active_prompt = st.chat_input("Inquire regarding historical archives, corporate context, or metrics...")
        st.markdown('</div>', unsafe_allow_html=True)

        if active_prompt:
            st.session_state["global_chat_history"].append({"role": "user", "content": active_prompt})

            with chat_box:
                st.markdown(
                    f'<div class="echo-msg-row-user">'
                    f'<div class="echo-user-bubble">{active_prompt}</div>'
                    f'<div class="echo-avatar-user">{SVG_USER_ICON}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                thinking_placeholder = st.empty()
                status_text = "Echo is searching the web..." if st.session_state["echo_source_web"] else "Echo is synthesizing..."
                thinking_placeholder.markdown(
                    f'<div class="echo-thinking-wrapper">'
                    f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                    f'<div class="echo-thinking-pill">'
                    f'<div class="echo-pulse-dot"></div> {status_text}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Source Ingestion Routing
            archives = fetch_meeting_archives(limit=100) if st.session_state["echo_source_archives"] else []
            web_context, web_sources = _perform_web_search(active_prompt) if st.session_state["echo_source_web"] else ("", [])
            
            answer, proposed_fact = _query_echo_backend(
                question=active_prompt,
                archive_records=archives,
                chat_history=st.session_state["global_chat_history"],
                web_context=web_context,
                model_name=st.session_state["echo_selected_model"],
                include_knowledge=st.session_state["echo_source_knowledge"]
            )
            
            thinking_placeholder.empty()
            st.session_state["global_chat_history"].append({
                "role": "assistant",
                "content": answer,
                "sources": web_sources
            })
            if proposed_fact:
                st.session_state["knowledge_proposal"] = proposed_fact

            st.rerun()


def _perform_web_search(query: str) -> tuple:
    """Fetches web context and clean source objects."""
    sources = []
    text_snippets = []
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
        if resp.status_code == 200:
            titles = re.findall(r'<a class="result__url"[^>]*>(.*?)</a>', resp.text)
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            urls = re.findall(r'<a class="result__url[^>]*href="([^"]+)"', resp.text)
            
            for i in range(min(4, len(snippets))):
                clean_snippet = re.sub(r'<.*?>', '', snippets[i]).strip()
                link = urls[i] if i < len(urls) else "#"
                raw_title = re.sub(r'<.*?>', '', titles[i]).strip() if i < len(titles) else f"Source {i+1}"
                
                domain = re.sub(r'^https?://(www\.)?', '', link).split('/')[0]
                pill_title = domain if domain else raw_title[:20]

                sources.append({"title": pill_title, "url": link})
                text_snippets.append(f"[{i+1}] {clean_snippet} (URL: {link})")
    except Exception:
        pass
    return ("\n".join(text_snippets), sources)


def _query_echo_backend(
    question: str, 
    archive_records: list, 
    chat_history: list, 
    web_context: str = "",
    model_name: str = "deepseek-chat",
    include_knowledge: bool = True
) -> tuple:
    """Synthesizes dynamic sources based on configuration with fallback error handling."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "DeepSeek API Key is missing in Streamlit Secrets.", None

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1) if archive_records else "[]"

    if include_knowledge:
        context_data = fetch_echo_context()
        team_list = ", ".join(context_data.get('team', []))
        jargon_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('jargon', {}).items()])
        projects = ", ".join(context_data.get('projects', []))
        knowledge_section = f"""
ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
---------------------------------------
TEAM MEMBERS: {team_list}
ACTIVE PROJECTS: {projects}
TECHNICAL JARGON:
{jargon_list}
"""
    else:
        knowledge_section = ""

    current_date_str = datetime.now().strftime("%A, %B %d, %Y")
    web_section = f"\nLIVE WEB SEARCH RESULTS:\n{web_context}\n" if web_context else ""

    context_string = f"""
CURRENT DATE & TIME: {current_date_str}
{knowledge_section}
{web_section}
"""

    citation_rule = (
        "Incorporate web facts smoothly into the response. Link structures are managed by the UI pills."
        if web_context else ""
    )

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        f"The current date is {current_date_str}. "
        "Synthesize available sources and archives accurately. Format responses concisely using Markdown headings, lists, and tables where appropriate. No emojis. "
        f"{citation_rule} "
        "Determine if the user's input contains a new terminology definition, project assignment, or role update that could belong in the knowledge base. "
        "Respond in strict JSON format matching the schema: "
        "{"
        "  \"response\": \"Your thorough Markdown response\", "
        "  \"propose_knowledge\": null OR {\"category\": \"team|jargon|projects\", \"key\": \"Name/Term\", \"value\": \"Definition/Role\", \"priority\": 2}"
        "}"
        f"\n\n{context_string}\n"
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:24000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 1500
    }

    if model_name == "deepseek-chat":
        payload["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            raw_content = resp.json()["choices"][0]["message"]["content"].strip()

            # Clean markdown code blocks if present
            cleaned = re.sub(r"^```json\s*", "", raw_content, flags=re.MULTILINE)
            cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE).strip()

            try:
                result = json.loads(cleaned)
                return result.get("response", cleaned), result.get("propose_knowledge")
            except json.JSONDecodeError:
                match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group(1))
                        return result.get("response", cleaned), result.get("propose_knowledge")
                    except Exception:
                        pass
                
                return raw_content, None

        return f"Service notice ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Analysis exception: {e}", None
