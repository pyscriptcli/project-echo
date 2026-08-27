import streamlit as st
import requests
import json
import pandas as pd
import re
from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context

# --- Pure SVG Icon Assets (No Emojis) ---
SVG_ECHO_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
</svg>
"""

SVG_BRAIN_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

CHAT_UI_CSS = """
<style>
/* Pill-shaped modern chat styling */
.echo-chat-thread {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 0.5rem 0.2rem;
}
.echo-msg-row-user {
    display: flex;
    justify-content: flex-end;
    width: 100%;
}
.echo-msg-user {
    background: linear-gradient(135deg, #1A2B4C 0%, #2D4675 100%);
    color: #FFFFFF;
    padding: 0.75rem 1.25rem;
    border-radius: 24px 24px 4px 24px;
    max-width: 80%;
    font-size: 0.88rem;
    line-height: 1.5;
    box-shadow: 0 4px 12px rgba(26, 43, 76, 0.12);
}
.echo-msg-row-assistant {
    display: flex;
    justify-content: flex-start;
    width: 100%;
}
.echo-msg-assistant {
    background-color: #FFFFFF;
    color: #1F2937;
    border: 1px solid rgba(0, 0, 0, 0.08);
    padding: 0.85rem 1.35rem;
    border-radius: 24px 24px 24px 4px;
    max-width: 88%;
    font-size: 0.88rem;
    line-height: 1.55;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.echo-system-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #1A2B4C;
    margin-bottom: 0.4rem;
}
.echo-inline-card {
    background-color: #FBF9F5;
    border: 1px dashed #D4AF37;
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin-top: 0.6rem;
}
</style>
"""

def render_echo_chat(container=None, height=720, title="Ask Echo — Global Intelligence", caption="Synthesize enterprise archives, align records, and synchronize organizational knowledge."):
    target = container if container else st
    st.markdown(CHAT_UI_CSS, unsafe_allow_html=True)

    # State Initializations
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "extracted_context_df" not in st.session_state:
        st.session_state["extracted_context_df"] = None
    if "knowledge_proposal" not in st.session_state:
        st.session_state["knowledge_proposal"] = None

    with target.container(height=height, border=True):
        # Header Controls
        header_col, btn_clear_col = st.columns([0.94, 0.06])
        with header_col:
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:8px;">'
                f'{SVG_ECHO_LOGO}<span style="font-family: \'Playfair Display\', serif; font-size: 1.15rem; font-weight:600; color:#1A2B4C;">{title}</span>'
                f'</div>'
                f'<p style="font-size:0.8rem; color:#6B7280; margin: 0 0 0.5rem 0;">{caption}</p>',
                unsafe_allow_html=True
            )
        with btn_clear_col:
            if st.button("", icon=":material/delete_sweep:", key="btn_clear_global_chat", help="Reset conversation"):
                st.session_state["global_chat_history"] = []
                st.session_state["knowledge_proposal"] = None
                st.rerun()

        # Tab Navigation Architecture
        tab_chat, tab_context = st.tabs(["Intelligence Thread", "Echo Knowledge Vault"])

        # --- TAB 1: Chat Thread ---
        with tab_chat:
            chat_box = st.container(height=height - 240)
            with chat_box:
                st.markdown('<div class="echo-chat-thread">', unsafe_allow_html=True)
                
                if not st.session_state["global_chat_history"]:
                    st.markdown(
                        '<div class="echo-msg-row-assistant">'
                        '<div class="echo-msg-assistant">'
                        '<div class="echo-system-badge">Echo Assistant</div>'
                        'Global Intelligence active. Inquire regarding past decisions, cross-meeting action plans, or designated timelines across historical records.'
                        '</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    for idx, msg in enumerate(st.session_state["global_chat_history"]):
                        if msg["role"] == "user":
                            st.markdown(
                                f'<div class="echo-msg-row-user">'
                                f'<div class="echo-msg-user">{msg["content"]}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            content_html = msg["content"].replace("\n", "<br>")
                            st.markdown(
                                f'<div class="echo-msg-row-assistant">'
                                f'<div class="echo-msg-assistant">'
                                f'<div class="echo-system-badge">Echo Assistant</div>'
                                f'{content_html}'
                                f'</div></div>',
                                unsafe_allow_html=True
                            )

                st.markdown('</div>', unsafe_allow_html=True)

            # Active Knowledge Proposal Approval Card
            if st.session_state["knowledge_proposal"]:
                prop = st.session_state["knowledge_proposal"]
                with st.container(border=True):
                    st.markdown(
                        f'<div class="echo-system-badge" style="color:#D4AF37;">'
                        f'{SVG_BRAIN_ICON} Knowledge Base Addition Detected'
                        f'</div>'
                        f'<p style="font-size:0.84rem; margin:0 0 0.5rem 0; color:#374151;">'
                        f'Would you like to register <b>{prop.get("key")}</b> ({prop.get("category")}) to the Echo Knowledge Base?<br/>'
                        f'<i>Value: {prop.get("value")}</i>'
                        f'</p>',
                        unsafe_allow_html=True
                    )
                    c_approve, c_reject = st.columns([1, 1])
                    with c_approve:
                        if st.button("Confirm & Add to Echo Knowledge", key="btn_confirm_prop", type="primary", use_container_width=True):
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

            # Chat Input Field
            if prompt := st.chat_input("Ask a question, identify project facts, or provide knowledge updates..."):
                st.session_state["global_chat_history"].append({"role": "user", "content": prompt})
                with st.spinner("Synthesizing archives and analyzing entities..."):
                    archives = fetch_meeting_archives(limit=100)
                    answer, proposed_fact = _query_echo_backend(prompt, archives, st.session_state["global_chat_history"])
                    
                    st.session_state["global_chat_history"].append({"role": "assistant", "content": answer})
                    if proposed_fact:
                        st.session_state["knowledge_proposal"] = proposed_fact
                st.rerun()

        # --- TAB 2: Knowledge Base Manager ---
        with tab_context:
            _render_context_manager_subtab()


def _render_context_manager_subtab():
    """Renders structured dual-mode Context Management UI within the dedicated tab."""
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
                    with st.spinner("Extracting parameters..."):
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
        st.markdown("<p style='font-size:0.85rem; font-weight:600; color:#1A2B4C;'>Staged Knowledge Base Rows</p>", unsafe_allow_html=True)

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
            with st.spinner("Committing to repository..."):
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


def _query_echo_backend(question: str, archive_records: list, chat_history: list) -> tuple:
    """
    Synthesizes archives while verifying if the user statement contains novel knowledge base entities.
    Returns a tuple: (answer_text, proposed_knowledge_dict_or_None)
    """
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "DeepSeek API Key is missing in Streamlit Secrets.", None

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    archive_context = json.dumps(archive_records, indent=1)

    context_data = fetch_echo_context()
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
"""

    system_prompt = (
        "You are Echo Global, an executive AI analyst for PRIME Philippines. "
        "Synthesize meeting archives accurately. Format with plain text and Markdown tables/bullets only. No emojis. "
        "Determine if the user's input contains a new terminology definition, project assignment, or role update that could belong in the knowledge base. "
        "Respond in strict JSON with schema: "
        "{"
        "  \"response\": \"Your thorough Markdown answer to the user\", "
        "  \"propose_knowledge\": null OR {\"category\": \"team|jargon|projects\", \"key\": \"Name/Term\", \"value\": \"Definition/Role\", \"priority\": 2}"
        "}"
        f"\n\n{context_string}\n"
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:26000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "response_format": {"type": "json_object"},
        "temperature": 0.2,
        "max_tokens": 900
    }

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            result = json.loads(resp.json()["choices"][0]["message"]["content"])
            return result.get("response", ""), result.get("propose_knowledge")
        return f"Service notice ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Analysis exception: {e}", None
