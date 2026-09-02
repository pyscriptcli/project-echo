# documents_template

Repository templates for the **Documents** page (`pages/8_documents.py`).

Drop PPTX/DOCX template files here named `template_*.pptx` / `template_*.docx`
(e.g. `template_quote.pptx`). They appear under **Templates** in the Documents
page and are protected from deletion inside the app.

Templates uploaded through the app are saved to `stored_templates/` at the
project root (gitignored).

## Format guidance (DOCX-first)

Most documents are **text-only**, so DOCX is the primary template format:
placeholders use `{{TOKEN}}` and are filled natively (paragraphs + tables).
The page exports the filled DOCX as-is, plus an optional **PDF** (`Download PDF`
button) that auto-detects a converter — `docx2pdf` (Microsoft Word) if
installed, otherwise LibreOffice (`soffice --headless --convert-to pdf`).

Use **PPTX** templates when a document needs **Image or Map placeholders** — the
page's image/map support is PPTX-only (DOCX fills text only).

## Storage

Templates are kept as **committed files in this folder (GitHub), not in the
database** — they are static, version-controlled brand assets (typically
well under the 3–5 MB ceiling). The DB is reserved for runtime user data.

