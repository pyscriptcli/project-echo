# coding_skills — Project Echo coding principles

Agent-facing coding playbook. **Read this before writing or modifying code.** It
codifies how this codebase is structured, its conventions, and the hard rules to
follow (including icons). Keep every edit native to the existing patterns below.

Project Echo is a Streamlit multi-page app for PRIME Philippines, backed by Supabase.
Everything here is verified from the actual code (`app.py`, `components/`, `pages/`,
`utils/`).

---

## 1. Project structure

- **Entry point:** `app.py` (dashboard). Multi-page app; `pages/` are discovered by
  Streamlit, and the number prefix sets sidebar order (e.g. `0_admin`, `1_minutes...`).
- **`components/`** — reusable UI (sidebar, calendar filters). Put new UI widgets here.
- **`utils/`** — data, auth, DB, and AI logic. Put non-UI logic here (e.g. `db.py`,
  `auth.py`, `notebook_db.py`, `echo_ai.py`, `skills.py`).
- **`skills/`** — all AI system prompts (`skills/prompts/*.md`) + shared context
  (`skills/context/*.md`). Prompts live here, never in `.py`.
- **Layout:** new feature = a new function; heavy sections use `st.tabs`, `st.columns`,
  `@st.dialog`, `st.popover` — match the existing idioms.

---

## 2. Page boilerplate (mandatory order)

Every page follows this exact sequence at the top; don't skip or reorder steps:

1. `sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))`
   (or `".."` from `pages/`) so imports resolve.
2. `st.set_page_config(page_title=..., layout="wide", ...)` — must come before other `st`.
3. `require_login()` (or `require_login(require_admin=True)` on admin-only pages).
4. `setup_page_layout()` from `components.sidebar`.

Precede these with the same imports other pages use (`from utils.auth import require_login`,
`from components.sidebar import setup_page_layout`, plus needed `utils.*`).

---

## 3. Config & secrets

- All configuration and credentials come from **Streamlit secrets only**:
  `SUPABASE_URL`, `SUPABASE_KEY`, `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY`,
  `OPENAI_API_KEY`, `SUPER_ADMIN_USERNAME`.
- `.streamlit/secrets.toml` is gitignored — **never commit it, never hardcode keys,
  URLs, or endpoints in source.**
- Read via `st.secrets.get("KEY", default)`. Guard against a missing key with a
  friendly `st.error(...)` and a safe early return.

---

## 4. Data layer

- Cache reads with `@st.cache_data(ttl=..., show_spinner=False)` and
  `@st.cache_resource` for the client. **Always call `.clear()` on the affected cache
  after a write** (see `upsert_log` clearing `fetch_logs_in_range` + `fetch_all_daily_logs`).
- **Per-user separation is enforced in app code (no RLS):** every read/write filters or
  inserts by `user_id`. The auth user id is a **UUID string** from
  `get_current_user()["id"]`, matching `admin_users.id`.
  - **Never cast `user_id` to `int`** — that raises `ValueError` on a UUID.
  - Use helpers like `_current_user_id()` that return the raw string (or `None`).
- Own the failure path: wrap Supabase/network calls in `try/except`, `logger.exception(...)`,
  surface `st.warning("...")`, and return a safe default (empty list/dict) — never crash.

---

## 5. AI layer

- **Never hardcode a system prompt in `.py`.** Put it in `skills/prompts/<name>.md` and
  load it via `from utils.skills import load_prompt`:
  `system_prompt = load_prompt("data_extractor")` or with runtime values, e.g.
  `load_prompt("echo_analyst", current_date=..., citation_rule=..., context=...)`.
- Template files use `{{PLACEHOLDER}}`; `utils/skills.py` substitutes kwargs and drops
  leftover tokens. Tuning the AI = editing the `.md` file, not the code.
- Shared hard-coded context lives in `skills/context/*.md` (see `load_context`).

---

## 6. Error handling

- Wrap DB/network/external calls in `try/except`; log with `logging.getLogger(__name__)`
  (`logger.exception(...)`) and show a user-friendly `st.warning`/`st.error`.
- Return safe defaults on failure so a downstream page never crashes.
- Don't `raise` raw exceptions to the Streamlit UI; don't leak internals (auth errors are
  generic on purpose). Handle parse/conversion with `try/except` (e.g. date parsing) and
  `continue`.

---

## 7. Icons — firm rules (no emoji)

- **No emojis in the UI, ever.** Not in `st.button`, labels, titles, markdown, or code.
- **Two allowed icon sources:**
  1. **Streamlit Material icons** for controls/buttons:
     `st.button("", icon=":material/add:", ...)` — the app already uses
     `:material/add:`, `:material/filter_list:`, `:material/visibility:`,
     `:material/delete:`.
  2. **Inline SVG** for branding/custom marks — the established pattern is
     `SVG_ECHO_LOGO` in `utils/echo_ai.py` (an SVG string embedded via
     `st.markdown(..., unsafe_allow_html=True)`).
- **SVG caution — make sure it never fails to load or renders as raw text:**
  - Always set explicit `width`, `height` (e.g. 12–24), and `viewBox="0 0 24 24"`.
  - Keep it **monochrome** (a single color). Prefer `fill="none"` + `stroke` the theme
    color (e.g. `stroke="#D4AF37"`) + `stroke-width="2"` + `stroke-linecap/linejoin="round"`.
    For text-adjacent SVGs add `style="vertical-align: middle; margin-right: ..."`.
  - Render exactly like existing SVG (embed the string inside an `st.markdown(...,
    unsafe_allow_html=True)` f-string). Do **not** attempt novel embeds that may display
    raw markup.
  - **Test it renders** before considering done.
- **Recommendations when coding:**
  - Reuse an icon already in the app before adding anything new.
  - Prefer a Material icon for controls; reserve inline SVG for brand/custom marks.
  - Always monochrome; match the theme tokens (use `#D4AF37`/`#1A2B4C`/`currentColor`, never
    multi-color fills).
  - If unsure an SVG will render, choose a Material icon instead (safer).

---

## 8. Naming & style

- Functions/`snake_case`; classes same. Private/helpers prefix with `_` (e.g.
  `_current_user_id`, `_load_log`).
- Add type hints to new functions (`user_id: str`, return types) and a short docstring
  describing intent.
- Keep constants grouped (e.g. `COLUMNS`, `SPECIFIC_PEOPLE`, `GROUP_OPTIONS`).
- Don't scatter data/prompts/keys across files — data in `utils/`, UI in `components/`,
  prompts in `skills/`.
- Keep spacing/layout native per `UI_skill.md`.

---

## 9. Suggested additions (coding principles to push toward)

These improve robustness and consistency; not yet fully adopted:

1. **Shared UI/theme module** — centralize tokens + `inject_global_css()` so pages stop
   duplicating `<style>` blocks (see `UI_skill.md` §8.1).
2. **Unit tests for pure helpers** — make `utils/*` helpers importable without a live
   Supabase so logic (stats, prompt loading, date parsing, per-user joins) is tested
   (the app currently has no tests/linter).
3. **Lint/format baseline** — adopt a consistent formatter (e.g. `ruff`/`black`) to keep
   the codebase uniform.
4. **Testable "contract"** — keep pure computation separate from `st.*` rendering so the
   core logic is unit-testable (mirror how dashboard stats were split out).
5. **Icon component** — a small `components/icons.py` exporting the monochrome SVG set,
   so icons are defined once and reused everywhere (single source of truth).

---

Keep this file in sync with the code — if a convention changes, update it here.
