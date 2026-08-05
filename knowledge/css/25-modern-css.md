---
id: css/25-modern-css
topic: css
slug: modern-css
title: "Modern CSS"
type: doc
order: 25
status: ready
tags: [css, modern-css, padding-block, margin-inline, aspect-ratio, container, "@layer", "@container"]
related: [css/19-container-queries, css/20-css-variables, css/26-browser-compatibility, css/07-grid, css/28-best-practices]
when_to_use: "Read before reaching for a preprocessor, a JS layout hack, or a utility library to do something CSS now does natively."
---
# Modern CSS

## Purpose

This document catalogs the CSS features that are baseline-available in 2026 and changes
how you should solve common problems. Much of the tooling and workarounds written before
2022 — Sass for nesting and variables, JavaScript for "is this element in view", brittle
`padding-top` hacks for aspect ratios — is now obsolete. Reaching for the native feature
is shorter, faster, and one less dependency. This is the "what to use instead" reference.

## Why It Matters

Agents trained on years of Stack Overflow answers default to old patterns: a JS resize
observer where `@container` works, a `float` clearfix, a `::before` spacer for a 16:9
video. That code still runs, but it is heavier, slower, and harder to maintain than the
native equivalent, and it drags in dependencies that need patching forever. Native CSS
runs on the browser's optimized layout engine, needs no build step, and cannot go stale.
Knowing the modern primitive is the difference between a five-line rule and a fifty-line
component.

## Core Principles

- **Prefer the platform.** If a browser feature does the job, use it instead of a library
  or a JS shim. The cost of a dependency is paid on every install and every audit forever.
- **Cascade layers over specificity wars.** `@layer` lets you order stylesheets
  deterministically so overrides are intentional, not accidents of selector weight.
- **Query the container, not the viewport, for components.** A card should respond to the
  space *it* is given, which makes it reusable in a sidebar or a full-width hero.
- **Use logical properties for anything text-directional.** `margin-inline`, `padding-block`,
  and `inset` adapt to right-to-left and vertical writing modes for free.
- **Let CSS do color math and relative values.** `color-mix()`, relative color syntax, and
  `clamp()` compute at render time, so one source value derives a whole scale.

## Best Practices

- Replace preprocessor nesting with **native CSS nesting** (`&`); you no longer need Sass
  purely to nest. Keep nesting shallow (one or two levels) to avoid specificity creep.
- Use **`@layer`** (reset, base, components, utilities) so late layers win regardless of
  selector specificity — this ends most `!important` battles. See
  [architecture](21-architecture.md).
- Use **container queries** (`@container`) for component-level responsiveness and
  **`cqi`/`cqw`** units for container-relative sizing. See
  [container queries](19-container-queries.md).
- Use **`:has()`** for parent/previous-sibling selection (e.g. `label:has(+ input:invalid)`)
  instead of adding JS state classes.
- Use **`clamp(min, preferred, max)`** for fluid type and spacing so values scale with the
  viewport without media-query steps.
- Use **`aspect-ratio`** for media boxes instead of the padding-hack; use **`gap`** on flex
  and grid instead of margins between children.
- Use **logical properties** (`margin-inline`, `padding-block`, `inset-inline-start`) and
  **`color-mix()` / relative color** to derive hover and tint variants from one base color.
- Adopt **`:is()` / `:where()`** to group selectors; remember `:where()` has zero specificity,
  which is what you usually want for resets.

## Examples

**Good Example** — native features replacing tooling

```css
@layer components {                 /* deterministic order, no specificity fights */
  .card {
    container-type: inline-size;    /* children can query THIS card's width */
    aspect-ratio: 16 / 9;           /* no padding-top hack */
    padding: clamp(1rem, 4cqi, 2rem); /* fluid, relative to the card, not the viewport */
    background: color-mix(in oklch, var(--brand) 12%, white); /* derived tint */

    & > .title {                    /* native nesting, no Sass */
      margin-block-end: 0.5rem;     /* logical: works in RTL and vertical writing modes */
    }
  }

  @container (min-width: 30rem) {   /* responds to the card, reusable anywhere */
    .card { flex-direction: row; }
  }
}
```

**Bad Example** — legacy workarounds for solved problems

```css
/* Aspect ratio via padding hack — fragile, needs an absolutely positioned child. */
.video { position: relative; height: 0; padding-top: 56.25%; }
.video > iframe { position: absolute; inset: 0; }

/* Fixed breakpoints tied to the viewport, so this card can't be reused in a sidebar. */
@media (min-width: 900px) { .card { flex-direction: row; } }

/* Manual override war because there are no layers. */
.card .title { margin-bottom: 8px !important; } /* !important papers over specificity */
```

## Common Mistakes

- Adding Sass or a CSS-in-JS runtime solely for nesting or variables that native CSS now
  provides.
- Using viewport media queries for a component that should use a container query, making
  the component non-reusable across layout contexts.
- Deep native nesting (four-plus levels), which recreates the specificity problems nesting
  was supposed to avoid.
- Using `:is()` where you meant `:where()`, unintentionally raising specificity.
- Assuming every modern feature is universally supported — check
  [browser compatibility](26-browser-compatibility.md) and provide fallbacks for anything
  not yet Baseline.
- Hardcoding hover/active color variants instead of deriving them with `color-mix()`.

## Production Tips

- Track feature status with Baseline (web.dev/baseline) and `@supports` rather than a
  browser-version table; "Baseline Widely available" is the safe-to-ship signal.
- Introduce cascade layers early in a project — retrofitting `@layer` into a specificity-heavy
  codebase is painful. See [methodologies](29-css-methodologies.md).
- You can still keep a preprocessor for build-time concerns (globbing, mixins) while using
  native features for runtime behavior; do not assume "modern CSS" means "no build".

## AI Review Checklist

- Is a native feature used where one exists, instead of a JS shim or preprocessor-only trick?
- Are components made responsive with container queries rather than viewport media queries?
- Is layer order (`@layer`) used to control cascade instead of `!important`?
- Are logical properties used for text-directional spacing so RTL works?
- Are color variants derived (`color-mix()`/relative color) from a single source value?
- Is any not-yet-Baseline feature guarded with `@supports` or a documented fallback?

## Related

- `knowledge/css/19-container-queries.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/26-browser-compatibility.md`
- `knowledge/css/07-grid.md`
- `knowledge/css/28-best-practices.md`
