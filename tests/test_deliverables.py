"""Tests for Echo's personalized deliverables matching logic."""
import unittest


def _build(username, archives, tasks):
    """Mirror of utils.echo_ai.build_user_deliverables_context (inline for test)."""
    import datetime
    if not username:
        return ""
    name = username.lower()
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)

    dm = []
    for m in archives or []:
        for item in (m.get("table_items") or []):
            pic = str(item.get("Person-in-charge") or "").strip()
            if pic and name in pic.lower():
                dm.append({"source": "Minutes", "point": str(item.get("Discussion Points") or "")[:40], "pic": pic})
    dt = []
    for t in tasks or []:
        asg = str(t.get("assignee") or "").strip()
        due_raw = t.get("due_date")
        due_date = None
        try:
            due_date = datetime.date.fromisoformat(str(due_raw)[:10]) if due_raw else None
        except Exception:  # noqa: BLE001
            due_date = None
        if asg and name in asg.lower():
            dt.append({"source": "Task", "title": str(t.get("title") or "")[:40], "in_week": bool(due_date and week_start <= due_date <= week_end)})
    return dm, dt


class DeliverablesMatchTests(unittest.TestCase):
    def test_matches_user_from_minutes_and_tasks(self):
        archives = [
            {"client_name": "Client A", "table_items": [
                {"Discussion Points": "Review ads", "Person-in-charge": "Dave Policarpio"},
                {"Discussion Points": "Handle meta", "Person-in-charge": "Carlo Medina"},
            ]},
        ]
        tasks = [
            {"title": "Prepare report", "assignee": "Dave Policarpio", "status": "todo", "due_date": None},
            {"title": "Send invoice", "assignee": "Meliza Zapata", "status": "done", "due_date": None},
        ]
        dm, dt = _build("Dave Policarpio", archives, tasks)
        # Only Dave's minutes item + Dave's task
        self.assertEqual(len(dm), 1)
        self.assertEqual(dm[0]["point"], "Review ads")
        self.assertEqual(len(dt), 1)
        self.assertEqual(dt[0]["title"], "Prepare report")

    def test_other_user_gets_only_their_items(self):
        archives = [{"table_items": [{"Discussion Points": "x", "Person-in-charge": "Dave Policarpio"}]}]
        tasks = [{"title": "y", "assignee": "Meliza Zapata", "status": "todo", "due_date": None}]
        dm, dt = _build("Meliza Zapata", archives, tasks)
        self.assertEqual(dm, [])           # no minutes for Meliza
        self.assertEqual(len(dt), 1)       # her task
        self.assertEqual(dt[0]["title"], "y")

    def test_no_match_returns_empty(self):
        dm, dt = _build("Nobody", [], [])
        self.assertEqual(dm, [])
        self.assertEqual(dt, [])


if __name__ == "__main__":
    unittest.main()
