"""
Project Echo — shared UI theme (primephilippines light-role adaptation).

Single source of truth for the design system so every page stays consistent.
`inject_global_css()` callable from any page (idempotent) emits one <style> block.

Palette (design tokens drawn from .reasonix/skills/primephilippines-design, light role):
  #f4f1ec  canvas (page background; also sidebar bg)
  #ffffff  panel / cards / surface
  #003366  ink / headings / brand navy (primary e-global-color-primary)
  #002244  deep navy (hover / deep brand)
  #c9ab4c  gold (secondary, accents)  | #d9bc5d bright-gold hover
  #0c0c0e  accent ink / strong CTAs
  #69727d  muted body text
  #c53a3f  danger

Typography (only these two families + Bebas for numerals):
  Heading / Display : Cormorant Garamond (600 italic)
  Body / UI         : Montserrat
  Numbers (stats)   : Bebas Neue (kept for data numerals, design-approved)
"""
import streamlit as st

# --- Design tokens (CSS custom properties + Python constants, mirrored) ---
TOKENS = {
    "canvas": "#f4f1ec",
    "panel": "#ffffff",
    "ink": "#003366",
    "muted": "#69727d",
    "gold": "#c9ab4c",
    "gold_bright": "#d9bc5d",
    "button": "#0c0c0e",
    "button_text": "#ffffff",
    "button_hover_bg": "#003366",
    "accent": "#0c0c0e",
    "borders": "rgba(0,51,102,0.15)",
    "white": "#FFFFFF",
    "danger": "#c53a3f",
    "radius": "6px",               # design radius scale (6px default; pills 999px)
    "radius_sm": "4px",
    "border": "1px solid rgba(0,51,102,0.15)",
    "border_strong": "2px solid #003366",
    "title_font": "'Cormorant Garamond', serif",
    "body_font": "'Montserrat', sans-serif",
    "number_font": "'Bebas Neue', 'Cormorant Garamond', serif",
    "brand_font": "'Cormorant Garamond', serif",
    "eyebrow_font": "'Montserrat', sans-serif",
}


def tokens_css() -> str:
    return """
    :root {
        --echo-canvas: #f4f1ec;
        --echo-panel: #ffffff;
        --echo-ink: #003366;
        --echo-muted: #69727d;
        --echo-gold: #c9ab4c;
        --echo-gold-bright: #d9bc5d;
        --echo-button: #0c0c0e;
        --echo-button-text: #ffffff;
        --echo-button-hover-bg: #003366;
        --echo-accent: #0c0c0e;
        --echo-borders: rgba(0,51,102,0.15);
        --echo-white: #FFFFFF;
        --echo-danger: #c53a3f;
        --echo-radius: 6px;
        --echo-radius-sm: 4px;
        --echo-border: 1px solid rgba(0,51,102,0.15);
        --echo-border-strong: 2px solid #003366;
        --echo-body: 'Montserrat', sans-serif;
        --echo-title: 'Cormorant Garamond', serif;
        --echo-number: 'Bebas Neue', 'Cormorant Garamond', serif;
        --echo-brand: 'Cormorant Garamond', serif;
        --echo-eyebrow: 'Montserrat', sans-serif;
    }
    """


def inject_global_css() -> None:
    """Emit the shared theme. Idempotent per page run."""
    css = (
        "<style>\n"
        '@import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Montserrat:wght@400;500;600&family=Bebas+Neue&display=swap");\n'
        + tokens_css()
        + """
/* ---- Canvas: primephilippines cream ---- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--echo-canvas) !important;
    color: #2A3441;
    font-family: var(--echo-body);
}

/* ---- Controls: base radius from the 4px grid ---- */
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

/* ---- App-wide buttons: accent/brand navy bg, white text, gold border on key CTAs ---- */
.stButton > button,
[data-testid="stButton"] > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: var(--echo-button) !important;
    color: var(--echo-button-text) !important;
    border: 1px solid var(--echo-gold) !important;
    border-radius: 6px !important;
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
    color: #ffffff !important;
    border-color: var(--echo-gold-bright) !important;
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
    color: var(--echo-ink) !important;
    margin: 0 0 4px 0 !important;
}
.page-title {
    font-family: var(--echo-title) !important;
    font-style: italic !important;
    font-weight: 600 !important;
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
    font-weight: 600 !important;
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

/* ---- Cards / panels: white surfaces, hairline navy border ---- */
.left-card,
.admin-card,
.workspace-card,
.editor-card,
[data-testid="stVerticalBlockBorderWrapper"]:has(.sync-height-scope),
.kpi-card, .task-card, .cal-cell,
.stContainer, [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 6px !important;
    border: 1px solid rgba(0,51,102,0.12) !important;
    box-shadow: none !important;
    background-color: var(--echo-panel) !important;
    color: #2A3441 !important;
}

/* ---- Inputs: light, navy border, focus border ---- */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
[data-testid="stBaseInput"] input,
[data-baseweb="input"],
[data-baseweb="textarea"],
div[data-baseweb="select"] > div,
[data-testid="stFileUploaderDropzone"] {
    background-color: #ffffff !important;
    border-color: rgba(0,51,102,0.25) !important;
    color: #2A3441 !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus,
[data-baseweb="input"]:focus-within {
    border-color: var(--echo-ink) !important;
    box-shadow: none !important;
}

/* ---- Tabs: navy active tab with gold underline ---- */
.stTabs [data-baseweb="tab"] {
    color: var(--echo-muted) !important;
    background-color: transparent !important;
}
.stTabs [aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--echo-ink) !important;
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
