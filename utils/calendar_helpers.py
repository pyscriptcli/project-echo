# utils/calendar_helpers.py
from datetime import date, datetime
from utils.db import get_supabase_client, fetch_meeting_archives

def fetch_calendar_events(start_date: date, end_date: date, assignee_filter: str = None, status_filter: list = None, meeting_filter: str = None):
    """
    Returns merged events from tasks + meeting action items.
    Each event dict:
    {
        "id": str,                     # task.id or f"meeting_{meeting_id}_{idx}"
        "title": str,                  # task.title or action_plan
        "date": date,                  # due_date or delivery_date
        "source": "task" | "meeting_action",
        "status": str,                 # for tasks: todo/in_progress/done
        "assignee": str,               # person-in-charge
        "meeting_id": str | None,      # linked meeting
        "color": str,                  # hex based on status/source
        "overdue": bool,
        "is_today": bool
    }
    """
    # 1. Fetch tasks with filters applied (assignee, status, meeting_id)
    # 2. Fetch meeting action items (from meeting_archives → table_items)
    # 3. Merge, apply date range, compute overdue/today flags
    pass
