"""Token usage + rate limiting for Ask Echo (per-user, configurable).

Persistence:
  - usage_limits (user_id, daily_limit, weekly_limit) -> per-user budgets.
  - user_usage rows (user_id, tokens_used, created_at) -> telemetry + balance.

Defaults (when no usage_limits row): daily 50k / weekly 250k tokens.
All separation enforced in app code by user_id.
"""
import datetime
import logging

import streamlit as st

from utils.db import get_supabase_client

logger = logging.getLogger(__name__)

DEFAULT_DAILY_LIMIT = 50_000
DEFAULT_WEEKLY_LIMIT = 250_000


@st.cache_data(ttl=15, show_spinner=False)
def get_user_limits(user_id: str) -> dict:
    """Return {daily_limit, weekly_limit} for a user (defaults if unset)."""
    if not user_id:
        return {"daily_limit": DEFAULT_DAILY_LIMIT, "weekly_limit": DEFAULT_WEEKLY_LIMIT}
    client = get_supabase_client()
    if not client:
        return {"daily_limit": DEFAULT_DAILY_LIMIT, "weekly_limit": DEFAULT_WEEKLY_LIMIT}
    try:
        resp = client.table("usage_limits").select("*").eq("user_id", user_id).limit(1).execute()
        if resp.data:
            row = resp.data[0]
            return {
                "daily_limit": int(row.get("daily_limit") or DEFAULT_DAILY_LIMIT),
                "weekly_limit": int(row.get("weekly_limit") or DEFAULT_WEEKLY_LIMIT),
            }
    except Exception as e:  # noqa: BLE001
        logger.exception("get_user_limits failed: %s", e)
    return {"daily_limit": DEFAULT_DAILY_LIMIT, "weekly_limit": DEFAULT_WEEKLY_LIMIT}


def set_user_limits(user_id: str, daily_limit: int, weekly_limit: int) -> bool:
    """Upsert a per-user budget. Returns True on success."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        resp = (
            client.table("usage_limits")
            .upsert(
                {"user_id": user_id, "daily_limit": int(daily_limit), "weekly_limit": int(weekly_limit)},
                on_conflict="user_id",
            )
            .execute()
        )
        if resp.data:
            get_user_limits.clear()
            return True
        return False
    except Exception as e:  # noqa: BLE001
        logger.exception("set_user_limits failed: %s", e)
        err = str(e)
        if any(m in err for m in ("PGRST205", "Could not find the table", "relation .* does not exist")):
            st.error("The limits table is missing. Run `supabase/full_schema_ddl.sql` (creates `usage_limits`).")
        else:
            st.error(f"Could not save limits: {e}")
        return False


def record_usage(user_id: str, tokens_used: int, action: str = "chat") -> bool:
    """Write one user_usage row (telemetry). Called after each AI call."""
    client = get_supabase_client()
    if not user_id or not client:
        return False
    try:
        client.table("user_usage").insert(
            {
                "user_id": user_id,
                "tokens_used": int(tokens_used or 0),
                "event_type": action or "chat",
                "metadata": {"action": action or "chat"},
            }
        ).execute()
        _usage_caches.clear()
        return True
    except Exception as e:  # noqa: BLE001
        logger.exception("record_usage failed: %s", e)
        return False


@st.cache_data(ttl=15, show_spinner=False)
def _usage_caches(user_id: str):
    """Return parsed usage rows for a user (all time), cached briefly."""
    client = get_supabase_client()
    if not client:
        return []
    try:
        resp = client.table("user_usage").select("*").eq("user_id", user_id).execute()
        return resp.data if resp.data else []
    except Exception as e:  # noqa: BLE001
        logger.exception("_usage_caches failed: %s", e)
        return []


def _start_of_week(d: datetime.date) -> datetime.date:
    return d - datetime.timedelta(days=d.weekday())


def token_balance(user_id: str) -> dict:
    """Return usage + remaining vs limits for the current day and week."""
    rows = _usage_caches(user_id)
    today = datetime.date.today()
    week_start = _start_of_week(today)

    day_used = 0
    week_used = 0
    for r in rows:
        ts = r.get("created_at")
        if not ts:
            continue
        try:
            d = datetime.datetime.fromisoformat(str(ts).replace("Z", "+00:00")).date()
        except ValueError:
            continue
        tokens = int(r.get("tokens_used") or 0)
        if d == today:
            day_used += tokens
        if d >= week_start:
            week_used += tokens

    limits = get_user_limits(user_id)
    daily = int(limits["daily_limit"] or DEFAULT_DAILY_LIMIT)
    weekly = int(limits["weekly_limit"] or DEFAULT_WEEKLY_LIMIT)

    def remaining_for(used, limit):
        return max(0, limit - used)

    day_remaining = remaining_for(day_used, daily)
    week_remaining = remaining_for(week_used, weekly)
    # "remaining chats": simplistic—assume ~1k tokens per chat turn
    est_per_chat = 1000
    day_chats = day_remaining // est_per_chat
    week_chats = week_remaining // est_per_chat

    return {
        "day_used": day_used,
        "day_limit": daily,
        "day_remaining": day_remaining,
        "week_used": week_used,
        "week_limit": weekly,
        "week_remaining": week_remaining,
        "day_chats_remaining": max(0, day_chats),
        "week_chats_remaining": max(0, week_chats),
    }


def check_rate_limit(user_id: str) -> dict:
    """Return {'allowed': bool, 'why': str|None}. Enforce before a chat query."""
    if not user_id:
        return {"allowed": False, "why": "Unauthenticated session. Please log in."}
    bal = token_balance(user_id)
    if bal["day_remaining"] <= 0:
        return {"allowed": False, "why": "Daily token limit reached. Please contact the developer to increase your limit."}
    if bal["week_remaining"] <= 0:
        return {"allowed": False, "why": "Weekly token limit reached. Please contact the developer to increase your limit."}
    return {"allowed": True, "why": None}
