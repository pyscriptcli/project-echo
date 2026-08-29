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

# --- Pure SVG Icon Assets ---
SVG_ECHO_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
</svg>
"""

SVG_PLUS_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
</svg>
"""

SVG_UPLOAD_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
    <polyline points="17 8 12 3 7 8"></polyline>
    <line x1="12" y1="3" x2="12" y2="15"></line>
</svg>
"""

SVG_USER_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
</svg>
"""

SVG_GLOBE_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="10"></circle>
    <line x1="2" y1="12" x2="22" y2="12"></line>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
</svg>
"""

SVG_BRAIN_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

SVG_SETTINGS_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
</svg>
"""

MODERN_CHAT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Styles */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0d0d !important;
    font-family: 'Inter', sans-serif !important;
}

.main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
    max-width: 100% !important;
}

/* Hide default Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main Chat Container */
.echo-main-container {
    background-color: #0d0d0d;
    max-width: 900px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Header Bar */
.echo-header-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid #2a2a2a;
    margin-bottom: 1rem;
}

.echo-logo-title {
    display: flex;
    align-items: center;
    gap: 10px;
}

.echo-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
}

/* Input Area Container */
.echo-input-area {
    background-color: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 0.75rem;
    margin-bottom: 1.5rem;
}

.echo-input-row {
    display: flex;
    align-items: flex-end;
    gap: 0.75rem;
}

.echo-attach-btn {
    background: transparent;
    border: none;
    color: #888;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 8px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.echo-attach-btn:hover {
    background-color: #2a2a2a;
    color: #D4AF37;
}

.echo-input-wrapper {
    flex: 1;
    position: relative;
}

.echo-chat-input {
    width: 100%;
    background: transparent;
    border: none;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    resize: none;
    outline: none;
    min-height: 24px;
    max-height: 200px;
}

.echo-chat-input::placeholder {
    color: #666;
}

.echo-send-btn {
    background-color: #D4AF37;
    border: none;
    color: #0d0d0d;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    font-weight: 600;
}

.echo-send-btn:hover {
    background-color: #F1C40F;
    transform: scale(1.05);
}

.echo-send-btn:active {
    transform: scale(0.95);
}

/* Model Selector Dropdown */
.echo-model-selector {
    background-color: #2a2a2a;
    border: 1px solid #333;
    color: #ffffff;
    padding: 0.4rem 0.75rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    outline: none;
}

.echo-model-selector:focus {
    border-color: #D4AF37;
}

/* Chat Messages Container */
.echo-chat-messages {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    padding-bottom: 2rem;
}

/* User Message */
.echo-msg-user {
    display: flex;
    justify-content: flex-end;
    align-items: flex-start;
    gap: 10px;
}

.echo-user-bubble {
    background-color: #2a2a2a;
    color: #ffffff;
    padding: 0.75rem 1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.5;
}

.echo-user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #2a2a2a;
    border: 1px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* Assistant Message */
.echo-msg-assistant {
    display: flex;
    justify-content: flex-start;
    align-items: flex-start;
    gap: 10px;
}

.echo-assistant-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #1a1a1a;
    border: 1px solid #D4AF37;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.echo-assistant-content {
    max-width: 75%;
}

.echo-assistant-bubble {
    background-color: transparent;
    color: #e0e0e0;
    font-size: 0.95rem;
    line-height: 1.6;
}

.echo-assistant-bubble h1, .echo-assistant-bubble h2, .echo-assistant-bubble h3 {
    color: #ffffff;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}

.echo-assistant-bubble p {
    margin: 0.5rem 0;
}

.echo-assistant-bubble code {
    background-color: #1a1a1a;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85em;
}

.echo-assistant-bubble pre {
    background-color: #1a1a1a;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 0.75rem 0;
}

.echo-assistant-bubble pre code {
    background: transparent;
    padding: 0;
}

.echo-assistant-bubble ul, .echo-assistant-bubble ol {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
}

.echo-assistant-bubble li {
    margin: 0.25rem 0;
}

/* Sources */
.echo-sources {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 0.75rem;
}

.echo-source-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background-color: #1a1a1a;
    border: 1px solid #D4AF37;
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 0.75rem;
    color: #D4AF37;
    text-decoration: none;
    transition: all 0.2s;
}

.echo-source-pill:hover {
    background-color: #D4AF37;
    color: #0d0d0d;
}

/* Thinking Indicator */
.echo-thinking {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0.75rem 1rem;
    background-color: #1a1a1a;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.echo-thinking-dot {
    width: 6px;
    height: 6px;
    background-color: #D4AF37;
    border-radius: 50%;
    animation: pulse 1.4s infinite ease-in-out;
}

.echo-thinking-dot:nth-child(2) { animation-delay: 0.2s; }
.echo-thinking-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

.echo-thinking-text {
    color: #888;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Knowledge Proposal Card */
.echo-knowledge-card {
    background-color: #1a1a1a;
    border: 1px solid #D4AF37;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

.echo-knowledge-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 0.75rem;
    font-size: 0.85rem;
    font-weight: 600;
    color: #D4AF37;
}

.echo-knowledge-body {
    font-size: 0.9rem;
    color: #e0e0e0;
    margin-bottom: 1rem;
}

.echo-knowledge-actions {
    display: flex;
    gap: 0.75rem;
}

.echo-btn-primary {
    background-color: #D4AF37;
    color: #0d0d0d;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.echo-btn-primary:hover {
    background-color: #F1C40F;
}

.echo-btn-secondary {
    background-color: transparent;
    color: #888;
    border: 1px solid #333;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.echo-btn-secondary:hover {
    border-color: #D4AF37;
    color: #D4AF37;
}

/* File Upload Preview */
.echo-file-preview {
    display: flex;
    align-items: center;
    gap: 8px;
    background-color: #2a2a2a;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    color: #e0e0e0;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: #0d0d0d;
}

::-webkit-scrollbar-thumb {
    background: #2a2a2a;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #333;
}

/* Settings Popover */
div[data-testid="stPopover"] {
    background-color: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
}

div[data-testid="stPopover"] label {
    color: #ffffff !important;
    font-size: 0.85rem !important;
}

div[data-testid="stPopover"] select {
    background-color: #2a2a2a !important;
    color: #ffffff !important;
    border-color: #333 !important;
}

div[data-testid="stPopover"] .stCheckbox label {
    color: #e0e0e0 !important;
}

/* Responsive */
@media (max-width: 768px) {
    .echo-user-bubble, .echo-assistant-content {
        max-width: 85%;
    }
    
    .echo-input-row {
        flex-wrap: wrap;
    }
    
    .echo-input-wrapper {
        order: 3;
        flex-basis: 100%;
        margin-top: 0.5rem;
    }
}
</style>
"""

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
        st.error(f"Failed to read PDF file: {e}")
        return ""

def _encode_image_to_base64(uploaded_file) -> tuple:
    try:
        image = Image.open(uploaded_file)
        fmt = image.format.lower() if image.format else "jpeg"
        if fmt == "jpg":
            fmt = "jpeg"
        buffered = io.BytesIO()
        image.save(buffered, format=image.format if image.format else "JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/{fmt};base64,{img_str}", image
    except Exception as e:
        st.error(f"Failed to process image: {e}")
        return None, None

def _get_existing_knowledge_map() -> dict:
    try:
        data = fetch_echo_context()
        knowledge_map = {}
        for cat, val in data.items():
            cat_clean = str(cat).lower().strip()
            if isinstance(val, dict):
                for k, v in val.items():
                    knowledge_map[(cat_clean, str(k).lower().strip())] = (str(k).strip(), str(v))
            elif isinstance(val, list):
                for item in val:
                    knowledge_map[(cat_clean, str(item).lower().strip())] = (str(item).strip(), str(item))
        return knowledge_map
    except Exception:
        return {}

def _safe_upsert_and_verify(category: str, key: str, value: str, priority: int) -> tuple:
    try:
        c_clean = str(category).strip().lower()
        k_clean = str(key).strip()
        v_clean = str(value).strip()
        p_clean = int(priority) if pd.notna(priority) else 2

        parsed_val = v_clean
        try:
            if (v_clean.startswith("{") and v_clean.endswith("}")) or (v_clean.startswith("[") and v_clean.endswith("]")):
                parsed_val = json.loads(v_clean)
        except Exception:
            parsed_val = v_clean

        write_success = upsert_echo_context(
            category=c_clean,
            key=k_clean,
            value=v_clean,
            priority=p_clean
        )

        if not write_success and isinstance(parsed_val, (dict, list)):
            write_success = upsert_echo_context(
                category=c_clean,
                key=k_clean,
                value=parsed_val,
                priority=p_clean
            )

        if not write_success:
            return False, f"Database write returned False for key: '{k_clean}'"

        if hasattr(fetch_echo_context, "clear"):
            fetch_echo_context.clear()

        latest_data = fetch_echo_context()
        cat_data = latest_data.get(c_clean, latest_data.get(category, {}))
        
        if isinstance(cat_data, dict):
            keys_lower = [str(k).strip().lower() for k in cat_data.keys()]
            if k_clean.lower() in keys_lower:
                return True, ""
        elif isinstance(cat_data, list):
            items_str = [str(item).lower() for item in cat_data]
            if any(k_clean.lower() in item for item in items_str):
                return True, ""

        return True, ""
    except Exception as e:
        return False, f"Exception during write of '{key}': {str(e)}"

def _check_duplicates_against_db(candidate_df: pd.DataFrame) -> tuple:
    existing_map = _get_existing_knowledge_map()
    clean_rows = []
    conflicts = []

    for idx, row in candidate_df.iterrows():
        if pd.isna(row.get('category')) or pd.isna(row.get('key')) or pd.isna(row.get('value')):
            continue
            
        cat = str(row['category']).strip()
        key = str(row['key']).strip()
        val = str(row['value']).strip()
        prio = int(row['priority']) if pd.notna(row.get('priority')) else 2
        lookup_key = (cat.lower(), key.lower())

        if lookup_key in existing_map:
            orig_key, orig_val = existing_map[lookup_key]
            conflicts.append({
                "category": cat,
                "key": key,
                "current_value": orig_val,
                "new_value": val,
                "priority": prio,
                "resolution": "Keep Current"
            })
        else:
            clean_rows.append({
                "category": cat,
                "key": key,
                "value": val,
                "priority": prio
            })

    return clean_rows, conflicts

@st.dialog("Echo Context Manager", width="large")
def render_context_popup_dialog():
    if "extracted_context_df" not in st.session_state:
        st.session_state["extracted_context_df"] = None
    if "detected_conflicts" not in st.session_state:
        st.session_state["detected_conflicts"] = None
    if "clean_staged_rows" not in st.session_state:
        st.session_state["clean_staged_rows"] = []

    if st.session_state["detected_conflicts"] is not None and len(st.session_state["detected_conflicts"]) > 0:
        st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#D4AF37;'>⚠️ Duplicate Entries Flagged</p>", unsafe_allow_html=True)
        st.caption("Choose how each key should be resolved:")

        b_c1, b_c2, _ = st.columns([1, 1, 2])
        with b_c1:
            if st.button("Set All to Overwrite", key="btn_all_overwrite", use_container_width=True):
                for item in st.session_state["detected_conflicts"]:
                    item["resolution"] = "Overwrite with New"
                st.rerun()
        with b_c2:
            if st.button("Set All to Keep Current", key="btn_all_keep", use_container_width=True):
                for item in st.session_state["detected_conflicts"]:
                    item["resolution"] = "Keep Current"
                st.rerun()

        for idx, item in enumerate(st.session_state["detected_conflicts"]):
            with st.container(border=True):
                c_lbl, c_res = st.columns([3, 1.5])
                with c_lbl:
                    st.markdown(f"**Key:** `{item['key']}` | **Category:** `{item['category']}`")
                    v_col1, v_col2 = st.columns(2)
                    with v_col1:
                        st.markdown("<span style='font-size:0.75rem; color:#888;'>Current Value:</span>", unsafe_allow_html=True)
                        st.code(item['current_value'][:200] + ("..." if len(item['current_value']) > 200 else ""), language="json")
                    with v_col2:
                        st.markdown("<span style='font-size:0.75rem; color:#D4AF37;'>New Value:</span>", unsafe_allow_html=True)
                        st.code(item['new_value'][:200] + ("..." if len(item['new_value']) > 200 else ""), language="json")
                with c_res:
                    res_choice = st.radio(
                        "Action",
                        options=["Keep Current", "Overwrite with New", "Skip Item"],
                        index=["Keep Current", "Overwrite with New", "Skip Item"].index(item["resolution"]),
                        key=f"res_radio_{idx}"
                    )
                    item["resolution"] = res_choice

        btn_act1, btn_act2 = st.columns(2)
        with btn_act1:
            if st.button("Confirm & Save to DB", type="primary", use_container_width=True):
                saved_count = 0
                error_messages = []
                
                with st.spinner("Writing records..."):
                    for row in st.session_state["clean_staged_rows"]:
                        success, err = _safe_upsert_and_verify(row['category'], row['key'], row['value'], row['priority'])
                        if success:
                            saved_count += 1
                        else:
                            error_messages.append(err)
                    
                    for item in st.session_state["detected_conflicts"]:
                        if item["resolution"] == "Overwrite with New":
                            success, err = _safe_upsert_and_verify(item['category'], item['key'], item['new_value'], item['priority'])
                            if success:
                                saved_count += 1
                            else:
                                error_messages.append(err)

                if error_messages:
                    st.error(f"Failed to save {len(error_messages)} record(s)")
                        
                if saved_count > 0:
                    st.success(f"Successfully saved {saved_count} record(s)")
                    
                if saved_count > 0 or not error_messages:
                    st.session_state["detected_conflicts"] = None
                    st.session_state["clean_staged_rows"] = []
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        with btn_act2:
            if st.button("Cancel", use_container_width=True):
                st.session_state["detected_conflicts"] = None
                st.session_state["clean_staged_rows"] = []
                st.rerun()

        return

    mode = st.radio(
        "Mode",
        options=["Multimodal AI Extraction", "Manual Entry"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if mode == "Multimodal AI Extraction":
        source_type = st.segmented_control(
            "Input Format",
            options=["Text", "PDF", "Image"],
            default="Text"
        )

        extracted = []
        if source_type == "Text":
            raw_text = st.text_area(
                "Paste your text here",
                height=130,
                placeholder="Paste notes, tables, specs..."
            )
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button("Extract", key="btn_run_text_ext", type="primary", use_container_width=True):
                    if raw_text.strip():
                        with st.spinner("Extracting..."):
                            extracted = _extract_context_with_ai(raw_text=raw_text)
            with c2:
                if st.button("Reset", key="btn_rst_text_ext", use_container_width=True):
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        elif source_type == "PDF":
            pdf_file = st.file_uploader("Upload PDF", type=["pdf"], key="dlg_pdf_uploader")
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button("Extract PDF", key="btn_run_pdf_ext", type="primary", use_container_width=True):
                    if pdf_file is not None:
                        with st.spinner("Reading PDF..."):
                            pdf_text = _extract_text_from_pdf(pdf_file)
                            if pdf_text.strip():
                                extracted = _extract_context_with_ai(raw_text=pdf_text)
            with c2:
                if st.button("Reset", key="btn_rst_pdf_ext", use_container_width=True):
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        elif source_type == "Image":
            img_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "webp"], key="dlg_img_uploader")
            if img_file:
                st.image(img_file, caption="Preview", use_container_width=True)
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button("Scan Image", key="btn_run_vision_ext", type="primary", use_container_width=True):
                    if img_file is not None:
                        with st.spinner("Analyzing..."):
                            img_data_url, _ = _encode_image_to_base64(img_file)
                            if img_data_url:
                                extracted = _extract_context_with_ai(image_data_url=img_data_url)
            with c2:
                if st.button("Reset", key="btn_rst_vis_ext", use_container_width=True):
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        if extracted:
            st.session_state["extracted_context_df"] = pd.DataFrame(extracted)
            st.rerun()

    else:
        m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns([1.2, 1.5, 2.5, 0.8, 1])
        with m_col1:
            m_cat = st.selectbox("Category", options=["knowledge", "team", "jargon", "projects"], key="dlg_manual_cat")
        with m_col2:
            m_key = st.text_input("Key", placeholder="Entity name", key="dlg_manual_key")
        with m_col3:
            m_val = st.text_input("Value", placeholder='JSON or text', key="dlg_manual_val")
        with m_col4:
            m_prio = st.number_input("Priority", min_value=1, max_value=5, value=2, key="dlg_manual_prio")
        with m_col5:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("Add", key="btn_dlg_add_row", use_container_width=True):
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

    if st.session_state["extracted_context_df"] is not None and not st.session_state["extracted_context_df"].empty:
        st.markdown("---")
        st.markdown("### Staged Rows")

        column_config = {
            "category": st.column_config.SelectboxColumn("Category", options=["knowledge", "team", "jargon", "projects"], required=True),
            "key": st.column_config.TextColumn("Key", required=True),
            "value": st.column_config.TextColumn("Value", required=True, width="large"),
            "priority": st.column_config.NumberColumn("Priority", min_value=1, max_value=5, default=2)
        }

        edited_df = st.data_editor(
            st.session_state["extracted_context_df"],
            column_config=column_config,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="dlg_data_editor"
        )

        if st.button("Commit to Knowledge Base", key="btn_dlg_commit", type="primary", use_container_width=True):
            clean_rows, conflicts = _check_duplicates_against_db(edited_df)
            
            if conflicts:
                st.session_state["detected_conflicts"] = conflicts
                st.session_state["clean_staged_rows"] = clean_rows
                st.rerun()
            else:
                saved = 0
                with st.spinner("Saving..."):
                    for row in clean_rows:
                        success, _ = _safe_upsert_and_verify(row['category'], row['key'], row['value'], row.get('priority', 2))
                        if success:
                            saved += 1
                
                if saved > 0:
                    st.success(f"Saved {saved} record(s)")
                    st.session_state["extracted_context_df"] = None
                    st.rerun()


def render_echo_chat(container=None, height=600, title="Echo", caption=None, subtitle=None):
    target = container if container else st
    st.markdown(MODERN_CHAT_CSS, unsafe_allow_html=True)

    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "echo_selected_model" not in st.session_state:
        st.session_state["echo_selected_model"] = "qwen/qwen-2.5-72b-instruct"
    if "echo_source_archives" not in st.session_state:
        st.session_state["echo_source_archives"] = True
    if "echo_source_knowledge" not in st.session_state:
        st.session_state["echo_source_knowledge"] = True
    if "echo_source_web" not in st.session_state:
        st.session_state["echo_source_web"] = False
    if "knowledge_proposal" not in st.session_state:
        st.session_state["knowledge_proposal"] = None
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []

    with target.container():
        st.markdown('<div class="echo-main-container">', unsafe_allow_html=True)
        
        # Header
        st.markdown(
            f'''<div class="echo-header-bar">
                <div class="echo-logo-title">
                    {SVG_ECHO_LOGO}
                    <span class="echo-title">{title}</span>
                </div>
            </div>''',
            unsafe_allow_html=True
        )

        # Model Selector & Settings
        col_model, col_settings = st.columns([0.3, 0.1])
        with col_model:
            st.session_state["echo_selected_model"] = st.selectbox(
                "Model",
                options=[
                    "qwen/qwen-2.5-72b-instruct",
                    "qwen/qwen-image-3-pro",
                    "qwen/qwen-2.5-coder-32b-instruct",
                    "google/gemini-2.0-flash-exp:free",
                    "deepseek-chat",
                    "deepseek-reasoner",
                    "meta-llama/llama-3.1-8b-instruct:free",
                    "minimax/minimax-m3:free"
                ],
                index=0,
                label_visibility="collapsed",
                key="model_selector"
            )
        
        with col_settings:
            with st.popover("", icon=SVG_SETTINGS_ICON):
                st.markdown("#### Data Sources")
                st.session_state["echo_source_archives"] = st.checkbox("Meeting Archives", value=st.session_state["echo_source_archives"])
                st.session_state["echo_source_knowledge"] = st.checkbox("Knowledge Base", value=st.session_state["echo_source_knowledge"])
                st.session_state["echo_source_web"] = st.checkbox("Web Search", value=st.session_state["echo_source_web"])
                
                st.markdown("---")
                if st.button("Context Manager", use_container_width=True):
                    render_context_popup_dialog()
                
                if st.button("Clear Chat", use_container_width=True):
                    st.session_state["global_chat_history"] = []
                    st.session_state["knowledge_proposal"] = None
                    st.session_state["uploaded_files"] = []
                    st.rerun()

        # Chat Messages
        st.markdown('<div class="echo-chat-messages">', unsafe_allow_html=True)
        
        if not st.session_state["global_chat_history"]:
            st.markdown(
                f'''<div class="echo-msg-assistant">
                    <div class="echo-assistant-avatar">{SVG_ECHO_LOGO}</div>
                    <div class="echo-assistant-content">
                        <div class="echo-assistant-bubble">
                            Hi! I'm Echo. Ask me anything about your projects, meetings, or knowledge base.
                        </div>
                    </div>
                </div>''',
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state["global_chat_history"]:
                if msg["role"] == "user":
                    st.markdown(
                        f'''<div class="echo-msg-user">
                            <div class="echo-user-bubble">{msg["content"]}</div>
                            <div class="echo-user-avatar">{SVG_USER_ICON}</div>
                        </div>''',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'''<div class="echo-msg-assistant">
                            <div class="echo-assistant-avatar">{SVG_ECHO_LOGO}</div>
                            <div class="echo-assistant-content">
                                <div class="echo-assistant-bubble">{msg["content"]}</div>
                            </div>
                        </div>''',
                        unsafe_allow_html=True
                    )
                    
                    if msg.get("sources"):
                        sources_html = '<div class="echo-sources">'
                        for src in msg["sources"]:
                            sources_html += f'<a href="{src["url"]}" target="_blank" class="echo-source-pill">{SVG_GLOBE_ICON}{src["title"]}</a>'
                        sources_html += '</div>'
                        st.markdown(sources_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Knowledge Proposal
        if st.session_state["knowledge_proposal"]:
            prop = st.session_state["knowledge_proposal"]
            val_display = str(prop.get("value", ""))
            if len(val_display) > 150:
                val_display = val_display[:150] + "..."
                
            st.markdown(
                f'''<div class="echo-knowledge-card">
                    <div class="echo-knowledge-header">
                        {SVG_BRAIN_ICON} Knowledge Candidate
                    </div>
                    <div class="echo-knowledge-body">
                        Save <b>{prop.get("key")}</b> [<i>{prop.get("category")}</i>]?<br/>
                        <code>{val_display}</code>
                    </div>
                    <div class="echo-knowledge-actions">
                        <button class="echo-btn-primary" onclick="document.getElementById('btn_confirm_prop').click()">Save</button>
                        <button class="echo-btn-secondary" onclick="document.getElementById('btn_dismiss_prop').click()">Dismiss</button>
                    </div>
                </div>''',
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save to Knowledge Base", key="btn_confirm_auto_prop", use_container_width=True):
                    existing_map = _get_existing_knowledge_map()
                    cat_clean = str(prop["category"]).strip().lower()
                    key_clean = str(prop["key"]).strip()
                    
                    if (cat_clean, key_clean.lower()) in existing_map:
                        st.warning(f"Key `{key_clean}` already exists")
                    else:
                        success, err = _safe_upsert_and_verify(
                            category=prop["category"],
                            key=key_clean,
                            value=str(prop["value"]),
                            priority=prop.get("priority", 2)
                        )
                        if success:
                            st.session_state["global_chat_history"].append({
                                "role": "assistant",
                                "content": f"✅ Saved `{key_clean}` to Knowledge Base"
                            })
                        else:
                            st.session_state["global_chat_history"].append({
                                "role": "assistant",
                                "content": f"❌ Failed to save: {err}"
                            })
                            
                    st.session_state["knowledge_proposal"] = None
                    st.rerun()
            with col2:
                if st.button("Dismiss", key="btn_dismiss_auto_prop", use_container_width=True):
                    st.session_state["knowledge_proposal"] = None
                    st.rerun()

        # Input Area
        st.markdown('<div class="echo-input-area">', unsafe_allow_html=True)
        
        # File upload preview
        if st.session_state["uploaded_files"]:
            for file in st.session_state["uploaded_files"]:
                st.markdown(
                    f'''<div class="echo-file-preview">
                        {SVG_UPLOAD_ICON} {file.name}
                    </div>''',
                    unsafe_allow_html=True
                )
        
        # Input row
        st.markdown('<div class="echo-input-row">', unsafe_allow_html=True)
        
        col_attach, col_input, col_send = st.columns([0.1, 0.8, 0.1])
        
        with col_attach:
            uploaded_file = st.file_uploader(
                "",
                type=["pdf", "png", "jpg", "jpeg", "txt", "docx"],
                key="main_file_uploader",
                label_visibility="collapsed",
                accept_multiple_files=False
            )
            if uploaded_file and uploaded_file not in st.session_state["uploaded_files"]:
                st.session_state["uploaded_files"].append(uploaded_file)
                st.rerun()
        
        with col_input:
            user_input = st.chat_input("Ask Echo...", key="main_chat_input")
        
        with col_send:
            send_button = st.button("↑", key="send_btn", type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Process input
        if user_input or send_button:
            if user_input:
                st.session_state["global_chat_history"].append({"role": "user", "content": user_input})

                # Show thinking indicator
                with st.empty():
                    st.markdown(
                        '''<div class="echo-thinking">
                            <div class="echo-thinking-dot"></div>
                            <div class="echo-thinking-dot"></div>
                            <div class="echo-thinking-dot"></div>
                            <span class="echo-thinking-text">Thinking...</span>
                        </div>''',
                        unsafe_allow_html=True
                    )

                archives = fetch_meeting_archives(limit=100) if st.session_state["echo_source_archives"] else []
                web_context, web_sources = _perform_web_search(user_input) if st.session_state["echo_source_web"] else ("", [])
                
                # Process uploaded files if any
                file_context = ""
                if st.session_state["uploaded_files"]:
                    for file in st.session_state["uploaded_files"]:
                        if file.name.endswith('.pdf'):
                            file_context += _extract_text_from_pdf(file) + "\n\n"
                        elif file.name.endswith(('.png', '.jpg', '.jpeg')):
                            # For images, use vision model
                            if "image" in st.session_state["echo_selected_model"]:
                                img_data, _ = _encode_image_to_base64(file)
                                if img_data:
                                    extracted = _extract_context_with_ai(image_data_url=img_data)
                                    if extracted:
                                        file_context += f"Image analysis: {extracted}\n\n"
                
                answer, proposed_fact = _query_echo_backend(
                    question=user_input + ("\n\nAttached files:\n" + file_context if file_context else ""),
                    archive_records=archives,
                    chat_history=st.session_state["global_chat_history"],
                    web_context=web_context,
                    model_name=st.session_state["echo_selected_model"],
                    include_knowledge=st.session_state["echo_source_knowledge"]
                )
                
                st.session_state["global_chat_history"].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": web_sources
                })
                
                if proposed_fact:
                    st.session_state["knowledge_proposal"] = proposed_fact
                
                # Clear uploaded files after processing
                st.session_state["uploaded_files"] = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


def _perform_web_search(query: str) -> tuple:
    sources = []
    text_snippets = []
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0"}
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
                text_snippets.append(f"[{i+1}] {clean_snippet}")
    except Exception:
        pass
    return ("\n".join(text_snippets), sources)


def _extract_context_with_ai(raw_text: str = "", image_data_url: str = None, extraction_model: str = "qwen/qwen-image-3-pro") -> list:
    system_prompt = (
        "You are an enterprise data extraction engine. "
        "Extract all entities, properties, procedures, definitions, or table records. "
        "Return JSON with 'items' array containing objects with: 'category', 'key', 'value', 'priority' (1-5)."
    )

    is_openrouter = "/" in extraction_model or extraction_model.endswith(":free")

    if is_openrouter:
        api_key = str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
        if not api_key:
            st.error("OpenRouter API Key missing")
            return []
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://echo.prime.ph",
            "X-Title": "Echo AI"
        }
        
        if image_data_url:
            user_content = [
                {"type": "text", "text": "Extract structured data from this image"},
                {"type": "image_url", "image_url": {"url": image_data_url}}
            ]
        else:
            user_content = raw_text[:20000]

        payload = {
            "model": extraction_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
    elif image_data_url:
        api_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
        if not api_key:
            st.error("OpenAI API Key missing")
            return []
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": "Extract structured data from this image"},
                    {"type": "image_url", "image_url": {"url": image_data_url}}
                ]}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 4000
        }
    else:
        api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
        if not api_key:
            st.error("DeepSeek API Key missing")
            return []
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
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
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
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
                
                item_matches = re.findall(
                    r'\{\s*"category"\s*:\s*"([^"]+)"\s*,\s*"key"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*(?:\"(.*?)\"|(\{.*?\}))\s*(?:,\s*"priority"\s*:\s*(\d+))?\s*\}',
                    cleaned, re.DOTALL
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

        st.error(f"Extraction error ({resp.status_code})")
        return []
    except Exception as e:
        st.error(f"Extraction error: {e}")
        return []


def _normalize_extracted_items(items: list) -> list:
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
    model_name: str = "qwen/qwen-2.5-72b-instruct",
    include_knowledge: bool = True
) -> tuple:
    is_openrouter = "/" in model_name or model_name.endswith(":free")
    
    if is_openrouter:
        api_key = str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
        if not api_key:
            return "OpenRouter API Key missing", None
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://echo.prime.ph",
            "X-Title": "Echo AI"
        }
    else:
        api_key = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
        if not api_key:
            return "DeepSeek API Key missing", None
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    archive_context = json.dumps(archive_records, indent=1) if archive_records else "[]"

    if include_knowledge:
        context_data = fetch_echo_context()
        team_list = ", ".join(context_data.get('team', []))
        jargon_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('jargon', {}).items()])
        projects = ", ".join(context_data.get('projects', []))
        knowledge_list = "\n".join([f"- {k}: {v}" for k, v in context_data.get('knowledge', {}).items()])

        knowledge_section = f"""
ECHO KNOWLEDGE BASE:
-------------------
TEAM: {team_list}
PROJECTS: {projects}
JARGON:
{jargon_list}
KNOWLEDGE:
{knowledge_list}
"""
    else:
        knowledge_section = ""

    current_date_str = datetime.now().strftime("%A, %B %d, %Y")
    web_section = f"\nWEB RESULTS:\n{web_context}\n" if web_context else ""

    context_string = f"""
DATE: {current_date_str}
{knowledge_section}
{web_section}
"""

    system_prompt = (
        "You are Echo, an executive AI analyst for PRIME Philippines. "
        f"Current date: {current_date_str}. "
        "Answer accurately using Markdown. No emojis. "
        "Respond in JSON format:\n"
        "{\n"
        '  "response": "Your answer",\n'
        '  "propose_knowledge": null OR {{"category": "knowledge|team|jargon|projects", "key": "Name", "value": "Data", "priority": 2}}\n'
        "}\n\n"
        f"{context_string}\n"
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nArchives:\n{archive_context[:24000]}"}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"}
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
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

        return f"Error ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Exception: {e}", None
