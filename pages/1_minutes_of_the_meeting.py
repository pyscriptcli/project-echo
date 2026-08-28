import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import datetime
import json
import re
import subprocess
import tempfile
import time
from io import BytesIO

import docx
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import parse_xml
from docx.shared import Inches, Pt, RGBColor
import pandas as pd
import PyPDF2
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, ListFlowable, ListItem
import requests
import streamlit.components.v1 as components

# Centralized DB & Components
from utils.db import get_supabase_client, fetch_echo_context
from components.sidebar import setup_page_layout

# 1. Page Configuration (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Project Echo - MoM Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Render Global Navigation
setup_page_layout()

# 3. Custom CSS & Pure CSS SVG Icon Injection (Strictly No Emojis)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=Playfair+Display:ital,wght@1,400;1,500;1,600&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp {
    background-color: #F3EFE6; 
    background-image: linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
    background-size: 80px 80px; color: #2D2D2D;
}
.stApp > header { display: none !important; }
.block-container { padding-top: 1.5rem !important; padding-right: 2rem !important; }
h3 { font-family: 'Playfair Display', serif !important; font-style: italic !important; font-weight: 400 !important; color: #1A2B4C !important; letter-spacing: 0.02em; margin-bottom: 0.25rem; font-size: 1.25rem !important; }
.playfair-label { font-family: 'Playfair Display', serif !important; font-style: italic !important; color: #1A2B4C !important; font-size: 1.05rem !important; margin-bottom: 0.25rem !important; display: block; }

/* Containers & Inputs */
div[data-testid="stVerticalBlockBorderWrapper"] { background-color: #FFFFFF !important; border-radius: 12px !important; box-shadow: 14px 8px 24px rgba(0, 0, 0, 0.06), 4px 4px 10px rgba(0, 0, 0, 0.03) !important; border: 1px solid rgba(0, 0, 0, 0.05) !important; padding: 1.5rem !important; margin-bottom: 1.25rem !important; }
.stTextArea textarea, .stTextInput input, .stSelectbox select { background-color: #FAFAFA !important; border: 1px solid rgba(0,0,0,0.08) !important; border-radius: 8px !important; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important; }
.stTextArea textarea:focus, .stTextInput input:focus, .stSelectbox select:focus { background-color: #FFFFFF !important; border-color: #D4AF37 !important; }

/* Buttons General */
.stButton > button { background-color: #222222 !important; color: #FFFFFF !important; border: none !important; border-radius: 50px !important; font-family: 'Montserrat', sans-serif !important; font-weight: 500 !important; font-size: 0.82rem !important; height: 36px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important; transition: all 0.2s ease !important; width: 100% !important; display: flex !important; align-items: center !important; justify-content: center !important; }
.stButton > button:hover { background-color: #D4AF37 !important; color: #161616 !important; }

/* Settings Button SVG Icon */
.stButton > button[key="card_settings_btn"] {
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    margin: 0 auto !important;
}
.stButton > button[key="card_settings_btn"]::before {
    content: "";
    display: inline-block;
    width: 18px;
    height: 18px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58a.49.49 0 0 0 .12-.61l-1.92-3.32a.488.488 0 0 0-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54a.484.484 0 0 0-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58a.49.49 0 0 0-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z'/%3E%3C/svg%3E") no-repeat center;
}

/* Save Meeting Button SVG Icon */
.stButton > button[key="btn_save_supabase_bottom"]::before {
    content: "";
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-right: 6px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z'/%3E%3C/svg%3E") no-repeat center;
}

/* Delete Row Button Styling & SVG Icon */
.stButton > button[key^="del_"] { background-color: #FDF9F9 !important; color: #B23A3A !important; border: 1px solid rgba(178, 58, 58, 0.25) !important; }
.stButton > button[key^="del_"]:hover { background-color: #B23A3A !important; color: #FFFFFF !important; }
.stButton > button[key^="del_"]::before {
    content: "";
    display: inline-block;
    width: 15px;
    height: 15px;
    margin-right: 4px;
    background-color: currentColor;
    -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E") no-repeat center;
    mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'/%3E%3C/svg%3E") no-repeat center;
}

/* Chat Styling */
.chat-container { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; padding-bottom: 1rem; }
.chat-ai { align-self: flex-start; background-color: transparent; color: #1A1A1A; padding: 0.2rem; max-width: 95%; font-size: 0.88rem; line-height: 1.5; }
.chat-user-wrap { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 0.2rem; }
.chat-user { background-color: #F3F4F6; color: #1A1A1A; padding: 0.55rem 0.95rem; border-radius: 14px; max-width: 82%; font-size: 0.88rem; line-height: 1.45; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 4. SVG Templates for HTML components
COPY_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="vertical-align: middle; margin-right: 6px;"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>'

# 5. Constants & Config
DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"
GROQ_API_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()
GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
OPENAI_API_KEY = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
OPENAI_AUDIO_URL = "https://api.openai.com/v1/audio/transcriptions"

CRD_MEMBERS = ["Sondi Tuazon", "Kristina Balajadia", "Meliza Zapata", "Dykstra Pineda", "Cedtrix Rena", "Carlo Medina", "Dave Policarpio", "Irish Rima"]
LOCATION_PRESETS = [
    "GreatWork Mega Tower 32F - Secret Room",
    "GreatWork Mega Tower 32F - Small Meeting Room",
    "GreatWork Mega Tower 24F - Meeting Room",
    "GreatWork Mega Tower 32F - Board Room",
    "GreatWork Mega Tower 32F - Co-working",
    "Online Meeting"
]
MEETING_TYPE_OPTIONS = ["Internal", "External", "Team"]

# 6. Session State Initialization
if "transcript" not in st.session_state: st.session_state["transcript"] = ""
if "df" not in st.session_state: st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
if "other_discussions" not in st.session_state: st.session_state["other_discussions"] = ""
if "show_settings" not in st.session_state: st.session_state["show_settings"] = False
if "tokens_used" not in st.session_state: st.session_state["tokens_used"] = 0
if "last_api_call" not in st.session_state: st.session_state["last_api_call"] = None
if "selected_engine" not in st.session_state: st.session_state["selected_engine"] = "AI - DeepSeek"
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "meeting_date" not in st.session_state: st.session_state["meeting_date"] = datetime.date.today()
if "meeting_location" not in st.session_state: st.session_state["meeting_location"] = ""
if "meeting_type" not in st.session_state: st.session_state["meeting_type"] = "Internal"
if "meeting_client_name" not in st.session_state: st.session_state["meeting_client_name"] = ""
if "meeting_selected_crd" not in st.session_state: st.session_state["meeting_selected_crd"] = []
if "meeting_ext_attendees" not in st.session_state: st.session_state["meeting_ext_attendees"] = ""
if "meeting_prep_name" not in st.session_state: st.session_state["meeting_prep_name"] = ""
if "meeting_prep_desig" not in st.session_state: st.session_state["meeting_prep_desig"] = ""
if "meeting_conf_name" not in st.session_state: st.session_state["meeting_conf_name"] = ""
if "meeting_conf_desig" not in st.session_state: st.session_state["meeting_conf_desig"] = ""

# 7. Core Logic Functions
def save_meeting_to_supabase(meeting_details, df, other_discussions, transcript):
    client = get_supabase_client()
    if not client: return False, "Supabase client uninitialized."
    try:
        table_items = [{"Discussion Points": str(row.get("Discussion Points", "")), "Action Plan": str(row.get("Action Plan", "")), "Indicative Delivery Date": str(row.get("Indicative Delivery Date", "")), "Person-in-charge": str(row.get("Person-in-charge", ""))} for _, row in df.iterrows()]
        meeting_id = f"MOM-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        client_name = meeting_details.get("company_name", "Unknown Client")
        meeting_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        if meeting_details.get("date"):
            try: meeting_date_str = datetime.datetime.strptime(meeting_details.get("date"), "%B %d, %Y").strftime("%Y-%m-%d")
            except Exception: pass
        
        payload = {
            "meeting_id": meeting_id, "client_name": client_name, "meeting_date": meeting_date_str,
            "meeting_type": meeting_details.get("meeting_type", "Internal"),
            "location": meeting_details.get("location", ""), "prepared_by": meeting_details.get("prep_name", ""),
            "confirmed_by": meeting_details.get("conf_name", ""), "summary_md": f"### Summary\n{other_discussions}",
            "transcript_md": f"### Transcript\n{transcript[:5000]}", "table_items": table_items,
            "raw_payload": {"meeting_details": meeting_details, "other_discussions": other_discussions}
        }
        client.table("meeting_archives").upsert(payload, on_conflict="meeting_id").execute()
        return True, "Successfully saved meeting to Supabase!"
    except Exception as e:
        return False, str(e)

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.txt'): return uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join([page.extract_text() for page in reader.pages])
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        return ""
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""

def _call_openai_transcribe(audio_bytes, filename="audio.mp3"):
    if not OPENAI_API_KEY: return None
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    files = {"file": (filename, audio_bytes), "model": (None, "gpt-4o-mini-transcribe"), "response_format": (None, "json")}
    try:
        resp = requests.post(OPENAI_AUDIO_URL, headers=headers, files=files, timeout=180)
        return resp.json().get("text", "") if resp.status_code == 200 else None
    except Exception: return None

def _call_groq_whisper(audio_bytes, filename="audio.mp3"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    files = {"file": (filename, audio_bytes), "model": (None, "whisper-large-v3-turbo"), "response_format": (None, "json")}
    try:
        resp = requests.post(GROQ_AUDIO_URL, headers=headers, files=files, timeout=60)
        return resp.json().get("text", "") if resp.status_code == 200 else None
    except Exception: return None

def transcribe_audio_pipeline(audio_bytes, original_filename, progress_bar, status_placeholder):
    progress_bar.progress(10, text="Preprocessing audio container (10%)...")
    ext = os.path.splitext(original_filename)[1] or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as src:
        src.write(audio_bytes)
        src_path = src.name
    compressed_mp3 = src_path + "_compressed.mp3"
    progress_bar.progress(25, text="Compressing audio to 16kHz Mono 24k MP3 (25%)...")
    try:
        res = subprocess.run(["ffmpeg", "-y", "-threads", "1", "-i", src_path, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "libmp3lame", "-b:a", "24k", compressed_mp3], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0: return None
        comp_size_mb = os.path.getsize(compressed_mp3) / (1024 * 1024)
        progress_bar.progress(45, text="Evaluating audio duration & routing (45%)...")
        if comp_size_mb <= 10.0 and GROQ_API_KEY:
            status_placeholder.info("Processing via Groq Whisper Primary...")
            progress_bar.progress(70, text="Transcribing via Groq Whisper (70%)...")
            with open(compressed_mp3, "rb") as f: text = _call_groq_whisper(f.read(), "audio.mp3")
            if text:
                progress_bar.progress(100, text="Transcription completed (100%)!")
                status_placeholder.empty()
                return text
        status_placeholder.info("Processing recording via OpenAI...")
        progress_bar.progress(55, text="Preparing audio segments for OpenAI (55%)...")
        segment_pattern = src_path + "_seg_%03d.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", compressed_mp3, "-f", "segment", "-segment_time", "600", "-c", "copy", segment_pattern], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        seg_dir = os.path.dirname(src_path)
        base_name = os.path.basename(src_path) + "_seg_"
        segments = sorted([os.path.join(seg_dir, f) for f in os.listdir(seg_dir) if f.startswith(base_name)])
        full_transcript = []
        for idx, seg in enumerate(segments):
            pct = int(55 + ((idx + 1) / len(segments)) * 40)
            progress_bar.progress(pct, text=f"Transcribing segment {idx + 1} of {len(segments)} ({pct}%)...")
            with open(seg, "rb") as f:
                t = _call_openai_transcribe(f.read(), f"part_{idx}.mp3")
                if t: full_transcript.append(t)
            time.sleep(0.2)
            try: os.remove(seg)
            except Exception: pass
        progress_bar.progress(100, text="Transcription completed successfully (100%)!")
        time.sleep(0.3)
        status_placeholder.empty()
        return " ".join(full_transcript)
    except Exception:
        return None
    finally:
        for path in [src_path, compressed_mp3]:
            if os.path.exists(path):
                try: os.remove(path)
                except Exception: pass

def normalize_llm_json_to_df(data):
    items, other_disc = None, ""
    if isinstance(data, list): items = data
    elif isinstance(data, dict):
        for key in ["table_items", "items", "minutes", "table", "data", "discussion_items", "discussions", "action_items"]:
            if key in data and isinstance(data[key], list) and len(data[key]) > 0:
                items = data[key]
                break
        if items is None:
            for v in data.values():
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                    items = v
                    break
            if items is None: items = [data]
        other_disc = str(data.get("other_discussions", "") or data.get("notes", "") or data.get("summary", ""))
    if not items or not isinstance(items, list): return None, ""
    df = pd.DataFrame(items)
    col_mapping = {}
    for c in df.columns:
        c_clean = str(c).lower().replace("_", " ").replace("-", " ")
        if any(k in c_clean for k in ["discuss", "point", "topic", "milestone"]): col_mapping[c] = "Discussion Points"
        elif any(k in c_clean for k in ["action", "plan", "step", "deliverable"]): col_mapping[c] = "Action Plan"
        elif any(k in c_clean for k in ["date", "time", "delivery", "deadline"]): col_mapping[c] = "Indicative Delivery Date"
        elif any(k in c_clean for k in ["person", "charge", "pic", "assign", "who", "responsible"]): col_mapping[c] = "Person-in-charge"
    df = df.rename(columns=col_mapping)
    for col in ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]:
        if col not in df.columns: df[col] = ""
    return df[["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]].drop_duplicates(), other_disc

def extract_metadata_with_deepseek(transcript):
    if not DEEPSEEK_API_KEY: return None
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    system_prompt = (
        "You are Echo, a highly meticulous and rigorous Executive AI Analyst for PRIME Philippines. "
        "Your objective is to extract exhaustive, precision-grade Minutes of the Meeting (MOM) from raw transcript data with zero hallucination. "
        f"Match all internal team attendees strictly against this verified list: {', '.join(CRD_MEMBERS)}. "
        "Infer meeting_type strictly as 'Internal', 'External', or 'Team'.\n\n"
        "STRICT EXTRACTION & FACTUAL INTEGRITY RULES:\n"
        "1. KNOWLEDGE BASE & CONTEXT AS SOURCE OF TRUTH: Cross-reference phonetic transcript errors, misheard terminology, and misspelled names against the provided Echo Knowledge Base context. Correct distorted proper nouns, acronyms, property identifiers, and proprietary team jargons (e.g., align phonetically transcribed names with verified team members and standardized terminology).\n"
        "2. GROUND TRUTH ONLY: Extract information exclusively supported by explicit transcript statements. NEVER assume, extrapolate, or fill in plausible details.\n"
        "3. ACTION PLANS & OWNERS: Pair every discussion point with its definitive, concrete next steps. If an action plan, delivery timeline, or person-in-charge is ambiguous, implicit, or unassigned, explicitly label it as 'Requires user validation / Check transcript' or 'Unassigned'—do NOT invent owners or target deadlines.\n"
        "4. DELIVERY TIMELINES: Record only verbatim dates or specific timeframes mentioned. Otherwise, explicitly state 'TBD (Confirm with transcript)'.\n"
        "5. DECISIONS MADE IN 'other_discussions': Consolidate all formal agreements, ratified proposals, approved budgets, and final consensus items under the 'other_discussions' field as a dedicated '### Decisions Made' section. Include unresolved items under '### Open Items'.\n"
        "6. TONE & SYNTAX: Convert colloquial Taglish/informal dialogue into polished, high-level corporate English while preserving exact technical specifications, figures, and property details.\n\n"
        "You must output ONLY a valid, parseable JSON object matching the requested schema without conversational commentary or code-block wrappers outside the JSON format. make sure to acknowledge additional prompt in the transcript added by the user for outlines and other discussion points"
    )
    user_prompt = f"""Extract metadata from this transcript into valid JSON:
Schema: {{"meeting_type": "Internal, External, or Team", "client_name": "Company/Client name or empty string", "location": "Meeting location preset or custom name or empty string", "crd_attendees": ["Exact matching names from CRD member list"], "external_attendees": "Comma-separated list of external attendee names", "prepared_by": "Name of attendee from PRIME taking notes or empty string", "confirmed_by": "Primary external attendee/client rep or empty string"}}
Transcript: {transcript[:15000]}"""
    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1, "max_tokens": 500}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=45)
        if resp.status_code == 200:
            raw_text = resp.json()["choices"][0]["message"]["content"].strip()
            clean_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
            clean_text = re.sub(r"\s*```$", "", clean_text).strip()
            return json.loads(clean_text)
    except Exception: pass
    return None

def extract_structured_insights(transcript, engine="AI - DeepSeek"):
    progress_bar = st.progress(0, text="Initializing MOM extraction (0%)...")
    time.sleep(0.2)
    progress_bar.progress(40, text=f"Translating Taglish conversation & extracting with {engine} (40%)...")
    if engine == "Non-AI - Python Heuristic":
        time.sleep(0.5)
        res_df, res_other = heuristic_non_ai_extraction(transcript)
        progress_bar.progress(100, text="Extraction completed (100%)!")
        time.sleep(0.2)
        progress_bar.empty()
        return res_df, res_other

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

    INSTRUCTION: Use this knowledge base to correct proper nouns, acronyms, and project names in the transcript. 
    If the transcript says 'Cool Berneties' but the Knowledge Base says 'Kubernetes', you MUST use 'Kubernetes'.
    """

    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    system_prompt = (
        "You are an expert executive assistant for PRIME Philippines tasked with producing comprehensive, high-level executive Minutes of the Meeting (MOM). "
        "The transcript contains Tagalog, English, and Taglish dialogue. "
        "Analyze the full conversation context and translate all colloquial, informal, and mixed-language statements into polished, high-level corporate English. "
        "Synthesize all key agreements, status reports, core discussion points, definitive action plans, indicative delivery timelines, and assigned persons-in-charge. "
        f"\n\n{context_string}\n"
        "Output valid JSON only matching the exact schema provided."
    )

    user_prompt = f"""Synthesize the following meeting transcript into formal, high-level Minutes of Meeting (MOM) formatted as valid JSON:
Schema: {{"table_items": [{{"Discussion Points": "Formal summary of key milestones, operational updates, or strategic topics discussed", "Action Plan": "Concrete, actionable executive deliverables and next steps (state 'None' if purely informational)", "Indicative Delivery Date": "Specific date, timeline, or 'TBD'", "Person-in-charge": "Designated individual, department (e.g., PRIME Philippines, Client name), or 'Unassigned'"}}], "other_discussions": "High-level summary of peripheral discussions, informal remarks, or general alignment"}}
Transcript: {transcript[:28000]}"""
    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1, "max_tokens": 1800}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            res_json = resp.json()
            st.session_state["tokens_used"] += res_json.get("usage", {}).get("total_tokens", len(transcript) // 4)
            st.session_state["last_api_call"] = datetime.datetime.now()
            raw_text = res_json["choices"][0]["message"]["content"].strip()
            clean_text = re.sub(r"^```(?:json)?\s*", "", raw_text).strip()
            clean_text = re.sub(r"\s*```$", "", clean_text).strip()
            match = re.search(r"\{.*\}", clean_text, re.DOTALL)
            data = json.loads(match.group(0)) if match else json.loads(clean_text)
            df, other = normalize_llm_json_to_df(data)
            progress_bar.progress(100, text="Finalizing Minutes of the Meeting (100%)...")
            time.sleep(0.3)
            progress_bar.empty()
            return df, other
    except Exception: pass
    df_fb, other_fb = heuristic_non_ai_extraction(transcript)
    progress_bar.empty()
    st.warning("AI completion request could not be completed. The table below was populated using offline Keyword Heuristics.")
    return df_fb, other_fb

def heuristic_non_ai_extraction(transcript):
    sentences = re.split(r'(?<=[.!?]) +', transcript)
    action_keywords = ['send', 'prepare', 'submit', 'update', 'review', 'check', 'email', 'kailangan', 'gagawin', 'ipapasa', 'provide', 'target', 'ipresent', 'kukunin']
    date_keywords = ['tomorrow', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'q1', 'q2', 'q3', 'q4', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'bukas', 'deadline']
    table_items, other_discussions = [], []
    for i in range(0, len(sentences), 3):
        chunk = sentences[i:i+3]
        if not chunk: continue
        chunk_text = " ".join(chunk)
        has_action = any(kw in chunk_text.lower() for kw in action_keywords)
        has_date = any(kw in chunk_text.lower() for kw in date_keywords)
        if has_action or has_date:
            action_text = " ".join([s for s in chunk if any(kw in s.lower() for kw in action_keywords)])
            table_items.append({"Discussion Points": chunk[0].strip() + "...", "Action Plan": action_text.strip() if action_text else "Review discussion for actions", "Indicative Delivery Date": "Check transcript (Date mentioned)" if has_date else "TBD", "Person-in-charge": "Unassigned"})
        else:
            other_discussions.append(chunk_text)
    if not table_items:
        table_items = [{"Discussion Points": "Meeting Overview", "Action Plan": "Please review transcript manually.", "Indicative Delivery Date": "TBD", "Person-in-charge": "Unassigned"}]
    df = pd.DataFrame(table_items[:10])
    for col in ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]:
        if col not in df.columns: df[col] = ""
    return df[["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]], "\n\n".join(other_discussions[:4])

def ask_deepseek_question(transcript, question, chat_history):
    if not DEEPSEEK_API_KEY: return "DeepSeek API key is missing. Please check your configuration."
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    system_prompt = "You are Ask Echo, an authentic, executive AI assistant for PRIME Philippines. Answer questions based accurately and concisely on the provided meeting transcript. Use subtle, clean Markdown with bullet points where appropriate. If a specific detail is not in the transcript, concisely state that it was not mentioned."
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]: messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": f"Transcript:\n{transcript[:22000]}\n\nQuestion: {question}"})
    payload = {"model": "deepseek-chat", "messages": messages, "temperature": 0.2, "max_tokens": 600}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            res_json = resp.json()
            st.session_state["tokens_used"] += res_json.get("usage", {}).get("total_tokens", 0)
            st.session_state["last_api_call"] = datetime.datetime.now()
            return res_json["choices"][0]["message"]["content"].strip()
        return f"Service notice ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Connection error: {e}"

def set_cell_shading(cell, color_hex):
    shd = parse_xml(f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

# -------------------------------------------------------------
# TEMPLATE 1: Standard Corporate (Combined Table)
# -------------------------------------------------------------
def export_to_word_template_1(df, meeting_details, other_discussions):
    template_files = ["MOM_Template.docx", "MOM Template.docx"]
    template_path = next((f for f in template_files if os.path.exists(f)), None)
    doc = Document(template_path) if template_path else Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("MINUTES OF THE MEETING")
    r_title.bold = True
    r_title.underline = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(11)

    company_target = meeting_details.get("external_attendees", [])
    primary_client_rep = company_target[0] if company_target else meeting_details.get("company_name", "").strip() or "CLIENT"
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run(f"PRIME PHILIPPINES & {primary_client_rep.upper()}")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)

    date_str = meeting_details.get("date", "____________")
    time_str = meeting_details.get("time_range", "")
    full_date = f"Date: {date_str}" + (f", {time_str}" if time_str.strip() else "")
    
    p_date = doc.add_paragraph(full_date)
    p_date.paragraph_format.space_after = Pt(2)
    for r in p_date.runs: r.font.name, r.font.size = "Arial", Pt(10)

    p_loc = doc.add_paragraph(f"Location: {meeting_details.get('location', '____________')}")
    p_loc.paragraph_format.space_after = Pt(2)
    for r in p_loc.runs: r.font.name, r.font.size = "Arial", Pt(10)

    prime_atts = meeting_details.get("prime_attendees", [])
    ext_atts = meeting_details.get("external_attendees", [])
    
    p_att = doc.add_paragraph()
    p_att.paragraph_format.space_after = Pt(2)
    p_att.paragraph_format.tab_stops.add_tab_stop(Inches(1.35), WD_TAB_ALIGNMENT.LEFT)
    r_att_label = p_att.add_run("Attended by:")
    r_att_label.font.name, r_att_label.font.size = "Arial", Pt(10)
    
    first_attendee = True
    for att in ext_atts:
        if not att.strip(): continue
        p = p_att if first_attendee else doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        if not first_attendee: p.paragraph_format.left_indent = Inches(1.35)
        else: p.add_run("\t")
        comp_label = f", {meeting_details.get('company_name')}" if meeting_details.get('company_name') else ""
        r = p.add_run(f"{att}{comp_label}")
        r.font.name, r.font.size = "Arial", Pt(10)
        first_attendee = False

    for att in prime_atts:
        p = p_att if first_attendee else doc.add_paragraph()
        p.paragraph_format.space_after = Pt(2)
        if not first_attendee: p.paragraph_format.left_indent = Inches(1.35)
        else: p.add_run("\t")
        r = p.add_run(f"{att} – PRIME Philippines")
        r.font.name, r.font.size = "Arial", Pt(10)
        first_attendee = False

    p_line = doc.add_paragraph()
    p_line.paragraph_format.space_before = Pt(4)
    p_line.paragraph_format.space_after = Pt(6)
    r_line = p_line.add_run("_________________________________________________________________________________")
    r_line.font.name, r_line.font.color.rgb = "Arial", RGBColor(160, 160, 160)

    client_display = meeting_details.get('company_name', '').strip() or "the Client"
    p_intro = doc.add_paragraph(f"During the meeting held last {date_str}, PRIME Philippines, represented by the attendee/s shown above, met with {client_display} to discuss opportunities for collaboration.")
    p_intro.paragraph_format.space_after = Pt(10)
    for r in p_intro.runs: r.font.name, r.font.size = "Arial", Pt(9.5)

    table = doc.add_table(rows=len(df)+1, cols=4)
    table.alignment, table.style, table.autofit, table.allow_autofit = WD_TABLE_ALIGNMENT.CENTER, "Table Grid", False, False
    col_widths = [Inches(2.5), Inches(2.2), Inches(1.1), Inches(1.2)]
    headers = ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]
    
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.width, cell.text = col_widths[i], header
        set_cell_shading(cell, "FFFF00")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.runs: p.runs[0].font.bold, p.runs[0].font.size, p.runs[0].font.name = True, Pt(9), "Arial"

    for i, row in df.iterrows():
        cells = table.rows[i+1].cells
        cells[0].text, cells[1].text, cells[2].text, cells[3].text = f"{i+1}. {str(row.get('Discussion Points', ''))}", str(row.get("Action Plan", "")), str(row.get("Indicative Delivery Date", "")), str(row.get("Person-in-charge", ""))
        for c_idx, cell in enumerate(cells):
            cell.width = col_widths[c_idx]
            p = cell.paragraphs[0]
            if c_idx in [2, 3]: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p.runs: p.runs[0].font.size, p.runs[0].font.name = Pt(8.5), "Arial"

    doc.add_paragraph()
    p_note = doc.add_paragraph("*Note: The indicative delivery date serves as reference point and still subject to changes. Furthermore, it depends on the progress of both parties.")
    p_note.paragraph_format.space_after = Pt(8)
    p_note.runs[0].italic, p_note.runs[0].font.name, p_note.runs[0].font.size = True, "Arial", Pt(8)

    if other_discussions.strip():
        p_od_head = doc.add_paragraph()
        p_od_head.paragraph_format.space_before, p_od_head.paragraph_format.space_after = Pt(6), Pt(4)
        r_od_head = p_od_head.add_run("Other Discussions:")
        r_od_head.bold, r_od_head.font.size, r_od_head.font.name = True, Pt(10), "Arial"
        p_od = doc.add_paragraph(other_discussions)
        p_od.paragraph_format.space_after = Pt(12)
        for r in p_od.runs: r.font.name, r.font.size = "Arial", Pt(9.5)

    p_prep_label = doc.add_paragraph("Prepared by:")
    p_prep_label.paragraph_format.space_before = Pt(12)
    p_prep_label.paragraph_format.space_after = Pt(2)
    p_prep_label.runs[0].font.name, p_prep_label.runs[0].font.bold, p_prep_label.runs[0].font.size = "Arial", True, Pt(9.5)
    p_prep_line = doc.add_paragraph("_______________________________")
    p_prep_line.paragraph_format.space_after = Pt(2)
    p_prep_line.runs[0].font.name = "Arial"
    prep_name = meeting_details.get("prep_name", "").strip() or "____________________"
    prep_desig = meeting_details.get("prep_desig", "").strip() or "PRIME Philippines"
    p_prep_info = doc.add_paragraph(f"{prep_name}\n{prep_desig}")
    p_prep_info.paragraph_format.space_after = Pt(12)
    for r in p_prep_info.runs: r.font.name, r.font.size = "Arial", Pt(9.5)

    p_conf_label = doc.add_paragraph("Confirmed by:")
    p_conf_label.paragraph_format.space_after = Pt(2)
    p_conf_label.runs[0].font.name, p_conf_label.runs[0].font.bold, p_conf_label.runs[0].font.size = "Arial", True, Pt(9.5)
    p_conf_line = doc.add_paragraph("_______________________________")
    p_conf_line.paragraph_format.space_after = Pt(2)
    p_conf_line.runs[0].font.name = "Arial"
    conf_name = meeting_details.get("conf_name", "").strip() or (ext_atts[0] if ext_atts else "____________________")
    conf_desig = meeting_details.get("conf_desig", "").strip() or (meeting_details.get("company_name", "").strip() or "Client")
    p_conf_info = doc.add_paragraph(f"{conf_name}\n{conf_desig}")
    p_conf_info.paragraph_format.space_after = Pt(6)
    for r in p_conf_info.runs: r.font.name, r.font.size = "Arial", Pt(9.5)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def export_to_pdf_template_1(df, meeting_details, other_discussions):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.6 * inch, rightMargin=0.6 * inch, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    story, styles = [], getSampleStyleSheet()
    
    style_title = ParagraphStyle('DocTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11.5, alignment=1, spaceAfter=2)
    company_target = meeting_details.get("external_attendees", [])
    primary_client_rep = company_target[0] if company_target else meeting_details.get("company_name", "").strip() or "CLIENT"
    style_subtitle = ParagraphStyle('DocSubTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10.5, alignment=1, spaceAfter=10)
    style_body = ParagraphStyle('DocBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, spaceAfter=3)
    style_th = ParagraphStyle('TableHead', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=10, alignment=1)
    style_td = ParagraphStyle('TableData', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
    style_td_center = ParagraphStyle('TableDataCenter', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=1)

    story.append(Paragraph("<u>MINUTES OF THE MEETING</u>", style_title))
    story.append(Paragraph(f"PRIME PHILIPPINES & {primary_client_rep.upper()}", style_subtitle))
    
    date_str, time_str = meeting_details.get("date", "____________"), meeting_details.get("time_range", "")
    full_date = f"<b>Date:</b> {date_str}" + (f", {time_str}" if time_str.strip() else "")
    story.append(Paragraph(full_date, style_body))
    story.append(Paragraph(f"<b>Location:</b> {meeting_details.get('location', '____________')}", style_body))
    
    prime_atts, ext_atts = meeting_details.get("prime_attendees", []), meeting_details.get("external_attendees", [])
    att_list = []
    for att in ext_atts:
        if att.strip(): att_list.append(f"{att}{f', {meeting_details.get('company_name')}' if meeting_details.get('company_name') else ''}")
    for att in prime_atts: att_list.append(f"{att} – PRIME Philippines")
    
    if att_list:
        story.append(Paragraph(f"<b>Attended by:</b>&nbsp;&nbsp;&nbsp;&nbsp;{att_list[0]}", style_body))
        for a in att_list[1:]: story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a}", style_body))
    
    story.append(Spacer(1, 4))
    client_display = meeting_details.get('company_name', '').strip() or "the Client"
    story.append(Paragraph(f"During the meeting held last {date_str}, PRIME Philippines, represented by the attendee/s shown above, met with {client_display} to discuss opportunities for collaboration.", style_body))
    story.append(Spacer(1, 6))
    
    table_data = [[Paragraph("<b>Discussion Points</b>", style_th), Paragraph("<b>Action Plan</b>", style_th), Paragraph("<b>Indicative Delivery Date</b>", style_th), Paragraph("<b>Person-in-charge</b>", style_th)]]
    for i, row in df.iterrows():
        table_data.append([
            Paragraph(f"{i+1}. {str(row.get('Discussion Points', ''))}", style_td),
            Paragraph(str(row.get("Action Plan", "")), style_td),
            Paragraph(str(row.get("Indicative Delivery Date", "")), style_td_center),
            Paragraph(str(row.get("Person-in-charge", "")), style_td_center)
        ])
    
    t = Table(table_data, colWidths=[2.4 * inch, 2.3 * inch, 1.1 * inch, 1.0 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFFF00')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(t)
    
    note_style = ParagraphStyle('Note', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=9, spaceBefore=4)
    story.append(Paragraph("*Note: The indicative delivery date serves as reference point and still subject to changes. Furthermore, it depends on the progress of both parties.", note_style))
    
    if other_discussions.strip():
        story.append(Spacer(1, 6))
        story.append(Paragraph("<b>Other Discussions:</b>", style_body))
        story.append(Paragraph(other_discussions, style_body))
    
    story.append(Spacer(1, 8))
    prep_name = meeting_details.get("prep_name", "").strip() or "____________________"
    prep_desig = meeting_details.get("prep_desig", "").strip() or "PRIME Philippines"
    conf_name = meeting_details.get("conf_name", "").strip() or (ext_atts[0] if ext_atts else "____________________")
    conf_desig = meeting_details.get("conf_desig", "").strip() or (meeting_details.get("company_name", "").strip() or "Client")
    
    sign_data = [
        [Paragraph("<b>Prepared by:</b>", style_body), Paragraph("<b>Confirmed by:</b>", style_body)],
        [Paragraph("_______________________________", style_body), Paragraph("_______________________________", style_body)],
        [Paragraph(f"{prep_name}<br/>{prep_desig}", style_body), Paragraph(f"{conf_name}<br/>{conf_desig}", style_body)]
    ]
    sign_table = Table(sign_data, colWidths=[3.4 * inch, 3.4 * inch])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2)
    ]))
    story.append(sign_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------------------------------------
# TEMPLATE 2: Detailed General Meeting (Vertical Layout)
# -------------------------------------------------------------
def export_to_word_template_2(df, meeting_details, other_discussions):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(2)
    r_title = p_title.add_run("MINUTES OF THE MEETING")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(16)
    
    company_target = meeting_details.get("external_attendees", [])
    primary_client_rep = company_target[0] if company_target else meeting_details.get("company_name", "").strip() or "General Meeting"
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(16)
    r_sub = p_sub.add_run(f"Project / Client: {primary_client_rep}")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(100, 100, 100)

    doc.add_heading('Meeting Details', level=2)
    details_table = doc.add_table(rows=5, cols=2)
    details_table.style = 'Table Grid'
    
    date_str = meeting_details.get("date", "____________")
    time_str = meeting_details.get("time_range", "____________")
    location_str = meeting_details.get('location', '____________')
    prep_name = meeting_details.get("prep_name", "").strip() or "____________________"
    
    details_map = [
        ("Date", date_str),
        ("Time", time_str),
        ("Venue", location_str),
        ("Prepared by", prep_name),
        ("Date prepared", datetime.now().strftime("%B %d, %Y"))
    ]
    
    for i, (key, val) in enumerate(details_map):
        cells = details_table.rows[i].cells
        cells[0].text = key
        cells[1].text = val
        cells[0].paragraphs[0].runs[0].font.bold = True
        for cell in cells:
            cell.paragraphs[0].runs[0].font.name = "Arial"
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)

    doc.add_paragraph()

    doc.add_heading('Attendees', level=2)
    all_atts = meeting_details.get("prime_attendees", []) + meeting_details.get("external_attendees", [])
    for att in all_atts:
        if att.strip():
            p_att = doc.add_paragraph(style='List Bullet')
            r_att = p_att.add_run(att.strip())
            r_att.font.name = "Arial"
            r_att.font.size = Pt(10)

    doc.add_paragraph()

    doc.add_heading('Purpose & Summary', level=2)
    p_purp = doc.add_paragraph(other_discussions if other_discussions.strip() else "To discuss project updates, ongoing deliverables, and establish clear action plans.")
    p_purp.paragraph_format.space_after = Pt(12)
    for r in p_purp.runs: r.font.name, r.font.size = "Arial", Pt(10)

    doc.add_heading('Discussion Points', level=2)
    for i, row in df.iterrows():
        p_dp = doc.add_paragraph(style='List Number')
        r_dp = p_dp.add_run(str(row.get('Discussion Points', '')))
        r_dp.font.name = "Arial"
        r_dp.font.size = Pt(10)

    doc.add_paragraph()

    doc.add_heading('Action Plan', level=2)
    act_table = doc.add_table(rows=len(df)+1, cols=4)
    act_table.style = 'Table Grid'
    act_headers = ["#", "Action Plan", "Owner", "Deadline"]
    col_widths = [Inches(0.5), Inches(3.5), Inches(1.5), Inches(1.5)]
    
    for i, header in enumerate(act_headers):
        cell = act_table.rows[0].cells[i]
        cell.width, cell.text = col_widths[i], header
        set_cell_shading(cell, "1A2B4C")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.runs: 
            p.runs[0].font.bold = True
            p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
            p.runs[0].font.size, p.runs[0].font.name = Pt(9), "Arial"

    for i, row in df.iterrows():
        cells = act_table.rows[i+1].cells
        cells[0].text, cells[1].text, cells[2].text, cells[3].text = str(i+1), str(row.get("Action Plan", "")), str(row.get("Person-in-charge", "")), str(row.get("Indicative Delivery Date", ""))
        for c_idx, cell in enumerate(cells):
            cell.width = col_widths[c_idx]
            p = cell.paragraphs[0]
            if c_idx in [0, 2, 3]: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if p.runs: p.runs[0].font.size, p.runs[0].font.name = Pt(9), "Arial"

    doc.add_paragraph()

    p_footer = doc.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_footer.paragraph_format.space_before = Pt(24)
    r_footer = p_footer.add_run(f"Prepared for circulation to {primary_client_rep}. Please return corrections before this is treated as the agreed record.")
    r_footer.italic = True
    r_footer.font.color.rgb = RGBColor(100, 100, 100)
    r_footer.font.name = "Arial"
    r_footer.font.size = Pt(8)

    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def export_to_pdf_template_2(df, meeting_details, other_discussions):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    story, styles = [], getSampleStyleSheet()
    
    style_title = ParagraphStyle('Title2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=15, alignment=1, spaceAfter=2)
    style_subtitle = ParagraphStyle('SubTitle2', parent=styles['Normal'], fontName='Helvetica', fontSize=10.5, textColor=colors.HexColor("#64748B"), alignment=1, spaceAfter=20)
    style_h2 = ParagraphStyle('Heading2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#1A2B4C"), spaceBefore=12, spaceAfter=6)
    style_body = ParagraphStyle('Body2', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=14, spaceAfter=4)
    style_th = ParagraphStyle('TH2', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white, alignment=1)
    style_td = ParagraphStyle('TD2', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12)
    style_td_center = ParagraphStyle('TDC2', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12, alignment=1)
    
    company_target = meeting_details.get("external_attendees", [])
    primary_client_rep = company_target[0] if company_target else meeting_details.get("company_name", "").strip() or "General Meeting"

    story.append(Paragraph("MINUTES OF THE MEETING", style_title))
    story.append(Paragraph(f"Project / Client: {primary_client_rep}", style_subtitle))
    
    story.append(Paragraph("Meeting Details", style_h2))
    date_str = meeting_details.get("date", "____________")
    time_str = meeting_details.get("time_range", "____________")
    location_str = meeting_details.get('location', '____________')
    prep_name = meeting_details.get("prep_name", "").strip() or "____________________"
    
    details_data = [
        [Paragraph("<b>Date</b>", style_body), Paragraph(date_str, style_body)],
        [Paragraph("<b>Time</b>", style_body), Paragraph(time_str, style_body)],
        [Paragraph("<b>Venue</b>", style_body), Paragraph(location_str, style_body)],
        [Paragraph("<b>Prepared by</b>", style_body), Paragraph(prep_name, style_body)],
        [Paragraph("<b>Date prepared</b>", style_body), Paragraph(datetime.now().strftime("%B %d, %Y"), style_body)]
    ]
    t_details = Table(details_data, colWidths=[2 * inch, 4.5 * inch])
    t_details.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(t_details)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Attendees", style_h2))
    all_atts = meeting_details.get("prime_attendees", []) + meeting_details.get("external_attendees", [])
    att_items = [ListItem(Paragraph(a.strip(), style_body)) for a in all_atts if a.strip()]
    if att_items:
        story.append(ListFlowable(att_items, bulletType='bullet'))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Purpose & Summary", style_h2))
    story.append(Paragraph(other_discussions if other_discussions.strip() else "To discuss project updates, ongoing deliverables, and establish clear action plans.", style_body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Discussion Points", style_h2))
    dp_items = [ListItem(Paragraph(str(row.get('Discussion Points', '')), style_body)) for _, row in df.iterrows()]
    if dp_items:
        story.append(ListFlowable(dp_items, bulletType='1'))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Action Plan", style_h2))
    act_data = [[Paragraph("<b>#</b>", style_th), Paragraph("<b>Action Plan</b>", style_th), Paragraph("<b>Owner</b>", style_th), Paragraph("<b>Deadline</b>", style_th)]]
    for i, row in df.iterrows():
        act_data.append([
            Paragraph(str(i+1), style_td_center),
            Paragraph(str(row.get("Action Plan", "")), style_td),
            Paragraph(str(row.get("Person-in-charge", "")), style_td_center),
            Paragraph(str(row.get("Indicative Delivery Date", "")), style_td_center)
        ])
    
    t_act = Table(act_data, colWidths=[0.4 * inch, 3.5 * inch, 1.3 * inch, 1.3 * inch], repeatRows=1)
    t_act.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A2B4C')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5)
    ]))
    story.append(t_act)

    story.append(Spacer(1, 24))
    footer_style = ParagraphStyle('Footer2', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.grey, alignment=1)
    story.append(Paragraph(f"Prepared for circulation to {primary_client_rep}. Please return corrections before this is treated as the agreed record.", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer

# 8. UI Layout
col_upload, col_details = st.columns(2)

# LEFT CONTAINER: Audio & Text Upload Section
with col_upload:
    with st.container(height=520, border=True):
        st.markdown('<h3>Input & Transcription</h3>', unsafe_allow_html=True)
        tab_upload, tab_record, tab_text = st.tabs(["Upload Audio", "Record Audio", "Upload Text"])
        with tab_upload:
            uploaded_file = st.file_uploader("Upload audio file (200MB limit supported)", type=["wav", "mp3", "m4a", "ogg", "flac", "mp4", "webm"], help="Audio uploads up to 200MB are supported.")
            if uploaded_file:
                st.write("")
                if st.button("Transcribe Audio", key="btn_tx_upload"):
                    p_bar = st.progress(0, text="Initializing audio pipeline (0%)...")
                    p_status = st.empty()
                    transcript = transcribe_audio_pipeline(uploaded_file.read(), uploaded_file.name, p_bar, p_status)
                    p_bar.empty()
                    p_status.empty()
                    if transcript:
                        st.session_state["transcript"] = transcript
                        st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
                        st.session_state["other_discussions"] = ""
                        st.session_state["chat_history"] = []
                        st.rerun()
        with tab_record:
            recorded_audio = st.audio_input("Record audio directly", label_visibility="collapsed")
            if recorded_audio:
                rec_bytes = recorded_audio.read()
                r_btn1, r_btn2 = st.columns(2)
                with r_btn1:
                    st.download_button(label="Save Recording (.wav)", data=rec_bytes, file_name=f"Recording_{datetime.date.today().strftime('%Y%m%d')}.wav", mime="audio/wav", use_container_width=True)
                with r_btn2:
                    if st.button("Transcribe Audio", key="btn_tx_record"):
                        p_bar = st.progress(0, text="Initializing audio pipeline (0%)...")
                        p_status = st.empty()
                        transcript = transcribe_audio_pipeline(rec_bytes, "recording.wav", p_bar, p_status)
                        p_bar.empty()
                        p_status.empty()
                        if transcript:
                            st.session_state["transcript"] = transcript
                            st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
                            st.session_state["other_discussions"] = ""
                            st.session_state["chat_history"] = []
                            st.rerun()
        with tab_text:
            uploaded_text_file = st.file_uploader("Upload Document (.txt, .docx, .pdf)", type=["txt", "docx", "pdf"])
            pasted_text = st.text_area("Or Paste Transcript Here", height=95, placeholder="Paste transcript text directly here...")
            if st.button("Process Text", key="btn_tx_text"):
                p_bar = st.progress(0, text="Extracting document text (0%)...")
                time.sleep(0.2)
                p_bar.progress(50, text="Reading document stream (50%)...")
                extracted_str = ""
                if uploaded_text_file: extracted_str = extract_text_from_file(uploaded_text_file)
                if pasted_text and pasted_text.strip(): extracted_str += "\n" + pasted_text.strip()
                p_bar.progress(100, text="Document processed (100%)!")
                time.sleep(0.2)
                p_bar.empty()
                if extracted_str.strip():
                    st.session_state["transcript"] = extracted_str.strip()
                    st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
                    st.session_state["other_discussions"] = ""
                    st.session_state["chat_history"] = []
                    st.rerun()
                else:
                    st.warning("Please upload a file or paste text to proceed.")

# RIGHT CONTAINER: Meeting Details Card
with col_details:
    with st.container(height=520, border=True):
        if st.session_state["transcript"]:
            head_col1, head_col_auto, head_col2 = st.columns([5.5, 3.5, 1.0])
            with head_col_auto:
                if st.button("Populate from Transcript", key="btn_auto_populate"):
                    with st.spinner("Extracting metadata..."):
                        meta = extract_metadata_with_deepseek(st.session_state["transcript"])
                        if meta:
                            if meta.get("meeting_type") and meta["meeting_type"] in MEETING_TYPE_OPTIONS:
                                st.session_state["meeting_type"] = meta["meeting_type"]
                            if meta.get("client_name"): st.session_state["meeting_client_name"] = meta["client_name"]
                            if meta.get("location"): st.session_state["meeting_location"] = meta["location"]
                            if meta.get("crd_attendees"):
                                matched_crd = [c for c in meta["crd_attendees"] if c in CRD_MEMBERS]
                                if matched_crd: st.session_state["meeting_selected_crd"] = matched_crd
                            if meta.get("external_attendees"): st.session_state["meeting_ext_attendees"] = meta["external_attendees"]
                            if meta.get("prepared_by"): st.session_state["meeting_prep_name"] = meta["prepared_by"]
                            if meta.get("confirmed_by"): st.session_state["meeting_conf_name"] = meta["confirmed_by"]
                            st.rerun()
        else:
            head_col1, head_col2 = st.columns([9.0, 1.0])
        with head_col1:
            st.markdown('<h3 style="margin-top:0.2rem;">Meeting Details</h3>', unsafe_allow_html=True)
        with head_col2:
            if st.button("", key="card_settings_btn", help="Settings"):
                st.session_state["show_settings"] = not st.session_state["show_settings"]
                st.rerun()
        if st.session_state["show_settings"]:
            with st.expander("Settings & Engine Diagnostics", expanded=True):
                set_col1, set_col2 = st.columns(2)
                with set_col1:
                    engine_options = ["AI - DeepSeek", "Non-AI - Python Heuristic"]
                    selected_eng = st.selectbox("MoM Generation Engine", options=engine_options, index=engine_options.index(st.session_state["selected_engine"]) if st.session_state["selected_engine"] in engine_options else 0)
                    st.session_state["selected_engine"] = selected_eng
                with set_col2:
                    st.markdown("**Diagnostics**")
                    st.write(f"• **Session Tokens:** `{st.session_state['tokens_used']:,}`")
                    if st.session_state["last_api_call"]:
                        last_call = st.session_state["last_api_call"]
                        st.write(f"• **Last Call:** `{last_call.strftime('%I:%M:%S %p')}`")
            st.markdown("---")
        
        # Row 1: Date, Location (Presets + Custom option), Meeting Type
        r1_c1, r1_c2, r1_c3 = st.columns([1.1, 1.4, 0.9])
        with r1_c1:
            meeting_date = st.date_input("Date", value=st.session_state["meeting_date"])
            st.session_state["meeting_date"] = meeting_date
        with r1_c2:
            current_loc = st.session_state.get("meeting_location", "")
            loc_options = list(LOCATION_PRESETS)
            
            if current_loc and current_loc not in loc_options:
                loc_options.append(current_loc)
            loc_options.append("Other / Custom...")

            default_idx = loc_options.index(current_loc) if current_loc in loc_options else 0
            selected_loc_choice = st.selectbox("Location", options=loc_options, index=default_idx)
            
            if selected_loc_choice == "Other / Custom...":
                custom_loc = st.text_input(
                    "Enter Location", 
                    value="" if current_loc in LOCATION_PRESETS else current_loc, 
                    placeholder="e.g. Boardroom or Client Office",
                    label_visibility="collapsed"
                )
                meeting_location = custom_loc
            else:
                meeting_location = selected_loc_choice
                
            st.session_state["meeting_location"] = meeting_location if meeting_location else ""
        with r1_c3:
            curr_type = st.session_state.get("meeting_type", "Internal")
            type_idx = MEETING_TYPE_OPTIONS.index(curr_type) if curr_type in MEETING_TYPE_OPTIONS else 0
            meeting_type = st.selectbox("Meeting Type", options=MEETING_TYPE_OPTIONS, index=type_idx)
            st.session_state["meeting_type"] = meeting_type

        # Row 2: Start and End Times
        r2_c1, r2_c2 = st.columns(2)
        with r2_c1:
            st.markdown("<p style='font-size:0.85rem; margin-bottom:0.2rem; color:#333; font-weight:500;'>Start Time</p>", unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns([1, 1, 1.2])
            sh = sc1.selectbox("SH", [f"{i:02d}" for i in range(1,13)], key="sh", label_visibility="collapsed")
            sm = sc2.selectbox("SM", [f"{i:02d}" for i in range(0,60,5)], key="sm", label_visibility="collapsed")
            sap = sc3.selectbox("SAP", ["AM", "PM"], key="sap", label_visibility="collapsed")
            start_str = f"{sh}:{sm} {sap}"
        with r2_c2:
            st.markdown("<p style='font-size:0.85rem; margin-bottom:0.2rem; color:#333; font-weight:500;'>End Time</p>", unsafe_allow_html=True)
            ec1, ec2, ec3 = st.columns([1, 1, 1.2])
            eh = ec1.selectbox("EH", [f"{i:02d}" for i in range(1,13)], key="eh", label_visibility="collapsed")
            em = ec2.selectbox("EM", [f"{i:02d}" for i in range(0,60,5)], key="em", label_visibility="collapsed")
            eap = ec3.selectbox("EAP", ["AM", "PM"], key="eap", label_visibility="collapsed")
            end_str = f"{eh}:{em} {eap}"
        
        # Row 3: Client, Attendees, Prepared & Confirmed details
        r3_c1, r3_c2 = st.columns(2)
        with r3_c1:
            client_name = st.text_input("Client / Company / Department", value=st.session_state["meeting_client_name"], placeholder="XYZ Company")
            st.session_state["meeting_client_name"] = client_name
            selected_crd = st.multiselect("CRD Team Attendees", options=CRD_MEMBERS, default=st.session_state["meeting_selected_crd"])
            st.session_state["meeting_selected_crd"] = selected_crd
        with r3_c2:
            ext_attendees_raw = st.text_input("External Attendees", value=st.session_state["meeting_ext_attendees"], placeholder="e.g. Mr. ABCD, Jane Doe")
            st.session_state["meeting_ext_attendees"] = ext_attendees_raw
            prep_col, conf_col = st.columns(2)
            with prep_col:
                prep_name = st.text_input("Prepared By", value=st.session_state["meeting_prep_name"], placeholder="Name")
                st.session_state["meeting_prep_name"] = prep_name
                prep_desig = st.text_input("Prep Designation", value=st.session_state["meeting_prep_desig"], placeholder="Designation")
                st.session_state["meeting_prep_desig"] = prep_desig
            with conf_col:
                conf_name = st.text_input("Confirmed By", value=st.session_state["meeting_conf_name"], placeholder="Name")
                st.session_state["meeting_conf_name"] = conf_name
                conf_desig = st.text_input("Conf Designation", value=st.session_state["meeting_conf_desig"], placeholder="Designation")
                st.session_state["meeting_conf_desig"] = conf_desig

# Step 2: Symmetrical Bottom Row (Full Transcript Left, Ask Echo Right)
if st.session_state["transcript"]:
    row_left, row_right = st.columns(2)
    with row_left:
        with st.container(height=580, border=True):
            st.markdown('<h3 style="margin-top:0.2rem;">Full Transcript</h3>', unsafe_allow_html=True)
            st.text_area("Transcript Content", st.session_state["transcript"], height=380, label_visibility="collapsed")
            st.markdown("<hr style='margin: 0.8rem 0; border-top: 1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
            t_col1, t_col2, t_col3 = st.columns(3)
            with t_col1:
                if st.button("Generate MOM", key="btn_gen_mom"):
                    extracted_df, other_disc = extract_structured_insights(st.session_state["transcript"], engine=st.session_state["selected_engine"])
                    if not extracted_df.empty:
                        st.session_state["df"] = extracted_df
                        st.session_state["other_discussions"] = other_disc
                        st.rerun()
            with t_col2:
                copy_html = f"""
                <!DOCTYPE html><html><head><style>body{{margin:0;padding:0;font-family:'Montserrat',sans-serif;}}button{{width:100%;height:36px;background-color:#222222;color:#FFFFFF;border:none;border-radius:50px;font-size:0.82rem;font-weight:500;cursor:pointer;transition:all 0.2s ease;box-shadow:0 4px 6px rgba(0,0,0,0.1);}}button:hover{{background-color:#D4AF37;box-shadow:0 6px 12px rgba(212,175,55,0.2);transform:translateY(-1px);}}</style></head><body><button id="copy-btn">{COPY_ICON} Copy Text</button><script>document.getElementById("copy-btn").addEventListener("click",function(){{navigator.clipboard.writeText({json.dumps(st.session_state["transcript"])}).then(function(){{document.getElementById("copy-btn").innerHTML = '{COPY_ICON} Copied';setTimeout(() => document.getElementById("copy-btn").innerHTML = '{COPY_ICON} Copy Text', 2000);}});}});</script></body></html>
                """
                components.html(copy_html, height=36)
            with t_col3:
                st.download_button(label="Download", data=st.session_state["transcript"], file_name=f"Transcript_{meeting_date.strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
    with row_right:
        with st.container(height=580, border=True):
            st.markdown('<h3 style="margin-top:0.2rem;">Ask Echo</h3>', unsafe_allow_html=True)
            st.caption("Ask specific questions regarding action items, timelines, deliverables, or remarks.")
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            if not st.session_state["chat_history"]:
                st.markdown('<div class="chat-ai">Hello. I am Echo. How may I assist you regarding this meeting transcript?</div>', unsafe_allow_html=True)
            else:
                for msg in st.session_state["chat_history"]:
                    if msg["role"] == "assistant":
                        st.markdown(f'<div class="chat-ai">{msg["content"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-user-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if prompt := st.chat_input("Ask Echo a question..."):
                st.session_state["chat_history"].append({"role": "user", "content": prompt})
                with st.spinner("Analyzing transcript..."):
                    answer = ask_deepseek_question(st.session_state["transcript"], prompt, st.session_state["chat_history"])
                st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                st.rerun()

# Step 3: Minutes of Meeting Editor (Bug-Free State Logic)
if not st.session_state["df"].empty:
    with st.container(border=True):
        st.markdown('<h3>Minutes of Meeting Editor</h3>', unsafe_allow_html=True)
        st.markdown("<p style='font-size:0.85rem; color:#666; margin-bottom: 0.75rem;'><i>*Note: Each discussion item is rendered as a clean card with auto-wrapping text boxes. Edit fields inline directly.</i></p>", unsafe_allow_html=True)
        
        editor_key = "mom_editor_rows"
        if editor_key not in st.session_state or st.session_state.get("_last_df_id") != id(st.session_state["df"]):
            st.session_state[editor_key] = st.session_state["df"].to_dict('records')
            st.session_state["_last_df_id"] = id(st.session_state["df"])
        
        rows = st.session_state[editor_key]
        rows_to_keep = []
        
        for idx, row in enumerate(rows):
            with st.container(border=True):
                c_disc, c_act, c_date, c_pic, c_del = st.columns([3.2, 3.2, 1.8, 1.8, 0.6])
                with c_disc:
                    st.markdown('<span class="playfair-label">Discussion Points</span>', unsafe_allow_html=True)
                    st.text_area("DP", value=str(row.get("Discussion Points", "")), key=f"dp_{idx}", height=75, label_visibility="collapsed")
                with c_act:
                    st.markdown('<span class="playfair-label">Action Plan</span>', unsafe_allow_html=True)
                    st.text_area("AP", value=str(row.get("Action Plan", "")), key=f"ap_{idx}", height=75, label_visibility="collapsed")
                with c_date:
                    st.markdown('<span class="playfair-label">Delivery Date</span>', unsafe_allow_html=True)
                    st.text_area("DD", value=str(row.get("Indicative Delivery Date", "")), key=f"date_{idx}", height=75, label_visibility="collapsed")
                with c_pic:
                    st.markdown('<span class="playfair-label">Person-in-charge</span>', unsafe_allow_html=True)
                    st.text_area("PIC", value=str(row.get("Person-in-charge", "")), key=f"pic_{idx}", height=75, label_visibility="collapsed")
                with c_del:
                    st.write("<div style='height: 38px;'></div>", unsafe_allow_html=True)
                    if st.button("Delete", key=f"del_{idx}"):
                        continue 
                
                rows_to_keep.append({
                    "Discussion Points": st.session_state[f"dp_{idx}"],
                    "Action Plan": st.session_state[f"ap_{idx}"],
                    "Indicative Delivery Date": st.session_state[f"date_{idx}"],
                    "Person-in-charge": st.session_state[f"pic_{idx}"]
                })
        
        if len(rows_to_keep) != len(rows):
            st.session_state[editor_key] = rows_to_keep
            st.session_state["df"] = pd.DataFrame(rows_to_keep, columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
            st.rerun()
        
        add_col, _ = st.columns([2, 8])
        with add_col:
            if st.button("+ Add Item", key="add_row"):
                rows_to_keep.append({"Discussion Points": "", "Action Plan": "", "Indicative Delivery Date": "", "Person-in-charge": ""})
                st.session_state[editor_key] = rows_to_keep
                st.session_state["df"] = pd.DataFrame(rows_to_keep, columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
                st.rerun()
        
        st.markdown('<span class="playfair-label" style="margin-top:0.75rem;">Other Discussions</span>', unsafe_allow_html=True)
        st.session_state["other_discussions"] = st.text_area("Other Discussions Content", value=st.session_state["other_discussions"], height=100, label_visibility="collapsed")

        time_range_str = f"{start_str} to {end_str}"
        meeting_details = {
            "date": meeting_date.strftime("%B %d, %Y"), "time_range": time_range_str,
            "meeting_type": st.session_state.get("meeting_type", "Internal"),
            "location": meeting_location if meeting_location.strip() else "____________",
            "company_name": client_name.strip() if client_name.strip() else "",
            "prime_attendees": selected_crd,
            "external_attendees": [x.strip() for x in ext_attendees_raw.split(",") if x.strip()],
            "prep_name": prep_name.strip(), "prep_desig": prep_desig.strip(),
            "conf_name": conf_name.strip(), "conf_desig": conf_desig.strip()
        }

        # Template Selection & Export Section
        st.markdown('<span class="playfair-label" style="margin-top:1.5rem;">Export Options</span>', unsafe_allow_html=True)
        template_selection = st.selectbox(
            "Select MoM Template Format",
            options=["Template 1 - Standard Corporate (Combined Table)", "Template 2 - Detailed General Meeting (Vertical Layout)"],
            label_visibility="collapsed"
        )

        exp_col1, exp_col2 = st.columns(2)
        if "Template 1" in template_selection:
            with exp_col1:
                doc_bio = export_to_word_template_1(st.session_state["df"], meeting_details, st.session_state["other_discussions"])
                st.download_button(label="Download Word Document (.docx)", data=doc_bio, file_name=f"MOM_{client_name.replace(' ', '_') if client_name else 'Report'}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_download_docx_1")
            with exp_col2:
                pdf_bio = export_to_pdf_template_1(st.session_state["df"], meeting_details, st.session_state["other_discussions"])
                st.download_button(label="Download PDF Document (.pdf)", data=pdf_bio, file_name=f"MOM_{client_name.replace(' ', '_') if client_name else 'Report'}.pdf", mime="application/pdf", key="btn_download_pdf_1")
        else:
            with exp_col1:
                doc_bio = export_to_word_template_2(st.session_state["df"], meeting_details, st.session_state["other_discussions"])
                st.download_button(label="Download Word Document (.docx)", data=doc_bio, file_name=f"MOM_Detailed_{client_name.replace(' ', '_') if client_name else 'Report'}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", key="btn_download_docx_2")
            with exp_col2:
                pdf_bio = export_to_pdf_template_2(st.session_state["df"], meeting_details, st.session_state["other_discussions"])
                st.download_button(label="Download PDF Document (.pdf)", data=pdf_bio, file_name=f"MOM_Detailed_{client_name.replace(' ', '_') if client_name else 'Report'}.pdf", mime="application/pdf", key="btn_download_pdf_2")

        st.write("")
        save_col1, save_col2 = st.columns([8, 2])
        with save_col2:
            if st.button("Save Meeting", key="btn_save_supabase_bottom"):
                success, msg = save_meeting_to_supabase(meeting_details, st.session_state["df"], st.session_state["other_discussions"], st.session_state["transcript"])
                if success:
                    st.success(msg)
                else:
                    st.error(f"Save failed: {msg}")
