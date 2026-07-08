---
id: css/04-box-model
topic: css
slug: box-model
title: "Box Model"
type: doc
order: 4
status: ready
tags: [css, box-model]
related: [css/05-positioning, css/08-sizing, css/09-spacing, css/01-css-fundamentals, css/06-flexbox]
when_to_use: "Read before laying out any element, to control its dimensions, spacing, and how padding and border affect size."
---
# Box Model

## Purpose

This document defines the **box model**: how the browser computes an element's rendered
size from `content`, `padding`, `border`, and `margin`, and how `box-sizing` changes that
math. Almost every layout bug — an element that overflows its container, a "1000px" column
that renders wider, a gap that won't collapse — traces back to a misunderstanding of these
four boxes. An agent that internalizes the model stops fighting widths and starts setting them.

## Why It Matters

The single most consequential default in CSS is `box-sizing: content-box`, under which
`width` sets only the *content* box — padding and border are added *on top*. So
`width: 300px; padding: 20px; border: 1px` renders 342px wide, silently overflowing a 300px
parent. This surprises nearly everyone and causes horizontal scrollbars, broken grids, and
"why is this off by exactly 40 pixels?" debugging sessions. Understanding the boxes — and
flipping the default to `border-box` — eliminates a whole category of layout defects.

## Core Principles

- **Every element is four nested boxes.** From inside out: content → padding (inside the
  border, shares the background) → border → margin (transparent space outside, separates
  from neighbors). Know which property affects which box.
- **`box-sizing` decides what `width`/`height` measure.** `content-box` (the default) sizes
  only content; `border-box` makes `width` include padding and border. `border-box` is what
  you almost always want, because "300px means 300px."
- **Vertical margins collapse; padding and horizontal margins do not.** Adjacent vertical
  margins merge into the larger of the two — a frequent source of "missing" or "extra" space.
- **`margin` is space *between* boxes; `padding` is space *inside* the border.** Choose by
  intent: padding when the space should share the background and be part of the click target,
  margin when it should separate the element from its neighbors.

## Best Practices

- Set `box-sizing: border-box` globally so dimensions are predictable:
  `*, *::before, *::after { box-sizing: border-box; }`. Do this once, in your reset.
- Prefer modern **`gap`** (in flex and grid) over margins for spacing between siblings — it
  avoids margin collapsing and the "last-child margin" cleanup entirely. See
  [spacing](09-spacing.md).
- Use **logical properties** (`padding-inline`, `margin-block`, `border-inline`) so layouts
  adapt to right-to-left and vertical writing modes without duplicated rules.
- Avoid fixed `height` on content that grows; let content dictate height and constrain with
  `max-height` / `min-height` when needed, so text never clips.
- Understand margin collapsing rather than defeating it with hacks; if you need to stop it,
  a `padding`, `border`, or a flex/grid container between the margins does so cleanly.

## Examples

**Good Example** — border-box, logical spacing, content-driven height

```css
*, *::before, *::after { box-sizing: border-box; } /* width means the full width */

.card {
  width: 300px;
  padding-inline: 1.5rem;   /* logical: honors LTR/RTL automatically */
  padding-block: 1rem;
  border: 1px solid var(--line);
  /* Renders exactly 300px wide — padding and border are inside the width. */
}

.stack { display: flex; flex-direction: column; gap: 1rem; } /* no margin cleanup */
```

**Bad Example** — content-box overflow and margin cleanup debt

```css
.card {
  /* box-sizing defaults to content-box here */
  width: 300px;
  padding: 20px;
  border: 1px solid #ccc;
  /* Actually renders 342px wide → overflows a 300px parent, horizontal scrollbar. */
}

.stack > * { margin-bottom: 1rem; }
.stack > *:last-child { margin-bottom: 0; } /* fragile cleanup gap solves for free */
```

## Common Mistakes

- Leaving `box-sizing` at `content-box`, then chasing "off by padding + border" width bugs.
- Adding padding/border to a fixed-width element and being surprised it overflows its parent.
- Fighting collapsed vertical margins instead of using `gap` or understanding the collapse rule.
- Setting a fixed `height` on text containers, clipping content when it grows or the font scales.
- Using physical `margin-left`/`padding-right` where logical properties would handle RTL for free.

## Production Tips

- When something overflows, toggle `outline: 1px solid red` (outline, not border — it does
  not affect layout) on the suspect elements to see which box is too big.
- Prefer `min-width: 0` on flex/grid children that contain long content; the default
  `min-width: auto` prevents them from shrinking and causes overflow.

## AI Review Checklist

- Is `box-sizing: border-box` applied globally so widths include padding and border?
- Is sibling spacing done with `gap` rather than margins where a flex/grid parent exists?
- Are logical properties used for padding/margin/border so RTL works without extra rules?
- Are heights content-driven (with `min`/`max` constraints) rather than fixed where content grows?
- Are collapsed-margin effects understood rather than patched with last-child hacks?

## Related

- `knowledge/css/05-positioning.md`
- `knowledge/css/08-sizing.md`
- `knowledge/css/09-spacing.md`
- `knowledge/css/01-css-fundamentals.md`
- `knowledge/css/06-flexbox.md`
