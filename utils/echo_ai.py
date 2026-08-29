import streamlit as st
import requests
import json
import base64
import io
import re
from datetime import datetime

# --- Optional DB Import with Fallback ---
try:
    from utils.db import fetch_meeting_archives, fetch_echo_context, upsert_echo_context
except ImportError:
    def fetch_meeting_archives(): return []
    def fetch_echo_context(): return {}
    def upsert_echo_context(data): pass

# --- Page Configuration ---
st.set_page_config(
    page_title="Echo AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Pure SVG Icon Assets ---
SVG_ECHO_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>"""
SVG_USER_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>"""
SVG_GLOBE_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 4px;"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>"""
SVG_BRAIN_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#854D0E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path></svg>"""
SVG_WARNING_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#854D0E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""
SVG_PLUS_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>"""
SVG_GEAR_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""
SVG_TRASH_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>"""
SVG_IMAGE_ICON = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>"""

# --- Custom Styling & Layout Injections ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

/* Reset and Container Styling */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
header {{visibility: hidden;}}
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 7rem !important;
    max-width: 900px !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}}

/* Header Layout */
.echo-modern-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    margin-bottom: 16px;
}}
.echo-title {{
    font-family: 'Playfair Display', Georgia, serif !important;
    font-style: italic;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}}

/* Animations */
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.animate-fade-in {{
    animation: fadeIn 0.25s ease-out forwards;
}}

/* Message Styling */
.user-msg-row {{
    display: flex;
    justify-content: flex-end;
    margin: 12px 0;
}}
.user-bubble {{
    background: #1A2B4C;
    color: #FFFFFF;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(26, 43, 76, 0.08);
}}
.assistant-msg-row {{
    display: flex;
    justify-content: flex-start;
    margin: 12px 0;
}}
.assistant-bubble {{
    background: #F8FAFC;
    color: #1E293B;
    border: 1px solid rgba(212, 175, 55, 0.2);
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    max-width: 82%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}}

/* Knowledge Proposal Card */
.knowledge-card {{
    background: #FEFCE8;
    border: 1px solid #FEF08A;
    border-left: 4px solid #CA8A04;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 10px;
}}
.knowledge-title {{
    font-weight: 600;
    color: #854D0E;
    font-size: 0.88rem;
    display: flex;
    align-items: center;
}}
.knowledge-content {{
    color: #713F12;
    font-size: 0.85rem;
    margin-top: 4px;
}}

/* Welcome Screen */
.welcome-container {{
    text-align: center;
    padding: 40px 20px;
    margin: 40px 0;
}}
.welcome-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin-top: 24px;
}}
.welcome-card {{
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px;
    font-size: 0.85rem;
    color: #475569;
    text-align: left;
}}

/* Animated Thinking Indicator */
.dot-flashing {{
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    background: #F1F5F9;
    border-radius: 12px;
    width: fit-content;
}}
.dot {{
    width: 6px;
    height: 6px;
    background-color: #64748B;
    border-radius: 50%;
    animation: pulse 1.4s infinite ease-in-out both;
}}
.dot:nth-child(1) {{ animation-delay: -0.32s; }}
.dot:nth-child(2) {{ animation-delay: -0.16s; }}
@keyframes pulse {{
    0%, 80%, 100% {{ transform: scale(0); }}
    40% {{ transform: scale(1); }}
}}
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "api_base" not in st.session_state:
    st.session_state.api_base = "https://api.openai.com/v1"
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "gpt-4o-mini"
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are Echo AI, a concise and intelligent collaborator."

# --- API Execution Handler with Route Resolution ---
def call_llm_api(messages, model, api_key, api_base):
    if not api_key:
        return {"error": "API Key is missing. Set it via Settings."}
    
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json"
    }
    
    base_url = api_base.rstrip("/")
    # Auto-route image generation models vs standard completion models
    is_image_model = any(k in model.lower() for k in ["image", "dall-e", "flux", "diffusion"])

    try:
        if is_image_model:
            prompt = messages[-1]["content"] if messages else ""
            endpoint = f"{base_url}/images/generations"
            payload = {
                "model": model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024"
            }
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                img_url = data.get("data", [{}])[0].get("url", "")
                b64_img = data.get("data", [{}])[0].get("b64_json", "")
                if img_url:
                    return {"type": "image", "content": img_url}
                elif b64_img:
                    return {"type": "image_b64", "content": b64_img}
            return {"error": f"Service Error ({response.status_code}): {response.text}"}
        else:
            endpoint = f"{base_url}/chat/completions"
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": st.session_state.system_prompt}] + messages,
                "temperature": 0.7
            }
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return {"type": "text", "content": content}
            return {"error": f"Service Error ({response.status_code}): {response.text}"}
    except Exception as e:
        return {"error": f"Request Failed: {str(e)}"}

# --- Header Controls ---
header_col1, header_col2, header_col3, header_col4 = st.columns([3, 2, 0.6, 0.6])

with header_col1:
    st.markdown(f'<div class="echo-title">{SVG_ECHO_LOGO} Echo AI</div>', unsafe_allow_html=True)

with header_col2:
    st.session_state.model_choice = st.selectbox(
        "Model",
        [
            "gpt-4o-mini",
            "gpt-4o",
            "claude-3-5-sonnet",
            "qwen/qwen-image-3-pro",
            "dall-e-3"
        ],
        index=0,
        label_visibility="collapsed"
    )

with header_col3:
    with st.popover("⚙️"):
        st.markdown("**Settings**")
        st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key, type="password")
        st.session_state.api_base = st.text_input("Base URL", value=st.session_state.api_base)
        st.session_state.system_prompt = st.text_area("System Context", value=st.session_state.system_prompt, height=80)

with header_col4:
    if st.button("🗑️", help="Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- Optional File Uploader Popover ---
with st.expander("📎 Attach Context Document (PDF, TXT, MD)", expanded=False):
    uploaded_file = st.file_uploader("Upload reference file", type=["pdf", "txt", "md"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                from pypdf import PdfReader
                reader = PdfReader(uploaded_file)
                extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            else:
                extracted_text = uploaded_file.read().decode("utf-8")
            st.session_state.system_prompt += f"\n\n[Uploaded Document Context: {uploaded_file.name}]\n{extracted_text[:2000]}"
            st.success(f"Attached {uploaded_file.name} to conversation context.")
        except Exception as e:
            st.error(f"Failed to process file: {str(e)}")

# --- Welcome View for Empty Chat ---
if not st.session_state.messages:
    st.markdown(f"""
    <div class="welcome-container animate-fade-in">
        <div style="font-size: 2rem; margin-bottom: 8px;">{SVG_ECHO_LOGO}</div>
        <h3 style="color: #1A2B4C; font-weight: 600; margin: 0;">How can Echo help today?</h3>
        <p style="color: #64748B; font-size: 0.9rem; margin-top: 4px;">Choose a capability or write a prompt below.</p>
        <div class="welcome-grid">
            <div class="welcome-card">
                <strong>{SVG_GLOBE_ICON} Web & Research</strong>
                <p style="margin: 4px 0 0 0;">Synthesize documentation and meeting archives.</p>
            </div>
            <div class="welcome-card">
                <strong>{SVG_IMAGE_ICON} Generative Imagery</strong>
                <p style="margin: 4px 0 0 0;">Switch to an image model to generate visual assets.</p>
            </div>
            <div class="welcome-card">
                <strong>{SVG_BRAIN_ICON} Deep Logic</strong>
                <p style="margin: 4px 0 0 0;">Solve code, debug architectures, and plan workflows.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Message Feed Display ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-msg-row animate-fade-in">
            <div class="user-bubble">
                {msg["content"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Check for knowledge base extraction tags
        content = msg["content"]
        kb_match = re.search(r"<knowledge>(.*?)</knowledge>", content, flags=re.DOTALL)
        kb_html = ""
        if kb_match:
            kb_text = kb_match.group(1).strip()
            content = content.replace(kb_match.group(0), "").strip()
            kb_html = f"""
            <div class="knowledge-card">
                <div class="knowledge-title">{SVG_BRAIN_ICON} Structured Memory Update</div>
                <div class="knowledge-content">{kb_text}</div>
            </div>
            """

        # Handle image models vs text output
        if msg.get("type") == "image":
            msg_body = f'<img src="{content}" style="max-width: 100%; border-radius: 8px; margin-top: 8px;" />'
        elif msg.get("type") == "image_b64":
            msg_body = f'<img src="data:image/png;base64,{content}" style="max-width: 100%; border-radius: 8px; margin-top: 8px;" />'
        else:
            msg_body = content.replace("\n", "<br/>")

        st.markdown(f"""
        <div class="assistant-msg-row animate-fade-in">
            <div class="assistant-bubble">
                <div>{msg_body}</div>
                {kb_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Chat Input & Dynamic Execution ---
if user_prompt := st.chat_input("Ask a question or describe an image to generate..."):
    # Render user query immediately
    st.session_state.messages.append({"role": "user", "content": user_prompt, "type": "text"})
    st.markdown(f"""
    <div class="user-msg-row animate-fade-in">
        <div class="user-bubble">
            {user_prompt}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Thinking state placeholder
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(f"""
    <div class="assistant-msg-row animate-fade-in">
        <div class="assistant-bubble">
            <div class="dot-flashing">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API Dispatch
    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type") == "text"]
    response = call_llm_api(
        messages=api_messages,
        model=st.session_state.model_choice,
        api_key=st.session_state.api_key,
        api_base=st.session_state.api_base
    )

    thinking_placeholder.empty()

    if "error" in response:
        st.markdown(f"""
        <div class="assistant-msg-row animate-fade-in">
            <div class="assistant-bubble" style="border-color: #FCA5A5; background: #FEF2F2;">
                <div style="color: #991B1B; display: flex; align-items: center;">
                    {SVG_WARNING_ICON} {response["error"]}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.session_state.messages.append({
            "role": "assistant",
            "content": response["content"],
            "type": response.get("type", "text")
        })
        st.rerun()
