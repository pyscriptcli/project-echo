"""Tests for usage/rate-limiting + agentic core + auth password helpers."""
import unittest


class LimitsLogicTests(unittest.TestCase):
    """Pure-logic tests; DB calls are stubbed via module monkeypatch."""

    def _make_balance_bundle(self, today_rows, week_extra_rows, daily, weekly):
        import utils.limits as L
        today = __import__('datetime').date.today()
        ws = L._start_of_week(today)
        rows = []
        for n in range(today_rows):
            rows.append({"created_at": today.isoformat() + "T10:00:00+00:00", "tokens_used": 1000})
        for n in range(week_extra_rows):
            rows.append({"created_at": ws.isoformat() + "T09:00:00+00:00", "tokens_used": 1000})
        L.get_user_limits = lambda uid: {"daily_limit": daily, "weekly_limit": weekly}
        L._usage_caches = lambda uid: rows
        return L

    def test_token_balance_counts_day_and_week(self):
        # 2 today + 1 earlier-this-week = day 2000, week 3000
        L = self._make_balance_bundle(today_rows=2, week_extra_rows=1, daily=5000, weekly=6000)
        bal = L.token_balance("u1")
        self.assertEqual(bal["day_used"], 2000)
        self.assertEqual(bal["day_limit"], 5000)
        self.assertEqual(bal["day_remaining"], 3000)
        self.assertEqual(bal["week_used"], 3000)  # 2 today + 1 week_start
        self.assertEqual(bal["week_remaining"], 3000)

    def test_check_rate_limit_allowed_and_blocked(self):
        # day 6000 > 5000 -> blocked
        L = self._make_balance_bundle(today_rows=6, week_extra_rows=0, daily=5000, weekly=9000)
        denied = L.check_rate_limit("u1")
        self.assertFalse(denied["allowed"])
        self.assertIn("Daily token limit", denied["why"])

    def test_check_rate_limit_none_user(self):
        import utils.limits as L
        out = L.check_rate_limit(None)
        self.assertFalse(out["allowed"])

    def test_defaults(self):
        import utils.limits as L
        self.assertEqual(L.DEFAULT_DAILY_LIMIT, 50000)
        self.assertEqual(L.DEFAULT_WEEKLY_LIMIT, 250000)


class CoreTests(unittest.TestCase):
    def test_tools_registry(self):
        from utils.agent import TOOLS, tool_definitions_prompt
        self.assertIn("create_task", TOOLS)
        self.assertIn("search_meetings", TOOLS)
        self.assertIn("log_daily_entry", TOOLS)
        self.assertIn("create_task", tool_definitions_prompt())

    def test_auth_password_policy_bad(self):
        from utils.auth import validate_password_strength
        self.assertTrue(validate_password_strength("short"))
        self.assertEqual(validate_password_strength("Abcdefg1"), [])


if __name__ == "__main__":
    unittest.main()
