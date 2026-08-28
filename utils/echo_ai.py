import streamlit as st
import requests
import json
import re
import pandas as pd
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
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
</svg>
"""

SVG_GLOBE_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 3px;">
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

CHAT_COMPACT_ALIGNED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,500;1,600&family=Inter:wght@400;500;600&display=swap');

/* Enable page/container scrolling while hiding scrollbars globally */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scrollbar-width: none !important; /* Firefox */
    -ms-overflow-style: none !important;  /* IE and Edge */
    padding-top: 0.3rem !important;
    padding-bottom: 0.3rem !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Hide scrollbar for Chrome, Safari, and Opera */
html::-webkit-scrollbar, 
body::-webkit-scrollbar, 
[data-testid="stAppViewContainer"]::-webkit-scrollbar, 
.main::-webkit-scrollbar, 
.block-container::-webkit-scrollbar,
div[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar,
.echo-chat-box-container div[data-testid="stVerticalBlockBorderWrapper"]::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    background: transparent !important;
}

/* Outer Card Container */
div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) {
    background-color: transparent !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 8px !important;
    padding: 0 !important;
    box-shadow: none !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    height: calc(100vh - 130px) !important;
    max-height: calc(100vh - 130px) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(.echo-main-card-scope) > div[data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    max-height: 100% !important;
    padding: 0.5rem 0.85rem !important;
    gap: 0 !important;
    box-sizing: border-box !important;
}

/* Header Alignment */
.echo-header-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    height: 36px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
    padding-bottom: 6px;
    margin-bottom: 6px;
    flex-shrink: 0 !important;
}

.echo-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-style: italic !important;
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: #1A2B4C !important;
    margin: 0 !important;
    line-height: 1 !important;
    letter-spacing: 0.01em !important;
}

/* Header Controls Pill Buttons */
div[data-testid="stPopover"] > button {
    background-color: #111A2B !important;
    color: #D4AF37 !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    padding: 0.15rem 0.5rem !important;
    height: 28px !important;
    min-height: 28px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stPopover"] > button:hover {
    border-color: #F1C40F !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3) !important;
}

div[data-testid="stButton"] > button {
    background-color: #111A2B !important;
    color: #D4AF37 !important;
    border: 1px solid #D4AF37 !important;
    border-radius: 20px !important;
    height: 28px !important;
    min-height: 28px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #F1C40F !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3) !important;
}

/* Inner Chat Box Container - Scrollable without visible scrollbars */
.echo-chat-box-container {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}

.echo-chat-box-container div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(4px) !important;
    -webkit-backdrop-filter: blur(4px) !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    border-radius: 6px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    padding: 0.65rem 0.9rem !important;
    height: 100% !important;
}

/* User Message Bubble */
.echo-msg-row-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 6px;
    width: 100%;
    margin-bottom: 0.65rem;
}

.echo-user-bubble {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    background: #111A2B;
    color: #FFFFFF !important;
    border: 1px solid #D4AF37;
    padding: 0.4rem 0.75rem;
    border-radius: 10px 2px 10px 10px;
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

/* Assistant Message */
.echo-msg-row-assistant {
    display: flex;
    flex-direction: column;
    width: 100%;
    margin-bottom: 0.75rem;
    background: transparent;
}

.echo-assistant-header {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-bottom: 0.15rem;
}

.echo-avatar-assistant {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #111A2B;
    border: 1px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.echo-assistant-title {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: 0.75rem;
    font-weight: 600;
    color: #1A2B4C;
}

.echo-assistant-badge-gold {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    font-size: 0.55rem;
    padding: 1px 4px;
    border-radius: 2px;
    background: #FEF3C7;
    color: #92400E;
    font-weight: 600;
    border: 0.5px solid #FDE68A;
}

.echo-assistant-body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    padding-left: 23px;
    color: #374151;
    font-size: 0.83rem;
    line-height: 1.5;
}
.echo-assistant-body strong {
    color: #111827;
}

/* Sources Pills */
.echo-sources-container {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 0.35rem;
    padding-left: 23px;
}
.echo-source-pill {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    display: inline-flex;
    align-items: center;
    background: #111A2B;
    border: 1px solid #D4AF37;
    border-radius: 12px;
    padding: 1px 7px;
    font-size: 0.68rem;
    color: #D4AF37 !important;
    text-decoration: none !important;
    font-weight: 500;
    transition: all 0.2s ease;
}
.echo-source-pill:hover {
    border-color: #F1C40F;
    color: #FFFFFF !important;
    box-shadow: 0 0 6px rgba(212, 175, 55, 0.3);
}

/* Tables */
.echo-assistant-body table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.4rem 0;
    font-size: 0.78rem;
    background: #FFFFFF;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #E2E8F0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}
.echo-assistant-body th {
    background: #111A2B;
    color: #D4AF37;
    font-weight: 600;
    border: 1px solid #334155;
    padding: 4px 7px;
    text-align: left;
}
.echo-assistant-body td {
    border: 1px solid #E2E8F0;
    padding: 4px 7px;
    color: #374151;
}

/* Thinking Indicator */
.echo-thinking-wrapper {
    display: flex;
    align-items: center;
    gap: 5px;
    padding-left: 0.2rem;
    margin-bottom: 0.45rem;
}
.echo-thinking-pill {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 7px;
    border-radius: 12px;
    background: #F8FAFC;
    border: 1px solid rgba(212, 175, 55, 0.35);
    font-size: 0.70rem;
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

/* Inline Candidate Prompt Card */
.echo-context-candidate-card {
    background: #FFFFFF;
    border: 1px solid #D4AF37;
    border-radius: 6px;
    padding: 0.45rem 0.65rem;
    margin-top: 0.35rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
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
    border-radius: 20px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    padding: 2px 8px !important;
}

div[data-testid="stChatInput"] textarea {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #0F172A !important;
    font-size: 0.84rem !important;
}
</style>
"""

@st.dialog("Echo Context Manager", width="large")
def render_context_popup_dialog():
    """Modal popup for manual and AI-assisted context knowledge additions."""
    if "extracted_context_df" not in st.session_state:
        st.session_state["extracted_context_df"] = None

    mode = st.radio(
        "Mode",
        options=["AI Smart Extraction", "Manual Row Entry"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if mode == "AI Smart Extraction":
        raw_text = st.text_area(
            "Raw Context / Knowledge Dump",
            height=140,
            placeholder="Paste raw unstructured notes, custom tables, logs, property records, or specs here..."
        )
        c_act1, c_act2 = st.columns([1.5, 1])
        with c_act1:
            if st.button("Extract Structured Knowledge", key="btn_dlg_run_ai", type="primary", use_container_width=True):
                if raw_text.strip():
                    with st.spinner("Extracting structured knowledge entries..."):
                        extracted = _extract_context_with_ai(raw_text)
                        if extracted:
                            st.session_state["extracted_context_df"] = pd.DataFrame(extracted)
                            st.rerun()
                        else:
                            st.error("No actionable knowledge items or entities identified.")
                else:
                    st.warning("Please supply context text.")
        with c_act2:
            if st.button("Reset Draft Table", key="btn_dlg_reset", use_container_width=True):
                st.session_state["extracted_context_df"] = None
                st.rerun()

    else:
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns([1.2, 1.5, 2.5, 0.8, 1])
        with m_col1:
            m_cat = st.selectbox("Category", options=["knowledge", "team", "jargon", "projects"], key="dlg_manual_cat")
        with m_col2:
            m_key = st.text_input("Key / Entity Identifier", placeholder="e.g. SRC-01162026-001 or Topic", key="dlg_manual_key")
        with m_col3:
            m_val = st.text_input("Value / Structured JSON", placeholder='e.g. {"property": "Sct. Gandia", "rate": 249}', key="dlg_manual_val")
        with m_col4:
            m_prio = st.number_input("Priority", min_value=1, max_value=5, value=2, key="dlg_manual_prio")
        with m_col5:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Add Row", key="btn_dlg_add_row", use_container_width=True):
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
                        st.session_state["extracted_context_df"] = pd.concat(
                            [st.session_state["extracted_context_df"], new_entry], ignore_index=True
                        )
                    st.rerun()
                else:
                    st.error("Key and Value required.")

    if st.session_state["extracted_context_df"] is not None and not st.session_state["extracted_context_df"].empty:
        st.markdown("---")
        st.markdown("<p style='font-size:0.80rem; font-weight:600; color:#1A2B4C;'>Staged Knowledge Rows (JSON Structured Values)</p>", unsafe_allow_html=True)

        column_config = {
            "category": st.column_config.SelectboxColumn("Category", options=["knowledge", "team", "jargon", "projects"], required=True),
            "key": st.column_config.TextColumn("Key / Entity Name", required=True),
            "value": st.column_config.TextColumn("Value (JSON / String)", required=True, width="large"),
            "priority": st.column_config.NumberColumn("Priority (1-5)", min_value=1, max_value=5, default=2)
        }

        edited_df = st.data_editor(
            st.session_state["extracted_context_df"],
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="dlg_data_editor"
        )

        if st.button("Commit to Echo Knowledge Base", key="btn_dlg_commit", type="primary", use_container_width=True):
            saved = 0
            with st.spinner("Saving knowledge records..."):
                for _, row in edited_df.iterrows():
                    if pd.notna(row['category']) and pd.notna(row['key']) and pd.notna(row['value']):
                        if upsert_echo_context(
                            category=str(row['category']),
                            key=str(row['key']),
                            value=str(row['value']),
                            priority=int(row['priority']) if pd.notna(row['priority']) else 2
                        ):
                            saved += 1
            if saved > 0:
                st.success(f"Saved {saved} record(s) to Echo Knowledge Base.")
                st.session_state["extracted_context_df"] = None
                st.rerun()


def render_echo_chat(container=None, height=620, title="Ask Echo", caption=None, subtitle=None):
    target = container if container else st
    st.markdown(CHAT_COMPACT_ALIGNED_CSS, unsafe_allow_html=True)

    # State Initializations
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "echo_selected_model" not in st.session_state:
        st.session_state["echo_selected_model"] = "deepseek-chat"
    if "echo_source_archives" not in st.session_state:
        st.session_state["echo_source_archives"] = True
    if "echo_source_knowledge" not in st.session_state:
        st.session_state["echo_source_knowledge"] = True
    if "echo_source_web" not in st.session_state:
        st.session_state["echo_source_web"] = False
    if "knowledge_proposal" not in st.session_state:
        st.session_state["knowledge_proposal"] = None

    safe_scroll_height = max(300, int(height) - 130) if height else 500

    with target.container(border=True):
        st.markdown('<div class="echo-main-card-scope"></div>', unsafe_allow_html=True)

        # Header Row: Logo, Title, and Action Controls
        h_left, h_right = st.columns([0.88, 0.12])
        with h_left:
            st.markdown(
                f'<div class="echo-header-bar">'
                f'{SVG_ECHO_LOGO}<span class="echo-title">{title}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        with h_right:
            c_settings, c_clr = st.columns(2)
            with c_settings:
                with st.popover("", icon=":material/settings:", help="Settings"):
                    st.markdown("<span style='font-size:0.75rem; font-weight:600; color:#854D0E;'>AI MODEL</span>", unsafe_allow_html=True)
                    st.session_state["echo_selected_model"] = st.selectbox(
                        "Model",
                        options=["deepseek-chat", "deepseek-reasoner"],
                        index=0,
                        label_visibility="collapsed"
                    )
                    st.markdown("---")
                    st.markdown("<span style='font-size:0.75rem; font-weight:600; color:#854D0E;'>DATA SOURCES</span>", unsafe_allow_html=True)
                    st.session_state["echo_source_archives"] = st.checkbox("Meeting Archives", value=st.session_state["echo_source_archives"])
                    st.session_state["echo_source_knowledge"] = st.checkbox("Echo Knowledge Base", value=st.session_state["echo_source_knowledge"])
                    st.session_state["echo_source_web"] = st.checkbox("Search Web", value=st.session_state["echo_source_web"])
                    
                    st.markdown("---")
                    st.markdown("<span style='font-size:0.75rem; font-weight:600; color:#854D0E;'>KNOWLEDGE MANAGEMENT</span>", unsafe_allow_html=True)
                    if st.button("Open Context Manager", key="btn_trigger_context_dialog", use_container_width=True):
                        render_context_popup_dialog()

            with c_clr:
                if st.button("", icon=":material/delete_sweep:", key="btn_clear_global_chat", help="Reset conversation"):
                    st.session_state["global_chat_history"] = []
                    st.session_state["knowledge_proposal"] = None
                    st.rerun()

        # ==========================================
        # --- Chat Stream Feed ---
        # ==========================================
        st.markdown('<div class="echo-chat-box-container">', unsafe_allow_html=True)
        chat_box = st.container(height=safe_scroll_height)
        st.markdown('</div>', unsafe_allow_html=True)

        with chat_box:
            if not st.session_state["global_chat_history"]:
                st.markdown(
                    '<div class="echo-msg-row-assistant">'
                    '<div class="echo-assistant-header">'
                    f'<div class="echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                    '<span class="echo-assistant-title">Echo</span>'
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
                            '<span class="echo-assistant-title">Echo</span>'
                            '<span class="echo-assistant-badge-gold">AI</span>'
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

        # Inline Knowledge Candidate Proposal
        if st.session_state["knowledge_proposal"]:
            prop = st.session_state["knowledge_proposal"]
            val_display = str(prop.get("value", ""))
            if len(val_display) > 180:
                val_display = val_display[:180] + "..."
                
            with st.container():
                st.markdown(
                    f'<div class="echo-context-candidate-card">'
                    f'<div style="font-size:0.75rem; font-weight:600; color:#854D0E; margin-bottom:2px;">'
                    f'{SVG_BRAIN_ICON} Knowledge Base Candidate Identified'
                    f'</div>'
                    f'<div style="font-size:0.78rem; color:#1F2937; margin-bottom:6px;">'
                    f'Save <b>{prop.get("key")}</b> [<i>{prop.get("category")}</i>] to Knowledge Base?<br/>'
                    f'<code style="font-size:0.72rem; color:#1A2B4C;">{val_display}</code>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
                kp_col1, kp_col2 = st.columns([0.5, 0.5])
                with kp_col1:
                    if st.button("Save to Knowledge Base", key="btn_confirm_auto_prop", use_container_width=True):
                        upsert_echo_context(
                            category=prop["category"],
                            key=prop["key"],
                            value=str(prop["value"]),
                            priority=prop.get("priority", 2)
                        )
                        st.session_state["global_chat_history"].append({
                            "role": "assistant",
                            "content": f"Confirmed: `{prop['key']}` registered into Echo Knowledge Base."
                        })
                        st.session_state["knowledge_proposal"] = None
                        st.rerun()
                with kp_col2:
                    if st.button("Dismiss", key="btn_dismiss_auto_prop", use_container_width=True):
                        st.session_state["knowledge_proposal"] = None
                        st.rerun()

        # Docked Bottom Chat Input
        st.markdown('<div class="echo-input-dock">', unsafe_allow_html=True)
        active_prompt = st.chat_input("Ask Echo...")
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
                status_text = "Searching the web..." if st.session_state["echo_source_web"] else "Thinking..."
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


def _extract_context_with_ai(raw_text: str) -> list:
    """Invokes LLM extraction schema with JSON chunking/recovery for unstructured and tabular data."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        st.error("DeepSeek API Key configuration missing.")
        return []

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    system_prompt = (
        "You are an enterprise data extraction engine for PRIME Philippines. "
        "Analyze the input text and extract all entities, properties, procedures, definitions, or table records. "
        "For complex, tabular, or scouting logs that have varying schemas, assign 'category': 'knowledge', 'key': [Main Entity Name or Code], "
        "and 'value': a compact JSON string capturing all available key-value pairs (e.g. {\"location\": \"...\", \"rate\": 100, \"contact\": \"...\"}). "
        "For team members, jargon, or projects, assign 'category' to 'team', 'jargon', or 'projects' respectively with a string or JSON 'value'. "
        "Always return a valid JSON object with key 'items' containing an array of objects with: 'category', 'key', 'value', 'priority' (integer 1-5)."
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text[:20000]}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 8000
    }

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=90)
        if resp.status_code == 200:
            raw_content = resp.json()["choices"][0]["message"]["content"].strip()
            
            cleaned = re.sub(r"^```json\s*", "", raw_content, flags=re.MULTILINE)
            cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE).strip()

            try:
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict) and "items" in parsed:
                    return _normalize_extracted_items(parsed["items"])
                elif isinstance(parsed, list):
                    return _normalize_extracted_items(parsed)
            except json.JSONDecodeError:
                match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
                if match:
                    try:
                        parsed = json.loads(match.group(1))
                        return _normalize_extracted_items(parsed.get("items", []))
                    except Exception:
                        pass
                
                # Regex item recovery
                item_matches = re.findall(
                    r'\{\s*"category"\s*:\s*"([^"]+)"\s*,\s*"key"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*(?:\"(.*?)\"|(\{.*?\}))\s*(?:,\s*"priority"\s*:\s*(\d+))?\s*\}',
                    cleaned,
                    re.DOTALL
                )
                if item_matches:
                    fallback_items = []
                    for cat, key, val_str, val_obj, prio in item_matches:
                        val = val_str if val_str else val_obj
                        fallback_items.append({
                            "category": cat,
                            "key": key,
                            "value": val,
                            "priority": int(prio) if prio else 2
                        })
                    return fallback_items

        st.error(f"Extraction service error ({resp.status_code}): {resp.text}")
        return []
    except Exception as e:
        st.error(f"Extraction error: {e}")
        return []


def _normalize_extracted_items(items: list) -> list:
    """Ensures nested JSON values inside item objects are cleanly stringified for database storage."""
    normalized = []
    for item in items:
        if isinstance(item, dict) and "key" in item and "value" in item:
            val = item["value"]
            if isinstance(val, (dict, list)):
                val = json.dumps(val)
            normalized.append({
                "category": str(item.get("category", "knowledge")),
                "key": str(item["key"]),
                "value": str(val),
                "priority": int(item.get("priority", 2))
            })
    return normalized


def _query_echo_backend(
    question: str, 
    archive_records: list, 
    chat_history: list, 
    web_context: str = "",
    model_name: str = "deepseek-chat",
    include_knowledge: bool = True
) -> tuple:
    """Synthesizes sources while detecting potential context knowledge additions."""
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
        knowledge_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('knowledge', {}).items()])

        knowledge_section = f"""
ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
---------------------------------------
TEAM MEMBERS: {team_list}
ACTIVE PROJECTS: {projects}
TECHNICAL JARGON:
{jargon_list}
ENTERPRISE KNOWLEDGE / STRUCTURED ENTITIES:
{knowledge_list}
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
        "You are Echo, an executive AI analyst for PRIME Philippines. "
        f"The current date is {current_date_str}. Directly answer temporal inquiries accurately. "
        "Synthesize available sources, structured knowledge, and meeting archives accurately. Format responses concisely using Markdown headings, lists, and tables where appropriate. No emojis. "
        f"{citation_rule}\n\n"
        "Determine if the user input defines a new team member role, acronym, project specification, property update, or general entity that should be preserved in the persistent Knowledge Base. "
        "Always respond in JSON format matching the schema:\n"
        "{\n"
        "  \"response\": \"Your thorough markdown response to the user\",\n"
        "  \"propose_knowledge\": null OR {\"category\": \"knowledge|team|jargon|projects\", \"key\": \"Term/Entity Name\", \"value\": \"Definition or JSON string\", \"priority\": 2}\n"
        "}\n\n"
        f"{context_string}\n"
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:24000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2000
    }

    if model_name == "deepseek-chat":
        payload["response_format"] = {"type": "json_object"}

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            raw_content = resp.json()["choices"][0]["message"]["content"].strip()
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
