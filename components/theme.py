"""
Project Echo — shared UI theme (flat & edgy, stone ramp + navy text).

Single source of truth for the design system so every page stays consistent.
`inject_global_css()` callable from any page (idempotent) emits one <style> block.

Palette:
  #ECEBDE  canvas (lightest, dominant background; also sidebar bg)
  #D7D3BF  buttons (flat, no border/shadow)
  #C1BAA1  separators / card borders / button hover / secondary
  #A59D84  darkest - ACCENTS ONLY (active pills, small highlights)
  #0D1B3E  ink / all fonts + button text (deep navy)
"""
import streamlit as st

# --- Design tokens (CSS custom properties + Python constants, mirrored) ---
TOKENS = {
    "canvas": "#ECEBDE",
    "ink": "#0D1B3E",
    "button": "#D7D3BF",
    "button_hover": "#C1BAA1",
    "borders": "#C1BAA1",
    "secondary": "#C1BAA1",
    "accent": "#A59D84",          # accents only
    "white": "#FFFFFF",
    "danger": "#A94442",
    "radius": "0px",             # flat / edgy — no rounded corners
    "radius_sm": "0px",
    "border": "1px solid #C1BAA1",
    "border_strong": "2px solid #A59D84",
    "title_font": "'Playfair Display', serif",
    "body_font": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "brand_font": "'Cormorant Garamond', 'Playfair Display', serif",
}


def tokens_css() -> str:
    return """
    :root {
        --echo-canvas: #ECEBDE;
        --echo-ink: #0D1B3E;
        --echo-button: #D7D3BF;
        --echo-button-hover: #C1BAA1;
        --echo-borders: #C1BAA1;
        --echo-secondary: #C1BAA1;
        --echo-accent: #A59D84;
        --echo-white: #FFFFFF;
        --echo-danger: #A94442;
        --echo-radius: 0px;
        --echo-border: 1px solid #C1BAA1;
        --echo-border-strong: 2px solid #A59D84;
        --echo-body: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --echo-title: 'Playfair Display', serif;
        --echo-brand: 'Cormorant Garamond', 'Playfair Display', serif;
    }
    """


def inject_global_css() -> None:
    """Emit the shared flat & edgy theme. Idempotent per page run."""
    css = (
        "<style>\n"
        + tokens_css()
        + """
/* ---- Canvas: clean flat cream (gridlines removed) ---- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--echo-canvas) !important;
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

/* App-wide buttons: small, flat, box-shaped — #D7D3BF, navy text, NO border */
.stButton > button,
[data-testid="stButton"] > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
.stButton[kind="primary"] > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: var(--echo-button) !important;
    color: var(--echo-ink) !important;
    border: 0 none !important;
    border-radius: 0 !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    line-height: 1 !important;
    padding: 0.1rem 0.45rem !important;
    min-height: 22px !important;
    height: 22px !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease;
}
.stButton > button:hover,
[data-testid="stButton"] > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: var(--echo-button-hover) !important;
    color: var(--echo-ink) !important;
    border: 0 none !important;
    box-shadow: none !important;
}

/* Section titles: flat, edgy, editorial */
.section-title,
.section-caption {
    border-left: 4px solid var(--echo-accent);
    padding-left: 0.6rem;
}
.section-caption {
    color: #7C7C7C;
}

/* Cards: squared, hairline grid border, no shadow */
.left-card,
.admin-card,
[data-testid="stVerticalBlockBorderWrapper"]:has(.sync-height-scope),
.kpi-card, .task-card, .cal-cell,
.stContainer, [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 0 !important;
    border: var(--echo-border) !important;
    box-shadow: none !important;
    background-color: rgba(255,255,255,0.9) !important;
}
</style>
"""
    )
    st.markdown(css, unsafe_allow_html=True)
