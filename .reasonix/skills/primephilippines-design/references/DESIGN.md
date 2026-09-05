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
