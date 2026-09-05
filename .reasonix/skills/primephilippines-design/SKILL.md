---
name: primephilippines-design
description: Design system skill for primephilippines. Activate when building UI components, pages, or any visual elements. Provides exact color tokens, typography scale, spacing grid, component patterns, and craft rules. Read references/DESIGN.md before writing any CSS or JSX.
---

# primephilippines Design System

You are building UI for **primephilippines**. Dark-themed, neutral palette, sans-serif typography (Cormorant Garamond), compact density on a 4px grid, expressive motion.

## Visual Reference

**IMPORTANT**: Study ALL screenshots below before writing any UI. Match colors, typography, spacing, layout, and motion exactly as shown.

### Homepage

![primephilippines Homepage](screenshots/homepage.png)

> Read `references/DESIGN.md` for full token details.

## Design Philosophy

- **Layered depth** — use shadow tokens to create a sense of physical layering. Each elevation level has a specific shadow.
- **Gradient accents** — gradients are used thoughtfully for emphasis, not decoration.
- **Type pairing** — Cormorant Garamond for body/UI text, Montserrat for headings/display. Never introduce a third typeface.
- **compact density** — 4px base grid. Every dimension is a multiple of 4.
- **neutral palette** — the color temperature runs neutral, matching the sans-serif typography.
- **Restrained accent** — `#0c0c0e` is the only pop of color. Used exclusively for CTAs, links, focus rings, and active states.
- **Expressive motion** — animations are an integral part of the experience. Use spring physics and layout animations.

## Color System

### Core Palette

| Role | Token | Hex | Use |
|------|-------|-----|-----|
| Background | `--background` | `#1b1d1e` | Page/app background |
| Surface | `--surface` | `#003366` | Cards, panels, modals |
| Text Primary | `--text-primary` | `#ffffff` | Headings, body text |
| Text Muted | `--text-muted` | `#c9ab4c` | Captions, placeholders |
| Accent | `--accent` | `#0c0c0e` | CTAs, links, focus rings |

### Status Colors

| Status | Hex | Use |
|--------|-----|-----|
| Success | `#5cb85c` | Confirmations, positive trends |
| Warning | `#b89a3e` | Caution states, pending items |
| Danger | `#c53a3f` | Errors, destructive actions |

### Extended Palette

- **e-global-color-prime_beige:** `#f4f1ec` — Light surface or highlight color
- `#0c1b38`
- **wp--preset--color--black:** `#000000` — Deep background layer or shadow color
- `#002244`
- `#d9534f` — Warm accent — hover glow or decorative highlight
- `#e8e4de` — Light surface or highlight color
- `#b3261e`
- `#d9bc5d`

### CSS Variable Tokens

```css
--border-radius: 0;
--border-top-width: 0px;
--border-right-width: 0px;
--border-bottom-width: 0px;
--border-left-width: 0px;
--border-style: initial;
--border-color: initial;
--border-block-start-width: var(--border-top-width);
--border-block-end-width: var(--border-bottom-width);
--border-inline-start-width: var(--border-left-width);
--border-inline-end-width: var(--border-right-width);
--border-inline-start-width: var(--border-right-width);
--border-inline-end-width: var(--border-left-width);
--e-global-color-primary: #003366;
--e-global-color-secondary: #C9AB4C;
--e-global-color-accent: #0C0C0E;
--e-global-typography-primary-font-family: "Cormorant Garamond";
--e-global-typography-primary-font-weight: 300;
--e-global-typography-primary-font-style: italic;
--e-global-typography-secondary-font-family: "Bebas Neue";
```

## Typography

### Font Stack

- **Cormorant Garamond** — Heading 1, Heading 2, Heading 3
- **Montserrat** — Body, Caption

### Font Sources

```css
@font-face {
  font-family: "Cormorant Garamond";
  src: url("fonts/CormorantGaramond-Bold.ttf") format("truetype");
  font-weight: 700;
}
@font-face {
  font-family: "Cormorant Garamond";
  src: url("fonts/CormorantGaramond-Regular.ttf") format("truetype");
  font-weight: 400;
}
@font-face {
  font-family: "Bebas Neue";
  src: url("fonts/BebasNeue-Regular.ttf") format("truetype");
  font-weight: 400;
}
@font-face {
  font-family: "Montserrat";
  src: url("fonts/Montserrat-Bold.ttf") format("truetype");
  font-weight: 700;
}
@font-face {
  font-family: "Montserrat";
  src: url("fonts/Montserrat-Regular.ttf") format("truetype");
  font-weight: 400;
}
```

### Type Scale

| Role | Family | Size | Weight |
|------|--------|------|--------|
| Heading 1 | Cormorant Garamond | 520px | 700 |
| Heading 2 | Cormorant Garamond | 380px | 700 |
| Heading 3 | Cormorant Garamond | 360px | 700 |
| Body | Montserrat | 11px | 400 |
| Caption | Montserrat | 14px | 400 |

### Typography Rules

- Body/UI: **Cormorant Garamond**, Headings: **Montserrat** — these are the only display fonts
- Max 3-4 font sizes per screen
- Headings: weight 600-700, body: weight 400
- Use color and opacity for text hierarchy, not additional font sizes
- Line height: 1.5 for body, 1.2 for headings

## Spacing & Layout

### Base Grid: 4px

Every dimension (margin, padding, gap, width, height) must be a multiple of **4px**.

### Spacing Scale

`2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24` px

### Spacing as Meaning

| Spacing | Use |
|---------|-----|
| 4-8px | Tight: related items (icon + label, avatar + name) |
| 12-16px | Medium: between groups within a section |
| 24-32px | Wide: between distinct sections |
| 48px+ | Vast: major page section breaks |

### Border Radius

Scale: `2px, 3px, 4px, 5px, 6px, 9px, 10%, 10px, 999px`
Default: `6px`

### Container

Max-width: `1024px`, centered with auto margins.

### Breakpoints

| Name | Value |
|------|-------|
| xs | 479px |
| xs | 480px |
| sm | 481px |
| sm | 520px |
| sm | 560px |
| sm | 600px |
| sm | 640px |
| md | 767px |
| md | 768px |
| lg | 900px |
| lg | 960px |
| lg | 1024px |
| xl | 1025px |
| xl | 1100px |
| 2xl | 99999px |

Mobile-first: design for small screens, layer on responsive overrides.

## Component Patterns

### Card

```css
.card {
  background: #003366;
  border-radius: 6px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.35);
}
```

```html
<div class="card">
  <h3>Card Title</h3>
  <p>Card content goes here.</p>
</div>
```

### Button

```css
/* Primary */
.btn-primary {
  background: #0c0c0e;
  color: #ffffff;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 500;
  transition: opacity 150ms ease;
}
.btn-primary:hover { opacity: 0.9; }

/* Ghost */
.btn-ghost {
  background: transparent;
  border: 1px solid #444444;
  color: #ffffff;
  border-radius: 6px;
  padding: 8px 16px;
}
```

```html
<button class="btn-primary">Get Started</button>
<button class="btn-ghost">Learn More</button>
```

### Input

```css
.input {
  background: #1b1d1e;
  border: 1px solid #444444;
  border-radius: 6px;
  padding: 8px 12px;
  color: #ffffff;
  font-size: 14px;
}
.input:focus { border-color: #0c0c0e; outline: none; }
```

```html
<input class="input" type="text" placeholder="Search..." />
```

### Badge / Chip

```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  background: #003366;
  color: #c9ab4c;
}
```

```html
<span class="badge">New</span>
<span class="badge">Beta</span>
```

### Modal / Dialog

```css
.modal-backdrop { background: rgba(0, 0, 0, 0.6); }
.modal {
  background: #003366;
  border-radius: 999px;
  padding: 24px;
  max-width: 480px;
  width: 90vw;
  box-shadow: 0 0 1px 0 rgba(0,0,0,0.5),0 1px 10px 0 rgba(0,0,0,0.15);
}
```

```html
<div class="modal-backdrop">
  <div class="modal">
    <h2>Dialog Title</h2>
    <p>Dialog content.</p>
    <button class="btn-primary">Confirm</button>
    <button class="btn-ghost">Cancel</button>
  </div>
</div>
```

### Table

```css
.table { width: 100%; border-collapse: collapse; }
.table th {
  text-align: left;
  padding: 8px 12px;
  font-weight: 500;
  font-size: 12px;
  color: #c9ab4c;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #444444;
}
.table td {
  padding: 12px;
  border-bottom: 1px solid #444444;
}
```

```html
<table class="table">
  <thead><tr><th>Name</th><th>Status</th><th>Date</th></tr></thead>
  <tbody>
    <tr><td>Item One</td><td>Active</td><td>Jan 1</td></tr>
    <tr><td>Item Two</td><td>Pending</td><td>Jan 2</td></tr>
  </tbody>
</table>
```

### Navigation

```css
.nav {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
}
.nav-link {
  color: #c9ab4c;
  padding: 8px 12px;
  border-radius: 6px;
  transition: color 150ms;
}
.nav-link:hover { color: #ffffff; }
.nav-link.active { color: #0c0c0e; }
```

```html
<nav class="nav">
  <a href="/" class="nav-link active">Home</a>
  <a href="/about" class="nav-link">About</a>
  <a href="/pricing" class="nav-link">Pricing</a>
  <button class="btn-primary" style="margin-left: auto">Get Started</button>
</nav>
```

### Extracted Components

These components were found in the codebase:

**Button** (`html`)

**Badge** (`html`)

## Page Structure

The following page sections were detected:

- **Navigation** — Top navigation bar (24 items)
- **Hero** — Hero/banner section with headline and CTAs
- **Footer** — Page footer with links and info (16 items)
- **Cta** — Call-to-action section
- **Stats** — Statistics/metrics display
- **Cards** — Grid of 11 card elements (11 items)
- **Features** — Feature/benefit cards grid (4 items)

When building pages, follow this section order and structure.

## Animation & Motion

This project uses **expressive motion**. Animations are part of the design language.

### CSS Animations

- `cmplz-fadein`
- `prime-bounce`
- `prime-marquee`
- `eicon-spin`
- `primeServiceFadeIn`

### Motion Tokens

- **Duration scale:** `0s`, `0.01ms`, `.75s`, `1.25s`, `2s`, `10s`, `20s`, `150ms`, `200ms`, `250ms`, `300ms`, `350ms`, `400ms`, `450ms`, `500ms`, `600ms`, `700ms`, `800ms`, `900ms`, `1000ms`, `1200ms`, `1600ms`
- **Easing functions:** `ease`, `ease-out`, `linear`, `cubic-bezier(0.34,1.56,0.64,1)`, `cubic-bezier(0.2,0.8,0.2,1)`, `cubic-bezier(0.4,0,0.2,1)`, `cubic-bezier(0.25,0.46,0.45,0.94)`
- **Animated properties:** `transform`

### Motion Guidelines

- **Duration:** Use values from the duration scale above. Short (0s) for micro-interactions, long (1600ms) for page transitions
- **Easing:** Use `ease` as the default easing curve
- **Direction:** Elements enter from bottom/right, exit to top/left
- **Reduced motion:** Always respect `prefers-reduced-motion` — disable animations when set

## Depth & Elevation

### Shadow Tokens

- Subtle: `0 0 0 1px rgba(179,38,30,0.35)`
- Subtle: `inset 0 0 0 1px rgba(0,0,0,.1)`
- Subtle: `0 0 0 2px rgba(201,171,76,0.25)`
- Subtle: `inset 0 2px 0 rgba(201,171,76,0.25)`
- Subtle: `inset 0 2px 0 rgba(201,171,76,0.55),inset 0-2px 0 rgba(201,171,76,0.35)`
- Raised (cards, buttons): `0 2px 6px rgba(0,0,0,0.35)`

### Z-Index Scale

`0, 1, 2, 3, 4, 98, 100, 999, 1000, 1001`

Use these exact values — never invent z-index values.

## Anti-Patterns (Never Do)

- **No blur effects** — no backdrop-blur, no filter: blur()
- **No zebra striping** — tables and lists use borders for separation
- **No invented colors** — every hex value must come from the palette above
- **No arbitrary spacing** — every dimension is a multiple of 4px
- **No extra fonts** — only Cormorant Garamond and Montserrat are allowed
- **No arbitrary border-radius** — use the scale: 2px, 3px, 4px, 5px, 6px, 9px, 10px, 999px
- **No opacity for disabled states** — use muted colors instead

## Workflow

1. **Read** `references/DESIGN.md` before writing any UI code
2. **Pick colors** from the Color System section — never invent new ones
3. **Set typography** — Cormorant Garamond, Montserrat only, using the type scale
4. **Build layout** on the 4px grid — check every margin, padding, gap
5. **Match components** to patterns above before creating new ones
6. **Apply elevation** — use shadow tokens
7. **Validate** — every value traces back to a design token. No magic numbers.

## Brand Spec

- **Favicon:** `https://primephilippines.com/wp-content/uploads/2026/05/cropped-prime-icon-32x32.jpeg`
- **Site URL:** `https://primephilippines.com`
- **Brand color:** `#0c0c0e`
- **Brand typeface:** Cormorant Garamond

## Quick Reference

```
Background:     #1b1d1e
Surface:        #003366
Text:           #ffffff / #c9ab4c
Accent:         #0c0c0e
Border:         (not extracted)
Font:           Cormorant Garamond
Spacing:        4px grid
Radius:         6px
Components:     10 detected
```

## When to Trigger

Activate this skill when:
- Creating new components, pages, or visual elements for primephilippines
- Writing CSS, Tailwind classes, styled-components, or inline styles
- Building page layouts, templates, or responsive designs
- Reviewing UI code for design consistency
- The user mentions "primephilippines" design, style, UI, or theme
- Generating mockups, wireframes, or visual prototypes

---

# Full Reference Files

> Every output file is embedded below. Claude has full design system context from /skills alone.

## Design System Tokens (DESIGN.md)

# primephilippines DESIGN.md

> Auto-generated design system — reverse-engineered via static analysis by skillui.
> Frameworks: None detected
> Colors: 20 · Fonts: 2 · Components: 10
> Icon library: not detected · State: not detected
> Primary theme: dark · Dark mode toggle: no · Motion: expressive

## Visual Reference

**Match this design exactly** — study colors, fonts, spacing, and component shapes before writing any UI code.

![primephilippines Homepage](../screenshots/homepage.png)

---

## 1. Visual Theme & Atmosphere

This is a **dark-themed** interface with a neutral tone. Depth is expressed through layered shadows and subtle surface color variation. Typography pairs **Montserrat** for display/headings with **Cormorant Garamond** for body text, creating clear visual hierarchy through type contrast. Spacing follows a **4px base grid** (compact density), with scale: 2, 4, 6, 8, 10, 12, 14, 16px. The accent color **#0c0c0e** anchors interactive elements (buttons, links, focus rings). Motion is expressive — spring physics, layout animations, and staggered reveals are part of the visual language.

---

## 2. Color Palette & Roles

| Token | Hex | Role | Use |
|---|---|---|---|
| e-global-color-text | `#1b1d1e` | background | Page background, darkest surface |
| e-global-color-primary | `#003366` | surface | Card and panel backgrounds |
| wp--preset--color--white | `#ffffff` | text-primary | Headings and body text |
| e-global-color-secondary | `#c9ab4c` | text-muted | Captions, placeholders, secondary info |
| text-muted | `#69727d` | text-muted | Captions, placeholders, secondary info |
| e-global-color-accent | `#0c0c0e` | accent | CTAs, links, focus rings, active states |
| e-global-color-prime_yellow | `#ffbf00` | accent | CTAs, links, focus rings, active states |
| danger | `#c53a3f` | danger | Error states, destructive actions |
| success | `#5cb85c` | success | Success states, positive indicators |
| warning | `#b89a3e` | warning | Warning states, caution indicators |
| info | `#0c1b38` | info | Informational highlights |
| e-global-color-prime_beige | `#f4f1ec` | unknown | Palette color |
| wp--preset--color--black | `#000000` | unknown | Palette color |
| unknown | `#002244` | unknown | Palette color |
| unknown | `#d9534f` | unknown | Palette color |
| unknown | `#e8e4de` | unknown | Palette color |
| unknown | `#b3261e` | unknown | Palette color |
| unknown | `#d9bc5d` | unknown | Palette color |
| unknown | `#5bc0de` | unknown | Palette color |
| unknown | `#f0ad4e` | unknown | Palette color |

### CSS Variable Tokens

```css
--border-radius: 0;
--border-top-width: 0px;
--border-right-width: 0px;
--border-bottom-width: 0px;
--border-left-width: 0px;
--border-style: initial;
--border-color: initial;
--border-block-start-width: var(--border-top-width);
--border-block-end-width: var(--border-bottom-width);
--border-inline-start-width: var(--border-left-width);
--border-inline-end-width: var(--border-right-width);
--border-inline-start-width: var(--border-right-width);
--border-inline-end-width: var(--border-left-width);
--e-global-color-primary: #003366;
--e-global-color-secondary: #C9AB4C;
--e-global-color-accent: #0C0C0E;
--e-global-typography-primary-font-family: "Cormorant Garamond";
--e-global-typography-primary-font-weight: 300;
--e-global-typography-primary-font-style: italic;
--e-global-typography-secondary-font-family: "Bebas Neue";
```


---

## 3. Typography Rules

**Font Stack:**
- **Cormorant Garamond** — Heading 1, Heading 2, Heading 3
- **Montserrat** — Body, Caption

**Font Sources:**

```css
@font-face {
  font-family: "Cormorant Garamond";
  src: url("fonts/CormorantGaramond-Bold.ttf") format("truetype");
  font-weight: 700;
}
@font-face {
  font-family: "Cormorant Garamond";
  src: url("fonts/CormorantGaramond-Regular.ttf") format("truetype");
  font-weight: 400;
}
@font-face {
  font-family: "Bebas Neue";
  src: url("fonts/BebasNeue-Regular.ttf") format("truetype");
  font-weight: 400;
}
@font-face {
  font-family: "Montserrat";
  src: url("fonts/Montserrat-Bold.ttf") format("truetype");
  font-weight: 700;
}
@font-face {
  font-family: "Montserrat";
  src: url("fonts/Montserrat-Regular.ttf") format("truetype");
  font-weight: 400;
}
```

| Role | Font | Size | Weight |
|---|---|---|---|
| Heading 1 | Cormorant Garamond | 520px | 700 |
| Heading 2 | Cormorant Garamond | 380px | 700 |
| Heading 3 | Cormorant Garamond | 360px | 700 |
| Body | Montserrat | 11px | 400 |
| Caption | Montserrat | 14px | 400 |

**Typographic Rules:**
- Limit to 2 font families max per screen
- Use **Cormorant Garamond** for body/UI text, **Montserrat** for display/headings
- Maintain consistent hierarchy: no more than 3-4 font sizes per screen
- Headings use bold (600-700), body uses regular (400)
- Line height: 1.5 for body text, 1.2 for headings
- Use color and opacity for secondary hierarchy, not additional font sizes


---

## 4. Component Stylings

### Layout (1)

**Footer** — `html`

### Navigation (1)

**Navigation** — `html`

### Data Display (3)

**Card** — `html`

**Badge** — `html`

**List** — `html`

### Data Input (2)

**Button** — `html`
- Animation: 

**Input** — `html`
- State: :focus, :placeholder

### Media (3)

**Image** — `html`

**Icon** — `html`

**Map/Canvas** — `html`



---

## 5. Layout Principles

- **Base spacing unit:** 4px
- **Spacing scale:** 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24
- **Border radius:** 2px, 3px, 4px, 5px, 6px, 9px, 10%, 10px, 999px
- **Max content width:** 1024px

**Spacing as Meaning:**
| Spacing | Use |
|---|---|
| 4-8px | Tight: related items within a group |
| 12-16px | Medium: between groups |
| 24-32px | Wide: between sections |
| 48px+ | Vast: major section breaks |


---

## 6. Depth & Elevation

### Flat — subtle depth hints

- `0 0 0 1px rgba(179,38,30,0.35)`
- `inset 0 0 0 1px rgba(0,0,0,.1)`
- `0 0 0 2px rgba(201,171,76,0.25)`

### Raised — cards, buttons, interactive elements

- `0 2px 6px rgba(0,0,0,0.35)`
- `0 0 0 3px rgba(201,171,76,0.25)`
- `0 0 0 5px rgba(201,171,76,0.08)`

### Floating — dropdowns, popovers, modals

- `0 0 1px 0 rgba(0,0,0,0.5),0 1px 10px 0 rgba(0,0,0,0.15)`
- `0 2px 12px rgba(0,0,0,0.08),0 1px 0 rgba(201,171,76,0.3)`
- `0 2px 12px rgba(0,0,0,0.08)`

### Overlay — full-screen overlays, top-level dialogs

- `0 12px 40px rgba(0,0,0,0.4)`
- `0 8px 30px rgba(0,0,0,0.12)`
- `0 12px 40px rgba(0,0,0,0.14)`

### Z-Index Scale

`0, 1, 2, 3, 4, 98, 100, 999, 1000, 1001`



---

## 7. Animation & Motion

This project uses **expressive motion**. Animations are an integral part of the experience.

### CSS Animations

- `@keyframes cmplz-fadein`
- `@keyframes prime-bounce`
- `@keyframes prime-marquee`
- `@keyframes eicon-spin`
- `@keyframes primeServiceFadeIn`
- `@keyframes prime-marker-pulse`
- `@keyframes prime-kc-pulse`
- `@keyframes prime-kc-kenburns`

### Animated Components

- **Button**: 

### Motion Guidelines

- Duration: 150-300ms for micro-interactions, 300-500ms for page transitions
- Easing: `ease-out` for enters, `ease-in` for exits
- Always respect `prefers-reduced-motion`


---

## 8. Do's and Don'ts

### Do's

- Use `#0c0c0e` for interactive elements (buttons, links, focus rings)
- Use `#1b1d1e` as the primary page background
- Pair **Cormorant Garamond** (body) with **Montserrat** (display) — these are the only allowed fonts
- Follow the **4px** spacing grid for all margins, padding, and gaps
- Use the defined shadow tokens for elevation — see Section 6
- Use border-radius from the scale: 2px, 3px, 4px, 5px, 6px
- Reuse existing components from Section 4 before creating new ones

### Don'ts

- Don't introduce colors outside this palette — extend the design tokens first
- Don't introduce additional font families beyond Cormorant Garamond and Montserrat
- Don't use arbitrary spacing values — stick to multiples of 4px
- Don't create custom box-shadow values outside the system tokens
- Don't use arbitrary border-radius values — pick from the defined scale
- Don't duplicate component patterns — check Section 4 first
- Don't use backdrop-blur or blur effects

### Anti-Patterns (detected from codebase)

- No blur or backdrop-blur effects
- No zebra striping on tables/lists


---

## 9. Responsive Behavior

| Name | Value | Source |
|---|---|---|
| xs | 479px | css |
| xs | 480px | css |
| sm | 481px | css |
| sm | 520px | css |
| sm | 560px | css |
| sm | 600px | css |
| sm | 640px | css |
| md | 767px | css |
| md | 768px | css |
| lg | 900px | css |
| lg | 960px | css |
| lg | 1024px | css |
| xl | 1025px | css |
| xl | 1100px | css |
| 2xl | 99999px | css |

**Approach:** Use `@media (min-width: ...)` queries matching the breakpoints above.


---

## 10. Agent Prompt Guide

Use these as starting points when building new UI:

### Build a Card

```
Background: #003366
Border: 1px solid var(--border)
Radius: 6px
Padding: 16px
Font: Cormorant Garamond
Use shadow tokens from Section 6.
```

### Build a Button

```
Primary: bg #0c0c0e, text white
Ghost: bg transparent, border var(--border)
Padding: 8px 16px
Radius: 6px
Hover: opacity 0.9 or lighter shade
Focus: ring with #0c0c0e
```

### Build a Page Layout

```
Background: #1b1d1e
Max-width: 1024px, centered
Grid: 4px base
Responsive: mobile-first, breakpoints from Section 9
```

### Build a Stats Card

```
Surface: #003366
Label: #c9ab4c (muted, 12px, uppercase)
Value: #ffffff (primary, 24-32px, bold)
Status: use success/warning/danger from Section 2
```

### Build a Form

```
Input bg: #1b1d1e
Input border: 1px solid var(--border)
Focus: border-color #0c0c0e
Label: #c9ab4c 12px
Spacing: 16px between fields
Radius: 6px
```

### General Component

```
1. Read DESIGN.md Sections 2-6 for tokens
2. Colors: only from palette
3. Font: Cormorant Garamond, type scale from Section 3
4. Spacing: 4px grid
5. Components: match patterns from Section 4
6. Elevation: shadow tokens
```

## Bundled Fonts (fonts/)

The following font files are bundled in the `fonts/` directory:

- `fonts/BebasNeue-Regular.ttf`
- `fonts/CormorantGaramond-Bold.ttf`
- `fonts/CormorantGaramond-Light.ttf`
- `fonts/CormorantGaramond-Medium.ttf`
- `fonts/CormorantGaramond-Regular.ttf`
- `fonts/CormorantGaramond-SemiBold.ttf`
- `fonts/Montserrat-Black.ttf`
- `fonts/Montserrat-Bold.ttf`
- `fonts/Montserrat-ExtraBold.ttf`
- `fonts/Montserrat-ExtraLight.ttf`
- `fonts/Montserrat-Light.ttf`
- `fonts/Montserrat-Medium.ttf`
- `fonts/Montserrat-Regular.ttf`
- `fonts/Montserrat-SemiBold.ttf`
- `fonts/Montserrat-Thin.ttf`

Use these local font files in `@font-face` declarations instead of fetching from Google Fonts.

## Homepage Screenshots (screenshots/)

![homepage.png](screenshots/homepage.png)

