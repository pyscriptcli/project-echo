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
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle;">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 17 12 22 22 17"></polyline>
    <polyline points="2 12 12 17 22 12"></polyline>
</svg>
"""

SVG_USER_ICON = """
<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04z"></path>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04z"></path>
</svg>
"""

CHAT_COMPACT_ALIGNED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@1,500;1,600&display=swap');

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.echo-main-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 20px;
}

.echo-modern-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0;
    border-bottom: 1px solid rgba(212, 175, 55, 0.15);
    margin-bottom: 20px;
    background: transparent;
}

.echo-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.echo-title {
    font-family: 'Playfair Display', Georgia, serif !important;
    font-style: italic;
    font-size: 1.4rem;
    font-weight: 600;
    color: #1A2B4C;
    margin: 0;
    letter-spacing: -0.02em;
}

.echo-header-controls {
    display: flex;
    align-items: center;
    gap: 12px;
}

.model-selector-container {
    position: relative;
}

.model-selector-container > div {
    background: #F8FAFC !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    min-width: 220px !important;
    transition: all 0.2s ease !important;
}

.model-selector-container label {
    display: none !important;
}

.upload-button-container {
    display: flex;
    align-items: center;
}

.settings-button-container button {
    background: transparent !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 8px !important;
    width: 38px !important;
    height: 38px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
}

.echo-chat-area {
    min-height: 400px;
    max-height: calc(100vh - 350px);
    overflow-y: auto;
    padding: 10px 0;
    margin-bottom: 20px;
}

.echo-welcome {
    text-align: center;
    padding: 60px 20px;
    color: #64748B;
}

.echo-welcome h2 {
    font-family: 'Playfair Display', Georgia, serif;
    font-style: italic;
    font-size: 2rem;
    color: #1A2B4C;
    margin-bottom: 12px;
    font-weight: 600;
}

.echo-message {
    margin-bottom: 24px;
    display: flex;
    gap: 12px;
    animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.echo-message-user {
    justify-content: flex-end;
}

.echo-message-assistant {
    justify-content: flex-start;
}

.echo-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-weight: 600;
    font-size: 0.85rem;
}

.echo-avatar-user {
    background: #111A2B;
    border: 1px solid #D4AF37;
    color: #D4AF37;
}

.echo-avatar-assistant {
    background: #111A2B;
    border: 1px solid #D4AF37;
    color: #D4AF37;
}

.echo-message-content {
    max-width: 75%;
    padding: 12px 18px;
    border-radius: 12px;
    font-size: 0.95rem;
    line-height: 1.6;
}

.echo-message-user .echo-message-content {
    background: #111A2B;
    color: #FFFFFF;
    border: 1px solid #D4AF37;
    border-bottom-right-radius: 4px;
}

.echo-message-assistant .echo-message-content {
    background: #F8FAFC;
    color: #1E293B;
    border: 1px solid rgba(212, 175, 55, 0.15);
    border-bottom-left-radius: 4px;
}

.echo-sources {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(212, 175, 55, 0.15);
}

.echo-source-pill {
    display: inline-flex;
    align-items: center;
    background: #111A2B;
    border: 1px solid #D4AF37;
    border-radius: 16px;
    padding: 4px 10px;
    font-size: 0.75rem;
    color: #D4AF37 !important;
    text-decoration: none !important;
    font-weight: 500;
}

.echo-input-area {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 20px 0;
    border-top: 1px solid rgba(212, 175, 55, 0.1);
    margin-top: auto;
}

.echo-thinking {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 18px;
    background: #F8FAFC;
    border-radius: 12px;
    border: 1px solid rgba(212, 175, 55, 0.15);
    margin-bottom: 20px;
    font-size: 0.85rem;
    color: #64748B;
}

.echo-pulse-dot {
    width: 6px;
    height: 6px;
    background-color: #D4AF37;
    border-radius: 50%;
    animation: echo-pulse 1.4s infinite ease-in-out both;
}

.echo-pulse-dot:nth-child(2) { animation-delay: 0.2s; }
.echo-pulse-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes echo-pulse {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

.echo-knowledge-card {
    background: #FFFFFF;
    border: 1px solid #D4AF37;
    border-radius: 12px;
    padding: 16px;
    margin: 16px 0;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.1);
}

.echo-knowledge-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    color: #854D0E;
    margin-bottom: 10px;
}

.echo-knowledge-card-body {
    font-size: 0.9rem;
    color: #1F2937;
    margin-bottom: 14px;
    line-height: 1.5;
}

.echo-knowledge-card code {
    background: #F8FAFC;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.85rem;
    color: #1A2B4C;
    border: 1px solid rgba(212, 175, 55, 0.2);
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

def _safe_upsert_and_verify(category: str, key: str, value: str, priority: int) -> tuple[bool, str]:
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
        st.markdown("<p style='font-size:0.95rem; font-weight:600; color:#854D0E;'>⚠️ Duplicate Entries Flagged in Knowledge Base</p>", unsafe_allow_html=True)
        st.caption("The following items already exist in the database with different or identical values. Choose how each key should be resolved:")

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
                        st.markdown("<span style='font-size:0.75rem; color:#64748B;'>Current Value:</span>", unsafe_allow_html=True)
                        st.code(item['current_value'][:200] + ("..." if len(item['current_value']) > 200 else ""), language="json")
                    with v_col2:
                        st.markdown("<span style='font-size:0.75rem; color:#854D0E;'>New Incoming Value:</span>", unsafe_allow_html=True)
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
            if st.button("Confirm Resolution & Save to DB", type="primary", use_container_width=True):
                saved_count = 0
                error_messages = []
                
                with st.spinner("Writing and actively verifying records..."):
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
                    st.error(f"Failed to save {len(error_messages)} record(s):")
                    for err_msg in error_messages:
                        st.caption(f"❌ {err_msg}")
                        
                if saved_count > 0:
                    st.success(f"Successfully saved and verified {saved_count} record(s).")
                    
                if saved_count > 0 or not error_messages:
                    st.session_state["detected_conflicts"] = None
                    st.session_state["clean_staged_rows"] = []
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        with btn_act2:
            if st.button("Cancel & Back to Staging", use_container_width=True):
                st.session_state["detected_conflicts"] = None
                st.session_state["clean_staged_rows"] = []
                st.rerun()

        return

    mode = st.radio(
        "Mode",
        options=["Multimodal AI Extraction (Text/PDF/Vision)", "Manual Row Entry"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if mode == "Multimodal AI Extraction (Text/PDF/Vision)":
        source_type = st.segmented_control(
            "Input Format",
            options=["Text Notes", "PDF Document", "Image / Vision Scan"],
            default="Text Notes"
        )

        extracted = []
        if source_type == "Text Notes":
            raw_text = st.text_area(
                "Raw Context / Knowledge Dump",
                height=130,
                placeholder="Paste raw unstructured notes, tables, specs, or logs here..."
            )
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button("Extract Knowledge", key="btn_run_text_ext", type="primary", use_container_width=True):
                    if raw_text.strip():
                        with st.spinner("Extracting structured records..."):
                            extracted = _extract_context_with_ai(raw_text=raw_text)
                    else:
                        st.warning("Please supply context notes.")
            with c2:
                if st.button("Reset Staged Table", key="btn_rst_text_ext", use_container_width=True):
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        elif source_type == "PDF Document":
            pdf_file = st.file_uploader("Upload PDF Document", type=["pdf"], key="dlg_pdf_uploader")
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button("Parse & Extract PDF", key="btn_run_pdf_ext", type="primary", use_container_width=True):
                    if pdf_file is not None:
                        with st.spinner("Reading and structuring PDF content..."):
                            pdf_text = _extract_text_from_pdf(pdf_file)
                            if pdf_text.strip():
                                extracted = _extract_context_with_ai(raw_text=pdf_text)
                            else:
                                st.error("No extractable text stream found in PDF.")
                    else:
                        st.warning("Please upload a PDF file first.")
            with c2:
                if st.button("Reset Staged Table", key="btn_rst_pdf_ext", use_container_width=True):
                    st.session_state["extracted_context_df"] = None
                    st.rerun()

        elif source_type == "Image / Vision Scan":
            img_file = st.file_uploader("Upload Image/Scan/Blueprint", type=["png", "jpg", "jpeg", "webp"], key="dlg_img_uploader")
            if img_file:
                st.image(img_file, caption="Scan Preview", use_container_width=True)
            c1, c2 = st.columns([1.5, 1])
            with c1:
                if st.button("Scan with Vision AI", key="btn_run_vision_ext", type="primary", use_container_width=True):
                    if img_file is not None:
                        with st.spinner("Analyzing image visual data with AI..."):
                            img_data_url, _ = _encode_image_to_base64(img_file)
                            if img_data_url:
                                extracted = _extract_context_with_ai(image_data_url=img_data_url)
                    else:
                        st.warning("Please upload an image.")
            with c2:
                if st.button("Reset Staged Table", key="btn_rst_vis_ext", use_container_width=True):
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

        if st.button("Validate & Commit to Knowledge Base", key="btn_dlg_commit", type="primary", use_container_width=True):
            clean_rows, conflicts = _check_duplicates_against_db(edited_df)
            
            if conflicts:
                st.session_state["detected_conflicts"] = conflicts
                st.session_state["clean_staged_rows"] = clean_rows
                st.rerun()
            else:
                saved = 0
                failed = 0
                with st.spinner("Saving and actively verifying records..."):
                    for row in clean_rows:
                        success, err = _safe_upsert_and_verify(
                            category=row['category'], 
                            key=row['key'], 
                            value=row['value'], 
                            priority=row.get('priority', 2)
                        )
                        if success:
                            saved += 1
                        else:
                            failed += 1
                
                if failed > 0:
                    st.error(f"Failed to save {failed} record(s). Check DB connection logs.")
                if saved > 0:
                    st.success(f"Successfully saved and verified {saved} new record(s).")
                    st.session_state["extracted_context_df"] = None
                    st.rerun()


def render_echo_chat(container=None, height=520, title="Ask Echo", caption=None, subtitle=None):
    target = container if container else st
    st.markdown(CHAT_COMPACT_ALIGNED_CSS, unsafe_allow_html=True)

    if "global_chat_history" not in st.session_state:
        st.session_state["global_chat_history"] = []
    if "echo_selected_model" not in st.session_state:
        st.session_state["echo_selected_model"] = "qwen/qwen2.5-vl-72b-instruct"
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
            '<div class="echo-modern-header">'
            '<div class="echo-header-left">'
            f'{SVG_ECHO_LOGO}<span class="echo-title">{title}</span>'
            '</div>'
            '<div class="echo-header-controls">',
            unsafe_allow_html=True
        )
        
        # Multimodal Model Selector
        st.markdown('<div class="model-selector-container">', unsafe_allow_html=True)
        st.session_state["echo_selected_model"] = st.selectbox(
            "Model",
            options=[
                "qwen/qwen2.5-vl-72b-instruct",
                "google/gemini-2.0-flash-001",
                "openai/gpt-4o-mini",
                "deepseek/deepseek-chat"
            ],
            index=0,
            label_visibility="collapsed",
            key="model_selector_header"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Header File Upload
        st.markdown('<div class="upload-button-container">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload",
            type=["pdf", "png", "jpg", "jpeg", "webp", "txt"],
            accept_multiple_files=False,
            key="header_file_uploader",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file and uploaded_file not in st.session_state["uploaded_files"]:
            st.session_state["uploaded_files"] = [uploaded_file]
            st.toast(f"📎 Attached for next prompt: {uploaded_file.name}", icon="✅")
        
        # Settings Popover
        st.markdown('<div class="settings-button-container">', unsafe_allow_html=True)
        with st.popover("⚙️", help="Settings"):
            st.markdown("### ⚙️ Settings")
            st.markdown("---")
            st.markdown("**Data Sources**")
            st.session_state["echo_source_archives"] = st.checkbox("Meeting Archives", value=st.session_state["echo_source_archives"])
            st.session_state["echo_source_knowledge"] = st.checkbox("Echo Knowledge Base", value=st.session_state["echo_source_knowledge"])
            st.session_state["echo_source_web"] = st.checkbox("Search Web", value=st.session_state["echo_source_web"])
            
            st.markdown("---")
            st.markdown("**Knowledge Management**")
            if st.button("Open Context Manager", key="btn_trigger_context_dialog", use_container_width=True):
                render_context_popup_dialog()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear Button
        if st.button("🗑️", key="btn_clear_global_chat", help="Clear conversation"):
            st.session_state["global_chat_history"] = []
            st.session_state["knowledge_proposal"] = None
            st.session_state["uploaded_files"] = []
            st.rerun()
        
        st.markdown('</div></div></div>', unsafe_allow_html=True)

        # Chat Area
        st.markdown('<div class="echo-chat-area">', unsafe_allow_html=True)
        chat_box = st.container()
        st.markdown('</div>', unsafe_allow_html=True)

        with chat_box:
            if not st.session_state["global_chat_history"]:
                st.markdown(
                    '<div class="echo-welcome">'
                    f'{SVG_ECHO_LOGO}'
                    '<h2>Welcome to Echo</h2>'
                    '<p>Your AI assistant for PRIME Philippines. Ask me anything or attach an image/PDF.</p>'
                    '</div>',
                    unsafe_allow_html=True
                )
            else:
                for msg in st.session_state["global_chat_history"]:
                    if msg["role"] == "user":
                        st.markdown(
                            f'<div class="echo-message echo-message-user">'
                            f'<div class="echo-message-content">{msg["content"]}</div>'
                            f'<div class="echo-avatar echo-avatar-user">You</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<div class="echo-message echo-message-assistant">'
                            f'<div class="echo-avatar echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                            f'<div class="echo-message-content">{msg["content"]}</div>'
                            '</div>',
                            unsafe_allow_html=True
                        )
                        
                        if msg.get("sources"):
                            sources_html = '<div class="echo-sources">'
                            for src in msg["sources"]:
                                sources_html += f'<a href="{src["url"]}" target="_blank" class="echo-source-pill">{SVG_GLOBE_ICON}{src["title"]}</a>'
                            sources_html += '</div>'
                            st.markdown(sources_html, unsafe_allow_html=True)

        # Knowledge Proposal Card
        if st.session_state["knowledge_proposal"]:
            prop = st.session_state["knowledge_proposal"]
            val_display = str(prop.get("value", ""))
            if len(val_display) > 180:
                val_display = val_display[:180] + "..."
                
            st.markdown(
                f'<div class="echo-knowledge-card">'
                f'<div class="echo-knowledge-card-header">'
                f'{SVG_BRAIN_ICON}Knowledge Base Candidate'
                f'</div>'
                f'<div class="echo-knowledge-card-body">'
                f'Save <b>{prop.get("key")}</b> [<i>{prop.get("category")}</i>] to Knowledge Base?<br/>'
                f'<code>{val_display}</code>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            kp_col1, kp_col2 = st.columns(2)
            with kp_col1:
                if st.button("✅ Save to Knowledge Base", key="btn_confirm_auto_prop", use_container_width=True):
                    existing_map = _get_existing_knowledge_map()
                    cat_clean = str(prop["category"]).strip().lower()
                    key_clean = str(prop["key"]).strip()
                    
                    if (cat_clean, key_clean.lower()) in existing_map:
                        st.warning(f"Key `{key_clean}` already exists in `{cat_clean}`.")
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
                                "content": f"✅ Confirmed: `{key_clean}` verified and saved to Echo Knowledge Base."
                            })
                        else:
                            st.session_state["global_chat_history"].append({
                                "role": "assistant",
                                "content": f"❌ Error: Failed to register `{key_clean}`. Detail: {err}"
                            })
                            
                        st.session_state["knowledge_proposal"] = None
                        st.rerun()
            with kp_col2:
                if st.button("❌ Dismiss", key="btn_dismiss_auto_prop", use_container_width=True):
                    st.session_state["knowledge_proposal"] = None
                    st.rerun()

        # Input Area
        st.markdown('<div class="echo-input-area">', unsafe_allow_html=True)
        active_prompt = st.chat_input("Ask Echo anything...", key="echo_chat_input")
        st.markdown('</div>', unsafe_allow_html=True)

        if active_prompt:
            attached_files = st.session_state.get("uploaded_files", [])
            display_prompt = active_prompt
            if attached_files:
                display_prompt += f" _(Attached: {', '.join([f.name for f in attached_files])})_"
            
            st.session_state["global_chat_history"].append({"role": "user", "content": display_prompt})

            with chat_box:
                st.markdown(
                    '<div class="echo-thinking">'
                    f'<div class="echo-avatar echo-avatar-assistant">{SVG_ECHO_LOGO}</div>'
                    '<div style="display: flex; align-items: center; gap: 6px;">'
                    '<div class="echo-pulse-dot"></div>'
                    '<div class="echo-pulse-dot"></div>'
                    '<div class="echo-pulse-dot"></div>'
                    '</div>'
                    '<span>Thinking...</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

            archives = fetch_meeting_archives(limit=100) if st.session_state["echo_source_archives"] else []
            web_context, web_sources = _perform_web_search(active_prompt) if st.session_state["echo_source_web"] else ("", [])
            
            answer, proposed_fact = _query_echo_backend(
                question=active_prompt,
                archive_records=archives,
                chat_history=st.session_state["global_chat_history"],
                web_context=web_context,
                model_name=st.session_state["echo_selected_model"],
                include_knowledge=st.session_state["echo_source_knowledge"],
                uploaded_files=attached_files
            )
            
            # Clear uploaded files after processing
            st.session_state["uploaded_files"] = []
            
            st.session_state["global_chat_history"].append({
                "role": "assistant",
                "content": answer,
                "sources": web_sources
            })
            if proposed_fact:
                st.session_state["knowledge_proposal"] = proposed_fact

            st.rerun()


def _perform_web_search(query: str) -> tuple:
    sources = []
    text_snippets = []
    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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


def _extract_context_with_ai(raw_text: str = "", image_data_url: str = None, extraction_model: str = "qwen/qwen2.5-vl-72b-instruct") -> list:
    system_prompt = (
        "You are an enterprise data extraction engine for PRIME Philippines. "
        "Analyze the input (text, PDF content, or scanned images/diagrams) and extract all entities, properties, procedures, definitions, or table records. "
        "For complex, tabular, or scouting logs that have varying schemas, assign 'category': 'knowledge', 'key': [Main Entity Name or Code], "
        "and 'value': a compact JSON string capturing all available key-value pairs. "
        "For team members, jargon, or projects, assign 'category' to 'team', 'jargon', or 'projects' respectively with a string or JSON 'value'. "
        "Always return a valid JSON object with key 'items' containing an array of objects with: 'category', 'key', 'value', 'priority' (integer 1-5)."
    )

    api_key = str(st.secrets.get("OPENROUTER_API_KEY", "")).strip()
    if not api_key:
        st.error("OpenRouter API Key is required for multimodal extraction.")
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
            {"type": "text", "text": "Extract all structured knowledge and data records from this image."},
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
        st.error(f"Extraction service error ({resp.status_code}): {resp.text}")
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
    model_name: str = "qwen/qwen2.5-vl-72b-instruct",
    include_knowledge: bool = True,
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

    system_prompt = (
        "You are Echo, an executive AI analyst for PRIME Philippines. "
        f"The current date is {current_date_str}. Directly answer temporal inquiries accurately. "
        "Synthesize available sources, structured knowledge, and meeting archives accurately. Format responses concisely using Markdown headings, lists, and tables where appropriate. No emojis. "
        "Determine if the user input defines a new team member role, acronym, project specification, property update, or general entity that should be preserved in the persistent Knowledge Base. "
        "Always respond in JSON format matching the schema:\n"
        "{\n"
        "  \"response\": \"Your thorough markdown response to the user\",\n"
        "  \"propose_knowledge\": null OR {\"category\": \"knowledge|team|jargon|projects\", \"key\": \"Term/Entity Name\", \"value\": \"Definition or JSON string\", \"priority\": 2}\n"
        "}\n\n"
        f"{context_string}\n"
    )

    messages = [{"role": "system", "content": f"{system_prompt}\n\nMeeting Archives:\n{archive_context[:24000]}"}]
    
    # Add previous chat history (text-only)
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

        return f"Service notice ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Analysis exception: {e}", None
