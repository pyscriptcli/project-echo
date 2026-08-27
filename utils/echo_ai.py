import streamlit as st
import requests
import json
import pandas as pd
import re
from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context

# --- Pure SVG Icon Assets ---
SVG_ECHO_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
</svg>
"""

SVG_USER_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
</svg>
"""

SVG_BRAIN_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

CHAT_GLASSMORPHISM_CSS = """
<style>
/* Outer Card Container - Frosted Glass without outer scrollbar */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) {
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(16px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(16px) saturate(160%) !important;
    border: 1px solid rgba(255, 255, 255, 0.65) !important;
    border-radius: 18px !important;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
    overflow: hidden !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    overflow: hidden !important;
    gap: 0.5rem !important;
}

/* Tab contents filling full remaining height */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) div[data-testid="stTabs"] {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 0 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) div[data-testid="stTabContent"] {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    min-height: 0 !important;
    overflow: hidden !important;
}

/* Fullscreen Viewport Mode */
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
    background: rgba(248, 249, 250, 0.96) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    padding: 1.5rem 3rem !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}

/* Inner Scrollable Chat Feed */
.echo-chat-box-container {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}

.echo-chat-box-container div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.35) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    border-radius: 14px !important;
    height: 100% !important;
    overflow-y: auto !important;
}

/* User Message Bubble */
.echo-msg-row-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 10px;
    width: 100%;
    margin-bottom: 1.5rem;
}

.echo-user-bubble {
    background: rgba(17, 17, 17, 0.94);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    color: #F9FAFB !important;
    border: 1px solid #D4AF37;
    padding: 0.8rem 1.25rem;
    border-radius: 18px 4px 18px 18px;
    max-width: 78%;
    font-size: 0.92rem;
    line-height: 1.55;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22), 0 0 10px rgba(212, 175, 55, 0.25);
    word-break: break-word;
}
.echo-user-bubble p {
    color: #F9FAFB !important;
    margin: 0;
}

.echo-avatar-user {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(17, 17, 17, 0.95);
    border: 1.5px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
}

/* Assistant Message Row */
.echo-msg-row-assistant {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: 1.75rem;
    background: transparent;
}

.echo-assistant-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.4rem;
}

.echo-avatar-assistant {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(17, 17, 17, 0.95) 0%, rgba(31, 41, 55, 0.95) 100%);
    border: 1.5px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 3px 10px rgba(212, 175, 55, 0.3);
}

.echo-assistant-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: 0.02em;
}

.echo-assistant-badge-gold {
    font-size: 0.68rem;
    padding: 2px 7px;
    border-radius: 6px;
    background: rgba(254, 243, 199, 0.85);
    color: #92400E;
    font-weight: 700;
    border: 1px solid rgba(253, 230, 138, 0.8);
    backdrop-filter: blur(4px);
}

.echo-assistant-body {
    padding-left: 42px;
    color: #111827;
    font-size: 0.94rem;
    line-height: 1.65;
}

/* Markdown Tables */
.echo-assistant-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.88rem;
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(229, 231, 235, 0.8);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}
.echo-assistant-body th {
    background: #111111;
    color: #D4AF37;
    font-weight: 600;
    border: 1px solid #2B2D31;
    padding: 10px 14px;
    text-align: left;
}
.echo-assistant-body td {
    border: 1px solid rgba(229, 231, 235, 0.8);
    padding: 10px 14px;
    color: #1F2937;
}

/* Thinking Indicator Pill */
.echo-thinking-wrapper {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-left: 0.2rem;
    margin-bottom: 1.25rem;
}
.echo-thinking-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    font-size: 0.82rem;
    color: #374151;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
.echo-pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #D4AF37;
    border-radius: 50%;
    animation: echo-pulse 1.4s infinite ease-in-out both;
}
@keyframes echo-pulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

/* Persistent Bottom Input Bar & Toolbar */
.echo-input-dock {
    flex-shrink: 0 !important;
    padding-top: 0.35rem !important;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.echo-input-dock div[data-testid="stChatInput"] {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
}
.echo-input-dock div[data-testid="stChatInput"] > div {
    background: rgba(255, 255, 255, 0.85) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}
.echo-input-dock div[data-testid="stChatInput"] textarea {
    color: #111827 !important;
}
</style>
"""

def render_echo_chat(container=None, height=720, title="Ask Echo — Global Intelligence", caption="Synthesize meeting archives, transcripts, and action logs."):
    target = container if container else st
    st.markdown(CHAT_GLASSMORPHISM_CSS, unsafe_allow_html=True)

    # State Initializations
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "extracted_context_df" not in st.session_state:
        st.session_state["extracted_context_df"] = None
    if "knowledge_proposal" not in st.session_state:
        st.session_state["knowledge_proposal"] = None
    if "chat_is_fullscreen" not in st.session_state:
        st.session_state["chat_is_fullscreen"] = False
    if "echo_web_search_enabled" not in st.session_state:
        st.session_state["echo_web_search_enabled"] = False

    is_fs = st.session_state["chat_is_fullscreen"]
    outer_container_height = 920 if is_fs else int(height)
    inner_scroll_height = outer_container_height - 210

    with target.container(height=outer_container_height, border=True):
        st.markdown('<div class="echo-main-card-scope"></div>', unsafe_allow_html=True)
        if is_fs:
            st.markdown('<div class="echo-fullscreen-active"></div>', unsafe_allow_html=True)

        # Header Controls
        header_col, btn_fs_col, btn_clear_col = st.columns([0.88, 0.06, 0.06])
        with header_col:
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:8px;">'
                f'{SVG_ECHO_LOGO}<span style="font-family: \'Playfair Display\', serif; font-size: 1.15rem; font-weight:600; color:#111827;">{title}</span>'
                f'</div>'
                f'<p style="font-size:0.8rem; color:#6B7280; margin: 0 0 0.25rem 0;">{caption}</p>',
                unsafe_allow_html=True
            )
        with btn_fs_col:
            fs_icon = ":material/fullscreen_exit:" if is_fs else ":material/fullscreen:"
            fs_help = "Exit Fullscreen" if is_fs else "Fullscreen"
            if st.button("", icon=fs_icon, key="btn_toggle_fullscreen", help=fs_help):
                st.session_state["chat_is_fullscreen"] = not st.session_state["chat_is_fullscreen"]
                st.rerun()

        with btn_clear_col:
            if st.button("", icon=":material/delete_sweep:", key="btn_clear_global_chat", help="Reset conversation"):
                st.session_state["global_chat_history"] = []
                st.session_state["knowledge_proposal"] = None
                st.rerun()

        tab_chat, tab_context = st.tabs(["Chat", "Context Manager"])

        # ==========================================
        # --- TAB 1: Chat Feed ---
        # ==========================================
        with tab_chat:
            st.markdown('<div class="echo-chat-box-container">', unsafe_allow_html=True)
            chat_box = st.container(height=inner_scroll_height)
            st.markdown('</div>', unsafe_allow_html=True)

            with chat_box:
                if not st.session_state["global_chat_history"]:
                    st.markdown(
                        '<div class="echo-msg-row-assistant">'
                        '<div class="echo-assistant-header">'
                        f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                        '<span class="echo-assistant-title">Echo Intelligence</span>'
                        '<span class="echo-assistant-badge-gold">AI</span>'
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
                                '<span class="echo-assistant-title">Echo Intelligence</span>'
                                '<span class="echo-assistant-badge-gold">AI</span>'
                                '</div>'
                                '<div class="echo-assistant-body">',
                                unsafe_allow_html=True
                            )
                            st.markdown(msg["content"])
                            st.markdown('</div></div>', unsafe_allow_html=True)

            # Active Knowledge Proposal Card
            if st.session_state["knowledge_proposal"]:
                prop = st.session_state["knowledge_proposal"]
                with st.container(border=True):
                    st.markdown(
                        f'<div style="display:flex; align-items:center; gap:6px; font-size:0.75rem; font-weight:700; color:#D4AF37; text-transform:uppercase; margin-bottom:4px;">'
                        f'{SVG_BRAIN_ICON} Knowledge Base Addition Detected'
                        f'</div>'
                        f'<p style="font-size:0.84rem; margin:0 0 0.5rem 0; color:#374151;">'
                        f'Register <b>{prop.get("key")}</b> ({prop.get("category")}) to the Echo Knowledge Base?<br/>'
                        f'<i>Value: {prop.get("value")}</i>'
                        f'</p>',
                        unsafe_allow_html=True
                    )
                    c_approve, c_reject = st.columns([1, 1])
                    with c_approve:
                        if st.button("Confirm Addition", key="btn_confirm_prop", type="primary", use_container_width=True):
                            upsert_echo_context(
                                category=prop["category"],
                                key=prop["key"],
                                value=prop["value"],
                                priority=prop.get("priority", 2)
                            )
                            st.session_state["global_chat_history"].append({
                                "role": "assistant",
                                "content": f"Confirmed: `{prop['key']}` has been recorded into the Echo Knowledge Base."
                            })
                            st.session_state["knowledge_proposal"] = None
                            st.rerun()
                    with c_reject:
                        if st.button("Dismiss", key="btn_reject_prop", use_container_width=True):
                            st.session_state["knowledge_proposal"] = None
                            st.rerun()

            # Docked Chat Input Area + Web Search Tick
            st.markdown('<div class="echo-input-dock">', unsafe_allow_html=True)
            
            tool_col1, tool_col2 = st.columns([0.8, 0.2])
            with tool_col2:
                use_web = st.toggle("Search Web", value=st.session_state["echo_web_search_enabled"], key="toggle_web_search", help="Enable to fetch live web sources and cite them in responses.")
                st.session_state["echo_web_search_enabled"] = use_web

            active_prompt = st.chat_input("Ask a question, identify project facts, or provide knowledge updates...")
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
                    search_label = "Echo is searching the web and thinking..." if use_web else "Echo is thinking..."
                    thinking_placeholder.markdown(
                        f'<div class="echo-thinking-wrapper">'
                        f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                        f'<div class="echo-thinking-pill">'
                        f'<div class="echo-pulse-dot"></div> {search_label}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                archives = fetch_meeting_archives(limit=100)
                web_context = _perform_web_search(active_prompt) if use_web else ""
                
                answer, proposed_fact = _query_echo_backend(
                    question=active_prompt,
                    archive_records=archives,
                    chat_history=st.session_state["global_chat_history"],
                    web_context=web_context
                )
                
                thinking_placeholder.empty()
                st.session_state["global_chat_history"].append({"role": "assistant", "content": answer})
                if proposed_fact:
                    st.session_state["knowledge_proposal"] = proposed_fact

                st.rerun()

        # ==========================================
        # --- TAB 2: Context Manager ---
        # ==========================================
        with tab_context:
            _render_context_manager_subtab()


def _render_context_manager_subtab():
    """Renders structured dual-mode Context Management UI."""
    mode = st.radio(
        "Context Input Mode",
        options=["AI Smart Extraction", "Manual Entry"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if mode == "AI Smart Extraction":
        raw_text = st.text_area(
            "Raw Information Dump",
            height=100,
            placeholder="Paste raw corporate updates, abbreviations, or team designations here...",
            label_visibility="collapsed"
        )
        col_act1, col_act2 = st.columns([1.5, 1])
        with col_act1:
            if st.button("Structure Unstructured Notes", key="btn_run_ai_struct", use_container_width=True, type="primary"):
                if raw_text.strip():
                    with st.spinner("Extracting..."):
                        extracted = _extract_context_with_ai(raw_text)
                        if extracted:
                            st.session_state["extracted_context_df"] = pd.DataFrame(extracted)
                            st.rerun()
                        else:
                            st.error("No actionable definitions or entities identified.")
                else:
                    st.warning("Please supply context text.")
        with col_act2:
            if st.button("Clear Working Table", key="btn_reset_tbl", use_container_width=True):
                st.session_state["extracted_context_df"] = None
                st.rerun()

    else:
        st.caption("Add an individual entity record directly into the staged schema.")
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns([1.2, 1.5, 2.5, 0.8, 1])
        with m_col1:
            m_cat = st.selectbox("Category", options=["team", "jargon", "projects"], key="manual_cat")
        with m_col2:
            m_key = st.text_input("Entity / Key", placeholder="e.g., QBR", key="manual_key")
        with m_col3:
            m_val = st.text_input("Definition / Role", placeholder="Quarterly Business Review", key="manual_val")
        with m_col4:
            m_prio = st.number_input("Priority", min_value=1, max_value=5, value=1, key="manual_prio")
        with m_col5:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Add Row", key="btn_add_manual_row", use_container_width=True):
                if m_key.strip() and m_val.strip():
                    new_entry = pd.DataFrame([{
                        "category": m_cat,
                        "key": m_key.strip(),
                        "value": m_val.strip(),
                        "priority": int(m_prio)
                    }])
                    if st.session_state["extracted_context_df"] is None:
                        st.session_state["extracted_context_df"] = new_entry
                    else:
                        st.session_state["extracted_context_df"] = pd.concat([st.session_state["extracted_context_df"], new_entry], ignore_index=True)
                    st.rerun()
                else:
                    st.error("Key and Value required.")

    # Shared Editable Review Data Grid
    if st.session_state["extracted_context_df"] is not None and not st.session_state["extracted_context_df"].empty:
        st.markdown("---")
        st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#111827;'>Staged Knowledge Base Rows</p>", unsafe_allow_html=True)

        column_config = {
            "category": st.column_config.SelectboxColumn("Category", options=["team", "jargon", "projects"], required=True),
            "key": st.column_config.TextColumn("Key / Entity", required=True),
            "value": st.column_config.TextColumn("Value / Definition", required=True, width="large"),
            "priority": st.column_config.NumberColumn("Priority (1-5)", min_value=1, max_value=5, default=1)
        }

        edited_df = st.data_editor(
            st.session_state["extracted_context_df"],
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="vault_data_editor"
        )

        if st.button("Save All to Knowledge Base", key="btn_commit_vault", type="primary", use_container_width=True):
            saved = 0
            with st.spinner("Saving..."):
                for _, row in edited_df.iterrows():
                    if pd.notna(row['category']) and pd.notna(row['key']) and pd.notna(row['value']):
                        if upsert_echo_context(
                            category=str(row['category']),
                            key=str(row['key']),
                            value=str(row['value']),
                            priority=int(row['priority']) if pd.notna(row['priority']) else 1
                        ):
                            saved += 1
            if saved > 0:
                st.success(f"Successfully committed {saved} item(s) to Echo Brain.")
                st.session_state["extracted_context_df"] = None
                st.rerun()


def _perform_web_search(query: str) -> str:
    """Fetches real-time web context using DuckDuckGo HTML endpoint."""
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
        if resp.status_code == 200:
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            urls = re.findall(r'<a class="result__url[^>]*href="([^"]+)"', resp.text)
            
            clean_results = []
            for i in range(min(5, len(snippets))):
                clean_text = re.sub(r'<.*?>', '', snippets[i]).strip()
                link = urls[i] if i < len(urls) else ""
                clean_results.append(f"[{i+1}] Source: {clean_text} (URL: {link})")
            
            if clean_results:
                return "\n".join(clean_results)
    except Exception:
        pass
    return ""


def _extract_context_with_ai(raw_text: str) -> list:
    """Invokes LLM extraction schema on raw unstructured entries."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        st.error("DeepSeek API Key configuration missing.")
        return []

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    system_prompt = (
        "Extract enterprise facts from text into a valid JSON object with key 'items'. "
        "Each array entry must contain: 'category' ('team', 'jargon', or 'projects'), "
        "'key' (term/proper noun), 'value' (definition/description), and 'priority' (integer 1-5)."
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 800
    }

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            parsed = json.loads(resp.json()["choices"][0]["message"]["content"])
            return parsed.get("items", [])
        return []
    except Exception as e:
        st.error(f"Extraction error: {e}")
        return []


def _query_echo_backend(question: str, archive_records: list, chat_history: list, web_context: str = "") -> tuple:
    """Synthesizes archives and optional web search results while providing clean citations."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "DeepSeek API Key is missing in Streamlit Secrets.", None

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)

    context_data = fetch_echo_context()
    team_list = ", ".join(context_data.get('team', []))
    jargon_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('jargon', {}).items()])
    projects = ", ".join(context_data.get('projects', []))

    web_section = f"\nLIVE WEB SEARCH RESULTS:\n{web_context}\n" if web_context else ""

    context_string = f"""
ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
---------------------------------------
TEAM MEMBERS: {team_list}
ACTIVE PROJECTS: {projects}
TECHNICAL JARGON:
{jargon_list}
{web_section}
"""

    citation_rule = (
        "When using LIVE WEB SEARCH RESULTS, cite your claims with hyperlinks or footnote markers pointing directly to the sources provided. "
        if web_context else ""
    )

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Synthesize meeting archives and web findings accurately. Format responses cleanly using standard Markdown headings, lists, and Markdown tables where appropriate. No emojis. "
        f"{citation_rule}"
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
