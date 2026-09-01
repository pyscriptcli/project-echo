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
        self.assertIn("--echo-canvas: #ECEBDE", captured["html"])
        self.assertIn("var(--echo-canvas)", captured["html"])
        self.assertIn("border-radius: var(--echo-radius)", captured["html"])
        # The rendered CSS must still contain literal CSS braces (proving no f-string mangling)
        self.assertIn(".stButton > button,", captured["html"])
        self.assertIn("border-radius: 0 !important;\n", captured["html"])

        # New stone-ramp + navy palette tokens
        self.assertIn("--echo-ink: #0D1B3E;", captured["html"])
        self.assertIn("--echo-button: #D7D3BF;", captured["html"])
        self.assertIn("--echo-canvas: #ECEBDE;", captured["html"])
        self.assertIn("--echo-borders: #C1BAA1;", captured["html"])
        self.assertIn("--echo-accent: #A59D84;", captured["html"])
        # Buttons: #D7D3BF flat, navy text, NO border
        self.assertIn("background-color: var(--echo-button) !important;", captured["html"])
        self.assertNotIn("--echo-accent) !important;\n    color:", captured["html"])
        self.assertNotIn("#C9B59C", captured["html"])
        self.assertNotIn("#412D15", captured["html"])


if __name__ == "__main__":
    unittest.main()
