import sys
import os
import calendar
import datetime
import hashlib
import html
import logging
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

import pandas as pd

logger = logging.getLogger(__name__)

from utils.db import fetch_meeting_archives, get_supabase_client
from components.sidebar import setup_page_layout
from components.theme import render_page_header, render_section_header
from utils.auth import init_supabase, require_login

st.set_page_config(
    page_title="Project Echo - Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)



st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Montserrat:wght@400;500;600&family=Bebas+Neue&display=swap');

/* ---- Header: hide content, NOT the element (sidebar expand button lives there) ---- */
header[data-testid="stHeader"],
.stApp > header {
    background: transparent !important;
    height: 0 !important;
    padding: 0 !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"],
#MainMenu,
footer {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}

.stApp {
    background-color: #f4f1ec !important;
    font-family: 'Montserrat', sans-serif !important;
    color: #1b1d1e;
}

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

[data-testid="stHorizontalBlock"] {
    gap: 1rem !important;
}

.left-card {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 1rem;
    box-shadow: none;
    color: #1b1d1e;
    flex-shrink: 0;
}

.left-card-scroll {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    margin-bottom: 0.5rem;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 600;
    color: #003366;
    font-size: 1.6rem;
    margin: 0 0 0.2rem 0;
}
.section-caption {
    font-size: 0.8rem;
    color: #69727d;
    margin: 0 0 0.8rem 0;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.65rem;
}
.kpi-grid-2x2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
}
.overview-ratio-card {
    background: #ffffff;
    border-radius: 6px;
    padding: 0.85rem 1rem;
    border: 1px solid rgba(0, 51, 102, 0.12);
    margin-top: 0.75rem;
}
.overview-ratio-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.45rem;
}
.overview-ratio-label {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #69727d;
}
.overview-ratio-pct {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    color: #003366;
}
.overview-bar-track {
    display: flex;
    height: 7px;
    border-radius: 999px;
    background: rgba(0, 51, 102, 0.08);
    overflow: hidden;
    margin-bottom: 0.55rem;
}
.overview-bar-fill {
    height: 100%;
}
.overview-bar-fill.internal {
    background: #003366;
}
.overview-bar-fill.external {
    background: #c9ab4c;
}
.overview-ratio-legend {
    display: flex;
    gap: 1rem;
    font-family: 'Montserrat', sans-serif;
    font-size: 0.68rem;
    color: #69727d;
}
.legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
}
.legend-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}
.legend-dot.navy { background: #003366; }
.legend-dot.gold { background: #c9ab4c; }
.kpi-card {
    background: #ffffff;
    border-radius: 6px;
    padding: 0.75rem 0.9rem;
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-left: 3.5px solid #003366;
}
.kpi-card.gold-accent {
    border-left: 3.5px solid #c9ab4c;
}
.kpi-title {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #69727d;
    display: block;
    margin-bottom: 0.2rem;
}
.kpi-value {
    font-family: 'Bebas Neue', 'Cormorant Garamond', serif;
    font-style: normal;
    font-size: 2.1rem;
    font-weight: 400;
    color: #003366;
    line-height: 1;
    display: block;
}
.kpi-sub {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.68rem;
    color: #69727d;
    margin-top: 0.25rem;
    display: block;
}

/* Quick Action Cards */
.qa-badge-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.45rem;
}
.qa-card-badge {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #003366;
    background: rgba(0, 51, 102, 0.07);
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid rgba(0, 51, 102, 0.15);
}
.qa-card-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 600;
    font-size: 1.15rem;
    color: #003366;
    margin: 0 0 0.35rem 0;
    line-height: 1.25;
}
.qa-card-desc {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.72rem;
    line-height: 1.45;
    color: #69727d;
    margin: 0 0 0.85rem 0;
    min-height: 2.8rem;
}

/* Recent Meetings Cards */
.tm-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.4rem;
}
.tm-type-badge {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 2px 8px;
    border-radius: 999px;
}
.tm-type-badge.internal {
    background: rgba(0, 51, 102, 0.08);
    color: #003366;
    border: 1px solid rgba(0, 51, 102, 0.18);
}
.tm-type-badge.external {
    background: rgba(201, 171, 76, 0.12);
    color: #8c6d23;
    border: 1px solid rgba(201, 171, 76, 0.3);
}
.tm-date-chip {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.68rem;
    color: #69727d;
    font-weight: 600;
}
.tm-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 600;
    font-size: 1.15rem;
    color: #003366;
    margin: 0 0 0.2rem 0;
    line-height: 1.25;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.tm-meta {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.68rem;
    color: #69727d;
    margin-bottom: 0.45rem;
}
.tm-summary {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.74rem;
    color: #1b1d1e;
    line-height: 1.4;
    margin-bottom: 0.75rem;
    min-height: 2.8rem;
}

/* Page links in main content styled as compact CTA buttons */
[data-testid="stMain"] [data-testid="stPageLink"] a,
.main [data-testid="stPageLink"] a {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0.35rem !important;
    background-color: #0c0c0e !important;
    color: #ffffff !important;
    border: 1px solid #c9ab4c !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    padding: 0.25rem 0.65rem !important;
    min-height: 28px !important;
    height: 28px !important;
    width: 100% !important;
    text-decoration: none !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}
[data-testid="stMain"] [data-testid="stPageLink"] a:hover,
.main [data-testid="stPageLink"] a:hover {
    background-color: #003366 !important;
    border-color: #d9bc5d !important;
    color: #ffffff !important;
}
[data-testid="stMain"] [data-testid="stPageLink"] a *,
.main [data-testid="stPageLink"] a *,
[data-testid="stMain"] [data-testid="stPageLink"] a p,
.main [data-testid="stPageLink"] a p,
[data-testid="stMain"] [data-testid="stPageLink"] a span,
.main [data-testid="stPageLink"] a span {
    color: #ffffff !important;
    fill: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.72rem !important;
    margin: 0 !important;
}

.meeting-card {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 0.6rem 0.75rem;
    margin-bottom: 0.5rem;
}
.meeting-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-size: 1rem;
    font-weight: 600;
    color: #003366;
    margin: 0 0 0.1rem 0;
}
.meeting-sub {
    font-size: 0.65rem;
    color: #69727d;
    margin-bottom: 0.3rem;
}
.meeting-desc {
    font-size: 0.78rem;
    color: #1b1d1e;
    line-height: 1.35;
    margin: 0;
}

.dashboard-topbar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.75rem;
}
.page-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #69727d;
    text-transform: uppercase;
    margin: 0 0 0.15rem 0;
}
.page-title {
    font-family: 'Cormorant Garamond', serif;
    font-style: italic;
    font-weight: 600;
    color: #003366;
    font-size: 2rem;
    line-height: 1;
    margin: 0;
}
.dash-card {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid rgba(0, 51, 102, 0.12);
    border-radius: 6px;
    padding: 0.75rem 0.85rem;
    margin-bottom: 0.5rem;
}
.dash-card-title {
    font-size: 0.82rem;
    font-weight: 700;
    color: #003366;
    line-height: 1.25;
    margin: 0 0 0.2rem 0;
}
.dash-card-meta {
    font-size: 0.68rem;
    color: #69727d;
    margin: 0;
}
.dash-card-body {
    font-size: 0.76rem;
    line-height: 1.35;
    color: #1b1d1e;
    margin: 0.25rem 0 0 0;
}
.attention-tag {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    border: 1px solid rgba(0, 51, 102, 0.12);
    background: #ffffff;
    color: #003366;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 1px 8px;
    margin-bottom: 0.35rem;
}
.attention-tag.danger {
    color: #c53a3f;
    border-color: rgba(197, 58, 63, 0.24);
    background: #FDF0EF;
}
.attention-tag.warning {
    color: #8C6D23;
    border-color: rgba(212, 175, 55, 0.32);
    background: #FFF9E8;
}
.agenda-day {
    font-size: 0.7rem;
    font-weight: 700;
    color: #003366;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    border-bottom: 1px solid rgba(0, 51, 102, 0.12);
    padding-bottom: 0.25rem;
    margin: 0.35rem 0;
}
.activity-row {
    display: grid;
    grid-template-columns: 120px 1fr 42px;
    gap: 0.6rem;
    align-items: center;
    font-size: 0.72rem;
    color: #1b1d1e;
    margin-bottom: 0.45rem;
}
.activity-track {
    height: 7px;
    border-radius: 999px;
    background: rgba(0, 51, 102, 0.08);
    overflow: hidden;
}
.activity-fill {
    height: 100%;
    border-radius: 999px;
    background: #003366;
}
.activity-fill.gold { background: #c9ab4c; }
.activity-fill.danger { background: #c53a3f; }
.empty-state {
    color: #69727d;
    font-size: 0.8rem;
    font-style: italic;
    padding: 0.5rem 0;
}

div[data-testid="stPopover"] { margin-bottom: 0 !important; }
div[data-testid="stPopover"] > button {
    background-color: #0c0c0e !important;
    color: #ffffff !important;
    border: 1px solid #c9ab4c !important;
    border-radius: 6px !important;
    font-size: 0.75rem !important;
    min-height: 32px !important;
    height: 32px !important;
}
.stButton > button,
[data-testid="stButton"] > button,
[data-testid="stDownloadButton"] > button,
.stDownloadButton > button,
.stFormSubmitButton > button,
[data-testid="stFormSubmitButton"] > button {
    background-color: #0c0c0e !important;
    color: #ffffff !important;
    border: 1px solid #c9ab4c !important;
    border-radius: 6px !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.75rem !important;
    min-height: 28px !important;
    height: 28px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}

/* Ensure deep charcoal buttons have pure white text and icons across all states and nested tags */
.stButton > button,
.stButton > button *,
[data-testid="stButton"] > button,
[data-testid="stButton"] > button *,
.stDownloadButton > button,
.stDownloadButton > button *,
[data-testid="stDownloadButton"] > button,
[data-testid="stDownloadButton"] > button *,
.stFormSubmitButton > button,
.stFormSubmitButton > button *,
[data-testid="stFormSubmitButton"] > button,
[data-testid="stFormSubmitButton"] > button *,
div[data-testid="stPopover"] > button,
div[data-testid="stPopover"] > button * {
    color: #ffffff !important;
    fill: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.stButton > button:hover,
.stButton > button:hover *,
[data-testid="stButton"] > button:hover,
[data-testid="stButton"] > button:hover *,
.stDownloadButton > button:hover,
.stDownloadButton > button:hover *,
[data-testid="stDownloadButton"] > button:hover,
[data-testid="stDownloadButton"] > button:hover *,
div[data-testid="stPopover"] > button:hover,
div[data-testid="stPopover"] > button:hover * {
    background-color: #003366 !important;
    border-color: #d9bc5d !important;
    color: #ffffff !important;
    fill: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Header date picker inline alignment */
[data-testid="stDateInput"] {
    margin-bottom: 0.85rem !important;
}
[data-testid="stDateInput"] > div > div {
    background-color: #ffffff !important;
    border: 1px solid rgba(0, 51, 102, 0.2) !important;
    border-radius: 6px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #003366 !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    min-height: 38px !important;
    height: 38px !important;
}
[data-testid="stDateInput"] input {
    font-family: 'Montserrat', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #003366 !important;
}
.header-border-ext {
    border-bottom: 1px solid rgba(0, 51, 102, 0.15);
    margin-bottom: 1rem;
}

/* ===== tasks.py Calendar Styles ===== */
:root {
    --bg: #f4f1ec;
    --surface: #ffffff;
    --ink: #003366;
    --muted: #69727d;
    --gold: #c9ab4c;
    --danger: #c53a3f;
    --radius: 6px;
    --control-height: 28px;
}

h3 {
    font-family: 'Cormorant Garamond', serif !important;
    font-style: italic !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    font-size: 1.4rem !important;
    margin-bottom: 0.2rem !important;
}



.stSelectbox > div > div,
.stMultiselect > div > div,
.stTextInput > div > div,
.stDateInput > div > div {
    min-height: var(--control-height) !important;
    border-radius: var(--radius) !important;
    font-size: 0.78rem !important;
    border-color: rgba(0, 51, 102, 0.2) !important;
    background: rgba(255,255,255,0.8) !important;
    color: #1b1d1e !important;
}

.assignee-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #003366;
    color: #fff;
    font-size: 0.52rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    flex-shrink: 0;
}

.due-chip {
    display: inline-flex;
    align-items: center;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.62rem;
    font-weight: 600;
    background: #ffffff;
    color: #1b1d1e;
    border: 1px solid rgba(0, 51, 102, 0.12);
    white-space: nowrap;
}
.due-chip.overdue {
    background: #FDF0EF;
    color: var(--danger);
    border-color: rgba(231, 76, 60, 0.3);
}
.due-chip.due-today {
    background: #FFF9E8;
    color: #8C6D23;
    border-color: rgba(212, 175, 55, 0.35);
}

.cal-filter-row {
    display: flex;
    align-items: center;
    gap: 6px;
}
.cal-filter-row .stSelectbox,
.cal-filter-row .stDateInput,
.cal-filter-row .stMultiselect {
    flex-shrink: 1;
}
.cal-filter-row [data-testid="stBaseButton-secondary"] {
    width: 28px !important;
    padding: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stPopover"] > button {
    height: var(--control-height) !important;
    min-height: var(--control-height) !important;
    min-width: 32px !important;
    border-radius: var(--radius) !important;
    border: 1px solid rgba(26, 43, 76, 0.15) !important;
    background: var(--surface) !important;
    color: var(--ink) !important;
    padding: 0 8px !important;
}

.cal-month-cell {
    background: var(--surface);
    border: 1px solid rgba(0, 51, 102, 0.1);
    border-radius: var(--radius);
    padding: 4px;
    min-height: 78px;
    height: auto !important;
    box-sizing: border-box;
}
.cal-month-cell:hover { border-color: rgba(0, 51, 102, 0.35); }
.cal-month-cell.dim { background: rgba(255, 255, 255, 0.35); border: none; }
.cal-month-cell.weekend { background: rgba(0, 51, 102, 0.06); border-color: rgba(0, 51, 102, 0.18); }
.cal-month-cell.today { border: 2px solid #003366; }

.cal-month-day-num {
    display: flex;
    align-items: center;
    gap: 4px;
    font-family: 'Bebas Neue', 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--ink);
    padding: 1px 2px 3px 2px;
}
.cal-month-cell.weekend .cal-month-day-num { color: #003366; }

.today-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--gold);
    display: inline-block;
    flex-shrink: 0;
}

.cal-more {
    font-size: 0.58rem;
    color: var(--muted);
    padding-left: 2px;
    margin-top: 1px;
}

.cal-unscheduled {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: var(--radius);
    padding: 0.35rem 0.5rem;
    margin-top: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# AUTH GATE — enforced on every page (login required)
# ------------------------------------------------------------
require_login(page_key="dashboard")

supabase = init_supabase()

# ------------------------------------------------------------
# DASHBOARD (AUTHENTICATED)
# ------------------------------------------------------------
setup_page_layout()

if "selected_meeting_id" not in st.session_state:
    st.session_state["selected_meeting_id"] = None

today = datetime.date.today()
if "start_date" not in st.session_state:
    st.session_state["start_date"] = today.replace(day=1)
if "end_date" not in st.session_state:
    _, last_day = calendar.monthrange(today.year, today.month)
    st.session_state["end_date"] = today.replace(day=last_day)
if "dash_date_range" not in st.session_state:
    st.session_state["dash_date_range"] = (st.session_state["start_date"], st.session_state["end_date"])

# Calendar session state
if "tasks_cal_focus_date" not in st.session_state:
    st.session_state["tasks_cal_focus_date"] = today
if "tasks_cal_view" not in st.session_state:
    st.session_state["tasks_cal_view"] = "Month"

# ------------------------------------------------------------
# DATA FETCHING
# ------------------------------------------------------------
supabase_records = fetch_meeting_archives(limit=100)
meetings = supabase_records

def fetch_tasks():
    if not supabase:
        st.error("Data service is not ready.")
        return []
    try:
        res = supabase.table("tasks").select("*").order("due_date", desc=False).execute()
        return res.data if res.data else []
    except Exception as e:
        logger.exception("Could not load dashboard tasks: %s", e)
        st.error("Tasks could not be loaded. Please try again shortly.")
        return []

tasks = fetch_tasks()

# ------------------------------------------------------------
# CONSTANTS & HELPERS
# ------------------------------------------------------------
SPECIFIC_PEOPLE = [
    "Sondi Tuazon", "Meliza Zapata", "Dykstra Pineda", "Kristina Balajadia",
    "Carlo Medina", "Cedtrix Rena", "Dave Policarpio", "Irish Rima"
]
GROUP_OPTIONS = ["All Team Members", "All Advisors"]

def parse_calendar_date(raw_val):
    if not raw_val:
        return None
    raw_s = str(raw_val).strip()
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%B %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.datetime.strptime(raw_s[:10], fmt).date()
        except ValueError:
            pass
    return None

def format_mm_dd_yyyy(d):
    if d is None:
        return "No date"
    return d.strftime("%m-%d-%Y")

def get_initials(name_str):
    if not name_str:
        return "—"
    parts = name_str.replace(",", " ").split()
    initials = "".join([p[0].upper() for p in parts if p][:2])
    return initials or "—"

def get_due_chip_info(due_dt, status):
    if not due_dt:
        return "No date", ""
    today = datetime.date.today()
    if status != "done" and due_dt < today:
        days = (today - due_dt).days
        return f"Overdue · {days}d", "overdue"
    if due_dt == today:
        return "Today", "due-today"
    if due_dt == today + datetime.timedelta(days=1):
        return "Tomorrow", ""
    return format_mm_dd_yyyy(due_dt), ""

def generate_stable_id(meeting_id, discussion_text, action_text):
    source = f"{meeting_id}-{discussion_text}-{action_text}"
    return hashlib.md5(source.encode()).hexdigest()

def add_task(title, description, assignee, due_date, meeting_id=None, discussion_point_id=None):
    if not supabase:
        st.error("Data service is not ready.")
        return False
    payload = {
        "title": title.strip(),
        "description": description.strip(),
        "assignee": assignee if assignee else None,
        "due_date": due_date.isoformat() if due_date else None,
        "meeting_id": meeting_id,
        "status": "todo",
        "discussion_point_id": discussion_point_id
    }
    try:
        supabase.table("tasks").insert(payload).execute()
        return True
    except Exception as e:
        logger.exception("Could not add dashboard task: %s", e)
        st.error("The task could not be created. Please try again shortly.")
        return False

def update_task(task_id, new_status, new_assignee=None, new_due_date=None):
    if not supabase:
        return
    try:
        update_payload = {
            "status": new_status,
            "status_updated_by": st.session_state.get("user", {}).get("username", "System"),
            "status_updated_at": "now()",
            "updated_at": "now()"
        }
        if new_assignee is not None:
            update_payload["assignee"] = new_assignee
        if new_due_date is not None:
            update_payload["due_date"] = new_due_date.isoformat()
        supabase.table("tasks").update(update_payload).eq("id", task_id).execute()
    except Exception as e:
        logger.exception("Could not update dashboard task: %s", e)
        st.error("The task could not be updated. Please try again shortly.")

def delete_task(task_id):
    if not supabase:
        return
    try:
        supabase.table("tasks").delete().eq("id", task_id).execute()
    except Exception as e:
        logger.exception("Could not delete dashboard task: %s", e)
        st.error("The task could not be deleted. Please try again shortly.")

def get_assignee_ui_state(assignee_str):
    if assignee_str in GROUP_OPTIONS:
        return "Group", assignee_str, []
    elif assignee_str:
        selected_ind = [name.strip() for name in assignee_str.split(",") if name.strip() in SPECIFIC_PEOPLE]
        if selected_ind:
            return "Specific Individuals", "", selected_ind
    return "Group", GROUP_OPTIONS[0], []

def build_calendar_events():
    events = []
    today = datetime.date.today()

    for t in tasks:
        due_date = parse_calendar_date(t.get("due_date"))
        if not due_date:
            continue
        status = t.get("status", "todo")
        events.append({
            "id": t.get("id"),
            "title": t.get("title", "Untitled Task"),
            "date": due_date,
            "source": "task",
            "status": status,
            "assignee": t.get("assignee") or "",
            "meeting_id": t.get("meeting_id"),
            "meeting_label": "",
            "overdue": due_date < today and status != "done",
        })

    for m in meetings:
        m_id = m.get("meeting_id")
        client_name = m.get("client_name", "Meeting")
        table_items = m.get("table_items") or []
        if not table_items:
            raw = m.get("raw_payload") or {}
            details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
            table_items = details.get("action_items") or []

        for idx, item in enumerate(table_items):
            action = (item.get("Action Plan") or item.get("Discussion Points") or
                      item.get("task") or item.get("topic") or item.get("action") or "")
            if not action:
                continue
            due_date = parse_calendar_date(
                item.get("Indicative Delivery Date") or item.get("delivery_date") or item.get("due_date")
            )
            if not due_date:
                continue
            assignee = item.get("Person-in-charge") or item.get("owner") or item.get("assigned_to") or ""
            events.append({
                "id": f"meeting_{m_id}_{idx}",
                "title": str(action)[:60],
                "date": due_date,
                "source": "meeting_action",
                "status": "n/a",
                "assignee": assignee,
                "meeting_id": m_id,
                "meeting_label": client_name,
                "overdue": due_date < today,
            })

    return events

def apply_calendar_filters(events, assignee_filters, status_filters, meeting_filter, start_date, end_date):
    result = []
    for e in events:
        if not (start_date <= e["date"] <= end_date):
            continue

        if assignee_filters and "All Assignees" not in assignee_filters:
            matched = False
            if "Unassigned" in assignee_filters and not e.get("assignee"):
                matched = True
            if not matched:
                for f in assignee_filters:
                    if f in GROUP_OPTIONS and e.get("assignee") == f:
                        matched = True
                        break
                    if f in SPECIFIC_PEOPLE and f in (e.get("assignee") or ""):
                        matched = True
                        break
            if not matched:
                continue

        if e["source"] == "task" and status_filters and e["status"] not in status_filters:
            continue

        if meeting_filter:
            search_text = f"{e.get('meeting_id', '')} {e.get('meeting_label', '')}".lower()
            if meeting_filter.lower() not in search_text:
                continue

        result.append(e)
    return result

def get_event_icon(evt):
    if evt["overdue"]:
        return ":material/error:"
    if evt["source"] == "meeting_action":
        return ":material/event:"
    status = evt.get("status", "todo")
    if status == "done":
        return ":material/check_circle:"
    if status == "in_progress":
        return ":material/play_circle:"
    return ":material/radio_button_unchecked:"

def get_event_label(evt):
    initials = get_initials(evt.get("assignee", ""))
    return f"{initials} · {evt['title']}"

def get_event_tooltip(evt):
    if evt["source"] == "meeting_action":
        line2 = evt.get("meeting_label") or f"Meeting: {evt.get('meeting_id') or '—'}"
    else:
        line2 = "Task"
    return f"{evt['title']}\n{line2}\nDue: {format_mm_dd_yyyy(evt['date'])}"

# ------------------------------------------------------------
# DIALOGS
# ------------------------------------------------------------
@st.dialog("Task Details", width="large")
def open_task_details():
    task = st.session_state.get('selected_task')
    if not task:
        st.warning("No task selected.")
        if st.button("Close", width="stretch"):
            st.session_state.pop('selected_task', None)
            st.rerun()
        return

    meeting_id = task.get('meeting_id')
    meeting_details = next((m for m in meetings if m.get('meeting_id') == meeting_id), None)

    left_col, right_col = st.columns([1.3, 1])

    with left_col:
        status_map = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
        status_options = list(status_map.keys())
        current_status = task.get('status', 'todo')
        current_index = status_options.index(current_status) if current_status in status_options else 0

        existing_due_date = parse_calendar_date(task.get('due_date'))

        render_section_header(task["title"], f"Task ID: {task['id']}")

        st.markdown("**Description**")
        st.write(task.get('description', 'No description provided.'))

        st.markdown("---")
        st.markdown("**Status**")
        new_status = st.selectbox(
            "Status",
            status_options,
            index=current_index,
            format_func=lambda x: status_map[x],
            label_visibility="collapsed",
            key=f"modal_status_{task['id']}"
        )

        st.markdown("**Assignee**")
        assignee_type, group_val, individuals = get_assignee_ui_state(task.get('assignee', ""))

        assign_type = st.radio(
            "Assignment Type",
            ["Group", "Specific Individuals"],
            index=0 if assignee_type == "Group" else 1,
            horizontal=True,
            label_visibility="collapsed",
            key=f"modal_assign_type_{task['id']}"
        )

        if assign_type == "Group":
            group_idx = GROUP_OPTIONS.index(group_val) if group_val in GROUP_OPTIONS else 0
            new_assignee = st.selectbox("Select Group", GROUP_OPTIONS, index=group_idx, key=f"modal_group_{task['id']}")
        else:
            new_assignee_list = st.multiselect(
                "Select Individuals",
                SPECIFIC_PEOPLE,
                default=individuals,
                key=f"modal_individuals_{task['id']}"
            )
            new_assignee = ", ".join(new_assignee_list)

        st.markdown("**Due Date**")
        new_due_date = st.date_input(
            "Due Date",
            value=existing_due_date,
            label_visibility="collapsed",
            key=f"modal_due_{task['id']}"
        )

        if st.button("Save Changes", width="stretch", type="primary"):
            update_task(task['id'], new_status, new_assignee, new_due_date)
            st.session_state.pop('selected_task', None)
            st.session_state["task_flash"] = "Task updated successfully."
            st.rerun()

        st.markdown("---")
        st.caption(f"Status Updated By: {task.get('status_updated_by') or '—'}")
        st.caption(f"Status Updated At: {task.get('status_updated_at') or '—'}")

    with right_col:
        render_section_header("Meeting origin", "Source meeting for this task.")
        if meeting_details:
            st.markdown(f"**{meeting_details.get('client_name', 'Meeting Record')}**")
            st.caption(f"Date: {format_mm_dd_yyyy(parse_calendar_date(meeting_details.get('meeting_date')))}")
            st.caption(f"Prepared By: {meeting_details.get('prepared_by') or '—'}")
            st.markdown("---")
            st.markdown("**Summary**")
            st.write(meeting_details.get('summary_md', 'No summary available.'))
        else:
            st.info("This task is not linked to a specific meeting.")

    if st.button("Close", width="stretch", key="close_modal_btn"):
        st.session_state.pop('selected_task', None)
        st.rerun()

@st.dialog("Create Task", width="large")
def new_task_dialog():
    prefill_date = st.session_state.get("cal_new_task_date")

    with st.form("cal_new_task_form", clear_on_submit=True):
        render_section_header("New task", "Create a task with clear ownership and timing.")
        left, right = st.columns(2)

        with left:
            title = st.text_input("Task Title *", placeholder="e.g., Prepare Q3 report")
            st.caption("Required. Brief, actionable summary of the task.")

            description = st.text_area("Description", placeholder="Add context, links, or dependencies...")
            st.caption("Optional. One or two lines are plenty.")

        with right:
            assign_type_new = st.radio(
                "Assignment Type",
                ["Group", "Specific Individuals"],
                horizontal=True,
                key="cal_dlg_assign_type"
            )

            if assign_type_new == "Group":
                assignee = st.selectbox("Select Group", GROUP_OPTIONS, key="cal_dlg_group")
                st.caption("Assign to a whole team or group.")
            else:
                assignee_list = st.multiselect("Select Individuals", SPECIFIC_PEOPLE, key="cal_dlg_individuals")
                assignee = ", ".join(assignee_list)
                st.caption("Select one or more specific people.")

            due_date = st.date_input("Due Date", value=prefill_date or datetime.date.today(), key="cal_dlg_due_date")
            st.caption(f"Format: MM-DD-YYYY · {format_mm_dd_yyyy(due_date)}")

            meeting_id = st.text_input(
                "Linked Meeting ID (optional)",
                key="cal_dlg_meeting",
                placeholder="e.g., MOM-20260831-1230"
            )
            st.caption("Paste a meeting ID to trace the origin.")

        submitted = st.form_submit_button("Create Task", type="primary", width="stretch")
        if submitted:
            if not title.strip():
                st.error("Title is required.")
            else:
                success = add_task(title, description, assignee, due_date, meeting_id if meeting_id else None)
                if success:
                    st.session_state.pop("cal_new_task_date", None)
                    st.session_state["task_flash"] = "Task created successfully."
                    st.rerun()

# ------------------------------------------------------------
# METRICS & MEETING LIST (LEFT COLUMN)
# ------------------------------------------------------------
total_team_meetings = len(supabase_records)
total_range_meetings = 0
total_internal_meetings = 0
total_external_meetings = 0
filtered_records = []

for m in supabase_records:
    m_date_raw = str(m.get("meeting_date", ""))
    try:
        parsed_d = datetime.datetime.strptime(m_date_raw[:10], "%Y-%m-%d").date()
        if st.session_state["start_date"] <= parsed_d <= st.session_state["end_date"]:
            filtered_records.append(m)
            total_range_meetings += 1
            m_type = m.get("meeting_type")
            if not m_type:
                client_name_str = str(m.get("client_name", "")).strip().lower()
                raw_payload = m.get("raw_payload", {}) or {}
                meeting_details_dict = raw_payload.get("meeting_details", {}) if isinstance(raw_payload, dict) else {}
                external_atts = meeting_details_dict.get("external_attendees", [])
                if "internal" in client_name_str or "prime" in client_name_str or (not external_atts and not client_name_str):
                    m_type = "Internal"
                else:
                    m_type = "External"
            if str(m_type).strip().lower() == "internal":
                total_internal_meetings += 1
            else:
                total_external_meetings += 1
    except Exception:
        pass

# ------------------------------------------------------------
# BUILD CALENDAR EVENTS & HELPERS
# ------------------------------------------------------------
all_events = build_calendar_events()

def get_meeting_items(meeting):
    table_items = meeting.get("table_items") or []
    if table_items:
        return table_items
    raw = meeting.get("raw_payload") or {}
    details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
    return details.get("action_items") or []

def render_empty_state(message):
    st.markdown(f'<div class="empty-state">{html.escape(message)}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# DASHBOARD CONTROLS (HEADER + DATE SELECTOR INLINE)
# ------------------------------------------------------------
hdr_col, filter_col = st.columns([3.5, 1.3], gap="medium", vertical_alignment="bottom")
with hdr_col:
    render_page_header(
        "Project Echo",
        "Dashboard",
        "Executive operational launchpad for meeting management, daily tracking, and team deliverables.",
    )
with filter_col:
    _dash_range = st.date_input(
        "Dashboard period",
        value=(st.session_state["start_date"], st.session_state["end_date"]),
        key="dash_date_range",
        label_visibility="collapsed",
        help="Filter dashboard metrics and recent meetings by date range",
    )
    st.markdown('<div class="header-border-ext"></div>', unsafe_allow_html=True)

if isinstance(_dash_range, (tuple, list)) and len(_dash_range) == 2:
    if st.session_state["start_date"] != _dash_range[0] or st.session_state["end_date"] != _dash_range[1]:
        st.session_state["start_date"] = _dash_range[0]
        st.session_state["end_date"] = _dash_range[1]
        st.rerun()

# ------------------------------------------------------------
# 1. QUICK ACTIONS
# ------------------------------------------------------------
render_section_header("Quick actions", "Direct access to primary operational workflows.")

qa_c1, qa_c2, qa_c3, qa_c4 = st.columns(4, gap="medium")

with qa_c1:
    with st.container(border=True):
        st.markdown("""
            <div class="qa-badge-row">
                <span class="qa-card-badge">MOM Studio</span>
            </div>
            <div class="qa-card-title">Generate Meeting Minutes</div>
            <p class="qa-card-desc">Transcribe live audio or paste notes to automatically extract topics and generate structured minutes.</p>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_minutes_of_the_meeting.py", label="Generate Minutes", icon=":material/mic:", use_container_width=True)

with qa_c2:
    with st.container(border=True):
        st.markdown("""
            <div class="qa-badge-row">
                <span class="qa-card-badge">Daily Routine</span>
            </div>
            <div class="qa-card-title">Add Daily Log</div>
            <p class="qa-card-desc">Record your daily client engagements, administrative tasks, adhoc work, and meeting recaps.</p>
        """, unsafe_allow_html=True)
        st.page_link("pages/6_notebook.py", label="Add Daily Log", icon=":material/edit_note:", use_container_width=True)

with qa_c3:
    with st.container(border=True):
        st.markdown("""
            <div class="qa-badge-row">
                <span class="qa-card-badge">AI Assistant</span>
            </div>
            <div class="qa-card-title">Ask Echo</div>
            <p class="qa-card-desc">Search across approved meeting transcripts, corporate knowledge base, and client intelligence.</p>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_echo_ai.py", label="Ask Echo", icon=":material/smart_toy:", use_container_width=True)

with qa_c4:
    with st.container(border=True):
        st.markdown("""
            <div class="qa-badge-row">
                <span class="qa-card-badge">Templates & Maps</span>
            </div>
            <div class="qa-card-title">Draft a Document</div>
            <p class="qa-card-desc">Generate branded client presentations, pitch decks, and static property maps from approved templates.</p>
        """, unsafe_allow_html=True)
        st.page_link("pages/8_documents.py", label="Draft Document", icon=":material/description:", use_container_width=True)

st.markdown("<div style='margin-bottom: 0.75rem;'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# 2. MEETING OVERVIEW & RECENT MEETINGS (2 COLUMNS IN SAME ROW)
# ------------------------------------------------------------
col_overview, col_recent = st.columns([1, 1.25], gap="large")

with col_overview:
    render_section_header("Meeting overview", "Volume and classification across the reporting period.")

    st.markdown(f"""
        <div class="kpi-grid-2x2">
            <div class="kpi-card">
                <span class="kpi-title">Total Meetings</span>
                <span class="kpi-value">{total_range_meetings}</span>
                <span class="kpi-sub">In selected period</span>
            </div>
            <div class="kpi-card gold-accent">
                <span class="kpi-title">Team Meetings</span>
                <span class="kpi-value">{total_team_meetings}</span>
                <span class="kpi-sub">All-time recorded archive</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-title">Internal Meetings</span>
                <span class="kpi-value">{total_internal_meetings}</span>
                <span class="kpi-sub">Team & operational</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-title">External Meetings</span>
                <span class="kpi-value">{total_external_meetings}</span>
                <span class="kpi-sub">Client & external partners</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Executive distribution bar for period meetings
    total_meetings_period = max(total_range_meetings, 1)
    internal_pct = int(round((total_internal_meetings / total_meetings_period) * 100)) if total_range_meetings > 0 else 0
    external_pct = int(round((total_external_meetings / total_meetings_period) * 100)) if total_range_meetings > 0 else 0

    st.markdown(f"""
        <div class="overview-ratio-card">
            <div class="overview-ratio-header">
                <span class="overview-ratio-label">Period Distribution</span>
                <span class="overview-ratio-pct">{internal_pct}% Internal · {external_pct}% External</span>
            </div>
            <div class="overview-bar-track">
                <div class="overview-bar-fill internal" style="width: {internal_pct}%;"></div>
                <div class="overview-bar-fill external" style="width: {external_pct}%;"></div>
            </div>
            <div class="overview-ratio-legend">
                <span class="legend-item"><span class="legend-dot navy"></span>Internal ({total_internal_meetings})</span>
                <span class="legend-item"><span class="legend-dot gold"></span>External ({total_external_meetings})</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_recent:
    render_section_header("Recent meetings", "Top 3 latest meeting records with executive summaries.")

    top_3_meetings = (filtered_records if filtered_records else supabase_records)[:3]

    if not top_3_meetings:
        render_empty_state("No meeting records found for this period.")
    else:
        for meeting in top_3_meetings:
            with st.container(border=True):
                client_name = meeting.get("client_name") or meeting.get("location") or meeting.get("meeting_id") or "Meeting Record"
                meeting_id = meeting.get("meeting_id", "")
                m_date = parse_calendar_date(meeting.get("meeting_date"))
                date_str = format_mm_dd_yyyy(m_date) if m_date else "No date"
                prepared_by = meeting.get("prepared_by") or "PRIME Team"

                m_type = meeting.get("meeting_type")
                if not m_type:
                    c_str = str(meeting.get("client_name", "")).strip().lower()
                    raw = meeting.get("raw_payload") or {}
                    raw_details = raw.get("meeting_details", {}) if isinstance(raw, dict) else {}
                    ext_atts = raw_details.get("external_attendees", [])
                    if "internal" in c_str or "prime" in c_str or (not ext_atts and not c_str):
                        m_type = "Internal"
                    else:
                        m_type = "External"
                type_class = "internal" if str(m_type).lower() == "internal" else "external"

                table_items = get_meeting_items(meeting)
                item_count = len(table_items)

                raw_summary = str(meeting.get("summary_md") or "No summary recorded.").replace("### Summary", "").strip()
                summary_snippet = raw_summary[:135] + ("..." if len(raw_summary) > 135 else "")

                st.markdown(f"""
                    <div class="tm-header-row">
                        <span class="tm-type-badge {type_class}">{html.escape(str(m_type))}</span>
                        <span class="tm-date-chip">{date_str}</span>
                    </div>
                    <div class="tm-title" title="{html.escape(str(client_name))}">{html.escape(str(client_name))}</div>
                    <div class="tm-meta">By {html.escape(str(prepared_by))} · {item_count} action item{'s' if item_count != 1 else ''}</div>
                    <div class="tm-summary" style="min-height: auto; margin-bottom: 0.5rem;">{html.escape(summary_snippet)}</div>
                """, unsafe_allow_html=True)
                st.page_link("pages/2_meeting_details.py", label="Open Meeting Record", icon=":material/visibility:", use_container_width=True)
