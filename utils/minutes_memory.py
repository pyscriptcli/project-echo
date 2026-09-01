"""Per-user 'Minutes Memory' persistence for the meeting-processing flow.

Stores approved Minutes-of-Meeting output in the `minutes_memory` table so
Echo can learn how each user wants their minutes formatted (few-shot style
learning). Separation enforced in app code via user_id (a uuid).
"""
import json
import logging

import streamlit as st

from utils.db import get_supabase_client

logger = logging.getLogger(__name__)


@st.cache_data(ttl=30, show_spinner=False)
def fetch_recent_minutes(user_id: str, limit: int = 5) -> list:
    """Return the user's most recent approved minutes-memory rows."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = (
            client.table("minutes_memory")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data if resp and resp.data else []
    except Exception as e:
        logger.exception("fetch_recent_minutes failed: %s", e)
        st.warning(f"Could not load minutes memory: {e}")
        return []


def store_approved_minutes(
    user_id: str,
    meeting_id: str,
    approved_items: list,
    other_discussions: str,
    client_name: str = "",
) -> bool:
    """Save an approved meeting's final minutes table as a style exemplar."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        resp = (
            client.table("minutes_memory")
            .insert(
                {
                    "user_id": user_id,
                    "meeting_id": meeting_id,
                    "client_name": client_name,
                    "approved_items": json.dumps(approved_items),
                    "other_discussions": other_discussions,
                }
            )
            .execute()
        )
        if resp.data:
            fetch_recent_minutes.clear()
            return True
        return False
    except Exception as e:
        logger.exception("store_approved_minutes failed: %s", e)
        st.error(f"Could not save minutes memory: {e}")
        return False


def build_style_examples(user_id: str, limit: int = 3) -> str:
    """Build a few-shot 'style examples' block from recent approved minutes.

    Returns an empty string if there is no memory yet, so callers can skip
    style injection cleanly. Output is appended to the minutes prompt under
    the {{MEMORY_EXAMPLES}} token.
    """
    rows = fetch_recent_minutes(user_id, limit=limit)
    if not rows:
        return ""

    blocks = []
    for i, row in enumerate(rows, 1):
        items = row.get("approved_items") or []
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except Exception:
                items = []
        client = row.get("client_name") or "past meeting"
        other = row.get("other_discussions") or ""
        item_lines = []
        for it in items[:6]:
            if not isinstance(it, dict):
                continue
            dp = it.get("Discussion Points") or it.get("discussion_point") or ""
            ap = it.get("Action Plan") or it.get("action_plan") or ""
            pic = it.get("Person-in-charge") or it.get("person_in_charge") or ""
            due = it.get("Indicative Delivery Date") or it.get("indicative_delivery_date") or ""
            item_lines.append(f"- {dp} | Action: {ap} | PIC: {pic} | Due: {due}")
        blocks.append(
            f"Example {i} ({client}):\n"
            + ("\n".join(item_lines) if item_lines else "(no items)")
            + (f"\nOther discussions: {other}" if other else "")
        )

    return (
        "\n\nThese are examples of how I like my minutes to look. Match this "
        "structure, tone, and level of detail when formatting the current meeting:\n\n"
        + "\n\n".join(blocks)
    )


def clear_memory_cache():
    fetch_recent_minutes.clear()
