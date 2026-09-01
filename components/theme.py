"""
Project Echo — shared UI theme (flat & edgy, warm monochrome palette).

Single source of truth for the design system so every page stays consistent.
`inject_global_css()` callable from any page (idempotent) emits one <style> block.

Palette:
  #F9F8F6  canvas (lightest, dominant background)
  #EFE9E3  separators / card borders
  #D9CFC7  secondary borders / inputs / badges
  #C9B59C  buttons / primary accents
  #412D15  ink / fonts / button text / headings
  #1F150C  hover / deepest accent
"""
import streamlit as st

# --- Design tokens (CSS custom properties + Python constants, mirrored) ---
TOKENS = {
    "canvas": "#F9F8F6",
    "ink": "#412D15",
    "ink_deep": "#1F150C",
    "accent": "#C9B59C",
    "borders": "#EFE9E3",
    "secondary": "#D9CFC7",
    "white": "#FFFFFF",
    "danger": "#A94442",
    "radius": "0px",             # flat / edgy — no rounded corners
    "radius_sm": "0px",
    "border": "1px solid #EFE9E3",
    "border_strong": "2px solid #412D15",
    "title_font": "'Playfair Display', serif",
    "body_font": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "brand_font": "'Cormorant Garamond', 'Playfair Display', serif",
}


def tokens_css() -> str:
    return """
    :root {
        --echo-canvas: #F9F8F6;
        --echo-ink: #412D15;
        --echo-ink-deep: #1F150C;
        --echo-accent: #C9B59C;
        --echo-borders: #EFE9E3;
        --echo-secondary: #D9CFC7;
        --echo-white: #FFFFFF;
        --echo-danger: #A94442;
        --echo-radius: 0px;
        --echo-border: 1px solid #EFE9E3;
        --echo-border-strong: 2px solid #412D15;
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

/* App-wide buttons: small, flat, box-shaped — warm tan on brown ink */
.stButton > button,
[data-testid="stButton"] > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
.stButton[kind="primary"] > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: var(--echo-accent) !important;
    color: var(--echo-ink) !important;
    border: 1px solid var(--echo-ink) !important;
    border-radius: 0 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    line-height: 1.2 !important;
    padding: 0.15rem 0.6rem !important;
    min-height: 26px !important;
    height: 26px !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease;
}
.stButton > button:hover,
[data-testid="stButton"] > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: var(--echo-ink-deep) !important;
    border-color: var(--echo-ink-deep) !important;
    color: var(--echo-canvas) !important;
    box-shadow: none !important;
}

/* Section titles: flat, edgy, editorial */
.section-title,
.section-caption {
    border-left: 4px solid var(--echo-accent);
    padding-left: 0.6rem;
}
.section-caption {
    color: #8A7A5F;
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
