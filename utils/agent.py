"""Agentic Echo core: a declarative tool/action registry with cost controls.

Echo (the chatbot) can act across the app by calling these tools. Writes are
proposed to the user for approval; reads run immediately. Cost is bounded by
a max tool round-trips per request and a tokens budget.
"""
import logging

import streamlit as st

from utils.skills import load_prompt
from utils.db import get_supabase_client, fetch_meeting_archives
from utils.notebook_db import upsert_log

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cost controls (tunable)
# ---------------------------------------------------------------------------
MAX_TOOL_ROUNDTRIPS = 3          # max tool calls per single agent request
MAX_TOOL_RESULT_CHARS = 4000     # truncate tool results before re-feeding the model
AGENT_MODEL_LOCK = "fast"        # agent mode is locked to the cheap/fast model


# ---------------------------------------------------------------------------
# Tool implementations (self-contained; mirror the app's real data helpers)
# ---------------------------------------------------------------------------
def _tasks_table():
    client = get_supabase_client()
    return client.table("tasks") if client else None


def _search_meetings(params):
    rows = fetch_meeting_archives(limit=50)
    q = str(params.get("query") or "").strip().lower()
    if q:
        rows = [r for r in rows if q in str(r.get("client_name") or "").lower()
                or q in str(r.get("meeting_id") or "").lower()
                or q in str(r.get("summary_md") or "").lower()]
    out = []
    for r in rows[:10]:
        out.append({
            "meeting_id": r.get("meeting_id"),
            "client": r.get("client_name"),
            "date": str(r.get("meeting_date") or "")[:10],
            "summary": str(r.get("summary_md") or "")[:200],
        })
    return {"meetings": out, "count": len(out)}


def _create_task(params):
    t = _tasks_table()
    if t is None:
        return {"ok": False, "error": "supabase uninitialized"}
    r = t.insert({
        "title": str(params.get("title") or "").strip(),
        "description": str(params.get("description") or "").strip(),
        "assignee": str(params.get("assignee") or "").strip(),
        "status": "todo",
        "due_date": params.get("due_date") or None,
        "meeting_id": params.get("meeting_id") or None,
    }).execute()
    return {"ok": bool(r.data), "task_id": r.data[0].get("id") if r.data else None}


def _update_task_status(params):
    t = _tasks_table()
    if t is None:
        return {"ok": False, "error": "supabase uninitialized"}
    status = str(params.get("status") or "").strip()
    if status not in ("todo", "in_progress", "done"):
        return {"ok": False, "error": "invalid status"}
    r = t.update({"status": status}).eq("id", params.get("task_id")).execute()
    return {"ok": bool(r.data)}


def _delete_task(params):
    t = _tasks_table()
    if t is None:
        return {"ok": False, "error": "supabase uninitialized"}
    r = t.delete().eq("id", params.get("task_id")).execute()
    return {"ok": bool(r.data)}


def _log_daily_entry(params):
    from utils.auth import get_current_user
    user = get_current_user()
    user_id = user["id"] if user and user.get("id") else None
    import datetime
    date = params.get("date") or datetime.date.today()
    fields = {
        "client": str(params.get("client") or ""),
        "admin": str(params.get("admin") or ""),
        "adhoc": str(params.get("adhoc") or ""),
        "meeting": str(params.get("meeting") or ""),
    }
    if user_id:
        return {"ok": upsert_log(user_id, date, fields)}
    return {"ok": False, "error": "no user"}


def _save_meeting_minutes(params):
    return {"ok": False, "error": "save_meeting_minutes requires the minutes page flow; not routed from chat. Provide details and use Rendered To-Do. See admin consent."}


def _read_knowledge(params):
    from utils.db import fetch_echo_context
    ctx = fetch_echo_context()
    return {"knowledge": ctx}


def _add_knowledge(params):
    from utils.db import upsert_echo_context
    ok = upsert_echo_context(
        str(params.get("category") or "knowledge").strip(),
        str(params.get("key") or "").strip(),
        params.get("value"),
        int(params.get("priority") or 2),
    )
    return {"ok": ok}


def _web_search(params):
    from utils.echo_ai import _perform_web_search
    try:
        text, _sources = _perform_web_search(str(params.get("query") or ""))
        return {"result": (text or "")[:MAX_TOOL_RESULT_CHARS]}
    except Exception as e:  # noqa: BLE001
        logger.exception("web_search tool failed")
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
TOOLS = {
    "search_meetings": {
        "description": "Find meetings in the archives (optional query).",
        "params": {"query": "optional search text"},
        "handler": _search_meetings,
        "write": False,
    },
    "create_task": {
        "description": "Add a task to the board.",
        "params": {"title": "required", "assignee": "optional", "due_date": "optional", "meeting_id": "optional"},
        "handler": _create_task,
        "write": True,
    },
    "update_task_status": {
        "description": "Move a task: todo/in_progress/done.",
        "params": {"task_id": "required", "status": "required"},
        "handler": _update_task_status,
        "write": True,
    },
    "delete_task": {
        "description": "Remove a task.",
        "params": {"task_id": "required"},
        "handler": _delete_task,
        "write": True,
    },
    "log_daily_entry": {
        "description": "Write to the user's daily log.",
        "params": {"date": "optional", "client": "optional", "admin": "optional", "adhoc": "optional", "meeting": "optional"},
        "handler": _log_daily_entry,
        "write": True,
    },
    "save_meeting_minutes": {
        "description": "Persist approved minutes (routed through the minutes flow).",
        "params": {"details": "required"},
        "handler": _save_meeting_minutes,
        "write": True,
    },
    "read_knowledge": {"description": "Read the Echo knowledge base.", "params": {"query": "optional"}, "handler": _read_knowledge, "write": False},
    "add_knowledge": {"description": "Add to the knowledge base.", "params": {"category": "required", "key": "required", "value": "required"}, "handler": _add_knowledge, "write": True},
    "web_search": {"description": "Search the web.", "params": {"query": "required"}, "handler": _web_search, "write": False},
}


def tool_definitions_prompt() -> str:
    """Compact one-line tool list the model sees (keeps prompt tokens bounded)."""
    lines = []
    for name, spec in TOOLS.items():
        lines.append(f"- {name}({', '.join(k for k in spec['params'])}) : {spec['description']}")
    return "\n".join(lines)


def run_tool(name, params, user_id=None):
    """Execute a tool. Reads run immediately; writes are checked for RBAC by caller."""
    spec = TOOLS.get(name)
    if not spec:
        return {"ok": False, "error": f"unknown tool: {name}"}
    try:
        return spec["handler"](params or {})
    except Exception as e:  # noqa: BLE001
        logger.exception("agent tool %s failed", name)
        return {"ok": False, "error": str(e)}


def check_agent_access(user_id) -> bool:
    """RBAC gate: may this user run agent mode?"""
    from utils.auth import can_use_agent
    return can_use_agent(user_id) if user_id else False
