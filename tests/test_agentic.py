"""Smoke tests for the agentic Echo core + RBAC + skills (no live Supabase).

Run: python -m unittest discover -s tests -p "test_*.py"
These import the pure modules; DB-touching paths are stubbed/injected.
"""
import unittest


class AgentCoreTests(unittest.TestCase):
    def test_tools_registry_shape(self):
        from utils.agent import TOOLS, tool_definitions_prompt
        self.assertIn("create_task", TOOLS)
        self.assertIn("search_meetings", TOOLS)
        self.assertIn("log_daily_entry", TOOLS)
        for name, spec in TOOLS.items():
            self.assertIn("handler", spec)
            self.assertIn("write", spec)
        prompt = tool_definitions_prompt()
        self.assertIn("create_task", prompt)
        self.assertIn("search_meetings", prompt)

    def test_run_tool_unknown(self):
        from utils.agent import run_tool
        out = run_tool("does_not_exist", {})
        self.assertFalse(out.get("ok"))
        self.assertIn("unknown tool", out.get("error", ""))


class SkillTests(unittest.TestCase):
    def test_skills_load_and_substitute(self):
        from utils.skills import load_prompt
        c = load_prompt("echo_chat", context="ctx")
        a = load_prompt("agent_controller", context="ctx")
        self.assertNotIn("{{", c)
        self.assertNotIn("{{", a)
        self.assertIn("You are Echo", c)
        self.assertIn("create_task", a)
        self.assertIn("search_meetings", a)

    def test_existing_skills_still_load(self):
        from utils.skills import load_prompt
        for n in ["echo_analyst", "data_extractor", "global_analyst"]:
            self.assertTrue(load_prompt(n))


class RBACHelperTests(unittest.TestCase):
    def test_can_use_agent_empty(self):
        from utils.auth import can_use_agent
        self.assertFalse(can_use_agent(None))


if __name__ == "__main__":
    unittest.main()
