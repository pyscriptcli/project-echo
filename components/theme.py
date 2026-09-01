"""
Project Echo — shared UI theme (flat & edgy, keeps the navy/charcoal/gold palette).

Single source of truth for the design system so every page stays consistent.
`inject_global_css()` callable from any page (idempotent) emits one <style> block.
"""
import streamlit as st

# --- Design tokens (CSS custom properties + Python constants, mirrored) ---
TOKENS = {
    "canvas": "#F5F1E8",
    "canvas_grid": "rgba(26, 43, 76, 0.10)",       # large gridlines on canvas
    "canvas_grid_fine": "rgba(26, 43, 76, 0.05)",
    "navy": "#1A2B4C",
    "charcoal": "#111A2B",
    "charcoal_hover": "#1A263D",
    "gold": "#D4AF37",
    "gold_bright": "#E6C44D",
    "muted": "#6C727A",
    "slate": "#768390",
    "ink": "#1A1A1A",
    "white": "#FFFFFF",
    "radius": "0px",             # flat / edgy — no rounded corners
    "radius_sm": "0px",
    "border": "1px solid rgba(26,43,76,0.14)",
    "border_strong": "2px solid #1A2B4C",
    "title_font": "'Playfair Display', serif",
    "body_font": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "brand_font": "'Cormorant Garamond', 'Playfair Display', serif",
}


def tokens_css() -> str:
    return """
    :root {
        --echo-canvas: #F5F1E8;
        --echo-grid: rgba(26,43,76,0.10);
        --echo-grid-fine: rgba(26,43,76,0.05);
        --echo-navy: #1A2B4C;
        --echo-charcoal: #111A2B;
        --echo-charcoal-hover: #1A263D;
        --echo-gold: #D4AF37;
        --echo-gold-bright: #E6C44D;
        --echo-muted: #6C727A;
        --echo-slate: #768390;
        --echo-ink: #1A1A1A;
        --echo-white: #FFFFFF;
        --echo-radius: 0px;
        --echo-border: 1px solid rgba(26,43,76,0.14);
        --echo-border-strong: 2px solid #1A2B4C;
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
/* ---- Canvas: cream + LARGE gridlines (editorial, real-estate feel) ---- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: var(--echo-canvas) !important;
    background-image:
        linear-gradient(to right, var(--echo-grid) 1px, transparent 1px),
        linear-gradient(to bottom, var(--echo-grid) 1px, transparent 1px),
        linear-gradient(to right, var(--echo-grid-fine) 1px, transparent 1px),
        linear-gradient(to bottom, var(--echo-grid-fine) 1px, transparent 1px) !important;
    background-size: 96px 96px, 96px 96px, 24px 24px, 24px 24px !important;
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

/* App-wide buttons: charcoal + gold edge, squared */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
.stButton[kind="primary"] > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: var(--echo-charcoal) !important;
    color: var(--echo-white) !important;
    border: 1px solid var(--echo-gold) !important;
    border-radius: 0 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    box-shadow: none !important;
    transition: background-color 0.15s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    background-color: var(--echo-charcoal-hover) !important;
    border-color: var(--echo-gold-bright) !important;
    box-shadow: none !important;
}

/* Section titles: flat, edgy, editorial */
.section-title,
.section-caption {
    border-left: 4px solid var(--echo-gold);
    padding-left: 0.6rem;
}
.section-caption {
    color: var(--echo-muted);
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
