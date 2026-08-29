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

# --- STREAMLIT PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="Echo Notebook", initial_sidebar_state="collapsed")

# --- NOTEBOOK LM UI CSS ---
NOTEBOOK_LM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600&display=swap');

/* Global Reset & Background */
.stApp {
    background-color: #131314 !important;
    font-family: 'Google Sans', -apple-system, sans-serif !important;
    color: #E3E3E3 !important;
}

/* Remove default padding */
.main .block-container {
    padding: 1rem 1rem 0rem 1rem !important;
    max-width: 100% !important;
}
header {display: none !important;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Custom Container Styling (The 3 Panels) */
[data-testid="stVerticalBlockBorderWrapper"] > div {
    background-color: #1E1F20 !important;
    border-radius: 16px !important;
    border: 1px solid #282A2C !important;
    padding: 1rem !important;
    height: calc(100vh - 2rem) !important;
    overflow-y: auto !important;
}

/* Panel Headers */
h3 {
    font-size: 1rem !important;
    font-weight: 500 !important;
    color: #E3E3E3 !important;
    margin-bottom: 1rem !important;
    padding-bottom: 0 !important;
}

/* Buttons */
.stButton > button {
    background-color: #282A2C !important;
    border: 1px solid #3C4043 !important;
    color: #E3E3E3 !important;
    border-radius: 20px !important;
    font-weight: 500 !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background-color: #3C4043 !important;
    border-color: #5F6368 !important;
    color: #FFF !important;
}

/* File Uploader to look like "Add Sources" */
[data-testid="stFileUploader"] {
    background-color: transparent !important;
}
[data-testid="stFileUploader"] section {
    background-color: #282A2C !important;
    border: 1px dashed #5F6368 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] section > div > div > span {
    color: #9AA0A6 !important;
    font-size: 0.85rem !important;
}

/* Text Inputs / Search */
.stTextInput > div > div > input {
    background-color: #282A2C !important;
    border: 1px solid #3C4043 !important;
    color: #E3E3E3 !important;
    border-radius: 24px !important;
    padding: 10px 16px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #8AB4F8 !important;
    box-shadow: none !important;
}

/* Chat Input overriding */
.stChatInputContainer {
    background-color: transparent !important;
    padding-bottom: 1rem !important;
}
.stChatInputContainer > div {
    background-color: #282A2C !important;
    border: 1px solid #3C4043 !important;
    border-radius: 24px !important;
}
.stChatInputContainer > div:focus-within {
    border-color: #8AB4F8 !important;
}

/* Chat Messages */
.stChatMessage {
    background-color: transparent !important;
}
.stChatMessage [data-testid="chatAvatarIcon-user"] {
    background-color: #8AB4F8 !important;
}
.stChatMessage [data-testid="chatAvatarIcon-assistant"] {
    background-color: #CC6B49 !important;
}

/* Welcome UI Elements */
.notebook-welcome {
    text-align: left;
    margin-top: 40px;
    padding: 0 20px;
}
.notebook-emoji {
    font-size: 48px;
    margin-bottom: 16px;
}
.notebook-title {
    font-size: 2.2rem;
    font-weight: 400;
    margin-bottom: 12px;
    color: #FFFFFF;
}
.notebook-subtitle {
    font-size: 1rem;
    color: #9AA0A6;
    line-height: 1.5;
    margin-bottom: 24px;
}

/* Suggestion Pills */
.suggestion-pill {
    display: inline-block;
    background-color: #282A2C;
    border: 1px solid #3C4043;
    border-radius: 20px;
    padding: 8px 16px;
    margin-bottom: 12px;
    margin-right: 8px;
    font-size: 0.9rem;
    color: #E3E3E3;
    cursor: pointer;
}

/* Studio Grid */
.studio-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}
.studio-card {
    background-color: #282A2C;
    border: 1px solid #3C4043;
    border-radius: 12px;
    padding: 12px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: background 0.2s;
}
.studio-card:hover {
    background-color: #3C4043;
}
.studio-card-icon {
    font-size: 1.2rem;
    margin-bottom: 8px;
}
.studio-card-title {
    font-size: 0.85rem;
    font-weight: 500;
    color: #E3E3E3;
}
.studio-card-arrow {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #9AA0A6;
    font-size: 1rem;
}
/* Top color bars for studio cards */
.top-bar-purple { border-top: 3px solid #C58AF9; }
.top-bar-yellow { border-top: 3px solid #FDE293; }
.top-bar-green { border-top: 3px solid #81C995; }
.top-bar-pink { border-top: 3px solid #F48FB1; }
.top-bar-blue { border-top: 3px solid #8AB4F8; }
.top-bar-teal { border-top: 3px solid #4DD0E1; }

/* Scrollbars */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #3C4043; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #5F6368; }

/* Custom Selectbox overrides */
div[data-baseweb="select"] > div {
    background-color: #282A2C !important;
    border-color: #3C4043 !important;
    color: white !important;
}
div[data-baseweb="select"] span {
    color: white !important;
}
</style>
"""

# --- BACKEND FUNCTIONS ---

def _extract_text_from_pdf(uploaded_file) -> str:
    try:
        reader = PdfReader(uploaded_file)
        text_content = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(f"--- Page {i+1} ---\n{page_text}")
        return "\n\n".join(text_content)
    except Exception as e:
        return f"Failed to read PDF: {e}"

def _encode_image_to_base64(uploaded_file) -> tuple:
    try:
        image = Image.open(uploaded_file)
        fmt = image.format.lower() if image.format else "jpeg"
        if fmt == "jpg": fmt = "jpeg"
        buffered = io.BytesIO()
        image.save(buffered, format=image.format if image.format else "JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/{fmt};base64,{img_str}", image
    except Exception as e:
        return None, None

def _perform_web_search(query: str) -> tuple:
    sources = []
    text_snippets = []
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=10)
        if resp.status_code == 200:
            snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', resp.text, re.DOTALL)
            urls = re.findall(r'<a class="result__url[^>]*href="([^"]+)"', resp.text)
            
            for i in range(min(4, len(snippets))):
                clean_snippet = re.sub(r'<.*?>', '', snippets[i]).strip()
                link = urls[i] if i < len(urls) else "#"
                domain = re.sub(r'^https?://(www\.)?', '', link).split('/')[0]
                pill_title = domain if domain else f"Source {i+1}"

                sources.append({"title": pill_title, "url": link})
                text_snippets.append(f"[{i+1}] {clean_snippet} (URL: {link})")
    except Exception:
        pass
    return ("\n".join(text_snippets), sources)

def _query_echo_backend(
    question: str, 
    chat_history: list, 
    web_context: str = "",
    model_name: str = "deepseek/deepseek-chat",
    uploaded_files: list = None
) -> tuple:
    api_key = str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
    if not api_key:
        return "OpenRouter API Key is missing in Streamlit Secrets.", None
        
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://echo.prime.ph",
        "X-Title": "Echo AI"
    }

    current_date_str = datetime.now().strftime("%A, %B %d, %Y")
    web_section = f"\nLIVE WEB SEARCH RESULTS:\n{web_context}\n" if web_context else ""

    system_prompt = (
        "You are an expert AI assistant. "
        f"The current date is {current_date_str}. Directly answer inquiries accurately. "
        "Synthesize available sources and format responses concisely using Markdown headings, lists, and tables where appropriate. No emojis. "
        f"{web_section}\n"
    )

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
        
    # Build multimodal content for the active prompt if files exist
    if uploaded_files:
        user_content = [{"type": "text", "text": question}]
        for f in uploaded_files:
            file_type = f.name.split('.')[-1].lower()
            if file_type in ['png', 'jpg', 'jpeg', 'webp']:
                img_data_url, _ = _encode_image_to_base64(f)
                if img_data_url:
                    user_content.append({"type": "image_url", "image_url": {"url": img_data_url}})
            elif file_type == 'pdf':
                pdf_text = _extract_text_from_pdf(f)
                user_content.append({"type": "text", "text": f"\n\n[ATTACHED PDF CONTENT ({f.name})]:\n{pdf_text[:12000]}"})
        messages.append({"role": "user", "content": user_content})
    else:
        messages.append({"role": "user", "content": question})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            raw_content = resp.json()["choices"][0]["message"]["content"].strip()
            return raw_content, None
        return f"Service notice ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Analysis exception: {e}", None

# --- MAIN UI RENDERER ---

def render_notebook_ui():
    st.markdown(NOTEBOOK_LM_CSS, unsafe_allow_html=True)

    # Initialize State
    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "echo_selected_model" not in st.session_state:
        st.session_state["echo_selected_model"] = "deepseek/deepseek-chat"
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []
    if "sources_list" not in st.session_state:
        st.session_state["sources_list"] = []

    # NotebookLM Layout: 3 Columns [Left: Sources, Mid: Chat, Right: Studio]
    col_left, col_mid, col_right = st.columns([1, 2.2, 1.2], gap="small")

    # --- LEFT PANEL: SOURCES ---
    with col_left:
        with st.container(border=True):
            st.markdown("### Sources")
            
            # Add sources logic
            uploaded_file = st.file_uploader(
                "Add a source",
                type=["pdf", "png", "jpg", "jpeg", "webp", "txt"],
                accept_multiple_files=False,
                label_visibility="collapsed"
            )
            
            if uploaded_file and uploaded_file not in st.session_state["uploaded_files"]:
                st.session_state["uploaded_files"].append(uploaded_file)
                st.session_state["sources_list"].append(uploaded_file.name)
                st.rerun()

            st.text_input("Search", placeholder="Search the web for new sources", label_visibility="collapsed")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if not st.session_state["sources_list"]:
                st.markdown("""
                <div style="text-align:center; padding:40px 10px; color:#9AA0A6;">
                    <div style="font-size:24px; margin-bottom:10px;">📄</div>
                    <div style="font-size:14px; font-weight:500; color:#E3E3E3;">Saved sources will appear here</div>
                    <div style="font-size:12px; margin-top:8px;">Add files, websites, or more. Then ask questions or create things based on these sources.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for src in st.session_state["sources_list"]:
                    st.markdown(f"""
                    <div style="background:#282A2C; padding:10px 14px; border-radius:8px; margin-bottom:8px; border:1px solid #3C4043; font-size:0.85rem;">
                        📄 {src}
                    </div>
                    """, unsafe_allow_html=True)

    # --- MIDDLE PANEL: CHAT ---
    with col_mid:
        with st.container(border=True):
            # Header with Model Selector embedded seamlessly
            c_title, c_model, c_clear = st.columns([4, 3, 0.5])
            with c_title:
                st.markdown("### Chat")
            with c_model:
                st.session_state["echo_selected_model"] = st.selectbox(
                    "Model",
                    options=[
                        "deepseek/deepseek-chat",
                        "minimax/minimax-01",
                        "qwen/qwen2.5-vl-72b-instruct",
                        "google/gemini-2.0-flash-001",
                        "openai/gpt-4o-mini"
                    ],
                    index=0,
                    label_visibility="collapsed"
                )
            with c_clear:
                if st.button("⋮", help="Clear Chat"):
                    st.session_state["global_chat_history"] = []
                    st.session_state["uploaded_files"] = []
                    st.session_state["sources_list"] = []
                    st.rerun()

            # Chat History or Welcome Screen
            chat_container = st.container(height=600, border=False)
            
            with chat_container:
                if not st.session_state["global_chat_history"]:
                    st.markdown("""
                    <div class="notebook-welcome">
                        <div class="notebook-emoji">👋</div>
                        <h1 class="notebook-title">Let's start your notebook...</h1>
                        <p class="notebook-subtitle">This is your blank canvas to understand, create, or make progress on something new. I can help you get started or you can go ahead and add your own sources.</p>
                        
                        <p style="font-size:0.9rem; font-weight:500; color:#E3E3E3; margin-bottom:12px;">What would you like this notebook to help you do?</p>
                        
                        <div class="suggestion-pill">Learn about a new topic</div><br>
                        <div class="suggestion-pill">Create something new</div><br>
                        <div class="suggestion-pill">Make progress on a project</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    for msg in st.session_state["global_chat_history"]:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])

            # Native Streamlit Chat Input mapped to this container
            active_prompt = st.chat_input("Ask a question or create something")

            if active_prompt:
                # Append user message immediately
                st.session_state["global_chat_history"].append({"role": "user", "content": active_prompt})
                st.rerun() # Rerun to show user message and trigger assistant processing on next load

            # Handle Assistant Response (runs after rerun if last message is user)
            if st.session_state["global_chat_history"] and st.session_state["global_chat_history"][-1]["role"] == "user":
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            # MULTIMODAL AUTO-ROUTING LOGIC
                            target_model = st.session_state["echo_selected_model"]
                            files_to_process = st.session_state.get("uploaded_files", [])
                            
                            if files_to_process and any(f.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) for f in files_to_process):
                                target_model = "qwen/qwen2.5-vl-72b-instruct" # Override to VL model
                            
                            web_context, _ = _perform_web_search(st.session_state["global_chat_history"][-1]["content"])
                            
                            answer, _ = _query_echo_backend(
                                question=st.session_state["global_chat_history"][-1]["content"],
                                chat_history=st.session_state["global_chat_history"][:-1],
                                web_context=web_context,
                                model_name=target_model,
                                uploaded_files=files_to_process
                            )
                            
                            st.markdown(answer)
                
                st.session_state["global_chat_history"].append({"role": "assistant", "content": answer})
                st.rerun()

    # --- RIGHT PANEL: STUDIO ---
    with col_right:
        with st.container(border=True):
            st.markdown("### Studio")
            
            # HTML Grid for Studio Buttons to perfectly match the UI
            st.markdown("""
            <div class="studio-grid">
                <div class="studio-card top-bar-purple">
                    <div class="studio-card-icon">🎙️</div>
                    <div class="studio-card-title">Audio Overview</div>
                    <div class="studio-card-arrow">›</div>
                </div>
                <div class="studio-card top-bar-yellow">
                    <div class="studio-card-icon">🖥️</div>
                    <div class="studio-card-title">Slide Deck</div>
                    <div class="studio-card-arrow">›</div>
                </div>
                <div class="studio-card top-bar-pink">
                    <div class="studio-card-icon">🔗</div>
                    <div class="studio-card-title">Mind Map</div>
                    <div class="studio-card-arrow">›</div>
                </div>
                <div class="studio-card top-bar-green">
                    <div class="studio-card-icon">📑</div>
                    <div class="studio-card-title">Reports</div>
                    <div class="studio-card-arrow">›</div>
                </div>
                <div class="studio-card top-bar-blue">
                    <div class="studio-card-icon">❓</div>
                    <div class="studio-card-title">Quiz</div>
                    <div class="studio-card-arrow">›</div>
                </div>
                <div class="studio-card top-bar-teal">
                    <div class="studio-card-icon">📊</div>
                    <div class="studio-card-title">Data Table</div>
                    <div class="studio-card-arrow">›</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="text-align:center; padding-top:80px; color:#9AA0A6;">
                <div style="font-size:24px; margin-bottom:10px;">🪄</div>
                <div style="font-size:13px; font-weight:500; color:#E3E3E3;">Studio output will be saved here.</div>
                <div style="font-size:12px; margin-top:8px;">After adding sources, click to add Audio Overview, Study Guide, Mind Map, and more!</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.button("📝 Add note", use_container_width=True)

# To execute the UI
if __name__ == "__main__":
    render_notebook_ui()
