# skills — AI Skills, Context & Prompts

Dedicated home for Project Echo's AI assets. Everything the AI needs to
be more robust and maximized lives here, organized so the app can call a
named skill/prompt instead of scattering text in code.

## Layout

```
skills/
├── README.md
├── context/                 # shared, hard-coded context (org baseline, style rules)
│   └── company_baseline.md
└── prompts/                 # one file per AI skill (system prompt templates)
    ├── echo_analyst.md       # Echo chat analyst (long-form Q&A, knowledge proposal)
    ├── data_extractor.md     # extraction from text/PDF/DOCX/image → JSON items
    ├── global_analyst.md     # global team-archive Q&A analyst
    ├── meeting_metadata.md   # transcript → meeting metadata JSON (type/client/attendees)
    ├── topic_extractor.md    # transcript → 4–7 discussion topics
    ├── minutes_generator.md  # transcript + user topics → evidence-matched deliverables (+ missed-point recs)
    ├── ask_echo.md           # Ask Echo: answer + mutate the MoM table
    └── minutes_style_learner.md  # mine approved minutes → style profile (few-shot learning)
```

## Notes

- Template files use `{{PLACEHOLDER}}` tokens. At call time, Python loads the
  file and substitutes the placeholders (see `utils/skills.py`).
- Keep prompts here, not in `utils/*.py`. `utils/*.py` only call
  `load_prompt("name", ...)`.
- Edit these files freely to tune the AI without touching Python code.
