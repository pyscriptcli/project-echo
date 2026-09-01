# Project Echo

**Project Echo** is a multi-page executive workflow suite for **PRIME Philippines**. It turns raw meeting transcripts into polished Minutes of Meeting (MoM), manages tasks and daily logs, and fronts it all with **Echo** — an AI assistant and agentic co-pilot that can act across the app.

Built with **Streamlit + Supabase**, powered by **DeepSeek / OpenRouter** LLMs, and styled with a warm, editorial navy-and-gold design system.

---

## Features

**? Dashboard** — date-filtered team + personal stats (meetings, tasks, daily-log activity) with a shared "This Month / All" scope.

**? Ask Echo (AI)** — executive Q&A over meetings, knowledge base, and web; file attachments (PDF/DOCX/image); model picker; **Agent mode** (opt-in) that can create/edit tasks, log entries, add knowledge, and more — with **per-user rate limits** and RBAC.

**? Minutes of the Meeting (MoM)** — full transcript → structured deliverables (discussion points, action plans, assignees, deadlines) with human-in-the-loop **evidence grounding** and **recommended "missed" topics**. Exports to Word/PDF.

**? Meeting Details** — browse archives, edit records, export documents.

**? Tasks** — Kanban board, import from meetings, calendar, per-assignee workload.

**? Notebook** — per-user **Notepad** (auto-saved) and **Daily Log** (Client / Admin / Adhoc / Meetings).

**? Atlas** — map / point-of-interest explorer.

**? Admin** — multi-tab console: accounts & password management, usage telemetry, Agent-access RBAC, and per-user token rate limits.

---

## Tech Stack

| Layer | Tech |
| --- | --- |
| Frontend | Streamlit, inline SVG (no emojis), custom CSS |
| Backend / DB | Supabase (Postgres, RLS off; app-enforced per-user authz) |
| Auth | bcrypt against `admin_users`, session timeouts, RBAC (`admin`/`member`) |
| AI | DeepSeek (`deepseek-chat`, reasoning) and OpenRouter (`qwen-vl` vision) |
| Docs | python-docx / reportlab / python-pptx |
| Maps | folium + geopandas + Overpass |

---

## Project Layout

```
project-echo/
├── app.py                    # Dashboard entry point
├── pages/                    # Streamlit multi-page app (number = sidebar order)
│   ├── 0_admin.py            # Admin console (accounts, telemetry, RBAC, limits)
│   ├── 1_minutes_of_the_meeting.py
│   ├── 2_meeting_details.py
│   ├── 3_echo_ai.py          # Ask Echo (AI + agent)
│   ├── 4_tasks.py
│   ├── 5_atlas.py
│   └── 6_notebook.py         # Notepad (auto-save) + Daily Log
├── components/               # Shared UI (sidebar, calendar filters)
├── utils/                    # Data / auth / AI / skills logic
│   ├── auth.py               # login, sessions, RBAC, passwords
│   ├── db.py                 # Supabase client, meeting archives, echo context
│   ├── the notebook/limits/agent/echo_ai modules, etc.
├── skills/                   # AI system prompts + context (see UI/coding skills)
├── supabase/                 # Schema DDL files (run in SQL Editor)
├── tests/                    # unittest suite
├── UI_skill.md               # Design-system guide
└── coding_skills.md          # Coding principles & conventions
```

---

## Quick Start

### 1. Secrets
Create `.streamlit/secrets.toml` (gitignored) with:

```toml
SUPABASE_URL="https://<project-ref>.supabase.co"
SUPABASE_KEY="<service-role-key>"
DEEPSEEK_API_KEY="..."
OPENROUTER_API_KEY="..."   # optional
OPENAI_API_KEY="..."       # for meeting audio transcription
SUPER_ADMIN_USERNAME="your-username"
```

> **Never** commit secrets or `secrets.toml`.

### 2. Install & run

```bash
pip install -r requirements.txt          # Python deps
streamlit run app.py                      # port 8501
```

### 3. Set up the database
Run the DDL files in **`supabase/`** in the Supabase SQL Editor, in order. They are idempotent (safe to re-run). The consolidated **`supabase/full_schema_ddl.sql`** covers everything if you haven't set the tables up yet:

```
supabase/full_schema_ddl.sql    # usage_limits, daily_logs unique, user_usage.event_type,
                                # admin_users.role/can_use_agent, minutes_memory, echo_context
```

Create your first admin user, then set `role='admin'` and `SUPER_ADMIN_USERNAME` in secrets to access the Admin console.

---

## Testing

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Conventions

- **UI:** Follow **`UI_skill.md`** — the navy/gold/charcoal design system, component classes, and "no emoji — SVG/Material icons only, monochrome" rule.
- **Code:** Follow **`coding_skills.md`** — page boilerplate order, secrets-only config, per-user (uuid) data separation, prompts in `skills/prompts/*`, graceful error handling.
- New capabilities should live in `utils/` (logic) + `components/` (UI), be wired into the relevant `pages/`, and be covered by `tests/`.

---

## AI Prompts (`skills/`)

All system prompts live under **`skills/prompts/*.md`** and are loaded by name via `utils/skills.load_prompt(name, **kwargs)`. Edit the `.md` files to tune the AI — no code changes needed.

---

## Roadmap (current focus)

- Agentic Echo: finish the end-to-end tool execution + confirm step.
- Exact LLM token accounting (currently an estimate).
- `skills/superpowers` integration (pending the cloned repo path).

---

_Generated & maintained as part of the Project Echo codebase._
