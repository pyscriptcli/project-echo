"""Regression tests for the Documents page (pages/8_documents.py)."""
import unittest


class DocumentsIntegrationTests(unittest.TestCase):
    def test_page_compiles(self):
        """pages/8_documents.py must import without syntax errors (py_compile)."""
        import py_compile

        py_compile.compile("pages/8_documents.py", doraise=True)

    def test_imports_are_private_to_the_app(self):
        """The page must not carry standalone-only imports or fall back to a
        hardcoded local storage dir (it should use the repo's documents_template/
        and stored_templates/)."""
        with open("pages/8_documents.py", encoding="utf-8") as f:
            source = f.read()

        # Standalone imports the app build does not use should be gone.
        for unused in ("subprocess", "tempfile", "base64", "traceback"):
            self.assertNotIn(f"import {unused}", source)

        # Storage must point at the committed repo templates folder, not a
        # past-project hardcoded path or a standalone "OpenFlux" identity.
        self.assertIn("documents_template", source)
        self.assertIn("stored_templates", source)
        self.assertNotIn("OpenFlux", source)

    def test_local_only_and_native_token_presence(self):
        """The page must be wired into the native Echo shell (require_login/
        setup_page_layout), carry the local-only notice, and use Echo tokens."""
        with open("pages/8_documents.py", encoding="utf-8") as f:
            source = f.read()

        self.assertIn("require_login()", source)
        self.assertIn("setup_page_layout()", source)
        self.assertIn("Documents are generated and exported locally", source)
        # Native Echo palette tokens — not the past project's #003366-era style.
        self.assertIn("#0D1B3E", source)
        self.assertIn("#D7D3BF", source)
        self.assertIn("#A59D84", source)
        self.assertIn("#C1BAA1", source)
        # No DB write should exist anywhere in the page.
        self.assertNotIn("import supabase", source)
        self.assertNotIn("utils.db", source)

    def test_caching_applied_to_expensive_helpers(self):
        """Filesystem reads, placeholder parsing, and map-tile fetches are cached."""
        with open("pages/8_documents.py", encoding="utf-8") as f:
            source = f.read()

        self.assertIn("@st.cache_data", source)
        self.assertIn("def get_saved_templates()", source)
        self.assertIn("def load_template_from_file(template_name)", source)
        self.assertIn("def extract_placeholders(template_bytes, template_type)", source)
        self.assertIn("def fetch_tile_with_retry(url_template, zoom, x, y, max_retries=3)", source)


if __name__ == "__main__":
    unittest.main()
