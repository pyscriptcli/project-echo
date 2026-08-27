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
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 5px;">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

# Fonts: Playfair Display (Executive Serif), Cinzel (Header tags), Montserrat (Clean body)
CHAT_PRIME_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Montserrat:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,600;1,400;1,600&display=swap');

/* Main Executive Card Frame */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) {
    background: #0D131F !important;
    background-image: 
        linear-gradient(rgba(212, 175, 55, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(212, 175, 55, 0.04) 1px, transparent 1px) !important;
    background-size: 28px 28px !important;
    border: 1px solid rgba(212, 175, 55, 0.22) !important;
    border-radius: 6px !important;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(212, 175, 55, 0.15) !important;
    overflow: hidden !important;
    padding: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
    gap: 0 !important;
    padding: 0.75rem 1rem !important;
}

/* Header Typography & Gold Accent Divider */
.echo-header-box {
    text-align: center;
    padding-bottom: 0.5rem;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(212, 175, 55, 0.15);
}

.echo-kicker {
    font-family: 'Cinzel', serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #D4AF37;
    margin-bottom: 2px;
}

.echo-title {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.25rem;
    font-weight: 400;
    color: #F8FAFC;
    letter-spacing: 0.01em;
    margin: 0;
}

.echo-gold-bar {
    width: 28px;
    height: 1.5px;
    background: #D4AF37;
    margin: 4px auto 0 auto;
}

/* Fullscreen Immersive Mode */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-fullscreen-active) {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    max-width: 100vw !important;
    max-height: 100vh !important;
    z-index: 999999 !important;
    border-radius: 0 !important;
    background: #080C14 !important;
    padding: 1rem 3rem !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

/* Inner Scrollable Chat Feed */
.echo-chat-box-container div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(7, 10, 18, 0.65) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(212, 175, 55, 0.12) !important;
    border-radius: 4px !important;
    overflow-y: auto !important;
    padding: 0.75rem 0.85rem !important;
}

/* User Message: Dark Navy/Charcoal Bubble with Gold Border */
.echo-msg-row-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 8px;
    width: 100%;
    margin-bottom: 0.85rem;
}

.echo-user-bubble {
    font-family: 'Montserrat', sans-serif;
    background: #111A2B;
    color: #F1F5F9 !important;
    border: 1px solid rgba(212, 175, 55, 0.45);
    padding: 0.55rem 0.85rem;
    border-radius: 12px 2px 12px 12px;
    max-width: 78%;
    font-size: 0.84rem;
    line-height: 1.45;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
    word-break: break-word;
}
.echo-user-bubble p {
    color: #F1F5F9 !important;
    margin: 0;
}

.echo-avatar-user {
    width: 24px;
    height: 24px;
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
    margin-bottom: 1.1rem;
    background: transparent;
}

.echo-assistant-header {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 0.25rem;
}

.echo-avatar-assistant {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #090E17;
    border: 1px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 0 8px rgba(212, 175, 55, 0.25);
}

.echo-assistant-title {
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #D4AF37;
}

.echo-assistant-badge-gold {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.58rem;
    padding: 1px 4px;
    border-radius: 2px;
    background: rgba(212, 175, 55, 0.15);
    color: #F8FAFC;
    font-weight: 600;
    border: 0.5px solid rgba(212, 175, 55, 0.4);
}

.echo-assistant-body {
    font-family: 'Montserrat', sans-serif;
    padding-left: 30px;
    color: #CBD5E1;
    font-size: 0.84rem;
    line-height: 1.55;
}
.echo-assistant-body strong {
    color: #F8FAFC;
}

/* Sources Pills */
.echo-sources-container {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 0.5rem;
    padding-left: 30px;
}
.echo-source-pill {
    font-family: 'Montserrat', sans-serif;
    display: inline-flex;
    align-items: center;
    background: #090E17;
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 0.70rem;
    color: #D4AF37 !important;
    text-decoration: none !important;
    transition: all 0.2s ease;
}
.echo-source-pill:hover {
    background: #111A2B;
    border-color: #D4AF37;
    color: #FFFFFF !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3);
}

/* Markdown Tables Styled in Prime Dark & Gold */
.echo-assistant-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.6rem 0;
    font-size: 0.78rem;
    background: #090E17;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid rgba(212, 175, 55, 0.2);
}
.echo-assistant-body th {
    font-family: 'Cinzel', serif;
    background: #111A2B;
    color: #D4AF37;
    font-weight: 700;
    letter-spacing: 0.05em;
    border: 1px solid rgba(212, 175, 55, 0.2);
    padding: 6px 10px;
    text-align: left;
}
.echo-assistant-body td {
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 6px 10px;
    color: #CBD5E1;
}

/* Thinking Indicator */
.echo-thinking-wrapper {
    display: flex;
    align-items: center;
    gap: 8px;
    padding-left: 0.2rem;
    margin-bottom: 0.8rem;
}
.echo-thinking-pill {
    font-family: 'Montserrat', sans-serif;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 4px;
    background: #111A2B;
    border: 1px solid rgba(212, 175, 55, 0.3);
    font-size: 0.75rem;
    color: #D4AF37;
}
.echo-pulse-dot {
    width: 6px;
    height: 6px;
    background-color: #D4AF37;
    border-radius: 50%;
    animation: echo-pulse 1.4s infinite ease-in-out both;
}
@keyframes echo-pulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.2; }
    40% { transform: scale(1); opacity: 1; }
}

/* Knowledge Proposal Inline Prompt */
.echo-knowledge-card {
    background: #111A2B;
    border: 1px solid #D4AF37;
    border-radius: 4px;
    padding: 0.6rem 0.8rem;
    margin-top: 0.4rem;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.4);
}

/* Bottom Bar Docked Styling */
.echo-input-dock {
    padding-top: 0.35rem !important;
    display: flex;
    flex-direction: column;
}

div[data-testid="stChatInput"] > div {
    background: #090E17 !important;
    border: 1px solid rgba(212, 175, 55, 0.35) !important;
    border-radius: 4px !important;
    box-shadow: none !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Montserrat', sans-serif !important;
    color: #F8FAFC !important;
    font-size: 0.84rem !important;
}

/* Streamlit Toggle Overwrite */
div[data-testid="stToggle"] label p {
    font-family: 'Cinzel', serif !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    color: #D4AF37 !important;
    text-transform: uppercase !important;
}
</style>
"""

def render_echo_chat(container=None, height=720, title="Global Intelligence", subtitle="BY THE NUMBERS"):
    target = container if container else st
    st.markdown(CHAT_PRIME_THEME_CSS, unsafe_allow_html=True)

    # State Initializations
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "knowledge_proposal" not in st.session_state:
        st.session_state["knowledge_proposal"] = None
    if "chat_is_fullscreen" not in st.session_state:
        st.session_state["chat_is_fullscreen"] = False
    if "echo_web_search_enabled" not in st.session_state:
        st.session_state["echo_web_search_enabled"] = False

    is_fs = st.session_state["chat_is_fullscreen"]
    chat_scroll_height = 720 if is_fs else max(260, int(height) - 170)

    with target.container(border=True):
        st.markdown('<div class="echo-main-card-scope"></div>', unsafe_allow_html=True)
        if is_fs:
            st.markdown('<div class="echo-fullscreen-active"></div>', unsafe_allow_html=True)

        # Header Controls & Executive Titles
        h_left, h_mid, h_right = st.columns([0.08, 0.84, 0.08])
        with h_left:
            st.markdown(f'<div style="padding-top:4px;">{SVG_ECHO_LOGO}</div>', unsafe_allow_html=True)

        with h_mid:
            st.markdown(
                f'<div class="echo-header-box">'
                f'<div class="echo-kicker">{subtitle}</div>'
                f'<h2 class="echo-title">{title}</h2>'
                f'<div class="echo-gold-bar"></div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with h_right:
            c_fs, c_clr = st.columns(2)
            with c_fs:
                fs_icon = ":material/fullscreen_exit:" if is_fs else ":material/fullscreen:"
                if st.button("", icon=fs_icon, key="btn_toggle_fullscreen", help="Fullscreen Toggle"):
                    st.session_state["chat_is_fullscreen"] = not st.session_state["chat_is_fullscreen"]
                    st.rerun()
            with c_clr:
                if st.button("", icon=":material/delete_sweep:", key="btn_clear_global_chat", help="Clear conversation"):
                    st.session_state["global_chat_history"] = []
                    st.session_state["knowledge_proposal"] = None
                    st.rerun()

        # ==========================================
        # --- Chat Stream Feed ---
        # ==========================================
        st.markdown('<div class="echo-chat-box-container">', unsafe_allow_html=True)
        chat_box = st.container(height=chat_scroll_height)
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

        # Knowledge Proposal Prompt Card
        if st.session_state["knowledge_proposal"]:
            prop = st.session_state["knowledge_proposal"]
            with st.container():
                st.markdown(
                    f'<div class="echo-knowledge-card">'
                    f'<div style="font-family:\'Cinzel\',serif; font-size:0.7rem; font-weight:700; color:#D4AF37; margin-bottom:2px;">'
                    f'{SVG_BRAIN_ICON} Knowledge Base Candidate'
                    f'</div>'
                    f'<div style="font-family:\'Montserrat\',sans-serif; font-size:0.78rem; color:#CBD5E1; margin-bottom:6px;">'
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

        # Docked Bottom Controls
        st.markdown('<div class="echo-input-dock">', unsafe_allow_html=True)
        _, tool_right = st.columns([0.80, 0.20])
        with tool_right:
            use_web = st.toggle("Search Web", value=st.session_state["echo_web_search_enabled"], key="toggle_web_search")
            st.session_state["echo_web_search_enabled"] = use_web

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
                status_text = "Echo is searching the web..." if use_web else "Echo is synthesizing..."
                thinking_placeholder.markdown(
                    f'<div class="echo-thinking-wrapper">'
                    f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                    f'<div class="echo-thinking-pill">'
                    f'<div class="echo-pulse-dot"></div> {status_text}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            archives = fetch_meeting_archives(limit=100)
            web_context, web_sources = _perform_web_search(active_prompt) if use_web else ("", [])
            
            answer, proposed_fact = _query_echo_backend(
                question=active_prompt,
                archive_records=archives,
                chat_history=st.session_state["global_chat_history"],
                web_context=web_context
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


def _query_echo_backend(question: str, archive_records: list, chat_history: list, web_context: str = "") -> tuple:
    """Synthesizes archives and optional web search results."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "DeepSeek API Key is missing in Streamlit Secrets.", None

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)

    context_data = fetch_echo_context()
    team_list = ", ".join(context_data.get('team', []))
    jargon_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('jargon', {}).items()])
    projects = ", ".join(context_data.get('projects', []))

    current_date_str = datetime.now().strftime("%A, %B %d, %Y")
    web_section = f"\nLIVE WEB SEARCH RESULTS:\n{web_context}\n" if web_context else ""

    context_string = f"""
CURRENT DATE & TIME: {current_date_str}
ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
---------------------------------------
TEAM MEMBERS: {team_list}
ACTIVE PROJECTS: {projects}
TECHNICAL JARGON:
{jargon_list}
{web_section}
"""

    citation_rule = (
        "Incorporate web facts smoothly into the response. Link structures are managed by the UI pills."
        if web_context else ""
    )

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        f"The current date is {current_date_str}. "
        "Synthesize meeting archives and web findings accurately. Format responses concisely using Markdown headings, lists, and tables where appropriate. No emojis. "
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
        "model": "deepseek-chat",
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "max_tokens": 1000
    }

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            result = json.loads(resp.json()["choices"][0]["message"]["content"])
            return result.get("response", ""), result.get("propose_knowledge")
        return f"Service notice ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Analysis exception: {e}", None
