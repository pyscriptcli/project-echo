"""components/doc_fonts.py — reportlab/docx brand-font support.

Registers the bundled Cormorant Garamond + Montserrat TTFs (kept under
.reasonix/skills/primephilippines-design/fonts/) with reportlab so exported
PDFs embed the brand faces, and exposes the Word family names for python-docx.
"""
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_ROOT = os.path.join(
    _HERE, "..", ".reasonix", "skills", "primephilippines-design", "fonts"
)

# Registered reportlab (embedded) font names
FONT_HEAD = "CormorantGaramond-Regular"   # headings/display
FONT_HEAD_BOLD = "CormorantGaramond-Bold"
FONT_BODY = "Montserrat-Regular"           # body/UI
FONT_BODY_BOLD = "Montserrat-Bold"

# python-docx references (cannot glyph-embed; these families are expected on the viewer)
WORD_HEAD = "Cormorant Garamond"
WORD_BODY = "Montserrat"


def _font_path(name: str) -> str:
    return os.path.normpath(os.path.join(_FONT_ROOT, name))


_registered = False


def ensure_pdf_fonts() -> None:
    """Register brand faces once so exported PDFs embed Cormorant + Montserrat."""
    global _registered
    if _registered:
        return
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        pairs = (
            ("CormorantGaramond-Regular.ttf", FONT_HEAD),
            ("CormorantGaramond-Bold.ttf", FONT_HEAD_BOLD),
            ("Montserrat-Regular.ttf", FONT_BODY),
            ("Montserrat-Bold.ttf", FONT_BODY_BOLD),
        )
        for file, name in pairs:
            pdfmetrics.registerFont(TTFont(name, _font_path(file)))
        _registered = True
    except Exception:
        # Fall back to reportlab built-ins rather than breaking document export.
        _registered = True
