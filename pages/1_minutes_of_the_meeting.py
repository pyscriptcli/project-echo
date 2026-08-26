import os
import sys

# 1. Path Resolution (Must be before custom imports)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
from navigation import render_global_navbar

# 2. Page Configuration (Must be the FIRST Streamlit command executed)
st.set_page_config(
    page_title="Project Echo - MoM Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="Expanded"
)

# 3. Global Navbar / Header
render_global_navbar("Project Echo &mdash; MoM Generator")

# 4. Standard Library & Third-Party Imports
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
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import requests
import streamlit.components.v1 as components
from supabase import Client, create_client

# Ensure root directory is on Python path for navbar import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) if "pages" in __file__ else os.path.abspath("."))
from navigation import render_global_navbar

# ========== CONFIG ==========
st.set_page_config(page_title="Project Echo - MoM Generator", layout="wide", initial_sidebar_state="collapsed")[cite: 4]

# --- PROGRAMMATIC LIGHT MODE & 200MB LIMIT ---
_config_dir = ".streamlit"
_config_file = os.path.join(_config_dir, "config.toml")
os.makedirs(_config_dir, exist_ok=True)
with open(_config_file, "w", encoding="utf-8") as f:
    f.write('[theme]\nbase="light"\n[server]\nmaxUploadSize = 200\n')[cite: 4]

# Render Shared Persistent Floating Navigation Rail & Topbar
render_global_navbar("Project Echo &mdash; MoM Generator")

# API Keys & Supabase Credentials
DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()[cite: 4]
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"[cite: 4]

GROQ_API_KEY = str(st.secrets.get("GROQ_API_KEY", "")).strip()[cite: 4]
GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"[cite: 4]

OPENAI_API_KEY = str(st.secrets.get("OPENAI_API_KEY", "")).strip()[cite: 4]
OPENAI_AUDIO_URL = "https://api.openai.com/v1/audio/transcriptions"[cite: 4]

SUPABASE_URL = str(st.secrets.get("SUPABASE_URL", "")).strip().rstrip("/")[cite: 4]
if SUPABASE_URL.endswith("/rest/v1"):[cite: 4]
    SUPABASE_URL = SUPABASE_URL[:-8][cite: 4]
SUPABASE_KEY = "".join(str(st.secrets.get("SUPABASE_KEY", "")).split())[cite: 4]

CRD_MEMBERS = [
    "Sondi Tuazon",
    "Kristina Balajadia",
    "Meliza Zapata",
    "Dykstra Pineda",
    "Cedtrix Rena",
    "Carlo Medina",
    "Dave Policarpio",
    "Irish Rima"
][cite: 4]

LOCATION_OPTIONS = [
    "GreatWork Mega Tower 32F - Secret Room",
    "GreatWork Mega Tower 32F - Small Meeting Room",
    "GreatWork Mega Tower 24F - Meeting Room",
    "GreatWork Mega Tower 32F - Board Room",
    "GreatWork Mega Tower 32F - Co-working",
    "Online Meeting"
][cite: 4]

# Initialize Session State Variables
if "transcript" not in st.session_state:[cite: 4]
    st.session_state["transcript"] = ""[cite: 4]
if "df" not in st.session_state:[cite: 4]
    st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])[cite: 4]
if "other_discussions" not in st.session_state:[cite: 4]
    st.session_state["other_discussions"] = ""[cite: 4]
if "show_settings" not in st.session_state:[cite: 4]
    st.session_state["show_settings"] = False[cite: 4]
if "tokens_used" not in st.session_state:[cite: 4]
    st.session_state["tokens_used"] = 0[cite: 4]
if "last_api_call" not in st.session_state:[cite: 4]
    st.session_state["last_api_call"] = None[cite: 4]
if "selected_engine" not in st.session_state:[cite: 4]
    st.session_state["selected_engine"] = "AI - DeepSeek"[cite: 4]
if "chat_history" not in st.session_state:[cite: 4]
    st.session_state["chat_history"] = [][cite: 4]

# State for Auto-Populated Meeting Details
if "meeting_date" not in st.session_state:[cite: 4]
    st.session_state["meeting_date"] = datetime.date(2026, 8, 25)[cite: 4]
if "meeting_location" not in st.session_state:[cite: 4]
    st.session_state["meeting_location"] = ""[cite: 4]
if "meeting_client_name" not in st.session_state:[cite: 4]
    st.session_state["meeting_client_name"] = ""[cite: 4]
if "meeting_selected_crd" not in st.session_state:[cite: 4]
    st.session_state["meeting_selected_crd"] = [][cite: 4]
if "meeting_ext_attendees" not in st.session_state:[cite: 4]
    st.session_state["meeting_ext_attendees"] = ""[cite: 4]
if "meeting_prep_name" not in st.session_state:[cite: 4]
    st.session_state["meeting_prep_name"] = ""[cite: 4]
if "meeting_prep_desig" not in st.session_state:[cite: 4]
    st.session_state["meeting_prep_desig"] = ""[cite: 4]
if "meeting_conf_name" not in st.session_state:[cite: 4]
    st.session_state["meeting_conf_name"] = ""[cite: 4]
if "meeting_conf_desig" not in st.session_state:[cite: 4]
    st.session_state["meeting_conf_desig"] = ""[cite: 4]

# ========== SVG ICONS ==========
SVG_ALERT = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>"""[cite: 4]

# ========== CORE LOGIC ==========
@st.cache_resource
def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:[cite: 4]
        return None[cite: 4]
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)[cite: 4]
    except Exception:
        return None[cite: 4]

def save_meeting_to_supabase(meeting_details, df, other_discussions, transcript):
    client = init_supabase()[cite: 4]
    if not client:[cite: 4]
        return False, "Supabase client uninitialized."[cite: 4]
    try:
        table_items = [][cite: 4]
        for _, row in df.iterrows():[cite: 4]
            table_items.append({
                "Discussion Points": str(row.get("Discussion Points", "")),
                "Action Plan": str(row.get("Action Plan", "")),
                "Indicative Delivery Date": str(row.get("Indicative Delivery Date", "")),
                "Person-in-charge": str(row.get("Person-in-charge", ""))
            })[cite: 4]
            
        meeting_id = f"MOM-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"[cite: 4]
        client_name = meeting_details.get("company_name", "Unknown Client")[cite: 4]
        meeting_date_str = datetime.datetime.now().strftime("%Y-%m-%d")[cite: 4]
        if meeting_details.get("date"):[cite: 4]
            try:
                meeting_date_str = datetime.datetime.strptime(meeting_details.get("date"), "%B %d, %Y").strftime("%Y-%m-%d")[cite: 4]
            except Exception:[cite: 4]
                pass[cite: 4]
        
        payload = {
            "meeting_id": meeting_id,
            "client_name": client_name,
            "meeting_date": meeting_date_str,
            "location": meeting_details.get("location", ""),
            "prepared_by": meeting_details.get("prep_name", ""),
            "confirmed_by": meeting_details.get("conf_name", ""),
            "summary_md": f"### Summary\n{other_discussions}",
            "transcript_md": f"### Transcript\n{transcript[:5000]}",
            "table_items": table_items,
            "raw_payload": {
                "meeting_details": meeting_details,
                "other_discussions": other_discussions
            }
        }[cite: 4]
        
        client.table("meeting_archives").upsert(payload, on_conflict="meeting_id").execute()[cite: 4]
        return True, "Successfully saved meeting to Supabase!"[cite: 4]
    except Exception as e:[cite: 4]
        return False, str(e)[cite: 4]

def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.txt'):[cite: 4]
            return uploaded_file.getvalue().decode("utf-8")[cite: 4]
        elif uploaded_file.name.endswith('.pdf'):[cite: 4]
            reader = PyPDF2.PdfReader(uploaded_file)[cite: 4]
            text = ""[cite: 4]
            for page in reader.pages:[cite: 4]
                text += page.extract_text() + "\n"[cite: 4]
            return text[cite: 4]
        elif uploaded_file.name.endswith('.docx'):[cite: 4]
            doc = Document(uploaded_file)[cite: 4]
            return "\n".join([para.text for para in doc.paragraphs])[cite: 4]
        return ""[cite: 4]
    except Exception as e:[cite: 4]
        st.error(f"Error reading file: {e}")[cite: 4]
        return ""[cite: 4]

def _call_openai_transcribe(audio_bytes, filename="audio.mp3"):
    if not OPENAI_API_KEY:[cite: 4]
        st.error("OpenAI API Key is missing. Please add it to your Streamlit Cloud Secrets.")[cite: 4]
        return None[cite: 4]
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}[cite: 4]
    files = {"file": (filename, audio_bytes), "model": (None, "gpt-4o-mini-transcribe"), "response_format": (None, "json")}[cite: 4]
    try:
        resp = requests.post(OPENAI_AUDIO_URL, headers=headers, files=files, timeout=180)[cite: 4]
        if resp.status_code == 200:[cite: 4]
            return resp.json().get("text", "")[cite: 4]
        return None[cite: 4]
    except Exception:[cite: 4]
        return None[cite: 4]

def _call_groq_whisper(audio_bytes, filename="audio.mp3"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}[cite: 4]
    files = {"file": (filename, audio_bytes), "model": (None, "whisper-large-v3-turbo"), "response_format": (None, "json")}[cite: 4]
    try:
        resp = requests.post(GROQ_AUDIO_URL, headers=headers, files=files, timeout=60)[cite: 4]
        if resp.status_code == 200:[cite: 4]
            return resp.json().get("text", "")[cite: 4]
        return None[cite: 4]
    except Exception:[cite: 4]
        return None[cite: 4]

def transcribe_audio_pipeline(audio_bytes, original_filename, progress_bar, status_placeholder):
    progress_bar.progress(10, text="Preprocessing audio container (10%)...")[cite: 4]
    
    ext = os.path.splitext(original_filename)[1] or ".m4a"[cite: 4]
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as src:[cite: 4]
        src.write(audio_bytes)[cite: 4]
        src_path = src.name[cite: 4]

    compressed_mp3 = src_path + "_compressed.mp3"[cite: 4]
    progress_bar.progress(25, text="Compressing audio to 16kHz Mono 24k MP3 (25%)...")[cite: 4]

    try:
        cmd = [
            "ffmpeg", "-y", "-threads", "1", "-i", src_path, "-vn", "-ac", "1",
            "-ar", "16000", "-c:a", "libmp3lame", "-b:a", "24k", compressed_mp3
        ][cite: 4]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)[cite: 4]
        if res.returncode != 0:[cite: 4]
            return None[cite: 4]

        comp_size_mb = os.path.getsize(compressed_mp3) / (1024 * 1024)[cite: 4]
        progress_bar.progress(45, text="Evaluating audio duration & routing (45%)...")[cite: 4]

        if comp_size_mb <= 10.0 and GROQ_API_KEY:[cite: 4]
            status_placeholder.info("Processing via Groq Whisper Primary...")[cite: 4]
            progress_bar.progress(70, text="Transcribing via Groq Whisper (70%)...")[cite: 4]
            with open(compressed_mp3, "rb") as f:[cite: 4]
                c_bytes = f.read()[cite: 4]
            text = _call_groq_whisper(c_bytes, "audio.mp3")[cite: 4]
            if text:[cite: 4]
                progress_bar.progress(100, text="Transcription completed (100%)!")[cite: 4]
                status_placeholder.empty()[cite: 4]
                return text[cite: 4]

        status_placeholder.info("Processing recording via OpenAI...")[cite: 4]
        progress_bar.progress(55, text="Preparing audio segments for OpenAI (55%)...")[cite: 4]
        
        segment_pattern = src_path + "_seg_%03d.mp3"[cite: 4]
        subprocess.run([
            "ffmpeg", "-y", "-i", compressed_mp3, "-f", "segment", "-segment_time", "600", "-c", "copy", segment_pattern
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)[cite: 4]

        seg_dir = os.path.dirname(src_path)[cite: 4]
        base_name = os.path.basename(src_path) + "_seg_"[cite: 4]
        segments = sorted([os.path.join(seg_dir, f) for f in os.listdir(seg_dir) if f.startswith(base_name)])[cite: 4]

        full_transcript = [][cite: 4]
        total_segs = len(segments)[cite: 4]

        for idx, seg in enumerate(segments):[cite: 4]
            pct = int(55 + ((idx + 1) / total_segs) * 40)[cite: 4]
            progress_bar.progress(pct, text=f"Transcribing segment {idx + 1} of {total_segs} ({pct}%)...")[cite: 4]
            
            with open(seg, "rb") as f:[cite: 4]
                seg_bytes = f.read()[cite: 4]
            t = _call_openai_transcribe(seg_bytes, f"part_{idx}.mp3")[cite: 4]
            if t:[cite: 4]
                full_transcript.append(t)[cite: 4]
            time.sleep(0.2)[cite: 4]
            try: os.remove(seg)[cite: 4]
            except Exception: pass[cite: 4]

        progress_bar.progress(100, text="Transcription completed successfully (100%)!")[cite: 4]
        time.sleep(0.3)[cite: 4]
        status_placeholder.empty()[cite: 4]
        return " ".join(full_transcript)[cite: 4]

    except Exception:[cite: 4]
        return None[cite: 4]
    finally:
        if os.path.exists(src_path):[cite: 4]
            try: os.remove(src_path)[cite: 4]
            except Exception: pass[cite: 4]
        if os.path.exists(compressed_mp3):[cite: 4]
            try: os.remove(compressed_mp3)[cite: 4]
            except Exception: pass[cite: 4]

def normalize_llm_json_to_df(data):
    items = None[cite: 4]
    other_disc = ""[cite: 4]
    
    if isinstance(data, list):[cite: 4]
        items = data[cite: 4]
    elif isinstance(data, dict):[cite: 4]
        for key in ["table_items", "items", "minutes", "table", "data", "discussion_items", "discussions", "action_items"]:[cite: 4]
            if key in data and isinstance(data[key], list) and len(data[key]) > 0:[cite: 4]
                items = data[key][cite: 4]
                break[cite: 4]
        if items is None:[cite: 4]
            for v in data.values():[cite: 4]
                if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):[cite: 4]
                    items = v[cite: 4]
                    break[cite: 4]
            if items is None:[cite: 4]
                items = [data][cite: 4]
                
        other_disc = str(data.get("other_discussions", "") or data.get("notes", "") or data.get("summary", ""))[cite: 4]

    if not items or not isinstance(items, list):[cite: 4]
        return None, ""[cite: 4]

    df = pd.DataFrame(items)[cite: 4]
    col_mapping = {}[cite: 4]
    for c in df.columns:[cite: 4]
        c_clean = str(c).lower().replace("_", " ").replace("-", " ")[cite: 4]
        if any(k in c_clean for k in ["discuss", "point", "topic", "milestone"]):[cite: 4]
            col_mapping[c] = "Discussion Points"[cite: 4]
        elif any(k in c_clean for k in ["action", "plan", "step", "deliverable"]):[cite: 4]
            col_mapping[c] = "Action Plan"[cite: 4]
        elif any(k in c_clean for k in ["date", "time", "delivery", "deadline"]):[cite: 4]
            col_mapping[c] = "Indicative Delivery Date"[cite: 4]
        elif any(k in c_clean for k in ["person", "charge", "pic", "assign", "who", "responsible"]):[cite: 4]
            col_mapping[c] = "Person-in-charge"[cite: 4]

    df = df.rename(columns=col_mapping)[cite: 4]
    for col in ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]:[cite: 4]
        if col not in df.columns:[cite: 4]
            df[col] = ""[cite: 4]
            
    df = df[["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]].drop_duplicates()[cite: 4]
    return df, other_disc[cite: 4]

def extract_metadata_with_deepseek(transcript):
    if not DEEPSEEK_API_KEY:[cite: 4]
        st.error("DeepSeek API Key is missing.")[cite: 4]
        return None[cite: 4]

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }[cite: 4]

    system_prompt = (
        "You are an AI assistant for PRIME Philippines. Analyze the meeting transcript "
        "and extract the meeting metadata. Match CRD team attendees strictly to this list: "
        f"{', '.join(CRD_MEMBERS)}. "
        "Output ONLY a valid JSON object matching the schema."
    )[cite: 4]

    user_prompt = f"""Extract metadata from this transcript into valid JSON:
Schema:
{{
  "client_name": "Company/Client name or empty string",
  "location": "Meeting location preset or custom name or empty string",
  "crd_attendees": ["Exact matching names from CRD member list"],
  "external_attendees": "Comma-separated list of external attendee names",
  "prepared_by": "Name of attendee from PRIME taking notes or empty string",
  "confirmed_by": "Primary external attendee/client rep or empty string"
}}

Transcript:
{transcript[:15000]}"""[cite: 4]

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 500
    }[cite: 4]

    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=45)[cite: 4]
        if resp.status_code == 200:[cite: 4]
            res_json = resp.json()[cite: 4]
            raw_text = res_json["choices"][0]["message"]["content"].strip()[cite: 4]
            clean_text = re.sub(r"^```(?:json)?\s*", "", raw_text)[cite: 4]
            clean_text = re.sub(r"\s*```$", "", clean_text).strip()[cite: 4]
            return json.loads(clean_text)[cite: 4]
    except Exception:[cite: 4]
        pass[cite: 4]
    return None[cite: 4]

def extract_structured_insights(transcript, engine="AI - DeepSeek"):
    progress_bar = st.progress(0, text="Initializing MOM extraction (0%)...")[cite: 4]
    time.sleep(0.2)[cite: 4]
    progress_bar.progress(40, text=f"Translating Taglish conversation & extracting with {engine} (40%)...")[cite: 4]

    if engine == "Non-AI - Python Heuristic":[cite: 4]
        time.sleep(0.5)[cite: 4]
        res_df, res_other = heuristic_non_ai_extraction(transcript)[cite: 4]
        progress_bar.progress(100, text="Extraction completed (100%)!")[cite: 4]
        time.sleep(0.2)[cite: 4]
        progress_bar.empty()[cite: 4]
        return res_df, res_other[cite: 4]

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }[cite: 4]

    system_prompt = (
        "You are an expert executive assistant for PRIME Philippines tasked with producing comprehensive, "
        "high-level executive Minutes of the Meeting (MOM). "
        "The transcript contains Tagalog, English, and Taglish dialogue. "
        "Analyze the full conversation context and translate all colloquial, informal, and mixed-language statements "
        "into polished, high-level corporate English. "
        "Synthesize all key agreements, status reports, core discussion points, definitive action plans, "
        "indicative delivery timelines, and assigned persons-in-charge without omitting critical business context. "
        "Output valid JSON only matching the exact schema provided."
    )[cite: 4]

    user_prompt = f"""Synthesize the following meeting transcript into formal, high-level Minutes of Meeting (MOM) formatted as valid JSON:

Schema:
{{
  "table_items": [
    {{
      "Discussion Points": "Formal summary of key milestones, operational updates, or strategic topics discussed",
      "Action Plan": "Concrete, actionable executive deliverables and next steps (state 'None' if purely informational)",
      "Indicative Delivery Date": "Specific date, timeline, or 'TBD'",
      "Person-in-charge": "Designated individual, department (e.g., PRIME Philippines, Client name), or 'Unassigned'"
    }}
  ],
  "other_discussions": "High-level summary of peripheral discussions, informal remarks, or general alignment"
}}

Transcript:
{transcript[:28000]}"""[cite: 4]

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": 1800
    }[cite: 4]

    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=120)[cite: 4]
        if resp.status_code == 200:[cite: 4]
            res_json = resp.json()[cite: 4]
            st.session_state["tokens_used"] += res_json.get("usage", {}).get("total_tokens", len(transcript) // 4)[cite: 4]
            st.session_state["last_api_call"] = datetime.datetime.now()[cite: 4]
            raw_text = res_json["choices"][0]["message"]["content"].strip()[cite: 4]
            clean_text = re.sub(r"^```(?:json)?\s*", "", raw_text)[cite: 4]
            clean_text = re.sub(r"\s*```$", "", clean_text).strip()[cite: 4]
            match = re.search(r"\{.*\}", clean_text, re.DOTALL)[cite: 4]
            data = json.loads(match.group(0)) if match else json.loads(clean_text)[cite: 4]
            df, other = normalize_llm_json_to_df(data)[cite: 4]
            progress_bar.progress(100, text="Finalizing Minutes of the Meeting (100%)...")[cite: 4]
            time.sleep(0.3)[cite: 4]
            progress_bar.empty()[cite: 4]
            return df, other[cite: 4]
    except Exception:[cite: 4]
        pass[cite: 4]

    df_fb, other_fb = heuristic_non_ai_extraction(transcript)[cite: 4]
    progress_bar.empty()[cite: 4]
    st.markdown(f"{SVG_ALERT} AI completion request could not be completed. The table below was populated using offline Keyword Heuristics.", unsafe_allow_html=True)[cite: 4]
    return df_fb, other_fb[cite: 4]

def heuristic_non_ai_extraction(transcript):
    sentences = re.split(r'(?<=[.!?]) +', transcript)[cite: 4]
    action_keywords = ['send', 'prepare', 'submit', 'update', 'review', 'check', 'email', 'kailangan', 'gagawin', 'ipapasa', 'provide', 'target', 'ipresent', 'kukunin'][cite: 4]
    date_keywords = ['tomorrow', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'q1', 'q2', 'q3', 'q4', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'bukas', 'deadline'][cite: 4]
    
    table_items = [][cite: 4]
    other_discussions = [][cite: 4]
    
    for i in range(0, len(sentences), 3):[cite: 4]
        chunk = sentences[i:i+3][cite: 4]
        if not chunk:[cite: 4]
            continue[cite: 4]
        chunk_text = " ".join(chunk)[cite: 4]
        
        has_action = any(kw in chunk_text.lower() for kw in action_keywords)[cite: 4]
        has_date = any(kw in chunk_text.lower() for kw in date_keywords)[cite: 4]
        
        if has_action or has_date:[cite: 4]
            action_text = " ".join([s for s in chunk if any(kw in s.lower() for kw in action_keywords)])[cite: 4]
            table_items.append({
                "Discussion Points": chunk[0].strip() + "...",
                "Action Plan": action_text.strip() if action_text else "Review discussion for actions",
                "Indicative Delivery Date": "Check transcript (Date mentioned)" if has_date else "TBD",
                "Person-in-charge": "Unassigned"
            })[cite: 4]
        else:
            other_discussions.append(chunk_text)[cite: 4]
            
    if not table_items:[cite: 4]
        table_items = [{
            "Discussion Points": "Meeting Overview",
            "Action Plan": "Please review transcript manually.",
            "Indicative Delivery Date": "TBD",
            "Person-in-charge": "Unassigned"
        }][cite: 4]
        
    df = pd.DataFrame(table_items[:10])[cite: 4]
    for col in ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]:[cite: 4]
        if col not in df.columns:[cite: 4]
            df[col] = ""[cite: 4]
            
    df = df[["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"]][cite: 4]
    other_text = "\n\n".join(other_discussions[:4])[cite: 4]
    return df, other_text[cite: 4]

def ask_deepseek_question(transcript, question, chat_history):
    if not DEEPSEEK_API_KEY:[cite: 4]
        return "DeepSeek API key is missing. Please check your configuration."[cite: 4]

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }[cite: 4]

    system_prompt = (
        "You are Ask Echo, an authentic, executive AI assistant for PRIME Philippines. "
        "Answer questions based accurately and concisely on the provided meeting transcript. "
        "Use subtle, clean Markdown with bullet points where appropriate. "
        "If a specific detail is not in the transcript, concisely state that it was not mentioned."
    )[cite: 4]

    messages = [{"role": "system", "content": system_prompt}][cite: 4]
    for msg in chat_history[-6:]:[cite: 4]
        messages.append({"role": msg["role"], "content": msg["content"]})[cite: 4]
    messages.append({"role": "user", "content": f"Transcript:\n{transcript[:22000]}\n\nQuestion: {question}"})[cite: 4]

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 600
    }[cite: 4]

    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=60)[cite: 4]
        if resp.status_code == 200:[cite: 4]
            res_json = resp.json()[cite: 4]
            st.session_state["tokens_used"] += res_json.get("usage", {}).get("total_tokens", 0)[cite: 4]
            st.session_state["last_api_call"] = datetime.datetime.now()[cite: 4]
            return res_json["choices"][0]["message"]["content"].strip()[cite: 4]
        else:
            return f"Service notice ({resp.status_code}): {resp.text}"[cite: 4]
    except Exception as e:[cite: 4]
        return f"Connection error: {e}"[cite: 4]

def set_cell_shading(cell, color_hex):
    shd = parse_xml(f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="{color_hex}"/>')[cite: 4]
    cell._tc.get_or_add_tcPr().append(shd)[cite: 4]

def export_to_word(df, meeting_details, other_discussions):
    template_files = ["MOM_Template.docx", "MOM Template.docx"][cite: 4]
    template_path = next((f for f in template_files if os.path.exists(f)), None)[cite: 4]

    if template_path:[cite: 4]
        doc = Document(template_path)[cite: 4]
    else:
        doc = Document()[cite: 4]

    for section in doc.sections:[cite: 4]
        section.top_margin = Inches(0.4)[cite: 4]
        section.bottom_margin = Inches(0.4)[cite: 4]
        section.left_margin = Inches(0.75)[cite: 4]
        section.right_margin = Inches(0.75)[cite: 4]

    p_title = doc.add_paragraph()[cite: 4]
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER[cite: 4]
    p_title.paragraph_format.space_before = Pt(0)[cite: 4]
    p_title.paragraph_format.space_after = Pt(2)[cite: 4]
    r_title = p_title.add_run("MINUTES OF THE MEETING")[cite: 4]
    r_title.bold = True[cite: 4]
    r_title.underline = True[cite: 4]
    r_title.font.name = "Arial"[cite: 4]
    r_title.font.size = Pt(11)[cite: 4]

    company_target = meeting_details.get("external_attendees", [])[cite: 4]
    primary_client_rep = company_target[0] if company_target else meeting_details.get("company_name", "").strip() or "CLIENT"[cite: 4]
    p_sub = doc.add_paragraph()[cite: 4]
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER[cite: 4]
    p_sub.paragraph_format.space_after = Pt(12)[cite: 4]
    r_sub = p_sub.add_run(f"PRIME PHILIPPINES & {primary_client_rep.upper()}")[cite: 4]
    r_sub.bold = True[cite: 4]
    r_sub.font.name = "Arial"[cite: 4]
    r_sub.font.size = Pt(11)[cite: 4]

    date_str = meeting_details.get("date", "____________")[cite: 4]
    time_str = meeting_details.get("time_range", "")[cite: 4]
    full_date = f"Date: {date_str}" + (f", {time_str}" if time_str.strip() else "")[cite: 4]
    
    p_date = doc.add_paragraph(full_date)[cite: 4]
    p_date.paragraph_format.space_after = Pt(2)[cite: 4]
    for r in p_date.runs:[cite: 4]
        r.font.name = "Arial"[cite: 4]
        r.font.size = Pt(10)[cite: 4]

    p_loc = doc.add_paragraph(f"Location: {meeting_details.get('location', '____________')}")[cite: 4]
    p_loc.paragraph_format.space_after = Pt(2)[cite: 4]
    for r in p_loc.runs:[cite: 4]
        r.font.name = "Arial"[cite: 4]
        r.font.size = Pt(10)[cite: 4]

    prime_atts = meeting_details.get("prime_attendees", [])[cite: 4]
    ext_atts = meeting_details.get("external_attendees", [])[cite: 4]
    
    p_att = doc.add_paragraph()[cite: 4]
    p_att.paragraph_format.space_after = Pt(2)[cite: 4]
    p_att.paragraph_format.tab_stops.add_tab_stop(Inches(1.35), WD_TAB_ALIGNMENT.LEFT)[cite: 4]
    r_att_label = p_att.add_run("Attended by:")[cite: 4]
    r_att_label.font.name = "Arial"[cite: 4]
    r_att_label.font.size = Pt(10)[cite: 4]
    
    first_attendee = True[cite: 4]
    if ext_atts:[cite: 4]
        for att in ext_atts:[cite: 4]
            if not att.strip():[cite: 4]
                continue[cite: 4]
            p = p_att if first_attendee else doc.add_paragraph()[cite: 4]
            p.paragraph_format.space_after = Pt(2)[cite: 4]
            if not first_attendee:[cite: 4]
                p.paragraph_format.left_indent = Inches(1.35)[cite: 4]
            else:
                p.add_run("\t")[cite: 4]
            comp_label = f", {meeting_details.get('company_name')}" if meeting_details.get('company_name') else ""[cite: 4]
            r = p.add_run(f"{att}{comp_label}")[cite: 4]
            r.font.name = "Arial"[cite: 4]
            r.font.size = Pt(10)[cite: 4]
            first_attendee = False[cite: 4]

    if prime_atts:[cite: 4]
        for att in prime_atts:[cite: 4]
            p = p_att if first_attendee else doc.add_paragraph()[cite: 4]
            p.paragraph_format.space_after = Pt(2)[cite: 4]
            if not first_attendee:[cite: 4]
                p.paragraph_format.left_indent = Inches(1.35)[cite: 4]
            else:
                p.add_run("\t")[cite: 4]
            r = p.add_run(f"{att} – PRIME Philippines")[cite: 4]
            r.font.name = "Arial"[cite: 4]
            r.font.size = Pt(10)[cite: 4]
            first_attendee = False[cite: 4]

    p_line = doc.add_paragraph()[cite: 4]
    p_line.paragraph_format.space_before = Pt(4)[cite: 4]
    p_line.paragraph_format.space_after = Pt(6)[cite: 4]
    r_line = p_line.add_run("_________________________________________________________________________________")[cite: 4]
    r_line.font.name = "Arial"[cite: 4]
    r_line.font.color.rgb = RGBColor(160, 160, 160)[cite: 4]

    client_display = meeting_details.get('company_name', '').strip() or "the Client"[cite: 4]
    p_intro = doc.add_paragraph(
        f"During the meeting held last {date_str}, PRIME Philippines, represented by the attendee/s shown above, "
        f"met with {client_display} to discuss opportunities for collaboration."
    )[cite: 4]
    p_intro.paragraph_format.space_after = Pt(10)[cite: 4]
    for r in p_intro.runs:[cite: 4]
        r.font.name = "Arial"[cite: 4]
        r.font.size = Pt(9.5)[cite: 4]

    table = doc.add_table(rows=len(df)+1, cols=4)[cite: 4]
    table.alignment = WD_TABLE_ALIGNMENT.CENTER[cite: 4]
    table.style = "Table Grid"[cite: 4]
    table.autofit = False[cite: 4]
    table.allow_autofit = False[cite: 4]

    col_widths = [Inches(2.5), Inches(2.2), Inches(1.1), Inches(1.2)][cite: 4]

    headers = ["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"][cite: 4]
    for i, header in enumerate(headers):[cite: 4]
        cell = table.rows[0].cells[i][cite: 4]
        cell.width = col_widths[i][cite: 4]
        cell.text = header[cite: 4]
        set_cell_shading(cell, "FFFF00")[cite: 4]
        p = cell.paragraphs[0][cite: 4]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER[cite: 4]
        if p.runs:[cite: 4]
            p.runs[0].font.bold = True[cite: 4]
            p.runs[0].font.size = Pt(9)[cite: 4]
            p.runs[0].font.name = "Arial"[cite: 4]

    for i, row in df.iterrows():[cite: 4]
        cells = table.rows[i+1].cells[cite: 4]
        cells[0].text = f"{i+1}. {str(row.get('Discussion Points', ''))}"[cite: 4]
        cells[1].text = str(row.get("Action Plan", ""))[cite: 4]
        cells[2].text = str(row.get("Indicative Delivery Date", ""))[cite: 4]
        cells[3].text = str(row.get("Person-in-charge", ""))[cite: 4]
        for c_idx, cell in enumerate(cells):[cite: 4]
            cell.width = col_widths[c_idx][cite: 4]
            p = cell.paragraphs[0][cite: 4]
            if c_idx in [2, 3]:[cite: 4]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER[cite: 4]
            if p.runs:[cite: 4]
                p.runs[0].font.size = Pt(8.5)[cite: 4]
                p.runs[0].font.name = "Arial"[cite: 4]

    doc.add_paragraph()[cite: 4]
    p_note = doc.add_paragraph("*Note: The indicative delivery date serves as reference point and still subject to changes. Furthermore, it depends on the progress of both parties.")[cite: 4]
    p_note.paragraph_format.space_after = Pt(8)[cite: 4]
    p_note.runs[0].font.italic = True[cite: 4]
    p_note.runs[0].font.name = "Arial"[cite: 4]
    p_note.runs[0].font.size = Pt(8)[cite: 4]

    if other_discussions.strip():[cite: 4]
        p_od_head = doc.add_paragraph()[cite: 4]
        p_od_head.paragraph_format.space_before = Pt(6)[cite: 4]
        p_od_head.paragraph_format.space_after = Pt(4)[cite: 4]
        r_od_head = p_od_head.add_run("Other Discussions:")[cite: 4]
        r_od_head.bold = True[cite: 4]
        r_od_head.font.size = Pt(10)[cite: 4]
        r_od_head.font.name = "Arial"[cite: 4]
        
        p_od = doc.add_paragraph(other_discussions)[cite: 4]
        p_od.paragraph_format.space_after = Pt(12)[cite: 4]
        for r in p_od.runs:[cite: 4]
            r.font.name = "Arial"[cite: 4]
            r.font.size = Pt(9.5)[cite: 4]

    p_prep_label = doc.add_paragraph("Prepared by:")[cite: 4]
    p_prep_label.paragraph_format.space_before = Pt(12)[cite: 4]
    p_prep_label.paragraph_format.space_after = Pt(2)[cite: 4]
    p_prep_label.runs[0].font.name = "Arial"[cite: 4]
    p_prep_label.runs[0].font.bold = True[cite: 4]
    p_prep_label.runs[0].font.size = Pt(9.5)[cite: 4]

    p_prep_line = doc.add_paragraph("_______________________________")[cite: 4]
    p_prep_line.paragraph_format.space_after = Pt(2)[cite: 4]
    p_prep_line.runs[0].font.name = "Arial"[cite: 4]

    prep_name = meeting_details.get("prep_name", "").strip() or "____________________"[cite: 4]
    prep_desig = meeting_details.get("prep_desig", "").strip() or "PRIME Philippines"[cite: 4]
    p_prep_info = doc.add_paragraph(f"{prep_name}\n{prep_desig}")[cite: 4]
    p_prep_info.paragraph_format.space_after = Pt(12)[cite: 4]
    for r in p_prep_info.runs:[cite: 4]
        r.font.name = "Arial"[cite: 4]
        r.font.size = Pt(9.5)[cite: 4]

    p_conf_label = doc.add_paragraph("Confirmed by:")[cite: 4]
    p_conf_label.paragraph_format.space_after = Pt(2)[cite: 4]
    p_conf_label.runs[0].font.name = "Arial"[cite: 4]
    p_conf_label.runs[0].font.bold = True[cite: 4]
    p_conf_label.runs[0].font.size = Pt(9.5)[cite: 4]

    p_conf_line = doc.add_paragraph("_______________________________")[cite: 4]
    p_conf_line.paragraph_format.space_after = Pt(2)[cite: 4]
    p_conf_line.runs[0].font.name = "Arial"[cite: 4]

    conf_name = meeting_details.get("conf_name", "").strip() or (ext_atts[0] if ext_atts else "____________________")[cite: 4]
    conf_desig = meeting_details.get("conf_desig", "").strip() or (meeting_details.get("company_name", "").strip() or "Client")[cite: 4]
    p_conf_info = doc.add_paragraph(f"{conf_name}\n{conf_desig}")[cite: 4]
    p_conf_info.paragraph_format.space_after = Pt(6)[cite: 4]
    for r in p_conf_info.runs:[cite: 4]
        r.font.name = "Arial"[cite: 4]
        r.font.size = Pt(9.5)[cite: 4]

    bio = BytesIO()[cite: 4]
    doc.save(bio)[cite: 4]
    bio.seek(0)[cite: 4]
    return bio[cite: 4]

def export_to_pdf(df, meeting_details, other_discussions):
    buffer = BytesIO()[cite: 4]
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch
    )[cite: 4]
    story = [][cite: 4]
    styles = getSampleStyleSheet()[cite: 4]

    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        alignment=1,
        spaceAfter=2
    )[cite: 4]
    company_target = meeting_details.get("external_attendees", [])[cite: 4]
    primary_client_rep = company_target[0] if company_target else meeting_details.get("company_name", "").strip() or "CLIENT"[cite: 4]
    style_subtitle = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        alignment=1,
        spaceAfter=10
    )[cite: 4]
    style_body = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        spaceAfter=3
    )[cite: 4]
    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        alignment=1
    )[cite: 4]
    style_td = ParagraphStyle(
        'TableData',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10
    )[cite: 4]
    style_td_center = ParagraphStyle(
        'TableDataCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=1
    )[cite: 4]

    story.append(Paragraph("<u>MINUTES OF THE MEETING</u>", style_title))[cite: 4]
    story.append(Paragraph(f"PRIME PHILIPPINES & {primary_client_rep.upper()}", style_subtitle))[cite: 4]

    date_str = meeting_details.get("date", "____________")[cite: 4]
    time_str = meeting_details.get("time_range", "")[cite: 4]
    full_date = f"<b>Date:</b> {date_str}" + (f", {time_str}" if time_str.strip() else "")[cite: 4]
    story.append(Paragraph(full_date, style_body))[cite: 4]
    story.append(Paragraph(f"<b>Location:</b> {meeting_details.get('location', '____________')}", style_body))[cite: 4]

    prime_atts = meeting_details.get("prime_attendees", [])[cite: 4]
    ext_atts = meeting_details.get("external_attendees", [])[cite: 4]
    att_list = [][cite: 4]
    if ext_atts:[cite: 4]
        for att in ext_atts:[cite: 4]
            if att.strip():[cite: 4]
                comp_label = f", {meeting_details.get('company_name')}" if meeting_details.get('company_name') else ""[cite: 4]
                att_list.append(f"{att}{comp_label}")[cite: 4]
    if prime_atts:[cite: 4]
        for att in prime_atts:[cite: 4]
            att_list.append(f"{att} – PRIME Philippines")[cite: 4]

    if att_list:[cite: 4]
        story.append(Paragraph(f"<b>Attended by:</b>&nbsp;&nbsp;&nbsp;&nbsp;{att_list[0]}", style_body))[cite: 4]
        for a in att_list[1:]:[cite: 4]
            story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{a}", style_body))[cite: 4]

    story.append(Spacer(1, 4))[cite: 4]
    client_display = meeting_details.get('company_name', '').strip() or "the Client"[cite: 4]
    story.append(Paragraph(
        f"During the meeting held last {date_str}, PRIME Philippines, represented by the attendee/s shown above, "
        f"met with {client_display} to discuss opportunities for collaboration.",
        style_body
    ))[cite: 4]
    story.append(Spacer(1, 6))[cite: 4]

    table_data = [[
        Paragraph("<b>Discussion Points</b>", style_th),
        Paragraph("<b>Action Plan</b>", style_th),
        Paragraph("<b>Indicative Delivery Date</b>", style_th),
        Paragraph("<b>Person-in-charge</b>", style_th)
    ]][cite: 4]

    for i, row in df.iterrows():[cite: 4]
        table_data.append([
            Paragraph(f"{i+1}. {str(row.get('Discussion Points', ''))}", style_td),
            Paragraph(str(row.get("Action Plan", "")), style_td),
            Paragraph(str(row.get("Indicative Delivery Date", "")), style_td_center),
            Paragraph(str(row.get("Person-in-charge", "")), style_td_center)
        ])[cite: 4]

    col_widths = [2.4 * inch, 2.3 * inch, 1.1 * inch, 1.0 * inch][cite: 4]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)[cite: 4]
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FFFF00')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))[cite: 4]
    story.append(t)[cite: 4]

    note_style = ParagraphStyle('Note', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=7.5, leading=9, spaceBefore=4)[cite: 4]
    story.append(Paragraph("*Note: The indicative delivery date serves as reference point and still subject to changes. Furthermore, it depends on the progress of both parties.", note_style))[cite: 4]

    if other_discussions.strip():[cite: 4]
        story.append(Spacer(1, 6))[cite: 4]
        story.append(Paragraph("<b>Other Discussions:</b>", style_body))[cite: 4]
        story.append(Paragraph(other_discussions, style_body))[cite: 4]

    story.append(Spacer(1, 8))[cite: 4]
    prep_name = meeting_details.get("prep_name", "").strip() or "____________________"[cite: 4]
    prep_desig = meeting_details.get("prep_desig", "").strip() or "PRIME Philippines"[cite: 4]
    conf_name = meeting_details.get("conf_name", "").strip() or (ext_atts[0] if ext_atts else "____________________")[cite: 4]
    conf_desig = meeting_details.get("conf_desig", "").strip() or (meeting_details.get("company_name", "").strip() or "Client")[cite: 4]

    sign_data = [
        [Paragraph("<b>Prepared by:</b>", style_body), Paragraph("<b>Confirmed by:</b>", style_body)],
        [Paragraph("_______________________________", style_body), Paragraph("_______________________________", style_body)],
        [Paragraph(f"{prep_name}<br/>{prep_desig}", style_body), Paragraph(f"{conf_name}<br/>{conf_desig}", style_body)]
    ][cite: 4]
    sign_table = Table(sign_data, colWidths=[3.4 * inch, 3.4 * inch])[cite: 4]
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))[cite: 4]
    story.append(sign_table)[cite: 4]

    doc.build(story)[cite: 4]
    buffer.seek(0)[cite: 4]
    return buffer[cite: 4]

# ---- TOP ROW: Symmetrical Fixed Containers ----
col_upload, col_details = st.columns(2)[cite: 4]

# LEFT CONTAINER: Audio & Text Upload Section
with col_upload:[cite: 4]
    with st.container(height=520, border=True):[cite: 4]
        st.markdown('<h3>Input & Transcription</h3>', unsafe_allow_html=True)[cite: 4]
        
        tab_upload, tab_record, tab_text = st.tabs(["Upload Audio", "Record Audio", "Upload Text"])[cite: 4]

        # TAB 1: UPLOAD AUDIO
        with tab_upload:[cite: 4]
            uploaded_file = st.file_uploader(
                "Upload audio file (200MB limit supported)",
                type=["wav", "mp3", "m4a", "ogg", "flac", "mp4", "webm"],
                help="Audio uploads up to 200MB are supported."
            )[cite: 4]
            if uploaded_file:[cite: 4]
                st.write("")[cite: 4]
                if st.button("Transcribe Audio", key="btn_tx_upload"):[cite: 4]
                    p_bar = st.progress(0, text="Initializing audio pipeline (0%)...")[cite: 4]
                    p_status = st.empty()[cite: 4]
                    transcript = transcribe_audio_pipeline(uploaded_file.read(), uploaded_file.name, p_bar, p_status)[cite: 4]
                    p_bar.empty()[cite: 4]
                    p_status.empty()[cite: 4]
                    if transcript:[cite: 4]
                        st.session_state["transcript"] = transcript[cite: 4]
                        st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])[cite: 4]
                        st.session_state["other_discussions"] = ""[cite: 4]
                        st.session_state["chat_history"] = [][cite: 4]
                        st.rerun()[cite: 4]

        # TAB 2: RECORD AUDIO
        with tab_record:[cite: 4]
            recorded_audio = st.audio_input("Record audio directly", label_visibility="collapsed")[cite: 4]
            if recorded_audio:[cite: 4]
                rec_bytes = recorded_audio.read()[cite: 4]
                r_btn1, r_btn2 = st.columns(2)[cite: 4]
                with r_btn1:[cite: 4]
                    st.download_button(label="Save Recording (.wav)", data=rec_bytes, file_name=f"Recording_{datetime.date.today().strftime('%Y%m%d')}.wav", mime="audio/wav", use_container_width=True)[cite: 4]
                with r_btn2:[cite: 4]
                    if st.button("Transcribe Audio", key="btn_tx_record"):[cite: 4]
                        p_bar = st.progress(0, text="Initializing audio pipeline (0%)...")[cite: 4]
                        p_status = st.empty()[cite: 4]
                        transcript = transcribe_audio_pipeline(rec_bytes, "recording.wav", p_bar, p_status)[cite: 4]
                        p_bar.empty()[cite: 4]
                        p_status.empty()[cite: 4]
                        if transcript:[cite: 4]
                            st.session_state["transcript"] = transcript[cite: 4]
                            st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])[cite: 4]
                            st.session_state["other_discussions"] = ""[cite: 4]
                            st.session_state["chat_history"] = [][cite: 4]
                            st.rerun()[cite: 4]

        # TAB 3: TEXT UPLOAD
        with tab_text:[cite: 4]
            uploaded_text_file = st.file_uploader("Upload Document (.txt, .docx, .pdf)", type=["txt", "docx", "pdf"])[cite: 4]
            pasted_text = st.text_area("Or Paste Transcript Here", height=95, placeholder="Paste transcript text directly here...")[cite: 4]
            if st.button("Process Text", key="btn_tx_text"):[cite: 4]
                p_bar = st.progress(0, text="Extracting document text (0%)...")[cite: 4]
                time.sleep(0.2)[cite: 4]
                p_bar.progress(50, text="Reading document stream (50%)...")[cite: 4]
                extracted_str = ""[cite: 4]
                if uploaded_text_file:[cite: 4]
                    extracted_str = extract_text_from_file(uploaded_text_file)[cite: 4]
                if pasted_text and pasted_text.strip():[cite: 4]
                    extracted_str += "\n" + pasted_text.strip()[cite: 4]
                
                p_bar.progress(100, text="Document processed (100%)!")[cite: 4]
                time.sleep(0.2)[cite: 4]
                p_bar.empty()[cite: 4]
                if extracted_str.strip():[cite: 4]
                    st.session_state["transcript"] = extracted_str.strip()[cite: 4]
                    st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])[cite: 4]
                    st.session_state["other_discussions"] = ""[cite: 4]
                    st.session_state["chat_history"] = [][cite: 4]
                    st.rerun()[cite: 4]
                else:
                    st.warning("Please upload a file or paste text to proceed.")[cite: 4]

# RIGHT CONTAINER: Meeting Details Card
with col_details:[cite: 4]
    with st.container(height=520, border=True):[cite: 4]
        
        # Header + Auto-populate button + Settings Button
        if st.session_state["transcript"]:[cite: 4]
            head_col1, head_col_auto, head_col2 = st.columns([5.5, 3.5, 1.0])[cite: 4]
            with head_col_auto:[cite: 4]
                if st.button("Populate from Transcript", key="btn_auto_populate"):[cite: 4]
                    with st.spinner("Extracting metadata..."):[cite: 4]
                        meta = extract_metadata_with_deepseek(st.session_state["transcript"])[cite: 4]
                        if meta:[cite: 4]
                            if meta.get("client_name"):[cite: 4]
                                st.session_state["meeting_client_name"] = meta["client_name"][cite: 4]
                            if meta.get("location"):[cite: 4]
                                st.session_state["meeting_location"] = meta["location"][cite: 4]
                            if meta.get("crd_attendees"):[cite: 4]
                                matched_crd = [c for c in meta["crd_attendees"] if c in CRD_MEMBERS][cite: 4]
                                if matched_crd:[cite: 4]
                                    st.session_state["meeting_selected_crd"] = matched_crd[cite: 4]
                            if meta.get("external_attendees"):[cite: 4]
                                st.session_state["meeting_ext_attendees"] = meta["external_attendees"][cite: 4]
                            if meta.get("prepared_by"):[cite: 4]
                                st.session_state["meeting_prep_name"] = meta["prepared_by"][cite: 4]
                            if meta.get("confirmed_by"):[cite: 4]
                                st.session_state["meeting_conf_name"] = meta["confirmed_by"][cite: 4]
                            st.rerun()[cite: 4]
        else:
            head_col1, head_col2 = st.columns([9.0, 1.0])[cite: 4]
            
        with head_col1:[cite: 4]
            st.markdown('<h3 style="margin-top:0.2rem;">Meeting Details</h3>', unsafe_allow_html=True)[cite: 4]
        with head_col2:[cite: 4]
            if st.button("", key="card_settings_btn"):[cite: 4]
                st.session_state["show_settings"] = not st.session_state["show_settings"][cite: 4]
                st.rerun()[cite: 4]

        # Settings Drawer
        if st.session_state["show_settings"]:[cite: 4]
            with st.expander("Settings & Engine Diagnostics", expanded=True):[cite: 4]
                set_col1, set_col2 = st.columns(2)[cite: 4]
                with set_col1:[cite: 4]
                    engine_options = ["AI - DeepSeek", "Non-AI - Python Heuristic"][cite: 4]
                    selected_eng = st.selectbox(
                        "MoM Generation Engine",
                        options=engine_options,
                        index=engine_options.index(st.session_state["selected_engine"]) if st.session_state["selected_engine"] in engine_options else 0
                    )[cite: 4]
                    st.session_state["selected_engine"] = selected_eng[cite: 4]
                with set_col2:[cite: 4]
                    st.markdown("**Diagnostics**")[cite: 4]
                    st.write(f"• **Session Tokens:** `{st.session_state['tokens_used']:,}`")[cite: 4]
                    if st.session_state["last_api_call"]:[cite: 4]
                        last_call = st.session_state["last_api_call"][cite: 4]
                        st.write(f"• **Last Call:** `{last_call.strftime('%I:%M:%S %p')}`")[cite: 4]
            st.markdown("---")[cite: 4]

        # Row 1: Date & Single Hybrid Location Input
        r1_c1, r1_c2 = st.columns([1.2, 2.0])[cite: 4]
        with r1_c1:[cite: 4]
            meeting_date = st.date_input("Date", value=st.session_state["meeting_date"])[cite: 4]
            st.session_state["meeting_date"] = meeting_date[cite: 4]
        with r1_c2:[cite: 4]
            try:
                meeting_location = st.selectbox(
                    "Location",
                    options=LOCATION_OPTIONS,
                    index=LOCATION_OPTIONS.index(st.session_state.get("meeting_location")) if st.session_state.get("meeting_location") in LOCATION_OPTIONS else None,
                    placeholder="e.g. Boardroom or GreatWork Tower",
                    accept_user_input=True
                )[cite: 4]
            except TypeError:[cite: 4]
                loc_val = st.session_state.get("meeting_location", "")[cite: 4]
                meeting_location = st.text_input("Location", value=loc_val, placeholder="e.g. Boardroom or GreatWork Tower")[cite: 4]
            
            st.session_state["meeting_location"] = meeting_location if meeting_location else ""[cite: 4]

        # Row 2: Time Pickers
        r2_c1, r2_c2 = st.columns(2)[cite: 4]
        with r2_c1:[cite: 4]
            st.markdown("<p style='font-size:0.85rem; margin-bottom:0.2rem; color:#333; font-weight:500;'>Start Time</p>", unsafe_allow_html=True)[cite: 4]
            sc1, sc2, sc3 = st.columns([1, 1, 1.2])[cite: 4]
            sh = sc1.selectbox("SH", [f"{i:02d}" for i in range(1,13)], key="sh", label_visibility="collapsed")[cite: 4]
            sm = sc2.selectbox("SM", [f"{i:02d}" for i in range(0,60,5)], key="sm", label_visibility="collapsed")[cite: 4]
            sap = sc3.selectbox("SAP", ["AM", "PM"], key="sap", label_visibility="collapsed")[cite: 4]
            start_str = f"{sh}:{sm} {sap}"[cite: 4]
        with r2_c2:[cite: 4]
            st.markdown("<p style='font-size:0.85rem; margin-bottom:0.2rem; color:#333; font-weight:500;'>End Time</p>", unsafe_allow_html=True)[cite: 4]
            ec1, ec2, ec3 = st.columns([1, 1, 1.2])[cite: 4]
            eh = ec1.selectbox("EH", [f"{i:02d}" for i in range(1,13)], key="eh", label_visibility="collapsed")[cite: 4]
            em = ec2.selectbox("EM", [f"{i:02d}" for i in range(0,60,5)], key="em", label_visibility="collapsed")[cite: 4]
            eap = ec3.selectbox("EAP", ["AM", "PM"], key="eap", label_visibility="collapsed")[cite: 4]
            end_str = f"{eh}:{em} {eap}"[cite: 4]

        # Row 3: Attendees & Parties
        r3_c1, r3_c2 = st.columns(2)[cite: 4]
        with r3_c1:[cite: 4]
            client_name = st.text_input("Client / Company", value=st.session_state["meeting_client_name"], placeholder="XYZ Company")[cite: 4]
            st.session_state["meeting_client_name"] = client_name[cite: 4]
            selected_crd = st.multiselect("CRD Team Attendees", options=CRD_MEMBERS, default=st.session_state["meeting_selected_crd"])[cite: 4]
            st.session_state["meeting_selected_crd"] = selected_crd[cite: 4]
        with r3_c2:[cite: 4]
            ext_attendees_raw = st.text_input("External Attendees", value=st.session_state["meeting_ext_attendees"], placeholder="e.g. Mr. ABCD, Jane Doe")[cite: 4]
            st.session_state["meeting_ext_attendees"] = ext_attendees_raw[cite: 4]
            prep_col, conf_col = st.columns(2)[cite: 4]
            with prep_col:[cite: 4]
                prep_name = st.text_input("Prepared By", value=st.session_state["meeting_prep_name"], placeholder="Name")[cite: 4]
                st.session_state["meeting_prep_name"] = prep_name[cite: 4]
                prep_desig = st.text_input("Prep Designation", value=st.session_state["meeting_prep_desig"], placeholder="Designation")[cite: 4]
                st.session_state["meeting_prep_desig"] = prep_desig[cite: 4]
            with conf_col:[cite: 4]
                conf_name = st.text_input("Confirmed By", value=st.session_state["meeting_conf_name"], placeholder="Name")[cite: 4]
                st.session_state["meeting_conf_name"] = conf_name[cite: 4]
                conf_desig = st.text_input("Conf Designation", value=st.session_state["meeting_conf_desig"], placeholder="Designation")[cite: 4]
                st.session_state["meeting_conf_desig"] = conf_desig[cite: 4]

# ---- Step 2: Symmetrical Bottom Row (Full Transcript Left, Ask Echo Right) ----
if st.session_state["transcript"]:[cite: 4]
    row_left, row_right = st.columns(2)[cite: 4]
    
    # LEFT CONTAINER: Full Transcript
    with row_left:[cite: 4]
        with st.container(height=580, border=True):[cite: 4]
            st.markdown('<h3 style="margin-top:0.2rem;">Full Transcript</h3>', unsafe_allow_html=True)[cite: 4]
            
            st.text_area(
                "Transcript Content", 
                st.session_state["transcript"], 
                height=380, 
                label_visibility="collapsed"
            )[cite: 4]
            
            st.markdown("<hr style='margin: 0.8rem 0; border-top: 1px solid rgba(0,0,0,0.05);'>", unsafe_allow_html=True)[cite: 4]
            
            # Action Buttons Array at Bottom
            t_col1, t_col2, t_col3 = st.columns(3)[cite: 4]
            with t_col1:[cite: 4]
                if st.button("Generate MOM", key="btn_gen_mom"):[cite: 4]
                    extracted_df, other_disc = extract_structured_insights(st.session_state["transcript"], engine=st.session_state["selected_engine"])[cite: 4]
                    if not extracted_df.empty:[cite: 4]
                        st.session_state["df"] = extracted_df[cite: 4]
                        st.session_state["other_discussions"] = other_disc[cite: 4]
                        st.rerun()[cite: 4]
            with t_col2:[cite: 4]
                copy_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                body {{ margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; }}
                button {{
                    width: 100%;
                    height: 36px;
                    background-color: #222222;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 50px;
                    font-size: 0.82rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
                }}
                button:hover {{ background-color: #D4AF37; box-shadow: 0 6px 12px rgba(212, 175, 55, 0.2), 0 2px 4px rgba(212, 175, 55, 0.15); transform: translateY(-1px); }}
                </style>
                </head>
                <body>
                    <button id="copy-btn">Copy Text</button>
                    <script>
                    document.getElementById("copy-btn").addEventListener("click", function() {{
                        navigator.clipboard.writeText({json.dumps(st.session_state["transcript"])}).then(function() {{
                            document.getElementById("copy-btn").innerText = "Copied";
                            setTimeout(() => document.getElementById("copy-btn").innerText = "Copy Text", 2000);
                        }});
                    }});
                    </script>
                </body>
                </html>
                """[cite: 4]
                components.html(copy_html, height=36)[cite: 4]
            with t_col3:[cite: 4]
                st.download_button(
                    label="Download",
                    data=st.session_state["transcript"],
                    file_name=f"Transcript_{meeting_date.strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )[cite: 4]

    # RIGHT CONTAINER: Ask Echo (AI on Left, User on Right, Symmetrical)
    with row_right:[cite: 4]
        with st.container(height=580, border=True):[cite: 4]
            st.markdown('<h3 style="margin-top:0.2rem;">Ask Echo</h3>', unsafe_allow_html=True)[cite: 4]
            st.caption("Ask specific questions regarding action items, timelines, deliverables, or remarks.")[cite: 4]
            
            # Chat history container with Claude Minimalist Styling
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)[cite: 4]
            if not st.session_state["chat_history"]:[cite: 4]
                st.markdown(
                    '<div class="chat-ai">Hello. I am Echo. How may I assist you regarding this meeting transcript?</div>',
                    unsafe_allow_html=True
                )[cite: 4]
            else:
                for msg in st.session_state["chat_history"]:[cite: 4]
                    if msg["role"] == "assistant":[cite: 4]
                        formatted_content = msg["content"].replace("\n", "<br>")[cite: 4]
                        st.markdown(
                            f'<div class="chat-ai">{formatted_content}</div>',
                            unsafe_allow_html=True
                        )[cite: 4]
                    else:
                        st.markdown(
                            f'<div class="chat-user-wrap">'
                            f'<div class="chat-user">{msg["content"]}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )[cite: 4]
            st.markdown('</div>', unsafe_allow_html=True)[cite: 4]
            
            # Chat input
            if prompt := st.chat_input("Ask Echo a question..."):[cite: 4]
                st.session_state["chat_history"].append({"role": "user", "content": prompt})[cite: 4]
                with st.spinner("Analyzing transcript..."):[cite: 4]
                    answer = ask_deepseek_question(st.session_state["transcript"], prompt, st.session_state["chat_history"])[cite: 4]
                st.session_state["chat_history"].append({"role": "assistant", "content": answer})[cite: 4]
                st.rerun()[cite: 4]

# ---- Step 3: Minutes of Meeting Editor ----
if not st.session_state["df"].empty:[cite: 4]
    with st.container(border=True):[cite: 4]
        st.markdown('<h3>Minutes of Meeting Editor</h3>', unsafe_allow_html=True)[cite: 4]
        
        st.markdown(
            "<p style='font-size:0.85rem; color:#666; margin-bottom: 0.75rem;'>"
            "<i>*Note: Each discussion item is rendered as a clean card with auto-wrapping text boxes. Edit fields inline directly.</i></p>", 
            unsafe_allow_html=True
        )[cite: 4]
        
        df = st.session_state["df"].copy().reset_index(drop=True)[cite: 4]
        
        row_to_delete = None[cite: 4]
        for idx in range(len(df)):[cite: 4]
            with st.container(border=True):[cite: 4]
                # Single Horizontal Row per discussion card with auto-wrapping text areas
                c_disc, c_act, c_date, c_pic, c_del = st.columns([3.2, 3.2, 1.8, 1.8, 0.6])[cite: 4]
                
                with c_disc:[cite: 4]
                    st.markdown('<span class="playfair-label">Discussion Points</span>', unsafe_allow_html=True)[cite: 4]
                    st.text_area(
                        "DP",
                        value=str(df.at[idx, "Discussion Points"]),
                        key=f"dp_{idx}",
                        height=75,
                        label_visibility="collapsed"
                    )[cite: 4]
                with c_act:[cite: 4]
                    st.markdown('<span class="playfair-label">Action Plan</span>', unsafe_allow_html=True)[cite: 4]
                    st.text_area(
                        "AP",
                        value=str(df.at[idx, "Action Plan"]),
                        key=f"ap_{idx}",
                        height=75,
                        label_visibility="collapsed"
                    )[cite: 4]
                with c_date:[cite: 4]
                    st.markdown('<span class="playfair-label">Delivery Date</span>', unsafe_allow_html=True)[cite: 4]
                    st.text_area(
                        "DD",
                        value=str(df.at[idx, "Indicative Delivery Date"]),
                        key=f"date_{idx}",
                        height=75,
                        label_visibility="collapsed"
                    )[cite: 4]
                with c_pic:[cite: 4]
                    st.markdown('<span class="playfair-label">Person-in-charge</span>', unsafe_allow_html=True)[cite: 4]
                    st.text_area(
                        "PIC",
                        value=str(df.at[idx, "Person-in-charge"]),
                        key=f"pic_{idx}",
                        height=75,
                        label_visibility="collapsed"
                    )[cite: 4]
                with c_del:[cite: 4]
                    st.write("<div style='height: 38px;'></div>", unsafe_allow_html=True)[cite: 4]
                    if st.button("Delete", key=f"del_{idx}"):[cite: 4]
                        row_to_delete = idx[cite: 4]
        
        # Handle Deletion
        if row_to_delete is not None:[cite: 4]
            df = df.drop(index=row_to_delete).reset_index(drop=True)[cite: 4]
            st.session_state["df"] = df[cite: 4]
            st.rerun()[cite: 4]
        
        # Collect updated values using robust list aggregation
        rows_data = [][cite: 4]
        for idx in range(len(df)):[cite: 4]
            discussion_val = st.session_state.get(f"dp_{idx}", df.at[idx, "Discussion Points"])[cite: 4]
            action_val = st.session_state.get(f"ap_{idx}", df.at[idx, "Action Plan"])[cite: 4]
            date_val = st.session_state.get(f"date_{idx}", df.at[idx, "Indicative Delivery Date"])[cite: 4]
            pic_val = st.session_state.get(f"pic_{idx}", df.at[idx, "Person-in-charge"])[cite: 4]
            
            rows_data.append({
                "Discussion Points": discussion_val,
                "Action Plan": action_val,
                "Indicative Delivery Date": date_val,
                "Person-in-charge": pic_val
            })[cite: 4]
        
        st.session_state["df"] = pd.DataFrame(rows_data, columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])[cite: 4]
        
        # Add Item Button
        add_col, _ = st.columns([2, 8])[cite: 4]
        with add_col:[cite: 4]
            if st.button("+ Add Item", key="add_row"):[cite: 4]
                new_row_df = pd.DataFrame([{
                    "Discussion Points": "",
                    "Action Plan": "",
                    "Indicative Delivery Date": "",
                    "Person-in-charge": ""
                }])[cite: 4]
                st.session_state["df"] = pd.concat([st.session_state["df"], new_row_df], ignore_index=True)[cite: 4]
                st.rerun()[cite: 4]
        
        st.markdown('<span class="playfair-label" style="margin-top:0.75rem;">Other Discussions</span>', unsafe_allow_html=True)[cite: 4]
        st.session_state["other_discussions"] = st.text_area(
            "Other Discussions Content",
            value=st.session_state["other_discussions"],
            height=100,
            label_visibility="collapsed"
        )[cite: 4]

        time_range_str = f"{start_str} to {end_str}"[cite: 4]

        meeting_details = {
            "date": meeting_date.strftime("%B %d, %Y"),
            "time_range": time_range_str,
            "location": meeting_location if meeting_location.strip() else "____________",
            "company_name": client_name.strip() if client_name.strip() else "",
            "prime_attendees": selected_crd,
            "external_attendees": [x.strip() for x in ext_attendees_raw.split(",") if x.strip()],
            "prep_name": prep_name.strip(),
            "prep_desig": prep_desig.strip(),
            "conf_name": conf_name.strip(),
            "conf_desig": conf_desig.strip()
        }[cite: 4]

        # Dual Export Section (Word DOCX and PDF)
        exp_col1, exp_col2 = st.columns(2)[cite: 4]
        
        with exp_col1:[cite: 4]
            doc_bio = export_to_word(
                st.session_state["df"],
                meeting_details,
                st.session_state["other_discussions"]
            )[cite: 4]
            st.download_button(
                label="Download Word Document (.docx)",
                data=doc_bio,
                file_name=f"MOM_{client_name.replace(' ', '_') if client_name else 'Report'}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="btn_download_docx"
            )[cite: 4]

        with exp_col2:[cite: 4]
            pdf_bio = export_to_pdf(
                st.session_state["df"],
                meeting_details,
                st.session_state["other_discussions"]
            )[cite: 4]
            st.download_button(
                label="Download PDF Document (.pdf)",
                data=pdf_bio,
                file_name=f"MOM_{client_name.replace(' ', '_') if client_name else 'Report'}.pdf",
                mime="application/pdf",
                key="btn_download_pdf"
            )[cite: 4]

        # Dedicated Save Meeting to Supabase Button at the bottom right corner
        st.write("")[cite: 4]
        save_col1, save_col2 = st.columns([8, 2])[cite: 4]
        with save_col2:[cite: 4]
            if st.button("Save Meeting", key="btn_save_supabase_bottom"):[cite: 4]
                success, msg = save_meeting_to_supabase(
                    meeting_details, 
                    st.session_state["df"], 
                    st.session_state["other_discussions"], 
                    st.session_state["transcript"]
                )[cite: 4]
                if success:[cite: 4]
                    st.success(msg)[cite: 4]
                else:
                    st.error(f"Save failed: {msg}")[cite: 4]
