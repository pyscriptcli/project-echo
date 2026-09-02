"""
Project Echo — shared UI theme (gray-azure, navy, dark-gray editorial).

Single source of truth for the design system so every page stays consistent.
`inject_global_css()` callable from any page (idempotent) emits one <style> block.

Palette:
  #d9d9d9  canvas / also sidebar bg
  #0D1B3E  ink / header fonts (deep navy blue)
  #a3acd5  buttons (blue-gray / periwinkle)
  #F9FAFB  panels / cards (light on canvas)
  #5A607A  muted body text

Typography:
  Page Eyebrow : Montserrat 12px/600, letter-spacing 2px, uppercase, navy
  Page Title    : Cormorant Garamond italic 34-40px/600, deep navy
  Page Subtitle : Cormorant Garamond italic 16-18px/400, muted
  Body          : Montserrat (headers Cormorant, numbers Bebas Neue)
"""
import streamlit as st

# --- Design tokens (CSS custom properties + Python constants, mirrored) ---
TOKENS = {
    "canvas": "#d9d9d9",
    "panel": "#F9FAFB",
    "ink": "#0D1B3E",
    "muted": "#5A607A",
    "gold": "#a3acd5",
    "button": "#a3acd5",
    "button_hover_bg": "#8fa2d6",
    "borders": "rgba(13,27,62,0.15)",
    "white": "#FFFFFF",
    "danger": "#C0392B",
    "radius": "0px",             # flat / edgy — no rounded corners
    "radius_sm": "0px",
    "border": "1px solid rgba(13,27,62,0.12)",
    "border_strong": "2px solid #0D1B3E",
    "title_font": "'Cormorant Garamond', serif",
    "body_font": "'Montserrat', sans-serif",
    "number_font": "'Bebas Neue', 'Cormorant Garamond', serif",
    "brand_font": "'Cormorant Garamond', 'Playfair Display', serif",
    "eyebrow_font": "'Montserrat', sans-serif",
}


def tokens_css() -> str:
    return """
    :root {
        --echo-canvas: #d9d9d9;
        --echo-panel: #F9FAFB;
        --echo-ink: #0D1B3E;
        --echo-muted: #5A607A;
        --echo-gold: #a3acd5;
        --echo-button: #a3acd5;
        --echo-button-hover-bg: #8fa2d6;
        --echo-borders: rgba(13,27,62,0.15);
        --echo-white: #FFFFFF;
        --echo-danger: #C0392B;
        --echo-radius: 0px;
        --echo-border: 1px solid rgba(13,27,62,0.12);
        --echo-border-strong: 2px solid #0D1B3E;
        --echo-body: 'Montserrat', sans-serif;
        --echo-title: 'Cormorant Garamond', serif;
        --echo-number: 'Bebas Neue', 'Cormorant Garamond', serif;
        --echo-brand: 'Cormorant Garamond', 'Playfair Display', serif;
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
/* ---- Canvas: gray azure ---- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--echo-canvas) !important;
    color: #2A3441;
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

/* ---- App-wide buttons: dark gray bg, white text ---- */
.stButton > button,
[data-testid="stButton"] > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: var(--echo-button) !important;
    color: #0D1B3E !important;
    border: 1px solid var(--echo-button) !important;
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
    color: #0D1B3E !important;
    border-color: var(--echo-button-hover-bg) !important;
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
    color: #0D1B3E !important;
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

/* ---- Cards / panels: light panels, hairline navy border, flat ---- */
.left-card,
.admin-card,
.workspace-card,
.editor-card,
[data-testid="stVerticalBlockBorderWrapper"]:has(.sync-height-scope),
.kpi-card, .task-card, .cal-cell,
.stContainer, [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 0 !important;
    border: 1px solid rgba(13,27,62,0.12) !important;
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
    background-color: #FFFFFF !important;
    border-color: rgba(13,27,62,0.25) !important;
    color: #2A3441 !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus,
.stNumberInput input:focus,
[data-baseweb="input"]:focus-within {
    border-color: #0D1B3E !important;
    box-shadow: none !important;
}

/* ---- Tabs: navy active tab ---- */
.stTabs [data-baseweb="tab"] {
    color: var(--echo-muted) !important;
    background-color: transparent !important;
}
.stTabs [aria-selected="true"],
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #0D1B3E !important;
    background-color: transparent !important;
    border-bottom: 2px solid #a3acd5 !important;
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
