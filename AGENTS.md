# Project Echo — AGENTS.md

Streamlit multi-page meeting-management suite for PRIME Philippines ("Echo"): meeting minutes (MOM), task board, calendar, AI assistant chat, GIS map (Atlas), notebook, and admin console, backed by Supabase.

## Project
- **Stack:** Python + Streamlit; Supabase (Postgres) for data & auth; DeepSeek / OpenRouter LLM APIs; folium + geopandas + Overpass API for maps; python-docx / reportlab / python-pptx for exports; html2image + selenium for MOM rendering.
- **Entry point:** `app.py` (Dashboard) — multipage app reads `pages/` (number prefix = sidebar order).
- **Dev:** `.devcontainer/devcontainer.json` (Codespaces) installs `packages.txt` (apt: gdal, proj, spatialindex) + `requirements.txt`, then `streamlit run app.py`.

## Commands
- Run: `streamlit run app.py` (port 8501)
- Install Python deps: `pip install -r requirements.txt` (Linux system deps: `xargs apt install -y <packages.txt`)
- **No tests and no linter configured** — don't claim any.

## Architecture
- `app.py` — Dashboard: global CSS theme (navy/gold), calendar + task widgets, task CRUD helpers; top area has a date-filtered, two-tab stats dashboard (Team Overview / Personal Stats) using `utils/notebook_db.fetch_all_daily_logs` and matplotlib charts.
- `components/sidebar.py` — `setup_page_layout()`: shared nav, header, global styling; call on every page.
- `utils/auth.py` — bcrypt login vs Supabase `users` table, session handling, `require_login(require_admin=False)`, `is_admin()`, `add_admin_user`, usage tracking.
- `utils/db.py` — cached Supabase client; tables `meeting_archives` and `echo_context` (team/jargon/projects/knowledge maps, upserted via `upsert_echo_context`).
- `utils/echo_ai.py` — the Echo assistant: PDF/DOCX/image text extraction, rapidfuzz KB alignment, DeepSeek/OpenRouter chat calls, chat UI (`render_echo_chat`), context-popup dialog.
- `utils/ai.py` — older global-archive Q&A helper (DeepSeek only).
- `utils/skills.py` — `load_prompt(name, **kwargs)` / `load_context(name)` read AI system prompts from `skills/prompts/*.md` and context from `skills/context/*.md` (resolved repo-root-relative, CWD-independent); substitutes `{{KEY}}` placeholders.
- `utils/notebook_db.py` — per-user Supabase persistence for notebook (Notepad `notepad_docs`, Daily Log `daily_logs`) and team-wide `fetch_all_daily_logs(start,end)` for dashboard stats; keyed on `user_id` (uuid = `admin_users.id`).
- `skills/` — dedicated home for all AI system prompts + hard-coded context; `.py` files only call `load_prompt("name")`, never hardcode prompt text.
- `utils/calendar_helpers.py`, `components/calendar_filters.py` — calendar event fetch + filter widgets.
- `pages/` — `0_admin.py` (user mgmt), `1_minutes_of_the_meeting.py` (MOM editor/exports), `2_meeting_details.py` (records + PDF/DOCX exports), `3_echo_ai.py` (chat), `4_tasks.py` (task board), `5_atlas.py` (map/POI explorer, `fetch_pois` Overpass), `6_notebook.py`.
- `mom_templates/mom_template_2.html` — HTML template for MOM rendering.

## Conventions
- Every page: `st.set_page_config(...)` first, then `sys.path.append(project root)`, then `require_login()` and `setup_page_layout()`.
- **Coding:** Follow **`coding_skills.md`** (project structure, data/AI/error conventions, naming, and the icon rules: **no emojis — SVG/Material icons only, monochrome**).
- **UI/UX:** Any new or edited UI must follow **`UI_skill.md`** at the repo root (design tokens, component classes, layout idioms). Reuse its tokens/components; don't introduce new colors/classes unless nothing fits.
- Config only via Streamlit secrets (`SUPABASE_URL`, `SUPABASE_KEY`, `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`) — `.streamlit/secrets.toml` is gitignored; never commit secrets.
- Design tokens (inline CSS via `st.markdown`): bg cream `#F5F1E8`, headings navy `#1A2B4C`, buttons charcoal `#111A2B` with gold accent `#D4AF37`; fonts Playfair Display (titles) + Inter (body). Keep these tokens consistent across pages.
- Heavier UI is custom HTML/CSS in `st.markdown` with classes like `left-card`, `section-title`, `kpi-grid` — check existing pages before introducing a new pattern.
- Cache DB reads with `@st.cache_data`/`@st.cache_resource`; call `.clear()` after writes.

## Notes
- (stub — add project-specific gotchas here as they surface)
