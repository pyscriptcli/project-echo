import sys
import os

# Add root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
import json
import re
import time
from io import BytesIO
from typing import Optional
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

# Centralized DB & Components
from utils.db import get_supabase_client, fetch_echo_context
from components.sidebar import setup_page_layout
from utils.auth import require_login, get_current_user
from utils.skills import load_prompt
from utils.minutes_memory import build_style_examples, store_approved_minutes
from utils.audit import audit_log

# Modularized MoM Subsystems
from utils.mom_audio import (
    transcribe_audio_pipeline,
    extract_text_from_file,
    detect_audio_format,
    CRD_MEMBERS
)
from utils.mom_export import (
    export_to_word_template_1,
    export_to_pdf_template_1,
    export_to_word_template_2,
    export_to_pdf_template_2
)

# 1. Page Configuration (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Project Echo - MoM Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Enforce login before rendering anything
require_login()

# 3. Render Global Navigation
setup_page_layout()

# 4. Custom CSS aligned with UI_skill.md (Strictly No Emojis, Cormorant Garamond + Montserrat)
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Montserrat:wght@400;500;600&family=Bebas+Neue&display=swap');
html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
.stApp {
    background-color: #f4f1ec;
    color: #1b1d1e;
}
.stApp > header { display: none !important; }
.block-container { padding-top: 1.2rem !important; padding-right: 2rem !important; padding-left: 2rem !important; max-width: 100% !important; }

/* Typography */
h1, h2, h3, .section-title { font-family: 'Cormorant Garamond', serif !important; font-style: italic !important; font-weight: 600 !important; color: #003366 !important; letter-spacing: 0.02em; }
.section-title { font-size: 1.4rem !important; margin-bottom: 0.15rem; }
.section-caption { color: #69727d; font-size: 0.85rem; margin-bottom: 0.75rem; }
.playfair-label { font-family: 'Cormorant Garamond', serif !important; font-style: italic !important; color: #003366 !important; font-size: 1.05rem !important; display: block; margin-bottom: 0.2rem; }

/* Panels & Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #ffffff !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    border: 1px solid rgba(0,51,102,0.12) !important;
    padding: 1.25rem !important;
    margin-bottom: 1rem !important;
}

/* Stepper Pill Bar */
.stepper-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    border: 1px solid rgba(0,51,102,0.14);
    border-radius: 6px;
    padding: 0.5rem 1rem;
    margin-bottom: 1.25rem;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    font-weight: 500;
    color: #69727d;
}
.step-item.active {
    color: #003366;
    font-weight: 600;
}
.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    font-size: 0.75rem;
    background: #e8e4de;
    color: #1b1d1e;
}
.step-item.active .step-badge {
    background: #003366;
    color: #ffffff;
}
.step-connector {
    flex: 1;
    height: 1px;
    background: rgba(0,51,102,0.15);
    margin: 0 1rem;
}

/* Buttons */
.stButton > button {
    background-color: #0c0c0e !important;
    color: #ffffff !important;
    border: 1px solid #c9ab4c !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    height: 34px !important;
    min-height: 34px !important;
    padding: 0.2rem 0.8rem !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #003366 !important;
    border-color: #d9bc5d !important;
    color: #ffffff !important;
}

/* Badges & Quotes */
.badge-confidence {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 600;
}
.badge-high { background-color: #DEF7EC; color: #03543F; }
.badge-medium { background-color: #FEF08A; color: #713F12; }
.badge-low { background-color: #FDE8E8; color: #9B1C1C; }

.evidence-quote-box {
    background-color: #F9FAFB;
    border-left: 3px solid #003366;
    padding: 0.5rem 0.75rem;
    font-size: 0.82rem;
    color: #1b1d1e;
    margin: 0.4rem 0;
    font-style: italic;
    border-radius: 0 4px 4px 0;
}

.guardrail-alert {
    background-color: #FFFBEB;
    border-left: 3px solid #F59E0B;
    padding: 0.35rem 0.6rem;
    font-size: 0.78rem;
    color: #92400E;
    margin-top: 0.3rem;
    border-radius: 0 4px 4px 0;
}

.missed-chip-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.4rem;
    margin-bottom: 0.8rem;
}

/* Chat Styling */
.chat-container { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; padding-bottom: 1rem; max-height: 360px; overflow-y: auto; }
.chat-ai { align-self: flex-start; background-color: #F9FAFB; border: 1px solid rgba(0,51,102,0.12); color: #1b1d1e; padding: 0.6rem 0.85rem; border-radius: 4px; max-width: 92%; font-size: 0.85rem; line-height: 1.45; }
.chat-user-wrap { display: flex; justify-content: flex-end; width: 100%; margin-bottom: 0.2rem; }
.chat-user { background-color: #0c0c0e; color: #FFFFFF; padding: 0.55rem 0.95rem; border-radius: 4px; max-width: 82%; font-size: 0.85rem; line-height: 1.45; }

.workflow-status {
    background: #ffffff;
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.9rem;
}
.workflow-status strong {
    color: #003366;
}

.summary-tile {
    background: #ffffff;
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 0.85rem 0.9rem;
    min-height: 88px;
}
.summary-label {
    color: #69727d;
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.35rem;
}
.summary-value {
    color: #003366;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    line-height: 1;
}
.summary-note {
    color: #1b1d1e;
    font-size: 0.82rem;
    margin-top: 0.3rem;
}
</style>
"""

# Global dialog guard cleanup
GUARD_CLEANUP_JS = """
<script>
(function() {
    var w = window.top;
    if (!w) return;
    var key = '__rec_studio_guard';
    if (w[key]) {
        w.removeEventListener('beforeunload', w[key]);
        delete w[key];
    }
})();
</script>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
components.html(GUARD_CLEANUP_JS, height=0)

# 5. Constants & Config
DEEPSEEK_API_KEY = str(st.secrets.get("DEEPSEEK_API_KEY", "")).strip()
DEEPSEEK_CHAT_URL = "https://api.deepseek.com/chat/completions"
SLACK_WEBHOOK_URL = str(st.secrets.get("SLACK_WEBHOOK_URL", "")).strip()

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
current_auth = get_current_user() or {}
auth_user_name = current_auth.get("full_name") or current_auth.get("name") or current_auth.get("username", "")
auth_user_role = current_auth.get("role", "Executive").title()
auth_desig_default = f"PRIME Philippines - {auth_user_role}" if "prime" not in auth_user_role.lower() else auth_user_role

if "mom_stage" not in st.session_state: st.session_state["mom_stage"] = "input"  # "input" | "review" | "export"
if "transcript" not in st.session_state: st.session_state["transcript"] = ""
if "user_notes" not in st.session_state: st.session_state["user_notes"] = ""
if "mom_items" not in st.session_state: st.session_state["mom_items"] = []
if "df" not in st.session_state: st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
if "other_discussions" not in st.session_state: st.session_state["other_discussions"] = ""
if "user_topics_text" not in st.session_state: st.session_state["user_topics_text"] = ""
if "recommended_missed_points" not in st.session_state: st.session_state["recommended_missed_points"] = []
if "entity_corrections_log" not in st.session_state: st.session_state["entity_corrections_log"] = []
if "speaker_mappings" not in st.session_state: st.session_state["speaker_mappings"] = {}
if "has_manual_edits" not in st.session_state: st.session_state["has_manual_edits"] = False
if "tokens_used" not in st.session_state: st.session_state["tokens_used"] = 0
if "last_api_call" not in st.session_state: st.session_state["last_api_call"] = None
if "chat_history" not in st.session_state: st.session_state["chat_history"] = []
if "draft_last_saved" not in st.session_state: st.session_state["draft_last_saved"] = None
if "draft_status_text" not in st.session_state: st.session_state["draft_status_text"] = "No draft yet"
if "selected_tpl" not in st.session_state: st.session_state["selected_tpl"] = 1
if "_recording_status" not in st.session_state: st.session_state["_recording_status"] = "IDLE"
if "_topics_discovered" not in st.session_state: st.session_state["_topics_discovered"] = False
if "last_processed_file" not in st.session_state: st.session_state["last_processed_file"] = None

# Metadata fields
if "meeting_date" not in st.session_state: st.session_state["meeting_date"] = datetime.date.today()
if "meeting_start_time" not in st.session_state: st.session_state["meeting_start_time"] = datetime.time(9, 0)
if "meeting_end_time" not in st.session_state: st.session_state["meeting_end_time"] = datetime.time(10, 0)
if "meeting_location" not in st.session_state: st.session_state["meeting_location"] = LOCATION_PRESETS[0]
if "meeting_type" not in st.session_state: st.session_state["meeting_type"] = "Internal"
if "meeting_client_name" not in st.session_state: st.session_state["meeting_client_name"] = ""
if "meeting_selected_crd" not in st.session_state: st.session_state["meeting_selected_crd"] = [auth_user_name] if auth_user_name in CRD_MEMBERS else []
if "meeting_ext_attendees" not in st.session_state: st.session_state["meeting_ext_attendees"] = ""
if "meeting_prep_name" not in st.session_state: st.session_state["meeting_prep_name"] = auth_user_name
if "meeting_prep_desig" not in st.session_state: st.session_state["meeting_prep_desig"] = auth_desig_default
if "meeting_conf_name" not in st.session_state: st.session_state["meeting_conf_name"] = ""
if "meeting_conf_desig" not in st.session_state: st.session_state["meeting_conf_desig"] = ""

# Dialog recording state
if "_dialog_recorded_bytes" not in st.session_state: st.session_state["_dialog_recorded_bytes"] = None
if "_dialog_record_notes" not in st.session_state: st.session_state["_dialog_record_notes"] = ""
if "_dialog_active" not in st.session_state: st.session_state["_dialog_active"] = False
if "_dialog_confirm_discard" not in st.session_state: st.session_state["_dialog_confirm_discard"] = False
if "_dialog_transcribing" not in st.session_state: st.session_state["_dialog_transcribing"] = False

# -------------------------------------------------------------
# Single Source of Truth State Synchronization Helpers
# -------------------------------------------------------------
def sync_mom_df_from_items():
    """Syncs st.session_state['df'] with approved items in mom_items."""
    approved = []
    for it in st.session_state["mom_items"]:
        if it.get("approved", True):
            approved.append({
                "Discussion Points": str(it.get("discussion_point", "")),
                "Action Plan": str(it.get("action_plan", "")),
                "Indicative Delivery Date": str(it.get("indicative_delivery_date", "TBD")),
                "Person-in-charge": str(it.get("person_in_charge", "Unassigned"))
            })
    if approved:
        st.session_state["df"] = pd.DataFrame(approved)
    else:
        st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])

def mark_draft_updated(reason: str) -> None:
    """Track the latest in-session draft checkpoint for the guided workflow."""
    now = datetime.datetime.now()
    st.session_state["draft_last_saved"] = now
    st.session_state["draft_status_text"] = f"{reason} at {now.strftime('%I:%M %p')}"

def reset_generated_minutes() -> None:
    """Clear generated review artifacts while preserving meeting setup fields."""
    st.session_state["mom_items"] = []
    st.session_state["df"] = pd.DataFrame(columns=["Discussion Points", "Action Plan", "Indicative Delivery Date", "Person-in-charge"])
    st.session_state["other_discussions"] = ""
    st.session_state["recommended_missed_points"] = []
    st.session_state["chat_history"] = []
    st.session_state["has_manual_edits"] = False
    st.session_state["_topics_discovered"] = False

def apply_metadata_to_session(meta: dict) -> None:
    """Populate meeting-detail session fields from extracted transcript metadata."""
    if not isinstance(meta, dict):
        return
    if meta.get("meeting_type") in MEETING_TYPE_OPTIONS:
        st.session_state["meeting_type"] = meta["meeting_type"]
    if meta.get("client_name"):
        st.session_state["meeting_client_name"] = meta["client_name"]
    if meta.get("location"):
        st.session_state["meeting_location"] = meta["location"]
    if meta.get("crd_attendees"):
        matched_crd = [name for name in meta["crd_attendees"] if name in CRD_MEMBERS]
        if matched_crd:
            st.session_state["meeting_selected_crd"] = matched_crd
    if meta.get("external_attendees"):
        st.session_state["meeting_ext_attendees"] = meta["external_attendees"]
    if meta.get("prepared_by"):
        st.session_state["meeting_prep_name"] = meta["prepared_by"]
    if meta.get("confirmed_by"):
        st.session_state["meeting_conf_name"] = meta["confirmed_by"]

def load_transcript_into_workflow(
    transcript_text: str,
    notes_text: str = "",
    auto_extract_metadata: bool = False,
    next_stage: Optional[str] = None,
) -> bool:
    """Normalize transcript ingestion so every input path resets and advances consistently."""
    clean_source = (transcript_text or "").strip()
    if not clean_source:
        return False

    clean_tx, logs = preprocess_transcript_entities(clean_source)
    st.session_state["transcript"] = clean_tx
    st.session_state["entity_corrections_log"] = logs
    if notes_text.strip():
        existing_notes = st.session_state.get("user_notes", "").strip()
        st.session_state["user_notes"] = f"{notes_text.strip()}\n{existing_notes}".strip() if existing_notes else notes_text.strip()

    reset_generated_minutes()

    if auto_extract_metadata:
        meta = extract_metadata_with_deepseek(clean_tx)
        if meta:
            apply_metadata_to_session(meta)

    st.session_state["_recording_status"] = "IDLE"
    mark_draft_updated("Draft saved")

    if next_stage:
        st.session_state["mom_stage"] = next_stage
    return True

def set_all_mom_items(items: list, mark_manual_edit: bool = False):
    st.session_state["mom_items"] = items
    if mark_manual_edit:
        st.session_state["has_manual_edits"] = True
    sync_mom_df_from_items()
    mark_draft_updated("Minutes draft updated")

def update_mom_item(idx: int, field_name: str, new_val):
    if 0 <= idx < len(st.session_state["mom_items"]):
        st.session_state["mom_items"][idx][field_name] = new_val
        st.session_state["has_manual_edits"] = True
        sync_mom_df_from_items()
        mark_draft_updated("Minutes draft updated")

def delete_mom_item(idx: int):
    if 0 <= idx < len(st.session_state["mom_items"]):
        st.session_state["mom_items"].pop(idx)
        st.session_state["has_manual_edits"] = True
        sync_mom_df_from_items()
        mark_draft_updated("Minutes draft updated")

def add_mom_item(topic: str = "New Item", dp: str = "", ap: str = "", dd: str = "TBD", pic: str = "Unassigned", quote: str = "", conf: str = "Medium"):
    new_item = {
        "topic_title": topic,
        "discussion_point": dp,
        "action_plan": ap,
        "indicative_delivery_date": dd,
        "person_in_charge": pic,
        "evidence_quote": quote,
        "confidence": conf,
        "approved": True
    }
    st.session_state["mom_items"].append(new_item)
    st.session_state["has_manual_edits"] = True
    sync_mom_df_from_items()
    mark_draft_updated("Minutes draft updated")

def parse_due_date_value(raw_value: str) -> tuple[datetime.date, bool]:
    """Parse a stored due date string into a date value plus a TBD flag."""
    value = str(raw_value or "").strip()
    if not value or value.lower() in {"tbd", "none", "n/a"}:
        return st.session_state.get("meeting_date", datetime.date.today()), True

    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(value, fmt).date(), False
        except ValueError:
            continue

    return st.session_state.get("meeting_date", datetime.date.today()), False

def build_review_summary() -> dict:
    """Compute workflow completeness metrics for the review and export stages."""
    items = st.session_state.get("mom_items", [])
    actionable = []
    missing_owner = 0
    missing_due = 0

    for item in items:
        if not item.get("approved", True):
            continue
        action_plan = str(item.get("action_plan", "")).strip()
        owner = str(item.get("person_in_charge", "")).strip()
        due = str(item.get("indicative_delivery_date", "")).strip()
        if action_plan and action_plan.lower() not in {"none", "n/a", "tbd"}:
            actionable.append(item)
            if owner in {"", "Unassigned", "None", "TBD"}:
                missing_owner += 1
            if due.lower() in {"", "tbd", "none", "n/a"}:
                missing_due += 1

    approved_count = len([item for item in items if item.get("approved", True)])
    return {
        "approved_count": approved_count,
        "actionable_count": len(actionable),
        "missing_owner": missing_owner,
        "missing_due": missing_due,
    }

def generate_minutes_draft(move_to_review: bool = True) -> None:
    """Generate or regenerate the minutes draft from the current transcript."""
    topics_suggested = suggest_discussion_topics_from_transcript(st.session_state["transcript"])
    st.session_state["user_topics_text"] = topics_suggested
    items, other_disc = match_evidence_and_synthesize(st.session_state["transcript"], topics_suggested)
    set_all_mom_items(items, mark_manual_edit=False)
    st.session_state["other_discussions"] = other_disc
    st.session_state["_topics_discovered"] = True
    if move_to_review:
        st.session_state["mom_stage"] = "review"

# -------------------------------------------------------------
# Entity & Guardrail Verification
# -------------------------------------------------------------
def preprocess_transcript_entities(transcript: str):
    if not transcript: return transcript, []
    context_data = fetch_echo_context() or {}
    replacements = []
    
    phonetic_map = {
        r"\bcool\s*berneties\b": "Kubernetes",
        r"\bcoolbernetes\b": "Kubernetes",
        r"\bmiss\s*meli\b": "Meliza Zapata",
        r"\bsir\s*sondi\b": "Sondi Tuazon",
        r"\bced\b": "Cedtrix Rena",
        r"\bprime\s*ph\b": "PRIME Philippines",
        r"\bgreat\s*work\b": "GreatWork",
        r"\bmom\b": "MOM"
    }
    cleaned = transcript
    for pattern, canonical in phonetic_map.items():
        if re.search(pattern, cleaned, flags=re.IGNORECASE):
            cleaned = re.sub(pattern, canonical, cleaned, flags=re.IGNORECASE)
            replacements.append(f"Standardized entity: '{canonical}'")

    jargon = context_data.get('jargon', {}) if isinstance(context_data, dict) else {}
    for k, v in jargon.items():
        if isinstance(k, str) and isinstance(v, str):
            p = r'\b' + re.escape(k) + r'\b'
            if re.search(p, cleaned, flags=re.IGNORECASE) and k.lower() != v.lower():
                cleaned = re.sub(p, v, cleaned, flags=re.IGNORECASE)
                replacements.append(f"Jargon match: '{k}' -> '{v}'")

    return cleaned, list(set(replacements))

def check_row_guardrails(row: dict, valid_attendees: list):
    warnings = []
    dp = str(row.get("discussion_point", "")).strip()
    ap = str(row.get("action_plan", "")).strip()
    dd = str(row.get("indicative_delivery_date", "")).strip()
    pic = str(row.get("person_in_charge", "")).strip()

    if pic and pic not in ["Unassigned", "None", "TBD", "PRIME Philippines", "Client"]:
        if valid_attendees:
            matched = any(att.lower() in pic.lower() or pic.lower() in att.lower() for att in valid_attendees)
            if not matched:
                warnings.append(f"Assignee '{pic}' not listed among confirmed attendees.")

    action_triggers = ['send', 'prepare', 'submit', 'update', 'review', 'email', 'coordinate', 'finalize', 'present', 'kailangan', 'ipapasa', 'gagawin']
    if (not ap or ap.lower() in ["none", "tbd", "n/a"]) and any(re.search(r'\b' + re.escape(w) + r'\b', dp, re.IGNORECASE) for w in action_triggers):
        warnings.append("Action commitment detected in discussion point, but Action Plan is empty.")

    if ap and ap.lower() not in ["none", "n/a"] and (not dd or dd.lower() in ["tbd", ""]):
        warnings.append("Missing target delivery date for actionable deliverable.")

    return warnings

def detect_speaker_tags(transcript: str):
    matches = re.findall(r'\b(Speaker\s*[0-9]+|Speaker\s*[A-Za-z]+)\b', transcript, flags=re.IGNORECASE)
    return sorted(list(set(matches)))

def apply_speaker_remapping(transcript: str, mapping: dict):
    if not mapping or not transcript: return transcript
    updated = transcript
    for spk, name in mapping.items():
        if name and name.strip():
            updated = re.sub(r'\b' + re.escape(spk) + r'\b', name.strip(), updated, flags=re.IGNORECASE)
    return updated

# -------------------------------------------------------------
# AI Extraction & Synthesis Pipeline
# -------------------------------------------------------------
def extract_metadata_with_deepseek(transcript: str):
    if not DEEPSEEK_API_KEY: return None
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    system_prompt = load_prompt("meeting_metadata")
    user_prompt = f"""Extract metadata from this transcript into valid JSON:
Schema: {{"meeting_type": "Internal, External, or Team", "client_name": "Company/Client name or empty string", "location": "Meeting location preset or custom name or empty string", "crd_attendees": ["Exact matching names from CRD member list: {', '.join(CRD_MEMBERS)}"], "external_attendees": "Comma-separated list of external attendee names", "prepared_by": "Name of attendee taking notes", "confirmed_by": "Primary external attendee/client rep"}}
Transcript: {transcript[:15000]}"""
    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1, "max_tokens": 500}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=45)
        if resp.status_code == 200:
            clean_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.json()["choices"][0]["message"]["content"].strip())
            return json.loads(clean_text)
    except Exception: pass
    return None

def suggest_discussion_topics_from_transcript(transcript: str):
    if not DEEPSEEK_API_KEY:
        return "1. Project Status & Progress\n2. Key Deliverables & Timelines\n3. Client Alignment & Action Items"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    system_prompt = load_prompt("topic_extractor")
    user_prompt = f"""Extract 4 to 7 key distinct discussion topics discussed in this transcript as valid JSON.
The transcript has [MM:SS] timestamps — use them to identify meeting flow and group consecutive segments into coherent topics.
Order topics chronologically by when they first appear in the timestamps.
Schema: {{"topics": ["Topic 1 title", "Topic 2 title", "Topic 3 title"]}}
Transcript: {transcript[:20000]}"""
    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1, "max_tokens": 500}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=45)
        if resp.status_code == 200:
            clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", resp.json()["choices"][0]["message"]["content"].strip())
            data = json.loads(clean)
            topics = data.get("topics", [])
            return "\n".join([f"{i+1}. {t}" for i, t in enumerate(topics)])
    except Exception: pass
    return "1. Project Updates\n2. Technical Implementation\n3. Timeline & Target Deadlines\n4. Resource Allocation & Next Steps"

def match_evidence_and_synthesize(transcript: str, user_topics_str: str):
    context_data = fetch_echo_context() or {}
    team = context_data.get('team', []) if isinstance(context_data, dict) else []
    team_list = ", ".join([str(t) for t in team if t])
    jargon = context_data.get('jargon', {}) if isinstance(context_data, dict) else {}
    jargon_list = "\n".join([f"- {k}: {v}" for k, v in jargon.items() if isinstance(k, str) and isinstance(v, str)])
    projects = context_data.get('projects', []) if isinstance(context_data, dict) else []
    projects_list = ", ".join([str(p) for p in projects if p])

    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    _uid = get_current_user().get("id") if get_current_user() else None
    style_examples = build_style_examples(_uid, limit=3) if _uid else ""

    knowledge_section = (
        f"Source Knowledge Base:\nTeam: {team_list}\nProjects: {projects_list}\nJargon:\n{jargon_list}"
        if (team_list or projects_list or jargon_list) else ""
    )
    system_prompt = load_prompt("minutes_generator", memory_examples=style_examples, knowledge_base=knowledge_section)

    user_prompt = f"""Match and synthesize evidence for each discussion point from the transcript.
The transcript has [MM:SS] timestamps — locate exact quotes with timestamp prefixes (e.g. "[03:45] We agreed...").

USER DISCUSSION TOPICS:
{user_topics_str}

MEETING TRANSCRIPT:
{transcript[:28000]}

ADDITIONAL USER NOTES:
{st.session_state.get("user_notes", "")[:5000]}

Format output strictly as JSON matching this schema:
{{
  "matched_items": [
    {{
      "topic_title": "Original or refined point title",
      "discussion_point": "Polished high-level corporate synthesized summary",
      "evidence_quote": "Exact 1-2 sentence verbatim quote with [MM:SS] timestamp prefix",
      "action_plan": "Specific executable deliverable, or 'None' if purely informational",
      "indicative_delivery_date": "Target date, time, or 'TBD'",
      "person_in_charge": "Designated individual (from attendees) or 'Unassigned'",
      "confidence": "High, Medium, or Low"
    }}
  ],
  "recommended_missed_points": [
    {{
      "topic_title": "Distinct topic found in transcript but NOT in user's input",
      "evidence_quote": "Exact 1-2 sentence verbatim quote supporting this topic"
    }}
  ],
  "other_discussions": "Concise executive summary of peripheral matters, announcements, or general context"
}}"""

    payload = {"model": "deepseek-chat", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], "response_format": {"type": "json_object"}, "temperature": 0.1, "max_tokens": 2500}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code == 200:
            res_json = resp.json()
            st.session_state["tokens_used"] += res_json.get("usage", {}).get("total_tokens", len(transcript) // 4)
            st.session_state["last_api_call"] = datetime.datetime.now()
            clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", res_json["choices"][0]["message"]["content"].strip())
            data = json.loads(clean)
            recs = data.get("recommended_missed_points", []) or []
            st.session_state["recommended_missed_points"] = recs if isinstance(recs, list) else []
            return data.get("matched_items", []), data.get("other_discussions", "")
    except Exception: pass
    st.session_state["recommended_missed_points"] = []
    return [], ""

def ask_deepseek_with_mutation(transcript: str, question: str, chat_history: list, current_df: pd.DataFrame):
    if not DEEPSEEK_API_KEY: return "DeepSeek API key is missing. Please check your configuration.", None
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    table_json = current_df.to_json(orient="records")
    system_prompt = load_prompt("ask_echo")
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-4:]: messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({
        "role": "user", 
        "content": f"CURRENT MOM TABLE:\n{table_json}\n\nTRANSCRIPT CONTEXT:\n{transcript[:20000]}\n\nUSER REQUEST: {question}"
    })
    payload = {"model": "deepseek-chat", "messages": messages, "response_format": {"type": "json_object"}, "temperature": 0.1, "max_tokens": 800}
    try:
        resp = requests.post(DEEPSEEK_CHAT_URL, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            res_json = resp.json()
            st.session_state["tokens_used"] += res_json.get("usage", {}).get("total_tokens", 0)
            st.session_state["last_api_call"] = datetime.datetime.now()
            clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", res_json["choices"][0]["message"]["content"].strip())
            data = json.loads(clean)
            return data.get("reply", "Understood."), data.get("action", None)
        return f"Service notice ({resp.status_code}): {resp.text}", None
    except Exception as e:
        return f"Connection error: {e}", None

# -------------------------------------------------------------
# Integrations (Supabase, Tasks, Webhooks)
# -------------------------------------------------------------
def save_meeting_to_supabase(meeting_details, df, other_discussions, transcript):
    client = get_supabase_client()
    if not client: return False, "Meeting archive service is unavailable.", None
    _user = get_current_user()
    _uid = _user.get("id") if _user else None
    _uname = _user.get("username") if _user else None
    t0 = time.time()
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

        # Learn user preferred style
        try:
            if _uid:
                store_approved_minutes(user_id=_uid, meeting_id=meeting_id, approved_items=table_items, other_discussions=other_discussions, client_name=client_name)
        except Exception: pass

        elapsed = int((time.time() - t0) * 1000)
        audit_log("save_meeting", f"MOM saved: {client_name} / {meeting_id}", _uid, _uname, status="ok", duration_ms=elapsed, page="1_minutes_of_the_meeting", endpoint="supabase")
        return True, "Successfully archived meeting record!", meeting_id
    except Exception as e:
        elapsed = int((time.time() - t0) * 1000)
        audit_log("save_meeting", f"FAILED: {e}", _uid, _uname, status="error", duration_ms=elapsed, page="1_minutes_of_the_meeting", endpoint="supabase")
        return False, str(e), None

def push_action_items_to_tasks_board(df: pd.DataFrame, meeting_details: dict) -> tuple[int, str]:
    client = get_supabase_client()
    if not client: return 0, "Task sync service is unavailable."
    inserted = 0
    company = meeting_details.get("company_name", "General Meeting")
    for _, row in df.iterrows():
        ap = str(row.get("Action Plan", "")).strip()
        if ap and ap.lower() not in ["none", "n/a", "tbd", ""]:
            pic = str(row.get("Person-in-charge", "Unassigned")).strip()
            dd = str(row.get("Indicative Delivery Date", "")).strip()
            due_iso = None
            if dd and dd.lower() != "tbd":
                for fmt in ["%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"]:
                    try:
                        due_iso = datetime.datetime.strptime(dd, fmt).date().isoformat()
                        break
                    except Exception: pass
            payload = {
                "title": ap[:150],
                "description": f"From Meeting: {company}\nContext: {str(row.get('Discussion Points', ''))}",
                "assignee": pic if pic not in ["Unassigned", "None", "TBD"] else None,
                "due_date": due_iso,
                "status": "todo"
            }
            try:
                client.table("tasks").insert(payload).execute()
                inserted += 1
            except Exception: pass
    return inserted, f"Synced {inserted} action items to the Task Board!"

def dispatch_action_items_webhook(webhook_url: str, df: pd.DataFrame, meeting_details: dict):
    if not webhook_url: return False, "No Webhook URL provided."
    try:
        tasks = []
        for idx, row in df.iterrows():
            ap = str(row.get("Action Plan", "")).strip()
            if ap and ap.lower() not in ["none", "n/a"]:
                tasks.append({
                    "task_number": idx + 1,
                    "action_plan": ap,
                    "assignee": str(row.get("Person-in-charge", "Unassigned")),
                    "due_date": str(row.get("Indicative Delivery Date", "TBD")),
                    "context": str(row.get("Discussion Points", ""))
                })
        payload = {
            "text": f"*New Action Items from Echo MoM*\n*Client/Project:* {meeting_details.get('company_name', 'Internal')}\n*Date:* {meeting_details.get('date', '')}",
            "tasks": tasks
        }
        res = requests.post(webhook_url, json=payload, timeout=15)
        if res.status_code in [200, 201, 204]:
            return True, f"Dispatched {len(tasks)} tasks via Webhook!"
        return False, f"Webhook error ({res.status_code}): {res.text}"
    except Exception as e:
        return False, f"Webhook failed: {e}"

# -------------------------------------------------------------
# Recording Studio Dialog
# -------------------------------------------------------------
@st.dialog("Recording Studio", width="large")
def recording_studio_dialog():
    st.session_state["_dialog_active"] = True
    if st.session_state.get("_dialog_recorded_bytes") is None and st.session_state["_recording_status"] == "IDLE":
        st.session_state["_recording_status"] = "RECORDING"

    is_capturing = st.session_state.get("_dialog_recorded_bytes") is None
    if is_capturing and not st.session_state.get("_dialog_transcribing"):
        st.markdown(
            """
            <style>
            button[aria-label="Close"] {
                display: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        components.html(
            """
            <script>
            (function() {
                var w = window.top;
                if (!w) return;
                var key = '__rec_studio_guard';
                if (w[key]) return;
                w[key] = function(e) {
                    e.preventDefault();
                    e.returnValue = 'Recording in progress. Finish the recording before leaving.';
                    return e.returnValue;
                };
                w.addEventListener('beforeunload', w[key]);
            })();
            </script>
            """,
            height=0,
        )

    if st.session_state["_dialog_transcribing"]:
        stored_bytes = st.session_state.get("_dialog_recorded_bytes")
        stored_notes = st.session_state.get("_dialog_record_notes", "")
        if stored_bytes is None:
            st.warning("No audio captured.")
            st.session_state["_dialog_transcribing"] = False
            st.session_state["_recording_status"] = "RECORDING"
        else:
            p_bar = st.progress(0, text="Initializing audio pipeline...")
            p_status = st.empty()
            raw_tx, tx_err = transcribe_audio_pipeline(stored_bytes, "recording.wav", p_bar, p_status)
            p_bar.empty()
            p_status.empty()
            if raw_tx:
                load_transcript_into_workflow(
                    raw_tx,
                    notes_text=stored_notes,
                    auto_extract_metadata=True,
                    next_stage="review",
                )
                st.session_state["_topics_discovered"] = False
                st.session_state["_dialog_recorded_bytes"] = None
                st.session_state["_dialog_record_notes"] = ""
                st.session_state["_dialog_transcribing"] = False
                st.session_state["_dialog_active"] = False
                st.session_state["_recording_status"] = "IDLE"
                st.rerun()
            else:
                st.error(f"Transcription failed: {tx_err}")
                st.session_state["_dialog_transcribing"] = False
                st.session_state["_recording_status"] = "RECORDED"
        return

    col_l, col_r = st.columns([0.6, 0.4])
    with col_l:
        st.markdown("##### Meeting Notes")
        st.session_state["_dialog_record_notes"] = st.text_area(
            "Jot down live meeting notes...",
            value=st.session_state.get("_dialog_record_notes", ""),
            height=280,
            placeholder="Key decisions, announcements, or discussion items..."
        )
    with col_r:
        st.markdown("##### Microphone Input")
        stored = st.session_state.get("_dialog_recorded_bytes")
        if stored is not None:
            st.session_state["_recording_status"] = "RECORDED"
            st.audio(stored, format="audio/wav")
            st.success(f"Audio recorded ({len(stored)//32000}s estimated).")
        else:
            st.info("Keep this dialog open while recording. Navigation and close actions stay locked until audio is captured.")
            rec = st.audio_input("Record audio", label_visibility="collapsed")
            if rec:
                st.session_state["_dialog_recorded_bytes"] = rec.read()
                st.session_state["_recording_status"] = "RECORDED"
                st.rerun()

    if st.session_state.get("_dialog_recorded_bytes") is not None:
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Transcribe recording", type="primary", use_container_width=True):
                st.session_state["_dialog_transcribing"] = True
                st.rerun()
        with b2:
            if st.button("Record again", use_container_width=True):
                st.session_state["_dialog_recorded_bytes"] = None
                st.session_state["_recording_status"] = "RECORDING"
                st.rerun()
        with b3:
            if st.button("Close studio", use_container_width=True):
                st.session_state["_dialog_active"] = False
                st.session_state["_recording_status"] = "IDLE"
                st.rerun()
    else:
        st.caption("Finish the recording with the microphone control above. Review actions will unlock once audio is captured.")

# =============================================================
# TOP HEADER & GUIDED STEPPER
# =============================================================
top_head_l, top_head_r = st.columns([7, 3])
with top_head_l:
    st.markdown('<div class="section-title">Minutes of the Meeting</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Convert meeting transcripts and audio into verified, evidence-grounded corporate deliverables.</div>', unsafe_allow_html=True)

with top_head_r:
    generate_label = "Generate minutes" if not st.session_state.get("mom_items") else "Regenerate minutes"
    if st.session_state["tokens_used"] > 0:
        st.markdown(
            f'<div style="text-align:right; font-size:0.75rem; color:#69727d; padding-top:0.4rem;">'
            f'Tokens: <b>{st.session_state["tokens_used"]:,}</b> | Engine: <b>DeepSeek</b></div>',
            unsafe_allow_html=True
        )
    generate_clicked = st.button(
        generate_label,
        icon=":material/auto_awesome:",
        use_container_width=True,
        disabled=not st.session_state.get("transcript"),
    )
    if generate_clicked:
        with st.spinner("Generating draft minutes..."):
            generate_minutes_draft(move_to_review=True)
        st.rerun()

# Stepper Navigation
stages_list = ["1. Input & Setup", "2. Review & Refine", "3. Finalize & Export"]
stage_key_map = {"1. Input & Setup": "input", "2. Review & Refine": "review", "3. Finalize & Export": "export"}
inv_stage_map = {v: k for k, v in stage_key_map.items()}

current_label = inv_stage_map.get(st.session_state["mom_stage"], "1. Input & Setup")
chosen_stage = st.segmented_control(
    "Workflow Stage",
    options=stages_list,
    default=current_label,
    label_visibility="collapsed"
)
if chosen_stage and stage_key_map[chosen_stage] != st.session_state["mom_stage"]:
    requested_stage = stage_key_map[chosen_stage]
    if requested_stage == "review" and not st.session_state.get("transcript"):
        st.warning("Load a transcript first before opening Review & Refine.")
    elif requested_stage == "export" and st.session_state.get("df", pd.DataFrame()).empty:
        st.warning("Approve at least one discussion item before opening Finalize & Export.")
    else:
        st.session_state["mom_stage"] = requested_stage
        st.rerun()

# =============================================================
# STAGE 1: INPUT & SETUP
# =============================================================
if st.session_state["mom_stage"] == "input":
    col_input_l, col_input_r = st.columns([1, 1])

    # Left Container: Source & Transcript
    with col_input_l:
        with st.container(border=True):
            st.markdown('<span class="playfair-label">1. Meeting Source</span>', unsafe_allow_html=True)
            tab_audio, tab_rec, tab_text = st.tabs(["Upload Audio", "Record Live", "Upload / Paste Text"])

            with tab_audio:
                audio_file = st.file_uploader("Upload meeting recording", type=["wav", "mp3", "m4a", "ogg", "flac", "mp4", "webm"], help="Uploads up to 200MB are supported.")
                if audio_file and st.session_state["_recording_status"] == "IDLE":
                    f_sig = f"{audio_file.name}_{audio_file.size}"
                    if f_sig != st.session_state.get("last_processed_file"):
                        st.session_state["last_processed_file"] = f_sig
                        st.session_state["_recording_status"] = "TRANSCRIBING"
                        p_bar = st.progress(0, text="Initializing audio pipeline...")
                        p_stat = st.empty()
                        raw_tx, tx_err = transcribe_audio_pipeline(audio_file.read(), audio_file.name, p_bar, p_stat)
                        p_bar.empty()
                        p_stat.empty()
                        if raw_tx:
                            load_transcript_into_workflow(raw_tx, auto_extract_metadata=True)
                            st.rerun()
                        else:
                            st.session_state["_recording_status"] = "IDLE"
                            st.error(f"Transcription failed: {tx_err}")

            with tab_rec:
                st.markdown("<p style='font-size:0.85rem; color:#69727d;'>Use the built-in Recording Studio to capture microphone audio and take live notes in a dedicated modal.</p>", unsafe_allow_html=True)
                if st.button("Open Recording Studio", icon=":material/mic:", use_container_width=True):
                    recording_studio_dialog()

            with tab_text:
                up_doc = st.file_uploader("Upload transcript or notes (.txt, .docx, .pdf)", type=["txt", "docx", "pdf"])
                pasted_tx = st.text_area("Or paste transcript directly here", height=120, placeholder="Paste transcript or notes here...")
                if st.button("Process Transcript Text", icon=":material/description:", use_container_width=True):
                    text_content = ""
                    if up_doc: text_content = extract_text_from_file(up_doc)
                    if pasted_tx.strip(): text_content += ("\n" + pasted_tx.strip() if text_content else pasted_tx.strip())
                    if text_content.strip():
                        load_transcript_into_workflow(text_content, auto_extract_metadata=True)
                        st.success(f"Transcript loaded successfully ({len(st.session_state['transcript'].split())} words)!")
                        st.rerun()
                    else:
                        st.warning("Please provide text or upload a document to proceed.")

            # Transcript Viewer & Notes
            if st.session_state["transcript"]:
                st.markdown("<hr style='margin:0.75rem 0 0.5rem 0;'>", unsafe_allow_html=True)
                with st.expander(f"Transcript Content ({len(st.session_state['transcript'].split())} words)", expanded=False):
                    st.text_area("Full Transcript", value=st.session_state["transcript"], height=200, label_visibility="collapsed")
                    t_col1, t_col2 = st.columns(2)
                    with t_col1:
                        st.download_button(label="Download Transcript (.txt)", data=st.session_state["transcript"], file_name=f"Transcript_{datetime.date.today().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
                    with t_col2:
                        if st.button("Clear Transcript", use_container_width=True):
                            st.session_state["transcript"] = ""
                            set_all_mom_items([], mark_manual_edit=False)
                            st.session_state["_topics_discovered"] = False
                            st.rerun()

                # Speaker Mapping (if tags detected)
                spk_found = detect_speaker_tags(st.session_state["transcript"])
                if spk_found:
                    with st.expander(f"Advanced Transcript Cleanup ({len(spk_found)} speaker tags found)", expanded=False):
                        st.caption("Map raw speaker labels (e.g. Speaker 1) to confirmed attendee names.")
                        crd_and_ext = st.session_state["meeting_selected_crd"] + [x.strip() for x in st.session_state["meeting_ext_attendees"].split(",") if x.strip()]
                        spk_options = [""] + crd_and_ext
                        for spk in spk_found:
                            st.session_state["speaker_mappings"][spk] = st.selectbox(
                                f"Map '{spk}' to:",
                                options=spk_options,
                                key=f"map_spk_{spk}"
                            )
                        if st.button("Apply Speaker Names to Transcript", use_container_width=True):
                            remapped = apply_speaker_remapping(st.session_state["transcript"], st.session_state["speaker_mappings"])
                            st.session_state["transcript"] = remapped
                            st.session_state["_topics_discovered"] = False
                            mark_draft_updated("Transcript cleanup saved")
                            st.success("Updated transcript with speaker names!")
                            st.rerun()

            # Optional Pre-meeting Notes
            with st.expander("Optional Meeting Notes & Objectives", expanded=False):
                st.caption("Provide additional agenda, background, or objectives to inform the AI synthesis.")
                st.session_state["user_notes"] = st.text_area("Notes", value=st.session_state.get("user_notes", ""), height=90, placeholder="Pre-meeting agenda or key priorities...", label_visibility="collapsed")

    # Right Container: Meeting Details Form
    with col_input_r:
        with st.container(border=True):
            st.markdown('<span class="playfair-label">2. Meeting Information</span>', unsafe_allow_html=True)
            
            # Row 1: Date & Time Pickers
            r1_1, r1_2, r1_3 = st.columns([1.2, 1, 1])
            with r1_1:
                st.session_state["meeting_date"] = st.date_input("Date", value=st.session_state["meeting_date"])
            with r1_2:
                st.session_state["meeting_start_time"] = st.time_input("Start Time", value=st.session_state["meeting_start_time"])
            with r1_3:
                st.session_state["meeting_end_time"] = st.time_input("End Time", value=st.session_state["meeting_end_time"])

            # Row 2: Type & Location
            r2_1, r2_2 = st.columns([1, 1.4])
            with r2_1:
                st.session_state["meeting_type"] = st.selectbox("Meeting Type", options=MEETING_TYPE_OPTIONS, index=MEETING_TYPE_OPTIONS.index(st.session_state["meeting_type"]) if st.session_state["meeting_type"] in MEETING_TYPE_OPTIONS else 0)
            with r2_2:
                loc_list = list(LOCATION_PRESETS)
                curr_loc = st.session_state.get("meeting_location", "")
                if curr_loc and curr_loc not in loc_list: loc_list.append(curr_loc)
                loc_list.append("Other / Custom...")
                sel_loc = st.selectbox("Venue / Location", options=loc_list, index=loc_list.index(curr_loc) if curr_loc in loc_list else 0)
                if sel_loc == "Other / Custom...":
                    st.session_state["meeting_location"] = st.text_input("Custom Venue", value="" if curr_loc in LOCATION_PRESETS else curr_loc, placeholder="e.g. Boardroom or Client Office")
                else:
                    st.session_state["meeting_location"] = sel_loc

            # Row 3: Client & Attendees
            st.session_state["meeting_client_name"] = st.text_input("Client / Project / Company Name", value=st.session_state["meeting_client_name"], placeholder="e.g. Acme Corp or Internal Project Echo")
            
            r3_1, r3_2 = st.columns(2)
            with r3_1:
                st.session_state["meeting_selected_crd"] = st.multiselect("PRIME Team Attendees", options=CRD_MEMBERS, default=st.session_state["meeting_selected_crd"])
            with r3_2:
                st.session_state["meeting_ext_attendees"] = st.text_input("External Attendees (comma-separated)", value=st.session_state["meeting_ext_attendees"], placeholder="e.g. Jane Doe (CEO), John Smith")

            # Row 4: Signatories (Prepared & Confirmed By)
            r4_1, r4_2 = st.columns(2)
            with r4_1:
                st.session_state["meeting_prep_name"] = st.text_input("Prepared By", value=st.session_state["meeting_prep_name"])
                st.session_state["meeting_prep_desig"] = st.text_input("Prep Designation", value=st.session_state["meeting_prep_desig"])
            with r4_2:
                st.session_state["meeting_conf_name"] = st.text_input("Confirmed By", value=st.session_state["meeting_conf_name"], placeholder="Client Rep or Lead")
                st.session_state["meeting_conf_desig"] = st.text_input("Conf Designation", value=st.session_state["meeting_conf_desig"], placeholder="Designation / Title")

            # Auto-fill helper
            if st.session_state["transcript"]:
                with st.expander("Advanced Setup Tools", expanded=False):
                    st.caption("Use this only when you want Echo to re-check attendees, client name, or venue from the transcript.")
                    if st.button("Re-extract Details from Transcript", icon=":material/auto_awesome:", use_container_width=True):
                        with st.spinner("Analyzing transcript metadata..."):
                            meta = extract_metadata_with_deepseek(st.session_state["transcript"])
                            if meta:
                                apply_metadata_to_session(meta)
                                mark_draft_updated("Meeting details refreshed")
                                st.success("Metadata populated from transcript!")
                                st.rerun()

    # Step 1 status
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    if not st.session_state["transcript"]:
        st.info("Upload an audio file, record audio, or paste transcript text to unlock minutes generation.")
    else:
        st.markdown(
            f'<div class="workflow-status"><strong>Draft status:</strong> {st.session_state.get("draft_status_text", "No draft yet")}<br>'
            f'<span style="color:#69727d; font-size:0.82rem;">Generate minutes from the top-right action whenever the transcript and meeting details are ready.</span></div>',
            unsafe_allow_html=True
        )

# =============================================================
# STAGE 2: REVIEW & REFINE
# =============================================================
elif st.session_state["mom_stage"] == "review":
    if not st.session_state["transcript"]:
        st.warning("No transcript loaded. Please return to Step 1 to input meeting audio or text.")
        if st.button("← Back to Input & Setup"):
            st.session_state["mom_stage"] = "input"
            st.rerun()
    else:
        # Auto-synthesis on first arrival if empty
        if not st.session_state.get("_topics_discovered") and not st.session_state["mom_items"]:
            with st.spinner("Extracting discussion topics and matching evidence quotes..."):
                generate_minutes_draft(move_to_review=False)
                st.rerun()

        # Review Header & Quick Controls
        tb_col1, tb_col2 = st.columns([7, 3])
        with tb_col1:
            item_count = len(st.session_state["mom_items"])
            approved_count = len([it for it in st.session_state["mom_items"] if it.get("approved", True)])
            st.markdown(f'<span class="section-title">Review Draft Minutes</span> &nbsp; <span style="font-size:0.85rem; color:#69727d;">({approved_count}/{item_count} Approved)</span>', unsafe_allow_html=True)
            st.caption("Each row combines the source quote, summary, action, owner, and due date in one place.")
        with tb_col2:
            r_c1, r_c2 = st.columns(2)
            with r_c1:
                if st.button("← Back", use_container_width=True):
                    st.session_state["mom_stage"] = "input"
                    st.rerun()
            with r_c2:
                if st.button("Export →", type="primary", use_container_width=True):
                    st.session_state["mom_stage"] = "export"
                    st.rerun()

        review_summary = build_review_summary()
        st.markdown(
            f'<div class="workflow-status"><strong>Review status:</strong> '
            f'{review_summary["approved_count"]} approved item(s), '
            f'{review_summary["actionable_count"]} action item(s), '
            f'{review_summary["missing_owner"]} missing owner(s), '
            f'{review_summary["missing_due"]} missing due date(s).</div>',
            unsafe_allow_html=True,
        )

        if review_summary["missing_owner"] or review_summary["missing_due"]:
            st.warning("A few action items still need cleanup before final export. Review the missing owners and due dates shown above.")
        else:
            st.success("The draft looks export-ready. You can still refine wording, but the key action-tracking fields are complete.")

        missed = st.session_state.get("recommended_missed_points", []) or []
        if missed:
            with st.expander(f"Suggested additional discussion points ({len(missed)})", expanded=False):
                st.caption("Echo found a few topics that might be worth adding to the draft.")
                chip_cols = st.columns(min(len(missed), 3))
                for c_idx, rec in enumerate(missed):
                    col_target = chip_cols[c_idx % len(chip_cols)]
                    rec_title = rec.get("topic_title", "Unassigned Topic")
                    rec_quote = rec.get("evidence_quote", "")
                    with col_target:
                        st.markdown(f"**{rec_title}**")
                        if rec_quote:
                            st.caption(rec_quote[:180] + ("..." if len(rec_quote) > 180 else ""))
                        if st.button(f"Add topic", key=f"chip_add_{c_idx}", use_container_width=True):
                            add_mom_item(topic=rec_title, dp=f"Discussion regarding {rec_title}.", ap="TBD", dd="TBD", pic="Unassigned", quote=rec_quote)
                            st.session_state["recommended_missed_points"].pop(c_idx)
                            st.rerun()

        all_attendees = st.session_state["meeting_selected_crd"] + [x.strip() for x in st.session_state["meeting_ext_attendees"].split(",") if x.strip()]
        if not st.session_state["mom_items"]:
            st.info("No items in review yet. Generate minutes from the top action to build the first draft.")
        else:
            for idx, item in enumerate(st.session_state["mom_items"]):
                with st.container(border=True):
                    head_c1, head_c2, head_c3, head_c4 = st.columns([5, 1.2, 1.2, 1])
                    with head_c1:
                        new_title = st.text_input(
                            f"Topic title {idx+1}",
                            value=item.get("topic_title", f"Point {idx+1}"),
                            key=f"title_{idx}",
                        )
                        if new_title != item.get("topic_title"):
                            update_mom_item(idx, "topic_title", new_title)
                    with head_c2:
                        conf = item.get("confidence", "Medium")
                        conf_cls = "badge-high" if conf.lower() == "high" else ("badge-low" if conf.lower() == "low" else "badge-medium")
                        st.markdown(f'<span class="badge-confidence {conf_cls}">{conf}</span>', unsafe_allow_html=True)
                    with head_c3:
                        app_val = st.checkbox("Include", value=item.get("approved", True), key=f"app_{idx}")
                        if app_val != item.get("approved"):
                            update_mom_item(idx, "approved", app_val)
                    with head_c4:
                        if st.button("Delete", key=f"del_card_{idx}", use_container_width=True):
                            delete_mom_item(idx)
                            st.rerun()

                    body_c1, body_c2, body_c3, body_c4 = st.columns([2.5, 3.4, 3.4, 1.7])
                    with body_c1:
                        st.caption("Source evidence")
                        eq = item.get("evidence_quote", "").strip() or "No quote attached to this row yet."
                        st.markdown(f'<div class="evidence-quote-box">{eq}</div>', unsafe_allow_html=True)
                    with body_c2:
                        new_dp = st.text_area(
                            "Discussion point",
                            value=item.get("discussion_point", ""),
                            height=170,
                            key=f"dp_{idx}",
                        )
                        if new_dp != item.get("discussion_point"):
                            update_mom_item(idx, "discussion_point", new_dp)
                    with body_c3:
                        new_ap = st.text_area(
                            "Action plan",
                            value=item.get("action_plan", ""),
                            height=170,
                            key=f"ap_{idx}",
                        )
                        if new_ap != item.get("action_plan"):
                            update_mom_item(idx, "action_plan", new_ap)
                    with body_c4:
                        pic_opts = ["Unassigned", "PRIME Philippines", "Client"] + all_attendees
                        curr_pic = item.get("person_in_charge", "Unassigned")
                        if curr_pic not in pic_opts:
                            pic_opts.append(curr_pic)
                        new_pic = st.selectbox(
                            "Owner",
                            options=pic_opts,
                            index=pic_opts.index(curr_pic) if curr_pic in pic_opts else 0,
                            key=f"pic_{idx}",
                        )
                        if new_pic != item.get("person_in_charge"):
                            update_mom_item(idx, "person_in_charge", new_pic)

                        current_due_date, is_tbd = parse_due_date_value(item.get("indicative_delivery_date", "TBD"))
                        tbd_key = f"dd_tbd_{idx}"
                        if tbd_key not in st.session_state:
                            st.session_state[tbd_key] = is_tbd
                        tbd_checked = st.checkbox("TBD", value=st.session_state[tbd_key], key=tbd_key)
                        picked_date = st.date_input(
                            "Due date",
                            value=current_due_date,
                            key=f"dd_{idx}",
                            disabled=tbd_checked,
                        )
                        new_due_value = "TBD" if tbd_checked else picked_date.strftime("%Y-%m-%d")
                        if new_due_value != item.get("indicative_delivery_date"):
                            update_mom_item(idx, "indicative_delivery_date", new_due_value)

                    row_warnings = check_row_guardrails(item, all_attendees)
                    for warning_text in row_warnings:
                        st.markdown(f'<div class="guardrail-alert">{warning_text}</div>', unsafe_allow_html=True)

        # Action Toolbar
        at1, at2 = st.columns([2, 8])
        with at1:
            if st.button("+ Add New Row", icon=":material/add:", use_container_width=True):
                add_mom_item()
                st.rerun()

        # Other Discussions / Executive Summary
        st.markdown("<hr style='margin:1rem 0 0.5rem 0;'>", unsafe_allow_html=True)
        st.markdown('<span class="playfair-label">Other Discussions & Peripheral Notes</span>', unsafe_allow_html=True)
        prior_other_discussions = st.session_state.get("other_discussions", "")
        st.session_state["other_discussions"] = st.text_area(
            "Other Discussions",
            value=st.session_state["other_discussions"],
            height=70,
            label_visibility="collapsed",
            placeholder="General announcements, warm-up banter, or peripheral alignment..."
        )
        if st.session_state["other_discussions"] != prior_other_discussions:
            mark_draft_updated("Summary notes updated")

        with st.expander("Advanced Review Tools", expanded=False):
            st.caption("Use these only when you want Echo to re-run the draft or make AI-assisted row edits.")
            if st.button("Re-run AI Matching", icon=":material/refresh:", use_container_width=True):
                if st.session_state["has_manual_edits"]:
                    st.warning("You have manual edits. Re-running will overwrite the current draft.")
                with st.spinner("Re-matching evidence with current transcript..."):
                    generate_minutes_draft(move_to_review=False)
                    st.success("Re-matched successfully!")
                    st.rerun()

            st.markdown("<hr style='margin:0.8rem 0;'>", unsafe_allow_html=True)
            st.caption("Ask questions or issue natural commands like: 'Assign row 2 to Cedtrix', 'Set row 1 date to Friday', or 'Delete row 3'.")
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            if not st.session_state["chat_history"]:
                st.markdown('<div class="chat-ai">Hello. I am Echo. You can instruct me to modify discussion points, assignees, or deadlines directly.</div>', unsafe_allow_html=True)
            else:
                for msg in st.session_state["chat_history"]:
                    if msg["role"] == "assistant":
                        st.markdown(f'<div class="chat-ai">{msg["content"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-user-wrap"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if prompt := st.chat_input("Instruct Echo to adjust items..."):
                st.session_state["chat_history"].append({"role": "user", "content": prompt})
                with st.spinner("Echo is updating items..."):
                    ans, act = ask_deepseek_with_mutation(st.session_state["transcript"], prompt, st.session_state["chat_history"], st.session_state["df"])
                    if act and isinstance(act, dict):
                        t_name = act.get("tool")
                        r_idx = int(act.get("row_index", 0))
                        flds = act.get("fields", {})
                        if t_name == "update_row" and 0 <= r_idx < len(st.session_state["mom_items"]):
                            for fk, fv in flds.items():
                                if fk == "Discussion Points": update_mom_item(r_idx, "discussion_point", str(fv))
                                elif fk == "Action Plan": update_mom_item(r_idx, "action_plan", str(fv))
                                elif fk == "Indicative Delivery Date": update_mom_item(r_idx, "indicative_delivery_date", str(fv))
                                elif fk == "Person-in-charge": update_mom_item(r_idx, "person_in_charge", str(fv))
                        elif t_name == "delete_row" and 0 <= r_idx < len(st.session_state["mom_items"]):
                            delete_mom_item(r_idx)
                        elif t_name == "add_row":
                            add_mom_item(
                                topic="New Item",
                                dp=flds.get("Discussion Points", ""),
                                ap=flds.get("Action Plan", ""),
                                dd=flds.get("Indicative Delivery Date", "TBD"),
                                pic=flds.get("Person-in-charge", "Unassigned")
                            )
                st.session_state["chat_history"].append({"role": "assistant", "content": ans})
                st.rerun()

# =============================================================
# STAGE 3: FINALIZE & EXPORT
# =============================================================
elif st.session_state["mom_stage"] == "export":
    # Header & Back button
    ex_top1, ex_top2 = st.columns([8, 2])
    with ex_top1:
        st.markdown('<div class="section-title">Export minutes</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-caption">Choose a template and download the final minutes package.</div>', unsafe_allow_html=True)
    with ex_top2:
        if st.button("← Back to Review", use_container_width=True):
            st.session_state["mom_stage"] = "review"
            st.rerun()

    # Consolidate meeting details dictionary
    start_fmt = st.session_state["meeting_start_time"].strftime("%I:%M %p")
    end_fmt = st.session_state["meeting_end_time"].strftime("%I:%M %p")
    time_range_str = f"{start_fmt} to {end_fmt}"
    client_display = st.session_state["meeting_client_name"].strip() or "Client"

    meeting_details_payload = {
        "date": st.session_state["meeting_date"].strftime("%B %d, %Y"),
        "time_range": time_range_str,
        "meeting_type": st.session_state.get("meeting_type", "Internal"),
        "location": st.session_state["meeting_location"].strip() or "PRIME Head Office",
        "company_name": client_display,
        "prime_attendees": st.session_state["meeting_selected_crd"],
        "external_attendees": [x.strip() for x in st.session_state["meeting_ext_attendees"].split(",") if x.strip()],
        "prep_name": st.session_state["meeting_prep_name"].strip(),
        "prep_desig": st.session_state["meeting_prep_desig"].strip(),
        "conf_name": st.session_state["meeting_conf_name"].strip(),
        "conf_desig": st.session_state["meeting_conf_desig"].strip()
    }

    if st.session_state["df"].empty:
        st.warning("No approved discussion items. Please go back and approve at least one item to enable export.")
    else:
        export_summary = build_review_summary()
        st.markdown(
            f'<div class="workflow-status"><strong>Ready to finalize:</strong> '
            f'{export_summary["approved_count"]} approved item(s), '
            f'{export_summary["actionable_count"]} action item(s), '
            f'{export_summary["missing_owner"]} missing owner(s), '
            f'{export_summary["missing_due"]} missing due date(s).<br>'
            f'<span style="color:#69727d; font-size:0.82rem;">Latest draft checkpoint: {st.session_state.get("draft_status_text", "No draft yet")}.</span></div>',
            unsafe_allow_html=True,
        )
        if export_summary["missing_owner"] or export_summary["missing_due"]:
            st.warning("You can still export now, but some action items are incomplete.")

        template_choice = st.segmented_control(
            "Export template",
            options=["Template 1", "Template 2"],
            default="Template 1" if st.session_state.get("selected_tpl", 1) == 1 else "Template 2",
        )
        st.session_state["selected_tpl"] = 1 if template_choice == "Template 1" else 2
        active_tpl = st.session_state["selected_tpl"]

        if active_tpl == 1:
            st.caption("Template 1 keeps the minutes in a single executive matrix.")
            docx_bio = export_to_word_template_1(st.session_state["df"], meeting_details_payload, st.session_state["other_discussions"])
            pdf_bio = export_to_pdf_template_1(st.session_state["df"], meeting_details_payload, st.session_state["other_discussions"])
        else:
            st.caption("Template 2 separates discussion notes from the action register.")
            docx_bio = export_to_word_template_2(st.session_state["df"], meeting_details_payload, st.session_state["other_discussions"])
            pdf_bio = export_to_pdf_template_2(st.session_state["df"], meeting_details_payload, st.session_state["other_discussions"])

        export_col1, export_col2 = st.columns(2)
        with export_col1:
            st.download_button(
                label="Download Word",
                icon=":material/description:",
                data=docx_bio,
                file_name=f"MOM_{client_display.replace(' ', '_')}_{datetime.date.today().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with export_col2:
            st.download_button(
                label="Download PDF",
                icon=":material/picture_as_pdf:",
                data=pdf_bio,
                file_name=f"MOM_{client_display.replace(' ', '_')}_{datetime.date.today().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with st.expander("Preview exported rows", expanded=False):
            st.dataframe(st.session_state["df"], use_container_width=True, hide_index=True)
