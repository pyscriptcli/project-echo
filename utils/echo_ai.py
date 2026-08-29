import streamlit as st
import requests
import json
import re
import base64
import io
import pandas as pd
from pypdf import PdfReader
from PIL import Image
from datetime import datetime
from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context

# ------------------------------------------------------------------------------
# SVG Icons (no external icon libraries)
# ------------------------------------------------------------------------------
SVG_ECHO_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
</svg>
"""

SVG_USER_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#854D0E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

SVG_WARNING_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#854D0E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
</svg>
"""

SVG_PLUS_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
</svg>
"""

SVG_GEAR_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
</svg>
"""

# ------------------------------------------------------------------------------
# Custom CSS – modern, responsive, with workarounds for Streamlit limitations
# ------------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

/* Overall app container */
.echo-app {
    max-width: 900px;
    margin: 0 auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Modern header */
.echo-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    border-bottom: 1px solid rgba(212, 175, 55, 0.15);
    flex-shrink: 0;
    gap: 10px;
    flex-wrap: wrap;
}

.echo-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 150px;
}

.echo-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-style: italic;
    font-size: 1.4rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.echo-header-right {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

/* Model selector */
.model-selector-container {
    min-width: 180px;
}
.model-selector-container .stSelectbox > div > div {
    background: #F8FAFC;
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 8px;
    padding: 6px 12px;
    transition: all 0.2s ease;
}
.model-selector-container .stSelectbox > div > div:hover {
    border-color: #D4AF37;
    box-shadow: 0 2px 8px rgba(212, 175, 55, 0.1);
}
.model-selector-container label {
    display: none !important;
}
.model-selector-container span {
    color: #1A2B4C;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Upload button */
.upload-btn-container .stButton > button {
    background: transparent;
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 8px;
    padding: 6px 14px;
    color: #1A2B4C;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}
.upload-btn-container .stButton > button:hover {
    background: rgba(212, 175, 55, 0.05);
    border-color: #D4AF37;
}

/* Settings gear */
.settings-btn-container .stButton > button {
    background: transparent;
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 8px;
    width: 38px;
    height: 38px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #1A2B4C;
    transition: all 0.2s ease;
}
.settings-btn-container .stButton > button:hover {
    border-color: #D4AF37;
    background: rgba(212, 175, 55, 0.05);
}

/* Chat area */
.echo-chat-area {
    flex: 1;
    overflow-y: auto;
    padding: 20px 0;
    margin-bottom: 10px;
}

/* Message rows */
.message-row {
    display: flex;
    margin-bottom: 16px;
    animation: fadeIn 0.3s ease-in;
}
.message-row.user {
    justify-content: flex-end;
}
.message-row.assistant {
    justify-content: flex-start;
}

/* Bubble styling */
.message-bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.95rem;
    line-height: 1.5;
    word-wrap: break-word;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.user .message-bubble {
    background: #1A2B4C;
    color: white;
    border-top-right-radius: 4px;
}
.assistant .message-bubble {
    background: #F8FAFC;
    color: #1A2B4C;
    border: 1px solid #E5E7EB;
    border-top-left-radius: 4px;
}

/* Thinking indicator */
.thinking-dots {
    display: inline-flex;
    gap: 4px;
    align-items: center;
}
.thinking-dots span {
    width: 6px;
    height: 6px;
    background: #D4AF37;
    border-radius: 50%;
    animation: bounce 1.4s infinite;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* Welcome screen */
.welcome-screen {
    text-align: center;
    padding: 40px 20px;
    color: #1A2B4C;
}
.welcome-logo {
    margin-bottom: 20px;
}
.welcome-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: 2rem;
    margin-bottom: 10px;
}
.welcome-subtitle {
    color: #64748B;
    font-size: 1rem;
}

/* Knowledge proposal card */
.knowledge-card {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 16px;
    margin: 12px 0;
    animation: fadeIn 0.3s ease-in;
}
.knowledge-card-header {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    color: #854D0E;
    font-weight: 600;
}
.knowledge-card-content {
    font-size: 0.9rem;
    color: #4B5563;
    white-space: pre-wrap;
    max-height: 200px;
    overflow-y: auto;
}
.knowledge-card-actions {
    margin-top: 12px;
    display: flex;
    gap: 10px;
}

/* Fade in animation */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 768px) {
    .echo-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .echo-header-right {
        width: 100%;
        justify-content: space-between;
    }
    .message-bubble {
        max-width: 95%;
    }
}
</style>
"""

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def extract_text_from_file(uploaded_file):
    """Extract text from uploaded file (PDF, image, text, CSV)."""
    file_type = uploaded_file.type
    text = ""
    try:
        if file_type == "application/pdf":
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        elif file_type.startswith("image/"):
            image = Image.open(io.BytesIO(uploaded_file.getvalue()))
            # In a real app, use OCR here; return placeholder
            text = f"[Image: {uploaded_file.name}]"
        elif file_type == "text/plain":
            text = uploaded_file.getvalue().decode("utf-8")
        elif file_type == "text/csv":
            df = pd.read_csv(uploaded_file)
            text = df.to_string()
        else:
            text = f"[Unsupported file type: {file_type}]"
    except Exception as e:
        text = f"Error extracting text: {str(e)}"
    return text

def call_chat_api(prompt, model, context=""):
    """
    Placeholder for the actual API call.
    Replace with your real endpoint.
    """
    # Example using requests
    # response = requests.post("your_api_url", json={...})
    # For demo, return a canned response
    return f"Echo response for: {prompt}"

# ------------------------------------------------------------------------------
# Main App
# ------------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Echo AI",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thinking" not in st.session_state:
        st.session_state.thinking = False
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "knowledge_base" not in st.session_state:
        st.session_state.knowledge_base = []

    # App container
    st.markdown('<div class="echo-app">', unsafe_allow_html=True)

    # ------------------------------------------------------------
    # Header
    # ------------------------------------------------------------
    with st.container():
        col_logo, col_controls = st.columns([2, 3])
        with col_logo:
            st.markdown(
                f"""
                <div class="echo-header-left">
                    {SVG_ECHO_LOGO}
                    <span class="echo-title">Echo</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_controls:
            st.markdown('<div class="echo-header-right">', unsafe_allow_html=True)
            # Model selector
            with st.container():
                st.markdown('<div class="model-selector-container">', unsafe_allow_html=True)
                model = st.selectbox(
                    "Model",
                    ["Echo‑1", "Echo‑2", "Echo‑3"],
                    label_visibility="collapsed",
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # Upload button
            with st.container():
                st.markdown('<div class="upload-btn-container">', unsafe_allow_html=True)
                upload_btn = st.button(
                    f"{SVG_PLUS_ICON} Upload",
                    key="upload_btn",
                    help="Upload documents for knowledge",
                )
                st.markdown("</div>", unsafe_allow_html=True)

            # Settings gear with popover
            with st.container():
                st.markdown('<div class="settings-btn-container">', unsafe_allow_html=True)
                with st.popover("⚙️", use_container_width=False):
                    st.markdown("### Settings")
                    st.markdown("Configure your Echo experience")
                    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
                    max_tokens = st.number_input("Max tokens", 100, 4000, 1000, 100)
                    st.session_state.temperature = temperature
                    st.session_state.max_tokens = max_tokens
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close header-right

    # ------------------------------------------------------------
    # Chat Area
    # ------------------------------------------------------------
    st.markdown('<div class="echo-chat-area" id="chat-area">', unsafe_allow_html=True)

    if not st.session_state.messages and not st.session_state.thinking:
        # Welcome screen
        st.markdown(
            f"""
            <div class="welcome-screen">
                <div class="welcome-logo">{SVG_ECHO_LOGO}</div>
                <div class="welcome-title">Welcome to Echo</div>
                <div class="welcome-subtitle">Your AI meeting knowledge assistant</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Render messages
        for msg in st.session_state.messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                bubble_class = "user"
                icon = SVG_USER_ICON
            else:
                bubble_class = "assistant"
                icon = SVG_GLOBE_ICON

            st.markdown(
                f"""
                <div class="message-row {bubble_class}">
                    <div class="message-bubble">
                        {content}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Thinking indicator
        if st.session_state.thinking:
            st.markdown(
                """
                <div class="message-row assistant">
                    <div class="message-bubble">
                        <div class="thinking-dots">
                            <span></span><span></span><span></span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)  # close chat area

    # ------------------------------------------------------------
    # Knowledge Proposal Card (shown after file upload)
    # ------------------------------------------------------------
    if "proposed_knowledge" in st.session_state and st.session_state.proposed_knowledge:
        st.markdown(
            f"""
            <div class="knowledge-card">
                <div class="knowledge-card-header">
                    {SVG_BRAIN_ICON}
                    Knowledge Proposal
                </div>
                <div class="knowledge-card-content">
                    {st.session_state.proposed_knowledge[:500]}
                </div>
                <div class="knowledge-card-actions">
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_add, col_cancel = st.columns(2)
        with col_add:
            if st.button("➕ Add to knowledge base"):
                # Save to DB
                upsert_echo_context(
                    text=st.session_state.proposed_knowledge,
                    source="upload",
                )
                st.session_state.proposed_knowledge = None
                st.rerun()
        with col_cancel:
            if st.button("❌ Discard"):
                st.session_state.proposed_knowledge = None
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)  # close echo-app

    # ------------------------------------------------------------
    # Chat Input (sticky at bottom)
    # ------------------------------------------------------------
    prompt = st.chat_input("Message Echo...")

    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.thinking = True
        st.rerun()  # Rerun to show thinking indicator immediately

    # Process after rerun (when thinking is True)
    if st.session_state.thinking:
        # Simulate API call
        with st.spinner("Thinking..."):
            # Get context from knowledge base
            context = ""
            if st.session_state.knowledge_base:
                context = "\n".join(st.session_state.knowledge_base[-3:])  # last 3 items
            # Call API (replace with actual call)
            response = call_chat_api(
                prompt=st.session_state.messages[-1]["content"],
                model=model,
                context=context,
            )
            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.thinking = False
            st.rerun()

    # ------------------------------------------------------------
    # File Upload Handling
    # ------------------------------------------------------------
    if upload_btn:
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["pdf", "txt", "csv", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key="file_uploader",
        )
        if uploaded_files:
            for file in uploaded_files:
                text = extract_text_from_file(file)
                if text:
                    st.session_state.proposed_knowledge = text
                    st.rerun()

if __name__ == "__main__":
    main()
