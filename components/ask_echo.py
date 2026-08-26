import os
import json
import requests
import streamlit as st

DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"
ARCHIVE_DB_FILE = ".echo_archive.json"

def _query_deepseek_global(question, chat_history):
    if not DEEPSEEK_API_KEY:
        return "DeepSeek API Key is missing. Please add it to your Streamlit Cloud Secrets."

    archive_context = "No archive database found."
    if os.path.exists(ARCHIVE_DB_FILE):
        try:
            with open(ARCHIVE_DB_FILE, "r", encoding="utf-8") as f:
                archive_context = json.dumps(json.load(f), indent=1)
        except Exception:
            pass

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = (
        "You are Ask Echo, an executive AI analyst for PRIME Philippines. "
        "Answer questions accurately using company meeting archives and records. "
        "Keep responses concise, clear, and professional in corporate English."
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nArchive Context:\n{archive_context[:22000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json={
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 500
        }, timeout=60)
        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"].strip()
        return f"Service notice ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"

def render_chat_body(history_key="global_chat_history"):
    """Renders the chat message stream with Claude-style minimalism."""
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    st.markdown("""
    <style>
    .chat-container { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.25rem; }
    .chat-ai { align-self: flex-start; color: #1A1A1A; font-size: 0.85rem; line-height: 1.45; }
    .chat-user-wrap { display: flex; justify-content: flex-end; width: 100%; }
    .chat-user { background-color: #F3F4F6; color: #1A1A1A; padding: 0.45rem 0.8rem; border-radius: 12px; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    if not st.session_state[history_key]:
        st.markdown('<div class="chat-ai">Hello. I am Echo. How can I assist you across your team\'s meeting records?</div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state[history_key]:
            if msg["role"] == "assistant":
                formatted = msg["content"].replace("\n", "<br>")
                st.markdown(f'<div class="chat-ai">{formatted}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask Echo anything...", key=f"input_{history_key}"):
        st.session_state[history_key].append({"role": "user", "content": prompt})
        with st.spinner("Thinking..."):
            ans = _query_deepseek_global(prompt, st.session_state[history_key])
        st.session_state[history_key].append({"role": "assistant", "content": ans})
        st.rerun()

def render_floating_echo_widget():
    """Renders a fixed, bottom-right floating trigger button with pop-up chat modal."""
    if "show_floating_echo" not in st.session_state:
        st.session_state["show_floating_echo"] = False

    # Floating CSS Trigger & Popover positioning
    st.markdown("""
    <style>
    div[data-testid="stButton"]:has(button[key="floating_echo_trigger_btn"]) {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 999999 !important;
        width: auto !important;
    }
    button[key="floating_echo_trigger_btn"] {
        background-color: #161616 !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.4rem !important;
        font-family: 'Playfair Display', serif !important;
        font-style: italic !important;
        font-size: 0.95rem !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25) !important;
        min-height: 44px !important;
    }
    button[key="floating_echo_trigger_btn"]:hover {
        background-color: #D4AF37 !important;
        color: #161616 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Floating Trigger Button
    btn_label = "Close Echo" if st.session_state["show_floating_echo"] else "Ask Echo"
    if st.button(btn_label, key="floating_echo_trigger_btn"):
        st.session_state["show_floating_echo"] = not st.session_state["show_floating_echo"]
        st.rerun()

    # Chat Popup Drawer
    if st.session_state["show_floating_echo"]:
        with st.sidebar:
            st.markdown("### Ask Echo")
            st.caption("Floating Enterprise Assistant")
            render_chat_body(history_key="global_chat_history")
