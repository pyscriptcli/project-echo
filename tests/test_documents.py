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

        # Standalone top-level imports the app build does not use should be gone.
        # (subprocess/tempfile now legitimately appear inside docx_bytes_to_pdf.)
        for sig in ("import io\nimport subprocess", "import base64", "import traceback"):
            self.assertNotIn(sig, source)

        # Storage must point at the committed repo templates folder, not a
        # past-project hardcoded path or a standalone "OpenFlux" identity.
        self.assertIn("documents_template", source)
        self.assertIn("stored_templates", source)
        self.assertNotIn("OpenFlux", source)

    def test_local_only_and_native_token_presence(self):
        """The page must be wired into the native Echo shell (require_login/
        setup_page_layout), carry the local-only notice, and use the dark navy/gold tokens."""
        with open("pages/8_documents.py", encoding="utf-8") as f:
            source = f.read()

        self.assertIn("require_login()", source)
        self.assertIn("setup_page_layout()", source)
        self.assertIn("Documents are generated and exported locally", source)
        # Native dark navy & gold palette tokens.
        self.assertIn("rgba(16, 30, 56", source)
        self.assertIn("#101E38", source)
        self.assertIn("#D4AF37", source)
        self.assertIn("#F5F5F0", source)
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

    def test_docx_to_pdf_export_wired(self):
        """The .docx download flow must offer a PDF export and use the shared
        helper, never writing to the DB."""
        with open("pages/8_documents.py", encoding="utf-8") as f:
            source = f.read()

        self.assertIn("def docx_bytes_to_pdf(docx_bytes)", source)
        self.assertIn('label="Download PDF"', source)
        self.assertIn('get_download_filename(base_template_name, "pdf")', source)
        self.assertIn("download_pdf_disabled", source)


class DocxToPdfHelperTests(unittest.TestCase):
    def test_raises_clear_error_when_no_converter(self):
        """With neither docx2pdf nor LibreOffice available, the helper must raise
        a RuntimeError explaining what's missing (not crash obscurely)."""
        import importlib.util
        import sys

        # Cannot import the page module without a Streamlit runtime; instead test
        # the pure logic by extracting the function source and compiling it.
        with open("pages/8_documents.py", encoding="utf-8") as f:
            source = f.read()
        marker = "def docx_bytes_to_pdf(docx_bytes):"
        start = source.index(marker)
        # Include a minimal header so exec has the pieces the function uses.
        ns = {"os": __import__("os")}
        head = "import os\n"
        exec(head + source[start:source.index("\n\ndef ", start)], ns)
        fn = ns["docx_bytes_to_pdf"]

        # Force the no-engine path: make docx2pdf import fail and no soffice on PATH.
        sys.modules["docx2pdf"] = None  # importlib.import_module("docx2pdf") raises ImportError
        import shutil
        orig_which = shutil.which
        shutil.which = lambda name, **kw: None
        try:
            with self.assertRaises(RuntimeError) as ctx:
                fn(b"%PDF-fake-minimal-docx-bytes")
            self.assertIn("docx2pdf", str(ctx.exception))
            self.assertIn("LibreOffice", str(ctx.exception))
            self.assertIn("soffice", str(ctx.exception))
        finally:
            shutil.which = orig_which
            sys.modules.pop("docx2pdf", None)


if __name__ == "__main__":
    unittest.main()
