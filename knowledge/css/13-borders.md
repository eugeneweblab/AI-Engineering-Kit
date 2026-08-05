---
id: css/13-borders
topic: css
slug: borders
title: "Borders"
type: doc
order: 13
status: ready
tags: [css, borders, border-radius, outline, outline-offset, border, none, box-sizing]
related: [css/04-box-model, css/12-backgrounds, css/08-sizing, css/23-accessibility]
when_to_use: "Read before adding borders, rounded corners, outlines, or focus rings to any element."
---
# Borders

## Purpose

This document defines how to draw edges around an element: `border`, `border-radius`,
and `outline`, plus how each interacts with size and layout. It is written so an agent
can add borders and focus rings without breaking box sizing or accessibility.

A border occupies space between the padding and margin in the [box model](04-box-model.md).
An outline does not — it is painted on top and never affects layout. That distinction
drives most correct decisions here.

## Why It Matters

Borders look trivial but touch two things that break easily: layout math and keyboard
accessibility. A border adds to an element's rendered size unless `box-sizing` accounts
for it, so a naively added `1px` border can shift a whole grid. More seriously, the
outline is the browser's default keyboard-focus indicator; removing it — a common
"cleanup" — makes the site unusable for keyboard and screen-reader users and is a direct
WCAG failure. Getting borders right is partly visual, partly a correctness and
accessibility obligation.

## Core Principles

- **Border adds to the box; outline does not.** Use `box-sizing: border-box` so a border
  eats into the declared width instead of enlarging the element.
- **Never remove focus visibility, only restyle it.** `outline: none` without a
  replacement breaks keyboard navigation. Provide a clearly visible custom indicator.
- **`border-radius` clips the border box, not the content by default.** To clip content
  (like an image) to the rounded corner, add `overflow: hidden`.
- **A border needs three parts to render:** width, style, and color. `border-style` is
  the one that actually turns it on; a width and color with no style shows nothing.
- **Prefer `outline` for focus rings** because it does not shift layout and can sit
  outside the element via `outline-offset`.

## Best Practices

- Set `box-sizing: border-box` globally (`*, *::before, *::after`) so borders never
  change an element's footprint — the single most common border layout bug.
- Style focus with `:focus-visible`, not `:focus`, so the ring appears for keyboard users
  but not on mouse click, and never delete it without a visible replacement.
- Give focus indicators at least a 3:1 contrast ratio against adjacent colors and a
  minimum ~2px thickness, per WCAG 2.2, so they are actually perceivable.
- Use a single-side longhand (`border-bottom`, `border-inline-start`) when you want one
  edge, instead of drawing all four and hiding three.
- Prefer logical properties (`border-inline-start`, `border-block-end`) for anything that
  must flip in right-to-left layouts.
- Use `border-radius` shorthand carefully: `border-radius: 10px / 20px;` sets horizontal
  and vertical radii separately (elliptical corners) — usually not what you want.

## Examples

**Good Example** — border-box sizing, accessible focus ring, clipped corners

```css
*, *::before, *::after { box-sizing: border-box; } /* border never grows the box */

.card {
  border: 1px solid #d0d0d8; /* width + style + color: all three present */
  border-radius: 12px;
  overflow: hidden;          /* clip inner image corners to the radius */
}

.button:focus-visible {
  /* Keyboard-only, clearly visible, and does not shift layout because outline
     is not part of the box. Offset lifts it clear of the element edge. */
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}
```

**Bad Example** — layout-shifting border, destroyed focus, invisible edge

```css
.button {
  width: 200px;
  border: 2px solid blue; /* with content-box, real width is now 204px → grid shifts */
}
.button:focus {
  outline: none; /* removes the only focus indicator: keyboard users are lost */
}
.divider {
  border-width: 1px;
  border-color: gray; /* no border-style → nothing renders at all */
}
```

## Common Mistakes

- Removing `outline` on `:focus` with no replacement, breaking keyboard accessibility.
- Forgetting `box-sizing: border-box`, so borders enlarge elements and shift layout.
- Setting `border-width` and `border-color` but omitting `border-style`, so no line
  appears (the default style is `none`).
- Expecting `border-radius` to clip inner content without `overflow: hidden`.
- Using `:focus` (fires on mouse click too) instead of `:focus-visible`.
- Drawing all four borders then overriding three, instead of using one-side longhands.

## Production Tips

- For hairline dividers on high-DPI screens, a `1px` border can look heavy; consider a
  subtle color rather than sub-pixel widths, which round inconsistently across browsers.
- When a hover state adds a border, reserve the space up front (e.g. a transparent
  border of the same width) so hovering does not nudge layout.

## AI Review Checklist

- Is `box-sizing: border-box` set so borders do not change element dimensions?
- Is every removed default outline replaced with a visible `:focus-visible` indicator?
- Do focus indicators meet ~3:1 contrast and ~2px thickness (WCAG 2.2)?
- Does every rendered border include a `border-style`?
- Is `overflow: hidden` present where content must clip to a `border-radius`?
- Are logical border properties used for layouts that must mirror in RTL?

## Related

- `knowledge/css/04-box-model.md`
- `knowledge/css/12-backgrounds.md`
- `knowledge/css/08-sizing.md`
- `knowledge/css/23-accessibility.md`
