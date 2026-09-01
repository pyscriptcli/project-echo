"""Per-user Supabase persistence for the Notebook screen.

Enforces per-user separation in application code (service-role key, no RLS):
every read writes filters/inserts by user_id. Tables are defined in
supabase/notebook_ddl.sql (notepad_docs, daily_logs).
"""
import datetime
import logging

import streamlit as st

from utils.db import get_supabase_client

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Notepad docs
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def fetch_docs(user_id: str) -> list:
    """Return all notepad_docs rows for a user, newest-updated first."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = (
            client.table("notepad_docs")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return resp.data if resp and resp.data else []
    except Exception as e:
        logger.exception("fetch_docs failed: %s", e)
        st.warning(f"Could not load your notes: {e}")
        return []


def upsert_doc(user_id: str, doc_id: str, title: str, content: str):
    """Insert or update a notepad_docs row for the user. Returns bool."""
    client = get_supabase_client()
    if not client:
        st.error("Supabase client not initialized.")
        return False
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    try:
        resp = (
            client.table("notepad_docs")
            .upsert(
                {
                    "id": doc_id,
                    "user_id": user_id,
                    "title": title,
                    "content": content,
                    "updated_at": now,
                },
                on_conflict="id",
            )
            .execute()
        )
        if resp.data:
            fetch_docs.clear()
            return True
        logger.error("notepad_docs upsert returned no rows: %s", resp)
        return False
    except Exception as e:
        logger.exception("upsert_doc failed: %s", e)
        st.error(f"Could not save note: {e}")
        return False


def delete_doc(user_id: str, doc_id: str) -> bool:
    """Delete a notepad_docs row (scoped by user_id)."""
    client = get_supabase_client()
    if not client:
        st.error("Supabase client not initialized.")
        return False
    try:
        resp = (
            client.table("notepad_docs")
            .delete()
            .eq("id", doc_id)
            .eq("user_id", user_id)
            .execute()
        )
        if resp.data:
            fetch_docs.clear()
            return True
        return False
    except Exception as e:
        logger.exception("delete_doc failed: %s", e)
        st.error(f"Could not delete note: {e}")
        return False


# ---------------------------------------------------------------------------
# Daily logs
# ---------------------------------------------------------------------------
def _log_payload(log_date, fields: dict) -> dict:
    return {
        "log_date": log_date.isoformat() if isinstance(log_date, (datetime.date, datetime.datetime)) else str(log_date),
        "client": fields.get("client", ""),
        "admin": fields.get("admin", ""),
        "adhoc": fields.get("adhoc", ""),
        "meeting": fields.get("meeting", ""),
    }


@st.cache_data(ttl=30, show_spinner=False)
def fetch_logs_in_range(user_id: str, start, end) -> list:
    """Return the user's daily_logs rows within [start, end]."""
    client = get_supabase_client()
    if not client:
        return []
    start_iso = start.isoformat()
    end_iso = end.isoformat()
    try:
        resp = (
            client.table("daily_logs")
            .select("*")
            .eq("user_id", user_id)
            .gte("log_date", start_iso)
            .lte("log_date", end_iso)
            .execute()
        )
        return resp.data if resp and resp.data else []
    except Exception as e:
        logger.exception("fetch_logs_in_range failed: %s", e)
        st.warning(f"Could not load your daily log: {e}")
        return []


def upsert_log(user_id: str, log_date, fields: dict) -> bool:
    """Insert or update the (user_id, log_date) daily_logs row. Auto-saves on edit."""
    client = get_supabase_client()
    if not client:
        st.error("Supabase client not initialized.")
        return False
    try:
        payload = _log_payload(log_date, fields)
        payload["user_id"] = user_id
        resp = (
            client.table("daily_logs")
            .upsert(payload, on_conflict="user_id,log_date")
            .execute()
        )
        if resp.data:
            fetch_logs_in_range.clear()
            return True
        logger.error("daily_logs upsert returned no rows: %s", resp)
        return False
    except Exception as e:
        logger.exception("upsert_log failed: %s", e)
        st.error(f"Could not save your daily log: {e}")
        return False
