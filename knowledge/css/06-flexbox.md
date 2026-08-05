---
id: css/06-flexbox
topic: css
slug: flexbox
title: "CSS Flexbox"
type: doc
order: 6
status: ready
tags: [css, flexbox]
related: [css/07-grid, css/08-sizing, css/09-spacing, css/05-positioning, css/17-responsive-design]
when_to_use: "Read before laying out a component's children in a single row or column, or centering content."
---
# CSS Flexbox

## Purpose

This document defines how to lay out elements in one dimension — a single row or a
single column — using `display: flex`. It covers the container/item model, the main
and cross axes, and how items grow, shrink, and align, so an agent can build a layout
that stays correct as content and viewport change.

Flexbox is for *content-driven* layout along one axis: navbars, toolbars, button rows,
card footers, centering. For two-dimensional page structure (rows *and* columns at once),
use [Grid](07-grid.md) instead.

## Why It Matters

Layout bugs are the most visible failures a user sees: overflowing text, squished
buttons, off-center modals. Most are caused by fighting the layout system with fixed
pixel widths and floats instead of letting flex distribute space. Flexbox solves whole
classes of these bugs — vertical centering, equal-height columns, "push this to the
right" — declaratively. Getting the container/item split and the axis direction right
the first time removes the need for magic-number hacks that break at the next breakpoint.

## Core Principles

- **Container sets the rules; items follow them.** `display: flex` on the parent creates
  a flex context. `flex-direction`, `justify-content`, `align-items`, and `gap` live on
  the container. `flex-grow`, `flex-shrink`, `flex-basis`, and `align-self` live on items.
- **Everything is relative to the two axes.** The *main axis* follows `flex-direction`;
  the *cross axis* is perpendicular. `justify-*` works along the main axis, `align-*`
  along the cross axis. Rotating `flex-direction` swaps which is which — this is the
  single most common source of confusion.
- **Space is distributed, not assigned.** Prefer `flex: 1` and `gap` over fixed widths.
  Let items compute their own size so the layout survives different content lengths.
- **`gap` is the correct way to space flex items.** It applies only *between* items, with
  no edge margins to strip, unlike per-item `margin`.

## Best Practices

- Use `gap` for spacing between items; do not use `margin-right` on every child and then
  fight the trailing margin. `gap` is supported in all current browsers.
- Center anything with `display: flex; justify-content: center; align-items: center;` —
  it works regardless of the child's size, unlike absolute-position centering.
- Set `min-width: 0` on a flex item that contains text which must truncate. Flex items
  default to `min-width: auto`, which refuses to shrink below content size and causes
  overflow instead of an ellipsis.
- Use the `flex` shorthand (`flex: 1`, `flex: 0 0 auto`) rather than the three longhands
  separately; the shorthand resets all three and avoids stale values.
- Add `flex-wrap: wrap` when items must reflow on narrow screens; a single-line flex row
  will otherwise shrink children past usability.
- Reach for `margin-left: auto` on one item to push it and everything after it to the
  end (classic "logo left, actions right" navbar) instead of adding a spacer element.

## Examples

**Good Example** — responsive navbar with truncation-safe title

```css
.navbar {
  display: flex;
  align-items: center; /* vertical centering, any child height */
  gap: 1rem;           /* spacing between items, no trailing margin */
  padding: 0 1rem;
}
.navbar__title {
  flex: 1;        /* take remaining space */
  min-width: 0;   /* allow shrink so overflow can truncate, not overflow */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.navbar__actions {
  flex: 0 0 auto; /* keep buttons at intrinsic size, never shrink */
}
```

**Bad Example** — fixed widths and margin hacks that break

```css
.navbar {
  display: flex;
}
.navbar__title {
  width: 600px;        /* magic number: overflows below 600px viewports */
  margin-right: 20px;  /* trailing margin on the last item too */
}
.navbar__actions {
  width: 200px;        /* squishes or clips when title is long */
}
/* No min-width:0, so a long title overflows the bar instead of truncating. */
```

## Common Mistakes

- Confusing the axes: applying `align-items` expecting horizontal movement, or
  `justify-content` expecting vertical, without checking `flex-direction`.
- Text overflowing its flex item because `min-width: auto` was never overridden to `0`.
- Spacing items with per-child `margin`, then hacking away the last child's margin with
  `:last-child` instead of using `gap`.
- Using Flexbox for a true 2-D grid, producing brittle nested flex containers where
  [Grid](07-grid.md) would be one declaration.
- Setting `flex-basis` in `%` and expecting it to account for `gap` — it does not; the
  gap is subtracted after, so `flex: 1` is safer than `flex-basis: 50%`.

## Production Tips

- When items must line up across separate flex containers (e.g., cards in different
  rows), Flexbox cannot align across containers — switch to [Grid](07-grid.md).
- Test layouts with both very short and very long content, and at the narrowest supported
  viewport; most flex bugs only appear at content extremes.
- `flex-direction: column` makes `height` the main axis — percentage heights then need a
  sized parent, a frequent "why won't it grow" cause.

## AI Review Checklist

- Is spacing done with `gap` rather than per-item margins?
- Do flex items containing truncatable text have `min-width: 0`?
- Is the layout genuinely one-dimensional, or should it be [Grid](07-grid.md)?
- Are `justify-*` / `align-*` applied to the correct axis for the `flex-direction`?
- Does the layout hold at the narrowest viewport and with long content?
- Are sizes expressed as `flex` ratios rather than fixed pixel widths where possible?

## Related

- `knowledge/css/07-grid.md`
- `knowledge/css/08-sizing.md`
- `knowledge/css/09-spacing.md`
- `knowledge/css/05-positioning.md`
- `knowledge/css/17-responsive-design.md`
