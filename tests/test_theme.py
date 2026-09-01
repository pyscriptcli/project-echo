"""Regression test for components/theme.inject_global_css (f-string NameError bug)."""
import unittest
from unittest import mock


class ThemeTests(unittest.TestCase):
    def test_inject_global_css_builds_without_nameerror(self):
        """The CSS body must NOT be an f-string (CSS braces like `button {` would be
        misparsed as f-string expressions -> NameError/SyntaxError)."""
        import components.theme as theme

        captured = {}
        with mock.patch.object(theme.st, "markdown", side_effect=lambda html, **kw: captured.update(html=html)):
            theme.inject_global_css()

        self.assertIn("<style>", captured["html"])
        self.assertIn("--echo-canvas: #F5F1E8", captured["html"])
        self.assertIn("var(--echo-canvas)", captured["html"])
        self.assertIn("border-radius: var(--echo-radius)", captured["html"])
        # The rendered CSS must still contain literal CSS braces (proving no f-string mangling)
        self.assertIn(".stButton > button,", captured["html"])
        self.assertIn("border-radius: 0 !important;\n", captured["html"])

        # Hotfix spec: NO gridlines — clean flat cream canvas
        self.assertIn("background-color: var(--echo-canvas) !important;", captured["html"])
        self.assertNotIn("linear-gradient(to right", captured["html"])
        self.assertNotIn("background-size:", captured["html"])
        # Hotfix spec: uniform compact charcoal/gold buttons
        self.assertIn("font-size: 0.72rem !important;", captured["html"])
        self.assertIn("min-height: 26px !important;", captured["html"])
        self.assertIn("border: 1px solid var(--echo-gold) !important;", captured["html"])


if __name__ == "__main__":
    unittest.main()
