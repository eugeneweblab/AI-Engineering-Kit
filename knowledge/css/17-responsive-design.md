---
id: css/17-responsive-design
topic: css
slug: responsive-design
title: "Responsive Design"
type: doc
order: 17
status: ready
tags: [css, responsive-design]
related: [css/18-media-queries, css/19-container-queries, css/06-flexbox, css/07-grid, css/08-sizing]
when_to_use: "Read before building any layout that must work across phone, tablet, and desktop widths."
---
# Responsive Design

## Purpose

This document defines how to build layouts that adapt to any viewport and content size:
mobile-first strategy, fluid sizing, breakpoints, and the modern intrinsic techniques that
reduce the need for explicit breakpoints. It is written so an agent can produce a layout
that works from a 320px phone to a wide desktop without horizontal scrolling or broken
components.

Responsive design is the strategy; its tools live in adjacent docs —
[media queries](18-media-queries.md), [container queries](19-container-queries.md),
[flexbox](06-flexbox.md), and [grid](07-grid.md). This doc explains how to combine them.

## Why It Matters

Most traffic is mobile, and viewports now range from watches to ultrawide monitors, so a
fixed-width layout is broken for the majority of users before it ships. The classic
failures — horizontal scroll on phones, text too small to read, tap targets too close, a
sidebar that overlaps content — are all invisible to a developer testing only on a desktop
browser at one width. Responsiveness is not a finishing touch; it is a baseline
correctness property of any layout.

## Core Principles

- **Design mobile-first.** Write base styles for the smallest screen, then add complexity
  at larger widths with `min-width` queries. Progressive enhancement is simpler than
  stripping a desktop layout back down.
- **Prefer intrinsic responsiveness over breakpoints.** Flexbox `wrap`, Grid
  `auto-fit`/`minmax`, and `clamp()` let content adapt continuously, so many layouts need
  zero media queries.
- **Content should reflow, never overflow.** The page body must never scroll horizontally;
  wide items (tables, code, diagrams) scroll inside their own container.
- **Choose breakpoints from content, not device names.** Add a breakpoint where the layout
  actually breaks, not at "iPhone width." Device sizes change; content needs do not.
- **The viewport meta tag is a prerequisite.** Without
  `<meta name="viewport" content="width=device-width, initial-scale=1">`, mobile browsers
  render at a fake desktop width and every media query is wrong.

## Best Practices

- Use fluid type with `clamp(min, preferred, max)` (e.g. `clamp(1rem, 0.9rem + 0.5vw, 1.25rem)`)
  so font size scales smoothly between a floor and ceiling instead of jumping at breakpoints.
- Build card/tile grids with `grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr))`
  so the column count adapts to available width with no media queries.
- Reach for [container queries](19-container-queries.md) to make a *component* respond to
  its own container width, so the same card works in a sidebar and a full-width region.
- Size images responsively: `max-width: 100%; height: auto;` plus `srcset`/`sizes` so the
  browser downloads an appropriately sized source.
- Ensure tap targets are at least ~24×24 CSS px (WCAG 2.2) with adequate spacing so touch
  users can hit them.
- Test at 320px width and at 200% zoom; both are baseline accessibility requirements and
  catch most overflow bugs.

## Examples

**Good Example** — mobile-first, intrinsic grid, fluid type, no overflow

```css
:root { font-size: clamp(1rem, 0.95rem + 0.4vw, 1.15rem); } /* scales, no jumps */

.gallery {
  display: grid;
  /* Columns adapt to width automatically: 1 on a phone, many on desktop,
     with NO media query. minmax stops columns from getting too narrow. */
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 1rem;
}
img { max-width: 100%; height: auto; } /* never overflow the container */

/* Add complexity only where content needs it (mobile-first min-width). */
@media (min-width: 48rem) {
  .layout { grid-template-columns: 16rem 1fr; } /* sidebar appears when there is room */
}
```

**Bad Example** — desktop-first, fixed widths, guaranteed mobile overflow

```css
.gallery {
  display: flex;
  /* Fixed pixel width per card + no wrap → 4×300px = 1200px forces the whole
     page to scroll horizontally on a 375px phone. */
  width: 1200px;
}
.card { width: 300px; }

.title { font-size: 42px; } /* fixed px: huge on mobile, no fluid scaling */
/* No viewport meta assumed, no min-width refinement: broken below desktop */
```

## Common Mistakes

- Omitting the viewport meta tag, so mobile renders a zoomed-out desktop layout.
- Fixed pixel widths (`width: 1200px`, `width: 300px`) that overflow small screens.
- Desktop-first `max-width` queries that pile up overrides and are hard to reason about.
- Picking breakpoints by device name instead of where the content breaks.
- Letting wide tables or code blocks overflow the page instead of scrolling in a container.
- Tap targets too small or too tightly packed for touch.
- Testing at only one width and missing 320px and 200%-zoom failures.

## Production Tips

- Prefer relative units (`rem`, `%`, `vw`, `ch`) over `px` for anything that should scale
  with the user's font-size or the viewport; `px` ignores user zoom preferences.
- Use `min()`/`max()`/`clamp()` to cap fluid values (e.g. `width: min(100%, 60ch)`) so a
  container never exceeds a readable line length on wide screens.
- Combine container queries for components with a few global media queries for page shell
  layout — they solve different problems.

## AI Review Checklist

- Is the viewport meta tag present with `width=device-width, initial-scale=1`?
- Are base styles mobile-first, refined upward with `min-width` queries?
- Does the layout use intrinsic techniques (`auto-fit`/`minmax`, `flex-wrap`, `clamp`)
  before resorting to breakpoints?
- Does the page avoid horizontal scroll at 320px, with wide items scrolling internally?
- Are images `max-width: 100%` and served responsively via `srcset`/`sizes`?
- Are breakpoints chosen from content, and tap targets ≥24px?
- Does the layout hold up at 200% zoom?

## Related

- `knowledge/css/18-media-queries.md`
- `knowledge/css/19-container-queries.md`
- `knowledge/css/06-flexbox.md`
- `knowledge/css/07-grid.md`
- `knowledge/css/08-sizing.md`
