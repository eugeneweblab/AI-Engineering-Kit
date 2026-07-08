---
id: css/08-sizing
topic: css
slug: sizing
title: "Sizing"
type: doc
order: 8
status: ready
tags: [css, sizing]
related: [css/04-box-model, css/09-spacing, css/06-flexbox, css/07-grid, css/17-responsive-design]
when_to_use: "Read before setting any width, height, or min/max dimension on an element."
---
# Sizing

## Purpose

This document defines how to size elements: the difference between `width`/`height`,
`min-*`/`max-*`, and the intrinsic keywords (`auto`, `min-content`, `max-content`,
`fit-content`); which units to use; and how `box-sizing` changes the math. It is written
so an agent can size elements that adapt to content and viewport instead of clipping,
overflowing, or overlapping.

Sizing is inseparable from the [box model](04-box-model.md); read that first if the
padding/border math is unclear.

## Why It Matters

Fixed sizes are the root cause of most responsive failures: text clipped mid-word, a
button that overflows its container, a card that overlaps its neighbor at a narrow width.
The fix is almost always to constrain a size *range* (`max-width`, `min-height`) and let
the browser choose the actual value from content and available space. An agent that
reaches for `min`/`max` constraints and relative units instead of hard pixel dimensions
produces layouts that survive real content and real screens.

## Core Principles

- **Constrain ranges, not exact values.** `max-width` caps a line length; `min-height`
  reserves space; the element still adapts between the bounds. A bare `width` forbids
  adaptation and is the usual overflow culprit.
- **`box-sizing: border-box` is the sane default.** With it, `width` includes padding and
  border, so `width: 100%` plus padding does not overflow. Set it globally.
- **Pick units by what they should track.** `rem` scales with user font settings (respects
  accessibility); `%` tracks the parent; `ch` tracks text width; `vw`/`vh`/`dvh` track the
  viewport. Fixed `px` tracks nothing and should be rare for layout.
- **Prefer intrinsic sizing keywords when content should decide.** `fit-content`,
  `min-content`, and `max-content` size to the content itself, avoiding magic numbers.

## Best Practices

- Set `box-sizing: border-box` on `*` (and `::before`/`::after`) once, globally; every
  other sizing rule then behaves intuitively.
- Cap readable text with `max-width: 65ch` (or similar) so line length stays legible;
  `ch` tracks the font, unlike a pixel width.
- Use `min-height` (not `height`) for containers that must hold at least some space but
  grow with content — a fixed `height` clips overflow.
- Use `max-width: 100%` on media (`img`, `video`, `svg`) plus `height: auto` so they scale
  down without distortion and never overflow their column.
- Prefer `min()`, `max()`, and `clamp()` for fluid-but-bounded sizes:
  `width: min(100%, 40rem)` is full-width until `40rem`, then capped — no media query.
- Use `dvh` (dynamic viewport height) instead of `vh` for full-height mobile layouts;
  `vh` ignores the collapsing mobile URL bar and causes jump/clip.
- Avoid fixed `height` on anything containing text; text reflows and will overflow a
  locked box.

## Examples

**Good Example** — bounded, content-aware sizing

```css
*, *::before, *::after { box-sizing: border-box; } /* predictable width math */

.prose {
  max-width: 65ch;      /* legible line length, tracks font size */
  margin-inline: auto;  /* center within available width */
}

.card {
  width: min(100%, 22rem); /* fluid until 22rem, then capped — no media query */
  min-height: 8rem;        /* reserve space but grow with content */
  padding: 1rem;           /* included in width thanks to border-box */
}

img { max-width: 100%; height: auto; } /* scale down, keep aspect ratio */
```

**Bad Example** — fixed sizes that clip and overflow

```css
.card {
  box-sizing: content-box; /* default: padding adds to width */
  width: 352px;            /* magic number; overflows below 352px viewports */
  height: 128px;           /* fixed height clips overflowing text */
  padding: 16px;           /* real width is 352 + 32 = 384px → overflow */
}
img { width: 400px; } /* overflows any narrower column, ignores aspect ratio */
```

## Common Mistakes

- Leaving `box-sizing` at the default `content-box`, so `width: 100%` + padding overflows.
- Using `height` where `min-height` is meant, clipping content that grows.
- Sizing text containers in `px`, ignoring the user's font-size and zoom preferences
  (an accessibility failure).
- Using `100vh` for full-screen mobile layouts, which is wrong while the URL bar is
  shown; use `100dvh`.
- Forgetting `height: auto` on responsive images, distorting aspect ratio.
- Hardcoding widths that duplicate what `flex`/`fr`/`fit-content` would compute for free.

## Production Tips

- `aspect-ratio: 16 / 9` reserves correct space for media before it loads, preventing
  layout shift (a Core Web Vitals win) — pair it with `width` and let height derive.
- `clamp(min, preferred, max)` gives fluid typography and spacing with hard bounds in one
  line; e.g. `font-size: clamp(1rem, 2.5vw, 1.5rem)`.
- When something overflows, inspect whether a fixed dimension or missing `min-width: 0`
  (in flex/grid children) is the cause before adding `overflow: hidden`.

## AI Review Checklist

- Is `box-sizing: border-box` set globally?
- Are ranges (`min-*`/`max-*`) preferred over fixed `width`/`height` for adaptive elements?
- Is readable text capped with a `max-width` in `ch` or `rem`?
- Do responsive images use `max-width: 100%; height: auto`?
- Are font-relative units (`rem`, `em`, `ch`) used where user preferences should apply?
- Do full-height layouts use `dvh` rather than `vh`?
- Is `aspect-ratio` used to reserve media space and avoid layout shift?

## Related

- `knowledge/css/04-box-model.md`
- `knowledge/css/09-spacing.md`
- `knowledge/css/06-flexbox.md`
- `knowledge/css/07-grid.md`
- `knowledge/css/17-responsive-design.md`
