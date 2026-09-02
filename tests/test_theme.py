"""Regression tests for components/theme.inject_global_css (f-string NameError bug +
dark navy & gold design-system tokens)."""
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

        html = captured["html"]
        self.assertIn("<style>", html)
        # Cormorant Garamond + Montserrat are loaded from Google Fonts
        self.assertIn("Cormorant+Garamond", html)
        self.assertIn("Montserrat", html)
        self.assertIn("var(--echo-canvas)", html)
        self.assertIn("border-radius: var(--echo-radius)", html)
        # The rendered CSS must still contain literal CSS braces (proving no f-string mangling)
        self.assertIn(".stButton > button,", html)
        self.assertIn("border-radius: 0 !important;\n", html)

    def test_theme_tokens(self):
        """The shared theme exposes the gray-azure / navy / dark-gray palette."""
        import components.theme as theme

        captured = {}
        with mock.patch.object(theme.st, "markdown", side_effect=lambda html, **kw: captured.update(html=html)):
            theme.inject_global_css()

        html = captured["html"]
        # Gray-azure canvas, deep-navy ink, dark-gray buttons
        self.assertIn("--echo-canvas: #A3ACB5;", html)
        self.assertIn("--echo-ink: #0D1B3E;", html)
        self.assertIn("--echo-button: #333333;", html)
        self.assertIn("--echo-gold: #333333;", html)
        # Bebas Neue loaded and used for numbers
        self.assertIn("Bebas+Neue", html)
        self.assertIn("--echo-number:", html)
        # Buttons: dark-gray bg, white text
        self.assertIn("background-color: var(--echo-button) !important;", html)
        self.assertIn("color: #FFFFFF !important;", html)

    def test_unified_page_header_hierarchy(self):
        """Page headers use a single Cormorant Garamond hierarchy (title/subtitle) and
        existing header classes are aliased to it."""
        import components.theme as theme

        captured = {}
        with mock.patch.object(theme.st, "markdown", side_effect=lambda html, **kw: captured.update(html=html)):
            theme.inject_global_css()

        html = captured["html"]
        # Eyebrow -> title -> subtitle
        self.assertIn(".page-eyebrow", html)
        self.assertIn(".page-title", html)
        self.assertIn(".page-subtitle", html)
        # Cormorant Garamond for titles
        self.assertIn("font-family: var(--echo-title) !important;", html)
        # Existing classes are aliased so all pages match
        for cls in (".section-title", ".docs-title", ".notebook-title", ".view-header"):
            self.assertIn(cls, html)

    def test_pages_use_shared_header_classes_no_old_palette(self):
        """Every top-level page uses the shared header classes and none re-assert the
        old light-theme canvas. Main-content pages shouldn't reference the legacy cream."""
        import os

        proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pages = [
            "app.py",
            "pages/0_admin.py",
            "pages/1_minutes_of_the_meeting.py",
            "pages/2_meeting_details.py",
            "pages/3_echo_ai.py",
            "pages/4_tasks.py",
            "pages/6_notebook.py",
            "pages/8_documents.py",
        ]
        header_classes = ("page-eyebrow", "section-title", "docs-title", "notebook-title", "page-title")
        header_mechanisms = header_classes + ("<h1", "<h2", "<h3", "st.title", "render_echo_chat(")
        for rel in pages:
            with open(os.path.join(proj, rel), encoding="utf-8") as f:
                src = f.read()
            # Pages must load the shared theme either via the full layout or by
            # injecting the theme directly (0_admin.py has its own sidebar).
            self.assertTrue(
                "setup_page_layout()" in src or "inject_global_css()" in src,
                f"{rel} must apply the shared theme",
            )
            self.assertTrue(
                any(hc in src for hc in header_mechanisms),
                f"{rel} must render at least one page header",
            )
            # Legacy light cream canvas must not be forced in the main app pages.
            self.assertNotIn("#ECEBDE", src, f"{rel} must not re-assert the legacy cream canvas")


if __name__ == "__main__":
    unittest.main()
