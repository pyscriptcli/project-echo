# UI_skill — Project Echo native UI/UX guide

Agent-facing playbook. **Read this before building or editing any page, component,
or style in this app.** Goal: every new feature looks native and has strong UI/UX —
reuse the existing design system instead of inventing new tokens, classes, or layout
patterns.

Project Echo is a Streamlit multi-page app for PRIME Philippines. Everything that
follows is verified from the actual code (`app.py`, `components/sidebar.py`, `pages/*`).

---

## 1. Look & feel (the essentials)

- Warm, editorial, monochrome "executive brief" aesthetic: a clean beige canvas with
  warm-brown ink and tan accents. Headings are elegant serif italics; body/UI text is
  clean sans. Flat & edgy: 0 radius, no shadows, no gridlines.
- Pages hide Streamlit chrome (default header, footer, menu) and render custom cards.
- Every custom control is styled via inline `<style>` inside `st.markdown(...)`, the
  shared `components/theme.py`, or page CSS. Keep this approach; don't add UI frameworks.

---

## 2. Color tokens (use these exact hexes)

| Token | Hex | Use |
| --- | --- | --- |
| canvas | `#F9F8F6` | page background (lightest, dominant) |
| borders | `#EFE9E3` | separators, card borders, hairlines |
| secondary | `#D9CFC7` | secondary borders, input borders, disabled/badges |
| accent / buttons | `#C9B59C` | buttons, active highlights, accents |
| ink / headings | `#412D15` | fonts, section titles, key numbers, button text |
| deep ink | `#1F150C` | hover states, deepest accent |
| muted ink | `#8A7A5F` | secondary captions / helper text |
| surface | `#FFFFFF` | cards / chips / panels |
| danger | `#A94442` (bg `#FDF0EF`) | overdue / destructive states |
| due-today | `#8C6D23` (bg `#FFF9E8`) | "due today" chips |
| status dot | `#6366F1` | meeting / "dot-meeting" indicator |

Rules: never introduce a new color unless no token fits. Prefer the tokens above.

---

## 3. Typography

- **Titles / headers:** `'Playfair Display', serif` — italic, weight 500–600, color
  `#1A2B4C`. Use the app's `section-title` pattern or `font-style: italic`.
- **Body / UI / buttons:** `'Inter', sans-serif` — weights 400/500/600.
- **Brand accent font (occasional):** `'Cormorant Garamond', 'Playfair Display', serif`
  (used in sidebar brand). `Montserrat` appears on specific pages — prefer Inter for new UI.
- **Hierarchy:** one dominant headline → supporting figures → tables. Don't build walls
  of equal-sized numbers; use size/weight to establish reading order.

---

## 4. Reusable components (copy these patterns, don't invent new ones)

### Cards & panels
- Design direction: **flat & edgy** — `border-radius:0` everywhere, `box-shadow:none`, hairline `1px solid rgba(26,43,76,0.14)` borders, and **large gridlines** on the cream canvas (96px major + 24px fine, `rgba(26,43,76,0.10)`/`0.05`) via `components/theme.py`.
- `.left-card` — white panel, hairline border, `0` radius, **no shadow**, `padding:1rem`. `.left-card-scroll` = scrollable variant.
- `.meeting-card` with `.meeting-title` / `.meeting-sub` / `.meeting-desc`.
- `.task-card` with `.task-card-header` / `.task-card-desc` / `.task-card-footer`,
  `.task-card-title`, status dot `.task-status-dot .dot-todo|.dot-in_progress|.dot-done|.dot-meeting`.
- `.kanban-card`, `.kanban-header .label`, `.board-column-header` (task board), `.day-col-header`.

### KPI / metric tiles
- `.kpi-grid` (grid of tiles) → `.kpi-card` → `.kpi-title` + `.kpi-value`.
  Use e.g. `grid-template-columns:repeat(4,1fr)` for a compact row.

### Sections
- `.section-title` (Playfair italic navy) + `.section-caption` (muted) — the standard
  page/panel heading pair. Prefer these over raw `<h2>`/`<h3>`.

### Status / people
- `.assignee-avatar` — circular initials chip.
- `.due-chip` with `.overdue` / `.due-today` states for due dates.
- `.status-chip` (suggested default for done/in-progress/overdue — see §6).

### Empty states
- `.empty-state` — centered, italic, muted (`#a0aec0`), compact `padding:0.75rem 0`.

### Sidebar (unified via `components/sidebar.py`)
- `.sb-brand`, `.sb-brand-sub`, `.sb-brand-rule`, `.sb-user`, `.sb-user-avatar`,
  `.sb-user-name`, `.sb-footer-scope`. Nav items use `st.page_link` with material icons.
- Page nav always goes through `setup_page_layout()` — never render your own sidebar.

---

## 5. Buttons (deep charcoal + gold, squared/flat, no shadow)

Global button style is applied via `components/theme.py` (`inject_global_css`) + the sidebar.
- Base: `background:#111A2B`, `color:#FFF`, `border:1px solid #D4AF37`,
  `border-radius:0` (flat/edgy), Inter 600, `letter-spacing:0.02em`, `text-transform:uppercase`, **no shadow**.
- Hover: `background:#1A263D`, `border-color:#E6C44D`, still no shadow.
- Secondary variant: same charcoal/gold but gold text (`#E6C44D`).
- Cover **all** button types with the same theme: `stButton`, `stPopover` toggle,
  `stFormSubmitButton`, `stDownloadButton`. Don't let any button look unstyled.

---

## 6. Layout idioms (native to Streamlit, matches the app)

- **Columns:** `st.columns` with sensible ratios — the dashboard uses `[1, 2.5]`,
  filter rows `[3.2, 1, 1]`, `[2.6, 1.4, 0.55, 1.6]`, toolbars `[1.5,1.5,4,1.5,1.5]`.
  Scale relative, prefer smaller gaps (`gap="small"`/`"medium"`).
- **Tabs:** `st.tabs([...])` for distinct views on one page (Tasks, Notebook, Dashboard).
- **Date ranges / filters:** `st.popover` with presets + custom `st.date_input`; or a
  top-level date picker + "This Month"/"All" buttons (dashboard). Default to current month.
- **Dialogs:** `@st.dialog` for modal forms (task create/update, notes gallery).
- **Segmented control:** `st.segmented_control` for Day/Week/Month and view toggles.
- **Equal-height panels:** wrap columns with `.sync-height-scope`.
- **Charts:** matplotlib in theme color (navy bars, gold current highlight); avoid garish
  palettes. CSS bar "charts" for status/category proportional fills.

### Spacing scale
Keep margins/padding on a 0.25/0.5/0.75/1/1.5rem scale; avoid ad-hoc values. Cards ~0.5–1rem.

---

## 7. Rules for native UI (do / don't)

- **Do** reuse tokens + component classes in §2–§4. **Don't** introduce new colors/classes
  until you've checked nothing fits.
- **Do** use `.section-title`/`.section-caption` for headings. **Don't** drop in raw bare
  headers that break the editorial style.
- **Do** keep visual hierarchy: a clear headline → supporting numbers/charts → detail table.
- **Do** style every interactive element (buttons, popovers, download buttons) with the
  charcoal/gold round theme. **Don't** leave default Streamlit widgets unstyled.
- **Do** keep spacing consistent (spacing scale), equal panel heights, compact empty states.
- **Do** route page chrome through `setup_page_layout()`.
- **Do** make new features responsive to existing page patterns (tabs, columns, dialogs)
  rather than a brand-new interaction model.

---

## 8. Suggested additions (high-value, native-feel improvements)

These are recommended directions to push UI/UX quality — not yet implemented everywhere:

1. **Shared theme module** — centralize tokens + a single `inject_global_css()` so pages
   stop duplicating `<style>` blocks. Improves consistency and cuts divergence risk.
2. **Reusable `metric_tile(label, value, accent=...)` helper** — standardize KPI cards so
   every page's metrics look identical.
3. **`status-chip` component** — one consistent pill for Done / In Progress / Overdue /
   Meeting (reuse `due-chip` styling language) instead of per-page variations.
4. **Icon system consistency** — settle on Material icons for controls; reserve inline
   SVG for Echo/logo assets only.
5. **Empty-state component** with an icon + action hint, so empty panels read deliberately.
6. **Grid card layout** (`.card-grid`) for gallery-style pages (notebook gallery reuse).
7. **Consistent chart styling helper** — a small matplotlib wrapper (navy/gold, no top/right
   spines) so all charts match.
8. **Focus/hover micro-interactions** — subtle transitions (0.2s) and gold hovers on all
   clickable cards, matching the button hover language.
9. **Accessibility pass** — sufficient contrast for muted text, larger tap targets, and
   visible focus states on interactive controls.

Keep this file in sync with the app — if a token or pattern changes, update it here.
