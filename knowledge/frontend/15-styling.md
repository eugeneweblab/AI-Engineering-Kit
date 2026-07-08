---
id: frontend/15-styling
topic: frontend
slug: styling
title: "Styling"
type: doc
order: 15
status: ready
tags: [frontend, styling]
related: [frontend/16-css-architecture, frontend/03-design-systems, frontend/10-responsive-design, frontend/09-accessibility, frontend/17-animations]
when_to_use: "Read before choosing a styling approach or writing component styles, tokens, or theming."
---
# Styling

## Purpose

This document defines how to apply visual styles to components: choosing a styling
approach, using design tokens, handling theming and dark mode, and writing CSS that scales
without specificity wars. It covers the tactical layer — how a single component gets its
colors, spacing, and states — while [CSS architecture](16-css-architecture.md) covers how
styles are organized across the whole codebase.

Good styling is consistent, themeable, and predictable: a value comes from a token, a
state is expressed declaratively, and one component's styles cannot leak into another's.

## Why It Matters

Styling is where design intent meets the browser, and it is deceptively easy to get into a
state nobody can safely change. Hardcoded hex values scattered across hundreds of files
make a rebrand a multi-week hunt. Deeply nested selectors and `!important` create
specificity wars where the only way to override a style is to escalate, permanently. CSS is
global by default, so a rule written for one component silently restyles another. These
problems compound: the codebase becomes one where every visual change risks breaking
something unrelated, and velocity collapses. Disciplined styling — tokens, scoping, low
specificity — is what keeps the UI changeable.

## Core Principles

- **Values come from tokens, not literals.** Colors, spacing, radii, typography, and
  z-index live as CSS custom properties or design-system tokens. A raw `#3b82f6` in a
  component is a bug waiting for a rebrand.
- **Scope styles to the component.** Use CSS Modules, scoped styles, or utility classes so
  a rule cannot leak. Global selectors (`.button`, bare element selectors) are reserved for
  a small, deliberate reset/base layer.
- **Keep specificity flat and low.** Prefer single-class selectors. `!important` and deep
  descendant chains are a signal the architecture is fighting itself.
- **Express state declaratively.** Drive variants with `data-*` attributes or classes
  (`data-state="loading"`), not by toggling inline styles imperatively in JS.
- **Theme with variables, not duplicated stylesheets.** Dark mode and brand themes should
  reassign token values at the `:root`/`[data-theme]` level, not fork every component's CSS.

## Best Practices

- Define a token layer of CSS custom properties (`--color-surface`, `--space-4`,
  `--radius-md`) and reference them everywhere. Themes override the variables; components
  never change.
- Pick **one** primary styling approach per project (CSS Modules, Tailwind, or a
  compiled-CSS-in-JS solution) and stick to it. Mixing three approaches is how you get
  conflicting cascades.
- Style states with pseudo-classes and attributes (`:hover`, `:focus-visible`,
  `:disabled`, `[aria-current]`) rather than JS-added classes where the browser can do it.
  Always style `:focus-visible` — never remove focus outlines without a visible replacement.
- Respect user preferences: honor `prefers-color-scheme`, `prefers-reduced-motion`, and
  `prefers-contrast` via media queries.
- Prefer logical properties (`margin-inline`, `padding-block`, `inset`) so layouts work in
  RTL languages without a second stylesheet.
- Keep runtime style computation out of the hot path — avoid heavy runtime CSS-in-JS that
  serializes styles on every render; prefer zero-runtime/compiled solutions or plain CSS.
- Never hardcode the same magic number in many places; if two spacings must match, they
  must reference the same token.

## Examples

**Good Example** — tokenized, scoped, theme-aware

```css
/* tokens.css — one source of truth, themes just reassign the variables */
:root {
  --color-surface: #ffffff;
  --color-text: #111827;
  --space-4: 1rem;
  --radius-md: 8px;
}
:root[data-theme="dark"] {
  --color-surface: #111827;
  --color-text: #f9fafb;
}

/* Button.module.css — single class, references tokens, styles focus */
.button {
  background: var(--color-surface);
  color: var(--color-text);
  padding: var(--space-4);
  border-radius: var(--radius-md);
}
.button:focus-visible {
  outline: 2px solid var(--color-text); /* keyboard focus stays visible */
}
```

```tsx
import styles from "./Button.module.css"; // scoped: class names are hashed, cannot leak
<button className={styles.button} data-state={loading ? "loading" : "idle"}>Save</button>
```

**Bad Example** — hardcoded values, global leak, specificity war

```css
/* global, unscoped: this restyles EVERY .button on the page */
.button {
  background: #ffffff; /* hardcoded — dark mode and rebrand both break */
  color: #111827;
  padding: 16px;       /* magic number duplicated across the codebase */
}
/* the only way anyone found to override the above */
.card .button.primary {
  background: #3b82f6 !important; /* specificity war escalates from here */
  outline: none;                 /* focus outline removed with no replacement */
}
```

## Common Mistakes

- Hardcoding colors, spacing, and radii instead of referencing tokens, making theming and
  rebrands a manual search-and-replace.
- Writing global, unscoped selectors that leak and collide across components.
- Reaching for `!important` and deep descendant selectors to win specificity battles.
- Removing `:focus` outlines for aesthetics without a visible `:focus-visible` replacement.
- Duplicating stylesheets for dark mode instead of reassigning token variables.
- Toggling inline styles from JS for states the browser could handle with a pseudo-class.
- Mixing several styling systems in one project, producing an unpredictable cascade.

## Production Tips

- Enforce the token layer with a lint rule (e.g. `stylelint` custom-property rules) that
  flags raw hex and pixel literals in component CSS.
- Set the theme attribute on `<html>` before first paint (inline script or SSR) to avoid a
  flash of the wrong theme.
- Audit computed specificity in review — a rising count of `!important` is a leading
  indicator that the styling architecture needs attention.

## AI Review Checklist

- Do colors, spacing, radii, and typography come from tokens rather than literals?
- Are component styles scoped (CSS Modules/utilities), with global selectors limited to a base layer?
- Is specificity flat, with no `!important` used to win overrides?
- Is `:focus-visible` styled, and are focus outlines never removed without a replacement?
- Are dark mode and themes implemented by reassigning variables, not forking stylesheets?
- Are `prefers-color-scheme` and `prefers-reduced-motion` honored?
- Does the project use a single, consistent styling approach?

## Related

- `knowledge/frontend/16-css-architecture.md`
- `knowledge/frontend/03-design-systems.md`
- `knowledge/frontend/10-responsive-design.md`
- `knowledge/frontend/09-accessibility.md`
- `knowledge/frontend/17-animations.md`
