"""Audio transcription and document text extraction pipeline for Minutes of the Meeting."""
import time
import requests
import streamlit as st
from docx import Document
import PyPDF2

from utils.auth import get_current_user
from utils.audit import audit_log

GROQ_AUDIO_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
OPENAI_AUDIO_URL = "https://api.openai.com/v1/audio/transcriptions"

CRD_MEMBERS = [
    "Sondi Tuazon",
    "Kristina Balajadia",
    "Meliza Zapata",
    "Dykstra Pineda",
    "Cedtrix Rena",
    "Carlo Medina",
    "Dave Policarpio",
    "Irish Rima"
]


def detect_audio_format(audio_bytes: bytes) -> str:
    """Detect audio container format from magic bytes and return the correct file extension."""
    header = audio_bytes[:16]
    if header[:4] == b'RIFF':
        return "wav"
    elif header[:4] == b'\x1a\x45\xdf\xa3':
        return "webm"
    elif header[:4] == b'ID3\x03' or header[:4] == b'ID3\x04' or header[:4] in (b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'):
        return "mp3"
    elif header[:4] == b'OggS':
        return "ogg"
    elif header[4:8] == b'ftyp':
        return "m4a"
    return "wav"


def extract_text_from_file(uploaded_file) -> str:
    """Extract plain text from uploaded txt, pdf, or docx files."""
    try:
        if uploaded_file.name.endswith('.txt'):
            return uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        return ""
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return ""


def _call_openai_transcribe(audio_bytes: bytes, filename: str = "audio.mp3", model: str = "gpt-4o-mini-transcribe"):
    """Transcribe with OpenAI returning (text|None, error_msg|None)."""
    openai_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
    if not openai_key:
        return None, "OPENAI_API_KEY not configured in secrets."
    headers = {"Authorization": f"Bearer {openai_key}"}
    vocab_prompt = f"PRIME Philippines corporate meeting with team: {', '.join(CRD_MEMBERS)}"
    files = {
        "file": (filename, audio_bytes),
        "model": (None, model),
        "response_format": (None, "verbose_json"),
        "prompt": (None, vocab_prompt)
    }
    try:
        resp = requests.post(OPENAI_AUDIO_URL, headers=headers, files=files, timeout=180)
        if resp.status_code != 200:
            reason = ""
            try:
                reason = resp.json().get("error", {}).get("message", "")
            except Exception:
                pass
            err_msg = f"OpenAI API returned HTTP {resp.status_code}"
            if reason:
                err_msg += f": {reason}"
            return None, err_msg
        data = resp.json()
        segments = data.get("segments")
        if segments and isinstance(segments, list):
            lines = []
            for seg in segments:
                start = seg.get("start", 0)
                text = seg.get("text", "").strip()
                if text:
                    mins, secs = int(start // 60), int(start % 60)
                    lines.append(f"[{mins:02d}:{secs:02d}] {text}")
            if lines:
                return "\n".join(lines), None
        text = data.get("text", "")
        return text if text else (None, "OpenAI returned empty response")
    except requests.exceptions.Timeout:
        return None, "OpenAI API timed out after 180s"
    except Exception as e:
        return None, f"OpenAI API error: {e}"


def _call_groq_whisper(audio_bytes: bytes, filename: str = "audio.mp3"):
    """Transcribe with Groq Whisper returning (text|None, error_msg|None)."""
    groq_key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
    if not groq_key:
        return None, "GROQ_API_KEY not configured in secrets."
    headers = {"Authorization": f"Bearer {groq_key}"}
    vocab_prompt = f"PRIME Philippines corporate meeting with team: {', '.join(CRD_MEMBERS)}"
    files = {
        "file": (filename, audio_bytes),
        "model": (None, "whisper-large-v3-turbo"),
        "response_format": (None, "verbose_json"),
        "prompt": (None, vocab_prompt)
    }
    try:
        resp = requests.post(GROQ_AUDIO_URL, headers=headers, files=files, timeout=120)
        if resp.status_code != 200:
            reason = ""
            try:
                reason = resp.json().get("error", {}).get("message", "")
            except Exception:
                pass
            err_msg = f"Groq API returned HTTP {resp.status_code}"
            if reason:
                err_msg += f": {reason}"
            return None, err_msg
        data = resp.json()
        segments = data.get("segments") or data.get("chunks")
        if segments and isinstance(segments, list):
            lines = []
            for seg in segments:
                start = seg.get("start", 0)
                text = seg.get("text", "").strip()
                if text:
                    mins, secs = int(start // 60), int(start % 60)
                    lines.append(f"[{mins:02d}:{secs:02d}] {text}")
            if lines:
                return "\n".join(lines), None
        text = data.get("text", "")
        return text if text else (None, "Groq returned empty response")
    except requests.exceptions.Timeout:
        return None, "Groq API timed out after 120s"
    except Exception as e:
        return None, f"Groq API error: {e}"


def transcribe_audio_pipeline(audio_bytes: bytes, original_filename: str, progress_bar=None, status_placeholder=None):
    """Transcribe audio by sending raw bytes to Groq Whisper with fallback to OpenAI.
    
    Returns (transcript|None, error_msg|None).
    """
    if progress_bar:
        progress_bar.progress(10, text="Preparing audio for transcription (10%)...")
    raw_mb = len(audio_bytes) / (1024 * 1024)
    user = get_current_user()
    uid = user.get("id") if user else None
    uname = user.get("username") if user else None
    t0_total = time.time()
    
    audio_ext = detect_audio_format(audio_bytes)
    exts_to_try = [audio_ext]
    for ext in ["mp3", "wav", "m4a"]:
        if ext not in exts_to_try:
            exts_to_try.append(ext)

    groq_key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
    openai_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()

    # ── 1. Try Groq Whisper first (<=25MB) ──
    err = None
    if raw_mb <= 25.0 and groq_key:
        for _ext in exts_to_try:
            _fn = f"audio.{_ext}"
            if status_placeholder:
                status_placeholder.info(f"Sending to Groq Whisper (as {_fn})...")
            if progress_bar:
                progress_bar.progress(40, text=f"Sending {raw_mb:.1f}MB to Groq Whisper ({_fn}) (40%)...")
            t0 = time.time()
            text, err = _call_groq_whisper(audio_bytes, _fn)
            elapsed = int((time.time() - t0) * 1000)
            if text:
                if progress_bar:
                    progress_bar.progress(100, text=f"Groq completed in {elapsed//1000:.1f}s (100%)!")
                if status_placeholder:
                    status_placeholder.empty()
                audit_log("transcription", f"Groq OK ({raw_mb:.1f}MB, {_fn}) -> {len(text)} chars", uid, uname, status="ok", duration_ms=elapsed, page="1_minutes_of_the_meeting", endpoint="groq")
                return text, None
            audit_log("transcription", f"Groq FAIL ({_fn}): {err[:200] if err else ''}", uid, uname, status="error", duration_ms=elapsed, page="1_minutes_of_the_meeting", endpoint="groq")
        if progress_bar:
            progress_bar.progress(50, text="Groq attempt complete — trying OpenAI (50%)...")

    # ── 2. Fallback to OpenAI (gpt-4o-mini-transcribe, then whisper-1) ──
    err2 = None
    if openai_key:
        for openai_model in ["gpt-4o-mini-transcribe", "whisper-1"]:
            for _ext in exts_to_try:
                _fn = f"audio.{_ext}"
                if status_placeholder:
                    status_placeholder.info(f"Sending to OpenAI ({openai_model} as {_fn})...")
                if progress_bar:
                    progress_bar.progress(65, text=f"Sending {raw_mb:.1f}MB to {openai_model} ({_fn}) (65%)...")
                t0 = time.time()
                text, err2 = _call_openai_transcribe(audio_bytes, _fn, model=openai_model)
                elapsed = int((time.time() - t0) * 1000)
                if text:
                    if progress_bar:
                        progress_bar.progress(100, text=f"OpenAI ({openai_model}, {_fn}) completed in {elapsed//1000:.1f}s (100%)!")
                    if status_placeholder:
                        status_placeholder.empty()
                    audit_log("transcription", f"OpenAI {openai_model} OK ({raw_mb:.1f}MB, {_fn}) -> {len(text)} chars", uid, uname, status="ok", duration_ms=elapsed, page="1_minutes_of_the_meeting", endpoint=f"openai-{openai_model}")
                    return text, None
                audit_log("transcription", f"OpenAI {openai_model} FAIL ({_fn}): {err2[:200] if err2 else ''}", uid, uname, status="error", duration_ms=elapsed, page="1_minutes_of_the_meeting", endpoint=f"openai-{openai_model}")
                if progress_bar:
                    progress_bar.progress(75, text=f"{openai_model} ({_fn}) failed — checking fallback (75%)...")

    err_msg = "Transcription failed: "
    if err and err2:
        err_msg += f"Groq: {err} | OpenAI: {err2}"
    elif err:
        err_msg += f"Groq: {err}"
    elif err2:
        err_msg += f"OpenAI: {err2}"
    else:
        err_msg = "No transcription API configured (set GROQ_API_KEY or OPENAI_API_KEY in secrets)."

    total_ms = int((time.time() - t0_total) * 1000)
    audit_log("transcription", f"ALL FAILED: {err_msg}", uid, uname, status="error", duration_ms=total_ms, page="1_minutes_of_the_meeting", endpoint="both")
    if status_placeholder:
        status_placeholder.empty()
    return None, err_msg
