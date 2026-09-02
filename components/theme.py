"""
Project Echo — shared UI theme (dark navy & gold, editorial).

Single source of truth for the design system so every page stays consistent.
`inject_global_css()` callable from any page (idempotent) emits one <style> block.

Palette (high-end real-estate dark navy & gold):
  #0A1128  primary canvas (deep navy) / also sidebar bg
  #101E38  secondary background / panels / cards
  #D4AF37  accent gold — active borders, eyebrow text, primary button borders
  #F5F5F0  primary text / titles (cream)
  #8A9BAE  secondary muted text (grayish blue)

Typography:
  Page Eyebrow : Montserrat 12px/600, letter-spacing 2px, uppercase, gold
  Page Title    : Cormorant Garamond italic 34-40px/500, cream
  Page Subtitle : Cormorant Garamond italic 16-18px/400, muted  #8A9BAE
  Body          : Montserrat 14px/400
"""
import streamlit as st

# --- Design tokens (CSS custom properties + Python constants, mirrored) ---
TOKENS = {
    "canvas": "#0A1128",
    "panel": "#101E38",
    "ink": "#F5F5F0",
    "muted": "#8A9BAE",
    "gold": "#D4AF37",
    "button": "#101E38",
    "button_hover_bg": "#D4AF37",
    "borders": "rgba(212,175,55,0.2)",
    "white": "#0A1128",
    "danger": "#E5484D",
    "radius": "0px",             # flat / edgy — no rounded corners
    "radius_sm": "0px",
    "border": "1px solid rgba(212,175,55,0.2)",
    "border_strong": "2px solid #D4AF37",
    "title_font": "'Cormorant Garamond', serif",
    "body_font": "'Montserrat', sans-serif",
    "brand_font": "'Cormorant Garamond', 'Playfair Display', serif",
    "eyebrow_font": "'Montserrat', sans-serif",
}


def tokens_css() -> str:
    return """
    :root {
        --echo-canvas: #0A1128;
        --echo-panel: #101E38;
        --echo-ink: #F5F5F0;
        --echo-muted: #8A9BAE;
        --echo-gold: #D4AF37;
        --echo-button: #101E38;
        --echo-button-hover-bg: #D4AF37;
        --echo-borders: rgba(212,175,55,0.2);
        --echo-white: #0A1128;
        --echo-danger: #E5484D;
        --echo-radius: 0px;
        --echo-border: 1px solid rgba(212,175,55,0.2);
        --echo-border-strong: 2px solid #D4AF37;
        --echo-body: 'Montserrat', sans-serif;
        --echo-title: 'Cormorant Garamond', serif;
        --echo-brand: 'Cormorant Garamond', 'Playfair Display', serif;
        --echo-eyebrow: 'Montserrat', sans-serif;
    }
    """


def inject_global_css() -> None:
    """Emit the shared dark navy & gold theme. Idempotent per page run."""
    css = (
        "<style>\n"
        '@import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=Montserrat:wght@400;500;600&display=swap");\n'
        + tokens_css()
        + """
/* ---- Canvas: deep navy with a faint gold grid ---- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--echo-canvas) !important;
    background-image:
        repeating-linear-gradient(rgba(212,175,55,0.05) 0 1px, transparent 1px 96px),
        repeating-linear-gradient(90deg, rgba(212,175,55,0.05) 0 1px, transparent 1px 96px);
    color: var(--echo-ink);
    font-family: var(--echo-body);
}

/* ---- Flat / edgy controls: remove ALL rounded corners ---- */
.stButton > button,
[data-testid="stButton"] > button,
.stTabs [data-baseweb="tab"],
[data-baseweb="tag"],
.stDownloadButton > button,
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stMetric"],
div[data-testid="stVerticalBlockBorderWrapper"],
.stDataFrame,
[data-testid="stDataFrame"] {
    border-radius: var(--echo-radius) !important;
}

/* ---- App-wide buttons: navy bg, gold border, cream text ---- */
.stButton > button,
[data-testid="stButton"] > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: var(--echo-button) !important;
    color: var(--echo-ink) !important;
    border: 1px solid var(--echo-gold) !important;
    border-radius: 0 !important;
    font-family: var(--echo-body) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    line-height: 1 !important;
    padding: 0.15rem 0.5rem !important;
    min-height: 28px !important;
    height: 28px !important;
    width: auto !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease, color 0.15s ease;
}
.stButton > button:hover,
[data-testid="stButton"] > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: var(--echo-button-hover-bg) !important;
    color: var(--echo-canvas) !important;
    border-color: var(--echo-gold) !important;
    box-shadow: none !important;
}

/* ---- Button placement: aligned, compressed, even spacing ---- */
[data-testid="stElementContainer"]:has(button) {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stElementContainer"]:has(button) .stButton,
[data-testid="stElementContainer"] .stButton {
    margin: 0 !important;
    padding: 0 !important;
}
.stButton,
.stDownloadButton,
.stFormSubmitButton {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"],
[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
    gap: 0.35rem !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stElementContainer"]:has(.stButton),
[data-testid="stHorizontalBlock"] [data-testid="column"]:has(.stButton) {
    align-items: center !important;
    justify-content: flex-start !important;
}
[data-testid="stHorizontalBlock"] .stButton > button {
    width: auto !important;
    margin-right: 0.25rem !important;
}
[data-testid="stHorizontalBlock"]:has(.stButton) {
    gap: 0.25rem !important;
}
[data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"] {
    gap: 0.25rem !important;
    padding: 0 !important;
}
[data-testid="stHorizontalBlock"]:has(.stButton) [data-testid="column"] [data-testid="stElementContainer"] {
    margin: 0 !important;
}

/* ---- Unified page-header hierarchy (eyebrow > title > subtitle) ---- */
.page-eyebrow {
    font-family: var(--echo-eyebrow) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--echo-gold) !important;
    margin: 0 0 4px 0 !important;
}
.page-title {
    font-family: var(--echo-title) !important;
    font-style: italic !important;
    font-weight: 500 !important;
    font-size: 2.25rem !important; /* 36px */
    line-height: 1.1 !important;
    color: var(--echo-ink) !important;
    margin: 0 0 8px 0 !important;
}
.page-subtitle {
    font-family: var(--echo-title) !important;
    font-style: italic !important;
    font-weight: 400 !important;
    font-size: 1.05rem !important; /* ~17px */
    line-height: 1.3 !important;
    color: var(--echo-muted) !important;
    opacity: 0.85 !important;
    margin: 0 0 0.75rem 0 !important;
}

/* Alias existing per-page header classes to the unified hierarchy. */
.section-title,
.docs-title,
.notebook-title,
.view-header {
    font-family: var(--echo-title) !important;
    font-style: italic !important;
    font-weight: 500 !important;
    font-size: 2.25rem !important;
    line-height: 1.1 !important;
    color: var(--echo-ink) !important;
    margin: 0 0 8px 0 !important;
}
.section-caption,
.docs-caption,
.notebook-subtitle {
    font-family: var(--echo-title) !important;
    font-style: italic !important;
    font-weight: 400 !important;
    font-size: 1.05rem !important;
    line-height: 1.3 !important;
    color: var(--echo-muted) !important;
    opacity: 0.85 !important;
    margin: 0 0 0.75rem 0 !important;
}

/* ---- Cards / panels: dark navy, thin gold hairline, flat ---- */
.left-card,
.admin-card,
.workspace-card,
.editor-card,
[data-testid="stVerticalBlockBorderWrapper"]:has(.sync-height-scope),
.kpi-card, .task-card, .cal-cell,
.stContainer, [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 0 !important;
    border: 1px solid rgba(212,175,55,0.2) !important;
    box-shadow: none !important;
    background-color: var(--echo-panel) !important;
    color: var(--echo-ink) !important;
}

/* ---- Inputs: dark navy, cream text, gold focus ---- */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stBaseInput"] input,
[data-baseweb="input"],
[data-baseweb="textarea"],
div[data-baseweb="select"] > div,
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--echo-canvas) !important;
    border-color: rgba(212,175,55,0.3) !important;
    color: var(--echo-ink) !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus,
[data-baseweb="input"]:focus-within {
    border-color: var(--echo-gold) !important;
    box-shadow: none !important;
}

/* ---- Tabs: gold active tab, cream labels ---- */
.stTabs [data-baseweb="tab"] {
    color: var(--echo-muted) !important;
    background-color: transparent !important;
}
.stTabs [aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--echo-gold) !important;
    background-color: transparent !important;
    border-bottom: 2px solid var(--echo-gold) !important;
}

/* ---- Muted/helper text ---- */
.section-caption,
.stCaption,
[data-testid="stCaptionContainer"] {
    color: var(--echo-muted) !important;
}
</style>
"""
    )
    st.markdown(css, unsafe_allow_html=True)
