"""
Project Echo — Global Audit Log.

Records key system events (transcription, save, login, chat, etc.) to the
Supabase `audit_log` table. Every page can import and call ``audit_log()``
to capture what happened for debugging and the Admin Console audit tab.

Table schema (created by migration / DDL):

    CREATE TABLE audit_log (
        id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        timestamp   TIMESTAMPTZ DEFAULT now(),
        user_id     UUID REFERENCES admin_users(id),
        username    TEXT,
        event_type  TEXT NOT NULL,      -- e.g. 'transcription', 'save_meeting', 'login'
        details     TEXT,               -- human-readable description
        status      TEXT NOT NULL,      -- 'ok' | 'error'
        duration_ms INTEGER,
        page        TEXT,
        endpoint    TEXT
    );
    CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
    CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
    CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
    CREATE INDEX idx_audit_log_status ON audit_log(status);
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def audit_log(
    event_type: str,
    details: str = "",
    user_id: str | None = None,
    username: str | None = None,
    status: str = "ok",
    duration_ms: int | None = None,
    page: str | None = None,
    endpoint: str | None = None,
) -> bool:
    """Insert a single row into the ``audit_log`` table.

    Returns True on success, False on failure (failure is logged but never
    raises — audit must never block the calling operation).
    """
    if not event_type:
        return False

    try:
        from utils.db import get_supabase_client
        client = get_supabase_client()
        if not client:
            logger.warning("audit_log: Supabase client unavailable, cannot log '%s'", event_type)
            return False

        payload = {
            "user_id": user_id,
            "username": username,
            "event_type": event_type,
            "details": details[:2000] if details else "",   # cap at 2k chars
            "status": status,
            "duration_ms": duration_ms,
            "page": page[:200] if page else None,
            "endpoint": endpoint[:200] if endpoint else None,
        }

        client.table("audit_log").insert(payload).execute()
        return True

    except Exception as e:
        logger.exception("audit_log failed for '%s': %s", event_type, e)
        return False


def fetch_audit_logs(
    limit: int = 200,
    event_type: str | None = None,
    user_id: str | None = None,
    status: str | None = None,
    days: int | None = None,
) -> list:
    """Fetch recent audit log entries with optional filters.

    Returns a list of dicts ordered by timestamp descending.
    """
    try:
        from utils.db import get_supabase_client
        client = get_supabase_client()
        if not client:
            return []

        q = client.table("audit_log").select("*")

        if days:
            q = q.gte("timestamp", f"now() - interval '{days} days'")
        if event_type:
            q = q.eq("event_type", event_type)
        if user_id:
            q = q.eq("user_id", user_id)
        if status:
            q = q.eq("status", status)

        q = q.order("timestamp", desc=True).limit(limit)
        resp = q.execute()
        return resp.data if resp and resp.data else []

    except Exception as e:
        logger.exception("fetch_audit_logs failed: %s", e)
        return []


def list_event_types() -> list:
    """Return distinct event_type values from the audit_log table."""
    try:
        from utils.db import get_supabase_client
        client = get_supabase_client()
        if not client:
            return []
        resp = client.table("audit_log").select("event_type").execute()
        if resp and resp.data:
            return sorted(set(r["event_type"] for r in resp.data if r.get("event_type")))
        return []
    except Exception as e:
        logger.exception("list_event_types failed: %s", e)
        return []