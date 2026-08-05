---
id: css/18-media-queries
topic: css
slug: media-queries
title: "Media Queries"
type: doc
order: 18
status: ready
tags: [css, media-queries, min-width, "@media", media, max-width, repeat, prefers-reduced-motion]
related: [css/17-responsive-design, css/19-container-queries, css/23-accessibility, css/22-performance, css/20-css-variables]
when_to_use: "Read before writing any responsive breakpoint, adapting to device features, or honoring user preferences like reduced motion or dark mode."
---
# Media Queries

## Purpose

This document defines how to adapt a layout to the *viewport and device* using `@media`.
It covers breakpoint strategy, feature queries beyond width (motion, contrast, color
scheme, pointer type), and the mistakes that make responsive CSS brittle.

Media queries answer "what is the environment rendering this page?" — screen size,
input device, user preferences. For adapting a component to *the space it happens to
occupy*, that is a different tool: see [container queries](19-container-queries.md).

## Why It Matters

Layout that only works at the designer's screen size is broken for most of the people
who visit it — phones, tablets, zoomed-in desktops, split-screen windows. Media queries
are also the mechanism for honoring accessibility and OS preferences: a user who set
"reduce motion" or "dark mode" at the system level expects the site to respect it, and
ignoring `prefers-reduced-motion` can trigger vestibular illness. Getting breakpoints
wrong forces horizontal scrolling, clipped content, and unreadable text — the most
common and most visible CSS failures.

## Core Principles

- **Design mobile-first.** Write base styles for the smallest screen, then layer
  enhancements with `min-width` queries. This keeps the default lightweight and means
  a query that fails simply falls back to a working narrow layout.
- **Breakpoints follow content, not devices.** Add a breakpoint where the layout starts
  to look wrong, not at a fixed "iPad width". Device sizes change; content constraints
  do not.
- **Use `em`/`rem` for width queries, not `px`.** Breakpoints in `em` scale with the
  user's font size, so a zoomed-in user gets the small-screen layout instead of clipped
  text. The cost is one mental conversion (`768px / 16 = 48em`).
- **Respect user preferences.** `prefers-reduced-motion`, `prefers-color-scheme`, and
  `prefers-contrast` are not optional polish; they are how the OS tells you what the
  user needs.
- **Query features, not widths alone.** `pointer`, `hover`, and `orientation` describe
  capability far more reliably than guessing from screen size.

## Best Practices

- Adopt one direction (mobile-first `min-width`) across the whole codebase. Mixing
  `min-width` and `max-width` creates overlapping ranges that fight each other.
- Define breakpoints once as named tokens (Sass maps, custom properties, or a config)
  so the same values are reused instead of magic numbers scattered per file.
- Prefer the range syntax `@media (width >= 48em)` where supported (baseline since
  2023); it is clearer than `min-width` and avoids off-by-one gaps between `max-width`
  and `min-width` boundaries.
- Wrap all non-essential animation in `@media (prefers-reduced-motion: no-preference)`
  so motion is opt-in from the animation's perspective.
- Use `@media (hover: hover) and (pointer: fine)` before showing hover-only affordances;
  touch users cannot hover and will be stranded.
- Keep breakpoints few. Two or three well-chosen ones beat eight that each handle a
  narrow band and must all be maintained.

## Examples

**Good Example** — mobile-first, `em` breakpoints, honored preferences

```css
/* Base: smallest screen. Works with zero media queries applied. */
.grid { display: grid; gap: 1rem; grid-template-columns: 1fr; }

/* Enhance upward. 48em = 768px at default font size, but scales with zoom. */
@media (width >= 48em) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (width >= 64em) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}

/* Motion is opt-in: only animate when the user has not asked to reduce it. */
@media (prefers-reduced-motion: no-preference) {
  .card { transition: transform 200ms ease; }
}
```

**Bad Example** — desktop-first, px breakpoints, motion forced on everyone

```css
.grid { display: grid; grid-template-columns: repeat(3, 1fr); } /* assumes desktop */

/* max-width walks downward; base is the heavy case, and boundaries can overlap
   a min-width query elsewhere by 1px, leaving a gap at exactly 767px. */
@media (max-width: 767px) {
  .grid { grid-template-columns: 1fr; }
}

/* Animation ignores prefers-reduced-motion → can cause nausea for some users. */
.card { transition: transform 200ms ease; }
```

## Common Mistakes

- Desktop-first `max-width` queries, so the default (heaviest) layout ships to phones.
- Hardcoding device widths (`375px`, `1024px`) instead of content-driven breakpoints.
- `px` width queries that ignore the user's font-size / zoom preference.
- Overlapping `min-width`/`max-width` ranges that both apply, or leave a 1px dead zone.
- Animating unconditionally, ignoring `prefers-reduced-motion`.
- Showing hover menus without a `hover: hover` guard, breaking touch navigation.
- Duplicating the same breakpoint number in dozens of files instead of a shared token.

## Production Tips

- Test at real breakpoint edges (1px below and above) and at 200% browser zoom — most
  responsive bugs hide exactly at the boundary.
- Set `<meta name="viewport" content="width=device-width, initial-scale=1">` or every
  media query is measured against a fake 980px viewport on mobile.
- Combine media queries with [CSS variables](20-css-variables.md): redefine a
  `--columns` custom property per breakpoint and reference it once, instead of
  rewriting whole rules.

## AI Review Checklist

- Are styles mobile-first, using `min-width` / `width >=` rather than `max-width`?
- Are width breakpoints in `em`/`rem` so they respect font size and zoom?
- Do breakpoints derive from content, with a small, named, reused set of values?
- Is every non-essential animation gated behind `prefers-reduced-motion`?
- Are hover-only affordances guarded by `(hover: hover)`?
- Is the viewport meta tag present so queries measure the real device width?
- Are query ranges free of overlaps and off-by-one gaps at the boundaries?

## Related

- `knowledge/css/17-responsive-design.md`
- `knowledge/css/19-container-queries.md`
- `knowledge/css/20-css-variables.md`
- `knowledge/css/22-performance.md`
- `knowledge/css/23-accessibility.md`
