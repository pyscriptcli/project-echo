import sys
import os
import json
import re
import datetime
import pandas as pd
import requests
import streamlit as st

from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context

# --- Custom Styling & CSS Scaffolding ---
CHAT_CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

.echo-chat-wrapper {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1E293B;
}

/* Header Container */
.echo-header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #E2E8F0;
    margin-bottom: 0.75rem;
}
.echo-title-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #0EA5E9;
    background: rgba(14, 165, 233, 0.1);
    padding: 2px 8px;
    border-radius: 9999px;
    margin-bottom: 4px;
}
.echo-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
}
.echo-caption {
    font-size: 0.8rem;
    color: #64748B;
    margin: 0;
}

/* Status Indicator */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    color: #059669;
    font-weight: 500;
    background: #ECFDF5;
    padding: 2px 8px;
    border-radius: 9999px;
    border: 1px solid #A7F3D0;
}
.status-dot {
    width: 6px;
    height: 6px;
    background-color: #10B981;
    border-radius: 50%;
}

/* Suggestion Pills */
.echo-prompt-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 8px;
}

/* Context Manager Stats Box */
.ctx-metric-card {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: center;
}
.ctx-metric-val {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
}
.ctx-metric-lbl {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #64748B;
    margin: 0;
}
</style>
"""


def render_echo_chat(
    container=None,
    height: int = 740,
    title: str = "Ask Echo",
    caption: str = "Synthesizing cross-meeting intelligence & active action logs.",
):
    target = container if container else st
    st.markdown(CHAT_CUSTOM_CSS, unsafe_allow_html=True)

    # Session State Initialization
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "show_context_manager" not in st.session_state:
        st.session_state["show_context_manager"] = False
    if "extracted_context_df" not in st.session_state:
        st.session_state["extracted_context_df"] = None

    with target.container(height=height, border=True):
        # 1. Header Toolbar
        c_title, c_clear, c_ctx = st.columns([1, 0.05, 0.05])
        with c_title:
            st.markdown(
                f"""
                <div class="echo-chat-wrapper">
                    <div class="echo-header-bar">
                        <div>
                            <div class="echo-title-badge"><span class="status-dot"></span> PRIME Intelligence</div>
                            <h3 class="echo-title">{title}</h3>
                            <p class="echo-caption">{caption}</p>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_clear:
            if st.button("", icon=":material/delete_sweep:", key="btn_clear_chat", help="Clear conversation history"):
                st.session_state["global_chat_history"] = []
                st.rerun()
        with c_ctx:
            ctx_btn_icon = ":material/database:" if not st.session_state["show_context_manager"] else ":material/close:"
            ctx_btn_help = "Open Knowledge Base Hub" if not st.session_state["show_context_manager"] else "Close Knowledge Base Hub"
            if st.button("", icon=ctx_btn_icon, key="btn_toggle_ctx", help=ctx_btn_help):
                st.session_state["show_context_manager"] = not st.session_state["show_context_manager"]
                st.rerun()

        # 2. Main Layout (Context Manager Drawer vs Chat Area)
        if st.session_state["show_context_manager"]:
            chat_col, ctx_col = st.columns([1.1, 0.9], gap="medium")
            with ctx_col:
                _render_context_manager()
            chat_target = chat_col
            feed_height = height - 210
        else:
            chat_target = st.container()
            feed_height = height - 190

        # 3. Chat Feed Area
        with chat_target:
            chat_history_container = st.container(height=feed_height)
            with chat_history_container:
                if not st.session_state["global_chat_history"]:
                    with st.chat_message("assistant", avatar="✨"):
                        st.markdown(
                            "**Echo System Active.** Ask me across all stored Minutes of Meetings, deliverables, decisions, and timelines."
                        )
                        st.markdown(
                            """
                            **Suggested Inquiries:**
                            - *Summarize all pending action items assigned to CRD.*
                            - *What were the major blockers discussed in the latest client meetings?*
                            - *Show all project milestones targeted for next month.*
                            """
                        )
                else:
                    for msg in st.session_state["global_chat_history"]:
                        avatar = "✨" if msg["role"] == "assistant" else None
                        with st.chat_message(msg["role"], avatar=avatar):
                            st.markdown(msg["content"])

            # 4. Message Input & Dispatch
            if user_query := st.chat_input("Ask a question about past meetings or deliverables..."):
                st.session_state["global_chat_history"].append({"role": "user", "content": user_query})
                with st.spinner("Synthesizing archives..."):
                    archives = fetch_meeting_archives(limit=100)
                    response = _query_echo_backend(
                        user_query, archives, st.session_state["global_chat_history"]
                    )
                st.session_state["global_chat_history"].append({"role": "assistant", "content": response})
                st.rerun()


def _render_context_manager():
    """Renders the Knowledge Base Context Hub with live stats, structured review, and direct editing."""
    ctx_data = fetch_echo_context()
    team_count = len(ctx_data.get("team", []))
    jargon_count = len(ctx_data.get("jargon", {}))
    proj_count = len(ctx_data.get("projects", []))

    st.markdown("#### Knowledge Base (Source of Truth)")
    st.caption("Entries here override transcript homophones and define company entities.")

    # Live Knowledge Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div class="ctx-metric-card"><p class="ctx-metric-val">{team_count}</p><p class="ctx-metric-lbl">Team</p></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="ctx-metric-card"><p class="ctx-metric-val">{jargon_count}</p><p class="ctx-metric-lbl">Jargon</p></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="ctx-metric-card"><p class="ctx-metric-val">{proj_count}</p><p class="ctx-metric-lbl">Projects</p></div>',
            unsafe_allow_html=True,
        )

    st.write("")

    tab_auto, tab_manual = st.tabs(["Smart Extraction", "Direct Injection"])

    # Tab 1: AI-Powered Unstructured Context Ingestion
    with tab_auto:
        raw_text = st.text_area(
            "Raw Notes or Jargon Dump",
            placeholder="Paste rough text here (e.g., 'Marc joined the Backend team. SOW stands for Statement of Work. Project Orion deadline is next Friday.').",
            height=110,
            label_visibility="collapsed",
        )
        c_ext_btn, c_clr_btn = st.columns([1.5, 1])
        with c_ext_btn:
            if st.button("Extract Entities", key="btn_run_ai_ctx", use_container_width=True, type="primary"):
                if raw_text.strip():
                    with st.spinner("Extracting structured entities..."):
                        extracted_list = _extract_context_with_ai(raw_text)
                        if extracted_list:
                            st.session_state["extracted_context_df"] = pd.DataFrame(extracted_list)
                            st.rerun()
                        else:
                            st.warning("No structured entities could be identified.")
                else:
                    st.warning("Please paste context or terminology notes.")
        with c_clr_btn:
            if st.button("Reset", key="btn_clear_staged_ctx", use_container_width=True):
                st.session_state["extracted_context_df"] = None
                st.rerun()

        # Data Editor Interface for Staged Entries
        if st.session_state["extracted_context_df"] is not None:
            st.markdown("---")
            st.markdown("**Review & Approve Entities:**")

            column_config = {
                "category": st.column_config.SelectboxColumn(
                    "Category",
                    options=["team", "jargon", "projects"],
                    required=True,
                    width="small",
                ),
                "key": st.column_config.TextColumn("Identifier / Term", required=True, width="medium"),
                "value": st.column_config.TextColumn("Full Name / Definition / Role", required=True, width="large"),
                "priority": st.column_config.NumberColumn(
                    "Priority (1-5)", min_value=1, max_value=5, step=1, default=1, width="small"
                ),
            }

            edited_df = st.data_editor(
                st.session_state["extracted_context_df"],
                column_config=column_config,
                num_rows="dynamic",
                use_container_width=True,
                hide_index=True,
                key="ai_ctx_editor",
            )

            if st.button("Commit to Brain", key="btn_commit_ctx_db", type="primary", use_container_width=True):
                _save_dataframe_to_context(edited_df)

    # Tab 2: Direct Single-Item Entry
    with tab_manual:
        with st.form("quick_context_form", clear_on_submit=True):
            f_cat = st.selectbox("Category", options=["jargon", "team", "projects"])
            f_key = st.text_input("Key / Term", placeholder="e.g., K8s or John Doe")
            f_val = st.text_input("Value / Description", placeholder="e.g., Kubernetes or Senior Systems Architect")
            f_prio = st.slider("Priority", 1, 5, 1)

            if st.form_submit_button("Add Single Entry", use_container_width=True):
                if f_key.strip() and f_val.strip():
                    ok = upsert_echo_context(category=f_cat, key=f_key.strip(), value=f_val.strip(), priority=f_prio)
                    if ok:
                        st.success(f"Added '{f_key.strip()}' to {f_cat} knowledge base.")
                        st.rerun()
                    else:
                        st.error("Failed to commit entry.")
                else:
                    st.warning("Both Key and Value are required.")


def _save_dataframe_to_context(df: pd.DataFrame):
    """Iterates through data editor records and commits them to Supabase."""
    success_count, fail_count = 0, 0
    with st.spinner("Writing to knowledge base..."):
        for _, row in df.iterrows():
            if pd.notna(row.get("category")) and pd.notna(row.get("key")) and pd.notna(row.get("value")):
                ok = upsert_echo_context(
                    category=str(row["category"]).strip().lower(),
                    key=str(row["key"]).strip(),
                    value=str(row["value"]).strip(),
                    priority=int(row["priority"]) if pd.notna(row.get("priority")) else 1,
                )
                if ok:
                    success_count += 1
                else:
                    fail_count += 1

        if success_count > 0:
            st.success(f"Committed {success_count} entities to Echo Brain.")
            st.session_state["extracted_context_df"] = None
            st.rerun()
        if fail_count > 0:
            st.warning(f"Could not persist {fail_count} entities.")


def _extract_context_with_ai(raw_text: str) -> list:
    """Uses DeepSeek structured JSON completion to isolate contextual entities."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        st.error("DEEPSEEK_API_KEY secret is missing.")
        return []

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    system_prompt = (
        "You are an executive knowledge-base curation engine. Extract entities from unstructured text. "
        "Categorize each entity strictly into one of: 'team', 'jargon', or 'projects'. "
        "Return ONLY a valid JSON object matching this schema: "
        '{"items": [{"category": "team|jargon|projects", "key": "short term or name", "value": "full expansion or role", "priority": 1-5}]}'
    )

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_text},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 1000,
    }

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            raw_text_out = resp.json()["choices"][0]["message"]["content"].strip()
            clean_text = re.sub(r"^```(?:json)?\s*", "", raw_text_out)
            clean_text = re.sub(r"\s*```$", "", clean_text).strip()
            parsed = json.loads(clean_text)
            return parsed.get("items", [])
    except Exception as e:
        st.error(f"Context extraction error: {e}")
    return []


def _query_echo_backend(question: str, archive_records: list, chat_history: list) -> str:
    """Synthesizes question answering with RAG over meeting archives and the live knowledge base."""
    api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
    if not api_key:
        return "DEEPSEEK_API_KEY is not configured in Streamlit Secrets."

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Compile Ground Truth Knowledge Base
    context_data = fetch_echo_context()
    team_list = ", ".join(context_data.get("team", [])) or "None specified"
    jargon_list = (
        "\n".join([f"- {k}: {v}" for k, v in context_data.get("jargon", {}).items()])
        or "None specified"
    )
    projects = ", ".join(context_data.get("projects", [])) or "None specified"

    knowledge_block = f"""
ECHO KNOWLEDGE BASE (SOURCE OF TRUTH):
---------------------------------------
TEAM MEMBERS: {team_list}
ACTIVE PROJECTS: {projects}
TECHNICAL JARGON & ACRONYMS:
{jargon_list}

INSTRUCTION: Use this knowledge base as the ground truth. Correct any misheard terminology or homophones found in past meeting transcripts.
"""

    system_prompt = (
        "You are Echo Global, the executive AI intelligence system for PRIME Philippines. "
        "Answer user inquiries authoritatively by synthesizing meeting archives, action items, dates, and responsibilities. "
        "Structure responses cleanly using Markdown headings, bullet points, and tables where applicable. "
        "Do not use emojis in your responses. Always maintain a professional, corporate tone."
        f"\n\n{knowledge_block}"
    )

    archive_dump = json.dumps(archive_records, indent=1)
    messages = [
        {
            "role": "system",
            "content": f"{system_prompt}\n\nMEETING ARCHIVES DATABASE:\n{archive_dump[:28000]}",
        }
    ]

    # Include recent chat history for context continuity
    for msg in chat_history[-6:]:
        if msg.get("content"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": question})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 900,
    }

    try:
        resp = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"Service notice ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"
