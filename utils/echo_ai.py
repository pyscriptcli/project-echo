import streamlit as st
import requests
import json
import pandas as pd
import re
from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context

# SVG Icon for the Context Manager Header
SVG_CONTEXT_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#1A2B4C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 8px;">
    <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
    <path d="M2 17l10 5 10-5"></path>
    <path d="M2 12l10 5 10-5"></path>
</svg>
"""

def render_echo_chat(container=None, height=720, title="Ask Echo — Global Intelligence", caption="Synthesize meeting archives, transcripts, and action logs."):
    target = container if container else st
    
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "show_context_manager" not in st.session_state:
        st.session_state["show_context_manager"] = False
    if "extracted_context_df" not in st.session_state:
        st.session_state["extracted_context_df"] = None

    with target.container(height=height, border=True):
        # 1. Header & Action Buttons
        chat_header_col, btn_clear_col, btn_full_col, btn_context_col = st.columns([1, 0.04, 0.04, 0.04])
        
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

        # NEW: Context Manager Toggle Button
        with btn_context_col:
            st.markdown('<div class="icon-action-btn">', unsafe_allow_html=True)
            ctx_icon = ":material/bookmark_remove:" if st.session_state["show_context_manager"] else ":material/bookmark_add:"
            ctx_tooltip = "Hide Context Manager" if st.session_state["show_context_manager"] else "Manage Echo Context"
            if st.button("", icon=ctx_icon, key="btn_toggle_context", help=ctx_tooltip):
                st.session_state["show_context_manager"] = not st.session_state["show_context_manager"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 2. Chat Feed
        chat_feed_height = 545 if not st.session_state["chat_fullscreen"] else 565
        if st.session_state["show_context_manager"]:
            chat_feed_height -= 200 # Reduce chat height if manager is open
            
        chat_history_container = st.container(height=chat_feed_height)
        with chat_history_container:
            if not st.session_state["global_chat_history"]:
                with st.chat_message("assistant"):
                    st.markdown("**System Online:** Hello. I am Echo. Ask me anything across your entire meeting archive.")
            else:
                for msg in st.session_state["global_chat_history"]:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        # 3. Chat Input
        if global_query := st.chat_input("Ask Echo a question..."):
            st.session_state["global_chat_history"].append({"role": "user", "content": global_query})
            with st.spinner("Analyzing meeting archives..."):
                archives = fetch_meeting_archives(limit=100)
                ans = _query_echo_backend(global_query, archives, st.session_state["global_chat_history"])
            st.session_state["global_chat_history"].append({"role": "assistant", "content": ans})
            st.rerun()

    # 4. Context Manager UI (Rendered outside the main chat container to avoid scrolling issues)
    if st.session_state["show_context_manager"]:
        _render_context_manager(target)


def _render_context_manager(target):
    """Renders the Context Management UI for adding/editing Echo's knowledge base."""
    with target.container(border=True):
        st.markdown(f'<h4 style="margin:0; color:#1A2B4C;">{SVG_CONTEXT_ICON}Echo Context Manager</h4>', unsafe_allow_html=True)
        st.caption("Paste raw notes, team updates, or jargon. Echo will structure it for you to review and save.")
        
        raw_text = st.text_area(
            "Raw Text Dump", 
            height=100, 
            placeholder="e.g., 'Alice is the new Lead Dev. K8s stands for Kubernetes. We are starting Project Echo next week.'",
            label_visibility="collapsed"
        )
        
        col_ext, col_save, col_clear = st.columns([1.2, 1.2, 1])
        
        with col_ext:
            if st.button("Extract & Structure with AI", key="btn_extract_ctx", use_container_width=True):
                if raw_text.strip():
                    with st.spinner("AI is structuring your data..."):
                        extracted_data = _extract_context_with_ai(raw_text)
                        if extracted_data:
                            st.session_state["extracted_context_df"] = pd.DataFrame(extracted_data)
                            st.rerun()
                        else:
                            st.error("AI could not extract structured data. Please try rephrasing.")
                else:
                    st.warning("Please enter some text first.")
                    
        with col_clear:
            if st.button("Clear Table", key="btn_clear_ctx_table", use_container_width=True):
                st.session_state["extracted_context_df"] = None
                st.rerun()

        # Display Editable Table
        if st.session_state["extracted_context_df"] is not None:
            st.markdown("---")
            st.markdown("**Review & Edit Extracted Context:**")
            
            # Define column configs for the data editor
            column_config = {
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["team", "jargon", "projects"],
                    required=True
                ),
                "key": st.column_config.TextColumn("Key (Term/Name)", required=True),
                "value": st.column_config.TextColumn("Value (Definition/Role)", required=True, width="large"),
                "priority": st.column_config.NumberColumn("Priority (1-5)", min_value=1, max_value=5, step=1, default=1)
            }
            
            edited_df = st.data_editor(
                st.session_state["extracted_context_df"],
                column_config=column_config,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="ctx_data_editor"
            )
            
            with col_save:
                if st.button("Save to Echo Brain", key="btn_save_ctx", use_container_width=True, type="primary"):
                    success_count = 0
                    fail_count = 0
                    with st.spinner("Saving to database..."):
                        for index, row in edited_df.iterrows():
                            if pd.notna(row['category']) and pd.notna(row['key']) and pd.notna(row['value']):
                                success = upsert_echo_context(
                                    category=str(row['category']),
                                    key=str(row['key']),
                                    value=str(row['value']),
                                    priority=int(row['priority']) if pd.notna(row['priority']) else 1
                                )
                                if success:
                                    success_count += 1
                                else:
                                    fail_count += 1
                    
                    if success_count > 0:
                        st.success(f"Successfully saved {success_count} entries to Echo's knowledge base!")
                        st.session_state["extracted_context_df"] = None
                        st.rerun()
                    if fail_count > 0:
                        st.warning(f"Failed to save {fail_count} entries.")


def _extract_context_with_ai(raw_text: str) -> list:
    """Calls DeepSeek to convert raw text into a structured JSON list of context items."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        st.error("DeepSeek API Key is missing.")
        return []
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    system_prompt = (
        "You are a data structuring assistant. Extract team members, technical jargon, and project names from the user's text. "
        "Output ONLY a valid JSON object with a single key 'items' containing an array of objects. "
        "Each object must have: 'category' (either 'team', 'jargon', or 'projects'), 'key' (the term or name), "
        "'value' (the definition, role, or full name), and 'priority' (integer 1 to 5, where 5 is highest importance)."
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
            raw_json = resp.json()["choices"][0]["message"]["content"]
            parsed = json.loads(raw_json)
            return parsed.get("items", [])
        return []
    except Exception as e:
        st.error(f"Context extraction failed: {e}")
        return []


def _query_echo_backend(question: str, archive_records: list, chat_history: list) -> str:
    """Internal function to handle the AI API call with Context Injection."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "DeepSeek API Key is missing in Streamlit Secrets."
    
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

INSTRUCTION: Use this knowledge base to correct proper nouns, acronyms, and project names in the archives. 
If the archive says 'Cool Berneties' but the Knowledge Base says 'Kubernetes', you MUST use 'Kubernetes'.
"""

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
